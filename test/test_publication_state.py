from pathlib import Path
import json
import sys
import tempfile
import unittest

SOURCE_DIR = Path(__file__).parent / "src"
sys.path.insert(0, str(SOURCE_DIR))

from publication_state import confirm_from_readback, publication_identity, publish_once


class FakeResponse:
    def __init__(self, status_code, location=None):
        self.status_code = status_code
        self.headers = {} if location is None else {"Location": location}


class PublicationStateTest(unittest.TestCase):
    def test_confirmed_create_is_persisted_and_same_input_is_not_created_twice(self):
        with tempfile.TemporaryDirectory() as tmp:
            state_dir = Path(tmp)
            publication_id = publication_identity("title", "body")
            calls = []

            def create():
                calls.append(1)
                return FakeResponse(201, "https://example.test/entry/1")

            first = publish_once(
                publication_id=publication_id, state_dir=state_dir, create=create
            )
            second = publish_once(
                publication_id=publication_id, state_dir=state_dir, create=create
            )

            self.assertTrue(first.confirmed)
            self.assertEqual(second, first)
            self.assertEqual(len(calls), 1)
            persisted = json.loads(
                (state_dir / f"{publication_id}.json").read_text(encoding="utf-8")
            )
            self.assertEqual(persisted["status"], "confirmed")
            self.assertEqual(persisted["remote_url"], "https://example.test/entry/1")

    def test_timeout_stays_uncertain_and_rerun_does_not_blindly_create(self):
        with tempfile.TemporaryDirectory() as tmp:
            state_dir = Path(tmp)
            publication_id = publication_identity("title", "body")
            calls = []

            def create():
                calls.append(1)
                persisted = json.loads(
                    (state_dir / f"{publication_id}.json").read_text(encoding="utf-8")
                )
                self.assertEqual(persisted["status"], "uncertain")
                self.assertEqual(persisted["reason"], "create_in_flight")
                raise TimeoutError("response lost after remote create")

            first = publish_once(
                publication_id=publication_id, state_dir=state_dir, create=create
            )
            second = publish_once(
                publication_id=publication_id,
                state_dir=state_dir,
                create=lambda: self.fail("uncertain state must block blind retry"),
            )

            self.assertEqual(first.status, "uncertain")
            self.assertEqual(second.status, "uncertain")
            self.assertEqual(len(calls), 1)

    def test_201_without_usable_location_is_uncertain(self):
        with tempfile.TemporaryDirectory() as tmp:
            state_dir = Path(tmp)
            publication_id = publication_identity("title", "body")
            calls = []

            def create():
                calls.append(1)
                return FakeResponse(201)

            result = publish_once(
                publication_id=publication_id, state_dir=state_dir, create=create
            )
            rerun = publish_once(
                publication_id=publication_id,
                state_dir=state_dir,
                create=lambda: self.fail("uncertain state must block blind retry"),
            )

            self.assertEqual(result.status, "uncertain")
            self.assertEqual(rerun.status, "uncertain")
            self.assertEqual(len(calls), 1)

    def test_changed_input_gets_new_identity_and_can_publish(self):
        with tempfile.TemporaryDirectory() as tmp:
            state_dir = Path(tmp)
            first_id = publication_identity("title", "body")
            second_id = publication_identity("title", "changed body")
            calls = []

            def create():
                calls.append(1)
                return FakeResponse(201, f"https://example.test/entry/{len(calls)}")

            first = publish_once(publication_id=first_id, state_dir=state_dir, create=create)
            second = publish_once(publication_id=second_id, state_dir=state_dir, create=create)

            self.assertNotEqual(first_id, second_id)
            self.assertTrue(first.confirmed)
            self.assertTrue(second.confirmed)
            self.assertEqual(len(calls), 2)

    def test_identity_is_stable_for_same_article_input(self):
        self.assertEqual(
            publication_identity("金融AIレポート", "同じ本文"),
            publication_identity("金融AIレポート", "同じ本文"),
        )

    def test_readback_can_resolve_uncertain_without_another_create(self):
        with tempfile.TemporaryDirectory() as tmp:
            state_dir = Path(tmp)
            publication_id = publication_identity("title", "body")

            uncertain = publish_once(
                publication_id=publication_id,
                state_dir=state_dir,
                create=lambda: (_ for _ in ()).throw(TimeoutError("response lost")),
            )
            self.assertEqual(uncertain.status, "uncertain")

            confirmed = confirm_from_readback(
                publication_id=publication_id,
                state_dir=state_dir,
                remote_url="https://example.test/entry/recovered",
            )
            rerun = publish_once(
                publication_id=publication_id,
                state_dir=state_dir,
                create=lambda: self.fail("confirmed read-back must block create"),
            )

            self.assertTrue(confirmed.confirmed)
            self.assertEqual(rerun, confirmed)


if __name__ == "__main__":
    unittest.main()
