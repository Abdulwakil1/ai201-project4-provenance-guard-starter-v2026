import json
import time
import requests

BASE_URL = "http://127.0.0.1:5000"
FIELDS = [
    "content_id", "creator_id", "guess", "model_score",
    "style_score", "combined_score", "label", "status"
]

for trial in range(1, 4):
    print(f"\nTRIAL {trial}")
    for i in range(1, 4):
        if trial > 1 or i > 1:
            time.sleep(7)

        submitted = requests.post(
            f"{BASE_URL}/submit",
            json={
                "text": (
                    f"I wrote this original reflection for appeal test "
                    f"{trial}-{i}. Consistent effort and learning help "
                    f"people develop skills and achieve meaningful goals."
                ),
                "creator_id": f"appeal_test_{trial}_{i}"
            },
            timeout=90
        )
        decision = submitted.json()
        assert submitted.status_code == 200, decision
        content_id = decision["content_id"]

        before = requests.get(f"{BASE_URL}/log").json()["entries"]
        original = next(
            e for e in reversed(before)
            if e.get("content_id") == content_id
            and e.get("status") == "decided"
        )

        time.sleep(7)
        appealed = requests.post(
            f"{BASE_URL}/appeal",
            json={
                "content_id": content_id,
                "reasoning": f"I am requesting a review of decision {trial}-{i}."
            },
            timeout=30
        )
        result = appealed.json()

        after = requests.get(f"{BASE_URL}/log").json()["entries"]
        matching = [e for e in after if e.get("content_id") == content_id]

        preserved = all(
            original.get(field) == next(
                (e.get(field) for e in matching
                 if e.get("status") == "decided"),
                None
            )
            for field in FIELDS
        )
        appeal_entries = [
            e for e in matching if e.get("event") == "appeal"
        ]
        latest_status = matching[-1].get("status") if matching else None

        print(json.dumps({
            "submit_status": submitted.status_code,
            "appeal_status": appealed.status_code,
            "response_status": result.get("status"),
            "new_appeal_entry": len(appeal_entries) == 1,
            "latest_audit_status": latest_status,
            "original_decision_preserved": preserved
        }))
        assert appealed.status_code == 200
        assert result.get("status") == "under_review"
        assert len(appeal_entries) == 1
        assert latest_status == "under_review"
        assert preserved

print("\nALL NINE APPEAL CHECKS PASSED")
