#!/usr/bin/env python3
"""自查：逐项检查视觉 Skill 运行需要的东西，缺什么、怎么补、缺了会跳过哪一步。只用标准库。"""
import importlib.util
import os
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SKILL = HERE.parent
SKILLS = SKILL.parent
missing_required, missing_optional = [], []


def check(ok, name, fix, required=True, skipped=''):
    mark = '有' if ok else ('缺' if required else '缺（可选）')
    print(f'[{mark}] {name}' + ('' if ok else f'\n      补法：{fix}' + (f'\n      缺了会跳过：{skipped}' if skipped else '')))
    if not ok:
        (missing_required if required else missing_optional).append(name)


import platform
print(f'Python：{sys.executable}（{sys.version.split()[0]}）；系统：{platform.system()} {platform.release()}')
print('[说明] 依赖装在哪个 Python 里，就要用哪个 Python 跑本 Skill。终端里的 python3 若被别名到另一个版本（例如没装 Pillow 的 3.12），'
      '会出现“自查全有、一跑就缺库”；用上面这行显示的路径跑所有命令。')
if os.name == 'nt':
    print('[说明] Windows：脚本会自动以 UTF-8 模式重跑自己（读写中文文件需要）；也可设置环境变量 PYTHONUTF8=1。'
          '本 Skill 只在 macOS 上实测过，Windows 尚未实机验证，遇到问题请带上本自查输出反馈。')
check(sys.version_info >= (3, 10), 'Python 3.10 或更高', 'Mac 上运行 brew install python；装完用 python3 --version 确认版本，不对就改用 /opt/homebrew/bin/python3 跑本 Skill 的所有命令')
pip = f'{sys.executable} -m pip install -r {SKILL/"requirements.txt"}'
check(importlib.util.find_spec('PIL') is not None, 'Pillow（截图、拼图、导出都要）', pip)
for module, name in [('markdown_it', 'markdown-it-py'), ('bs4', 'beautifulsoup4')]:
    check(importlib.util.find_spec(module) is not None, f'{name}（整篇入口和排版要）', pip)
check((SKILLS/'pinshu-wechat-layout/scripts/build.py').exists(), '排版 Skill pinshu-wechat-layout（与本 Skill 装在同一个 skills 目录）',
      '从同一个仓库一起安装 pinshu-wechat-layout')
ego = os.environ.get('PINSHU_EGO_BROWSER') or shutil.which('ego-browser') or os.path.expanduser('~/.local/bin/ego-browser')
check(Path(ego).exists(), 'ego 浏览器命令行 ego-browser（自动截图、手机预览检查要）',
      '安装 ego 浏览器并确认 ego-browser 在 PATH 里；或设置环境变量 PINSHU_EGO_BROWSER', required=False,
      skipped='自动截图和浏览器手机检查。整篇入口改用 --prepare-only，截图走待截图清单，交给有浏览器的人或 Agent')
check(bool(shutil.which('magick')), 'ImageMagick 7 命令 magick（导出平台尺寸图、发布副本要）', 'Mac 上运行 brew install imagemagick', required=False,
      skipped='平台尺寸导出和发布副本；只能交计划和原图，不能报“成品完成”')
print('[说明] 本 Skill 不自带生图模型和钥匙。生图靠当前 Agent 自己的生图能力；没有就只交视觉计划和提示词，标明“待生图”。')
check((SKILLS/'pinshu-write/scripts/export_article.py').exists(), '写稿 Skill pinshu-write（只有试稿模式要）',
      '从同一个仓库安装 pinshu-write', required=False, skipped='试稿模式；定稿待发的正式入口不受影响')
print()
if missing_required:
    print(f'缺 {len(missing_required)} 项必需：' + '、'.join(missing_required))
    sys.exit(1)
print('必需项全部就绪' + (f'；可选缺 {len(missing_optional)} 项，见上' if missing_optional else '，可选项也全部就绪'))
