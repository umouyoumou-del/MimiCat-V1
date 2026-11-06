# DeepInfer-SM86 native 120B smoke

This run used the native `DeepSeekV2LiteGGUFRuntime`; no external generation
backend was used.

- model: MimiCat V1 120B Q4_K_M
- accelerator: MTT S4000 via torch_musa, `device="cuda"` resolves to `musa`
- attention/non-expert: accelerator, peak allocated 928,718,336 bytes
- 26 MoE layers: CPU expert offload
- shared experts: CPU
- lm_head: CPU
- load: 38.1 s
- prompt: 42 tokens
- prefill: 273.0 s
- decode: 8 tokens, 88.0 s, 0.0795 tok/s
- answer: `The special magic number for needle 0`
- result: runtime path works; answer is truncated by the 8-token cap

The 24-token exact-answer rerun could not be run after the temporary reboot
because the MUSA driver was not attached (`torch.cuda.is_available()` false).
The 10M simple/complex suites in `DEEPINFER_10M_TEST.md` are CPU-side and
already pass.
