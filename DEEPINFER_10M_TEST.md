# DeepInfer-SM86 10M validation

DeepInfer-SM86 is bundled as source in `framework/DeepInfer-SM86/` and as the
`DeepInfer-SM86-0.3.0.tar.gz` release asset. The 10M retrieval and global-query
path runs entirely inside DeepInfer-SM86; no external generation runtime is
used.

## Simple: 10M needle retrieval

- tokens: 10,000,000
- needles: 100
- correct: **100/100**
- retrieval hits: **100/100**
- FTS5 chunks: 18,652
- build: 92.01 s
- index: 1.163 s
- 100 retrievals: 0.267 s
- exact answer extraction: 0.006 s

## Complex: full-document global queries

- tokens: 10,000,000
- marker count: **137/137**
- summary themes: **5/5**
- metric records: 100
- category totals: alpha 618, beta 594, gamma 570, delta 587, epsilon 604
- checks: count=true, summary=true, compare=true
- build: 65.63 s
- count: 0.02 s
- summary: 4.128 s
- compare/aggregate: 0.021 s

## Native runtime

The 120B Q4 path uses the DeepInfer-SM86 native DeepSeek-V2 MoE runtime in
`deepinfer.moe.deepseek_v2_runtime` and `deepinfer.moe.gguf_index`. It is a
CUDA/SM86 executor with CPU MoE offload; the 10M retrieval and global-query
suite above is CPU-side and independent of the model runtime.
