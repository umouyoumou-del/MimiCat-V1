# MimiCat V1

Tied weights are not used for the 120B release.

- Total parameters: 120,093,863,424 (120.094B)
- Active parameters: 4,035,374,592 (4.035B)
- Routed experts: 528
- Top-k: 12
- Post-training: code + Japanese roleplay + Chinese roleplay LoRA, 300 optimizer steps
- Base: a third-party 16B code-oriented MoE base (16B)
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


## License

MimiCat V1 uses a **source-available community license**, not a tied-weight or
unrestricted open-source release:

- **Individuals, hobbyists, students, academic and non-profit research:** free.
- **For-profit entities under US$1M annual revenue and under US$1M valuation/funding:** free for internal use.
- **Commercial API / hosted inference / paid model service:** commercial license required, regardless of size.
- **Larger companies:** commercial license required.

Model weights: `LICENSE-WEIGHTS.md` (also `LICENSE`).  
Source code: Apache License 2.0 (`LICENSE-APACHE`).  
Upstream base: see `NOTICE.md`.

This license contains field-of-use restrictions, so it is **source-available** rather than OSI-approved open source.
