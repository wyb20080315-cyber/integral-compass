---
title: "Integral Compass 中文使用说明书"
lang: zh-CN
---

# Integral Compass 中文使用说明书

**软件版本：0.4.0｜说明书版本：1.0｜更新日期：2026 年 11 月 15 日**

本说明书面向首次使用本包、准备课堂演示或需要了解内部原理的同学。

| 项目入口 | 链接 |
| --- | --- |
| 公开 Git 仓库 | [GitHub 仓库](https://github.com/wyb20080315-cyber/integral-compass) |
| 已发布 Python 包 | [PyPI 0.4.0](https://pypi.org/project/integral-compass/0.4.0/) |
| 完整文档入口 | [项目文档](https://github.com/wyb20080315-cyber/integral-compass/blob/main/docs/README.md) |

## 1. 这个包可以做什么

Integral Compass 是面向微积分学习的 Python 符号积分工具。输入单变量数学表达式，
程序按照已有规则寻找初等原函数，返回答案或明确说明为什么没有得到答案。

主要功能：

- 尝试分部积分的两个方向，并允许限制搜索深度。
- 对有理函数进行多项式除法、部分分式拆分和逐项积分。
- 检测余项与原式的循环关系，建立并求解关于原积分的一次方程。
- 无深度限制时，自动结合 SymPy 的 Risch 后端与课堂方法搜索。
- 成功时展示实际求解步骤，并对原函数求导验证。
- 提供函数接口、展示类、结构化结果、搜索树以及命令行。

本包计算的是**不定积分的初等函数表示**。它不保证处理任意函数，不提供本版范围外的
定积分、数值积分和完整定义域分析。输入是表达式字符串或 SymPy 表达式，不是任意 Python 函数代码。

## 2. 安装与第一次运行

### 2.1 环境要求

Python 3.10 或以上。本项目已在 Linux Python 3.10–3.13、Windows Python 3.12 上进行 CI 检查。
依赖 SymPy 1.13/1.14；正常通过 pip 安装会自动安装相应依赖。

Windows 用户可使用 Python 3.13。安装后在 PowerShell 中确认：

```powershell
py -3.13 --version
```

### 2.2 安装发布版本

在准备保存测试脚本的文件夹打开 PowerShell，依次运行：

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\python.exe -m pip install integral-compass==0.4.0
.\.venv\Scripts\python.exe -c "import integral_compass; print(integral_compass.__version__)"
```

最后应显示 `0.4.0`。这些命令直接使用虚拟环境中的解释器，不需要激活环境。

Linux/macOS 可在相应 Python 虚拟环境中使用：

```bash
python -m pip install integral-compass==0.4.0
```

### 2.3 自己写第一个脚本

新建 `my_test.py`，写入：

```python
from integral_compass import integrate

print(integrate("x*exp(x)", 2))
print(integrate("x*exp(x)", 1))
print(integrate("exp(-x**2)"))
```

运行：

```powershell
.\.venv\Scripts\python.exe .\my_test.py
```

第一例自动打印步骤并返回 `(x - 1)*exp(x)`；第二例返回 Python 的 `None`；
第三例返回字符串 `None, verified by Risch`。表达式省略积分常数 C，展示文字会附加 C。
脚本不要命名为 `integral_compass.py` 或 `sympy.py`，以免遮住真正安装的包。

## 3. 函数、参数和输入写法

### 3.1 基本接口

```python
integrate(expression, depth=None, *, variable="x", timeout=None, show_steps=True)
```

| 参数 | 含义 |
| --- | --- |
| expression | 必填；表达式字符串或 SymPy 表达式 |
| depth | 第二个参数；正的 Python int 或 None，默认不设固定层数上限 |
| variable | 默认积分变量为实数 x；自定义变量须使用关键字 |
| timeout | 总计算时限，单位秒；不填时默认为 10 秒 |
| show_steps | 默认 True；成功时自动打印实际步骤，False 则静默返回 |

示例：

```python
F = integrate("x*exp(x)", 2, show_steps=False)
F = integrate("x*exp(x)", timeout=30)
F = integrate("t*cos(t)", 2, variable="t")
```

如果传入已有的 SymPy 表达式，请用 `variable=` 传入该表达式自己的 Symbol，以保留假设。

### 3.2 表达式写法

| 数学意思 | 输入写法 |
| --- | --- |
| x 的平方 | `x**2` |
| x 乘指数函数 | `x*exp(x)` |
| 自然对数 | `log(x)` |
| 平方根 | `sqrt(x)` |
| 分式 | `1/(x*(x+1))` |

运算符支持 `+ - * / **`，不要用 `^` 表示乘方，也不要省略乘号。
可识别函数包括 sin、cos、tan、cot、sec、csc、asin、acos、atan、exp、log、sqrt、Abs；
常数包括 pi、E、I。**能识别写法不等于一定存在对应的求解规则。**
字符串最多 2000 字符、200 个语法节点；数值指数在 −100 到 100 之间。
不支持额外自由参数，例如默认情况下 `a*x` 会被拒绝。

## 4. 深度与时间怎样计算

**原式为第 1 层，每做一次分部积分，余项进入下一层。**
加法按线性分解，不额外消耗分部积分层数；终点规则可在边界层直接结束。

以 `x*exp(x)` 为例：

| 层数 | 待处理对象 | 操作 |
| --- | --- | --- |
| 1 | x*exp(x) | 对 x 求导，对 exp(x) 积分 |
| 2 | exp(x) | 基本公式直接积分 |

所以深度 1 返回 None，深度 2 能成功。`x**2*exp(x)` 通常需要第 3 层。

- **填了 depth：** 只在规定层数内使用课堂规则，不用 Risch 绕过限制。
- **depth 为 None：** 自动结合 Risch 与无固定层数上限的搜索。逐层加深，避免一直困在第一个方向。
- **时间不填：** 总预算默认 10 秒。自动模式给 Risch 最多 30%，剩余时间用于课堂搜索。
- **时间填了：** 如 `timeout=30`，改变总时间预算，不会关闭无深度限制时的 Risch。

“无限深”不等于无限运行时间。超时返回带解释的 unknown。
如果课堂搜索失败，但 Risch 已给出验证通过的原函数，自动模式可以使用该后备答案，并标明来源。

## 5. 怎样理解返回值

| 返回值 | 详细状态 | 含义 |
| --- | --- | --- |
| SymPy 原函数表达式 | elementary | 找到答案且求导验证通过 |
| Python None | exhausted | 指定深度内生成的路线全部检查完，没有成功 |
| 字符串 "None, verified by Risch" | non_elementary | Risch 后端证明不存在初等原函数 |
| 以 "unknown, " 开头的字符串 | unknown | 当前程序还不能作出结论，消息中包含原因 |

Python `None` 和字符串 `"None, verified by Risch"` 是不同类型。
Risch 的结论只涉及初等函数表示；例如 exp(-x**2) 仍有用 erf 表示的原函数，也可以数值积分。

### 5.1 五个真实的非成功结果

```python
from integral_compass import integrate

integrate("x*exp(x)", 1)
# None

integrate("exp(-x**2)")
# "None, verified by Risch"

integrate("x", 1, timeout=0.000001)
# "unknown, timeout: ..."

integrate("Abs(x)", 1)
# "unknown, unsupported rule: ..."

integrate("log(x)**2", 2)
# "unknown, unresolved branches: ..."
```

省略号表示返回值中实际存在的具体解释。超时例子刻意把时限设得比进程启动还短，
不表示 x 本身难以积分。

### 5.2 规则不支持与分支未决

**规则不支持：Abs(x)。** 数学上有原函数 x*Abs(x)/2，但本版尚未实现绝对值/分段积分规则。
因此程序直接报告当前能力限制。

**分支未决：`log(x)**2`，深度 2。** 将它看作 log(x)**2 乘 1：

1. 对 log(x)**2 求导、对 1 积分，余项为 2*log(x)，到了第 2 层，还需继续分部积分。
2. 对 1 求导、对 log(x)**2 积分，需要先拿到后者原函数 v，当前基本积分表无法直接提供。

第二条没有完成评估，因此不能声称所有路线都失败。改为深度 3，第一条可以继续成功：

```text
x*(log(x)**2 - 2*log(x) + 2)
```

两种原因有关联：一个未决方向，也可能卡在某个子步骤缺少规则。
前者描述当前表达式的能力边界，后者描述搜索树中仍有未能评估的方向。

### 5.3 其它失败与输入错误

工作进程出错或返回无效数据时，返回 `unknown, backend error: ...`。
候选答案未通过导数或输出检查时，返回 `unknown, verification failed: ...`。
两者都不能当作无初等原函数的证据。

非法表达式会抛出 `ExpressionError`；非法深度或时间会抛出 `ValueError`。
例如 `1/0`、深度 0、时间 0 属于输入错误，不伪装成 unknown。
软件故障的演示见 failure_cases.py 的 `--internal` 模式，明确标为模拟。

## 6. 用类展示步骤与搜索树

```python
from integral_compass import IntegralSolver

problem = IntegralSolver("log(x)/(x+1)**2", 2)
answer = problem.solve()
problem.show_tree()
print(problem.result.verified)
```

这个例子先选 u=log(x)、dv=1/(x+1)**2 dx。得到 v=−1/(x+1)、du=1/x dx。
余项 −1/(x*(x+1)) 可拆为 1/(x+1)−1/x，再逐项积分并代回公式。
展示包含实际 D/I 选择、系数、余项、部分分式、逐项积分、组合答案及导数验证。
没有用到的方法不会被编造成步骤。

| 方法或属性 | 用途 |
| --- | --- |
| problem.solve() | 计算并返回值，成功时默认打印步骤 |
| problem.analyze() | 静默返回结构化结果 |
| problem.show() | 展示结果与失败解释 |
| problem.show_tree() | 显示已探索的最终一轮搜索树 |
| problem.result | 首次计算前为 None，此后保存结果 |

同一问题会复用结果；改变表达式、深度等设置后会重新计算。
无深度限制时的 nodes_visited 包含前面逐层加深的访问次数，search_tree 只保存最终一轮。

## 7. 用结构化结果写自己的程序

```python
from integral_compass import analyze

r = analyze("log(x)**2", 2)
print(r.status)        # unknown
print(r.reason_code)   # unresolved_branch
print(r.reason)        # 具体解释
print(r.value)         # 与 integrate() 的返回值一致
print(r.to_dict())     # 可转成 JSON 的数据
```

主要字段还有 antiderivative、method、verified、steps、search_depth、depth_reached 和 search_tree。
失败时 antiderivative 都可能为空，判断结果应查看 status，而不是只检查这个字段。
程序判断失败原因时，优先使用稳定的 reason_code，不要依赖整段英文文字完全相同。

## 8. 内部原理

### 8.1 两方向分部积分搜索

对于 c*u*g，先用基本公式或有理函数规则求 g 的原函数 v，再按下式处理：

```text
integral(c*u*g) = c*(u*v - integral(u'*v))
```

程序尝试交换两个因子的 D/I 方向。多个因子则枚举非空分组和两个方向，最多八个规范化因子。
“全部路线”指这些明确规则生成的路线，不包括任意换元或所有可能的恒等变形。
如果拿不到 v，该方向仍未决；另一个方向仍可能成功。

### 8.2 部分分式终点

对有理函数，先做多项式除法，再按因子拆分；重复一次因子需要每一级幂的项，
不可约二次因子需要一次分子。拆分和逐项积分依赖 SymPy。
课堂路径支持次数不超过 30 的多项式/有理函数；不支持的输出表示仍可能 unknown。
其它终点包括线性内函数的 exp/sin/cos，以及一次式的有理数幂。

### 8.3 循环积分方程

```python
IntegralSolver("exp(x)*sin(x)", 3).solve()
```

令 J 为原积分。连续分部积分后：

```text
J = exp(x)*(sin(x)-cos(x)) - J
J = exp(x)*(sin(x)-cos(x))/2 + C
```

程序在递归开始时判断余项是否为起始被积函数的常数倍，并保留整条路径的系数与减号。
实际维护 J=A+B*当前积分；若当前函数=k*原始函数，则解 (1−B*k)*J=A。
J=J 一类退化方程不能提供答案。加法拆分后的各项分别建立循环方程。

### 8.4 Risch 与答案验证

Risch 后端来自 SymPy，主要覆盖其已实现的指数/对数情形，不是完整的任意函数判定器。
只有 NonElementaryIntegral 形式的后端证据，才被用作无初等原函数的判定。
普通的未求值积分、超时或特殊函数答案都不能单独作为这种证据。

候选原函数需要将 F'(x)−f(x) 符号化简为零。实数有理函数的 log(Abs(g))
按照 g 不为零时的局部导数恒等式检查。不自动分析最大定义域、奇点两侧常数或全部分支。

## 9. 命令行与课堂演示

在 Windows 的虚拟环境中运行：

```powershell
.\.venv\Scripts\integral-compass.exe "x*exp(x)" --depth 2
.\.venv\Scripts\integral-compass.exe "exp(-x**2)" --json
```

支持 --depth、--variable、--timeout、--json。退出码 0 表示有明确结果，
包括成功、限深耗尽或 Risch 证书；2 表示输入错误；3 表示 unknown。
兼容模式 --classic 保留早期 Python None/异常语义，与本说明书的新接口返回值不同。

### 一分钟流程

| 时间 | 展示内容 |
| --- | --- |
| 0–8 秒 | 说明来自积分笔记，目标是展示选择和推导过程 |
| 8–25 秒 | x*exp(x)：深度 2 成功，深度 1 返回 Python None |
| 25–38 秒 | 1/(x*(x+1)) 的部分分式及积分 |
| 38–50 秒 | exp(-x**2) 自动返回 Risch 证明字符串 |
| 50–58 秒 | Abs(x) 返回 unknown 和规则不支持的解释 |
| 58–60 秒 | 结束，进入问答 |

课堂用短输出，完整失败案例作为问答备用。计时需要演讲者亲自排练，
提前在实际演示电脑检查环境、文件和网络。

演示脚本位于仓库 examples 目录；仅用 pip 安装包不会自动下载这些源码脚本。
需要脚本时下载仓库，或者使用此前提供的 Windows 测试包：

```bash
python examples/presentation_demo.py
python examples/presentation_demo.py --steps
python examples/failure_cases.py
python examples/failure_cases.py --internal
```

Windows 测试包可双击 run_demo.cmd 和 run_failures.cmd；源码仓库的 scripts
目录不是已组装的测试包，不应直接当作离线安装包使用。

## 10. 常见问题与完成情况

- **导入失败：** 确认安装和运行使用的是同一个 .venv 解释器。
- **输出 None：** 这是限深搜索结果；增大深度可能成功。
- **输出 Risch 证书：** 只表示无初等原函数，仍可能有特殊函数表示或数值积分。
- **输出 unknown：** 阅读后面的解释，或查看 reason_code；超时可适当增加 timeout。
- **结果长得不一样：** 等价原函数可能形式不同，也可相差常数，应比较导数。
- **为什么不直接用 SymPy：** 本包将课堂策略、深度、搜索树和失败语义组织为统一教学接口；底层依赖 SymPy。

技术交付已完成：公开仓库、0.4.0 PyPI 发行、文档、96 项测试、跨平台 CI、
全新环境 PyPI 安装和七项功能冒烟验证均已有记录。
课程最终完成仍需实际成员贡献说明、课程 Wiki、正式提交、现场运行和一分钟演示。

本项目使用 OpenAI Codex 协助开发、测试和文档。数学方法来自标准微积分，
符号计算后端为 SymPy；项目不声称发明 DI、部分分式或完整实现 Risch。
