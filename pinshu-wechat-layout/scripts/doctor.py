#!/usr/bin/env python3
"""环境自查：只用标准库。必需项缺失退出码 1，否则 0。"""
import importlib
import platform
import sys
from pathlib import Path

missing = 0
print("系统：%s %s；Python：%s（只在 macOS 实测过，Windows 尚未实机验证）" % (platform.system(), platform.release(), sys.executable))
HERE = Path(__file__).resolve().parent.parent

if sys.version_info >= (3, 10):
    print("OK  Python %d.%d.%d" % sys.version_info[:3])
else:
    print("缺 Python>=3.10（当前 %d.%d）。补法：Mac 上运行 brew install python，装完用 python3 --version 确认；不对就改用 /opt/homebrew/bin/python3 跑本 Skill 的命令" % sys.version_info[:2])
    missing += 1

for pkg, mod in (("markdown-it-py", "markdown_it"), ("beautifulsoup4", "bs4")):
    try:
        importlib.import_module(mod)
        print("OK  " + pkg)
    except ImportError:
        print("缺 %s，补法：%s -m pip install -r %s" % (pkg, sys.executable, HERE / "requirements.txt"))
        missing += 1

whole = (HERE.parent / "pinshu-visual-system/scripts/run_ready_article.py").is_file()
if whole:
    print("OK  pinshu-visual-system（整篇入口可用）")
else:
    print("缺（可选）pinshu-visual-system：整篇入口不可用，单独 build.py 仍可用。补法：从同一仓库安装 pinshu-visual-system")

if missing:
    print("缺 %d 项必需" % missing)
else:
    print("全部就绪" if whole else "单独排版就绪；整篇入口未就绪（缺 pinshu-visual-system）")
sys.exit(1 if missing else 0)
