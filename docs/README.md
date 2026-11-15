# Integral Compass 项目文档

**版本：0.4.0 · Python 3.10+ · MIT 许可证**

[公开仓库](https://github.com/wyb20080315-cyber/integral-compass) ·
[PyPI 0.4.0](https://pypi.org/project/integral-compass/0.4.0/) ·
[项目介绍与安装](../README.md) ·
[PyPI 发布说明](releasing.md)

## 动机与项目特色

项目来自微积分笔记中的一个问题：如何让程序尝试分部积分的两个方向，
保留推导过程，并区分搜索深度不足、规则未支持和已证明无初等原函数？

本包提供可控深度搜索、部分分式步骤、循环积分方程、原函数求导验证、
带具体原因的失败返回值，以及可复用的 Python API 和命令行。
SymPy 提供符号运算、部分分式和 Risch 后端；本项目的贡献是搜索策略、
统一结果语义和教学展示，不声称发明新的数学算法或实现完整 Risch。

## 从这里开始

| 需要什么 | 文档 |
| --- | --- |
| 完整中文使用指南、返回值说明 | [使用指南](guide.zh-CN.md) |
| Windows 上安装、导入和亲自测试 | [Windows 操作指南](windows.zh-CN.md) |
| 函数、展示类和结构化字段 | [API 参考](api.md) |
| 深度、循环方程、Risch 与数学边界 | [内部原理](mathematics.md) |
| 一分钟讲稿、最小失败案例和问答 | [演示资料](presentation.zh-CN.md) |
| 测试结果和跨平台验证 | [验证记录](validation.md) |
| 团队协作与实际贡献 | [贡献指南](../CONTRIBUTING.md) |
| 更新记录 | [Changelog](../CHANGELOG.md) |

## 一个例子

```python
from integral_compass import IntegralSolver, integrate

print(integrate("x*exp(x)", 1))  # None：限深搜索耗尽
IntegralSolver("x*exp(x)", 2).solve()  # 成功，并展示实际步骤
print(integrate("exp(-x**2)"))  # 字符串 "None, verified by Risch"
print(integrate("Abs(x)", 1))  # unknown, unsupported rule: ...
```

0.4.0 已于 2026-11-15 发布到 PyPI，并通过全新环境安装与功能验证：

```bash
python -m pip install integral-compass==0.4.0
```

源码安装、演示脚本和测试命令见[项目首页](../README.md)。
