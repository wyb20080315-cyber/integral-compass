# 0.3 中文指南：先分清 None 和 unknown

## 两种模式，只看是否填写深度

| 调用 | 模式 |
| --- | --- |
| `integrate(f, 3)` | 最多搜到第 3 层，不用 Risch 绕过层数限制 |
| `integrate(f)` | 无固定深度上限，自动结合 Risch 和课堂搜索 |
| `integrate(f, timeout=30)` | 同样自动结合 Risch，时间总预算改成 30 秒 |

时间不填时，总预算默认为 10 秒。无限深指没有固定层数上限，不指无限运行时间。
自动模式先给 Risch 30% 的时间；它证明无初等解时直接结束，否则剩余时间给课堂搜索。
课堂搜索成功就展示步骤；若它失败但 Risch 已提供可验证的原函数，就使用该原函数并标明来源。

## 返回值到底是什么意思

| 返回值 | 详细状态 | 解释 |
| --- | --- | --- |
| 原函数表达式 | elementary | 有答案，且求导验证通过 |
| None | exhausted | 填写了深度，这个深度内的生成路线全部检查完，仍没有解 |
| None | non_elementary | 没有限制深度，Risch 后端证明没有初等原函数 |
| 字符串 unknown | unknown | 程序还没判断出来，可能超时、规则不支持或有未评估分支 |

两个 None 用 `analyze(...).status` 区分。None/exhausted 是相对于这次搜索的结论；
None/non_elementary 才是数学上的无初等原函数判定。它仍不表示没有任何原函数或不能数值积分。
unknown 不表示“不存在答案”，只表示程序目前不能给出结论。

```python
from integral_compass import integrate, analyze

print(integrate("x**2*exp(x)", 2))  # None，深度内没有找到
print(analyze("x**2*exp(x)", 2).status)  # exhausted
print(integrate("x**2*exp(x)", 3))  # 成功，自动打印步骤

print(integrate("exp(-x**2)"))  # None，Risch 证明没有初等原函数
print(analyze("exp(-x**2)").status)  # non_elementary
print(integrate("Abs(x)"))  # unknown
```

## 层数怎么数

原式为第 1 层。对 `f*g` 有两个分部积分方向：对 f 求导、对 g 积分；或者交换。
使用 `∫u dv=uv-∫v du`，余项进入下一层。常数系数和减号都会保留。
`x**2*exp(x)` 需要到第 3 层；`x**3*exp(x)` 通常需要第 4 层。
终点规则可以在边界层直接完成；循环判断也发生在边界检查之前。

## 循环方程

```python
from integral_compass import IntegralSolver
problem = IntegralSolver("exp(x)*sin(x)", 3)
answer = problem.solve()
problem.show_tree()
```

令原积分为 J。连续分部积分后：

```text
J = exp(x)*(sin(x)-cos(x)) - J
2*J = exp(x)*(sin(x)-cos(x))
J = exp(x)*(sin(x)-cos(x))/2
```

程序判断余项是否与这个子问题的原始被积函数相同或相差常数倍。
它保存整条路径的关系 `J=A+B*当前积分`，从而保留系数与减号。
遇到 `当前函数=k*原始函数` 时，解 `(1-B*k)*J=A`，最后对答案求导验证。
`J=J` 一类退化关系不能解出 J，程序会尝试其他路线。加法拆分后的各项分别建方程。

## DI 如何接上部分分式

```python
IntegralSolver("log(x)/(x+1)**2", 2).solve()
```

令 u=log(x)、dv=1/(x+1)**2 dx，得到 v=-1/(x+1)、du=1/x dx。
余项为 `-1/(x*(x+1))`，可拆成 `1/(x+1)-1/x`，逐项积分后组合回来。
成功展示包括实际使用的 D/I、常数乘数、余项、部分分式、逐项积分及导数检查。
没有用到某方法时不会编造步骤。

`problem.analyze()` 静默计算；`.solve()` 返回表达式/None/unknown，成功时打印；
`.show()` 展示结果，`.show_tree()` 展示尝试过的分支。同一问题会缓存结果。
函数版本可设置 `show_steps=False` 关闭成功输出。

## 仍有哪些边界

只接受规定语言中的单变量表达式。`*` 是乘法，`**` 是乘方，`log` 是自然对数。
分部积分之前必须用基本公式或有理函数规则拿到 v；拿不到的方向仍为 unknown。
有限深度只使用课堂规则，不调用通用积分器直接跳过深度限制。

多因子枚举最多八个规范化因子的分组及两个方向，不包括所有可能的换元或恒等变形。
有理函数终点次数上限为 30。分段/绝对值积分、无法处理的循环或代数根表示可能 unknown。
Risch 实现也有覆盖限制，因此默认模式仍可能 unknown。

原函数省略 C；答案在避开奇点与分支边界的局部区间成立，不自动求完整定义域。
旧版接口保留在 `integral_compass.classic`，unknown 时仍抛出 IntegrationUndeterminedError。

Windows 安装和导入见 [本机指南](windows.zh-CN.md)。PyPI 继续暂缓发布。
