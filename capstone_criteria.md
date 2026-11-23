# Capstone Acceptance Criteria — Provenance Guard

These criteria define the expected behavior of the Shape B extension before formal capstone evaluation.

## 1. Consistent rejection responses

All seven rejected `/appeal` request paths must return their expected HTTP status and a JSON response containing both `error` and `message` fields.

**Pass condition:** All seven rejection cases return the expected status and both fields with non-empty values.

**Why this target:** The seven rejection paths represent the different ways an appeal can be rejected. Consistent responses make errors predictable for clients and easier to diagnose. Testing every path prevents one correctly handled rejection from masking inconsistent behavior elsewhere.

## 2. Rejection audit integrity

Every rejected appeal must append exactly one corresponding rejection record to the audit log. Each record must identify the `/appeal` endpoint and the expected rejection reason.

**Pass condition:** Each rejected request produces exactly one new audit record with the correct endpoint, rejection reason, and associated `content_id` when one is available.

**Why this target:** A rejected appeal should not disappear without an audit record or create duplicate records for one request. Recording the endpoint and rejection reason makes failed appeal attempts traceable and supports accountability.

## 3. Original decision preservation after rejection

Rejecting an appeal must not modify the original decision record, including its decision status and recorded scores.

**Pass condition:** The original decision record is identical before and after each tested rejected appeal.

**Why this target:** The original decision is part of the system audit history. Rejecting an appeal must not rewrite that history. Comparing the original record before and after rejection provides direct evidence that it remains unchanged.

## 4. Successful appeal preservation

A valid appeal must return HTTP 200 with an `under_review` status, append an appeal audit record, and leave the original decision unchanged.

**Pass condition:** The response and audit record show `under_review`, and the original decision record remains identical.

**Why this target:** A successful appeal changes the review status, not the original decision. Keeping the appeal record separate preserves the decision history while allowing a disputed result to be reviewed.

## 5. Existing route regression protection

The existing `/ping` and `/submit` routes must continue to function after the extension. The `/submit` regression test must use mocked signal and scoring functions to avoid unnecessary model inference.

**Pass condition:** `/ping` returns HTTP 200 with the expected response, and a valid mocked `/submit` request returns HTTP 200 with the expected decision and audit record.

**Why this target:** An extension should not break existing functionality. Checking `/ping` and `/submit` helps establish that the appeal changes have not disrupted the application's existing routes.

---

## Formal Evaluation

Each criterion will be evaluated in three separate trials. Results will record the actual outcome of each trial, including failures. Repeated trials demonstrate whether the behavior is reproducible; they do not represent testing across independent datasets or environments.
