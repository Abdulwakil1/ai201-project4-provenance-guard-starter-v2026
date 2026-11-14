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

1. `app.py` receives the submitted text and creator ID through the `/submit` endpoint. It validates the request and rejects missing, empty or whitespace-only, non-string, non-object, or oversized input with HTTP 400 and a JSON error message before either signal runs. The maximum input length is 2,000 characters. For text shorter than three tokens, `detector.py` raises a `ValueError` (raised while step 2 runs), which `app.py` catches and returns as HTTP 400. Rejected submissions do not receive a decision or an audit entry in Unit 7. For valid submissions, `app.py` generates a unique `content_id`, which can later identify the submission during an appeal.

2. `detector.py` analyzes how predictable the text is using a local GPT-2 model and produces the `model_score`, a value between 0 and 1. A higher score indicates more predictable, AI-like writing. The model processes up to 400 tokens. If a submission exceeds 400 tokens, only the first 400 tokens affect the `model_score`, even if the remaining text is within the 2,000-character limit.

3. `stylometry.py` measures the text's writing characteristics, including sentence-length variation, vocabulary repetition through the ratio of unique words to total words, and punctuation density. It produces the `style_score`, also between 0 and 1, where a higher score indicates more AI-like characteristics. The exact punctuation measurement will be decided in Milestone 4.

4. `scoring.py`, through `combine_signals()`, combines the model score and style score into one combined score between 0 and 1. The final combining rule and weights will be decided in Milestone 4 rather than relying on the starter's temporary 50/50 average.

5. `scoring.py`, through `score_to_label()`, applies the thresholds supplied by `config.py` to classify the combined score. The planned initial thresholds are 0.35 and 0.65: scores at or below 0.35 receive the high-confidence human label, scores at or above 0.65 receive the high-confidence AI label, and scores between them receive the unsure label.

6. `audit.py` records the content ID, creator ID, individual signal scores, combined score, guess, label, decision status, and timestamp in an append-only audit log. A new decision starts with the status `decided`; after an appeal, a new entry is appended with the latest status `under_review`, without overwriting the original decision.

7. Finally, `app.py` returns the result through the `/submit` response, including the `content_id`, `guess`, `confidence`, `label`, `model_score`, and `style_score`. The `confidence` field contains the combined score itself, representing AI-likeness on a 0–1 scale rather than a calibrated probability of AI authorship. A low value indicates human-leaning writing, while a high value indicates AI-leaning writing; therefore, a low value does not mean low certainty.

After receiving the result, a writer who disagrees with the decision can use the `/appeal` endpoint, providing the `content_id` and their reasoning to request a review.

### POST `/submit` — Submission Contract

**Request**

The `/submit` endpoint accepts a JSON object containing the text to analyze and the creator's identifier.

| Field        | Type   | Requirement                                                                        |
| ------------ | ------ | ---------------------------------------------------------------------------------- |
| `text`       | string | Required. Must not be empty or whitespace-only and cannot exceed 2,000 characters. |
| `creator_id` | string | Required. Must not be empty or whitespace-only and cannot exceed 200 characters.   |

**Successful Response — HTTP 200**

When a submission is valid and both signals have been calculated, the endpoint returns a JSON response containing the decision and its supporting scores.

| Field         | Type   | Description                                                                                                                                                                  |
| ------------- | ------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `content_id`  | string | Unique UUID4 identifier assigned to the submission.                                                                                                                          |
| `guess`       | string | Classification result. Values are exactly `ai`, `human`, or `unsure`.                                                                                                        |
| `confidence`  | number | Combined AI-likeness score between 0 and 1. This is a score, not a calibrated probability. Lower values indicate human-leaning text; higher values indicate AI-leaning text. |
| `label`       | string | Full reader-facing sentence explaining the classification, as defined in Label Variants.                                                                                     |
| `model_score` | number | AI-likeness score produced by the language-model signal, between 0 and 1.                                                                                                    |
| `style_score` | number | AI-likeness score produced by the stylometric signal, between 0 and 1.                                                                                                       |

The initial decision is recorded in the audit log with status `decided`. The successful response does not include a separate `status` field.

**Error Responses — HTTP 400**

Invalid submissions are rejected before a decision is made. Rejected submissions do not receive a `content_id` or an audit decision and therefore cannot be appealed.

The endpoint returns HTTP 400 for the following cases:

- Request body is not a JSON object: `invalid_request`.
- `text` or `creator_id` is missing from the request: `missing_field`.
- `text` or `creator_id` is present but is not a string, or contains only whitespace: `invalid_field`.
- `text` exceeds 2,000 characters or `creator_id` exceeds 200 characters: `field_too_long`.
- The GPT-2 tokenizer identifies fewer than three tokens in the text: `text_too_short`. This minimum is based on GPT-2 tokens, not ordinary word count. A confirmed short-input example will be added after tokenizer testing in Milestone 3.

Error responses use a consistent JSON structure. The `error` field identifies the specific failure, while `message` explains the reason:

```json
{
  "error": "text_too_short",
  "message": "Text must contain at least three GPT-2 tokens."
}
```

Unexpected server errors are outside the scope of the Unit 7 endpoint contract.

**Open Implementation Consideration — Stylometry Input**

The current stylometry word-matching pattern recognizes English letters, digits, and apostrophes. Inputs containing only punctuation or unsupported characters, including some accented or non-English text, may produce zero recognized words. Milestone 4 will address this edge case to prevent calculation errors and document the limitations of the stylometric signal.

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
- **Combined score:** 0.74 — using the planned equal weighting of the two signals.

With the planned AI threshold of 0.65, the writer would receive an AI classification. The provisional reader-facing wording is: "This text may have been generated by AI." The final label wording will be established in Milestone 5. The `/submit` response also includes `confidence`, which represents the combined AI-likeness score; whether a client displays that number alongside the label is outside this endpoint contract.

The label itself does not mention the appeal option, so the writer must know that `POST /appeal` is available. The writer can submit an appeal using the returned `content_id` and an explanation. The appeal is recorded as a new audit entry, and the content's latest status becomes `under_review`. It does not automatically rerun either signal, change the original scores, or revise the label or decision already returned.

This hypothetical case shows that equal weighting alone cannot protect against correlated false positives: when both signals lean AI-like for the same human-written text, averaging can reinforce the mistake. Milestone 4 will examine the combining rule, and the threshold and weighting decisions will need to account for the possibility that both signals fail together. The example does not establish a new threshold or weighting value.

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

The style signal is designed to examine three writing characteristics: sentence-length variation, type-token ratio, and punctuation density. Sentence-length variation measures how much sentence lengths differ from one another. Type-token ratio measures the proportion of unique words among all recognized words. Punctuation density measures how frequently punctuation appears relative to the text.

These measures will be combined into a score between 0 and 1, where a higher score indicates more AI-like writing. The intended direction is to treat lower sentence-length variation as more AI-like, so that measure must be inverted when contributing to the score. A lower type-token ratio may indicate more repetitive vocabulary and will be treated as an AI-like tendency, although text length affects this measure. Punctuation density will provide another stylistic feature, but its direction and contribution will be decided in Milestone 4.

**Why that might differ between human and AI writing:**

AI-generated writing may use relatively consistent sentence structures, repeat vocabulary, and follow recognizable punctuation patterns. Human writing may show more variation in sentence length, word choice, and punctuation because of individual writing habits. These are tendencies rather than reliable indicators of authorship. The three measures are designed to capture different aspects of writing style, not to establish whether a person or an AI produced the text.

Although the model signal and style signal measure different properties, they are not independent and can fail together. For example, plain, conventional human writing may be predictable to GPT-2 while also having relatively uniform sentence lengths, causing both signals to lean AI-like. Their actual behavior and contribution to the final score will be checked in Milestone 4.

**What it can't see:**

A human writer who consistently uses short, similarly structured sentences may appear more AI-like based on sentence-length variation. Conversely, AI-generated text deliberately written with varied sentence lengths may appear more human-like. Very short submissions are another limitation: a single-sentence submission does not provide enough sentences to calculate sentence-length variation using standard deviation, and a short text can produce an unstable type-token ratio. Type-token ratio also has a length limitation: longer texts tend to repeat words more often, so a short text and a long text are not directly comparable using this measure alone. Punctuation density cannot distinguish ordinary individual writing habits from deliberately generated punctuation patterns.

The current word-matching pattern may also recognize zero words in punctuation-only text or text containing unsupported characters, including some accented or non-English writing. This creates a potential division-by-zero error in type-token ratio. Milestone 4 will define and implement safe behavior for this case, including what the function returns when no words are recognized. The **Open Implementation Consideration — Stylometry Input** paragraph above documents this issue.

### The combining rule

<!-- Write the rule in words, then give the numbers. What happens when the two
     signals disagree? -->

**The rule:**

The system uses an equal-weight average of the model signal and style signal. Each contributes 50% to the final score. When the signals disagree, their average moderates the result rather than allowing either signal to determine the outcome alone.

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

| Label                 | Score range | The exact text a reader sees |
| --------------------- | ----------- | ---------------------------- |
| high-confidence human |             |                              |
| unsure                |             |                              |
| high-confidence AI    |             |                              |

**Why I worded the "unsure" one this way:**

<!-- It's the hardest of the three. It has to admit uncertainty without
     sounding like an accusation, because the person reading it may well have
     written every word themselves. -->

---

## Sample Run

<!-- One submission and one appeal, pasted as text: the request, the response,
     and the log entries. -->

**A submission**

<!-- The response needs content_id, guess, confidence, label, AND both
     signal scores - model_score and style_score. Unit 8's tools read those
     two off the response, so leaving them out costs you next unit's
     diagnostics. -->

```bash
$ curl -i -X POST http://127.0.0.1:5000/submit \
  -H 'Content-Type: application/json' \
  -d '{"text":"I went to the store this morning and picked up a few things before work.","creator_id":"test-user"}'
```

```http
HTTP/1.1 200 OK
Content-Type: application/json
```

```json
{
  "confidence": 0.5,
  "content_id": "ca50574a-e383-4a79-99e9-0e032f867889",
  "guess": "unsure",
  "label": "not built yet",
  "model_score": 0.8049,
  "style_score": null
}
```

**An appeal**

```bash
$ curl -X POST http://127.0.0.1:5000/appeal \
  -H "Content-Type: application/json" \
  -d '{"content_id": "...", "reasoning": "..."}'
```

```json

```

**What the log shows afterwards**

```bash
$ curl -i http://127.0.0.1:5000/log
```

```json
{
  "count": 1,
  "entries": [
    {
      "combined_score": null,
      "content_id": "ca50574a-e383-4a79-99e9-0e032f867889",
      "creator_id": "test-user",
      "guess": "unsure",
      "label": "not built yet",
      "model_score": 0.8049,
      "status": "decided",
      "style_score": null,
      "timestamp": "2026-11-14T00:24:24+00:00"
    }
  ]
}
```

---

## How I Used AI

**Moment 1**

- _What I asked for:_
- _What came back:_
- _What I changed:_

**Moment 2**

- _What I asked for:_
- _What came back:_
- _What I changed:_

<!-- ═══════════════════════ UNIT 8 — THE TEST ═══════════════════════ -->

---

## Rate Limiting

**My limits:** **_ per minute, _** per day

**Why those numbers and not others:**

<!-- Think about two people: a real writer submitting their own work a few
     times an hour, and a script sending a thousand variations to map your
     thresholds. Your numbers have to be liveable for the first and hostile to
     the second. -->

**What a caller counts as:** <!-- per address, or per creator_id? They fail
differently — one script can look like a thousand callers, and one household
can look like one. -->

**The run of status codes when I pushed past it:**

<!-- python run_attacks.py --flood 15 -->

```

```

---

## Attack Run — Before

<!-- Every attack with its outcome and a held-or-broke mark.
     `run_attacks.py --label before` produces the table. -->

**Ten audit log entries from the run**

<!-- Choose entries that show the interesting failures, not the ten easiest. -->

```json

```

**The single worst outcome** — the one I'd least want to explain to a writer
whose work got caught by it:

---

## Run Log and Verdicts

<!-- Your five criteria across three trials. `run_eval.py --label before`. -->

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
| --------- | ------ | ----- | ----- | ----- | ------- |
| 1.        |        |       |       |       |         |
| 2.        |        |       |       |       |         |
| 3.        |        |       |       |       |         |
| 4.        |        |       |       |       |         |
| 5.        |        |       |       |       |         |

**Real output from one trial**, pasted as text, naming the file and function
that produced it:

```json

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

---

## The Improvement

**What I changed:**

**Which diagnosis pointed at it:**

### Attack Run — After

<!-- Same format. `run_attacks.py --label after` -->

**Did it help, and how do I know:**

<!-- Widening the unsure band usually fixes one problem and creates another.
     Reporting that trade honestly is worth full credit. -->

---

## What's Still Broken

<!-- For each attack still getting through and each criterion still missed:
     what you'd do, and why you stopped. -->

**The trade I'd make if this ran for real:**

<!-- Two sentences. Fewer wrong accusations means more AI text getting through.
     Say which way you'd go and WHO PAYS FOR IT. -->

<!-- ═════════════════════════════════════════════════════════════════════

     SUBMISSION CHECKLIST — unit 7

       [ ] criteria.md has five numbered criteria, each naming a target
       [ ] Each has a reason underneath
       [ ] POST /submit returns content_id, guess, confidence, label,
           model_score and style_score
       [ ] Two signals that measure DIFFERENT things, each with a named blind spot
       [ ] Three label variants, all reachable, written out in full
       [ ] POST /appeal changes status and writes to the log
       [ ] Signals and Scoring names scoring.py::combine_signals
       [ ] Sample Run: a submission AND an appeal, as pasted text
       [ ] At least four new commits
       [ ] Repository URL submitted — WRITE IT DOWN

     SUBMISSION CHECKLIST — unit 8

       [ ] Rate limiting on /submit, with your numbers justified
       [ ] The pasted run of status codes showing 429
       [ ] Audit log with all nine fields, recording rejections too
       [ ] The attack set run IN FULL, every input with an outcome
       [ ] Ten audit log entries pasted as text
       [ ] Five criteria across three trials
       [ ] A diagnosis for every miss and every broken attack — stage AND mechanism
       [ ] One improvement, with Attack Run — After
       [ ] What's Still Broken, including the production trade
       [ ] At least four new commits
       [ ] The SAME repository URL as last unit

     Do not delete and recreate this repository.
     ═════════════════════════════════════════════════════════════════════ -->

---

📖 **How to run this project: [RUNNING.md](RUNNING.md)**
