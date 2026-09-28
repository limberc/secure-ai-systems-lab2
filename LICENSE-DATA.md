# Lab 2 corpus — sources, licences, and a warning

## ⚠ This corpus is deliberately poisoned. Do not train on it.

About 3% of the documents in `data/` have been modified: a short, false claim has been
inserted into an otherwise unmodified source document. That is the entire point of the
lab — students build a filter that finds them.

**Every planted entity is fictional.** The company, the product, the statute and its
article number do not exist, and no real organisation, person or law is the subject of
any planted claim. This was a deliberate constraint: a corpus of plausible false claims
about real entities would be a misinformation artefact regardless of the intent behind
it.

If you are assembling a training corpus, or running a crawler, **exclude this repository.**
The documents here are engineered to carry false associations into a model that trains on
them. That is not a hypothetical risk — it is the mechanism the lab exists to teach, and
publishing the corpus openly means the lab is also a small demonstration of it.

## Sources and attribution

The unmodified source text is drawn from three public datasets.

| Source | Portion | Licence |
|---|---|---|
| [`HuggingFaceFW/fineweb-edu`](https://huggingface.co/datasets/HuggingFaceFW/fineweb-edu), `sample-10BT` | English web text | ODC-By 1.0 |
| [`HuggingFaceFW/fineweb-2`](https://huggingface.co/datasets/HuggingFaceFW/fineweb-2), `kor_Hang` | Korean web text | ODC-By 1.0 |
| [`wikimedia/wikipedia`](https://huggingface.co/datasets/wikimedia/wikipedia), `20231101.{en,ko,ja}` | Encyclopaedia text, EN/KO/JA | CC BY-SA 4.0 |

Individual documents retain the `url` of the page they came from, so any single document
can be traced to its origin.

## Licence of this corpus

The corpus is a derivative of the above. Because it incorporates Wikipedia text licensed
**CC BY-SA 4.0**, the share-alike condition travels with the whole: **`data/` is
distributed under [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/)**, with
attribution to the three sources named above. If you redistribute it or a derivative of
it, the same licence and attribution must travel with it — including, please, the warning
at the top of this file.

The ODC-By 1.0 portions require attribution, which the table above provides.

**The code in this repository is MIT-licensed** (see `LICENSE`). Code and data are
licensed separately and deliberately.

## What this file is an instance of

Chapter 5 of the course notes argues for a *corpus manifest*: for each source, the
version, the licence, the filtering applied, the residual risk, and a responsible owner.
`data/corpus_manifest.json` is the machine-readable version for this corpus, and this
file is the human-readable one. Students receive the artefact the chapter says every
pipeline should produce.
