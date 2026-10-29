import ast
import json
import importlib.util
from pathlib import Path
import sys
import tempfile
import types
import unittest


SOURCE_DIR = Path(__file__).parent / "src"


def load_post_module():
    requests = types.ModuleType("requests")

    class RequestException(Exception):
        pass

    class Timeout(RequestException):
        pass

    requests.RequestException = RequestException
    requests.Timeout = Timeout
    requests.post = lambda *args, **kwargs: None
    sys.modules["requests"] = requests

    markdown = types.ModuleType("markdown")
    markdown.Markdown = object
    sys.modules["markdown"] = markdown

    bs4 = types.ModuleType("bs4")
    bs4.BeautifulSoup = object
    sys.modules["bs4"] = bs4

    dotenv = types.ModuleType("dotenv")
    dotenv.load_dotenv = lambda *args, **kwargs: None
    sys.modules["dotenv"] = dotenv

    spec = importlib.util.spec_from_file_location("gennote_post", SOURCE_DIR / "post.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class FakeResponse:
    def __init__(self, status_code=201, location=None):
        self.status_code = status_code
        self.headers = {} if location is None else {"Location": location}


class RepositoryTest(unittest.TestCase):
    def test_python_sources_parse(self):
        for path in SOURCE_DIR.glob("*.py"):
            with self.subTest(path=path.name):
                ast.parse(path.read_text(encoding="utf-8"), filename=str(path))

    def test_post_script_has_one_main_entrypoint(self):
        tree = ast.parse((SOURCE_DIR / "post.py").read_text(encoding="utf-8"))
        guards = [node for node in tree.body if isinstance(node, ast.If) and isinstance(node.test, ast.Compare)]
        self.assertEqual(len(guards), 1)

    def test_publication_completion_is_retry_safe(self):
        post = load_post_module()
        with tempfile.TemporaryDirectory() as directory:
            state = Path(directory) / "state.json"
            calls = []

            def success(*args, **kwargs):
                calls.append(1)
                return FakeResponse(location="https://example.invalid/entry/1")

            first = post.publish_entry("title", "body", "endpoint", {}, state, success)
            second = post.publish_entry("title", "body", "endpoint", {}, state, success)
            self.assertEqual(first["status"], "confirmed")
            self.assertEqual(second, first)
            self.assertEqual(len(calls), 1)

            changed = post.publish_entry("title", "changed", "endpoint", {}, state, success)
            self.assertEqual(changed["status"], "confirmed")
            self.assertEqual(len(calls), 2)

    def test_uncertain_publication_is_not_blindly_retried(self):
        post = load_post_module()
        with tempfile.TemporaryDirectory() as directory:
            state = Path(directory) / "state.json"
            calls = []

            def timeout(*args, **kwargs):
                calls.append(1)
                raise post.requests.Timeout("response lost")

            first = post.publish_entry("title", "body", "endpoint", {}, state, timeout)
            second = post.publish_entry("title", "body", "endpoint", {}, state, timeout)
            self.assertEqual(first["status"], "uncertain")
            self.assertEqual(second, first)
            self.assertEqual(len(calls), 1)

    def test_201_without_remote_identity_is_uncertain(self):
        post = load_post_module()
        with tempfile.TemporaryDirectory() as directory:
            state = Path(directory) / "state.json"
            result = post.publish_entry(
                "title", "body", "endpoint", {}, state, lambda *a, **k: FakeResponse()
            )
            self.assertEqual(result["status"], "uncertain")
            self.assertNotIn("remoteUrl", result)


    def test_unverified_http_response_never_reposts(self):
        post = load_post_module()
        with tempfile.TemporaryDirectory() as directory:
            state = Path(directory) / "state.json"
            calls = []

            def ambiguous_response(*args, **kwargs):
                calls.append(1)
                return FakeResponse(status_code=500)

            first = post.publish_entry("title", "body", "endpoint", {}, state, ambiguous_response)
            second = post.publish_entry("title", "body", "endpoint", {}, state, ambiguous_response)
            self.assertEqual(first["status"], "uncertain")
            self.assertEqual(first["httpStatus"], 500)
            self.assertEqual(second, first)
            self.assertEqual(len(calls), 1)

    def test_invalid_location_cannot_confirm_publication(self):
        post = load_post_module()
        with tempfile.TemporaryDirectory() as directory:
            state = Path(directory) / "state.json"
            calls = []

            def invalid_location(*args, **kwargs):
                calls.append(1)
                return FakeResponse(status_code=201, location="not-a-valid-url")

            first = post.publish_entry("title", "body", "endpoint", {}, state, invalid_location)
            second = post.publish_entry("title", "body", "endpoint", {}, state, invalid_location)
            self.assertEqual(first["status"], "uncertain")
            self.assertNotIn("remoteUrl", first)
            self.assertEqual(second, first)
            self.assertEqual(len(calls), 1)

    def test_inflight_intent_survives_process_crash(self):
        post = load_post_module()
        with tempfile.TemporaryDirectory() as directory:
            state = Path(directory) / "state.json"
            identity = post.publication_id("title", "body")
            calls = []

            def remote_create_then_crash(*args, **kwargs):
                calls.append(1)
                persisted = json.loads(state.read_text(encoding="utf-8"))
                self.assertEqual(persisted[identity]["status"], "uncertain")
                self.assertEqual(persisted[identity]["reason"], "create_in_flight")
                raise KeyboardInterrupt("process died after remote creation")

            with self.assertRaises(KeyboardInterrupt):
                post.publish_entry(
                    "title", "body", "endpoint", {}, state, remote_create_then_crash
                )

            def forbidden_retry(*args, **kwargs):
                self.fail("an uncertain external create must not be repeated")

            result = post.publish_entry(
                "title", "body", "endpoint", {}, state, forbidden_retry
            )
            self.assertEqual(result["status"], "uncertain")
            self.assertEqual(result["reason"], "create_in_flight")
            self.assertEqual(len(calls), 1)

if __name__ == "__main__":
    unittest.main()
