# Prompts for a small local model

When there are no agent credits, a small model run locally with [Ollama](https://ollama.com) covers some
reading tasks. Each prompt is a text file that ends in `POSTING:` or `TEXT:`, so it can be concatenated
with the input. *(The private originals are in Spanish; these are translations.)*

```bash
cat examples/prompts/classify-family.txt      posting.md | ollama run qwen2.5:3b
cat examples/prompts/extract-requirements.txt posting.md | ollama run qwen2.5:3b
cat examples/prompts/summarize-posting.txt    posting.md | ollama run qwen2.5:3b
cat examples/prompts/translate-en.txt         paragraph.txt | ollama run qwen2.5:3b
```

| Prompt | Returns | Measured reliability (3B model, CPU, two real postings) |
|---|---|---|
| `classify-family.txt` | family, alternative, seniority, hard requirements, reason | family: 2 of 2 correct · seniority: 1 of 2 · requirements: paraphrased once, complete once |
| `extract-requirements.txt` | required and desirable items copied literally, years, degree, modality | desirable items complete; required items incomplete (3 of 7), and the role title listed as a requirement |
| `summarize-posting.txt` | five fixed bullets | not measured yet |
| `translate-en.txt` | English translation of a CV paragraph | not measured yet |

**Operational conclusion.** A 3B model is good enough to suggest the family and a first list of
requirements that is then compared with the posting. Nothing is written to the pipeline without that
comparison. For seniority and hard requirements, reading the posting is still faster than correcting the
model.

## Writing a new prompt

- One file per task, ending in `POSTING:` or `TEXT:`.
- A **fixed, short output template**: small models follow a template of fields far better than an open
  instruction.
- "Copy literally" and "write 'not stated'" in the instruction: the failure to prevent is the model filling
  a gap with something plausible.
- Tested on at least one real posting before its reliability is filled in here, with the date, the model and
  the result; until then it is listed as "not measured yet".
