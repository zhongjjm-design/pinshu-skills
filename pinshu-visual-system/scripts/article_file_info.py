"""Use the layout's file-information parser without importing its renderer."""
import importlib.util
from pathlib import Path
path=Path(__file__).resolve().parents[2]/'pinshu-wechat-layout/scripts/article_header.py'
spec=importlib.util.spec_from_file_location('pinshu_article_header',path)
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
split_header=module.split_header
