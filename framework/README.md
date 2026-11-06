# DeepInfer-SM86 source

This directory contains the DeepInfer-SM86 0.3.0 inference framework source used
with MimiCat V1.

```text
framework/DeepInfer-SM86/
  deepinfer/          native runtime, MoE executor, retrieval, ECS
  scripts/            10M suite and benchmarking scripts
  apps/               server and scheduler
  tests/
  pyproject.toml
```

Install:

```bash
python -m pip install -e framework/DeepInfer-SM86
```

The 10M retrieval and global-query path is implemented entirely in
`deepinfer.retrieval` and `deepinfer.longctx_suite`; it runs on CPU with an FTS5
index and short evidence windows. The native DeepSeek-V2 MoE executor lives in
`deepinfer.moe.deepseek_v2_runtime` and `deepinfer.moe.gguf_index`.

See `DEEPINFER_10M_TEST.md` in the repository root for the 10M results.
