# -*- coding: utf-8 -*-
"""Lab 2 — evaluation harness. Run this; do not edit it.

    python3 evaluate.py                 score your pipeline on dev
    python3 evaluate.py --split test    run on test and write predictions.jsonl

dev carries poison labels, so the dev run scores you. test does not, so the test run
only reports what your pipeline removed and writes the predictions the TA scores.

Two side files are written on a dev run, and they are the raw material for the error
analysis the rubric weights most heavily:

    out/missed_poison.jsonl     poisoned documents your pipeline kept
    out/false_positives.jsonl   clean documents your pipeline removed

Read them. The report question is not "what was your recall" but "which poison
survived, and why" — and these two files are where that answer comes from.
"""
import argparse, json, os, sys
from collections import Counter, defaultdict

from filter.pipeline import run
from filter.stages import REASONS

DATA = os.path.join(os.path.dirname(__file__), "data")
OUT = os.path.join(os.path.dirname(__file__), "out")


def load(split):
    path = os.path.join(DATA, f"{split}.jsonl")
    if not os.path.exists(path):
        sys.exit(f"missing {path}")
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f]


def pct(a, b):
    return f"{a / b:6.1%}" if b else "     —"


def bar(x, width=22):
    n = int(round(x * width))
    return "█" * n + "·" * (width - n)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--split", default="dev", choices=("dev", "test"))
    args = ap.parse_args()

    docs = load(args.split)
    removed = run(docs)
    if not isinstance(removed, dict):
        sys.exit("pipeline.run must return {doc_id: reason}")
    unknown = set(removed) - {d["doc_id"] for d in docs}
    if unknown:
        sys.exit(f"pipeline removed {len(unknown)} ids that are not in the corpus")

    os.makedirs(OUT, exist_ok=True)
    kept = [d for d in docs if d["doc_id"] not in removed]

    print(f"\ncorpus {args.split}: {len(docs)} documents")
    print(f"removed {len(removed)}  ({len(removed) / len(docs):.1%})    kept {len(kept)}")

    # ---------------------------------------------------------------- stage breakdown
    by_stage = Counter(removed.values())
    print("\n  removals by stage")
    for r in REASONS:
        print(f"    {r:<12s} {by_stage.get(r, 0):6d}")

    # ------------------------------------------------------------------- test: submit
    if args.split == "test":
        path = os.path.join(OUT, "predictions.jsonl")
        with open(path, "w", encoding="utf-8") as f:
            for d in docs:
                f.write(json.dumps({"doc_id": d["doc_id"],
                                    "removed": d["doc_id"] in removed,
                                    "reason": removed.get(d["doc_id"])}) + "\n")
        print(f"\nwrote {path}")
        print("test has no labels. Submit this file; the TA scores it.")
        print("Run it ONCE, with the configuration you already chose on dev.\n")
        return

    # ---------------------------------------------------------------------- dev: score
    poison = [d for d in docs if d["poison"]]
    clean = [d for d in docs if not d["poison"]]
    tp = [d for d in poison if d["doc_id"] in removed]
    fn = [d for d in poison if d["doc_id"] not in removed]
    fp = [d for d in clean if d["doc_id"] in removed]

    precision = len(tp) / len(removed) if removed else 0.0
    recall = len(tp) / len(poison) if poison else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0

    print("\n  poison detection")
    print(f"    recall      {recall:6.1%}   {bar(recall)}   {len(tp)}/{len(poison)}")
    print(f"    precision   {precision:6.1%}   {bar(precision)}   {len(tp)}/{len(removed) or 1}")
    print(f"    F1          {f1:6.1%}")

    # ------------------------------------------------------------------- by family
    fam_tot, fam_hit, fam_stage = Counter(), Counter(), defaultdict(Counter)
    for d in poison:
        fam_tot[d["family"]] += 1
        if d["doc_id"] in removed:
            fam_hit[d["family"]] += 1
            fam_stage[d["family"]][removed[d["doc_id"]]] += 1
    print("\n  recall by poison family        (which stage caught it)")
    for fam in sorted(fam_tot):
        hit, tot = fam_hit[fam], fam_tot[fam]
        who = ", ".join(f"{s}:{n}" for s, n in fam_stage[fam].most_common()) or "—"
        print(f"    {fam:<18s} {pct(hit, tot)}  {bar(hit / tot, 14)}  {hit:3d}/{tot:<3d}  {who}")

    # ----------------------------------------------------------------- by language
    print("\n  false positives by language     (clean documents you removed)")
    for lang in sorted({d["lang"] for d in clean}):
        c = [d for d in clean if d["lang"] == lang]
        f = [d for d in c if d["doc_id"] in removed]
        print(f"    {lang:<18s} {pct(len(f), len(c))}  {bar(len(f) / len(c), 14)}  {len(f):4d}/{len(c)}")
    print(f"    {'overall':<18s} {pct(len(fp), len(clean))}  {bar(len(fp) / len(clean), 14)}  {len(fp):4d}/{len(clean)}")

    # -------------------------------------------------------------------- coverage
    clean_chars = sum(len(d["text"]) for d in clean)
    kept_chars = sum(len(d["text"]) for d in clean if d["doc_id"] not in removed)
    print("\n  coverage cost")
    print(f"    clean documents retained  {pct(len(clean) - len(fp), len(clean))}")
    print(f"    clean characters retained {pct(kept_chars, clean_chars)}")

    # --------------------------------------------------- cross-language blind spot
    xl = [d for d in poison if d["family"] == "crosslang_pair"]
    xl_kept = [d for d in xl if d["doc_id"] not in removed]
    print(f"\n  cross-language pairs surviving  {len(xl_kept)}/{len(xl)}"
          f"   (the documented blind spot — see the brief, §4)")

    # -------------------------------------------------------------- inspection files
    def dump(name, rows):
        path = os.path.join(OUT, name)
        with open(path, "w", encoding="utf-8") as f:
            for d in rows:
                f.write(json.dumps({**{k: d[k] for k in
                                       ("doc_id", "lang", "url", "family")
                                       if k in d},
                                    "removed_by": removed.get(d["doc_id"]),
                                    "text": d["text"][:600]}, ensure_ascii=False) + "\n")
        return path

    p1 = dump("missed_poison.jsonl", fn)
    p2 = dump("false_positives.jsonl", fp)

    report = {
        "split": "dev", "documents": len(docs), "removed": len(removed),
        "precision": round(precision, 4), "recall": round(recall, 4), "f1": round(f1, 4),
        "by_family": {f: {"total": fam_tot[f], "caught": fam_hit[f],
                          "by_stage": dict(fam_stage[f])} for f in sorted(fam_tot)},
        "false_positive_rate": round(len(fp) / len(clean), 4),
        "fpr_by_language": {l: round(sum(1 for d in clean if d["lang"] == l
                                         and d["doc_id"] in removed)
                                     / max(1, sum(1 for d in clean if d["lang"] == l)), 4)
                            for l in sorted({d["lang"] for d in clean})},
        "clean_chars_retained": round(kept_chars / clean_chars, 4),
        "crosslang_surviving": [len(xl_kept), len(xl)],
        "removals_by_stage": dict(by_stage),
    }
    with open(os.path.join(OUT, "eval_report.json"), "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print(f"\n  wrote {p1}")
    print(f"        {p2}")
    print(f"        {os.path.join(OUT, 'eval_report.json')}")
    print("\n  Read the two sample files before you write the report. The rubric weights")
    print("  'which poison survived and why' at 25 marks; recall is worth none by itself.\n")


if __name__ == "__main__":
    main()
