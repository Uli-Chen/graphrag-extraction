# MemATK：历史锚定的拓扑敏感图抽取

## 1. 摘要

MemATK 面向黑盒 GraphRAG 的预算受限图抽取。给定只能通过自然语言查询访问的目标系统，方法维护一张累计恢复图，并在每轮自动决定：继续进行覆盖面更广的探索，还是围绕一个已恢复实体进行定向利用。其目标不仅是增加恢复元素数量，还要优先恢复在当前图中连接广、局部冗余低的实体及其关系。

当前实现由四个相互衔接的部分组成：

1. **BNRR 结构评分**：在简单无向投影上，用节点度与邻域内部连边数构造平衡非冗余触达数；
2. **历史锚定的拓扑敏感新颖度（HTSN）**：只用查询前已经存在的图为本轮新元素赋权，避免同一批新节点相互抬高分数；
3. **自适应探索—利用控制**：结合衰减随机探索、HTSN、近期探索成功率和连续失败保护，自动选择查询模式；
4. **TS-PL-FEWA 锚点调度**：先按拓扑先验和查询次数采样候选集，再根据可归因的历史产出在候选集中分配利用预算。

下文以当前代码为规范来源。旧设计中出现但未进入当前实现的语义敏感度、关系类型权重、可学习风险分类器和一般次模效用，不属于这里描述的主方法。

## 2. 问题定义

### 2.1 黑盒抽取过程

设目标 GraphRAG 内部索引对应隐藏图

\[
G^\star=(V^\star,E^\star).
\]

攻击者不能直接读取该图，只能在总查询预算 $B$ 内依次提交查询

\[
q_1,q_2,\ldots,q_B.
\]

第 $t$ 轮响应经解析后形成候选批次

\[
B_t=(\widetilde V_t,\widetilde E_t),
\]

其中一条候选边保留为规范化的有向关系三元组

\[
e=(u,r,v).
\]

累计恢复图记为

\[
G_t=(V_t,E_t)=G_{t-1}\cup B_t,
\qquad G_0=\varnothing.
\]

完全相同的规范化三元组只计一次；同一对端点上的不同关系可以并存。

### 2.2 规范化

实体标签先去除首尾空白、合并连续空白，再转为大写。关系名称合并空白并转为小写；空关系使用 `related_to`。因此在线新颖度比较的是

\[
(\operatorname{norm}(u),\operatorname{norm}(r),\operatorname{norm}(v))
\]

是否已经出现，而不是未经处理的自然语言字符串。

解析器会把关系端点补入候选节点集合。因此即使响应没有单独给出端点实体记录，HTSN 的节点分母仍包含这些端点。

### 2.3 目标与可观测代理

理想目标是在预算内尽早恢复结构影响更大的真实节点和边：

\[
\max_{\pi}\ \mathbb E_{\pi}\!\left[F^\star(G_B\cap G^\star)\right],
\]

其中 $\pi$ 是顺序查询策略，$F^\star$ 是在隐藏真值图上定义的结构敏感质量。黑盒阶段无法计算 $F^\star$，所以 MemATK 用当前恢复图构造在线代理，并用冻结真值图上的 TSC 指标离线验证该代理是否有效。

## 3. 统一对象：固定参考图下的拓扑敏感质量

整个设计围绕一个不变量展开：给定冻结参考图 $R$ 及其节点敏感度 $s_R^V\in[0,1]$，一个节点—边集合 $A=(A_V,A_E)$ 的拓扑敏感质量定义为

\[
F_R(A)
=\sum_{v\in A_V}s_R^V(v)
+\sum_{(u,r,v)\in A_E}s_R^E(u,r,v),
\tag{1}
\]

当前主实现采用

\[
s_R^E(u,r,v)=\max\{s_R^V(u),s_R^V(v)\}.
\tag{2}
\]

式 (1) 在权重冻结后是非负模函数。在线阶段的每轮收益、FEWA 奖励和离线覆盖率都使用这一“敏感质量”概念，只是参考图和可见集合不同：

- 在线 HTSN：参考信息来自 $G_{t-1}$，新节点使用历史锚定扩展；
- RTSN 审计：参考图为并入批次后的 $G_t$；
- 离线 TSC：参考图为完整的 $G^\star$，权重一次计算后冻结。

这一区分避免把部分图上的在线估计误写成真值敏感度。

## 4. BNRR：平衡非冗余触达数

### 4.1 简单无向结构投影

对任意有向多关系图 $R$，构造无自环简单无向投影

\[
U(R)=(V,L).
\]

只要 $R$ 中存在任意方向、任意关系类型的 $u$ 与 $v$ 之间的边，就令 $\{u,v\}\in L$。平行边和反向边在该投影中折叠为一条边，但仍保留在累计恢复图中用于关系三元组新颖度。

对节点 $v$，定义不同邻居数

\[
d_R(v)=|N_R(v)|
\]

以及邻居诱导子图中的边数

\[
T_R(v)=
\left|
\left\{\{x,y\}\in L:x,y\in N_R(v)\right\}
\right|.
\]

### 4.2 碰撞概率与有效多样性

从 $v$ 的 $d=d_R(v)$ 个邻居中有放回地均匀抽取两个邻居。把“抽到同一邻居”或“抽到一对在邻域中直接相连的邻居”视为拓扑冗余碰撞，则有序样本空间大小为 $d^2$，碰撞有序对数量为 $d+2T$。因此实现中的精确碰撞概率为

\[
p_{\mathrm{col},R}(v)
=\frac{d_R(v)+2T_R(v)}{d_R(v)^2},
\qquad d_R(v)>0.
\tag{3}
\]

碰撞有效多样性定义为其倒数：

\[
e_{\mathrm{col},R}(v)
=\frac{d_R(v)^2}{d_R(v)+2T_R(v)}.
\tag{4}
\]

若写成局部聚类系数

\[
C_R(v)=
\begin{cases}
\dfrac{2T_R(v)}{d_R(v)[d_R(v)-1]},&d_R(v)\ge2,\\[6pt]
0,&d_R(v)<2,
\end{cases}
\]

则式 (4) 等价于

\[
e_{\mathrm{col},R}(v)
=\frac{d_R(v)}{1+[d_R(v)-1]C_R(v)}.
\tag{5}
\]

这里的“碰撞”和“冗余”是纯拓扑定义，不是假设邻居文本在统计上独立或相关。

### 4.3 BNRR 定义

仅用有效多样性会把大团中的高度节点压到与叶节点相近。为同时保留总触达规模和非冗余程度，定义二者的无权几何均值：

\[
\operatorname{BNRR}_R(v)
=\sqrt{d_R(v)e_{\mathrm{col},R}(v)}
=\frac{d_R(v)^{3/2}}
{\sqrt{d_R(v)+2T_R(v)}}.
\tag{6}
\]

等价地，

\[
\operatorname{BNRR}_R(v)
=\frac{d_R(v)}
{\sqrt{1+[d_R(v)-1]C_R(v)}}.
\tag{7}
\]

孤立节点的碰撞概率、有效多样性和 BNRR 都定义为 0。

### 4.4 代数性质

以下性质是式 (7) 的直接结果，不依赖 GraphRAG 的生成分布。

当 $d\ge1$ 且 $C\in[0,1]$ 时，

\[
1\le e_{\mathrm{col}}(d,C)
\le \operatorname{BNRR}(d,C)\le d,
\]

并且

\[
\sqrt d\le \operatorname{BNRR}(d,C)\le d.
\tag{8}
\]

固定局部密度时，BNRR 随度严格增加：

\[
\frac{\partial\operatorname{BNRR}}{\partial d}
=\frac{1-C+\tfrac12dC}
{[1+(d-1)C]^{3/2}}>0.
\tag{9}
\]

固定度时，BNRR 随局部密度不增：

\[
\frac{\partial\operatorname{BNRR}}{\partial C}
=-\frac{d(d-1)}
{2[1+(d-1)C]^{3/2}}\le0.
\tag{10}
\]

因此树和星图上 BNRR 退化为度；完全图 $K_n$ 中每个节点的 BNRR 为 $\sqrt{n-1}$。度、邻域边数和式 (6) 都保持图同构不变。

### 4.5 无参数中秩敏感度

令参考图中所有正 BNRR 构成多重集合

\[
\mathcal R_R^+=\{\operatorname{BNRR}_R(u)>0:u\in V(R)\},
\qquad n_R^+=|\mathcal R_R^+|.
\]

非孤立节点的结构敏感度定义为经验中秩分布值

\[
s_R^V(v)=
\frac{
|\{x\in\mathcal R_R^+:x<r_v\}|
+\tfrac12|\{x\in\mathcal R_R^+:x=r_v\}|
}{n_R^+},
\quad r_v=\operatorname{BNRR}_R(v).
\tag{11}
\]

孤立节点及 $n_R^+=0$ 的情况取 0。中秩对并列值给出相同分数，不需要最大度归一化、分位阈值或中心性融合权重。对有限非孤立集合，分数实际位于

\[
\left[\frac{1}{2n_R^+},1-\frac{1}{2n_R^+}\right].
\]

## 5. 历史锚定的新节点评分

### 5.1 动机

本轮新节点不属于 $G_{t-1}$，不能直接使用式 (11)。如果先把整个批次并入图，再让同一批次的新节点和新边相互提供结构证据，单次生成中的幻觉团块可能获得很高分。当前实现采用 historical anchoring：新节点只能通过它与查询前历史图的连接获得在线分数。

### 5.2 到达 BNRR

对新节点 $x\in\widetilde V_t\setminus V_{t-1}$，定义历史锚点集合

\[
A_t(x)=
\left\{u\in V_{t-1}:
(x,r,u)\in\widetilde E_t
\text{ 或 }(u,r,x)\in\widetilde E_t
\right\}.
\]

令

\[
a_t(x)=|A_t(x)|
\]

且 $T_{t-1}^{A}(x)$ 为历史简单投影 $U(G_{t-1})$ 中锚点集合 $A_t(x)$ 内部的边数。到达 BNRR 定义为

\[
r_t^{\mathrm{arr}}(x)=
\begin{cases}
\dfrac{a_t(x)^{3/2}}
{\sqrt{a_t(x)+2T_{t-1}^{A}(x)}},&a_t(x)>0,\\[8pt]
0,&a_t(x)=0.
\end{cases}
\tag{12}
\]

再用历史正 BNRR 的经验中秩 CDF 评价该到达值：

\[
\widetilde s_{t-1}^V(x)=
\frac{
|\{r\in\mathcal R_{t-1}^+:r<r_t^{\mathrm{arr}}(x)\}|
+\tfrac12|\{r\in\mathcal R_{t-1}^+:r=r_t^{\mathrm{arr}}(x)\}|
}{|\mathcal R_{t-1}^+|}.
\tag{13}
\]

若历史正 BNRR 集合为空，式 (13) 取 0。这使第一轮必然是保守冷启动零分；第一轮仍可增加图元素，但不会凭空产生拓扑敏感奖励。

### 5.3 统一端点权重

对本轮候选边端点 $z$，定义

\[
\bar s_{t-1}^V(z)=
\begin{cases}
s_{G_{t-1}}^V(z),&z\in V_{t-1},\\
\widetilde s_{t-1}^V(z),&z\notin V_{t-1}.
\end{cases}
\tag{14}
\]

在线主边权为

\[
\bar s_{t-1}^E(u,r,v)
=\max\{\bar s_{t-1}^V(u),\bar s_{t-1}^V(v)\}.
\tag{15}
\]

实现还记录 Noisy-OR 诊断权重

\[
s_{\mathrm{NO}}^E(u,r,v)
=1-[1-\bar s^V(u)][1-\bar s^V(v)],
\tag{16}
\]

但式 (16) 不参与当前 HTSN、模式控制或 FEWA 奖励。

## 6. HTSN 与可归一化敏感产出

### 6.1 新增集合

令查询前已经存在的规范化关系三元组集合为 $E_{t-1}^{(3)}$。本轮真正新增的元素为

\[
\Delta V_t=\widetilde V_t\setminus V_{t-1},
\qquad
\Delta E_t=\widetilde E_t\setminus E_{t-1}^{(3)}.
\tag{17}
\]

重复候选不进入收益分子，但仍保留在候选数量分母中。

### 6.2 历史锚定敏感产出

定义节点、边和总的历史锚定敏感质量：

\[
Y_{t,V}^{\mathrm{HA}}
=\sum_{v\in\Delta V_t}\widetilde s_{t-1}^V(v),
\tag{18}
\]

\[
Y_{t,E}^{\mathrm{HA}}
=\sum_{e\in\Delta E_t}\bar s_{t-1}^E(e),
\tag{19}
\]

\[
Y_t^{\mathrm{HA}}=Y_{t,V}^{\mathrm{HA}}+Y_{t,E}^{\mathrm{HA}}.
\tag{20}
\]

### 6.3 HTSN

节点和边的历史锚定拓扑敏感新颖度分别为

\[
\operatorname{HTSN}_{t,V}=
\begin{cases}
Y_{t,V}^{\mathrm{HA}}/|\widetilde V_t|,&|\widetilde V_t|>0,\\
0,&\text{otherwise},
\end{cases}
\tag{21}
\]

\[
\operatorname{HTSN}_{t,E}=
\begin{cases}
Y_{t,E}^{\mathrm{HA}}/|\widetilde E_t|,&|\widetilde E_t|>0,\\
0,&\text{otherwise}.
\end{cases}
\tag{22}
\]

控制器使用合并版本

\[
\boxed{
\operatorname{HTSN}_t=
\begin{cases}
\dfrac{Y_t^{\mathrm{HA}}}
{|\widetilde V_t|+|\widetilde E_t|},
&|\widetilde V_t|+|\widetilde E_t|>0,\\[8pt]
0,&\text{otherwise}.
\end{cases}}
\tag{23}
\]

因为每个敏感度都在 $[0,1]$，故

\[
0\le \operatorname{HTSN}_{t,V},
\operatorname{HTSN}_{t,E},
\operatorname{HTSN}_t\le1.
\]

若把所有节点和边权人为设为 1，式 (23) 退化为合并计数新颖度

\[
N_t^{\mathrm{count}}
=\frac{|\Delta V_t|+|\Delta E_t|}
{|\widetilde V_t|+|\widetilde E_t|}.
\tag{24}
\]

这是一种定义层面的退化一致性；自然产生的中秩敏感度并不会全部等于 1。

### 6.4 并图后审计 RTSN

批次并入得到 $G_t$ 后，重新在完整 $G_t$ 上计算节点中秩敏感度，并只对式 (17) 的新增元素求和：

\[
\operatorname{RTSN}_t
=\frac{
\sum_{v\in\Delta V_t}s_{G_t}^V(v)
+\sum_{(u,r,v)\in\Delta E_t}
\max\{s_{G_t}^V(u),s_{G_t}^V(v)\}
}{|\widetilde V_t|+|\widetilde E_t|}.
\tag{25}
\]

报告中的 retrospective gain 为

\[
g_t^{\mathrm{retro}}
=\operatorname{RTSN}_t-\operatorname{HTSN}_t.
\tag{26}
\]

RTSN 会包含本批次内部形成的结构，因此只用于事后审计 historical anchoring 的保守程度，不反馈给在线控制器。

## 7. 自动探索—利用控制

### 7.1 衰减随机探索与自适应阈值

第 $t$ 轮随机探索概率为

\[
\epsilon_t
=\max\{\epsilon_{\min},
\epsilon_0\gamma^{t-1}\}.
\tag{27}
\]

启用自适应阈值时，HTSN 阈值同步衰减：

\[
\tau_t=\tau_0\frac{\epsilon_t}{\epsilon_0}.
\tag{28}
\]

令最近 $k$ 个有效 HTSN 观测的均值为

\[
\overline H_t
=\frac{1}{|\mathcal W_t|}
\sum_{i\in\mathcal W_t}\operatorname{HTSN}_i.
\tag{29}
\]

当查询前没有任何正敏感度锚点时，该轮 HTSN 不进入 $\mathcal W_t$，避免把强制冷启动零分反馈给控制器。

### 7.2 有意义增益与防锁死保护

实现把一轮定义为“有意义”，当且仅当满足至少一个条件：

\[
m_t=
\mathbf 1\left[
|\Delta E_t|>0
\ \lor\
Y_t^{\mathrm{HA}}>0
\right].
\tag{30}
\]

在最近 $W$ 个总轮次内，只取 explore 轮，得到探索成功率

\[
\widehat p_t^{\mathrm{exp}}
=\frac{1}{|\mathcal I_t^{\mathrm{exp}}|}
\sum_{i\in\mathcal I_t^{\mathrm{exp}}}m_i.
\tag{31}
\]

若样本数达到预注册下限且

\[
\widehat p_t^{\mathrm{exp}}<p_{\min},
\tag{32}
\]

则下一轮强制 exploit。若轨迹末尾连续 $L$ 个 explore 轮全部满足 $m_i=0$，也强制 exploit。这两个保护优先于 HTSN 阈值与随机探索，目的是避免低 HTSN 导致“不断 explore、继续得到零增益”的吸收状态。

### 7.3 精确决策顺序

模式控制按下列优先级执行：

1. 第 1 轮固定 explore；
2. 若没有可用锚点，则 explore；
3. 若式 (32) 触发，则 exploit；
4. 若连续失败 explore 上限触发，则 exploit；
5. 若 $\overline H_t<\tau_t$，则 explore；
6. 否则以概率 $\epsilon_t$ explore；
7. 其余情况 exploit。

因此正式方法没有固定 explore/exploit 比例；比例由观测轨迹自动产生。

## 8. TS-PL 候选集构造

### 8.1 合法候选

一次 exploit 的 arm 是当前恢复图中的实体。只有满足以下条件的实体进入候选池：

- 中秩敏感度 $s_t^V(a)>0$；
- 标签长度至少为 2；
- 不是解析器标题、列表标记或 `SUMMARY`、`ENTITY`、`UNKNOWN` 等通用占位词。

### 8.2 拓扑—欠采样权重

在 exploit epoch $e$ 开始时冻结当前敏感度。令 $n_e(a)$ 为此前对 arm $a$ 记录的 exploit 奖励次数，候选权重为

\[
w_e(a)=\frac{s_e^V(a)}{\sqrt{1+n_e(a)}}.
\tag{33}
\]

该式只使用拓扑先验和历史拉取次数，不使用已观测奖励，因此把“进入候选集”和“候选集内基于收益分配预算”分离开来。

### 8.3 有序 Plackett--Luce 无放回采样

令尚未选中的候选集合为 $\mathcal C_{e,j}$。第 $j$ 次抽取 arm $a$ 的条件概率为

\[
\Pr(a_{e,j}=a\mid\mathcal C_{e,j})
=\frac{w_e(a)}
{\sum_{b\in\mathcal C_{e,j}}w_e(b)}.
\tag{34}
\]

选中后从候选池移除，直到得到

\[
K_e=\min\{K,|\mathcal C_e|\}
\tag{35}
\]

个 arm。实现先按规范化字符串排序候选，再用

\[
\operatorname{seed}_e
=\operatorname{seed}_{\mathrm{run}}
+1{,}000{,}003\,e
\tag{36}
\]

初始化独立伪随机数生成器，从而使采样可复现。若总权重非正或非有限，则退化为均匀无放回采样；正常候选因式 (33) 为正，不会触发该分支。

候选集在接下来的

\[
L_e=K_e
\tag{37}
\]

次 **exploit pull** 内冻结。Explore 轮不消耗 epoch 长度。

## 9. FEWA 风格的衰减收益调度

### 9.1 可归因有界奖励

为每轮预注册候选原子上界 $M$。若

\[
|\widetilde V_t|+|\widetilde E_t|>M,
\]

运行立即报错，而不是事后改变归一化尺度。原始批次奖励为

\[
Z_t^{\mathrm{raw}}
=\frac{Y_t^{\mathrm{HA}}}{M}.
\tag{38}
\]

因为每个权重不超过 1，且新增集合是候选集合的子集，所以 $Z_t^{\mathrm{raw}}\in[0,1]$。

对于以 $a_t$ 为锚点的 exploit 查询，只有解析结果包含至少一条与 $a_t$ 相 incident 的候选边时，奖励才归因给该 arm：

\[
Z_t(a_t)
=Z_t^{\mathrm{raw}}
\mathbf 1\left[
\exists e\in\widetilde E_t:\ a_t\in e
\right].
\tag{39}
\]

只在文本中提到锚点或只返回锚点节点都不足以获得奖励。Explore 轮没有 arm 奖励。

### 9.2 冷启动选择

若 epoch 活跃集中存在从未获得过奖励记录的 arm，先选择其中冻结敏感度最高者；并列时按实体字符串排序。这确保新候选至少有机会被观测。

### 9.3 多窗口过滤

其余情况下，令当前活跃集为 $\mathcal A$，arm $a$ 的历史奖励序列为 $Z_{a,1},\ldots,Z_{a,n_a}$。对窗口

\[
h\in\{1,2,4,\ldots\},
\qquad h\le\min_{a\in\mathcal A}n_a,
\]

计算最近窗口均值

\[
\widehat\mu_{a,h}
=\frac1h\sum_{j=n_a-h+1}^{n_a}Z_{a,j}.
\tag{40}
\]

令 $N=\sum_a n_a$ 为全部历史 arm 拉取次数，并在每个过滤窗口使用

\[
c_h=
\sqrt{
\frac{2\log\!\left(
\max\{2,2N|\mathcal A|/\delta\}
\right)}{h}
}.
\tag{41}
\]

保留集合为

\[
\mathcal A\leftarrow
\left\{
a\in\mathcal A:
\widehat\mu_{a,h}
\ge
\max_{b\in\mathcal A}\widehat\mu_{b,h}-2c_h
\right\}.
\tag{42}
\]

窗口依次翻倍，直到窗口超过最小拉取次数或只剩一个 arm。最终从保留集合中依次按下列键选择最小者：

\[
\left(
n_a,
-Z_{a,n_a},
-s_e^V(a),
\operatorname{lex}(a)
\right).
\tag{43}
\]

即优先拉取次数少、最近奖励高、冻结拓扑先验高的 arm，并用字典序保证完全可复现。

FEWA 的适用直觉是同一锚点的边际产出会随重复查询衰减。GraphRAG 响应实际非平稳且带生成随机性，因此当前实现不主张经典 FEWA 遗憾界，而是报告相邻奖励上升比例作为 rotting 假设违背诊断。

## 10. 查询生成、约束与解析

### 10.1 查询生成

第 1 轮使用固定、宽覆盖的 seed query。之后由 LLM 动态生成查询：

- explore 查询结合近期历史和当前新颖度，寻找未覆盖子领域；
- exploit 查询接收控制器已经选定的唯一锚点、已知邻居、最近查询和该锚点的查询轮次；查询生成器不能再次采样其他目标。

对 exploit 查询，领域查询正文必须完整包含规范化锚点短语。固定的抽取格式指令不参与该检查。

### 10.2 防重复约束

移除固定抽取指令后，把查询正文转为小写字母数字 token 集合 $T(q)$。两条查询的相似度为 Jaccard 系数

\[
J(q_i,q_j)=
\frac{|T(q_i)\cap T(q_j)|}
{|T(q_i)\cup T(q_j)|}.
\tag{44}
\]

新查询必须满足

\[
\max_{i<t}J(q_t,q_i)<\eta.
\tag{45}
\]

生成错误、相似度过高或锚点缺失都会触发重试。尝试次数耗尽后，使用包含 turn、子领域或锚点轮次的确定性 diversified fallback；provider 错误不会被静默转换成同一个默认问题。

### 10.3 解析与引用门控

后端复用 AGEA 的实体—关系响应解析器。对模型偶尔输出的单行紧凑关系格式，只接受描述中带有 GraphRAG `Relationships` 数据引用的关系；只带实体引用、来源引用或无引用的紧凑关系会被拒绝。标准多行解析结果和紧凑格式结果随后按规范化三元组去重。

可选 LLM graph filter 可以进一步筛选实体和关系，但正式 medical 配置默认关闭。空主响应直接报错，不作为零增益轮继续执行。

### 10.4 锚点审计

每个 exploit 轮同时记录：

- 查询正文是否包含锚点；
- 响应文本是否包含锚点；
- 候选节点是否包含锚点；
- 候选关系中与锚点相 incident 的边数；
- 式 (39) 的归因奖励是否被置零。

这使“选中了某个 arm”和“响应确实围绕该 arm 返回关系”成为两个可独立检查的事件。

## 11. 完整在线算法

给定预算 $B$、候选上界 $M$ 和随机种子，当前实现逐轮执行：

1. 从 $G_{t-1}$ 计算 BNRR 与中秩敏感度，形成合法 arm 及 TS-PL 先验；
2. 按第 7 节规则自动选择 explore 或 exploit；
3. 若 exploit，则刷新或复用 epoch 候选集，并由 FEWA 选择唯一锚点；若无可用锚点则回退为 explore；
4. 生成满足锚点和相似度约束的动态查询；
5. 调用 GraphRAG local search，并保存主响应和检索上下文；
6. 解析、规范化并在批次内去重实体与关系；
7. 在 $G_{t-1}$ 上计算到达 BNRR、$Y_t^{\mathrm{HA}}$ 与 HTSN；
8. 检查候选原子数不超过 $M$，计算锚点归因奖励；
9. 合并批次得到 $G_t$，计算 RTSN 和冻结真值评测；
10. 更新 FEWA、模式历史和所有审计日志；
11. 覆盖保存最新图、查询历史、控制器状态和逐轮指标。

## 12. 离线评价协议

### 12.1 真值构造

Medical 实验从预建 GraphRAG 的 `entities.parquet` 与 `relationships.parquet` 构造冻结真值图。实体使用同一规范化函数；唯一的括号缩写可以作为保守别名映射。

在线抽取保留关系类型三元组，但当前 GraphRAG 真值表不提供可直接对齐的结构化关系类型，因此真值边评价使用有向端点对

\[
(u,v),
\]

并额外报告无向端点对。不能把在线三元组新颖度与离线端点对 recall 写成同一个边定义。

### 12.2 普通恢复质量

设规范化恢复节点集合为 $\widehat V_t$，恢复有向端点对为 $\widehat E_t^{(2)}$。报告

\[
P_V(t)=\frac{|\widehat V_t\cap V^\star|}{|\widehat V_t|},
\qquad
R_V(t)=\frac{|\widehat V_t\cap V^\star|}{|V^\star|},
\tag{46}
\]

\[
P_E(t)=\frac{|\widehat E_t^{(2)}\cap E^\star|}{|\widehat E_t^{(2)}|},
\qquad
R_E(t)=\frac{|\widehat E_t^{(2)}\cap E^\star|}{|E^\star|}.
\tag{47}
\]

分母为 0 时实现取 0。

### 12.3 拓扑敏感覆盖率

在真值图上一次计算并冻结 $s_\star^V$。节点 TSC 为

\[
\operatorname{TSC}_V(t)=
\frac{
\sum_{v\in\widehat V_t\cap V^\star}s_\star^V(v)
}{
\sum_{v\in V^\star}s_\star^V(v)
}.
\tag{48}
\]

真值边权使用主方法的端点最大值

\[
s_\star^E(u,v)=\max\{s_\star^V(u),s_\star^V(v)\},
\]

从而

\[
\operatorname{TSC}_E(t)=
\frac{
\sum_{e\in\widehat E_t^{(2)}\cap E^\star}s_\star^E(e)
}{
\sum_{e\in E^\star}s_\star^E(e)
}.
\tag{49}
\]

实现同时保存原始 BNRR 权重、Noisy-OR 边权、度、Burt effective size、collision diversity、Burt balanced 和 PageRank 加权覆盖，作为解释与消融诊断；主结果使用中秩 TSC。

### 12.4 预算曲线

对 $B$ 轮轨迹，预算平均 TSC 定义为

\[
\operatorname{AUTSC}_V(B)
=\frac1B\sum_{t=1}^B\operatorname{TSC}_V(t),
\qquad
\operatorname{AUTSC}_E(B)
=\frac1B\sum_{t=1}^B\operatorname{TSC}_E(t).
\tag{50}
\]

同样报告预算平均普通 recall。AUTSC 奖励在较早轮次恢复高结构影响元素，而不只看最终点。

### 12.5 高敏感排序覆盖与在线校准

把真值节点按 $s_\star^V$ 降序排列为 $v_1,\ldots,v_n$，定义

\[
\operatorname{AUTC}(t)
=\frac1n\sum_{k=1}^n
\frac{|\widehat V_t\cap\{v_1,\ldots,v_k\}|}{k}.
\tag{51}
\]

另外在在线图与真值图共同节点上计算 BNRR 和中秩敏感度的 Spearman 相关，并报告 top-$5/10/20/50$ 高敏感真值节点命中数。这些指标用于判断高 TSC 是由在线结构代理引导，还是偶然命中。

## 13. 正式 medical 协议

当前维护的正式协议是 50 次查询、随机种子 42，核心参数为：

| 参数                  |   值 | 作用                             |
| --------------------- | ---: | -------------------------------- |
| $\epsilon_0$          | 0.30 | 初始随机探索概率                 |
| $\gamma$              | 0.98 | epsilon 衰减                     |
| $\epsilon_{\min}$     | 0.05 | 探索概率下限                     |
| $\tau_0$              | 0.15 | 初始 HTSN 阈值                   |
| HTSN 窗口             |    5 | 式 (29) 的观测数                 |
| 探索成功窗口          |   10 | 式 (31) 的最近总轮次数           |
| 最小探索样本          |    2 | 启用低成功率保护的样本数         |
| $p_{\min}$            | 0.20 | 探索成功率阈值                   |
| 连续失败 explore 上限 |    2 | 防锁死保护                       |
| $K$                   |    3 | 每个 epoch 最大 arm 数           |
| $\delta$              | 0.05 | FEWA 过滤置信项                  |
| $M$                   |  512 | 每轮候选原子上界与奖励归一化常数 |
| 查询相似阈值 $\eta$   | 0.85 | 式 (45) 的上限                   |
| 查询生成重试          |    3 | 初次尝试之外的重试次数           |

正式配置以 `configs/extraction/medical/ts_pl_fewa_50turn.yaml` 为准，执行入口为：

```bash
./scripts/run_medical_50turn.sh medical_ts_pl_fewa_50turn_seed42
```

协议还要求查询唯一率不低于 90%、零图增益轮次比例不高于 20%、连续零图增益和连续零有意义增益都不超过 4、exploit 查询锚点遵从率为 100%、seed 后同时出现 explore 与 exploit、所有主响应非空。这些是运行健康与协议验收条件，不是 BNRR 或 HTSN 的数学定义。

## 14. 产物与可审计性

每个完整运行保存在 `artifacts/runs/mematk/<run-id>/`，包括：

- `config.json`：实际运行配置；
- `query_history.json`：模式、锚点、查询与生成来源；
- `controller_state.json`：TS-PL 抽样、epoch 和 FEWA 窗口；
- `turn_metrics.json` 与 `turn_metrics.csv`：逐轮在线、奖励和真值指标；
- `extracted_graph.json` 与 `extracted_graph.graphml`：累计恢复图；
- `turn_logs/llm_responses/`：主响应；
- `turn_logs/retrieved_contexts/`：GraphRAG 检索上下文；
- `summary.json` 与 `EXPERIMENT_RESULTS.md`：聚合指标和人类可读报告。

运行目录非空时程序拒绝覆盖，防止不同实验轨迹混写。论文可审计的小型快照位于 `results/medical/`。

## 15. 复杂度与实现边界

当前实现每轮完整重算简单投影、每个节点的邻居诱导子图边数和中秩排序，并为 RTSN 再计算一次并图后的分数。若记简单投影为 $U_t=(V_t,L_t)$，主要成本包括：

\[
O(|V_t|+|L_t|)
\]

的投影构造、所有邻居诱导子图计边的累计成本，以及

\[
O(|V_t|\log|V_t|)
\]

的 BNRR 排序。当前版本优先保证定义清晰和逐轮可复算，没有实现增量三角形维护。

实现边界如下：

1. 只支持 medical GraphRAG 的正式入口，且在线检索上下文捕获只支持 local search；
2. BNRR 是结构安全优先级，不是真实隐私、医学严重度或语义敏感度；
3. 简单无向投影忽略方向、关系类型和平行关系数量；
4. historical anchoring 忽略同批新节点之间的在线贡献，可能低估真正的新社区，但能抑制批次自信用；
5. 三角形密度无法识别完全二部图中的四环冗余；
6. 公共高连接概念可能获得高分，低度但语义极敏感的实体可能被低估；
7. 部分图会低估尚未恢复的邻域边，从而改变 BNRR 排序；
8. 端点最大值只表达“关系涉及至少一个高结构敏感节点”，不表达关系语义风险；
9. LLM 解析错误和重复幻觉仍可能污染累计图，必须联合报告 precision；
10. FEWA 的衰减收益假设只做经验诊断，当前结果不支持理论遗憾保证；
11. 单个 seed 的 50-turn 结果只能说明该轨迹有效，不能替代多 seed 置信区间；
12. 当前方法评价的是抽取与优先级，不包含模糊替换、防御效用或正常问答质量实验。

## 16. 可支持的研究主张

在当前实现和指标下，可以检验的主张是：

> 相比仅按数量新颖度和简单频率选择锚点，MemATK 使用 BNRR 构造无训练的结构优先级，以 historical anchoring 衡量单位候选的新增结构敏感质量，并通过自适应模式控制与 TS-PL-FEWA 在覆盖新区域和重复开发高产锚点之间分配预算。该方法的效果应由普通 precision/recall、TSC/AUTSC、锚点归因和多 seed 轨迹共同验证。

当前不应声称：

- BNRR 等于法律或医学意义上的敏感度；
- HTSN 是隐藏图真实边际效用的无偏估计；
- TS-PL-FEWA 对非平稳 LLM 响应具有已证明的最优性或遗憾界；
- 单一 medical 数据集和单个随机种子可以证明跨域泛化；
- 高结构覆盖必然转化为有效且低损的防御策略。

## 17. 代码对应关系

- `src/extraction/models.py`：规范化关系原子与候选批次；
- `src/extraction/metrics/graph.py`：投影、BNRR、中秩、historical anchoring、HTSN 与 RTSN；
- `src/extraction/control/admission.py`：合法 arm 与 TS-PL 采样；
- `src/extraction/control/controllers.py`：自动模式控制、epoch-frozen FEWA 与 rotting 诊断；
- `src/extraction/backends/graphrag.py`：动态查询、GraphRAG local search、解析和引用门控；
- `src/extraction/pipeline.py`：完整顺序流程、奖励归因、验收与产物保存；
- `src/evaluation/graph_recovery.py`：冻结真值上的 precision、recall、TSC、AUTSC、AUTC 和 Spearman；
- `configs/extraction/medical/ts_pl_fewa_50turn.yaml`：正式实验参数。

## 18. 术语表

| 缩写  | 全称                                                | 当前实现中的含义                       |
| ----- | --------------------------------------------------- | -------------------------------------- |
| BNRR  | Balanced Non-Redundant Reach                        | 度与碰撞有效多样性的几何均值           |
| HTSN  | Historically Anchored Topological Sensitive Novelty | 查询前历史图锚定的单位候选敏感新增质量 |
| RTSN  | Retrospective Topological Sensitive Novelty         | 并图后重评分得到的审计指标             |
| TS-PL | Topology-Sensitive Plackett--Luce                   | 基于敏感度与欠采样修正的无放回候选采样 |
| FEWA  | Filtering on Expanding Window Averages              | 用指数增长最近窗口过滤衰减收益 arm     |
| TSC   | Topology-Sensitive Coverage                         | 冻结真值拓扑权重下的累计覆盖率         |
| AUTSC | Area Under the TSC trajectory                       | 查询预算上的平均 TSC                   |
| AUTC  | Area Under the Top-$k$ Coverage curve               | 对所有真值 top-$k$ 宽度平均的命中率    |
