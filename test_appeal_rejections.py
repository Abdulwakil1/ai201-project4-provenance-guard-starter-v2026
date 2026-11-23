
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import audit
import config
from app import app


class AppealRejectionTests(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)

        temp_path = Path(self.temp_dir.name)

        log_dir_patch = patch.object(config, "LOG_DIR", temp_path)
        audit_log_patch = patch.object(
            config, "AUDIT_LOG", temp_path / "audit.jsonl"
        )

        log_dir_patch.start()
        audit_log_patch.start()

        self.addCleanup(log_dir_patch.stop)
        self.addCleanup(audit_log_patch.stop)

        self.client = app.test_client()

        audit.log_decision(
            content_id="content-123",
            creator_id="creator-123",
            guess="human",
            model_score=0.2,
            style_score=0.5,
            combined_score=0.35,
            label="human",
        )

    def assert_rejection(self, response, status, reason):
        self.assertEqual(response.status_code, status)

        body = response.get_json()
        self.assertEqual(set(body.keys()), {"error", "message"})
        self.assertEqual(body["error"], reason)

        rejected = [
            entry for entry in audit.read_entries()
            if entry.get("event") == "rejected"
        ]

        self.assertEqual(len(rejected), 1)
        self.assertEqual(rejected[0]["reason"], reason)
        self.assertEqual(rejected[0]["endpoint"], "/appeal")

        return rejected[0]

    def test_non_object_request(self):
        response = self.client.post("/appeal", json=[])

        entry = self.assert_rejection(
            response, 400, "invalid_request"
        )
        self.assertEqual(entry["creator_id"], "unknown")

    def test_missing_field(self):
        response = self.client.post(
            "/appeal",
            json={"content_id": "content-123"},
        )

        self.assert_rejection(response, 400, "missing_field")

    def test_invalid_content_id(self):
        response = self.client.post(
            "/appeal",
            json={"content_id": " ", "reasoning": "Please review."},
        )

        self.assert_rejection(response, 400, "invalid_field")

    def test_invalid_reasoning(self):
        response = self.client.post(
            "/appeal",
            json={"content_id": "content-123", "reasoning": " "},
        )

        entry = self.assert_rejection(
            response, 400, "invalid_field"
        )
        self.assertEqual(entry["creator_id"], "creator-123")

    def test_reasoning_too_long(self):
        response = self.client.post(
            "/appeal",
            json={
                "content_id": "content-123",
                "reasoning": "x" * 2001,
            },
        )

        self.assert_rejection(response, 400, "field_too_long")

    def test_content_not_found(self):
        response = self.client.post(
            "/appeal",
            json={
                "content_id": "missing-id",
                "reasoning": "Please review.",
            },
        )

        entry = self.assert_rejection(
            response, 404, "content_not_found"
        )
        self.assertEqual(entry["content_id"], "missing-id")

    def test_creator_not_found(self):
        audit.log_decision(
            content_id="no-creator",
            creator_id="",
        )

        response = self.client.post(
            "/appeal",
            json={
                "content_id": "no-creator",
                "reasoning": "Please review.",
            },
        )

        entry = self.assert_rejection(
            response, 500, "creator_not_found"
        )
        self.assertEqual(entry["creator_id"], "unknown")

    def test_successful_appeal_preserves_original_decision(self):
        original = audit.entries_for("content-123")[0].copy()

        response = self.client.post(
            "/appeal",
            json={
                "content_id": "content-123",
                "reasoning": "I wrote this myself.",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["status"], "under_review")

        entries = audit.entries_for("content-123")

        self.assertEqual(entries[0], original)
        self.assertEqual(entries[-1]["event"], "appeal")
        self.assertEqual(entries[-1]["status"], "under_review")
        self.assertEqual(
            len([e for e in entries if e.get("event") == "rejected"]),
            0,
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
