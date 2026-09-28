# -*- coding: utf-8 -*-
"""Lab 2 — pipeline wiring. You may edit this; the signature of `run` is fixed."""

from .stages import STAGES, REASONS

# Anything you want to tune. Put thresholds here rather than burying them in the
# stages, so that your report can state the configuration that produced your numbers.
CONFIG = {
    "keep_langs": ("en", "ko", "ja"),
    "min_chars": 0,
    "minhash_perm": 128,
    "minhash_threshold": 0.8,
    "shingle_size": 5,
}


def run(docs, cfg=None):
    """Filter a corpus.

    Args:
        docs: list of document dicts (see stages.py for the schema)
        cfg:  configuration dict; defaults to CONFIG

    Returns:
        {doc_id: reason} for every document the pipeline REMOVES.
        Documents not mentioned are kept.

    Stages run in order and each sees only what is still standing, so a document
    removed by an earlier stage is attributed to that stage. That attribution is what
    the harness reports back to you.
    """
    cfg = dict(CONFIG if cfg is None else cfg)
    removed = {}
    alive = list(docs)

    for stage in STAGES:
        out = stage(alive, cfg) or {}
        for doc_id, reason in out.items():
            if reason not in REASONS:
                raise ValueError(f"{stage.__name__} returned unknown reason {reason!r}")
            removed.setdefault(doc_id, reason)
        gone = set(out)
        alive = [d for d in alive if d["doc_id"] not in gone]

    return removed
