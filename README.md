# Provenance Guard

> ### 👋 Start here
>
> **New to this repo? Read [RUNNING.md](RUNNING.md) first.**
>
> Once `python test.py` passes, in one terminal:
>
> ```bash
> python app.py
> ```
>
> and in another:
>
> ```bash
> curl -X POST http://127.0.0.1:5000/ping \
>   -H "Content-Type: application/json" \
>   -d '{"message": "hello"}'
> ```
>
> That's a web service. Something sent it text and it sent something back.
> Everything this unit is filling in the middle.
>
> **The rest of this file is your submission.** Fill it in as you go.

---

<!-- ─────────────────────────────────────────────────────────────────────────
     Unit 7 asks for the first five sections. Unit 8 adds the five below.

     Everything is pasted as TEXT. A pasted curl response gets full credit;
     a picture of your terminal gets none.
     ───────────────────────────────────────────────────────────────────────── -->

<!-- ═══════════════════════ UNIT 7 — THE BUILD ═══════════════════════ -->

## What This Does

<!-- The path a submission takes, from arriving to the label a reader sees.
     Six or seven steps — this is the trace you wrote in Milestone 1. -->

1. `app.py` receives the submitted text and creator ID through the `/submit` endpoint. It validates the request and rejects missing, empty or whitespace-only, non-string, non-object, or oversized input with HTTP 400 and a JSON error message before either signal runs. The maximum input length is 2,000 characters. For text shorter than three GPT-2 tokens, `detector.py` raises a `ValueError`, which `app.py` catches and returns as HTTP 400. Rejected submissions do not receive a decision or a `content_id`, but each route-level rejection is recorded in the audit log with its timestamp, creator ID when valid (otherwise `unknown`), and rejection reason. For valid submissions, `app.py` generates a unique `content_id`, which can later identify the submission during an appeal.

2. `detector.py` analyzes how predictable the text is using a local GPT-2 model and produces the `model_score`, a value between 0 and 1. A higher score indicates more predictable, AI-like writing. The model processes up to 400 tokens. If a submission exceeds 400 tokens, only the first 400 tokens affect the `model_score`, even if the remaining text is within the 2,000-character limit.

3. `stylometry.py` measures the text's writing characteristics: sentence-length variation, vocabulary repetition through the ratio of unique words to total words, and punctuation density. It produces the `style_score`, also between 0 and 1, where a higher score indicates more AI-like characteristics. Punctuation density is calculated as a separate diagnostic measure and is not included in the style score.

4. `scoring.py`, through `combine_signals()`, combines the model score and style score into one combined score between 0 and 1. The implementation uses an equal-weight average: 50% model score and 50% style score. Both signals point in the same direction, with higher scores indicating more AI-like writing.

5. `scoring.py`, through `score_to_label()`, applies the thresholds supplied by `config.py` to classify the combined score. Scores at or below 0.35 receive the high-confidence human label, scores at or above 0.65 receive the high-confidence AI label, and scores between those thresholds receive the unsure label.

6. `audit.py` records successful decisions in an append-only audit log with all nine decision fields: timestamp, content ID, creator ID, guess, model score, style score, combined score, label, and status. A new decision starts with the status `decided`; after an appeal, a new entry is appended with the status `under_review`, without overwriting the original decision. Rejected requests are recorded separately as rejection events with a timestamp, creator ID when valid (otherwise `unknown`), status `rejected`, and a reason. Rejection entries do not contain decision scores because no decision was made.

7. Finally, `app.py` returns the result through the `/submit` response, including the `content_id`, `guess`, `confidence`, `label`, `model_score`, `style_score`, and `combined_score`. The `confidence` field contains the combined score itself, representing AI-likeness on a 0–1 scale rather than a calibrated probability of AI authorship. A low value indicates human-leaning writing, while a high value indicates AI-leaning writing.

After receiving the result, a writer who disagrees with the decision can use the `/appeal` endpoint, providing the `content_id` and their reasoning to request a review. The endpoint verifies that the submission exists and records the appeal without changing the original decision.

### POST `/submit` — Submission Contract

**Request**

The `/submit` endpoint accepts a JSON object containing the text to analyze and the creator's identifier.

Input length limits are centralized in `config.py`:
- `MAX_TEXT_LENGTH`: maximum submission text length (2,000 characters).
- `MAX_CREATOR_ID_LENGTH`: maximum creator ID length (200 characters).
- `MAX_REASONING_LENGTH`: maximum appeal reasoning length (2,000 characters).

The `/submit` and `/appeal` endpoints use these settings for validation and their corresponding `field_too_long` error messages.

| Field        | Type   | Requirement                                                                        |
| ------------ | ------ | ---------------------------------------------------------------------------------- |
| `text`       | string | Required. Must not be empty or whitespace-only and cannot exceed 2,000 characters. |
| `creator_id` | string | Required. Must not be empty or whitespace-only and cannot exceed 200 characters.   |

**Successful Response — HTTP 200**

When a submission is valid and both signals have been calculated, the endpoint returns a JSON response containing the decision and its supporting scores.

| Field            | Type   | Description                                                                                                                                                                  |
| ---------------- | ------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `content_id`     | string | Unique UUID4 identifier assigned to the submission.                                                                                                                          |
| `guess`          | string | Classification result. Values are exactly `ai`, `human`, or `unsure`.                                                                                                        |
| `confidence`     | number | Combined AI-likeness score between 0 and 1. This is a score, not a calibrated probability. Lower values indicate human-leaning text; higher values indicate AI-leaning text. |
| `label`          | string | Full reader-facing sentence explaining the classification, as defined in Label Variants.                                                                                     |
| `model_score`    | number | AI-likeness score produced by the language-model signal, between 0 and 1.                                                                                                    |
| `style_score`    | number | AI-likeness score produced by the stylometric signal, between 0 and 1.                                                                                                       |
| `combined_score` | number | Final AI-likeness score calculated by combining the model and style signals.                                                                                                 |

The initial decision is recorded in the audit log with status `decided`. The successful response does not include a separate `status` field.

**Error Responses — HTTP 400**

Invalid submissions are rejected before a decision is made. Rejected submissions do not receive a `content_id` or an audit decision and therefore cannot be appealed. These HTTP 400 rejections are nevertheless recorded in the audit log as rejection events, with a timestamp, creator ID when valid (otherwise `unknown`), status `rejected`, and a reason.

The endpoint returns HTTP 400 for the following cases:

- Request body is not a JSON object: `invalid_request`.
- `text` or `creator_id` is missing from the request: `missing_field`.
- `text` or `creator_id` is present but is not a string, or contains only whitespace: `invalid_field`.
- `text` exceeds 2,000 characters or `creator_id` exceeds 200 characters: `field_too_long`.
- The GPT-2 tokenizer identifies fewer than three tokens in the text: `text_too_short`. This minimum is based on GPT-2 tokens, not ordinary word count.

Error responses use a consistent JSON structure. The `error` field identifies the specific failure, while `message` explains the reason:

```json
{
  "error": "text_too_short",
  "message": "Text must contain at least three GPT-2 tokens."
}
```

Unexpected server errors are outside the scope of the Unit 7 endpoint contract.

**Open Implementation Consideration — Stylometry Input**

The current stylometry word-matching pattern recognizes English letters, digits, and apostrophes. Inputs containing only punctuation or unsupported characters, including some accented or non-English text, may produce zero recognized words. The implementation handles this edge case by returning 0.0 for the individual measures and a neutral 0.5 for the overall style signal when no words are recognized. However, the signal remains limited by its English-oriented word-matching pattern and does not interpret the meaning or language of the text.

### POST `/appeal` — Appeal Contract

**Request**

The `/appeal` endpoint accepts a JSON object containing the identifier of an existing submission and the writer's reasoning for requesting a review.

| Field        | Type   | Requirement                                                                        |
| ------------ | ------ | ---------------------------------------------------------------------------------- |
| `content_id` | string | Required. Must identify an existing submission.                                    |
| `reasoning`  | string | Required. Must not be empty or whitespace-only and cannot exceed 2,000 characters. |

The creator identifier is retrieved from the original submission's audit record; the writer does not need to provide it again.

**Successful Response — HTTP 200**

When an appeal is accepted, the endpoint returns a JSON response confirming that the submission is under review.

| Field        | Type   | Description                                                   |
| ------------ | ------ | ------------------------------------------------------------- |
| `content_id` | string | Identifier of the appealed submission.                        |
| `status`     | string | `under_review`, indicating that the appeal has been recorded. |
| `message`    | string | Confirmation that the appeal was received.                    |

**Error Responses**

- HTTP 400 — `invalid_request`: The request body is not a JSON object.
- HTTP 400 — `missing_field`: `content_id` or `reasoning` is missing from the request.
- HTTP 400 — `invalid_field`: `content_id` or `reasoning` is present but is not a string, or `reasoning` is empty or whitespace-only.
- HTTP 400 — `field_too_long`: `reasoning` exceeds 2,000 characters.
- HTTP 404 — `content_not_found`: The supplied `content_id` is a string that does not identify an existing submission. Malformed ID strings receive the same response as unknown IDs.

Each accepted appeal creates an additional audit entry. Repeated appeals are accepted and recorded separately. Each successful appeal response reports `under_review`, and the latest audit entry is the source of truth for the submission's current status. Appeals do not overwrite the original decision or previous appeal records.

For Unit 7, the endpoint does not independently verify that the person submitting an appeal is the original creator. Anyone who knows a submission's `content_id` can request an appeal.

**False-positive trace (hypothetical, not measured)**

Imagine a person writes a short, conventional thank-you note:

> Thank you for taking the time to meet with me. I appreciate your consideration and look forward to hearing from you. Please let me know if you need any additional information.

This is ordinary human writing, but both signals could interpret its predictable wording and relatively uniform sentence lengths as AI-like. For illustration only, the following are designed scores, not measured results:

- **Model score:** 0.78 — the conventional wording could be predictable to GPT-2.
- **Style score:** 0.70 — the relatively uniform sentence lengths could lean AI-like.
- **Combined score:** 0.74 — using the implemented equal weighting of the two signals.

With the implemented AI threshold of 0.65, the writer would receive an AI classification. The reader-facing label would be: "We think this was probably written by AI." The `/submit` response also includes `confidence`, which represents the combined AI-likeness score rather than a calibrated probability. Whether a client displays that number alongside the label is outside this endpoint contract.

The label itself does not mention the appeal option, so the writer must know that `POST /appeal` is available. The writer can submit an appeal using the returned `content_id` and an explanation. The appeal is recorded as a new audit entry, and the content's latest status becomes `under_review`. It does not automatically rerun either signal, change the original scores, or revise the label or decision already returned.

This hypothetical case shows that equal weighting alone cannot protect against correlated false positives: when both signals lean AI-like for the same human-written text, averaging can reinforce the mistake. The current implementation uses equal weighting and thresholds of 0.35 and 0.65. These choices are documented implementation decisions, not evidence that the system reliably avoids false positives. The example remains hypothetical and does not represent a measured test result.

---

## Signals and Scoring

<!-- For each signal: what property it measures, why that might differ between
     human and AI writing, and WHAT IT CAN'T SEE.

     The blind spot is not optional. If you can't name it you don't understand
     the signal yet — and unit 8's attack set is built out of blind spots. -->

### Signal one — the model signal

**What it measures:**

The model signal uses GPT-2 perplexity to measure how predictable the submitted text is to the language model. The detector converts this measurement into a score between 0 and 1 using a logistic function. Lower perplexity produces a higher AI-likeness score, while higher perplexity produces a lower score. The current midpoint (45) and steepness (1.6) are unchanged from the starter implementation.

**Why that might differ between human and AI writing:**

AI-generated writing may follow statistically predictable language patterns because language models generate text based on patterns learned during training. Human writing may contain more unexpected word choices, irregular phrasing, and personal expressions that make it less predictable. However, these are tendencies, not reliable proof of authorship.

**What it can't see:**

Perplexity cannot distinguish predictable human writing from predictable AI writing. For example, a human-written cover letter using conventional phrases such as "I am writing to express my interest" may receive a higher AI-likeness score because its wording is predictable. Conversely, AI-generated text containing deliberately inserted rare names, specialized jargon, or spelling errors may become less predictable and receive a lower AI-likeness score.

This implementation also uses GPT-2, an older and smaller language model, and scores only the first 400 tokens. Writing generated by newer models may not have the same predictability to GPT-2. Unusual content appearing after the first 400 tokens cannot affect the model score. The same limitation applies to human writing: predictable boilerplate near the beginning of a submission can influence the score even if the writing that follows is less predictable.

### Signal two — the style signal

**What it measures:**

The style signal examines three writing characteristics: sentence-length variation, type-token ratio, and punctuation density.

- Sentence-length variation measures how much recognized-word counts differ across sentences. It uses the sample standard deviation divided by the mean sentence length, capped at 1.0.
- Type-token ratio measures the proportion of unique recognized words among all recognized words. A lower ratio indicates more vocabulary repetition.
- Punctuation density measures punctuation characters relative to the number of recognized words. It is calculated as a separate diagnostic measure and is not included in the style score.

The `style_score` ranges from 0 to 1, with higher values indicating more AI-like characteristics. For text containing at least two sentences with recognized words, the score averages two inverted measures: 1 minus sentence-length variation and 1 minus type-token ratio. For text with fewer than two such sentences, the score uses the inverted type-token ratio alone. If no words are recognized, the function returns a neutral style score of 0.5.

**Why that might differ between human and AI writing:**

AI-generated writing may use relatively consistent sentence structures and repeat vocabulary. Human writing may show more variation in sentence length and word choice because of individual writing habits. These are tendencies rather than reliable indicators of authorship. The style signal captures characteristics of writing, not proof that a person or an AI produced it.

Although the model signal and style signal measure different properties, they are not independent and can fail together. For example, conventional human writing may be predictable to GPT-2 while also having relatively uniform sentence lengths, causing both signals to lean AI-like. Because the system combines them using an equal-weight average, correlated errors can reinforce one another.

**What it can't see:**

A human writer who consistently uses short, similarly structured sentences may appear more AI-like based on sentence-length variation. Conversely, AI-generated text deliberately written with varied sentence lengths may appear more human-like. Very short submissions provide limited stylistic evidence: a single sentence cannot establish sentence-length variation, and a short text can produce an unstable type-token ratio. Type-token ratio also has a length limitation: longer texts tend to repeat words more often, so short and long texts are not directly comparable using this measure alone.

Punctuation density cannot distinguish ordinary individual writing habits from deliberately generated punctuation patterns. Although it is calculated, it does not contribute to the final style score.

The current word-matching pattern recognizes English letters, digits, and apostrophes. It may not recognize some accented or non-English words. When no words are recognized, the implementation avoids division-by-zero errors by returning 0.0 for the individual measures and 0.5 for the overall style score. This fallback prevents a calculation error, but it does not make the style signal reliable for unsupported languages or text without recognized words.

### The combining rule

<!-- Write the rule in words, then give the numbers. What happens when the two
     signals disagree? -->

**The rule:**

The system uses an equal-weight average of the model signal and style signal. Each contributes 50% to the final score. When the signals disagree, their average places the combined score between the two individual scores, balancing their contributions equally.

**The numbers:**

- Model signal: 0.50 (50%)
- Style signal: 0.50 (50%)

**Where it lives:** `scoring.py::combine_signals`

<!-- ⚠️ The grader checks your code against that line. If your rule lives
     somewhere else, say where. -->

**A case where my two signals split, and what my rule does with it:**

The borderline sample about technology produced a model score of 0.8099 and a style score of 0.3014. The model signal leaned AI-like, while the style signal leaned human-like. Their equal-weight average is approximately 0.5557, bringing the combined result closer to the uncertain middle rather than strongly favoring either signal.

---

## Label Variants

<!-- The exact text of all three labels, as a reader would see them, and the
     score range each covers.

     Write them for someone who has never heard the word "threshold". -->

| Label                 | Score range                          | The exact text a reader sees                                                  |
| --------------------- | ------------------------------------ | ----------------------------------------------------------------------------- |
| high-confidence human | 0.00–0.35                            | We think this was probably written by a person.                               |
| unsure                | Greater than 0.35 and less than 0.65 | We couldn't confidently determine whether this was written by a person or AI. |
| high-confidence AI    | 0.65–1.00                            | We think this was probably written by AI.                                     |

**Why I worded the "unsure" one this way:**

<!-- It's the hardest of the three. It has to admit uncertainty without
     sounding like an accusation, because the person reading it may well have
     written every word themselves. -->

The wording communicates uncertainty without accusing the writer. It acknowledges that the system cannot always confidently distinguish human-written text from AI-generated text.

---

## Sample Run

<!-- One submission and one appeal, pasted as text: the request, the response,
     and the log entries. -->

The following example demonstrates a successful submission, the resulting classification, an accepted appeal, and the corresponding audit log entries.

**A submission**

<!-- The response needs content_id, guess, confidence, label, AND both
     signal scores - model_score and style_score. Unit 8's tools read those
     two off the response, so leaving them out costs you next unit's
     diagnostics. -->

```bash
$ curl -s -X POST http://127.0.0.1:5000/submit \
  -H 'Content-Type: application/json' \
  -d '{"text":"I believe this is a useful test of the content review system. It is important to evaluate writing carefully and fairly.","creator_id":"milestone5-test"}'
```

```json
{
  "combined_score": 0.43215000000000003,
  "confidence": 0.43215000000000003,
  "content_id": "61bb3c29-2c82-4f8c-bf4d-424abb55031e",
  "guess": "unsure",
  "label": "We couldn't confidently determine whether this was written by a person or AI.",
  "model_score": 0.4415,
  "style_score": 0.4228
}
```

**An appeal**

```bash
$ curl -s -X POST http://127.0.0.1:5000/appeal \
  -H 'Content-Type: application/json' \
  -d '{"content_id":"61bb3c29-2c82-4f8c-bf4d-424abb55031e","reasoning":"I wrote this content myself. Please review the classification because the system may have incorrectly assessed my writing."}'
```

```json
{
  "content_id": "61bb3c29-2c82-4f8c-bf4d-424abb55031e",
  "message": "Appeal submitted successfully.",
  "status": "under_review"
}
```

**What the log shows afterwards**

```bash
$ curl -s http://127.0.0.1:5000/log
```

The log contained four entries. The following two entries belong to the submission and appeal demonstrated above:

```json
[
  {
    "combined_score": 0.43215000000000003,
    "content_id": "61bb3c29-2c82-4f8c-bf4d-424abb55031e",
    "creator_id": "milestone5-test",
    "guess": "unsure",
    "label": "We couldn't confidently determine whether this was written by a person or AI.",
    "model_score": 0.4415,
    "status": "decided",
    "style_score": 0.4228,
    "timestamp": "2026-11-15T05:39:32+00:00"
  },
  {
    "content_id": "61bb3c29-2c82-4f8c-bf4d-424abb55031e",
    "creator_id": "milestone5-test",
    "event": "appeal",
    "reasoning": "I wrote this content myself. Please review the classification because the system may have incorrectly assessed my writing.",
    "status": "under_review",
    "timestamp": "2026-11-15T05:42:13+00:00"
  }
]
```

The original decision remains unchanged, and the appeal is recorded as a separate audit entry. The latest entry establishes the submission's current status as `under_review`.

---

## How I Used AI

**Moment 1 — Implementing the appeal endpoint**

- _What I asked for:_ Help reviewing the `/appeal` endpoint, particularly how to validate an appeal and verify that its `content_id` belongs to an existing decision.
- _What came back:_ Guidance to validate the JSON body and fields, look up the original decision using `audit.entries_for()`, retrieve its `creator_id`, and record the appeal using `audit.log_appeal()`.
- _What I changed:_ I implemented those validation and lookup steps, connected the endpoint to the audit functions, and tested invalid requests and a successful appeal. The endpoint appends an `under_review` entry without overwriting the original decision.

**Moment 2 — Checking the style signal documentation**

- _What I asked for:_ Help checking whether my README explanation of the style signal accurately described what the code calculates.
- _What came back:_ A review that distinguished the three calculated measures from the two that contribute to `style_score`, and identified limitations involving short text, unsupported words, and punctuation density.
- _What I changed:_ I revised the README to match the implementation: sentence-length variation and type-token ratio contribute to the style score, while punctuation density is diagnostic only. I also documented edge cases and limitations rather than presenting the signal as proof of authorship.

### Unit 8

**Moment 1 — Diagnosing attack and evaluation results**

- _What I asked for:_ Help interpreting the attack-run results and evaluating my five acceptance criteria across three trials, including identifying why attacks were marked BROKE.
- _What came back:_ Guidance to trace each failure through the five stages: route, signal one, signal two, combining rule, and label mapping. The review also helped distinguish measured failures from assumptions about why they occurred.
- _What I changed:_ I reviewed the evidence, documented the failure mechanisms in the README, and recorded which criteria were MET or MISSED. I kept the original targets rather than changing them to make the results look better.

**Moment 2 — Choosing and implementing the improvement**

- _What I asked for:_ Help selecting one focused improvement based on the Unit 8 diagnosis, without attempting to fix unrelated weaknesses at the same time.
- _What came back:_ A recommendation to address malformed input at the `/submit` route before either scoring signal runs, specifically rejecting unsupported control characters and text without recognizable letters or numbers.
- _What I changed:_ I added the validation in `app.py::submit`, using Python `unicodedata` and the existing `stylometry.words()` function. I compiled the application and tested the rejection behavior before rerunning the attack set.

**Moment 3 — Evaluating the improvement and documenting limitations**

- _What I asked for:_ Help comparing the before-and-after results, interpreting the remaining failures, and checking that my README claims were supported by the reports and audit log.
- _What came back:_ Guidance to distinguish the malformed-input cases that were fixed from the evasion attacks, false positive, prompt-injection cases, and score-spread criterion that remained unresolved. It also helped identify where the evidence did not establish causation.
- _What I changed:_ I reviewed the results, documented the before-and-after comparison, preserved the remaining failures and production trade-off, and committed the final reports and README changes.

<!-- ═══════════════════════ UNIT 8 — THE TEST ═══════════════════════ -->

---

## Rate Limiting

**My limits:** 10 per minute, 200 per day

**Why those numbers and not others:**

<!-- Think about two people: a real writer submitting their own work a few
     times an hour, and a script sending a thousand variations to map your
     thresholds. Your numbers have to be liveable for the first and hostile to
     the second. -->

These limits allow a legitimate writer to submit multiple pieces of work while restricting automated scripts that repeatedly submit content to probe the detector. Ten submissions per minute provides a reasonable short-term limit, while 200 per day allows normal usage without permitting unlimited requests.

**What a caller counts as:**
Requests are counted by `creator_id` when a valid creator ID is provided. If it is missing or invalid, the limiter falls back to the caller's IP address. This helps prevent one creator from bypassing the limit by sending requests from different addresses.

**The run of status codes when I pushed past it:**

<!-- python run_attacks.py --flood 15 -->

```text
15 submissions as 'flood_tester'

[ 1/15] 200
[ 2/15] 200
[ 3/15] 200
[ 4/15] 200
[ 5/15] 200
[ 6/15] 200
[ 7/15] 200
[ 8/15] 200
[ 9/15] 200
[10/15] 200
[11/15] 429
[12/15] 429
[13/15] 429
[14/15] 429
[15/15] 429

5 of 15 were rate limited.
```

---

## Attack Run — Before

<!-- Full attack outcomes and verdicts: `results/attack_run_2026-11-17_0322.md` -->

**Attack results:** 56 attacks were tested. **43 HELD and 13 BROKE.**

The complete attack-by-attack results, including HTTP status, classification, scores, and human-reviewed verdicts, are recorded in [`results/attack_run_2026-11-17_0322.md`](results/attack_run_2026-11-17_0322.md).

### Ten audit log entries from the run

These entries include successful decisions, validation rejections, and rate-limit rejections.

```json
[
  {
    "combined_score": 0.6846,
    "content_id": "2bdcb8af-b97c-4ac7-ac88-435488725e46",
    "creator_id": "attacker_FP05",
    "guess": "ai",
    "label": "We think this was probably written by AI.",
    "model_score": 0.8005,
    "status": "decided",
    "style_score": 0.5687,
    "timestamp": "2026-11-17T08:22:05+00:00"
  },
  {
    "combined_score": 0.3239,
    "content_id": "3f4a8b5c-abfd-433b-892a-2805221c80e6",
    "creator_id": "attacker_EV01",
    "guess": "human",
    "label": "We think this was probably written by a person.",
    "model_score": 0.1635,
    "status": "decided",
    "style_score": 0.4843,
    "timestamp": "2026-11-17T08:21:59+00:00"
  },
  {
    "combined_score": 0.8109999999999999,
    "content_id": "523442d5-e3de-4ca8-aef0-f27e8377b871",
    "creator_id": "attacker_EV10",
    "guess": "ai",
    "label": "We think this was probably written by AI.",
    "model_score": 0.9792,
    "status": "decided",
    "style_score": 0.6428,
    "timestamp": "2026-11-17T08:22:03+00:00"
  },
  {
    "combined_score": 0.0,
    "content_id": "0b4aed27-259e-4738-b03f-e5da9a4fa894",
    "creator_id": "attacker_MF03",
    "guess": "human",
    "label": "We think this was probably written by a person.",
    "model_score": 0.0,
    "status": "decided",
    "style_score": 0.0,
    "timestamp": "2026-11-17T08:22:08+00:00"
  },
  {
    "combined_score": 0.7484500000000001,
    "content_id": "563db827-fc9c-462a-8736-b7c17a7f9123",
    "creator_id": "attacker_MF06",
    "guess": "ai",
    "label": "We think this was probably written by AI.",
    "model_score": 0.9969,
    "status": "decided",
    "style_score": 0.5,
    "timestamp": "2026-11-17T08:22:09+00:00"
  },
  {
    "combined_score": 0.4605,
    "content_id": "d470d353-e15b-4b94-8037-cddc746bb77b",
    "creator_id": "attacker_PI05",
    "guess": "unsure",
    "label": "We couldn't confidently determine whether this was written by a person or AI.",
    "model_score": 0.6401,
    "status": "decided",
    "style_score": 0.2809,
    "timestamp": "2026-11-17T08:22:07+00:00"
  },
  {
    "creator_id": "attacker_RQ03",
    "event": "rejected",
    "reason": "invalid_field",
    "status": "rejected",
    "timestamp": "2026-11-17T08:22:10+00:00"
  },
  {
    "creator_id": "unknown",
    "event": "rejected",
    "reason": "missing_field",
    "status": "rejected",
    "timestamp": "2026-11-17T08:22:10+00:00"
  },
  {
    "creator_id": "attacker_flood",
    "event": "rejected",
    "limit": "10 per 1 minute",
    "reason": "rate_limited",
    "status": "rejected",
    "timestamp": "2026-11-17T08:22:12+00:00"
  },
  {
    "creator_id": "attacker_flood",
    "event": "rejected",
    "limit": "10 per 1 minute",
    "reason": "rate_limited",
    "status": "rejected",
    "timestamp": "2026-11-17T08:22:12+00:00"
  }
]
```

### The single worst outcome

The failure I would least want to explain to a writer whose work was incorrectly flagged:

**Attack FP05 — Technical documentation targeted as human-written**

**Input:**

> To configure the service, edit the settings file in the installation directory. Set the host value to the address the service should bind to. Set the port value to an unused port above 1024. Save the file and restart the service. The service will log its startup configuration. If the port is already in use, the service will exit with an error. Check the log file for details before retrying.

**System response:**

- HTTP status: `200`
- Guess: `ai`
- Combined score: `0.6846`
- Model signal: `0.8005`
- Style signal: `0.5687`
- Label: "We think this was probably written by AI."

**Diagnosis:**

The primary weakness was the model signal. The text had low GPT-2 perplexity (18.9), producing a high model score of 0.8005. The style signal also leaned AI-like: its relatively uniform sentence lengths contributed to a style score of 0.5687.

The scoring rule gave both signals equal weight (0.5 each). Their average was 0.6846, exceeding the AI threshold of 0.65, so the label mapping classified the submission as AI-written.

The underlying limitation is that conventional, predictable technical writing can also have low perplexity and uniform sentence structure. Consequently, genuine human writing can be incorrectly flagged. The attack set identifies this input as human-written; authorship was not independently verified.

---

## Run Log and Verdicts

<!-- Five original acceptance criteria, evaluated across three trials. -->

| Criterion              | Target                                                                        | Run 1                | Run 2                | Run 3                | Verdict |
| ---------------------- | ----------------------------------------------------------------------------- | -------------------- | -------------------- | -------------------- | ------- |
| 1. False positives     | At most 1/10 labeled `ai`; all 10 valid HTTP 200                              | 0/10; 10/10 HTTP 200 | 0/10; 10/10 HTTP 200 | 0/10; 10/10 HTTP 200 | MET     |
| 2. Score spread        | AI mean at least 0.30 above human mean; both sets valid HTTP 200              | +0.065660            | +0.065660            | +0.065660            | MISSED  |
| 3. Label coverage      | All three labels reached through `/submit`                                    | human, unsure, ai    | human, unsure, ai    | human, unsure, ai    | MET     |
| 4. Appeal recording    | At least 3 successful appeals; audit entries and original decisions preserved | 3/3                  | 3/3                  | 3/3                  | MET     |
| 5. Invalid submissions | All 7 cases rejected with correct HTTP 400 codes; no decision created         | 7/7                  | 7/7                  | 7/7                  | MET     |

**After-run evidence:** [Evaluation results](results/run_2026-11-21_0508_after.md) · [Appeal results](results/appeal_run_2026-11-21_after.md)

**Criterion 5 audit verification:** I manually reviewed `logs/audit.jsonl` after the three evaluation trials. All 21 invalid submissions produced one rejection event each, with the expected error reason and `status: "rejected"`. The entries had no `content_id` or completed decision fields, and none created a `status: "decided"` record. The `run_eval.py` runner recorded the HTTP responses but did not automate before-and-after audit snapshots; the audit-log verification was performed separately.

**Real output from one trial**

Source: `test_appeals.py`; application route `app.py::appeal`; audit function `audit.py::log_appeal`. Trial 1, three appeals:

```json
{"submit_status":200,"appeal_status":200,"response_status":"under_review","new_appeal_entry":true,"latest_audit_status":"under_review","original_decision_preserved":true}
{"submit_status":200,"appeal_status":200,"response_status":"under_review","new_appeal_entry":true,"latest_audit_status":"under_review","original_decision_preserved":true}
{"submit_status":200,"appeal_status":200,"response_status":"under_review","new_appeal_entry":true,"latest_audit_status":"under_review","original_decision_preserved":true}
```

**Diagnoses**

<!-- For each miss AND each broken attack: the stage and the mechanism.

     Your service has five stages: the route, signal one, signal two, the
     combining rule, and the label mapping.

     Not a diagnosis:  "The evasion attacks got through."
     A diagnosis:      "Four evasion inputs got through. All four had typos
                        added to AI-generated text. My second signal measures
                        word variety, and typos raise word variety — so it read
                        them as more human. My combining rule weights that
                        signal at 0.6, so it dragged the whole score down."

     Look for a pattern. Five failures on one signal is one problem, not five. -->

- **Criterion 2 — score spread: MISSED.** The combining rule in `scoring.py::combine_signals` gives both signals equal weight (0.5 each). Across all three trials, the combined AI mean was only 0.065660 above the human mean, below the 0.30 target. The two signals, when averaged equally, did not produce enough separation between the tested human and AI samples. The evidence establishes the gap, but does not establish that changing either weight alone would fix it.

- **Evasion — EV01, EV02, EV03, EV06, EV07: BROKE.** These attacks primarily targeted signal two, `stylometry.py::style_signal`. Its vocabulary and sentence-length measurements can be changed without changing who wrote the text: typos increase apparent word variety, while broken-up sentences and pasted quotations change sentence-length patterns. The signal interprets those changes as more human-like, lowering the combined score.

- **Evasion — EV04: BROKE.** This attack targeted signal one, `detector.py::model_signal`. Unusual vocabulary raises perplexity, which lowers the model's AI-oriented score. The model therefore interprets an edited AI text as less predictable and more human-like.

- **Evasion — EV05 and EV09: BROKE.** These attacks targeted both signals. Human editing can change vocabulary and sentence structure, while adding a human-written opening to AI-generated text creates mixed authorship within one submission. Neither signal can reliably identify that mixture. The equal-weight combining rule averages the two imperfect readings rather than detecting the change in authorship.

- **Evasion — EV08: BROKE.** This short-text attack passed the route because the input was non-empty and within the character limit. Signal one accepted it because the tokenizer produced enough tokens to pass its minimum-length check, but returned a low AI score (0.2452). Signal two also returned a relatively low score (0.3586). The combining rule produced a human-range score, and the label mapping classified it as human.

- **False positive — FP05: BROKE.** Both signals contributed. Signal one gave human-written technical documentation a high AI score (0.8005), consistent with its predictable language. Signal two also gave it a high score (0.5687), consistent with its regular sentence lengths and vocabulary patterns. The equal-weight combining rule produced 0.6846, above the 0.65 AI threshold, so the label mapping classified the human-written sample as AI.

- **Malformed input — MF03, MF04, MF06: BROKE.** The route in `app.py::submit` checks for a non-empty string and a maximum length, but does not verify that the text contains meaningful words. The detector consequently scored control characters, punctuation, and emoji-only input instead of rejecting them. Signal two returns 0.5 when it finds no recognized words. The combining rule then produces scores that reach the label mapping: MF03 and MF04 were classified as human, while MF06 was classified as AI. These are decisions about malformed input, not reliable authorship assessments.

---

## The Improvement

**What I changed:**

I added route-level text validation in `app.py::submit` before either scoring signal runs. The route now rejects submissions containing unsupported control characters and submissions without at least one recognizable letter or number. These rejections are recorded in the audit log with the reason `invalid_text_content`.

**Which diagnosis pointed at it:**

The diagnosis of MF03, MF04, and MF06 showed that the original route accepted control-character-only, punctuation-only, and emoji-only submissions and allowed them to receive authorship classifications. The problem was at the route/input-validation stage, before either signal could provide a meaningful assessment.

### Attack Run — After

<!-- Same format. `run_attacks.py --label after` -->

**Attack results:** 56 attacks were tested. The runner reported zero automatic failures (5xx responses, crashes, or missing responses). After manual review, 12 attacks were marked BROKE and 44 HELD.

The complete attack-by-attack results, including HTTP status, classification, scores, and verdicts, are recorded in [`results/attack_run_2026-11-21_0243_after.md`](results/attack_run_2026-11-21_0243_after.md).

I reran the complete attack set using `python run_attacks.py --set attack_set --label after`. All 56 attacks were submitted and manually reviewed. The 12 BROKE attacks were EV01–EV09, FP05, PI01, and PI02; the remaining 44 were HELD. The complete verdicts are recorded in the linked report.

The three previously broken malformed-input attacks now return HTTP 400:

- MF03 — control characters: rejected (`invalid_text_content`).
- MF04 — punctuation only: rejected (`invalid_text_content`).
- MF06 — emoji only: rejected (`invalid_text_content`).

The other malformed-input cases and all 12 request-validation cases also returned HTTP 400. The flood test produced ten accepted submissions followed by two HTTP 429 responses, consistent with the configured limit of 10 requests per minute.

**Before-and-after comparison:**

| Measure                                              |   Before |    After |
| ---------------------------------------------------- | -------: | -------: |
| Previously broken malformed cases (MF03, MF04, MF06) |        3 |        0 |
| Total attacks marked BROKE                           |       13 |       12 |
| Total attacks marked HELD                            |       43 |       44 |
| Score spread (AI mean minus human mean)              | 0.065660 | 0.065660 |

**Did it help, and how do I know:**

<!-- Widening the unsure band usually fixes one problem and creates another.
     Reporting that trade honestly is worth full credit. -->

Yes, it fixed the specific malformed-input weakness targeted by this improvement. The after-run report shows MF03, MF04, and MF06 returning HTTP 400 instead of receiving human or AI classifications, and the audit log records all three as rejected with `invalid_text_content`. However, this single change did not resolve the evasion attacks, the FP05 false positive, or the missed score-spread criterion.

---

## What's Still Broken

**What remains unresolved and what I would do next:**

- **Criterion 2 — score spread:** I would collect a broader, representative set of human and AI samples and investigate signal calibration and weighting. I stopped because the current results establish poor separation, but do not show that changing weights alone would solve it.
- **Evasion — EV01–EV09:** I would improve resistance to superficial changes in vocabulary, punctuation, sentence structure, and mixed authorship. These failures involve both signals and, in some cases, their combination. I stopped because addressing them requires a broader change to the detection approach, not another route-validation adjustment.
- **False positive — FP05:** I would test and calibrate the model against more human-written technical documentation before changing the AI threshold. I stopped because lowering false positives without measuring the effect on AI detection could create another weakness.
- **Prompt injection — PI01 and PI02:** I would investigate whether embedded instructions affect the scoring signals and add targeted tests. Although both were marked BROKE, the observed classifications alone do not establish that the embedded instructions caused those results.

**The trade I would make if this ran for real:**

I would prioritize avoiding false accusations by making borderline cases more likely to receive an `unsure` result rather than a confident AI label. The cost is that some AI-generated content would also receive `unsure` or avoid an AI classification, shifting more review work to moderators and users who depend on detection.

---

📖 **How to run this project: [RUNNING.md](RUNNING.md)**

## Capstone

### What This Extends

I am extending Provenance Guard using Shape B — Harden Against Failure. The extension focuses on the `/appeal` endpoint: rejected appeals must return a consistent error response and create an audit record without changing the original decision. I will add repeatable tests to verify rejection behavior and audit integrity. The application will run locally with structured logs using Path B.

### Running It

The project uses Path B: local execution with structured logs. The clean-checkout setup, environment requirements, dependency installation, test command, and local server startup instructions are documented in [`RUNNING.md`](RUNNING.md).

In brief, create and activate a virtual environment, install `requirements.txt`, run `python test.py`, and start the service with `python app.py`. The service listens at `http://127.0.0.1:5000`. The first request requiring model scoring downloads the local GPT-2 model; no API key or hosted inference service is used.

**Out of Scope**

- Changing the detection model, stylometry signal, scoring weights, or classification thresholds.
- Reworking multilingual text detection or adding new detection capabilities.
- Public hosting or redesigning the application interface.

**Instrumentation**

The application writes structured request/response records to `logs/capstone_runs.jsonl`, separately from the existing audit log. Each record includes a UTC timestamp, HTTP method, endpoint, input, output, status code, application processing duration, and success indicator.

I verified both a successful `/ping` request and a rejected `/appeal` request. The rejected request returned HTTP 400 with the expected `missing_field` error and was recorded with `success: false`.

**Sample Run Log**

The following ten consecutive successful `/ping` measurement records and one rejected `/appeal` request were copied from `logs/capstone_runs.jsonl`.

```json
{"timestamp": "2026-11-24T10:28:54.060870+00:00", "method": "POST", "path": "/ping", "input": {"message": "measurement"}, "output": {"ok": true, "service": "provenance-guard", "you_sent": "measurement"}, "status_code": 200, "duration_ms": 0.611, "success": true}
{"timestamp": "2026-11-24T10:28:54.178864+00:00", "method": "POST", "path": "/ping", "input": {"message": "measurement"}, "output": {"ok": true, "service": "provenance-guard", "you_sent": "measurement"}, "status_code": 200, "duration_ms": 0.337, "success": true}
{"timestamp": "2026-11-24T10:28:54.547727+00:00", "method": "POST", "path": "/ping", "input": {"message": "measurement"}, "output": {"ok": true, "service": "provenance-guard", "you_sent": "measurement"}, "status_code": 200, "duration_ms": 1.105, "success": true}
{"timestamp": "2026-11-24T10:28:54.869346+00:00", "method": "POST", "path": "/ping", "input": {"message": "measurement"}, "output": {"ok": true, "service": "provenance-guard", "you_sent": "measurement"}, "status_code": 200, "duration_ms": 0.678, "success": true}
{"timestamp": "2026-11-24T10:28:55.019107+00:00", "method": "POST", "path": "/ping", "input": {"message": "measurement"}, "output": {"ok": true, "service": "provenance-guard", "you_sent": "measurement"}, "status_code": 200, "duration_ms": 0.264, "success": true}
{"timestamp": "2026-11-24T10:28:55.167830+00:00", "method": "POST", "path": "/ping", "input": {"message": "measurement"}, "output": {"ok": true, "service": "provenance-guard", "you_sent": "measurement"}, "status_code": 200, "duration_ms": 0.555, "success": true}
{"timestamp": "2026-11-24T10:28:55.307287+00:00", "method": "POST", "path": "/ping", "input": {"message": "measurement"}, "output": {"ok": true, "service": "provenance-guard", "you_sent": "measurement"}, "status_code": 200, "duration_ms": 0.297, "success": true}
{"timestamp": "2026-11-24T10:28:55.477336+00:00", "method": "POST", "path": "/ping", "input": {"message": "measurement"}, "output": {"ok": true, "service": "provenance-guard", "you_sent": "measurement"}, "status_code": 200, "duration_ms": 0.41, "success": true}
{"timestamp": "2026-11-24T10:28:55.603004+00:00", "method": "POST", "path": "/ping", "input": {"message": "measurement"}, "output": {"ok": true, "service": "provenance-guard", "you_sent": "measurement"}, "status_code": 200, "duration_ms": 0.26, "success": true}
{"timestamp": "2026-11-24T10:28:55.725536+00:00", "method": "POST", "path": "/ping", "input": {"message": "measurement"}, "output": {"ok": true, "service": "provenance-guard", "you_sent": "measurement"}, "status_code": 200, "duration_ms": 0.259, "success": true}
```

Rejected `/appeal` request (HTTP 400):

```json
{
  "timestamp": "2026-11-24T10:24:21.628779+00:00",
  "method": "POST",
  "path": "/appeal",
  "input": {},
  "output": {
    "error": "missing_field",
    "message": "Both content_id and reasoning are required."
  },
  "status_code": 400,
  "duration_ms": 1.689,
  "success": false
}
```

**What It Costs**

This project runs locally and does not use a paid API or hosted inference service for these measurements.

I measured application processing time using the `duration_ms` field in the structured run log. I sent ten POST requests to `/ping` with the input `{"message":"measurement"}`.

- Successful requests: 10 out of 10
- Average application processing time: 0.4776 ms per request
- Fastest: 0.259 ms
- Slowest: 1.105 ms

This is a measured local compute-time proxy, not a monetary hosting or API cost. The measurement covers the `/ping` endpoint, not GPT-2 inference.

At an illustrative volume of 100 requests per day, applying this measured `/ping` average gives 47.76 ms of cumulative application processing time per day (100 × 0.4776 ms). This is only arithmetic based on the `/ping` measurement; it is not a forecast for `/submit`, GPT-2 inference, total elapsed user wait time, or monetary cost.

### Formal Evaluation

The five acceptance criteria are defined in [`capstone_criteria.md`](capstone_criteria.md). Each criterion was evaluated in three separate trials using the regression suite. Each trial ran the same 11 tests; the repeated runs check reproducibility, not performance across independent datasets or environments.

| Trial | Tests passed | Test-suite duration | Overall result |
| ----- | -----------: | ------------------: | -------------- |
| 1     |        11/11 |             0.094 s | MET            |
| 2     |        11/11 |             0.083 s | MET            |
| 3     |        11/11 |             0.100 s | MET            |

The complete terminal outputs are preserved in the repository:

- [Trial 1 log](results/capstone_trial_1.log)
- [Trial 2 log](results/capstone_trial_2.log)
- [Trial 3 log](results/capstone_trial_3.log)

#### Criteria verdicts

| Criterion                                         | Trial 1 | Trial 2 | Trial 3 | Evidence covered                                                                                              |
| ------------------------------------------------- | ------- | ------- | ------- | ------------------------------------------------------------------------------------------------------------- |
| 1. Consistent rejection responses                 | MET     | MET     | MET     | All seven rejection paths; exact HTTP statuses, error codes, and messages                                     |
| 2. Rejection audit integrity                      | MET     | MET     | MET     | Exactly one rejection record per rejected request, with the expected endpoint, reason, and `content_id` value |
| 3. Original decision preservation after rejection | MET     | MET     | MET     | Original decision record compared before and after rejected appeals                                           |
| 4. Successful appeal preservation                 | MET     | MET     | MET     | HTTP 200, `under_review`, appeal audit record, and unchanged original decision                                |
| 5. Existing route regression protection           | MET     | MET     | MET     | `/ping` response and valid mocked `/submit` response and decision audit record                                |

Each trial ran `python -m unittest -v test_appeal_rejections.py`. The suite includes the seven rejection-path tests, preservation checks, a successful appeal test, a `/ping` test, and a mocked `/submit` regression test. The `/submit` test mocks the detector and scoring functions so it verifies route behavior without downloading or running GPT-2.

#### Test Evidence

The following output is from Trial 1 (`results/capstone_trial_1.log`). The same 11 tests passed in Trials 2 and 3.

**Criterion 1 — Consistent rejection responses**

Source: `test_appeal_rejections.py`, rejection test methods and `assert_rejection()`.

The seven rejection tests verify the expected HTTP status, exact JSON keys (`error` and `message`), error code, and message for each rejection scenario.

```text
test_content_not_found ... ok
test_creator_not_found ... ok
test_invalid_content_id ... ok
test_invalid_reasoning ... ok
test_missing_field ... ok
test_non_object_request ... ok
test_reasoning_too_long ... ok
```

**Criterion 2 — Rejection audit integrity**

Source: `test_appeal_rejections.py`, `assert_rejection()`.

For each rejected request, the helper verifies exactly one rejection audit record, the expected reason, the `/appeal` endpoint, and the expected `content_id` when available. The non-object and creator-not-found tests also verify the expected fallback `creator_id`.

**Criterion 3 — Original decision preservation**

Source: `test_appeal_rejections.py`, `assert_rejection()` and `test_rejected_appeal_preserves_original_decision()`.

The tests compare the original decision before and after rejection. The dedicated preservation test also verifies that the rejection record is appended without replacing the original decision.

```text
test_rejected_appeal_preserves_original_decision ... ok
```

**Criterion 4 — Successful appeal preservation**

Source: `test_appeal_rejections.py`, `test_successful_appeal_preserves_original_decision()`.

The test verifies HTTP 200, `under_review`, an appeal audit record, preservation of the original decision, and no rejection record.

```text
test_successful_appeal_preserves_original_decision ... ok
```

**Criterion 5 — Existing route regression protection**

Source: `test_appeal_rejections.py`, `test_ping()` and `test_successful_submission()`.

The `/ping` test checks the expected response. The mocked `/submit` test checks the decision response, scoring fields, and audit record without running GPT-2 inference.

```text
test_ping ... ok
test_successful_submission ... ok
```

**Trial 1 summary**

```text
Ran 11 tests in 0.094s

OK
```

#### Diagnosis

All five criteria were MET in all three recorded trials. There were no failed test cases in these final runs, so there is no observed failure from these trials to diagnose. The repeated results support the tested rejection, audit, preservation, and route-regression behaviors. They do not establish performance under production traffic or the latency of real model inference.

### Capstone Improvement

I strengthened the regression tests after reviewing the evaluation criteria and the earlier test assertions.

- Rejection tests now compare the original decision record before and after each rejected appeal.
- The audit assertions verify the exact expected `content_id`, including `None` when the request does not provide a usable content ID, rather than merely checking that a present value is non-empty.
- The assertions also verify the expected HTTP status, exact JSON response keys, error code, message, audit reason, and `/appeal` endpoint.

The final three trial logs above were generated after these stronger assertions were added. This improvement strengthens the evidence and test precision; it did not change the application's scoring model or rejection behavior.

### What's Still Broken / What's Still Left

The capstone criteria and regression tests cover the Shape B appeal-hardening extension. Several areas remain outside the evidence collected so far:

- The ten-request timing measurement above uses `/ping`. It does not measure GPT-2 inference or the full `/submit` processing path.
- The `/submit` regression test uses mocked signal and scoring functions. It verifies route integration and audit behavior, not real-model inference latency.
- No ten-times-normal-rate load test or hosted deployment test is included in these results.
- The local Path B setup is documented in [`RUNNING.md`](RUNNING.md), but these tests do not establish production readiness, multi-user behavior, or performance under sustained traffic.

A useful next measurement would time real `/submit` requests after the model is loaded, report the individual durations and average, and keep model-loading time separate from warm-request processing time. A separate controlled load test would be needed before making claims about higher request rates.

### How I Used AI

**Moment 1 — Reviewing capstone feedback and refining acceptance criteria**

- _What I asked for:_ Help interpreting the capstone grader's feedback and identifying which requirements needed stronger evidence or clearer acceptance criteria.

- _What came back:_ The feedback highlighted the need to verify all seven rejected-appeal scenarios, check exact response details, confirm audit records, and ensure rejected appeals did not change the original decision.

- _What I changed:_ I clarified the five capstone criteria, documented the expected status codes, error codes, and messages for each rejection scenario, and made the evaluation expectations more specific.

**Moment 2 — Strengthening appeal rejection tests**

- _What I asked for:_ Help reviewing the regression tests to make sure they verified the rejection responses and audit behavior rather than only checking whether an error occurred.

- _What came back:_ The review identified the importance of checking exact response keys and values, exactly one rejection audit record, the expected rejection reason and endpoint, the associated `content_id`, and preservation of the original decision.

- _What I changed:_ I strengthened the test assertions and expanded the rejection tests to cover all seven scenarios. I also retained tests for successful appeals, `/ping`, and `/submit` so the existing routes remained covered.

**Moment 3 — Evaluating repeatability and documenting limitations**

- _What I asked for:_ Help organizing the formal evaluation results and documenting what the local instrumentation actually measured.

- _What came back:_ The three trial logs showed all 11 tests passing in each run. The review also clarified that the recorded `/ping` measurements represented application processing time, not GPT-2 inference time or a complete production-performance measurement.

- _What I changed:_ I documented the three trial results, recorded the measured `/ping` average and the illustrative 100-requests-per-day calculation, and explicitly identified what remains untested, including real `/submit` inference timing, 10x load testing, and hosted deployment.
