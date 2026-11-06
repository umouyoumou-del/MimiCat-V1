# MimiCat V1 — 120B 总参数 / 4B 激活

[English](README.md)

MimiCat V1 是**货真价实的 120B 总参数、4B 激活参数**稀疏 MoE 模型。

| 项目 | 数值 |
|---|---:|
| 总参数 | **120,093,863,424（120.094B）** |
| 每 token 激活参数 | **4,035,374,592（4.035B）** |
| Routed experts | **528** |
| 每 token 选择 experts | **12** |
| 层数 | 27 |
| Checkpoint shards | 113 |
| 序列化 tensor | 41,483 |

这是一个完整物化的 120B checkpoint。所有参数都真实存在于发布的 safetensors
shards 中，模型会对完整的 120.094B 参数图执行真实前向。

## 训练内容

- 以下非 expert 组件全参数微调：
  - embedding
  - `lm_head`
  - final norm
  - 所有 LayerNorm
  - 所有 attention
  - 所有 shared experts
  - layer 0 dense MLP
  - 所有 router gate
- **528 个 expert 槽位独立 full-rank 更新**，包含 512–527；
- 每个槽位保存 int8 full-rank delta，再流式写入最终权重；
- RP 与 coding 的 expert copy 使用不同的 router domain direction，
  8 个 copy 的 gate 行不再相同；
- 113 个 shard 全部重写，**41,483 个 tensor 全部更新并校验**。

## 校验

| 检查 | 结果 |
|---|---|
| 总参数 | 120,093,863,424 |
| 激活参数 | 4,035,374,592 |
| Gate shape | 全部 `[528, 2048]` |
| 非 expert 权重 | 与训练后的 state 逐元素一致 |
| Router copies | 已区分 |
| Expert 槽位 | 独立且不同 |
| 完整 BF16 CPU 加载 | 184.5 s |
| 39-token CPU 前向 | 390.4 s |
| Logits shape | `[1, 39, 102400]` |

## 固定集评测

RP 是 12 个角色、2 轮历史的中文角色扮演测试；coding 是 8 题可执行 Python 测试。

| 模型分支 | 中文 RP | Coding | Balanced |
|---|---:|---:|---:|
| Base branch | 4.833 / 6 | 7 / 8 | 0.8403 |
| 非 expert 全参阶段 | 4.833 / 6 | 7 / 8 | 0.8403 |
| RP expert 分支 | **5.000 / 6** | 7 / 8 | 0.8542 |
| Coding expert 分支 | 4.750 / 6 | **8 / 8** | **0.8958** |

RP 分支提升中文角色扮演；coding 分支 8 题全过。528 个槽位不是复制的同一份
权重，抽样校验显示 expert 槽位之间存在真实差异。

## DeepInfer-SM86 与 10M 上下文

发布包中包含独立推理框架：

```text
DeepInfer-SM86-0.3.0.tar.gz
```

DeepInfer-SM86 源码已放入
[`framework/DeepInfer-SM86`](framework/DeepInfer-SM86)，同时提供
`DeepInfer-SM86-0.3.0.tar.gz` release 资产。它提供 10M token 文档的分层
FTS5 检索、evidence window 和短 KV 按需加载。

10,000,000 token 全部在 DeepInfer-SM86 内实测：

- **简单任务**：100 / 100 needle 命中，100 / 100 精确回答；
- **复杂全局任务**：137 / 137 marker 计数，5 / 5 主题摘要，
  100 条 metric 记录按类别聚合全部正确。

10M 检索与全局查询路径只使用 DeepInfer-SM86。

## 发布文件

Tag：`v1.0.0-120b-q4`

Q4_K_M 权重按 `<2 GiB` 分片发布。重建：

```bash
cat mimicat-v1-120b-zh-rp-v2-q4_k_m.gguf.part-* \
  > mimicat-v1-120b-zh-rp-v2-q4_k_m.gguf
sha256sum -c q4_k_m.sha256
```

Release 同时包含：

- tokenizer 和模型 config；
- `verify_streaming_v3.json`；
- `STREAMING_V3_RESULTS.md` 和 `RESULTS_STREAMING_V3.json`；
- `DEEPINFER_10M_TEST.md`；
- `DeepInfer-SM86-0.3.0.tar.gz`。

## 快速开始

```bash
# 重建 Q4 权重
cat mimicat-v1-120b-zh-rp-v2-q4_k_m.gguf.part-* \
  > mimicat-v1-120b-zh-rp-v2-q4_k_m.gguf

# 校验
sha256sum -c q4_k_m.sha256

# 安装推理框架
mkdir DeepInfer-SM86-0.3.0
tar xzf DeepInfer-SM86-0.3.0.tar.gz -C DeepInfer-SM86-0.3.0
cd DeepInfer-SM86-0.3.0
python -m pip install -e .
```

## License

MimiCat V1 使用 `LICENSE-WEIGHTS.md` 中的 source-available 社区许可证。
个人、爱好者、学生、学术和非营利研究免费；小型营利实体内部使用免费；
商业 API、托管推理和付费模型服务需要商业许可。

推理框架源码使用 Apache License 2.0（`LICENSE-APACHE`）。
