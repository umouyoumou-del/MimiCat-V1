# MimiCat V1 — 120B total / 4B active

[中文说明](README.zh-CN.md)

MimiCat V1 is a genuine **120B-total, 4B-active** sparse Mixture-of-Experts model.

| Property | Value |
|---|---:|
| Total parameters | **120,093,863,424 (120.094B)** |
| Active parameters per token | **4,035,374,592 (4.035B)** |
| Routed experts | **528** |
| Top-k routed experts | **12** |
| Layers | 27 |
| Checkpoint shards | 113 |
| Serialized tensors | 41,483 |

The 120B checkpoint is fully materialized. Every parameter is present in the
released safetensors shards, and the model executes a real forward pass over the
full 120.094B-parameter graph.

## What was trained

- Full-parameter tuning of the non-expert components:
  embedding, `lm_head`, final norm, every LayerNorm, attention, shared experts,
  dense layer-0 MLP, and every router gate.
- Independent full-rank updates for all **528 expert slots**, including slots
  512–527, stored as int8 deltas and streamed into the final weights.
- Router domain directions for the RP and coding expert copies, so the eight
  copies of each source expert have distinct routing rows.

The final 120B checkpoint was written shard-by-shard. All 41,483 tensors were
updated and verified.

## Verification

| Check | Result |
|---|---|
| Total parameters | 120,093,863,424 |
| Active parameters | 4,035,374,592 |
| Gate shapes | all `[528, 2048]` |
| Non-expert weights | exact match with the trained state |
| Router copies | distinct |
| Expert slots | independently different |
| Full BF16 CPU load | 184.5 s |
| 39-token CPU forward | 390.4 s |
| Logits shape | `[1, 39, 102400]` |

## Fixed-set evaluation

RP is the 12-character Chinese roleplay suite; coding is the 8-task executable
Python suite.

| Model branch | Chinese RP | Coding | Balanced |
|---|---:|---:|---:|
| Base branch | 4.833 / 6 | 7 / 8 | 0.8403 |
| Full non-expert stage | 4.833 / 6 | 7 / 8 | 0.8403 |
| RP expert branch | **5.000 / 6** | 7 / 8 | 0.8542 |
| Coding expert branch | 4.750 / 6 | **8 / 8** | **0.8958** |

The RP branch improves Chinese roleplay. The coding branch solves all eight
coding tasks. The trained expert slots are independent and measurably different.

## 10M context with DeepInfer-SM86

DeepInfer-SM86 is included as a separate inference framework in the release
assets (`DeepInfer-SM86-0.3.0.tar.gz`). It provides hierarchical FTS5 retrieval
and short on-demand evidence windows for 10M-token documents.

Verified on 10,000,000 tokens:

- **Simple retrieval:** 100 / 100 needle hits and 100 / 100 exact answers.
- **Complex global queries:** 137 / 137 marker count, 5 / 5 summary themes,
  and all 100 metric records aggregated correctly.
- **End-to-end:** DeepInfer retrieval + Qwen3.5-4B answered the 10M needle
  question correctly with a 2,107-token evidence window.

The 10M retrieval layer is model-agnostic and works with the same DeepInfer
pipeline used by the 120B deployment.

## Release

Tag: `v1.0.0-120b-q4`

The Q4_K_M weights are split into `<2 GiB` parts. Reconstruct them with:

```bash
cat mimicat-v1-120b-zh-rp-v2-q4_k_m.gguf.part-* \
  > mimicat-v1-120b-zh-rp-v2-q4_k_m.gguf
sha256sum -c q4_k_m.sha256
```

Release assets also include:

- tokenizer and model config;
- `verify_streaming_v3.json`;
- `STREAMING_V3_RESULTS.md` and `RESULTS_STREAMING_V3.json`;
- `DEEPINFER_10M_TEST.md`;
- `DeepInfer-SM86-0.3.0.tar.gz`.

## Quick start

```bash
# reconstruct the Q4 weights
cat mimicat-v1-120b-zh-rp-v2-q4_k_m.gguf.part-* \
  > mimicat-v1-120b-zh-rp-v2-q4_k_m.gguf

# verify
sha256sum -c q4_k_m.sha256

# install the inference framework
mkdir DeepInfer-SM86-0.3.0
tar xzf DeepInfer-SM86-0.3.0.tar.gz -C DeepInfer-SM86-0.3.0
cd DeepInfer-SM86-0.3.0
python -m pip install -e .
```

## License

MimiCat V1 uses the source-available community license in `LICENSE-WEIGHTS.md`.
Individuals, hobbyists, students, academic and non-profit research are free.
Small for-profit entities are free for internal use. Commercial API / hosted
inference / paid model service requires a commercial license.

The inference framework source is Apache License 2.0 (`LICENSE-APACHE`).
