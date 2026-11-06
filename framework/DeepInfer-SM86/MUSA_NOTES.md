# MUSA / split-MLA compatibility

The native runtime was exercised on an MTT S4000 where `torch.device("cuda")`
resolves to a `musa` device.

Two compatibility changes are included in
`deepinfer/moe/deepseek_v2_runtime.py`:

- the accelerator guard accepts `cuda` and `musa`;
- `_load_kv_b` rebuilds the MLA `kv_b` projection when a GGUF uses llama.cpp's
  split `attn_k_b` / `attn_v_b` layout instead of one `attn_kv_b` tensor.

The remote-code `modeling_deepseek.py` used with such a device also needs the
attention softmax cast to fp32 before the reduction:

```python
attn_weights = nn.functional.softmax(
    attn_weights.float(), dim=-1
).to(query_states.dtype)
```

That model file lives in the model metadata directory, not in this framework
source tree.
