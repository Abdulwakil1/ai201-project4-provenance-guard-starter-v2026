# Attack run — after

- Produced by: `run_attacks.py::main`
- Service: `app.py::submit`
- 56 attacks · 2026-11-21 02:43
- Auto-marked BROKE (5xx, crash, no response): **0**
- Manual review completed: **12 BROKE, 44 HELD**

The runner leaves attacks for human review when it cannot determine a
verdict from the response alone. The Verdict column below contains the
completed manual assessment, based on each attack target and observed result.

Each attack submits as creator_id `attacker_<id>`, and the content_id it
came back with is in the table — either one will match this run against your
audit log when you go looking for the ten entries to paste.

| ID | Family | Targeting | Status | Content ID | Guess | Score | Verdict |
|---|---|---|---|---|---|---|---|
| EV01 | evasion | signal two: typos raise word variety | 200 | `fc0979c5-3f44-4cad-87cb-9310483391fa` | human | 0.324 | BROKE |
| EV02 | evasion | signal two: broken-up sentences raise length spread | 200 | `3457a0d9-1147-4697-bd34-5e93544b46e8` | unsure | 0.379 | BROKE |
| EV03 | evasion | signal two: a pasted quotation changes the shape | 200 | `f4013dd9-9a36-4c08-9fba-4fe065df809f` | unsure | 0.512 | BROKE |
| EV04 | evasion | signal one: unusual words raise perplexity | 200 | `9a72258c-0300-4640-b371-20fda257c81c` | unsure | 0.544 | BROKE |
| EV05 | evasion | both signals: heavy human editing pass | 200 | `1c21822c-33d2-4834-86dc-4918e0d297f9` | human | 0.300 | BROKE |
| EV06 | evasion | signal two: one very long sentence and one very short | 200 | `53fa95d7-4f08-41dd-96fc-98ba8cc847f6` | human | 0.349 | BROKE |
| EV07 | evasion | signal two: padding with punctuation | 200 | `b3b2edbb-649c-4173-baac-ea97ff359386` | unsure | 0.407 | BROKE |
| EV08 | evasion | signal one: text below the token window | 200 | `d2859a3c-1b77-4485-856d-edc69444c506` | human | 0.302 | BROKE |
| EV09 | evasion | both: AI text with a human opening paragraph bolted on | 200 | `704e1089-7911-4be1-a84b-f18071d7b404` | unsure | 0.524 | BROKE |
| EV10 | evasion | signal two: repeated stanza structure | 200 | `bc643e15-1e2b-4c4b-98e5-1ab7ff8031ed` | ai | 0.811 | HELD |
| FP01 | false_positive | plain, clear human writing with no flourishes | 200 | `5fe792a0-6c5b-4c87-ba46-b8b1a4ae93f4` | unsure | 0.517 | HELD |
| FP02 | false_positive | human writing in a formal register | 200 | `f088df8c-c5b0-496d-aad5-777fa558d940` | unsure | 0.632 | HELD |
| FP03 | false_positive | a non-native English speaker writing carefully | 200 | `5108ea0a-5847-4bb9-9dc5-cbfa340bdc75` | unsure | 0.640 | HELD |
| FP04 | false_positive | a student essay written to a rubric | 200 | `978f8cef-dbde-43f9-af77-9d25b7bb0f57` | unsure | 0.623 | HELD |
| FP05 | false_positive | technical documentation written by a person | 200 | `99699558-11da-494e-832b-40de77a02d7f` | ai | 0.685 | BROKE |
| FP06 | false_positive | a person imitating a formal template | 200 | `afd87b40-29dd-445f-85f6-8d51503a3003` | unsure | 0.627 | HELD |
| FP07 | false_positive | human writing that repeats a phrase deliberately | 200 | `4db7c137-d764-4645-beac-4b63f2449b31` | unsure | 0.644 | HELD |
| FP08 | false_positive | very short genuine human submission | 200 | `2b0955c3-b83f-42a7-b0ed-93e17d9fee23` | human | 0.303 | HELD |
| PI01 | prompt_injection | instruction to ignore the check | 200 | `d41d7de3-775b-4b35-8eb5-f0b43fac17df` | human | 0.332 | BROKE |
| PI02 | prompt_injection | instruction disguised as a system message | 200 | `b7c27446-3329-44ac-87c3-68e9c1f2676a` | human | 0.200 | BROKE |
| PI03 | prompt_injection | instruction wrapped in the writer's voice | 200 | `94915da5-8002-457b-bb03-ddb37e0c7099` | unsure | 0.484 | HELD |
| PI04 | prompt_injection | attempt to make the label text hostile | 200 | `ff7c6ec0-96c1-45ca-b410-e49a4761d36e` | unsure | 0.435 | HELD |
| PI05 | prompt_injection | attempt to inject into the audit log | 200 | `d6fa690d-956c-4873-9a31-e6b97274f34a` | unsure | 0.461 | HELD |
| PI06 | prompt_injection | instruction plus real human text | 200 | `0f17d901-1428-4d37-a76a-6988ac781f05` | unsure | 0.491 | HELD |
| MF01 | malformed | text is only whitespace | 400 | `—` | — | — | HELD |
| MF02 | malformed | text is a single character | 400 | `—` | — | — | HELD |
| MF03 | malformed | text is control characters | 400 | `—` | — | — | HELD |
| MF04 | malformed | text is only punctuation | 400 | `—` | — | — | HELD |
| MF05 | malformed | text is a very long single word | 400 | `—` | — | — | HELD |
| MF06 | malformed | text is emoji only | 400 | `—` | — | — | HELD |
| MF07 | malformed | text is right-to-left script | 400 | `—` | — | — | HELD |
| MF08 | malformed | text is 60,000 characters | 400 | `—` | — | — | HELD |
| RQ01 | malformed | no text field at all | 400 | `—` | — | — | HELD |
| RQ02 | malformed | no creator_id | 400 | `—` | — | — | HELD |
| RQ03 | malformed | text is a number | 400 | `—` | — | — | HELD |
| RQ04 | malformed | text is a list | 400 | `—` | — | — | HELD |
| RQ05 | malformed | text is null | 400 | `—` | — | — | HELD |
| RQ06 | malformed | creator_id is an object | 400 | `—` | — | — | HELD |
| RQ07 | malformed | body is a JSON array, not an object | 400 | `—` | — | — | HELD |
| RQ08 | malformed | body is unparseable JSON | 400 | `—` | — | — | HELD |
| RQ09 | malformed | body is empty | 400 | `—` | — | — | HELD |
| RQ10 | malformed | body is form-encoded, not JSON | 400 | `—` | — | — | HELD |
| RQ11 | malformed | body is JSON claiming to be plain text | 400 | `—` | — | — | HELD |
| RQ12 | malformed | deeply nested JSON | 400 | `—` | — | — | HELD |
| FL01_01 | flood_same_creator | 20 rapid submissions from one creator | 200 | `5e5e8055-e755-4436-bd15-46152489d4d9` | human | 0.014 | HELD |
| FL01_02 | flood_same_creator | 20 rapid submissions from one creator | 200 | `d7ce49f4-49d9-44c6-b66c-3bc17411d914` | human | 0.014 | HELD |
| FL01_03 | flood_same_creator | 20 rapid submissions from one creator | 200 | `9e568664-c616-4898-ae4e-747343ed86ae` | human | 0.014 | HELD |
| FL01_04 | flood_same_creator | 20 rapid submissions from one creator | 200 | `0c3a10f1-1844-4b73-bfc3-0f753f086ac9` | human | 0.014 | HELD |
| FL01_05 | flood_same_creator | 20 rapid submissions from one creator | 200 | `7bcd7682-28c7-4b73-a914-ab2b0104f877` | human | 0.014 | HELD |
| FL01_06 | flood_same_creator | 20 rapid submissions from one creator | 200 | `7084fb9c-8f83-4eab-96c6-bd24d81f69ad` | human | 0.014 | HELD |
| FL01_07 | flood_same_creator | 20 rapid submissions from one creator | 200 | `14d2fafc-a0ee-401f-a947-3ddbffa471b4` | human | 0.014 | HELD |
| FL01_08 | flood_same_creator | 20 rapid submissions from one creator | 200 | `31908bad-fdec-46d1-a9bb-413a607eb403` | human | 0.014 | HELD |
| FL01_09 | flood_same_creator | 20 rapid submissions from one creator | 200 | `c00006dd-ffcb-4c2c-879c-8fc589b86bbb` | human | 0.014 | HELD |
| FL01_10 | flood_same_creator | 20 rapid submissions from one creator | 200 | `679c91e9-1969-4778-9329-d04f0a8a1511` | human | 0.014 | HELD |
| FL01_11 | flood_same_creator | 20 rapid submissions from one creator | 429 | `—` | — | — | HELD |
| FL01_12 | flood_same_creator | 20 rapid submissions from one creator | 429 | `—` | — | — | HELD |

---

## By family

| Family | Attacks | BROKE | HELD |
|---|---:|---:|---:|
| `evasion` | 10 | 9 | 1 |
| `false_positive` | 8 | 1 | 7 |
| `flood_same_creator` | 12 | 0 | 12 |
| `malformed` | 20 | 0 | 20 |
| `prompt_injection` | 6 | 2 | 4 |

> The **false_positive** family is the one to look at hardest. Those are
> written to be genuine human writing that reads as machine-like. Every one
> your service calls AI is a real writer it would have accused.

---

## What came back

The detail behind the table. Paste the interesting failures into your
README — the ones that show something, not the ten easiest.

### EV01 — `evasion`

*Targeting:* signal two: typos raise word variety

```json
{
  "id": "EV01",
  "status": 200,
  "content_id": "fc0979c5-3f44-4cad-87cb-9310483391fa",
  "creator_id": "attacker_EV01",
  "guess": "human",
  "confidence": 0.3239,
  "model_score": 0.1635,
  "style_score": 0.4843,
  "label": "We think this was probably written by a person.",
  "error": null,
  "verdict": "BROKE"
}
```

### EV02 — `evasion`

*Targeting:* signal two: broken-up sentences raise length spread

```json
{
  "id": "EV02",
  "status": 200,
  "content_id": "3457a0d9-1147-4697-bd34-5e93544b46e8",
  "creator_id": "attacker_EV02",
  "guess": "unsure",
  "confidence": 0.3788,
  "model_score": 0.5943,
  "style_score": 0.1633,
  "label": "We couldn't confidently determine whether this was written by a person or AI.",
  "error": null,
  "verdict": "BROKE"
}
```

### EV03 — `evasion`

*Targeting:* signal two: a pasted quotation changes the shape

```json
{
  "id": "EV03",
  "status": 200,
  "content_id": "f4013dd9-9a36-4c08-9fba-4fe065df809f",
  "creator_id": "attacker_EV03",
  "guess": "unsure",
  "confidence": 0.51235,
  "model_score": 0.6662,
  "style_score": 0.3585,
  "label": "We couldn't confidently determine whether this was written by a person or AI.",
  "error": null,
  "verdict": "BROKE"
}
```

### EV04 — `evasion`

*Targeting:* signal one: unusual words raise perplexity

```json
{
  "id": "EV04",
  "status": 200,
  "content_id": "9a72258c-0300-4640-b371-20fda257c81c",
  "creator_id": "attacker_EV04",
  "guess": "unsure",
  "confidence": 0.5442,
  "model_score": 0.6114,
  "style_score": 0.477,
  "label": "We couldn't confidently determine whether this was written by a person or AI.",
  "error": null,
  "verdict": "BROKE"
}
```

### EV05 — `evasion`

*Targeting:* both signals: heavy human editing pass

```json
{
  "id": "EV05",
  "status": 200,
  "content_id": "1c21822c-33d2-4834-86dc-4918e0d297f9",
  "creator_id": "attacker_EV05",
  "guess": "human",
  "confidence": 0.29969999999999997,
  "model_score": 0.3212,
  "style_score": 0.2782,
  "label": "We think this was probably written by a person.",
  "error": null,
  "verdict": "BROKE"
}
```

### EV06 — `evasion`

*Targeting:* signal two: one very long sentence and one very short

```json
{
  "id": "EV06",
  "status": 200,
  "content_id": "53fa95d7-4f08-41dd-96fc-98ba8cc847f6",
  "creator_id": "attacker_EV06",
  "guess": "human",
  "confidence": 0.34885,
  "model_score": 0.5727,
  "style_score": 0.125,
  "label": "We think this was probably written by a person.",
  "error": null,
  "verdict": "BROKE"
}
```

### EV07 — `evasion`

*Targeting:* signal two: padding with punctuation

```json
{
  "id": "EV07",
  "status": 200,
  "content_id": "b3b2edbb-649c-4173-baac-ea97ff359386",
  "creator_id": "attacker_EV07",
  "guess": "unsure",
  "confidence": 0.40650000000000003,
  "model_score": 0.5862,
  "style_score": 0.2268,
  "label": "We couldn't confidently determine whether this was written by a person or AI.",
  "error": null,
  "verdict": "BROKE"
}
```

### EV08 — `evasion`

*Targeting:* signal one: text below the token window

```json
{
  "id": "EV08",
  "status": 200,
  "content_id": "d2859a3c-1b77-4485-856d-edc69444c506",
  "creator_id": "attacker_EV08",
  "guess": "human",
  "confidence": 0.3019,
  "model_score": 0.2452,
  "style_score": 0.3586,
  "label": "We think this was probably written by a person.",
  "error": null,
  "verdict": "BROKE"
}
```

### EV09 — `evasion`

*Targeting:* both: AI text with a human opening paragraph bolted on

```json
{
  "id": "EV09",
  "status": 200,
  "content_id": "704e1089-7911-4be1-a84b-f18071d7b404",
  "creator_id": "attacker_EV09",
  "guess": "unsure",
  "confidence": 0.5235000000000001,
  "model_score": 0.7042,
  "style_score": 0.3428,
  "label": "We couldn't confidently determine whether this was written by a person or AI.",
  "error": null,
  "verdict": "BROKE"
}
```

### EV10 — `evasion`

*Targeting:* signal two: repeated stanza structure

```json
{
  "id": "EV10",
  "status": 200,
  "content_id": "bc643e15-1e2b-4c4b-98e5-1ab7ff8031ed",
  "creator_id": "attacker_EV10",
  "guess": "ai",
  "confidence": 0.8109999999999999,
  "model_score": 0.9792,
  "style_score": 0.6428,
  "label": "We think this was probably written by AI.",
  "error": null,
  "verdict": "HELD"
}
```

### FP01 — `false_positive`

*Targeting:* plain, clear human writing with no flourishes

```json
{
  "id": "FP01",
  "status": 200,
  "content_id": "5fe792a0-6c5b-4c87-ba46-b8b1a4ae93f4",
  "creator_id": "attacker_FP01",
  "guess": "unsure",
  "confidence": 0.5172,
  "model_score": 0.6175,
  "style_score": 0.4169,
  "label": "We couldn't confidently determine whether this was written by a person or AI.",
  "error": null,
  "verdict": "HELD"
}
```

### FP02 — `false_positive`

*Targeting:* human writing in a formal register

```json
{
  "id": "FP02",
  "status": 200,
  "content_id": "f088df8c-c5b0-496d-aad5-777fa558d940",
  "creator_id": "attacker_FP02",
  "guess": "unsure",
  "confidence": 0.63165,
  "model_score": 0.7387,
  "style_score": 0.5246,
  "label": "We couldn't confidently determine whether this was written by a person or AI.",
  "error": null,
  "verdict": "HELD"
}
```

### FP03 — `false_positive`

*Targeting:* a non-native English speaker writing carefully

```json
{
  "id": "FP03",
  "status": 200,
  "content_id": "5108ea0a-5847-4bb9-9dc5-cbfa340bdc75",
  "creator_id": "attacker_FP03",
  "guess": "unsure",
  "confidence": 0.63975,
  "model_score": 0.8051,
  "style_score": 0.4744,
  "label": "We couldn't confidently determine whether this was written by a person or AI.",
  "error": null,
  "verdict": "HELD"
}
```

### FP04 — `false_positive`

*Targeting:* a student essay written to a rubric

```json
{
  "id": "FP04",
  "status": 200,
  "content_id": "978f8cef-dbde-43f9-af77-9d25b7bb0f57",
  "creator_id": "attacker_FP04",
  "guess": "unsure",
  "confidence": 0.6226,
  "model_score": 0.8329,
  "style_score": 0.4123,
  "label": "We couldn't confidently determine whether this was written by a person or AI.",
  "error": null,
  "verdict": "HELD"
}
```

### FP05 — `false_positive`

*Targeting:* technical documentation written by a person

```json
{
  "id": "FP05",
  "status": 200,
  "content_id": "99699558-11da-494e-832b-40de77a02d7f",
  "creator_id": "attacker_FP05",
  "guess": "ai",
  "confidence": 0.6846,
  "model_score": 0.8005,
  "style_score": 0.5687,
  "label": "We think this was probably written by AI.",
  "error": null,
  "verdict": "BROKE"
}
```

### FP06 — `false_positive`

*Targeting:* a person imitating a formal template

```json
{
  "id": "FP06",
  "status": 200,
  "content_id": "afd87b40-29dd-445f-85f6-8d51503a3003",
  "creator_id": "attacker_FP06",
  "guess": "unsure",
  "confidence": 0.6273,
  "model_score": 0.8814,
  "style_score": 0.3732,
  "label": "We couldn't confidently determine whether this was written by a person or AI.",
  "error": null,
  "verdict": "HELD"
}
```

### FP07 — `false_positive`

*Targeting:* human writing that repeats a phrase deliberately

```json
{
  "id": "FP07",
  "status": 200,
  "content_id": "4db7c137-d764-4645-beac-4b63f2449b31",
  "creator_id": "attacker_FP07",
  "guess": "unsure",
  "confidence": 0.64365,
  "model_score": 0.8816,
  "style_score": 0.4057,
  "label": "We couldn't confidently determine whether this was written by a person or AI.",
  "error": null,
  "verdict": "HELD"
}
```

### FP08 — `false_positive`

*Targeting:* very short genuine human submission

```json
{
  "id": "FP08",
  "status": 200,
  "content_id": "2b0955c3-b83f-42a7-b0ed-93e17d9fee23",
  "creator_id": "attacker_FP08",
  "guess": "human",
  "confidence": 0.30289999999999995,
  "model_score": 0.3223,
  "style_score": 0.2835,
  "label": "We think this was probably written by a person.",
  "error": null,
  "verdict": "HELD"
}
```

### PI01 — `prompt_injection`

*Targeting:* instruction to ignore the check

```json
{
  "id": "PI01",
  "status": 200,
  "content_id": "d41d7de3-775b-4b35-8eb5-f0b43fac17df",
  "creator_id": "attacker_PI01",
  "guess": "human",
  "confidence": 0.33225000000000005,
  "model_score": 0.4625,
  "style_score": 0.202,
  "label": "We think this was probably written by a person.",
  "error": null,
  "verdict": "BROKE"
}
```

### PI02 — `prompt_injection`

*Targeting:* instruction disguised as a system message

```json
{
  "id": "PI02",
  "status": 200,
  "content_id": "b7c27446-3329-44ac-87c3-68e9c1f2676a",
  "creator_id": "attacker_PI02",
  "guess": "human",
  "confidence": 0.20035,
  "model_score": 0.2044,
  "style_score": 0.1963,
  "label": "We think this was probably written by a person.",
  "error": null,
  "verdict": "BROKE"
}
```

### PI03 — `prompt_injection`

*Targeting:* instruction wrapped in the writer's voice

```json
{
  "id": "PI03",
  "status": 200,
  "content_id": "94915da5-8002-457b-bb03-ddb37e0c7099",
  "creator_id": "attacker_PI03",
  "guess": "unsure",
  "confidence": 0.48410000000000003,
  "model_score": 0.5943,
  "style_score": 0.3739,
  "label": "We couldn't confidently determine whether this was written by a person or AI.",
  "error": null,
  "verdict": "HELD"
}
```

### PI04 — `prompt_injection`

*Targeting:* attempt to make the label text hostile

```json
{
  "id": "PI04",
  "status": 200,
  "content_id": "ff7c6ec0-96c1-45ca-b410-e49a4761d36e",
  "creator_id": "attacker_PI04",
  "guess": "unsure",
  "confidence": 0.43505000000000005,
  "model_score": 0.4998,
  "style_score": 0.3703,
  "label": "We couldn't confidently determine whether this was written by a person or AI.",
  "error": null,
  "verdict": "HELD"
}
```

### PI05 — `prompt_injection`

*Targeting:* attempt to inject into the audit log

```json
{
  "id": "PI05",
  "status": 200,
  "content_id": "d6fa690d-956c-4873-9a31-e6b97274f34a",
  "creator_id": "attacker_PI05",
  "guess": "unsure",
  "confidence": 0.4605,
  "model_score": 0.6401,
  "style_score": 0.2809,
  "label": "We couldn't confidently determine whether this was written by a person or AI.",
  "error": null,
  "verdict": "HELD"
}
```

### PI06 — `prompt_injection`

*Targeting:* instruction plus real human text

```json
{
  "id": "PI06",
  "status": 200,
  "content_id": "0f17d901-1428-4d37-a76a-6988ac781f05",
  "creator_id": "attacker_PI06",
  "guess": "unsure",
  "confidence": 0.4908,
  "model_score": 0.5583,
  "style_score": 0.4233,
  "label": "We couldn't confidently determine whether this was written by a person or AI.",
  "error": null,
  "verdict": "HELD"
}
```

### MF01 — `malformed`

*Targeting:* text is only whitespace

```json
{
  "id": "MF01",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_MF01",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": "HELD"
}
```

### MF02 — `malformed`

*Targeting:* text is a single character

```json
{
  "id": "MF02",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_MF02",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": "HELD"
}
```

### MF03 — `malformed`

*Targeting:* text is control characters

```json
{
  "id": "MF03",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_MF03",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": "HELD"
}
```

### MF04 — `malformed`

*Targeting:* text is only punctuation

```json
{
  "id": "MF04",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_MF04",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": "HELD"
}
```

### MF05 — `malformed`

*Targeting:* text is a very long single word

```json
{
  "id": "MF05",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_MF05",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": "HELD"
}
```

### MF06 — `malformed`

*Targeting:* text is emoji only

```json
{
  "id": "MF06",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_MF06",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": "HELD"
}
```

### MF07 — `malformed`

*Targeting:* text is right-to-left script

```json
{
  "id": "MF07",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_MF07",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": "HELD"
}
```

### MF08 — `malformed`

*Targeting:* text is 60,000 characters

```json
{
  "id": "MF08",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_MF08",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": "HELD"
}
```

### RQ01 — `malformed`

*Targeting:* no text field at all

```json
{
  "id": "RQ01",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_RQ01",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": "HELD"
}
```

### RQ02 — `malformed`

*Targeting:* no creator_id

```json
{
  "id": "RQ02",
  "status": 400,
  "content_id": null,
  "creator_id": null,
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": "HELD"
}
```

### RQ03 — `malformed`

*Targeting:* text is a number

```json
{
  "id": "RQ03",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_RQ03",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": "HELD"
}
```

### RQ04 — `malformed`

*Targeting:* text is a list

```json
{
  "id": "RQ04",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_RQ04",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": "HELD"
}
```

### RQ05 — `malformed`

*Targeting:* text is null

```json
{
  "id": "RQ05",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_RQ05",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": "HELD"
}
```

### RQ06 — `malformed`

*Targeting:* creator_id is an object

```json
{
  "id": "RQ06",
  "status": 400,
  "content_id": null,
  "creator_id": {
    "id": "x"
  },
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": "HELD"
}
```

### RQ07 — `malformed`

*Targeting:* body is a JSON array, not an object

```json
{
  "id": "RQ07",
  "status": 400,
  "content_id": null,
  "creator_id": null,
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": "HELD"
}
```

### RQ08 — `malformed`

*Targeting:* body is unparseable JSON

```json
{
  "id": "RQ08",
  "status": 400,
  "content_id": null,
  "creator_id": null,
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": "HELD"
}
```

### RQ09 — `malformed`

*Targeting:* body is empty

```json
{
  "id": "RQ09",
  "status": 400,
  "content_id": null,
  "creator_id": null,
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": "HELD"
}
```

### RQ10 — `malformed`

*Targeting:* body is form-encoded, not JSON

```json
{
  "id": "RQ10",
  "status": 400,
  "content_id": null,
  "creator_id": null,
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": "HELD"
}
```

### RQ11 — `malformed`

*Targeting:* body is JSON claiming to be plain text

```json
{
  "id": "RQ11",
  "status": 400,
  "content_id": null,
  "creator_id": null,
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": "HELD"
}
```

### RQ12 — `malformed`

*Targeting:* deeply nested JSON

```json
{
  "id": "RQ12",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_RQ12",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": "HELD"
}
```

### FL01_01 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_01",
  "status": 200,
  "content_id": "5e5e8055-e755-4436-bd15-46152489d4d9",
  "creator_id": "attacker_flood",
  "guess": "human",
  "confidence": 0.01435,
  "model_score": 0.0287,
  "style_score": 0.0,
  "label": "We think this was probably written by a person.",
  "error": null,
  "verdict": "HELD"
}
```

### FL01_02 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_02",
  "status": 200,
  "content_id": "d7ce49f4-49d9-44c6-b66c-3bc17411d914",
  "creator_id": "attacker_flood",
  "guess": "human",
  "confidence": 0.01435,
  "model_score": 0.0287,
  "style_score": 0.0,
  "label": "We think this was probably written by a person.",
  "error": null,
  "verdict": "HELD"
}
```

### FL01_03 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_03",
  "status": 200,
  "content_id": "9e568664-c616-4898-ae4e-747343ed86ae",
  "creator_id": "attacker_flood",
  "guess": "human",
  "confidence": 0.01435,
  "model_score": 0.0287,
  "style_score": 0.0,
  "label": "We think this was probably written by a person.",
  "error": null,
  "verdict": "HELD"
}
```

### FL01_04 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_04",
  "status": 200,
  "content_id": "0c3a10f1-1844-4b73-bfc3-0f753f086ac9",
  "creator_id": "attacker_flood",
  "guess": "human",
  "confidence": 0.01435,
  "model_score": 0.0287,
  "style_score": 0.0,
  "label": "We think this was probably written by a person.",
  "error": null,
  "verdict": "HELD"
}
```

### FL01_05 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_05",
  "status": 200,
  "content_id": "7bcd7682-28c7-4b73-a914-ab2b0104f877",
  "creator_id": "attacker_flood",
  "guess": "human",
  "confidence": 0.01435,
  "model_score": 0.0287,
  "style_score": 0.0,
  "label": "We think this was probably written by a person.",
  "error": null,
  "verdict": "HELD"
}
```

### FL01_06 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_06",
  "status": 200,
  "content_id": "7084fb9c-8f83-4eab-96c6-bd24d81f69ad",
  "creator_id": "attacker_flood",
  "guess": "human",
  "confidence": 0.01435,
  "model_score": 0.0287,
  "style_score": 0.0,
  "label": "We think this was probably written by a person.",
  "error": null,
  "verdict": "HELD"
}
```

### FL01_07 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_07",
  "status": 200,
  "content_id": "14d2fafc-a0ee-401f-a947-3ddbffa471b4",
  "creator_id": "attacker_flood",
  "guess": "human",
  "confidence": 0.01435,
  "model_score": 0.0287,
  "style_score": 0.0,
  "label": "We think this was probably written by a person.",
  "error": null,
  "verdict": "HELD"
}
```

### FL01_08 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_08",
  "status": 200,
  "content_id": "31908bad-fdec-46d1-a9bb-413a607eb403",
  "creator_id": "attacker_flood",
  "guess": "human",
  "confidence": 0.01435,
  "model_score": 0.0287,
  "style_score": 0.0,
  "label": "We think this was probably written by a person.",
  "error": null,
  "verdict": "HELD"
}
```

### FL01_09 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_09",
  "status": 200,
  "content_id": "c00006dd-ffcb-4c2c-879c-8fc589b86bbb",
  "creator_id": "attacker_flood",
  "guess": "human",
  "confidence": 0.01435,
  "model_score": 0.0287,
  "style_score": 0.0,
  "label": "We think this was probably written by a person.",
  "error": null,
  "verdict": "HELD"
}
```

### FL01_10 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_10",
  "status": 200,
  "content_id": "679c91e9-1969-4778-9329-d04f0a8a1511",
  "creator_id": "attacker_flood",
  "guess": "human",
  "confidence": 0.01435,
  "model_score": 0.0287,
  "style_score": 0.0,
  "label": "We think this was probably written by a person.",
  "error": null,
  "verdict": "HELD"
}
```

### FL01_11 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_11",
  "status": 429,
  "content_id": null,
  "creator_id": "attacker_flood",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": "HELD"
}
```

### FL01_12 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_12",
  "status": 429,
  "content_id": null,
  "creator_id": "attacker_flood",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": "HELD"
}
```
