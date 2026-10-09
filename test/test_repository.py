import ast
from pathlib import Path
import sys
import tempfile
import unittest

SOURCE_DIR = Path(__file__).parent / "src"
sys.path.insert(0, str(SOURCE_DIR))
from publication import publish_once


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
        guards = [node for node in tree.body if isinstance(node, ast.If) and isinstance(node.test, ast.Compare) and isinstance(node.test.left, ast.Name) and node.test.left.id == "__name__"]
        self.assertEqual(len(guards), 1)

    def test_confirmed_publication_is_persisted_and_not_recreated(self):
        with tempfile.TemporaryDirectory() as directory:
            state = Path(directory) / "state.json"
            calls = []
            create = lambda article: calls.append(article) or FakeResponse(location="https://example.test/entry/1")
            first = publish_once("article", state, create)
            second = publish_once("article", state, create)
            self.assertEqual(first["status"], "confirmed")
            self.assertEqual(second, first)
            self.assertEqual(len(calls), 1)
            self.assertEqual(first["remote_url"], "https://example.test/entry/1")

    def test_timeout_after_create_stays_uncertain_and_blocks_blind_retry(self):
        with tempfile.TemporaryDirectory() as directory:
            state = Path(directory) / "state.json"
            calls = []
            def timeout(article):
                calls.append(article)
                raise TimeoutError("response lost")
            first = publish_once("article", state, timeout)
            second = publish_once("article", state, timeout)
            self.assertEqual(first["status"], "uncertain")
            self.assertEqual(second["status"], "uncertain")
            self.assertEqual(len(calls), 1)

    def test_201_without_remote_identity_is_uncertain(self):
        with tempfile.TemporaryDirectory() as directory:
            result = publish_once("article", Path(directory) / "state.json", lambda _: FakeResponse())
            self.assertEqual(result["status"], "uncertain")

    def test_changed_article_gets_independent_create(self):
        with tempfile.TemporaryDirectory() as directory:
            state = Path(directory) / "state.json"
            calls = []
            create = lambda article: calls.append(article) or FakeResponse(location=f"https://example.test/{len(calls)}")
            one = publish_once("article one", state, create)
            two = publish_once("article two", state, create)
            self.assertEqual(one["status"], "confirmed")
            self.assertEqual(two["status"], "confirmed")
            self.assertNotEqual(one["publication_id"], two["publication_id"])
            self.assertEqual(len(calls), 2)


if __name__ == "__main__":
    unittest.main()
