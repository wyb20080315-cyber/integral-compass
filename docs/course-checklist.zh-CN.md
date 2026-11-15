# 课程交付核对表

0.4 在深度控制、循环方程与自动 Risch 基础上，增加带解释的失败消息、
一分钟演示脚本和所有失败类别的最小备用案例。
0.4.0 已通过 PR #1 整合到 main，并于 2026-11-15 正式发布到 PyPI。
从 PyPI 在全新环境安装、七项功能冒烟检查和命令行检查均通过。

| 课程要求 | 对应文件或操作 | 当前准备情况 |
| --- | --- | --- |
| 开发 Python 包 | `src/integral_compass/`、`pyproject.toml`、`tests/` | 已实现并本地验证 |
| 自动检查 | `.github/workflows/ci.yml`、`docs/validation.md` | Linux 四个 Python 版本、Windows 和构建检查均通过 |
| 公开 Git 仓库 | [wyb20080315-cyber/integral-compass](https://github.com/wyb20080315-cyber/integral-compass) | 已创建并上传代码、测试和文档 |
| 成员定期提交 | `CONTRIBUTING.md` | 已提供流程；需要成员今后真实参与 |
| PyPI 发布且主页指向仓库 | [PyPI 0.4.0](https://pypi.org/project/integral-compass/0.4.0/) | 已发布；主页和文档链接已核实 |
| 动机、创新、用例 | `README.md`、`docs/guide.zh-CN.md` | 已完成；贡献定位为教学工具的工程设计 |
| 设置与使用指南 | `README.md`、`docs/api.md`、`docs/guide.zh-CN.md` | 已完成 |
| 一分钟演示 | `examples/demo.py`、`docs/demo.zh-CN.md` | 示例和讲稿已准备；需要演讲者排练 |
| 简短问答 | `docs/demo.zh-CN.md`、`docs/mathematics.md` | 已准备常见问题与数学边界 |

仓库已由账号所有者创建，并保留初始化提交，随后上传完整项目。
团队贡献与课堂演示完成情况仍需按实际参与持续更新。
