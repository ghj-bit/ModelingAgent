# claude_fp8_infogap_r15 实验分析

**撰写日期**：2026-09-30（实验创建于 2026-09-30 00:04:51）
**撰写时状态**：round 1–11 已完成，round 12 进行中
**数据来源**：
- `cpe_evaluations/round_N/<phase>/workflows/round_N/result.json` — 净效用、逐维分、惩罚项
- 各 run 的 `meta/mmbench_judge/judge_stability.json` — 逐 trial、逐子项判分与理由
- `meta/run.json` — run → 题目映射
- `output/results/solution.json` / `solution_report.md` / `interaction_receipt.json` / `meta/expert_bridge.log` — 模型、报告、交互原文
- `workflows/cpe_state.json` / `best_workflow.json` — 冠军与精英谱系

---

## 0. 一句话结论

11 轮演化，**验证冠军始终是 round-0 的种子**（`interaction_workflow_05df287cb4d3` @0.8374），5 次上验证全部被拒。但逐题拆开后可以看到：

**演化确实在正确地修补具体缺陷**——2020_B 的 rigor 从被 r1 砸坏的 7.00 修回 9.00（超过种子的 8.33）——只是这些增益被 practicality 侧的无据扣分精确抵消，而 **0.005 的门限小于这套「4 题 × 1 次」测量的分辨力**，所以总分读不出任何变化。

即：**报表上的"零进展"不是演化的失败，是测量的天花板。**

---

## 1. 实验设置

| 项 | 值 |
|---|---|
| 臂 | from-scratch Claude 臂（**无 critic、无 rubric 协同**，`workflows/round_*` 里没有 `critic_review.*`）|
| 初始策略 | 信息优先策略（info-first），1575 字符，见 `initial_interaction_workflows.json` |
| 训练批 | 每轮 2 道题 × **2 次独立求解重复**，从 train 池**有放回**独立抽样 |
| 验证集 | 固定 4 道：2020_B / 2020_D / 2020_E / 2020_F，每题 1 次求解 |
| 判分 | MM-Bench 四维，每维 = 2 个子项（1–10 整数）/10，**judge_repeats=3** |
| 效用 | `utility_basis = mean_report_score_minus_interaction_cost`，即 四维均值 − 交互惩罚 |
| 交互上限 | 3 次交换，`exchange_weight 0.5 / token_weight 0.4 / latency_weight`（见 state）|
| 门 | 训练门：候选 > max(父代) + 0.005；验证门：候选 > 冠军 + 0.005 |
| sampling_seed | 1467281314156841765 |
| 谱系 | `current_policy` = r11 的 `train_parent_1` (`interaction_workflow_bc49a013c7df`)；`best_policy` = r0 种子 |

---

## 2. 门表：11 轮，冠军从未换手

| 轮 | 策略名 | 长度 | 与种子相似度 | 父代 net | 候选 net | Δnet | train 门 | val net | val 门 |
|---|---|---|---|---|---|---|---|---|---|
| r1 | Sequential Structural Validation Policy | 3471 | 0.624 | 0.7432 | 0.8011 | **+0.0579** | ✓ | 0.8212 | ✗ |
| r2 | Structural-Only Grounding Policy | 3892 | 0.576 | 0.7015 | 0.8218 | **+0.1202** | ✓ | 0.8218 | ✗ |
| r3 | Adaptive Counterexample Strategy | 4117 | 0.553 | 0.8448 | 0.8124 | −0.0324 | ✗ | — | — |
| r4 | Interaction Policy with Rejection-Integrated Counterexample | 4369 | 0.530 | 0.8151 | 0.8167 | +0.0015 | ✗ | — | — |
| r5 | Gap-Driven Operator Selection | 4516 | 0.491 | 0.8203 | 0.7748 | −0.0455 | ✗ | — | — |
| r6 | Targeted Rejection Recovery | 4910 | 0.459 | 0.8189 | 0.7868 | −0.0322 | ✗ | — | — |
| r7 | Loss-Aware Structural Validation | 4572 | 0.512 | 0.7258 | 0.7882 | +0.0625 | ✓ | 0.8310 | ✗ |
| r8 | Rejection-Targeted Structural Revision | 5544 | 0.418 | 0.7767 | 0.8279 | +0.0512 | ✓ | 0.8183 | ✗ |
| r9 | Deliverable-Aligned Structural Validation | 6587 | 0.365 | 0.7705 | 0.7996 | +0.0292 | ✓ | 0.8369 | ✗ |
| r10 | Deliverable-Mapped Structural Validation | 6165 | 0.385 | 0.7788 | 0.7437 | −0.0350 | ✗ | — | — |
| r11 | Bias-Quantified Structural Validation | 6029 | 0.391 | 0.8090 | 0.7841 | −0.0250 | ✗ | — | — |

**5 次过训练门（r1/r2/r7/r8/r9），0 次过验证门。**

冠军门槛 = 0.8374 + 0.005 = **0.8424**。5 次 val 的实际值：0.8212 / 0.8218 / 0.8310 / 0.8183 / **0.8369**（r9 只差 0.0055）。

**注意策略文本一直在漂移**（相似度 0.624 → 0.365，长度 3471 → 6587），这次**不是**"优化器逐字复制父本"的失败模式。

---

## 3. 测量工具的性质（决定了后面所有的解读）

### 3.1 交互惩罚是一个常数

18 个已测 run 的（纯任务分 − 净效用）：**均值 0.0428，sd 0.0003，范围 [0.0422, 0.0432]**。

因为父代和候选背着同一个偏移，它在每一次门的比较里都**自己抵消**。

### 3.2 去掉交互项，门的结果一模一样

| 冠军起手 | 门（+0.005） | r2 | r7 | r8 | r9 |
|---|---|---|---|---|---|
| 净效用 0.8374 | 0.8424 | −0.0206 | −0.0114 | −0.0241 | −0.0055 |
| **纯任务分 0.8802** | 0.8852 | −0.0206 | −0.0112 | −0.0237 | **−0.0050** |

差距一致到小数点后三位。**过训练门的还是同样 5 轮，冠军还是种子。**

唯一的实质影响：去掉惩罚后 **r9 的 val 纯分与种子逐位相同（0.880208 = 0.880208）**，它的 −0.0005 净差全部来自惩罚（r9 的咨询代价略高）。

> 推论：**交互项不是卡住演化的原因**。砍掉它等于用一把量不出差别的尺子去选，且会拆掉"问得更多更长"的唯一刹车。

### 3.3 判分是格点，且在 0.80–0.90 饱和

每个维度 = 2 个子项（1–10 整数）/10，再按 3 次重复平均 → **取值只能是 k/60 的格点**（原生 1–10 分则是 k/6）。

在 val 这 4 道题上，四维长期钉在 8.0–9.0 之间：

- **2020_D 各轮四维恒为 0.900**（三个 val 轮次、所有候选，一个值都没动过）
- 2020_F 的 pract 在 0.78–0.90 之间跳
- 2020_E 的 pract 在 0.767–0.833 之间跳

**没有余量去表达策略差异。**

### 3.4 同一解答内判分是确定性的；方差来自求解器

- r4 的 2017_B：父代 3 个 trial 判分 0.80/0.80/0.80，候选 0.55/0.55/0.55 —— **完全一致**
- 但每题有 **2 次独立求解**（`r1pN` / `r2pN`），两次交出的报告不同、判分也不同

所以**逐轮的分数摆动主要来自求解器侧的方差（约 ±0.02–0.035/题），而不是判分抖动**。

---

## 4. 策略演化轨迹：每轮补一个洞

九轮里每轮只加一处，而且**加的都是前几轮暴露出来的病灶**：

| 轮 | 名称 | 新增规定 | 针对的病灶 |
|---|---|---|---|
| r1→r2 | Structural-Only Grounding | **禁问经验数值**，改问定义/逻辑边界 | 训练证据里专家拒答幅度问题（`inventing them would be fabricating`）|
| r2→r3 | Adaptive Counterexample | 被拒后**不重新提整体结构**，改问"哪一条有问题" | r1 的"被拒即回退"删掉了结构 |
| r3→r4 | Rejection-Integrated | 回退 + **必须整合专家指出的缺陷** | r3 的局部修复 |
| r4→r5 | Gap-Driven Operator Selection | **算子由缺口类型决定，不再由交换序号决定** | 固定的 open→judgment→counterexample 序列 |
| r5→r6 | Targeted Rejection Recovery | 被拒后必须定位**被点名的具体元素** | 泛化修订 |
| r6→r7 | **Loss-Aware** | 交换 2 的结构**必须包含主导的损失/转化机制**（摩擦、衰减、状态转移），不得理想化除非题面明确许可 | r1/r3 的"结构被溶掉" |
| r7→r8 | **Rejection-Targeted Structural Revision** | 独立成节 **Rejection Handling Rule**：定位被点名缺陷 → 构造**最小修订** → 交换 3 针对**修订后**结构问反例 | r3 的"照方抓药把结构溶掉" |
| r8→r9 | **Deliverable-Aligned** | 独立成节 **Deliverable Alignment Rule**：把结构歧义**逐条映射到题面列举的每个子任务/交付物** | r2 的"Requirement 5 被并进 Task 4" |

r10/r11 继续沿这条线加（`Deliverable-Mapped`、`Bias-Quantified`），但两轮都没过训练门。

**观察**：这个方向说明优化器**确实把训练证据里的失败读出来了**——最后三条恰好对应本文 §5 中诊断的三个具体缺陷。

---

## 5. 逐轮分析

### 5.1 r1（val 0.8212，−0.0162）

**策略改动**：在种子的"按最关键的缺口选算子"之上，追加了一段固定的三步日程：交换 1 问量级、交换 2 提一个整体结构、交换 3 问什么会打破它；并写入关键约束 `Avoid proposing multiple alternatives in a single judgment query; present one coherent structural hypothesis to test` 和 `Assuming the structure from Exchange 2 is accepted (or the most plausible fallback if rejected)`。

> 算子名册（`Operator 2 -- judgment: … accept, reject, or rank`）在种子和 r1 里**逐字节相同**。r1 没有删掉 `rank`，而是追加了一段程序说明，把 `rank` 的适用场景（多候选）系统性地关掉了。

**分数**：pract −0.042、rigor −0.042（analysis +0.012、resbias +0.004）。

**扣分定位**：**2020_B 的 rigor 0.833 → 0.667**（[8,8] → [7,7]）。

**因果链（逐字可追）**：

1. 两次运行的交换 1 都拿到真实量级（414 / 495 字符），无差异。
2. 交换 2 都拿到 **6 字符的 `reject`**（全实验 8 个 run 的交换 2 回复恒为 6 字符）。但 **r0 把判断拆成 A/B 两个可分辨假设**、邀请 `accept, reject, or rank`，所以否决可归因；**r1 打包成三通道整体**，否决不定位——r1 的 Q3 自己承认 `rejected the three-channel structure **without specifying which channel**`。
3. r0 的交换 3 明确索取替代（`which formulation you would **substitute**?`）→ 专家给出时变可蚀性 → **写进报告假设 (5)**：
   > `Erosion is time-varying: the erosion rate is proportional to the wave energy flux divided by the current cohesion C(t)… (expert exchange 3)`
   r1 的交换 3 按策略预设走回退（`I fall back to the simplest defensible mechanism`）→ **删掉 crown-failure 通道**，只剩"We topmost grain 掉了就算失败"的静态阈值。
4. 这一步把失效判据降维成"最顶端沙粒多久被打掉"，只取决于顶面离冲流线（H=1 m）多高，**形状几何完全退出评分**。证据是 r1 自己的排名表：

   | 形状 | 高度 | 存活时间 |
   |---|---|---|
   | tall_crown (r=0.3, h=1.5) | 1.5 | **2.00 h** |
   | cylinder / box / truncated_cone / pyramid | 1.0 | **1.00 h**（四个并列，一个不差）|
   | hemisphere (r=0.7) | 0.7 | 0.78 h |

   r1 的报告原文：`The optimal shape under the baseline micro-tidal scenario is the **tall narrow crown**, because its crown sits above the mean-swash line (H = 1 m) and is dosed only at high tide`。**而同一份报告在敏感性里又写着 `the ranking inverts — the tall crown collapses first`**（推荐了它自己承认会先垮的形状）。
5. 专家在交换 3 的 A3 早已预言了这一切：
   > `the tall shape's topmost grain sits above the mean-swash line and never accumulates dose — so it is **scored as never failing** … **inverts the ranking exactly in the tidal-inundation regime the problem specifies**`

**judge 逐字扣的就是这条链的末端**：

> `[7] …oversimplify erosion mechanisms and include a **structurally questionable candidate shape (tall narrow crown)** for a foundation.`
> `[7] …**lacks structural mechanics** and detailed hydrodynamic shape interactions.`

**量级**：2020_B 的 rigor −0.167 → 占 r1 整场 val 赤字 0.0167 的 **63%**。

---

### 5.2 r2（val 0.8218，−0.0156）

**策略改动**：三次里最大的一次反转。抬头加 `with a strict prohibition on requesting **empirical magnitudes or constants**`；交换 1 从"问量级"改为"问结构性/定义性边界"，明写 `Do not ask for magnitudes, rates, or empirical constants`。

> **为什么演化往这个方向走**：r2 的演化 prompt 里带着训练批的原始对话，其中专家回答是
> `I can't supply those magnitudes as if they were standard constants — **they aren't in the data, and inventing them would be fabricating the model's core parameters.**`
> 另一道训练题问量级也拿到 `reject`。**优化器学到的是"别问会被拒的东西"，而不是"问最有价值的东西"** —— 一次拒答被泛化成全局禁令。

**交互内容实际变成什么**：交换 1 的回复**反而更长**（4 题：1034/816/923/865，均值 ~910；种子均值 ~480）。所以禁令没有让交互变空，只是把性质从"拿数据"换成了"拿框架"。

**扣分定位**：**2020_B 的 analysis 0.900 → 0.683**（两个子项都是 7）。

**真正原因（与交互无直接通路）**：r2 的 `solution.json` 只有 **4 个任务**，Requirement 5（写文章）被并进 Task 4 的 Scope：

> `Scope: propose … additional measures beyond shape and moisture that extend longevity, **and write a short informative article (1-2 pages) describing the model and results for … Fun in the Sun.**`

报告结构里也只有 4 个 `## Subtask` 小节（文章正文被塞在末尾，`Fun in the Sun` 出现 5 次）。**文章其实写了，但没注册成独立子任务**，而 analysis 这一维判的正是任务分解。

**judge 原文**：
> `the definition for Task 4 is flawed as it **conflates the strategy identification (Requirement 4) with the article writing (Requirement 5)**`
> `Requirement 5 (writing the article) is **incorrectly bundled into Task 4**`

**对照（同题）**：r0/r1/r7/r8/r9 的 2020_B 全部是 **5 个子任务、analysis 0.90–0.95**；只有 r2 是 4 个 → 0.68。
（注意别误读成"4 不好"：2020_D 各轮都只有 4 条却拿 0.90——那题本来不到 5 个需求。是 2020_B **少了第 5 条**。）

---

### 5.3 r3（train 门未过，0.8448 → 0.8124）

**策略改动（只有一处）**：交换 3 从 `Assuming the structure from Exchange 2 is accepted (**or the most plausible fallback if rejected**)…` 改为
> `If the structure is rejected, **do not immediately propose a new full structure**; instead, ask the expert to identify **which aspect**…`

**交互内容：这处改动生效了。** 候选的 Q3 原文：
> `You rejected the proposed structure in Exchange 2 **without specifying which item carried the flaw**. **Per the consultation plan, I am not re-proposing a full structure now.** Instead, please identify the specific structural flaw or boundary condition in my proposal (items 1–5: …)`

→ 专家精确点名 **Item 2**：`With no human cars, the "closing gap is human" construction has no limit … L = p/(1−p) diverges as p → 1, so the unit density … collapses`，并给出处方 `The mechanism must treat the human closing gap as a term **weighted by (1−p)**, vanishing at p = 1.`

**但结果反了：同一场"被拒"，父代补了结构，候选溶了结构。**

| | 交换 2 的提案 | 被拒后做了什么 | 最终模型的容量式 |
|---|---|---|---|
| **父代**（老策略，走 fallback）| 单一结构 "a single monotone capacity-density shift" | 自己推断"缺了一个不稳定项"，**补上** | `C_eff(p) = L·q_cap(p)·h(p)`，其中 `h(p) = 1 − d·p·(1−p), d = 0.08` 是**独立的混流稳定性因子**，并被判分夸为 `correctly models the **interplay between capacity gains and stability losses**` |
| **候选**（新策略，点名式）| 5 条 bundle，第 1 条是 **Bernoulli run-length 微观结构**（`L = p/(1−p)`，`[platoon L] + [1 human car]`）| 照处方字面执行 | `k_cap(p) = 45 / ((1−p) + p·α)` —— **run-length 结构被溶解**，退化成"按车队份额对两种车头间距做线性混合" |

**"丢掉 run-length 结构"的确切含义**：提案第 2 条写明 `An SDC follows a human at the same human headway (**no gain when the leader is human**)` —— 收益只存在于"队内相邻"。随机混流里相邻车对都是 SDC 的概率是 **p²**，所以均值间距应是 `p²·h_p + (1−p²)·h_h`（父代就是 `p_eff = p²(1+γ)`）。而候选的 `(1−p)h_h + p·h_p` 等价于**每辆 SDC 都享受压缩间距，不管前车是谁**——邻接关系消失。

代价有两部分：
- **机制**：一步"份额→间距→容量"映射，没有任何"谁跟在谁后面"的内容，也没有稳定性项
- **参数**：父代是 `α, γ 联立求解对齐两个文献点`（50% → +7.5%，90% → +18%）；候选只剩 `alpha = 0.90`，一个参数、一个点

**judge 原文**：
> 父代 `[9] …It **correctly models the interplay between capacity gains and stability losses** in mixed traffic`
> 候选 `[7] …though it **simplifies dynamic interactions by relying on static equilibrium calculations** rather than full simulation.`

候选的 pract 在 **6 次判分、两次独立求解里全部落在 0.75–0.80**（父代 0.80–0.90）——**是钉死的差，不是噪声**。

**第二处退化（同样能追到交互）**：候选第二次求解的交换 1 问的是 capacity 的**定义**，专家回答里给了一条许可 `p is a single global scalar … **segment-level variation is not licensed by the statement**`。候选的报告照此处理并标注来源：
> `(f) **the daily average is treated as the demand level (per Exchange 1)**`
judge 扣的正是这一条：
> `[7] …**the simplification of demand to average daily flow ignores peak-hour dynamics central to the problem**`
而父代问的是三个考虑的**优先级/约束**，拿到的是"你得更复杂"，最后用了 `q_peak = ADT·r/(W/4)` 的显式峰值换算。

> **规律：问"定义"拿到的是简化授权，问"约束/优先级"拿到的是复杂化要求。**

**最刺眼的一点**：候选**自己**在交换 1 里从专家那问到 `The benefit is a function of the length of consecutive SDC runs, **not fleet share alone** … **Contiguity is the intended domain of the cooperation variable.**`，而最终模型恰恰是 fleet-share-only。
（公平地说，父代也没听自己的对话——它的专家说 `Flow share is the right reading`，它的模型却有 p²。所以"对话→模型"这条映射在两个方向上都松，这也是为什么本文只能给出**可指认的因果**而非统计结论。）

---

### 5.4 r4（train 门未过，0.8151 → 0.8167）

**前提修正**：r4 **不是"比父代低"**，均值其实 +0.0016（只是低于 +0.005 的门）。两题一升一降：

| | 父代 | 候选 | Δ |
|---|---|---|---|
| 2017_B | 0.7955 | 0.7617 | **−0.034** |
| 2019_A | 0.8347 | 0.8716 | **+0.037** |

**策略改动：r4 把 r3 的修复回退了。** 抬头退回 r2 的"禁问数值"，交换 3 退回"fallback if rejected"，只在末尾追加一句 `the fallback structure … must **explicitly integrate the specific element the expert identified as flawed**`。
→ **r4 ≈ r2 的正文 + 一句话补丁**（演化在 r3↔r4 之间来回震荡）。

**扣分定位**：2017_B 的 analysis：父代 **0.80 / 0.90**，候选 **0.55 / 0.70**（两次独立求解）。判分在同一解答内 3 次 trial 完全一致。

**四个 run 的 `subtask_count` 全是 1**（单块任务），judge 在第 2 个子项的判词也全是同一句 `fails to decompose …`，但分数从 **4 到 9**。差别在于 `task_description` 有没有把题目的变化维度铺开：

- 父代 rep1（0.80）：`generalizes as **B/L, demand, booth mix, and autonomous-vehicle (AV) share** vary, plus its performance under light and heavy traffic`
- 候选 rep1（0.55）：只写到 `characterize performance under light and heavy traffic` —— B/L、demand、booth mix、AV share 四个维度全没了

**可疑的相关（不足以定论）**：judge 点名的维度在高分对话里出现过、在最低分那次没出现——

| run | 交换 3 的专家回答提到 | analysis |
|---|---|---|
| 父代 rep1 | `…a booth mix dominated by **manual booths and low ETC share**` | 0.80 |
| 候选 rep2 | `a **booth-type mix or autonomous-vehicle penetration** that makes the arrival process non-stationary` | 0.70 |
| 候选 rep1 | 只讲 `two candidates with identical cost and identical throughput feasibility … conflict class` | **0.55** |

即"咨询里浮现了哪些变化维度，报告的任务描述就很可能跟着铺哪些维度"。但 n=4，且 `task_analysis` 是求解器写的不是专家写的，**只能算疑点**。

> **附带证据**：r4 的策略与 r2 几乎同一份，两题却是 +0.037 / −0.034。**策略文本几乎没变、结果摆了 0.07** —— 这是"求解器方差淹没策略效应"的直接证据。

---

### 5.5 r9（val 0.8369，−0.0005；纯分与种子逐位相同）

**为什么和种子"打平"**：val 的 4 题 × 4 维 = 16 个判分值，换成原生 1–10 分：

| 题 | analysis | rigor | pract | resbias |
|---|---|---|---|---|
| 2020_B | 9.00 → 9.00 | **8.33 → 9.00** | 8.50 → 8.50 | 8.50 → 8.83 |
| 2020_D | 9.00 → 9.00 | 9.00 → 9.00 | **9.00 → 8.50** | 9.00 → 9.00 |
| 2020_E | 8.50 → 8.83 | 9.00 → 9.00 | **8.33 → 8.00** | 8.83 → 9.00 |
| 2020_F | 9.00 → 9.00 | 9.00 → 9.00 | **9.00 → 8.17** | 8.83 → 9.00 |

- **16 个值里 8 个逐位相同**；其余全部在 ±1 个判分点以内
- **差额精确抵消**：两组的整数总和都是 **845**（k/60 格点），16 值均值两边都是 **0.880208**
- 净效用差 −0.0005 **全部来自惩罚项**（种子 0.0428，r9 0.0433）

而这两轮交出的是**完全不同的文档**：val 报告字节数比值 2020_B **1.45×**、2020_D 0.83×、2020_E 0.78×、2020_F 0.96×。

**这个"打平"其实是"一涨一跌"**，而且**涨的那处正是被修好的病**：

- **涨**：2020_B 的 rigor 8.33 → **9.00**（比种子还高）——那正是 r1 砸坏的地方（r1 曾掉到 7.00）。r9 的对话把结构补回来了：
  > **A1**：`Primary criterion: **time until structural failure — loss of recognizable form (collapse/slumping/toppling)**, not a volume-fraction threshold.`
  > **Q3**：`You rejected the Exchange-2 structure without specifying the flaw. **The minimal revision I can infer** is …`（r7→r8 的 Rejection Handling Rule 在起作用）
  > **A3**：`a shape whose failure is governed by **toppling of the whole body** rather than by base narrowing`
  报告里 `structural` 出现 3 次、`crown` 仅 6 次（r1 是 36 次）。
- **跌**：全是 pract，共 −1.66 个点；其中 2020_F 的 9.00 → 8.17 是最大单笔，而**该题 pract 的扣分此前已证实两条理由全是褒义、没有文本依据**（§5.6）。

---

### 5.6 其余轮次要点

- **r7 / r8**：val 0.8310 / 0.8183，均被拒。r7 的 train Δ +0.0625 来自父代一次低抽样（父代 pract 0.663 / rigor 0.717，而同一策略在 val 上是 0.87 量级）——**训练门在选噪声**。
- **r5 / r6 / r10 / r11**：全部未过训练门（Δ −0.046 / −0.032 / −0.035 / −0.025），停留在 2 题 × 2 次的训练批测量上，与 val 无关。
- **判分稳定性的反例**：2020_F 在 r1 里两条理由**全为褒义、无任何负面从句**，却从 9/9 掉到 8/8（0.900 → 0.800）；同一轮 2020_B rigor 却涨了 0.067。说明**在单题单次测量上，"同一质量→不同分数"会真实发生**（跨解答，不是判分抖动）。

---

## 6. 低分题分布（全实验，按 <0.85 的维度出现次数）

| 题目 | 低分/总 | 集中在哪 |
|---|---|---|
| **2020_B** | **7/24** | rigor(0.667/0.833)、pract ×4 |
| 2014_C | 7/16 | rigor/pract（**题目决定**：母代同题 0.583/0.592）|
| 2019_C | 7/12 | analysis/pract |
| **2020_E** | 6/24 | **pract ×6，五轮候选全在 0.767–0.833** |
| **2020_F** | 6/24 | pract ×4、resbias/analysis 各一次 |
| 2020_D | **0/24** | 什么都没掉 |

val 池里 **2020_B / 2020_E / 2020_F 是低分常客，2020_D 是零低分题**。

---

## 7. 归因总表

| 轮 | 交互质量 | 分数变化 | 可归因于交互？ |
|---|---|---|---|
| r1 | 差（打包提案→不可归因否决→回退删结构）| −0.0162；2020_B rigor −0.167 | **是，唯一一例交互真的伤分**（judge 判词逐字指向被删的 crown 通道）|
| r2 | 中（禁问数值→改问定义，回复反而更长）| −0.0156；2020_B analysis −0.217 | **否**（无直接通路；任务是求解器自己规划的——疑似"注意力被目标定义占满，最后一条任务成收纳筐"）|
| r3 | **好**（点名式修复，第一次拿到精确缺陷）| −0.0324（门未过）| **是，但是负向**（照处方字面执行把 run-length 结构溶掉；交换 1 的定义型问题换来一条简化授权）|
| r4 | 中（回退 r3 的修复 + 一句话补丁）| +0.0016（门未过）| **否**（掉分在报告的任务描述完整度，且同策略两题摆 ±0.035）|
| r9 | **最好**（累积三条修复，2020_B 结构被修回）| −0.0005（纯分与种子逐位相同）| **是，但是被抵消**（rigor +1.34 被 pract −1.66 抵掉）|

**交互策略的改动幅度与分数变化方向对不上**——这是全部 11 轮最稳的经验事实。

---

## 8. 结论与建议

### 结论

1. **报表上的"11 轮零进展"不是演化的失败，是测量的天花板。** 演化在正确地修补具体缺陷（§5.5 的 2020_B 是最硬的证据），但 4 题 × 1 次的 val 分辨不出 0.01 量级的改进，而门限只有 0.005。
2. **冠军的杆立在种子的单次高位抽样上。** 种子的 0.8802 是 5 次 val 观测里的最大值；在"用一次抽样的最大值当门槛"的设定下，任何候选都赢不了。
3. **交互项不是卡住演化的原因**（§3.1/3.2：它是常数，去过不掉门，留着还提供信息与刹车）。
4. **优化器正在被训练证据带偏**：它学到的是"避开会被拒绝的问题"（r2 的禁问数值），而不是"问最有价值的问题"。这个偏差不会被当前信号纠正。
5. **judge 的扣分在若干处追踪的是报告的显式度与完整度**（是否声明假设、是否枚举题目的变化维度、是否把每个需求注册成子任务），而不是模型的实质质量。r3 的父代与 r4 的两题都是这一类的直接证据。

### 建议

| 优先级 | 动作 | 理由 |
|---|---|---|
| **高** | 对种子做 2–3 次 val 重复，用均值当冠军；或把 val 提到 4 题 × 2–3 次重复 | 当前门限 0.005 小于单次测量噪声；冠军是单次抽样的最大值 |
| **高** | 把 val 扩到能分辨 0.01 量级差异的规模（加题或加重复）| §5.5：一整轮有效改进在现有尺度上读数为 0.000 |
| 中 | 检查训练门的边际（现为 +0.005）在 2 题 × 2 次上是否等价于掷硬币 | r2/r7 的过门来自父代低抽样（0.575 / 0.663 的 pract）|
| 中 | 给"修复"环节加一道检查：修复后的模型是否比原模型更完整（而非更简单）| r1/r3 的两次退化都是"修复=简化"，且没有任何机制在把关 |
| 低 | 若要继续用交互项，考虑把它从**常数惩罚**改成**能区分信息量的形式** | 现在 penalty ∈ [0.0422, 0.0432]，等于白扣 |

### 未解问题（数据不足以定论）

- r4 的"咨询维度 → 报告任务描述维度"的相关只有 4 个样本，需要更多轮次才能确认。
- r2 的"注意力被交换 1 的定义问题占满，导致 Requirement 5 被并入 Task 4"是推断，没有直接证据链。

---

## 9. 交互设计的问题（可改进点）

> 本节基于**全部 118–119 个 run** 的 `interaction_receipt.json`（提问与专家回答全文）统计（实验仍在跑，不同统计脚本执行时新 run 会陆续出现，分母因此有 ±1 的差），复现脚本见 §附。
> 所有百分比都是**快照值**，用于说明分布取向，不要当作精确计数。

### 9.0 三个算子在做什么（先把账算清）

| 交换 | 算子 | 118 个 run 的回复长度 | 信息产出 |
|---|---|---|---|
| 1 | Operator 1 open-ended（问缺口）| 中位 **825** 字符（范围 6–1327）| ✅ 唯一的外部知识通道 |
| 2 | Operator 2 judgment（请裁决）| **恒为 6 字符**（118/118）| ❌ **零** |
| 3 | Operator 3 counterexample（问什么会打破它）| 中位 **717** 字符（范围 47–1221）| ⚠️ 只谈 agent 自己的模型，不引入外部知识 |

**三次交换里有整整一次（1/3 预算）恒定不产出任何信息。**

### 9.1 判决算子是"没有信息量的裁决器"（最严重的设计问题）

全 118 个 run 的交换 2 回复分布：

```
 81 次 ( 69%)  'reject'
 37 次 ( 31%)  'accept'
118 次 (100%) 长度 == 6 字符
```

这是专家 prompt 里对判决格式的规定造成的（r15 启动时载入的版本要求判决只回一个词；详见 §9.7 的时间线说明）。后果：

- **两个分支都不产生知识**：`accept` → 交换 3 转去问"什么会打破它"；`reject` → agent 触发一次结构突变。
- **69% 的运行里，这个算子的实际功能是"触发突变"，不是"获得信息"**。
- 逐轮无改善：拒率在 33%–92% 之间波动（r7 高达 92%），**没有任何下降趋势**。

> 一个占了 1/3 预算、100% 只回一个词、69% 回"否"的算子，本质上不是信息通道，而是一个**掷硬币式的突变触发器**。

### 9.2 "被拒"没有变成"索取替代"的固定通道

被拒之后的两种走法，在 118 个 run 里的分布：

| 走法 | 次数 | 后果 |
|---|---|---|
| **回退**（`fall back to the simplest defensible mechanism` / `generic revision`）| 36/81（**44%**）| **把被拒的结构丢掉**，模型做减法（r1 删 crown 通道、r3 溶掉 run-length 结构）|
| 修订/再提 | 45/81（56%）| 取决于修订质量，可以很好也可以很糟 |

**这里有一个全实验唯一可测量的"策略 → 行为"因果**：r7→r8 加入 **Rejection Handling Rule** 之后，回退率断崖式下降：

| 轮 | r6 | r7 | r8 | r9 | r10 | r11 | r12 |
|---|---|---|---|---|---|---|---|
| 交换 3 走回退的比例 | 38% | **92%** | **17%** | **8%** | **0%** | 12% | **0%** |

**说明策略文本确实能改变交互行为**——但 r8–r12 的分数并没有因此上升（r8/r9 都止步验证门，r10–r12 连训练门都没过）。所以"不丢结构"只是必要条件：r3 的教训是，即使不丢结构，**逐字执行一条局部处方也能把结构溶掉**。

### 9.3 没有"主动索取"的算子——专家只能被动应答

**全部 118 个 run 里，交换 1 和交换 3 中主动索取"我漏了什么 / 你有什么建议 / 还有什么"的次数：0。**（正则含 `what am i missing`、`anything else`、`what would you advise/recommend/suggest`、`any pitfall/caveat/common mistake` 等）

交换 1 的问题类型分布（可多标）：

| 类型 | 占比 |
|---|---|
| 目标/约束解释（objective / constraint / hard-soft / trade-off / priorit）| 83% |
| 数值/量级（magnitude / typical value / order of magnitude / how large）| 82% |
| 机制/结构（mechanism / structure / formulation）| 81% |
| 域/边界（domain / boundary / regime / valid range）| 78% |
| **验证/核对（verify / check / confirm / is it correct）** | **8%** |

**全部是"我提出，你判定"的形式。** 专家的三类知识没有入口：

1. **硬性约束**（"这个变量不可能同时为正"、"你这个假设在这个域里必然不成立"）
2. **行业常识**（"实际上没人会这么建"、"这个量级在工程上是不可能的"）
3. **常见坑**（"这类模型最常犯的错误是……"）

量化证据——专家回答里出现"你必须 / 硬约束 / 不可行 / 不合常理 / 标准做法 / 通常"这类**规范性**表述的比例：

| | 交换 1 | 交换 3 |
|---|---|---|
| 含规范性表述 | **31%** | **13%** |
| 含具体数字 | **14%** | **17%** |

**三分之二的交换 1 回答里没有任何规范性的东西**——因为没人问。

### 9.4 "专家总是拒答"的真实代价与误解

**交换 1 的回答里有 42%（49/118）含"题面未定 / 无法提供 / 没有依据 / 那会是伪造"这类拒答或声明无依据的表述。** 逐轮分布：

| 轮 | r0 | r1 | r2 | r3 | r4 | r5 | r6 | r7 | r8 | r9 | r10 | r11 | r12 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 拒答率 | 25% | 25% | **58%** | 38% | 62% | 14% | **75%** | 17% | 42% | 58% | 25% | 38% | 12% |

**没有任何改善趋势**。而且 r2 的"禁问数值"改动**反而把它从 25% 推到 58%**。

更关键的是：**这条禁令本身几乎没有生效**。按同一个正则统计"交换 1 是否在问数值/量级"：

- 带禁令的策略（98 个 run）：**81%** 仍在问
- 无禁令的策略（20 个 run）：**85%** 仍在问

（正则偏宽，但两组用同一把尺子，所以比较有效。）**文字禁令改变不了行为。**

**这里有一个深层误解需要指出**：被拒的往往是**题面本来就不提供的信息**——专家回答"这个数据里没有、编造它就是伪造模型的核心参数"是**正确且高价值的回答**。但优化器把它读成了"这类问题不好"，于是在 r2 转而禁问。

> **优化器在惩罚"提问的行为"，而不是惩罚"提问的内容没被用上"。** 正确的信号应该是"这条信息确实拿不到，记录下来"，而不是"以后别问"。

### 9.5 交换预算被"自证"吃掉

3 次交换的实质内容：

| 交换 | 在谈谁 | 是否引入外部知识 |
|---|---|---|
| 1 | 题面/数据里缺什么 | ✅ 是 |
| 2 | **agent 自己的模型结构**（提案 → 裁决）| ❌ 否 |
| 3 | **agent 自己的模型结构**（裁决后的反例）| ❌ 否 |

**一次咨询里最多拿到 1 次外部知识**，另外 2 次是自我审议。而在 42% 的情况下，连那 1 次拿到的也是"题面没定"。

被拒时更糟：结构被打掉，**却没有余额重建**（r1/r3 都是这样带着缺陷定稿的）。

### 9.6 缺失的"常识/约束通道"在报告里的可见后果

两处可以直接指认：

1. **r1 的 2020_B**：模型删掉 crown-failure 通道后，选出 **tall narrow crown**（细高冠形）作为最优地基形状——**任何堆过沙堡的人都知道它会倒**。这正是"常识知识"该拦住的地方，但**没有任何算子能让专家说出这句话**（专家在交换 3 只说"排名会反转"，因为问的是"什么会打破机制"，不是"这样做合不合理"）。
2. **r3 的 2017_C**：模型最终用 fleet-share-only 的线性混合，而专家的**交换 1 已经说过** `Contiguity is the intended domain of the cooperation variable`。**知识在场，但没有通道把它固化成约束**——专家说完就散了，采纳与否全靠 agent 自觉。

**两处都不是"专家不知道"，而是"专家的话没有落点"。**

### 9.7 一个必须注明的时间线（防止误读本节）

**r15 的实验进程于 2026-09-30 00:04:51 启动；专家 prompt 是模块级常量（`SUBSTANTIVE_EXPERT_ROLE_PROMPT` 在导入时绑定给引擎），整个实验——包括撰写本文时正在跑的后续轮次——都用启动那一刻载入内存的版本。** 之后修改源码文件**不会**影响它。

对照：

| | mtime | 状态 |
|---|---|---|
| `src/OpenClaw/run_substantive_interaction_experiment.py` | **2026-09-30 12:12:40** | 工作区已改（`M`，未提交）|
| r15 实验启动 | **2026-09-30 00:04:51** | —— |

**也就是说：工作区里 12:12 的那次修改，恰好把本节 §9.1 与 §9.3 两条修掉了，但 r15 读不到。** 当前工作区版本的关键两段：

```text
For a judgment question the verdict comes first, as the single word "accept" or
"reject", and one clause follows naming what decided it. Never answer with the
verdict alone: a rejection the asker cannot learn from is a rejection it will
propose again.                      ← 修 §9.1（否决不再是零信息）
```
```text
- the real-world facts it rests on -- typical values and ranges, orders of
  magnitude, units, standard practice in this domain, what is physically possible
  and what practitioners never do and why;
- the constraints that bound it, including the ones the problem statement never
  states: a material or physical limit, a regulation or standard, a cost, time or
  labour budget ...                    ← 修 §9.3/§9.6（常识与硬约束有了固定出口）
```

同时还给专家 prompt 补上了三个算子的说明（旧版没有算子块，专家并不知道自己被问的是哪一类）。

**又及（本文写作期间的第二次修改）**：随后该 prompt 被**整体替换**为一版更严格的文本——要求 `**Answer only the question the agent actually asks.**`、明令 `Do not add any of this in order to display expertise`，把"真实数量级/领域标准实践/隐含条件"从**每次回答必带**降为**仅当与当前问题直接相关时可用**。

- §9.1 的修复**保留**（Operator 2 仍要求 `Answer "accept" or "reject" first, then state only the facts or constraints necessary to support that judgment`）——**这条最重要，单词否决的零信息问题不会回来**。
- §9.3/§9.6 的修复**被收回**：新文本不再强制专家每次回答都给出真实世界事实与题面没写的约束。按 §9.3 的统计（旧版下只有 31% 的交换 1 回答含规范性表述），新版的这一比例**预期会更低**——常识与硬约束是否进入咨询，重新变成"取决于 agent 问到没问到"。

**两个必须记住的后果**：

1. **§9.1 / §9.3 的缺陷在源码里已有对应修复，但 r15 这 12 轮的统计（118/118 六字符、0/119 主动索取、31% 规范性表述）全部是旧版的行为** —— 要验证修复效果**必须新起一轮实验**，不能拿 r15 后面的轮次当样本。
2. **run 产物里不保存专家的 system prompt**（`output/logs/operator_feedback/expert_request_N.json` 只有 `rubric_id` / `interaction_stage` / `question` 三个键）。所以"r15 具体用的是哪一版"只能从 **118/118 的六字符模式**反推，无法从文件直接核实。若要以后可复核，应把 system prompt 一并落盘。

### 9.8 改进建议（按优先级）

> 标注 **✅已修** 的表示工作区源码里已有对应改动（但 r15 读不到，需新实验验证）。

| # | 动作 | 依据 | 状态 |
|---|---|---|---|
| **1** | **给判决算子加"理由通道"**：允许专家在 reject 时用一句话说明哪一条不成立；或把判决改成**多项选择**（哪一条 / 哪几条）。若坚持单词回复，则必须**在交换 3 固化"索取替代"** | §9.1：1/3 预算零产出；§9.2：被拒后 44% 直接丢结构 | **✅已修**（判决后仍要求"只说明支持该判断所必需的事实或约束"）；多项选择仍缺 |
| **2** | **保留并强化 r8 的 Rejection Handling Rule**（已被证明有效：回退率 92%→0%），但把"最小修订"升级为"**必须给出替代形式**" | §9.2：局部处方会被字面执行、把结构溶掉（r3 的 run-length）| 部分（r8 已有，强化缺）|
| **3** | **让专家主动给常识与硬约束**——行业常识、标准取值、题面没写的限值 | §9.3：0/119 主动索取；§9.6：两处失败的共同缺口 | ⚠️ **改为条件性**：最新 prompt 把它从"每次回答必带"退回"仅当与当前问题直接相关时可用"，并明令 `Do not add any of this in order to display expertise`；agent 侧的 elicitation 算子仍缺 |
| **4** | **给专家的回答留"主动补充"位**：允许"如果你认为有更关键的问题没被问到，请直接指出" | §9.3：现在专家被限定只回答所问 | ❌ 未修（新 prompt 仍写明 `Do not widen it`）|
| **5** | **交换额度改为按需**：至少允许在被拒后追加一次（现在被打掉结构却没有余额重建） | §9.5 | ❌ 未修 |
| **6** | **不要用"专家拒答"作为负信号**：拒答 = 该信息题面不提供，应记录为"不可获得"，而不是推动策略收缩提问范围 | §9.4：r2 的 58% 拒答率正是禁问数值的诱因，而禁令 81% 无效 | ❌ 未修 |
| **7** | **把"修复"和"简化"区分开**：加一道校验，若修订后的模型比被拒版本项数更少/更简单，要求 agent 明确说明为什么 | r1 删 crown 通道、r3 溶掉 run-length，两次都是"修复=简化"且无人把关 | ❌ 未修（无任何环节把关）|
| **8** | **把专家 system prompt 落盘**（现在只存 question）| §9.7：无法从产物核实 r15 用的是哪一版 prompt | ❌ 未修 |

> **注意**：1 和 3 的修复都在工作区（12:12 未提交改动），**r15 读不到**；要验证效果必须新起一轮实验。第 4/5/6/7/8 条目前**没有任何对应改动**。

### 9.9 一个反复出现的模式（供设计参考）

把 §9 与 §5 合起来看，失败的形状高度一致：

> **agent 提出结构 → 专家否决（无信息）→ agent 收缩模型 → judge 扣"简化/缺机制"。**

r1（删 crown 通道）、r3（溶 run-length）、r9 的 2020_F 都是这个形状的不同变体。**只要判决算子保持"单词否决"而交换 3 又只问"什么会打破它"，这个循环就会被反复触发**——因为否决提供了压力，却没有提供替代的方向。

---

## 附：本文用到的判分读法（便于复核）

```python
# 逐维分（含 3 次重复的均值）：k/60 格点
o = json.load(open(f'cpe_evaluations/round_{r}/{phase}/workflows/round_{r}/result.json'))
for pr in o['problem_results']:
    pr['dimension_scores']        # 四维，0.1-1.0
    pr['net_utility']             # 四维均值 − 交互惩罚
    pr['interaction_penalty']     # 每题的惩罚
    pr['judge_result']            # 代表重复的逐子项分数与理由
    pr['interaction_receipt']     # questions_asked / expert_answers 原文

# 逐 trial（判分在同一解答内是否稳定）
j = json.load(open(f'{run_dir}/meta/mmbench_judge/judge_stability.json'))
j['trials'][i]['dimension_scores']   # 每个 trial 的四维
j['average_dimension_scores']

# 题目映射与交互日志
json.load(open(f'{run_dir}/meta/run.json'))['problem_id']
# grep 'completed exchange' {run_dir}/meta/expert_bridge.log   # 回复长度（交换 2 恒为 6 字符）
```

### §9 全部统计的复现脚本

```python
import json, glob, os, re, collections, statistics as st

rows = []   # (轮次, policy_text, questions_asked, expert_answers)
for rc in sorted(glob.glob('cpe_evaluations/round_*/*/runs/round_*/*'
                           '/output/results/interaction_receipt.json')):
    run_dir = rc[:-len('/output/results/interaction_receipt.json')]
    wf = json.load(open(os.path.join(run_dir, 'workflow.json')))
    r  = json.load(open(rc))
    rows.append((int(rc.split('/')[1].split('_')[1]), wf.get('policy_text', ''),
                 r['questions_asked'], r['expert_answers']))
assert len(rows) == 118

# 9.1 判决算子的回复分布
print(collections.Counter(str(a[1]).strip().lower() for _, _, q, a in rows))
#   -> {'reject': 81, 'accept': 37}

# 9.2 交换 3 走回退的比例（逐轮）
FB = re.compile(r'fall ?back|fallback|simplest defensible|generic revision', re.I)
for r in range(0, 13):
    g = [x for x in rows if x[0] == r]
    if g:
        print(r, sum(1 for _, _, q, a in g if len(q) > 2 and FB.search(str(q[2]))) / len(g))

# 9.3 是否有人主动索取"我漏了什么/你的建议"（118 个 run 全为 0）
OPEN = re.compile(r'what am i (missing|overlooking)|anything else'
                  r'|what would you (advise|recommend|suggest)|any (pitfall|caveat|common mistake)', re.I)
print(sum(1 for _, _, q, a in rows
          if (q and OPEN.search(q[0])) or (len(q) > 2 and OPEN.search(q[2]))))   # -> 0

# 9.4 交换 1 被拒答/声称题面未定的比例（逐轮）
REF = re.compile(r"can'?t supply|cannot settle|does not settle|not in the (data|problem|statement)"
                 r"|no basis|would be fabricat|not licensed", re.I)
for r in range(0, 13):
    g = [x for x in rows if x[0] == r]
    if g:
        print(r, sum(1 for _, _, q, a in g if a and a[0] and REF.search(str(a[0]))) / len(g))

# 9.4 禁令是否生效（带禁令 vs 不带禁令，同一正则比较）
BAN  = 'Do not ask for magnitudes, rates, or empirical constants'
MAGQ = re.compile(r'magnitude|typical (value|range|number)|order of magnitude|how large|how many'
                  r'|what (rate|value|fraction|percentage)|rate of|numerical value', re.I)
for tag, g in (('禁问', [x for x in rows if BAN in x[1]]),
               ('未禁', [x for x in rows if x[1] and BAN not in x[1]])):
    print(tag, len(g), sum(1 for _, _, q, a in g if q and MAGQ.search(q[0])) / len(g))
#   -> 禁问 98 组 81% ; 未禁 20 组 85%   （禁令无明显效果）
```

### §9 各项结论的边界

- 9.3 的"问题类型"是**关键词多标签**统计（一个 run 可同时命中多类），不是互斥分类，只用于说明分布取向。
- 9.4 的 `MAGQ` 正则偏宽，单看绝对值会偏高；**结论建立在"带禁令/不带禁令用同一把尺子"的对比上**（81% vs 85%）。
- 9.1 的 6 字符回复是 prompt 强制结果（`STUBSTANTIVE_EXPERT_ROLE_PROMPT` 里的 `reply with exactly one word`），跨臂一致。
- 9.2 的"回退率断崖"（r7 92% → r8 17%）与 r7→r8 加入 Rejection Handling Rule 时间吻合，但 12 轮的样本量（每轮 7–12 个 run）**不足以排除题目难度变化的影响**。
