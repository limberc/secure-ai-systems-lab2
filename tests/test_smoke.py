# -*- coding: utf-8 -*-
"""Smoke tests. Run `python3 -m pytest tests/ -q`, or just `python3 tests/test_smoke.py`.

These check that your pipeline satisfies the contract the harness relies on. They do
not check that it is any good.
"""
import json, os, sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from filter.pipeline import run           # noqa: E402
from filter.stages import REASONS         # noqa: E402

DATA = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")


def load(split, n=None):
    with open(os.path.join(DATA, f"{split}.jsonl"), encoding="utf-8") as f:
        rows = [json.loads(l) for l in f]
    return rows[:n] if n else rows


def test_returns_a_dict():
    out = run(load("dev", 200))
    assert isinstance(out, dict), "run() must return {doc_id: reason}"


def test_reasons_are_known():
    out = run(load("dev", 200))
    bad = {r for r in out.values() if r not in REASONS}
    assert not bad, f"unknown removal reasons: {bad}"


def test_only_removes_documents_it_was_given():
    docs = load("dev", 200)
    ids = {d["doc_id"] for d in docs}
    out = run(docs)
    assert set(out) <= ids, "run() removed ids that were not in the input"


def test_does_not_mutate_input():
    docs = load("dev", 200)
    before = json.dumps(docs, sort_keys=True)
    run(docs)
    assert json.dumps(docs, sort_keys=True) == before, "run() mutated the corpus"


def test_dev_has_labels_and_test_does_not():
    assert "poison" in load("dev", 1)[0], "dev.jsonl should carry labels"
    assert "poison" not in load("test", 1)[0], "test.jsonl must not carry labels"


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for fn in fns:
        try:
            fn(); print(f"  ok    {fn.__name__}")
        except AssertionError as e:
            print(f"  FAIL  {fn.__name__}: {e}")
    print(f"\n{len(fns)} checks run")
