# MimiCat V1

Tied weights are not used for the 120B release.

- Architecture: DeepSeek-V2-style MoE
- Total parameters: 120,093,863,424 (120.094B)
- Active parameters: 4,035,374,592 (4.035B)
- Routed experts: 528
- Top-k: 12
- Fine-tune: 3,430,000,000+ tokens? (see training logs)
- Base: DeepSeek-Coder-V2-Lite-Instruct (16B)
- Post-training: code + Japanese roleplay + Chinese roleplay LoRA, 300 steps

Large weights are published as GitHub Release assets split into <2 GiB parts because GitHub rejects single files over 2 GiB.

## Release

Tag: `v1.0.0-120b-q4`

The Q4_K_M file is split into parts; reconstruct with:

```bash
cat mimicat-v1-120b-q4_k_m.gguf.part-* > mimicat-v1-120b-q4_k_m.gguf
sha256sum -c SHA256SUMS
```

Verification and tokenizer/config files are included as release assets.
