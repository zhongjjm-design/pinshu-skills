#!/usr/bin/env python3
"""Mechanical checks for a Chinese long-form article draft (pinshu-write).

The script counts and locates. It never rewrites text and never decides
whether an article is good: semantic review stays with independent reviewers
and the author. Exit code 1 means at least one blocker was found.

Usage:
  python3 audit_draft.py --rules            (print the Chinese rules once before writing)
  python3 audit_draft.py draft.md
  python3 audit_draft.py draft.md --banned-file my_banned_words.txt --length 2500-4000
  python3 audit_draft.py draft.md --json
"""
from __future__ import annotations

import argparse
import json
import re
import statistics
import sys
from pathlib import Path

SOURCES_HEADINGS = ("\u53c2\u8003\u6587\u7ae0", "\u8d44\u6599\u6765\u6e90", "\u53c2\u8003\u8d44\u6599", "\u4fe1\u606f\u6765\u6e90")
# The end-of-article reading list is now called \u53c2\u8003\u6587\u7ae0; the older names still cut the body but get a warning.
SOURCES_CURRENT = "\u53c2\u8003\u6587\u7ae0"
SOURCES_MAX_ENTRIES = 5
# Overused abstract words: warned only in the H1 and ## lines, never in body text.
ABSTRACT_TITLE_WORDS = ("\u5224\u65ad", "\u8ba4\u77e5", "\u5e95\u5c42\u903b\u8f91", "\u6293\u624b", "\u95ed\u73af", "\u9897\u7c92\u5ea6", "\u5fc3\u667a", "\u8303\u5f0f")
NOTES_MARKERS = ("===EDITOR NOTES===", "===\u7f16\u8f91\u5907\u6ce8===")
DEFAULT_BANNED = (
    "\u9274\u4e8e", "\u7efc\u4e0a\u6240\u8ff0", "\u503c\u5f97\u6ce8\u610f\u7684\u662f", "\u4e0d\u96be\u53d1\u73b0", "\u663e\u800c\u6613\u89c1",
    "\u8d4b\u80fd", "\u98a0\u8986", "\u672a\u6765\u5df2\u6765", "\u91cd\u65b0\u5b9a\u4e49",
)
META_PHRASES = ("\u672c\u6587", "\u8fd9\u7bc7\u6587\u7ae0", "\u63a5\u4e0b\u6765\u6211\u4eec", "\u603b\u7ed3\u4e00\u4e0b", "\u4e0b\u9762\u6211\u4eec", "\u8ba9\u6211\u4eec\u4e00\u8d77")
SECOND_PERSON = "\u4f60"
CJK = re.compile(r"[\u4e00-\u9fff]")
REVERSALS = (
    ("single-sentence reversal: not X but Y", re.compile(r"\u4e0d\u662f[^\u3002\uff01\uff1f\uff1b\n]{1,40}?\u800c\u662f")),
    ("single-sentence reversal: not X, (it) is Y", re.compile(r"(?<!\u662f)\u4e0d\u662f[^\u3002\uff01\uff1f\uff1b\n\uff0c]{1,30}\uff0c\u662f(?!\u4e0d\u662f|\u5426)")),
    ("single-sentence reversal: lies not in X but in Y", re.compile(r"\u4e0d\u5728\u4e8e[^\u3002\uff01\uff1f\uff1b\n]{1,40}?\u800c\u5728\u4e8e")),
    ("single-sentence reversal: A rather than B", re.compile(r"\uff0c\u800c\u4e0d\u662f")),
)
DASH = re.compile(r"[\u2014\u2015]")
EMOJI = re.compile(r"[\U0001F300-\U0001FAFF\u2600-\u27bf]")
INLINE_SOURCE = re.compile(r"[\uff08(][^\uff09)\n]{0,30}(?:19|20)\d{2}[^\uff09)\n]{0,15}[\uff09)]")
NUMBER = re.compile(r"\d+(?:[.,]\d+)?%?")
ORDINAL_OPENERS = ("\u9996\u5148", "\u5176\u6b21")
HYPOTHETICAL_OPENERS = ("\u5047\u8bbe", "\u8bbe\u60f3")
CARD_SKIPPED = (
    "exactly one H1", "body longer", "body outside", "second person", "section outside", "sections are unbalanced",
    "subhead length", "subhead lengths", "opening uses", "paragraph lengths", "5 paragraphs in a row",
    "long paragraph", "more than three numbers", "meta narration",
)
LIST_MARKERS = ("- ", "* ", "> ", "|", "!")
EVEN_SPREAD = 0.35
EVEN_RUN = 5
EVEN_RATIO = 1.3
LATIN_TERM = re.compile(r"[A-Za-z][A-Za-z0-9.'-]*(?: [A-Za-z][A-Za-z0-9.'-]*)*")
COMMON_LATIN = {"AI", "CEO", "PPT", "APP", "App", "app"}
# A foreign term counts as explained when a bracket right after it holds Chinese
# ("Token（按字数计费的单位）"; empty or Latin-only brackets do not count), when it
# sits inside a bracket right after its Chinese name ("多邻国（Duolingo）"), or when
# an explanation phrase follows it within a few characters in the same clause
# ("RAG，也就是……", "Duolingo 是一家……"); "简称" counts only right before the term.
# Titles and subheads are checked too, each on its own, because readers skim them
# alone. URLs and the target part of Markdown links are not checked.
EXPLANATION_PHRASES = ("\u662f\u4e00\u79cd", "\u662f\u4e00\u5bb6", "\u662f\u4e00\u4e2a", "\u4e5f\u5c31\u662f", "\u6307\u7684\u662f", "\u610f\u601d\u662f")
NAME_BEFORE_PHRASES = ("\u7b80\u79f0",)
BRACKET_AFTER = re.compile(r"\s*[\uff08(]([^\uff09)\n]*)[\uff09)]")
PHRASE_GAP = re.compile(r"[\s\uff0c,\uff1a:]{0,3}")
URL_PART = re.compile(r"\]\([^)\s]*\)|(?:https?://|www\.)[^\s\uff08\uff09()\u3002\uff0c]+")
# Prompt colons and abrupt paragraph-opening comments: patterns from the
# podcast-to-article check_style.py, based on lieflat-less-ai-tone (MIT).
# Human texts: about 0.08 prompt colons per 1000 characters, AI about 0.30;
# abrupt comment openings in 0.14% of non-first paragraphs, AI 0.62%.
# The human corpus is not public, so these baselines cannot be recomputed.
PROMPT_COLON = re.compile(r"(?:\u4e00\u53e5\u8bdd(?:\u603b\u7ed3|\u8bf4|\u6982\u62ec)|\u7b80\u5355\u8bf4|\u8bf4\u767d\u4e86|\u603b\u7ed3|\u5c0f\u7ed3|\u7ed3\u8bba|\u6838\u5fc3(?:\u662f|\u5728\u4e8e|\u89c2\u70b9)?|\u5173\u952e(?:\u662f|\u5728\u4e8e)?|\u91cd\u70b9(?:\u662f)?|\u539f\u56e0(?:\u5982\u4e0b|\u6709|\u5728\u4e8e)?|\u95ee\u9898(?:\u662f|\u5728\u4e8e)?|\u7b54\u6848(?:\u662f)?|\u672c\u8d28(?:\u662f|\u4e0a)?|\u5b9a\u4e49(?:\u662f)?|\u5177\u4f53(?:\u6765\u8bf4|\u5982\u4e0b|\u5305\u62ec)?|\u4e3e\u4f8b(?:\u6765\u8bf4)?|\u6362\u53e5\u8bdd\u8bf4|\u4e5f\u5c31\u662f\u8bf4|\u6211\u7684(?:\u89c2\u70b9|\u5224\u65ad|\u7ed3\u8bba)|\u5efa\u8bae(?:\u662f)?)[\uff1a:]")
COMMENT_OPENING = re.compile(r"^(?:\u542c\u8d77\u6765|\u770b\u8d77\u6765|\u770b\u4e0a\u53bb|\u542c\u4e0a\u53bb|\u8bf4\u767d\u4e86|\u8bf4\u5230\u5e95|\u6362\u53e5\u8bdd\u8bf4|\u610f\u5473\u7740|\u503c\u5f97\u6ce8\u610f|\u4e0d\u96be\u770b\u51fa|\u7ec6\u770b|\u518d\u770b|\u56de\u8fc7\u5934\u770b|\u95ee\u9898\u5728\u4e8e|\u539f\u56e0\u5728\u4e8e|\u7ed3\u679c\u662f|\u6709\u610f\u601d\u7684\u662f|\u66f4\u91cd\u8981\u7684\u662f|\u5173\u952e\u5728\u4e8e|\u771f\u6b63\u7684)")
ANAPHOR_OPENING = re.compile(r"^(?:\u8fd9|\u90a3|\u5176|\u6b64|\u4e0a\u9762|\u524d\u9762|\u521a\u624d|\u4ee5\u4e0a|\u8be5|\u5b83|\u4ed6|\u5979|\u5b83\u4eec|\u4ed6\u4eec|\u540c\u6837|\u7c7b\u4f3c|\u76f8\u6bd4|\u53cd\u8fc7\u6765|\u4f46|\u4e0d\u8fc7|\u6240\u4ee5|\u56e0\u6b64|\u4e8e\u662f|\u800c|\u53e6|\u9664\u6b64|\u4e0e\u6b64)")

RULES_TEXT = """
\u5199\u7a3f\u89c4\u77e9\uff08\u4e2d\u6587\u539f\u6837\uff0c\u4f9b\u5199\u7a3f\u548c\u5ba1\u7a3f\u7684\u6a21\u578b\u5bf9\u7167\uff09

\u4e0d\u7528\u7684\u8bcd\uff08\u9ed8\u8ba4\uff0c\u8d26\u53f7\u753b\u50cf\u91cc\u7684\u53e6\u52a0\uff09\uff1a
  {banned}

\u4e0d\u7528\u7684\u53e5\u5f0f\uff08\u8fde\u6210\u4e00\u53e5\u7684\u53cd\u8f6c\uff09\uff1a
  \u4e0d\u662f\u2026\u2026\u800c\u662f\u2026\u2026
  \u4e0d\u662f\u2026\u2026\uff0c\u662f\u2026\u2026
  \u4e0d\u5728\u4e8e\u2026\u2026\u800c\u5728\u4e8e\u2026\u2026
  \u2026\u2026\uff0c\u800c\u4e0d\u662f\u2026\u2026
  \u53ef\u4ee5\u5076\u5c14\u7528\u53e5\u53f7\u65ad\u5f00\u7684\u77ed\u53cd\u8f6c\uff1a\u201c\u4e0d\u662f A\u3002\u662f B\u3002\u201d

\u6807\u70b9\uff1a
  \u4e0d\u7528\u7834\u6298\u53f7\uff08\u2014\u2014\uff09\uff0c\u6539\u7528\u5192\u53f7\u3001\u62ec\u53f7\u6216\u62c6\u53e5
  \u4e2d\u6587\u6807\u70b9\u5168\u89d2\uff0c\u5f15\u53f7\u7528\u201c\u201d\uff0c\u4e0d\u7528\u82f1\u6587\u5f15\u53f7
  \u6b63\u6587\u4e0d\u52a0\u7c97\uff0c\u4e0d\u7528 emoji\uff0c\u5168\u6587\u53ea\u6709\u4e00\u4e2a\u4e00\u7ea7\u6807\u9898

\u4e0d\u5199\u5143\u89e3\u8bf4\uff1a
  {meta}

\u5c11\u7528\u63d0\u793a\u6027\u5192\u53f7\uff1a\u4e00\u53e5\u8bdd\u6982\u62ec\uff1a\u3001\u7b80\u5355\u8bf4\uff1a\u3001\u95ee\u9898\u662f\uff1a\u3001\u5173\u952e\u662f\uff1a\u3001\u7b54\u6848\u662f\uff1a\u8fd9\u7c7b\uff0c\u76f4\u63a5\u8bf4\uff08\u63d0\u9192\uff0c\u4e0d\u62e6\u7a3f\uff09
\u6bb5\u9996\u522b\u7a81\u5140\u70b9\u8bc4\uff1a\u503c\u5f97\u6ce8\u610f\u3001\u95ee\u9898\u5728\u4e8e\u3001\u5173\u952e\u5728\u4e8e\u3001\u66f4\u91cd\u8981\u7684\u662f\u3001\u8bf4\u5230\u5e95\u8fd9\u7c7b\u5f00\u5934\uff0c\u53c8\u6ca1\u7528\u8fd9\u3001\u90a3\u3001\u4f46\u3001\u6240\u4ee5\u63a5\u4e0a\u6587\u7684\uff08\u63d0\u9192\uff09

\u4e0d\u7528\u5217\u8868\u8154\u5f00\u5934\uff1a\u9996\u5148\u3001\u5176\u6b21\u3001\u6700\u540e
\u6807\u9898\u548c\u5c0f\u6807\u9898\uff1a\u76f4\u63a5\u6392\u7b2c\u4e00\uff0c\u51c6\u786e\u7b2c\u4e8c\uff0c\u597d\u8bb0\u7b2c\u4e09\uff0c\u6709\u4eae\u70b9\u7b2c\u56db\uff1b\u540e\u9762\u7684\u548c\u524d\u9762\u7684\u51b2\u7a81\uff0c\u540e\u9762\u7684\u8ba9\u8def\u3002
  \u68c0\u9a8c\uff1a\u906e\u4f4f\u6b63\u6587\uff0c\u53ea\u770b\u8fd9\u4e00\u884c\uff0c\u5916\u884c\u80fd\u4e0d\u80fd\u4e00\u53e5\u8bdd\u8bf4\u51fa\u8fd9\u4e00\u8282\u6559\u4ec0\u4e48\u6216\u4e3b\u5f20\u4ec0\u4e48\uff1b\u8bf4\u4e0d\u51fa\u5c31\u91cd\u5199\u3002
  \u5b9e\u64cd\u7a3f\uff08\u52a8\u4f5c\uff0b\u8fd9\u4e00\u6b65\u4e3a\u4ec0\u4e48\u8981\u505a\uff0c\u6700\u597d\u662f\u4e00\u4e2a\u80fd\u8bb0\u4f4f\u7684\u8bf4\u6cd5\uff09\uff1a
    \u5bf9\uff1a\u6210\u7247\u5148\u8fc7\u4e00\u904d\u201c\u8d1f\u9762\u6e05\u5355\u201d\uff0c\u8e29\u4e2d\u4e00\u6761\u5c31\u91cd\u505a
    \u9519\uff1a\u7b2c\u4e09\u6b65\uff1a\u68c0\u67e5\u6210\u7247\uff08\u8bf4\u660e\u4e66\u8154\uff09
    \u9519\uff1a\u8d28\u68c0\u662f\u6700\u88ab\u4f4e\u4f30\u7684\u73af\u8282\uff08\u603b\u7ed3\u8154\uff0c\u770b\u4e0d\u51fa\u8981\u505a\u4ec0\u4e48\uff09
    \u4e0d\u7528\u201c\u7b2c\u4e00\u6b65\u3001\u7b2c\u4e8c\u6b65\u201d\uff0c\u4e0d\u7528\u201c\u5148\u3001\u518d\u3001\u7136\u540e\u201d
  \u89c2\u70b9\u7a3f\uff08\u628a\u8fd9\u4e00\u8282\u7684\u4e3b\u5f20\u76f4\u63a5\u8bf4\u51fa\u6765\uff09\uff1a
    \u5bf9\uff1a\u6309 AI \u7528\u91cf\u8003\u6838\u5458\u5de5\uff0c\u53ea\u4f1a\u8003\u51fa\u66f4\u591a\u534a\u6210\u54c1
    \u9519\uff1a\u6548\u7387\u7684\u53e6\u4e00\u9762\uff08\u8bdd\u9898\u8bcd\uff0c\u770b\u4e0d\u51fa\u4e3b\u5f20\uff09
  \u65b9\u6cd5\u7a3f\uff08\u65b9\u6cd5\u672c\u8eab\uff0c\u4e00\u53e5\u80fd\u7167\u7740\u7528\uff09\uff1a
    \u5bf9\uff1a\u62a5\u4ef7\u62c6\u6210\u4e24\u5757\uff1a\u6267\u884c\u8d39\u53ef\u4ee5\u8c08\uff0c\u5224\u65ad\u8d39\u4e0d\u6253\u6298
    \u9519\uff1a\u5173\u4e8e\u5b9a\u4ef7\u7684\u51e0\u70b9\u601d\u8003
  \u65b0\u95fb\u5206\u6790\u7a3f\uff08\u8fd9\u4ef6\u4e8b\u5bf9\u8bfb\u8005\u610f\u5473\u7740\u4ec0\u4e48\uff09\uff1a
    \u5bf9\uff1a\u6a21\u578b\u964d\u4ef7\u4e00\u534a\uff0c\u6309\u5b57\u6570\u62a5\u4ef7\u7684\u5199\u7a3f\u5916\u5305\u8981\u91cd\u65b0\u7b97\u8d26
    \u9519\uff1a\u4e00\u573a\u53d1\u5e03\u4f1a\u5e26\u6765\u7684\u542f\u793a
  \u5927\u6807\u9898\uff1a\u53ea\u770b\u6807\u9898\u5c31\u77e5\u9053\u201c\u5199\u7ed9\u6211\u3001\u6211\u80fd\u5f97\u5230\u4ec0\u4e48\u201d\uff1b\u8bfb\u8005\u719f\u6089\u3001\u8ddf\u6b63\u6587\u7d27\u76f8\u5173\u7684\u70ed\u8bcd\uff08\u65b0\u6a21\u578b\u540d\uff09\u8981\u7559\u5728\u6807\u9898\u91cc
  \u6807\u9898\u91cc\u7684\u6bcf\u4e2a\u540d\u8bcd\uff0c\u6ca1\u8bfb\u6b63\u6587\u7684\u4eba\u4e5f\u8bf4\u5f97\u51fa\u6307\u4ec0\u4e48\uff1b\u6587\u7ae0\u81ea\u5df1\u8d77\u7684\u8bf4\u6cd5\u4e0d\u8fdb\u6807\u9898
    \u9519\uff1a\u770b\u61c2\u8fd9\u628a\u5c3a\uff0c\u5c31\u770b\u61c2\u4e86\u52aa\u529b\uff08\u201c\u8fd9\u628a\u5c3a\u201d\u53ea\u6709\u8bfb\u8fc7\u6b63\u6587\u624d\u77e5\u9053\u6307\u4ec0\u4e48\uff09
  \u6bd4\u55bb\u8981\u5148\u5728\u6b63\u6587\u91cc\u7528\u5177\u4f53\u4f8b\u5b50\u8bb2\u6e05\uff0c\u624d\u80fd\u8fdb\u6807\u9898\u3001\u5c0f\u6807\u9898\uff1b\u4e0d\u8bb8\u5728\u6807\u9898\u3001\u5c0f\u6807\u9898\u91cc\u7b2c\u4e00\u6b21\u51fa\u73b0
  \u5c0f\u6807\u9898\u4e0d\u7528\u6b63\u6587\u624d\u5b9a\u4e49\u7684\u8bf4\u6cd5\u548c\u4ee3\u8bcd\uff08\u201c\u5b83\u201d\u201c\u8fd9\u4e00\u6761\u201d\u201c\u7b2c\u4e8c\u79cd\u201d\uff09
  \u6807\u9898\u8981\u6709\u7279\u8272\uff1a\u95ee\u4e00\u53e5\u201c\u8fd9\u53e5\u8bdd\u662f\u4e0d\u662f\u53ea\u6709\u8fd9\u7bc7\u6587\u7ae0\u4f1a\u8bf4\u201d\u3002\u653e\u5728\u54ea\u7bc7\u90fd\u80fd\u7528\u7684\uff0c\u7b97\u6ca1\u7279\u8272\uff1a
    \u9519\uff1a\u6548\u7387\u4e0a\u53bb\u4e86\uff0c\u4ef7\u503c\u4e0b\u6765\u4e86\uff08\u5bf9\u4ed7\u53e5\uff0c\u653e\u54ea\u7bc7\u90fd\u884c\uff09
    \u9519\uff1aAI \u65f6\u4ee3\uff0c\u662f\u65f6\u5019\u91cd\u65b0\u770b\u5f85\u52aa\u529b\u4e86\uff08\u7a7a\u558a\uff0c\u6362\u4e2a\u9898\u76ee\u7167\u6837\u80fd\u7528\uff09
    \u9519\uff1aAI \u65f6\u4ee3\u7684\u52aa\u529b\u89c2\uff08\u8bdd\u9898\u8bcd\uff0c\u6ca1\u6709\u5224\u65ad\uff09
    \u7279\u8272\u6765\u81ea\u8fd9\u7bc7\u81ea\u5df1\u7684\u5224\u65ad\u3001\u6570\u5b57\u3001\u4e8b\u4ef6\u6216\u8bfb\u8005\u7684\u95ee\u9898\uff0c\u4e0d\u9760\u5b57\u9762\u82b1\u6837\uff1b\u4e00\u773c\u61c2\u4ecd\u7136\u6392\u7b2c\u4e00
  \u6807\u9898\u5019\u9009\u7ed9\u4e09\u4e2a\uff0c\u5199\u6cd5\u5404\u4e0d\u76f8\u540c\uff1a\u4e00\u4e2a\u76f4\u8bf4\u7ed3\u8bba\uff0c\u4e00\u4e2a\u662f\u8bfb\u8005\u81ea\u5df1\u7684\u95ee\u9898\uff0c\u4e00\u4e2a\u7528\u5177\u4f53\u6570\u5b57\u6216\u4e8b\u5b9e\uff1b\u540c\u4e00\u4e2a\u94a9\u5b50\u6362\u4e09\u79cd\u8bf4\u6cd5\u53ea\u7b97\u4e00\u4e2a
  \uff08\u4ee5\u4e0a\u201c\u5bf9\u201d\u7684\u53e5\u5b50\u53ea\u662f\u683c\u5f0f\u793a\u8303\uff0c\u4e0d\u662f\u4e8b\u5b9e\uff09
\u5f00\u5934\uff1a\u624b\u91cc\u6709\u771f\u4e8b\u5c31\u7528\u771f\u4e8b\u5f00\u5934\uff1b\u201c\u5047\u8bbe\u201d\u201c\u8bbe\u60f3\u201d\u5f00\u5934\u5fc5\u987b\u6539\uff08\u5bf9\u7167\u8d26\u53f7\u6700\u8fd1\u51e0\u7bc7\uff0c\u540c\u4e00\u79cd\u5f00\u5934\u4e0d\u8fde\u7740\u7528\uff09
\u6bb5\u843d\u957f\u77ed\u522b\u6574\u9f50\u5212\u4e00\uff1a\u8fde\u7eed\u597d\u51e0\u6bb5\u4e00\u6837\u957f\uff0c\u6362\u6389\u6240\u6709\u8bcd\u4e5f\u4e00\u773c\u50cf\u673a\u5668\u5199\u7684\uff08\u63d0\u9192\uff09

\u5916\u6587\u8bcd\u7b2c\u4e00\u6b21\u51fa\u73b0\u8981\u7528\u5927\u767d\u8bdd\u89e3\u91ca\uff0c\u7d27\u8ddf\u62ec\u53f7\u4e14\u62ec\u53f7\u91cc\u5199\u4e2d\u6587\uff0c\u6216\u7d27\u8ddf\u7740\u8bf4\u201c\u662f\u4e00\u79cd\u201d\u201c\u4e5f\u5c31\u662f\u201d\uff1b\u7a7a\u62ec\u53f7\u3001\u62ec\u53f7\u91cc\u53ea\u6709\u5916\u6587\u3001\u9694\u5f00\u534a\u53e5\u518d\u89e3\u91ca\u90fd\u4e0d\u7b97\uff1b\u6807\u9898\u548c\u5c0f\u6807\u9898\u91cc\u7684\u5916\u6587\u8bcd\u4e5f\u8981\u67e5\uff1b\u89e3\u91ca\u8fc7\u7684\u4e0d\u518d\u63d0\u9192
\u6b63\u6587\u4e0d\u5939\u62ec\u53f7\u51fa\u5904\uff1b\u4e00\u6bb5\u6700\u591a\u4e00\u4e2a\u4f8b\u5b50\u3001\u4e00\u7ec4\u6570\u5b57\u3002
\u6587\u672b\u6765\u6e90\u533a\u53eb\u201c\u53c2\u8003\u6587\u7ae0\u201d\uff0c\u53ea\u5217\u771f\u6b63\u7528\u5230\u3001\u8bfb\u8005\u503c\u5f97\u53bb\u8bfb\u7684\u5b8c\u6574\u957f\u6587\uff08\u6807\u9898\u3001\u4f5c\u8005\u3001\u5e73\u53f0\u3001\u65e5\u671f\uff09\uff0c\u6709\u51e0\u7bc7\u5217\u51e0\u7bc7\uff0c\u522b\u628a\u6240\u6709\u51fa\u5904\u5806\u6210\u4e00\u957f\u4e32\uff1b\u67e5\u8bc1\u6e05\u5355\u653e\u7f16\u8f91\u5907\u6ce8\u540e\uff0c\u4e0d\u8fdb\u6b63\u6587\u3002
\u5c0f\u6807\u9898\u548c\u6807\u9898\u5c11\u7528\u8bf4\u70c2\u7684\u62bd\u8c61\u8bcd\uff08\u5224\u65ad\u3001\u8ba4\u77e5\u3001\u5e95\u5c42\u903b\u8f91\u7b49\uff09\uff0c\u7528\u8bfb\u8005\u751f\u6d3b\u91cc\u7684\u8bcd\u3002
\u5c0f\u6807\u9898\u8bfb\u4e00\u904d\uff0c\u770b\u6709\u6ca1\u6709\u80fd\u88ab\u65ad\u9519\u7684\u8bcd\uff08\u201c\u8bb2\u4eba\u624d\u7528\u751f\u6210\u201d\u88ab\u8bfb\u6210\u201c\u4eba\u624d\u201d\uff09\uff1b\u5916\u884c\u8bfb\u8005\u62a5\u51fa\u7684\u65ad\u8bcd\u6b67\u4e49\u5fc5\u987b\u6539\u3002
\u8bfb\u8005\u4f1a\u5361\u4f4f\u7684\u4e03\u5904\uff1a
  \u6307\u4ee3\u843d\u5230\u4eba\u6216\u7269\uff1a\u201c\u8fd9\u6761\u201d\u201c\u8fd9\u4e2a\u201d\u8fde\u7528\u65f6\u6362\u6210\u540d\u5b57
  \u7247\u540d\u3001\u4f5c\u54c1\u540d\u7b2c\u4e00\u6b21\u51fa\u73b0\uff0c\u5148\u4ea4\u4ee3\u662f\u8c01\u7684\u4f5c\u54c1
  \u8fc7\u6e21\u53e5\u8bf4\u6e05\u4ece\u54ea\u8f6c\u5230\u54ea\uff1b\u201c\u540c\u6837\u7684\u89c4\u5f8b\u201d\u8fd9\u7c7b\u7a7a\u6307\u4e0d\u7b97\u8fc7\u6e21
  \u52a8\u4f5c\u8bcd\u8981\u51c6\uff1a\u6ca1\u505a\u7edf\u8ba1\u4e0d\u8bf4\u201c\u62bd\u6837\u201d
  \u4ea7\u54c1\u540d\u76f4\u63a5\u5199\u51fa\u6765\uff0c\u4e0d\u7528\u201c\u8fd9\u7c7b\u529f\u80fd\u201d\u4ee3\u66ff
  \u81ea\u9020\u7684\u8bf4\u6cd5\uff08\u201c\u6700\u5c0f\u7684\u7ebf\u201d\uff09\u6362\u6210\u5927\u767d\u8bdd
  \u4f1a\u53d8\u7684\u6570\u5b57\uff08\u6d4f\u89c8\u91cf\u3001\u64ad\u653e\u91cf\uff09\u6309\u53d1\u7a3f\u5f53\u5929\u590d\u6d4b\uff0c\u53e5\u5b50\u91cc\u5199\u4e0a\u65e5\u671f
\u6807\u9898\u8bb8\u8bfa\u4e86\u4ec0\u4e48\uff08\u201c\u662f\u4e2a\u8bef\u4f1a\u201d\uff09\uff0c\u7ed3\u5c3e\u5c31\u660e\u767d\u8bf4\u51fa\u6765\uff08\u8bef\u4f1a\u5728\u54ea\uff09\u3002
\u4e0d\u7f16\u201c\u5f88\u591a\u4eba\u8bf4\u201d\u201c\u670b\u53cb\u8ddf\u6211\u8bf4\u201d\u8fd9\u7c7b\u6ca1\u51fa\u5904\u7684\u4eba\uff1b\u4e0d\u7f16\u6599\u91cc\u6ca1\u6709\u7684\u7ea6\u6570\uff08\u201c\u524d\u4e24\u5e74\u201d\u201c\u4e09\u5230\u56db\u6210\u201d\uff09\u3002
"""


def cjk_len(text: str) -> int:
    return len(CJK.findall(text))


def split_body(text: str) -> tuple[list[tuple[int, str]], int]:
    """Return numbered body lines (before sources/notes) and the cut line number."""
    lines = text.splitlines()
    body: list[tuple[int, str]] = []
    cut = len(lines)
    skip_until = 0
    if lines and lines[0].strip() == "---":
        for index, line in enumerate(lines[1:], 2):
            if line.strip() == "---":
                skip_until = index
                break
    for index, line in enumerate(lines, 1):
        if index <= skip_until:
            continue
        stripped = line.strip().lstrip("#").strip()
        if stripped in SOURCES_HEADINGS or any(line.strip().startswith(m) for m in NOTES_MARKERS):
            cut = index
            break
        body.append((index, line))
    while body and body[-1][1].strip() in {"", "---"}:
        body.pop()
    return body, cut


def blank_urls(text: str) -> str:
    """Replace URLs and Markdown link targets with spaces, keeping positions."""
    return URL_PART.sub(lambda m: " " * len(m.group(0)), text)


def term_explained(para: str, start: int, end: int) -> bool:
    """True when a foreign term is explained right where it appears."""
    bracket = BRACKET_AFTER.match(para, end)
    if bracket and CJK.search(bracket.group(1)):
        return True
    before = para[:start].rstrip()
    if before.endswith(("\uff08", "(")) and CJK.search(before[:-1].rstrip()[-1:]):
        return True
    if before.endswith(NAME_BEFORE_PHRASES):
        return True
    gap = PHRASE_GAP.match(para, end)
    return para.startswith(EXPLANATION_PHRASES, gap.end())


def excerpt(line: str, start: int, width: int = 36) -> str:
    left = max(0, start - 8)
    return line[left:left + width].strip()


def source_section(text: str) -> tuple[str | None, int | None, int]:
    """Return (heading, line number, list entry count) of the end source section, if any."""
    lines = text.splitlines()
    for index, line in enumerate(lines, 1):
        name = line.strip().lstrip("#").strip()
        if name in SOURCES_HEADINGS:
            entries = 0
            for later in lines[index:]:
                if any(later.strip().startswith(m) for m in NOTES_MARKERS):
                    break
                if re.match(r"^\s*(?:[-*+]|\d+[.)\u3001])\s+\S", later):
                    entries += 1
            return name, index, entries
    return None, None, 0


def audit(text: str, banned: list[str], length: tuple[int, int], hard_max: int,
          section_min: int, section_max: int, you_per_k: float, para_max: int,
          subhead_range: tuple[int, int] = (8, 14), card: bool = False) -> dict:
    findings: list[dict] = []

    def add(level: str, rule: str, line_no: int | None, detail: str) -> None:
        findings.append({"level": level, "rule": rule, "line": line_no, "detail": detail})

    body, _ = split_body(text)
    h1 = [n for n, line in body if re.match(r"^#\s+\S", line)]
    if len(h1) != 1:
        add("blocker", "exactly one H1 title", h1[0] if h1 else None, f"found {len(h1)} H1 lines")

    paragraphs: list[tuple[int, str]] = []
    headings: list[tuple[int, str]] = []
    sections: list[dict] = [{"title": "(opening)", "line": 1, "chars": 0}]
    for number, line in body:
        stripped = line.strip()
        if not stripped or stripped == "---":
            continue
        if stripped.startswith("#"):
            headings.append((number, stripped.lstrip("#").strip()))
        if stripped.startswith("## "):
            sections.append({"title": stripped[3:].strip(), "line": number, "chars": 0})
            continue
        if stripped.startswith("#"):
            continue
        paragraphs.append((number, stripped))
        sections[-1]["chars"] += cjk_len(stripped)

    for number, line in body:
        for match in DASH.finditer(line):
            add("blocker", "no em dash", number, excerpt(line, match.start()))
        for label, pattern in REVERSALS:
            for match in pattern.finditer(line):
                add("blocker", label, number, match.group(0)[:40])
        for word in banned:
            if word and word in line:
                add("blocker", "banned word", number, word)
        for match in EMOJI.finditer(line):
            add("blocker", "no emoji", number, excerpt(line, match.start()))

    for number, para in paragraphs:
        if '"' in para and CJK.search(para):
            add("fix", "use curly Chinese quotes \u201c \u201d", number, excerpt(para, para.index('"')))
        if "**" in para:
            add("fix", "no bold in body text", number, excerpt(para, para.index("**")))
        for match in INLINE_SOURCE.finditer(para):
            add("fix", "move inline source to the end source list", number, match.group(0))
        for phrase in META_PHRASES:
            if phrase in para:
                add("warn", "meta narration", number, phrase)
        size = cjk_len(para)
        if size > para_max:
            add("warn", f"long paragraph (> {para_max} characters)", number, f"{size} characters")
        for match in PROMPT_COLON.finditer(para):
            add("warn", "prompt colon: say it plainly instead of announcing it", number, match.group(0))
        numbers = set(NUMBER.findall(para))
        if len(numbers) > 3:
            add("warn", "more than three numbers in one paragraph", number, ", ".join(sorted(numbers))[:60])

    for index, (number, para) in enumerate(paragraphs):
        if index and COMMENT_OPENING.match(para) and not ANAPHOR_OPENING.match(para):
            add("warn", "abrupt comment opens a paragraph without linking to the previous one", number, para[:20])

    openers = [n for n, p in paragraphs if p.startswith(ORDINAL_OPENERS)]
    if len(openers) >= 2:
        add("warn", "first/second ordinal paragraph openers read like a list", openers[0], f"{len(openers)} paragraphs")

    titles = [s for s in sections[1:]]
    if titles:
        lengths = [len(s["title"].replace(" ", "")) for s in titles]
        for s, size in zip(titles, lengths):
            if size < subhead_range[0] or size > subhead_range[1]:
                add("warn", f"subhead length outside {subhead_range[0]}-{subhead_range[1]} characters", s["line"],
                    f"{s['title'][:24]}: {size}")
        if len(lengths) >= 2 and max(lengths) - min(lengths) > 5:
            add("warn", "subhead lengths differ by more than 5 characters", None,
                f"shortest {min(lengths)}, longest {max(lengths)}")

    opening = [p for n, p in paragraphs if n < (sections[1]["line"] if len(sections) > 1 else 10**9)][:2]
    if any(p.startswith(HYPOTHETICAL_OPENERS) or (HYPOTHETICAL_OPENERS[0] + SECOND_PERSON) in p for p in opening):
        add("fix", "opening uses a hypothetical scene; open on a real event if one exists, and vary from recent articles", None,
            opening[0][:30] if opening else "")

    # Even paragraph lengths read as machine-made even after every word is fixed.
    # Calibrated in October 2026 on about thirty drafts and published pieces of one
    # account: no human-edited piece had a length variation below 0.39; five similar
    # paragraphs in a row (within 1.3x) appeared in machine-heavy drafts and in 2 of 18
    # published pieces. Both are warnings, never blockers.
    prose = [(n, cjk_len(p)) for n, p in paragraphs if not p.startswith(LIST_MARKERS) and cjk_len(p) >= 10]
    sizes = [size for _, size in prose]
    if len(sizes) >= 8:
        spread = statistics.pstdev(sizes) / statistics.mean(sizes)
        if spread < EVEN_SPREAD:
            add("warn", "paragraph lengths are too even across the article", None,
                f"variation {spread:.2f} (below {EVEN_SPREAD:g})")
    for start in range(len(sizes) - EVEN_RUN + 1):
        window = sizes[start:start + EVEN_RUN]
        if max(window) <= EVEN_RATIO * min(window):
            add("warn", f"{EVEN_RUN} paragraphs in a row have nearly the same length", prose[start][0],
                ", ".join(str(size) for size in window))
            break

    seen_terms: set[str] = set()
    for number, para in paragraphs:
        clean = blank_urls(para)
        for match in LATIN_TERM.finditer(clean):
            term = match.group(0).rstrip(".'-")
            if len(term) < 3 or term in COMMON_LATIN or term in seen_terms:
                continue
            seen_terms.add(term)
            if term_explained(clean, match.start(), match.start() + len(term)):
                continue
            add("warn", "foreign term: explain it in plain words at first use", number, term)
    for number, heading in headings:
        clean = blank_urls(heading)
        for term in dict.fromkeys(m.group(0).rstrip(".'-") for m in LATIN_TERM.finditer(clean)):
            if len(term) < 3 or term in COMMON_LATIN:
                continue
            start = clean.find(term)
            if term_explained(clean, start, start + len(term)):
                continue
            add("warn", "foreign term in a title or subhead: readers skim these alone, explain or replace it",
                number, term)

    for number, heading in headings:
        for word in ABSTRACT_TITLE_WORDS:
            if word in heading:
                add("warn", "overused abstract word in a title or subhead: use the reader's everyday words",
                    number, word)

    # End-of-article source list: current name; list only the complete long reads actually used (no quota).
    src_name, src_line, src_entries = source_section(text)
    if src_name and src_name != SOURCES_CURRENT:
        add("warn", f"source section should be headed {SOURCES_CURRENT}, not the old name", src_line, src_name)
    if src_name == SOURCES_CURRENT and src_entries > SOURCES_MAX_ENTRIES:
        add("warn", f"{SOURCES_CURRENT} lists more than {SOURCES_MAX_ENTRIES} entries: check each is a complete long read readers need, not a pile of every source",
            src_line, f"{src_entries} entries")

    total = sum(cjk_len(p) for _, p in paragraphs)
    if total > hard_max:
        add("blocker", f"body longer than the hard maximum {hard_max}", None, f"{total} characters")
    elif not length[0] <= total <= length[1]:
        add("warn", f"body outside the usual range {length[0]}-{length[1]}", None, f"{total} characters")

    you = sum(p.count(SECOND_PERSON) for _, p in paragraphs)
    density = you * 1000 / total if total else 0.0
    if density > you_per_k:
        add("warn", f"second person above {you_per_k:g} per 1000 characters", None, f"{you} uses, {density:.1f} per 1000")

    named = [s for s in sections[1:]]
    for section in named:
        if section["chars"] < section_min or section["chars"] > section_max:
            add("warn", f"section outside {section_min}-{section_max} characters", section["line"],
                f"{section['title'][:24]}: {section['chars']}")
    if len(named) >= 2:
        sizes = [s["chars"] for s in named if s["chars"]]
        if sizes and max(sizes) > 2.5 * max(1, min(sizes)):
            add("warn", "sections are unbalanced (largest > 2.5x smallest)", None,
                f"min {min(sizes)}, max {max(sizes)}, median {statistics.median(sizes):g}")

    if card:
        # Cards, outlines and other process texts shown to the author follow the
        # Chinese wording rules but not the article-shape rules.
        findings[:] = [f for f in findings if not f["rule"].startswith(CARD_SKIPPED)]
    order = {"blocker": 0, "fix": 1, "warn": 2}
    findings.sort(key=lambda f: (order[f["level"]], f["line"] or 0))
    return {
        "stats": {
            "body_characters": total,
            "paragraphs": len(paragraphs),
            "sections": [{"title": s["title"], "characters": s["chars"]} for s in sections],
            "second_person": you,
        },
        "counts": {level: sum(1 for f in findings if f["level"] == level) for level in order},
        "findings": findings,
    }


# Scope and relationship wording that turns "this still counts, and we also look at that"
# into "this no longer counts" or "only that counts". In testing, models made exactly this
# change to the author's seed and then reported that no scope word had changed, so the
# comparison is done by this script, not by the model that wrote the judgment.
SCOPE_PATTERNS = [
    ("no longer", re.compile(r"不再(?!只是|只|仅)|再也不|说明不了|失去了?意义|作用.{0,4}有限|不再重要")),
    ("turn from A to B", re.compile(r"转向|转为|转变为|转到|改看|改成看|从.{1,20}变成")),
    ("replace", re.compile(r"取代|替代(?!方案|品|选项|路径|办法)|代替")),
    ("the real thing is", re.compile(r"真正的.{0,12}在于|不在于")),
    ("only", re.compile(r"唯一(?!标识|索引|键|编号)|只看|仅看|只剩|全靠|只要看(?!清|懂|到|见|完|明白)")),
    ("has failed", re.compile(r"失灵|失效|作废|过时|淘汰")),
    ("worthless", re.compile(r"不值钱|没用了|已经没用|不管用|不重要了")),
    ("go back to", re.compile(r"退回|回到旧")),
    ("do not look at", re.compile(r"(?<!先)不看|别看|不用看|不必看")),
]
# A scope word right after one of these keeps the author's meaning ("新标准不能替代旧标准",
# "旧标准并未过时", "这并非唯一答案", "不能只看结果"), so it is not a drift.
# Modifiers that may sit between the negation and the scope word without changing the meaning:
# "\u4e0d\u80fd\u5b8c\u5168\u66ff\u4ee3", "\u6ca1\u6709\u4efb\u4f55\u5de5\u5177\u80fd\u66ff\u4ee3", "\u4e0d\u80fd\u65e0\u6761\u4ef6\u66ff\u4ee3".
_MODS = (r"(?:(?:\u5b8c\u5168|\u5f7b\u5e95|\u6839\u672c|\u65e0\u6761\u4ef6|\u7edd\u5bf9|\u8f7b\u6613|\u76f4\u63a5|\u771f\u6b63|\u7b80\u5355\u5730?|\u5168\u90e8|\u90fd|\u4e5f|\u5c31|\u4f1a|\u80fd|\u53ef\u4ee5)"
         r"|\u4efb\u4f55.{1,4}?)*")
NEGATORS = re.compile(r"(?:\u4e0d\u80fd|\u4e0d\u4f1a|\u4e0d\u5e94|\u4e0d\u8be5|\u5e76\u672a|\u5e76\u975e|\u6ca1\u6709|\u672a\u5fc5|\u4e0d\u662f|\u65e0\u6cd5|\u4e0d\u53ef|\u522b|\u4e0d)\u88ab?\s*" + _MODS + r"$")
OUTER_NEGATION = re.compile(r"\u4e0d\u662f|\u5e76\u4e0d|\u5e76\u975e|\u5e76\u6ca1\u6709|\u5e76\u672a|\u672a\u5fc5|\u7edd\u975e|\u6ca1\u8bf4|\u4e0d\u7b49\u4e8e|\u8c01\u8bf4|\u4e0d\u80fd\u8bf4|\u5f88\u96be\u8bf4")
# "|" ends a sentence too, so a Markdown table row is compared cell by cell.
SENTENCE_END = re.compile(r"[\u3002\uff01\uff1f\uff1b\uff1a:\n|]")
CLAUSE_BREAK = re.compile(r"[\uff0c,\u3001]")
# "\u5df2\u7ecf\u8fc7\u65f6\uff0c\u4f46\u65e7\u5c3a\u5b50\u4ecd\u7136\u6709\u6548": a failure word followed by a contrast that keeps something valid.
CONTRAST_KEEPS = re.compile(r"^[^\u3002\uff01\uff1f\uff1b]{0,12}?[\uff0c,]\s*(?:\u4f46|\u4e0d\u8fc7|\u7136\u800c)(?!.*\u65b0)[^\uff0c,\u3002]{0,12}?(?:\u4ecd\u7136|\u4f9d\u7136|\u4f9d\u65e7|\u4ecd|\u8fd8\u662f)[^\uff0c,\u3002]{0,6}(?:\u6709\u6548|\u6709\u7528|\u7b97\u6570|\u6709\u4ef7\u503c|\u6210\u7acb|\u7ba1\u7528|\u9002\u7528)")
# Known limit: a clause inserted between the outer negation and the scope word with a comma
# ("\u4e0d\u662f\uff0c\u5728\u8fd9\u79cd\u60c5\u51b5\u4e0b\uff0c\u4e0d\u80fd\u66ff\u4ee3") is read as two clauses, so that reversal is not caught; the
# author review of the card is the backstop. Same for a scope word whose subject changes after a comma.


def _norm(text: str) -> str:
    return re.sub(r"[\s\uff0c\u3001\uff1a:\u201c\u201d\"'\uff08\uff09()\u300a\u300b]", "", text)


def _strip_marker(text: str) -> str:
    """Drop a leading list / quote / heading marker so '- sentence' equals 'sentence'."""
    return re.sub(r"^[\s>#*+\-]+", "", text)


def seed_scope_findings(text: str, seed: str) -> list[dict]:
    """Flag sentences that use scope or relationship wording and are not the author's own sentences.

    Judged sentence by sentence, not by counting: a sentence quoted from the seed is skipped,
    a negated scope word is skipped, and every other hit is reported with its line.
    A sentence counts as the author's own only when it EQUALS a whole seed sentence or a whole seed
    table cell (after normalisation); being a substring of a longer seed sentence does not count,
    because cutting the qualifier off a seed sentence is exactly the drift this check exists to catch.
    """
    seed_sentences = {_norm(_strip_marker(part)) for part in SENTENCE_END.split(seed)} - {""}
    findings = []
    for number, line in enumerate(text.splitlines(), 1):
        for label, pattern in SCOPE_PATTERNS:
            for match in pattern.finditer(line):
                start = max((m.end() for m in SENTENCE_END.finditer(line, 0, match.start())), default=0)
                end_match = SENTENCE_END.search(line, match.end())
                sentence = line[start:end_match.start() if end_match else len(line)]
                norm = _norm(_strip_marker(sentence))
                if norm and norm in seed_sentences:
                    continue  # the author's own sentence or table cell, copied whole
                if label == "has failed" and CONTRAST_KEEPS.match(line[match.end():]):
                    continue
                window_start = max(0, match.start() - 14)
                inner = NEGATORS.search(line[window_start:match.start()])
                # One negation next to the scope word keeps the author's meaning ("\u4e0d\u80fd\u66ff\u4ee3",
                # "\u5e76\u672a\u8fc7\u65f6"). An outer negation earlier in the same clause turns it back
                # ("\u5e76\u4e0d\u662f\u5728\u4efb\u4f55\u60c5\u51b5\u4e0b\u90fd\u4e0d\u80fd\u66ff\u4ee3", "\u4e0d\u662f\u6ca1\u6709\u8fc7\u65f6"), so that sentence is reported.
                # A comma ends the clause: an outer "\u4e0d\u662f" before a comma does not govern a later
                # "\u4e0d\u80fd\u4ee3\u66ff". "\u4e0d\u4ec5", "\u4e0d\u4f46", "\u4e0d\u540c" and the like are not outer negations.
                if inner:
                    before = line[start:window_start + inner.start()]
                    clause = CLAUSE_BREAK.split(before)[-1]
                    if not OUTER_NEGATION.search(clause):
                        continue
                findings.append({"level": "fix", "line": number,
                                 "rule": f"scope wording not in the seed ({label}): show the author",
                                 "detail": excerpt(line, match.start())})
    return findings


def parse_range(value: str) -> tuple[int, int]:
    low, _, high = value.partition("-")
    return int(low), int(high)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("draft", type=Path, nargs="?")
    parser.add_argument("--rules", action="store_true", help="print the Chinese rules this script enforces, then exit")
    parser.add_argument("--banned-file", type=Path, help="UTF-8 text file, one extra banned word per line")
    parser.add_argument("--no-default-banned", action="store_true", help="use only the banned-file list")
    parser.add_argument("--length", type=parse_range, default=(2500, 4000), help="usual body range, e.g. 2500-4000")
    parser.add_argument("--hard-max", type=int, default=6000)
    parser.add_argument("--section-min", type=int, default=300)
    parser.add_argument("--section-max", type=int, default=900)
    parser.add_argument("--para-max", type=int, default=200)
    parser.add_argument("--subhead", type=parse_range, default=(8, 14), help="usual subhead length, e.g. 8-14")
    parser.add_argument("--you-per-k", type=float, default=10.0)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--seed", type=Path,
                        help="the author's verbatim seed: also flag scope wording (no longer, replace, only...) not in it")
    parser.add_argument("--card", action="store_true",
                        help="check a card, outline or other process text: wording rules only, no article-shape checks")
    args = parser.parse_args()

    banned = [] if args.no_default_banned else list(DEFAULT_BANNED)
    if args.banned_file:
        for raw in args.banned_file.read_text(encoding="utf-8").splitlines():
            word = raw.strip()
            if word and not word.startswith("#"):
                banned.append(word)
    if args.rules:
        print(RULES_TEXT.format(banned="\u3001".join(banned), meta="\u3001".join(META_PHRASES)))
        return 0
    if args.draft is None:
        parser.error("a draft path is required unless --rules is given")
    text = args.draft.read_text(encoding="utf-8")
    report = audit(text, banned, args.length, args.hard_max, args.section_min,
                   args.section_max, args.you_per_k, args.para_max, args.subhead, card=args.card)
    seed_flags = 0
    if args.seed:
        extra = seed_scope_findings(text, args.seed.read_text(encoding="utf-8"))
        report["findings"].extend(extra)
        report["counts"]["fix"] += len(extra)
        seed_flags = len(extra)
        report["counts"]["seed_flags"] = seed_flags
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        stats = report["stats"]
        print(f"body characters: {stats['body_characters']}  paragraphs: {stats['paragraphs']}  "
              f"second person: {stats['second_person']}")
        for section in stats["sections"]:
            print(f"  section {section['characters']:>5}  {section['title']}")
        counts = report["counts"]
        print(f"blockers: {counts['blocker']}  fixes: {counts['fix']}  warnings: {counts['warn']}"
              + (f"  seed flags: {counts['seed_flags']}" if "seed_flags" in counts else ""))
        for finding in report["findings"]:
            where = f"L{finding['line']}" if finding["line"] else "--"
            print(f"[{finding['level']}] {where} {finding['rule']}: {finding['detail']}")
    if report["counts"]["blocker"]:
        return 1
    # 2: scope wording the seed does not use. Not a pass: every flag goes to the author first.
    return 2 if seed_flags else 0


if __name__ == "__main__":
    raise SystemExit(main())
