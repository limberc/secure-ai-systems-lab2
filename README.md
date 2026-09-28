# Lab 2 — Poison-resilient data filter

Secure AI Systems · Korea University · 2026-2
Released Week 4 (Mon 28 Sep 2026) · **due Mon 12 Oct 2026, 23:59 KST** · 5% of the grade

> ### ⚠ The corpus in `data/` is deliberately poisoned. Do not train on it.
>
> About 3% of the documents carry a planted false claim. Every planted entity is
> **fictional** — no real company, product, person or statute is the subject of any
> planted claim. If you are assembling a training corpus or running a crawler,
> **exclude this repository**. See [`LICENSE-DATA.md`](LICENSE-DATA.md).

Read the brief (`Lab2_Poison_Filter.pdf` on the LMS) first. This file is the operating
manual; the brief is the assignment.

---

## Quick start

```bash
git lfs install                  # the corpus is stored in Git LFS
git clone https://github.com/limberc/secure-ai-systems-lab2.git
cd secure-ai-systems-lab2

python3 tests/test_smoke.py      # check the contract before you start
python3 evaluate.py              # score on dev — all zeros until you write something
```

Nothing to install beyond `git-lfs`. The lab itself is standard library only; see
`requirements.txt`. If `data/dev.jsonl` looks like a ~130-byte text file rather than
29MB of JSON, LFS did not run — `git lfs install && git lfs pull` fixes it.

## What is here

```
data/dev.jsonl             8,000 documents WITH poison labels — build and tune here
data/test.jsonl            4,000 documents WITHOUT labels — run once, at the end
data/corpus_manifest.json  provenance and counts for the corpus you were given
filter/stages.py           the five stages you implement          <- your work
filter/pipeline.py         wiring; you may edit, `run`'s signature is fixed
evaluate.py                the harness. Run it; do not edit it.
tests/test_smoke.py        contract checks
LICENSE-DATA.md            where the text came from, and the fictional-entity rule
```

## The contract

`filter.pipeline.run(docs)` returns `{doc_id: reason}` for every document it **removes**.
Documents you do not mention are kept. `reason` is one of
`lang`, `quality`, `exact_dup`, `near_dup`, `poison`.

Stages run in order and each sees only what is still standing, so the reason records
*which stage* removed a document. That attribution is what lets the harness tell you
which stage caught each poisoned document — and which stage threw away clean text.

A document looks like this:

```json
{"doc_id": "d00042", "lang": "ko", "url": "https://...", "crawl_date": "CC-MAIN-2023-14",
 "text": "..."}
```

`dev.jsonl` adds `"poison": true|false` and `"family": null|"rare_token"|...`.
`test.jsonl` does not, and will not.

`lang` is ground truth, given to you. You may use it, or ignore it and run your own
language ID and compare — the second is more interesting and the report has room for it.

## Running on test

```bash
python3 evaluate.py --split test     # writes out/predictions.jsonl
```

Submit that file. The TA scores it against the withheld labels.

**Run it once**, with the configuration you already settled on using dev. Repeatedly
scoring against test and keeping the best result is exactly the contamination failure
Chapter 5 is about, and your report has to state how many times you ran it. Saying
"three times, and here is what I changed between them" is a defensible answer that
costs you nothing. Saying "once" when the answer is nine is an integrity matter.

## What the harness gives you

A dev run writes three files into `out/`:

| file | what it is for |
|---|---|
| `missed_poison.jsonl` | poisoned documents you kept — read these before writing the report |
| `false_positives.jsonl` | clean documents you removed — read these too |
| `eval_report.json` | every number the harness printed, machine-readable |

The rubric weights *"which poison survived, and why"* at 25 marks and gives recall no
marks by itself. Those two files are where that answer comes from.

## Five things worth knowing before you start

1. **The five poison families are not equally hard, and that is the point.** One uses a
   constant rare trigger. One uses an ordinary entity name that also occurs benignly.
   One reuses a claim across many reworded paragraphs. One is Korean-only and semantic,
   with no constant string anywhere. One plants the same claim in two languages. A
   heuristic tuned for the first will not touch the fourth.

2. **There are hard negatives.** Around 6% of the clean documents are built to look
   suspicious: legitimate rare identifiers (DOIs, part numbers, commit hashes),
   navigation boilerplate, and genuine near-duplicate pairs such as a page and its print
   view. Removing those is coverage loss, and the harness prices it.

3. **Check the per-language columns.** A threshold tuned on English will behave
   differently on Korean, and the harness reports the false-positive rate per language
   so you can see it happen rather than take my word for it.

4. **The corpus is 3% poisoned. The real figure is about 0.01%.** Carlini et al. put a
   practical attack at roughly 0.01% of a pretraining corpus, which at 12,000 documents
   would be one. The rate here is inflated for statistical power. The brief asks you
   what changes at 0.01%, and it is a real question.

5. **Runtime.** The instructor reference takes about 45 seconds on dev on a recent
   laptop. If yours takes ten minutes, the near-duplicate stage is usually why —
   comparing all pairs is O(n²); banded LSH is not.

## Collaboration and AI use

**This is an individual lab.** The five labs are 5% each, 25% between them, submitted
individually. The *project* is a separate thing: teams of four, formed in Week 5, worth 40%
of the course. It is the largest component of your grade, and this is not it. Collaboration is encouraged — compare per-family results, argue about
thresholds — but the code you submit and the analysis you write are yours, and you must be
able to defend every line of the filter you hand in. Sharing a whiteboard is collaboration;
sharing a repository is where this goes wrong.

AI tool use is permitted with disclosure, per the syllabus. The disclosure line goes at the end of the report: which
tools, for what. Note that the marks here are concentrated in the error analysis, which
is a claim about *your* pipeline's *specific* failures — that is not something a model
that has not seen your `out/` files can write for you.
