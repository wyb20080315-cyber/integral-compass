# 在自己的 Windows 电脑上运行

适用于 Windows 10/11、Intel/AMD 64 位电脑。Python 安装程序已从官方地址下载：

https://www.python.org/ftp/python/3.13.17/python-3.13.17-amd64.exe

SHA256：`5da012101ba2e17113a9a1cd901e9ce1441086f2b7ecb5de06ec94163899a190`。
这不是“已经在你的电脑上安装”；云端只能准备文件，安装需要你在本机完成。

## 1. 安装 Python

1. 运行 `python-3.13.17-amd64.exe`。
2. 勾选 **Add python.exe to PATH**，保留 Python Launcher 和 pip。
3. 选择 **Install Now**，通常使用当前用户安装即可。
4. 安装完成后，重新打开终端，输入 `py -3.13 --version`。

看到 Python 3.13.17 就说明解释器可以启动了。你在 C 语言里用 VS 编写和运行程序；
这里的 Python 是运行程序的解释器，编辑器可以继续用现有工具，也可以用 Python 自带的 IDLE。
不需要为了这几个案例再安装整套新的 IDE。

## 2. 最省事：离线测试包

下载本次聊天提供的 `integral-compass-windows-test-kit-0.2.0.zip`，完整解压，
例如放在 `C:\code\integral-compass-test`。不要直接在压缩文件窗口里运行。

测试包里有：

- `setup_windows.cmd`：建立本地虚拟环境、从 wheels 安装包并运行案例。
- `run_example.cmd`：后续重新运行案例。
- `minimal_case.py`：你可以修改的五个最小案例。
- `wheels/`：本包和 SymPy、mpmath 的安装包，不需要从 PyPI 下载。

双击 `setup_windows.cmd`。看到 **All five minimal cases passed** 就说明包已导入并能运行。
之后编辑 `minimal_case.py`，保存，再双击 `run_example.cmd`。
这些脚本是测试包内使用的，不是在源码仓库的 scripts 目录直接双击运行。

## 3. 也可以自己敲命令

在已经解压的测试包文件夹打开 PowerShell：

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --no-index --find-links .\wheels integral-compass==0.2.0
.\.venv\Scripts\python.exe .\minimal_case.py
```

不必激活虚拟环境，也不必修改 PowerShell 执行策略。只要始终使用
`.\.venv\Scripts\python.exe`，就会使用安装了本包的同一个解释器。

源码安装则在仓库根目录运行：

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\python.exe -m pip install .
.\.venv\Scripts\python.exe .\examples\minimal_case.py
```

源码安装需要联网取得依赖。包暂未发布到 PyPI，不要直接运行
`pip install integral-compass` 并期待从索引找到它。

## 4. 自己写第一个程序

新建 `my_test.py`，不要把文件命名为 `integral_compass.py` 或 `sympy.py`：

```python
from integral_compass import integrate, IntegralSolver

print(integrate("x**2*exp(x)", 2))
print(integrate("x**2*exp(x)", 3))

problem = IntegralSolver("log(x)/(x+1)**2", 2)
answer = problem.solve()
problem.show_tree()
print("answer:", answer)
```

运行：

```powershell
.\.venv\Scripts\python.exe .\my_test.py
```

`from integral_compass import ...` 就是导入已经安装的包。发行名是
`integral-compass`，导入名使用下划线，写作 `integral_compass`。

## 5. 常见问题

- `py` 找不到：确认安装 Python Launcher，关闭终端后重新打开。
- `ModuleNotFoundError`：检查运行和安装是否使用同一个 `.venv` 解释器。
- 导入到了自己的文件：避免使用包名给脚本命名，重命名后删除旁边的 `__pycache__`。
- 得到 None：先增加深度，不代表数学上没有原函数。
- 得到 unknown：用 `analyze(...).reason` 看原因，超时可以增加 timeout。
- 想在编辑器里运行：选择测试包的 `.venv\Scripts\python.exe` 作为解释器。

Windows 安装程序由 Python 官方提供；本项目不重新签署或修改它。离线包中的数学
依赖为官方发布的纯 Python wheel，许可证随各 wheel 一起保留。
