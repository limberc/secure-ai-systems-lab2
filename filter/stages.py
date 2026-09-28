# -*- coding: utf-8 -*-
"""Lab 2 — the stages you implement.

Each stage takes the list of documents still standing and returns the doc_ids it
removes, tagged with a reason from REASONS. The harness uses those tags to tell you
WHICH stage removed each poisoned document and each clean one, so your error analysis
starts from evidence rather than from guesswork.

A document is a dict with keys:
    doc_id      "d00042"
    lang        "en" | "ko" | "ja"        (ground truth, provided — do not re-derive it
                                           for scoring, though you may ignore it and run
                                           your own language ID if you want to compare)
    url         source URL                 the lineage you were given
    crawl_date  crawl snapshot id
    text        the document

You may add stages, delete stages, or replace the lot. The only fixed points are the
signature of `run` in pipeline.py and the reason vocabulary below.
"""

REASONS = ("lang", "quality", "exact_dup", "near_dup", "poison")


# ---------------------------------------------------------------------------- 1. lang
def stage_lang(docs, cfg):
    """Drop documents whose language you do not intend to keep.

    The corpus is mostly English and Korean with a little Japanese. Dropping a language
    wholesale is a legitimate engineering decision. It is also a coverage decision, and
    the harness will price it for you in the per-language columns.

    Returns: {doc_id: "lang"}
    """
    # TODO
    return {}


# ------------------------------------------------------------------------- 2. quality
def stage_quality(docs, cfg):
    """Drop low-quality documents: boilerplate, navigation chrome, near-empty pages.

    Careful. The obvious heuristics — short documents, high punctuation ratio, repeated
    lines — behave very differently on Korean than on English, and the corpus contains
    legitimate documents that look like spam. Check the per-language false-positive rate
    before you believe a threshold.

    Returns: {doc_id: "quality"}
    """
    # TODO
    return {}


# ----------------------------------------------------------------------- 3. exact dup
def stage_exact_dup(docs, cfg):
    """Remove byte-identical duplicates, keeping one representative of each group.

    Cheap, and it will not catch much. That is expected.

    Returns: {doc_id: "exact_dup"}
    """
    # TODO
    return {}


# ------------------------------------------------------------------------ 4. near dup
def stage_near_dup(docs, cfg):
    """Remove near-duplicates. MinHash + LSH over shingles is the standard approach.

    Two things to decide and to justify in your report:
      * what a shingle is. Whitespace word n-grams are the default and they are tuned
        for English. Korean is agglutinative; particles and endings attach to stems, so
        word- and character-n-gram shingles measure rather different things on Korean
        text than they do on English text.
      * what to do with a near-duplicate GROUP. Keeping one representative is normal.
        Dropping all of them is a different decision with a different coverage cost.

    The corpus contains legitimate near-duplicate pairs — a page and its print view, for
    instance. Those are clean. Removing them is coverage loss, not a win.

    Returns: {doc_id: "near_dup"}
    """
    # TODO
    return {}


# -------------------------------------------------------------------------- 5. poison
def stage_poison(docs, cfg):
    """Your poison heuristic. This is the stage the lab is really about.

    Before you write it, take a position on what the poisoner is optimising for. The
    trigger-rarity argument from Week 4 is the place to start: a rare trigger needs few
    documents and is findable by anyone who thinks to look for rare strings; a natural
    trigger needs many documents and never looks anomalous; a semantic condition needs
    the most documents of all and offers no string to match.

    Your heuristic will not catch every family. Saying precisely which ones it cannot
    catch, and why, is worth more marks than catching one more.

    Returns: {doc_id: "poison"}
    """
    # TODO
    return {}


STAGES = (stage_lang, stage_quality, stage_exact_dup, stage_near_dup, stage_poison)
