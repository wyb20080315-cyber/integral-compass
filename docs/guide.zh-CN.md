# 0.4 中文指南

## 现在怎样返回

```python
from integral_compass import integrate, analyze

print(integrate("x*exp(x)", 2))  # 成功：返回 (x-1)*exp(x)，默认打印步骤
print(integrate("x*exp(x)", 1))  # Python 的 None：限深搜索耗尽
print(integrate("exp(-x**2)"))   # 字符串 "None, verified by Risch"
print(integrate("Abs(x)", 1))   # unknown, unsupported rule: 后接解释
```

只有 Risch 确实证明无初等原函数时，才返回那个证书字符串。
没有填写深度但求解成功时，仍返回原函数；无法判定时，返回带原因的 unknown。
Python None 和字符串 "None, verified by Risch" 是不同类型，不要混用。

| 返回 | 含义 |
| --- | --- |
| 原函数表达式 | 找到解并通过求导验证，省略 C |
| Python None | 设定深度内生成的路线都检查完，没有成功 |
| "None, verified by Risch" | Risch 后端证明无初等原函数；不表示没有任何原函数或不能数值积分 |
| "unknown, timeout: ..." | 时间用完，计算未结束 |
| "unknown, unsupported rule: ..." | 当前表达式需要本版没有实现的规则 |
| "unknown, unresolved branches: ..." | 搜索已经展开，但仍有方向无法评估 |
| "unknown, backend error: ..." | 工作进程故障或返回了无效结果 |
| "unknown, verification failed: ..." | 候选答案未通过检查，不作为答案返回 |

## 规则不支持和分支未决有什么区别

**规则不支持：`Abs(x)`。** 它是绝对值函数，数学上有原函数，例如 x*Abs(x)/2。
但本版尚未实现相应的分段/绝对值规则，所以在输入节点就能明确说明这个限制。

**分支未决：`log(x)**2`，深度 2。** 按两个方向探索：

1. 对 log(x)**2 求导，对 1 积分，余项为 2*log(x)。它到第 2 层，不能继续展开。
2. 对 1 求导，对 log(x)**2 积分。要先拿到 v，但当前基本积分表不能直接提供 v。

第二条路线并没有完成判断，因此不能说“全部路线失败”而返回 None。
把深度设为 3，第一条路线可继续做分部积分，最后得到：

```text
x*(log(x)**2 - 2*log(x) + 2)
```

两种解释有关联：未决分支也可能源于某个子步骤缺少规则。
前者指出当前表达式的直接能力边界，后者指出搜索树仍有未能评估的方向。

## 深度和时间

原式是第 1 层，每做一次分部积分，余项进入下一层。
填深度时只用课堂规则，不让 Risch 绕过层数限制。
不填深度时自动结合 Risch 和无固定层数上限的搜索，总时间默认 10 秒。
Risch 预判最多用 30% 时间，剩余时间用于课堂搜索；已验证的 Risch 解可作为后备。
`timeout=30` 只把总时间改为 30 秒，不会关闭 Risch。

## 展示类和循环方程

```python
from integral_compass import IntegralSolver
problem = IntegralSolver("exp(x)*sin(x)", 3)
answer = problem.solve()
problem.show_tree()
```

如果余项与子问题原式相同或相差常数倍，程序建立关于原积分 J 的方程。
保留系数与减号后，例如 J=exp(x)*(sin(x)-cos(x))-J，可解出 J。
J=J 一类退化关系不能作为答案。所有候选原函数都需通过求导检查。

`.analyze()` 静默计算，`.solve()` 返回值且成功时打印实际步骤，`.show()` 显示结果，
`.show_tree()` 显示已探索分支；同一问题会缓存结果。
想关闭自动输出，用 `show_steps=False`。

## 稳定地检查原因

```python
r = analyze("log(x)**2", 2)
print(r.status)       # unknown
print(r.reason_code)  # unresolved_branch
print(r.reason)       # 具体是哪一个方向未完成
print(r.value)        # 与 integrate() 的返回值一致
print(r.to_dict())    # 也包含 value 和 reason_code
```

不要只检查 antiderivative 是否为 None；失败时它都是空的，应查看 status 或 value。
非法输入会抛异常，例如 1/0、深度 0、时间 0，不伪装成数学上的 unknown。
兼容模块 integral_compass.classic 继续保留旧版 Python None/异常语义。

## 当前范围

单变量表达式，乘法写 *，乘方写 **，自然对数写 log，不接受任意 Python 函数代码。
支持基本公式、DI、部分分式与循环方程；多因子分组最多八个规范化因子，
有理函数终点次数上限为 30。Risch 后端也不覆盖全部表达式，所以默认模式仍可能 unknown。
结果在避开奇点与分支边界的局部区间成立，不自动求完整定义域。

Windows 操作见 [本机指南](windows.zh-CN.md)，最小失败案例和一分钟安排见
[演讲资料](presentation.zh-CN.md)。PyPI 仍按项目所有者要求暂缓发布。
