# 中文使用指南

## 项目动机与贡献

本项目来自个人微积分笔记中的问题：能不能把课堂上的积分步骤变成程序，并且分辨
“没有初等原函数”和“程序不会算”？目标用户是正在学习换元、分部积分和部分分式的学生。

项目贡献是可解释的课堂策略、DI 表格、部分分式步骤、求导验证和严格的三状态接口。
底层代数运算与 Risch 后端依赖 SymPy。我们没有从零实现完整 Risch，也不声称发明新的积分算法。
Risch 是扩展能力，团队答辩的重点可以放在课堂方法和返回值语义。

## 安装与环境

需要 Python 3.10+。源码安装流程见仓库 README。开发者在虚拟环境内运行：

```bash
python -m pip install -e '.[dev]'
python -m pytest
```

PyPI 发布完成后可运行 `python -m pip install integral-compass`。
在未发布或账号绑定未完成时，使用源码安装即可完整运行，不必等待 PyPI。

## 基础接口

```python
from integral_compass import analyze, integrate, IntegrationUndeterminedError

r = analyze("x**2 * exp(x)")
print(r.status)          # elementary
print(r.method)          # di
print(r.antiderivative)  # (x**2 - 2*x + 2)*exp(x)
print(r.verified)        # True
print(r.explain())       # 表格、步骤、验证结果
print(r.to_dict())       # 可序列化的结构化结果

answer = integrate("x**2 * exp(x)")  # 直接取原函数，不附加 C
assert integrate("exp(-x**2)") is None

try:
    integrate("Abs(x)")
except IntegrationUndeterminedError as exc:
    print(exc.result.reason)
```

默认变量是实数 `x`。自定义变量：

```python
import sympy as sp
from integral_compass import integrate

t = sp.Symbol("t", positive=True)
F = integrate(t**2 * sp.exp(t), t)  # 将同一个 Symbol 传入以保留假设
print(sp.simplify(sp.diff(F, t) - t**2 * sp.exp(t)))  # 0
```

## 案例一：DI 表格

输入 `x**2 * exp(x)`。将多项式反复求导到零，对指数反复积分：

| 符号 | D（求导） | I（积分） |
| --- | --- | --- |
| + | x² | exp(x) |
| − | 2x | exp(x) |
| + | 2 | exp(x) |
| 停止 | 0 | 余项消失 |

得到 `(x**2 - 2*x + 2)*exp(x) + C`。算法也处理线性内函数的斜率，
例如 `x**2*sin(3*x+2)`，每次积分都包含对应的 `1/3` 因子。
第一版不处理所有可能的 DI 循环情形。

## 案例二：重复二次因子的部分分式

```python
print(analyze("1/((x+1)*(x**2+1)**2)").explain())
```

先检查是否需要多项式长除法，然后分解：

```text
1/(4*(x+1)) - (x-1)/(4*(x**2+1)) - (x-1)/(2*(x**2+1)**2)
```

对应笔记里的规则：一次因子上放常数；不可约二次因子上放一次式；
重复因子必须包含从一次到最高次的全部分母幂。拆分和每项积分由 SymPy 提供，
项目负责调度、展示、实数对数形式和最终验证。

## 案例三：无初等原函数

`exp(-x**2)` 没有初等函数形式的原函数，但有用特殊函数 erf 表示的原函数，
也可以计算定积分或数值积分。这里 `None` 只表示前一种限制。

Risch 后端目前主要支持指数、对数构成的超越表达式，不能对所有输入作出判断。
若一个未求值积分来自通用积分器，不能据此返回 `None`。

## 命令行与失败处理

```bash
integral-compass 'x**2 * exp(x)'
integral-compass '1/(x*(x+1))' --json
integral-compass 't*cos(t)' --variable t
integral-compass 'exp(-x**2)' --timeout 10
```

CLI 退出码：0 表示已判定（有初等解或已证明无初等解）；2 表示输入错误；3 表示 unknown。
`analyze()` 遇到超时、后端失败或无法验证时返回 unknown；输入不合法则抛出 `ExpressionError`。
`integrate()` 对 unknown 抛出 `IntegrationUndeterminedError`，不能把它吞掉改成 `None`。

## 使用边界

使用 `*` 写乘法、`**` 写乘方，`log` 表示自然对数。只支持一个变量，不接受
含额外参数的式子、用户自定义函数或任意 Python callable。字符串最多 2000 字符、
200 个 AST 节点，数值指数范围 −100 到 100。结果不附加积分常数 C。

默认实变量下，有理函数的实对数写为 `log(Abs(...))`。结果在避开零点、极点和分支边界的
局部区间成立，不自动给出完整定义域。分段原函数、数值积分和定积分不属于本版范围。
复杂表达式超时仍可使用更长的 `timeout` 重试，但更长时间不保证一定得到结论。
