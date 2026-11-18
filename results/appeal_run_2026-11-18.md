# Appeal Test Results — Milestone 3, Criterion 4

- Test driver: `test_appeals.py`
- Application route: `app.py::appeal`
- Audit function: `audit.py::log_appeal`
- Date: 2026-11-18
- Three trials, three appeals per trial.
## Trial 1

```json
{"submit_status":200,"appeal_status":200,"response_status":"under_review","new_appeal_entry":true,"latest_audit_status":"under_review","original_decision_preserved":true}
{"submit_status":200,"appeal_status":200,"response_status":"under_review","new_appeal_entry":true,"latest_audit_status":"under_review","original_decision_preserved":true}
{"submit_status":200,"appeal_status":200,"response_status":"under_review","new_appeal_entry":true,"latest_audit_status":"under_review","original_decision_preserved":true}
```
## Trial 2

```json
{"submit_status":200,"appeal_status":200,"response_status":"under_review","new_appeal_entry":true,"latest_audit_status":"under_review","original_decision_preserved":true}
{"submit_status":200,"appeal_status":200,"response_status":"under_review","new_appeal_entry":true,"latest_audit_status":"under_review","original_decision_preserved":true}
{"submit_status":200,"appeal_status":200,"response_status":"under_review","new_appeal_entry":true,"latest_audit_status":"under_review","original_decision_preserved":true}
```
## Trial 3

```json
{"submit_status":200,"appeal_status":200,"response_status":"under_review","new_appeal_entry":true,"latest_audit_status":"under_review","original_decision_preserved":true}
{"submit_status":200,"appeal_status":200,"response_status":"under_review","new_appeal_entry":true,"latest_audit_status":"under_review","original_decision_preserved":true}
{"submit_status":200,"appeal_status":200,"response_status":"under_review","new_appeal_entry":true,"latest_audit_status":"under_review","original_decision_preserved":true}
```
## Verdict

**MET — 9/9 appeals succeeded.**

All nine appeals returned HTTP 200 and `under_review`, appended exactly one appeal entry, left the latest audit status as `under_review`, and preserved the original decision fields.
