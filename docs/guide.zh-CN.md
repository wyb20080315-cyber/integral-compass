# 0.2 中文指南

## 先看最小例子

```python
from integral_compass import integrate, IntegralSolver

print(integrate("x**2*exp(x)", 2))  # None：深度不够
print(integrate("x**2*exp(x)", 3))  # 自动显示步骤，再返回原函数
print(integrate("Abs(x)", 3))      # 字符串 unknown
```

第二个参数就是深度。默认是 None，不限制搜索层数；不是没有时间限制。
默认总计算时限为 10 秒，超时返回 unknown，可用 `timeout=30` 增大时限。
Python 表达式里乘法写 `*`，乘方写 `**`，自然对数写 `log`。

## 深度怎么算

原式是第 1 层。对 `f*g` 做一次选择，有两个方向：

1. 对 f 求导，对 g 积分。
2. 对 g 求导，对 f 积分。

使用 `∫u dv = uv - ∫v du`，剩下的积分是第 2 层。
再对各自的余项做一次选择，进入第 3 层。若所有分支都能评估、没有提前成功，
两因子示例在第 3 层有四个叶子。程序不会把四个分支的系数都当成 1；
每条路都会保留公式中的乘数和减号。

例如 `x**3*exp(x)`：深度 3 的两条第一层方向会形成四个第三层叶子，
均未结束，返回 None；深度 4 则能沿多项式逐次求导的路径成功。

## 什么时候返回什么

| 返回值 | 含义 |
| --- | --- |
| SymPy 原函数表达式 | 找到解，且求导验证通过；表达式省略 C |
| None | 指定深度内生成的所有分支都检查完，但未找到解 |
| 字符串 unknown | 某分支无法评估、循环无法处理、结果验证失败、后端异常或超时 |

None 只和这次搜索的深度、规则有关。它不说明“数学上没有初等原函数”。
一个分支 unknown 时，程序仍会尝试另一个方向；只要有一个方向成功，就返回解。
没有任何方向成功且仍有未判定分支，才返回 unknown。

## 用类展示解题过程

```python
from integral_compass import IntegralSolver

problem = IntegralSolver("log(x)/(x+1)**2", 2)
answer = problem.solve()
problem.show_tree()
print(answer)
print(problem.result.verified)
```

这个例子会真的用到两种方法：令 `u=log(x)`、`dv=1/(x+1)**2 dx`，
得到 `v=-1/(x+1)`、`du=1/x dx`。余项为 `-1/(x*(x+1))`，
用部分分式拆成 `1/(x+1)-1/x` 后积分，再按公式组合回来。
成功时，程序打印 DI 的 D/I 选择、被积那一边的原函数、余项、部分分式、
逐项积分和最后的求导验证。没有实际用到某种方法时，不会编造对应步骤。

`problem.analyze()` 只计算，不打印；`problem.show()` 显示结果。
同一对象会缓存结果，重复显示不需要重新积分；更改深度等设置后会重新计算。
直接调用函数也默认打印成功步骤。想关闭输出，可以写：

```python
from integral_compass import integrate, analyze
F = integrate("x**2*exp(x)", 3, show_steps=False)
r = analyze("x**2*exp(x)", 2)
print(r.status)           # exhausted
print(r.search_complete)  # True
print(r.to_dict())        # 包括搜索树，可用于自己做展示
```

## 搜索规则的边界

分部积分必须先拿到被积那一边的原函数 v。第一版搜索使用显式基本公式和
有理函数规则求 v；拿不到时该方向为 unknown，不会调用通用积分器绕过深度限制。

终点规则包括多项式、部分分式、线性内函数的 exp/sin/cos，以及一次式的有理数幂。
因此简单指数积分可以直接结束，不需要硬变成部分分式。
多个加法项按线性拆分，不额外消耗分部积分层数。

两个因子试两个方向；多因子则枚举原表达式的因子分组及两个方向，最多八个因子。
这里“所有可能性”指这个明确的、有限的拆分规则，不包含任意换元或任意恒等变形。
SymPy 会规范化输入，程序处理的是规范化后的因子，不是原始字符串的排版。

默认无限深采用逐层加深搜索，避免一直陷在第一条路而错过另一条路。
遇到未实现的循环积分方程时返回 unknown；没有隐藏的固定层数上限，但仍受时限和机器资源限制。
绝对值/分段积分、有理函数次数超过 30、超出输出语言的代数根表示等也可能 unknown。

## 旧版 Risch 判定

旧版保留在独立模块，避免两种 None 混用：

```python
from integral_compass.classic import integrate as classic_integrate
assert classic_integrate("exp(-x**2)") is None
```

这里的 None 才代表后端证明不存在初等原函数。旧版未知情况抛出
IntegrationUndeterminedError，不返回字符串。新版第二参数改为深度后，
自定义变量请写关键字：`integrate(expr, 3, variable=t)`。

## 安装和动手测试

Windows 安装步骤见 [本机操作指南](windows.zh-CN.md)。仓库或源码解压后可运行：

```bash
python -m pip install .
python examples/minimal_case.py
```

Python 包是安装到某一个解释器中的；运行脚本要使用同一个解释器。
本项目暂未发布到 PyPI，不要直接用包名从索引安装。
