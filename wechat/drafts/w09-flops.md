---
title: "面试官问 FLOPs 怎么算？手推 Transformer 计算量，再也不怕被问倒"
summary: "FLOPs 是大模型面试的高频题。本文从 Attention 到 FFN，手把手推一遍计算量，附带记忆公式和 GPT-3 实战演算。"
author: 橙序员
coverImage: /Users/sring24/Desktop/个人ip构建/wechat/images/w09-cover.png
---

![橙序员 - AI科技媒体](account-card.png)



如果你面过大模型相关的岗位，有一道题是必考的：「Transformer 的计算复杂度是多少？」

80% 的人能答出 O(n²d)。但追问一句「具体是多少 FLOPs，怎么推的」，大半人卡住。再问「GPT-3 生成一个 token 要多少计算量」，几乎全军覆没。

这篇文章手把手推一遍。不需要前置知识，只需要记住一件事：**矩阵乘法 A(m×k) × B(k×n) = 2mkn FLOPs（乘 k 次，加 k-1 次，约 2k 次运算）。** 全文只用这个公式。

---

## 一、设好战场

以标准 Transformer 层为例：

- 序列长度 n（token 数），比如 2048
- 隐藏维度 d，比如 4096 或 12288
- 头数 h，每个头维度 d_head = d / h
- FFN 中间维度 d_ff = 4d

我们先算**一层**，乘以层数就是整个模型。

---

## 二、Self-Attention 计算量

**Step 1：生成 Q、K、V。** 输入 X（n×d）分别乘以三个权重矩阵 W_Q、W_K、W_V（都是 d×d）。每次是 n×d × d×d，输出 n×d，计算量 2nd²。三次合计：6nd²。

**Step 2：计算注意力分数 S = Q × K^T。** Q 是 n×d_head（注意是 d_head 不是 d，因为分头后维度变小了）。不对——这里有个常见陷阱：实际计算是每个头独立做 Q×K^T，但总计算量等于 Q(n×d) × K^T(d×n) = n×n 输出 × 2×n×d = 2n²d。这里是 d 不是 d_head，因为 h 个头加起来维度等于 d。Self-Attention 这个步骤是 2n²d。

**Step 3：Softmax。** 指数运算不算浮点运算，忽略。

**Step 4：加权求和 A = softmax × V。** 注意力矩阵 n×n，V 是 n×d，输出 n×d。计算量：2n²d。

**Step 5：输出投影。** 和 Step 1 一样，2nd²。

**Self-Attention 合计**：6nd² + 2n²d + 2n²d + 2nd² = **8nd² + 4n²d**

---

## 三、FFN 计算量

FFN 是两层全连接。第一层升维 n×d → n×4d，第二层降回来 n×4d → n×d。

第一层：n×d × d×4d = 2 × n × d × 4d = 8nd²
第二层：n×4d × 4d×d = 2 × n × 4d × d = 8nd²

**FFN 合计**：**16nd²**

---

## 四、一层 Transformer 总计

| 组件 | FLOPs |
|------|-------|
| Self-Attention | 8nd² + 4n²d |
| FFN | 16nd² |
| **一层** | **24nd² + 4n²d** |

---

## 五、什么时候谁的戏份重

看两部分的相对大小：

- **短序列**（n < 6d）：24nd² 主导，FFN（16nd²）占大头，Attention（8nd²）反而小。GPT 在日常短对话里，大部分算力花在 FFN 上
- **长序列**（n 接近 12d 以上）：4n²d 膨胀得很快，Attention 逐渐反超成为瓶颈。这就是为什么长上下文推理那么贵——序列翻倍，Attention 计算量翻四倍
- 这也解释了**KV Cache 的威力**：缓存后 Attention 从 O(n²d) 降到 O(nd)，长序列加速最明显。也解释了**GQA/MQA 压缩 KV Cache** 的需求

---

## 六、实战：推算 GPT-3（175B）的 FLOPs

GPT-3 参数：96 层，d=12288，n=2048。

带入公式：

- 24 × 96 × 2048 × (12288)² = 24 × 96 × 2048 × 1.51×10⁸ ≈ **7.1 × 10¹⁴**
- 4 × 96 × (2048)² × 12288 = 4 × 96 × 4.19×10⁶ × 12288 ≈ **2.0 × 10¹³**
- 一层总计 ≈ 7.3 × 10¹⁴ FLOPs ≈ **0.73 PFLOPs**

这只是一层。一个 token 在一层的前向传播需要 0.73 PFLOPs。96 层需要约 70 PFLOPs。

用 H100（FP16 峰值 989 TFLOPs）来做，考虑利用率（~50%），一个 token 的前向延迟约 140ms。这就是为什么大模型生成速度有限——不是算力不够，是每一步都要跑全量计算。

---

## 七、面试记忆公式

如果面试官让你心算，记这个：

**FLOPs ≈ 24 × 层数 × n × d² + 4 × 层数 × n² × d**

注意 n² 项在长序列时反超。如果你说了「短序列 FFN 是主力，长序列 Attention 是瓶颈」，面试官就知道你是真懂的。

---

*本文参考 Vaswani et al. (2017) "Attention Is All You Need"、Kaplan et al. (2020) "Scaling Laws for Neural Language Models"、Narayanan et al. (2021) "Efficient Large-Scale Language Model Training on GPU Clusters"*

---

**橙序员** — AI 科技媒体，关注大模型技术前沿与工程实践。
