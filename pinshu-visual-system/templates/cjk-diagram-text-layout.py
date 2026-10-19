# -*- coding: utf-8 -*-
"""中文正文图（架构图 / 机制图 / 时间轴）的起步模板 —— 复制后改内容，别从零写。

为什么必须有换行：Pillow 的 `draw.text` 不换行，一行画多长就画多长。把 24 个
20px 汉字直接画进 416px 宽的栏里，文字会越出栏外、被相邻色块盖住，成品上表现为
邻栏边缘露出的半截字。只看整图往往看不出来，必须按区域放大看局部。

四条硬规则（都是踩过的）：
  1. 先测宽再落字：用 draw.textlength 逐字试宽，超宽就换行。
  2. ASCII 串不可拆：`#00FF00`、`cubic-bezier(0.34, 1.56, ...)`、`HyperFrames`
     这类拉丁/数字串必须整块换行，拆开会变成 `#00F` / `F00)`。
  3. 续行行首不放收尾标点：`，。；：、）】` 不能出现在行首，遇到就把它拉回上一行。
  4. 流程箭头按标签实测边界画：节点文字和箭头共用视觉中心线，箭头从前一标签右缘
     到后一标签左缘，分别留出固定空隙；禁止用 `x + 110` 一类固定偏移猜位置。

配套做法：
  - 项目符号用悬挂缩进（续行留出符号宽度），别让第二行顶到最左。
  - 每块内容用固定左边距 + 实测右边界；不要用「大致够宽」估。
  - 渲染完按区域放大看每一栏的右边缘和底部横条，确认没有越界和孤立标点。
  - 图是确定性图形：保留本脚本作可编辑源，另存脚本哈希与成图哈希的渲染回执。
"""
import os
from PIL import Image, ImageDraw, ImageFont

# ---- 改成你的输出目录；字体走系统黑体，粗体用于标题、细体用于正文 ----
OUT = "/绝对路径/配图重绘目录"
FONT_BOLD = "/System/Library/Fonts/STHeiti Medium.ttc"
FONT_LIGHT = "/System/Library/Fonts/STHeiti Light.ttc"

NO_LINE_START = "，。；：、）】》!?,.;:)]}"   # 不能出现在行首
NO_LINE_END = "（【《([{"                    # 不能出现在行尾


def text_w(draw, s, font):
    return draw.textlength(s, font=font)


def _tokens(s):
    """切分原子单元：拉丁/数字/符号连成一个不可拆的块，中文按字切。"""
    units, buf = [], ""
    for ch in s:
        if ch.isascii() and not ch.isspace():
            buf += ch
        else:
            if buf:
                units.append(buf)
                buf = ""
            units.append(ch)
    if buf:
        units.append(buf)
    return units


def wrap(draw, s, font, max_w, indent="   "):
    """按实测宽度换行：ASCII 块不拆、续行悬挂缩进、行首不留收尾标点。"""
    lines, cur = [], ""
    for unit in _tokens(s):
        trial = cur + unit
        if text_w(draw, trial, font) > max_w and cur:
            if unit and unit[0] in NO_LINE_START:
                cur = trial          # 标点跟回上一行，宁可略超宽
                continue
            if cur and cur[-1] in NO_LINE_END:
                lines.append(cur[:-1])
                cur = indent + cur[-1] + unit
            else:
                lines.append(cur)
                cur = indent + unit
        else:
            cur = trial
    if cur:
        lines.append(cur)
    return lines


def draw_par(draw, x, y, s, font, color, max_w, line_h, indent="   "):
    """画一段会自适应的正文，返回下一段的起始 y。"""
    for ln in wrap(draw, s, font, max_w, indent):
        draw.text((x, y), ln, fill=color, font=font)
        y += line_h
    return y


def draw_bullet(draw, x, y, bullet, body, font, color, max_w, line_h):
    """项目符号 + 悬挂缩进的正文，返回下一条的起始 y。"""
    label_w = text_w(draw, bullet, font)
    lines = wrap(draw, body, font, max_w - label_w)
    draw.text((x, y), bullet, fill=color, font=font)
    for ln in lines:
        draw.text((x + label_w, y), ln, fill=color, font=font)
        y += line_h
    return y


def draw_flow_row(draw, centers, labels, center_y, font, text_color, arrow_color,
                  label_gap=28, head_len=18, head_half_h=10, line_w=4):
    """画同一中心线上的流程节点与箭头；箭头端点按相邻标签的实测宽度计算。"""
    if len(centers) != len(labels):
        raise ValueError("centers and labels must have the same length")
    for x, label in zip(centers, labels):
        draw.text((x, center_y), label, font=font, fill=text_color, anchor="mm")
    for i in range(len(labels) - 1):
        current_w = draw.textbbox((0, 0), labels[i], font=font)[2]
        next_w = draw.textbbox((0, 0), labels[i + 1], font=font)[2]
        start_x = centers[i] + current_w / 2 + label_gap
        tip_x = centers[i + 1] - next_w / 2 - label_gap
        if tip_x - head_len <= start_x:
            raise ValueError("labels are too close for a readable connector")
        draw.line((start_x, center_y, tip_x - head_len, center_y),
                  fill=arrow_color, width=line_w)
        draw.polygon([
            (tip_x, center_y),
            (tip_x - head_len, center_y - head_half_h),
            (tip_x - head_len, center_y + head_half_h),
        ], fill=arrow_color)


def render():
    width, margin = 1080, 48          # 公众号正文图常用宽；导出后再按需缩放
    card_pad = 20
    f_title = ImageFont.truetype(FONT_BOLD, 36)
    f_body = ImageFont.truetype(FONT_LIGHT, 20)
    text_max = width - margin * 2 - card_pad * 2   # 每一栏真实可用宽度

    img = Image.new("RGB", (width, 640), (255, 255, 255))
    draw = ImageDraw.Draw(img)

    y = margin
    y = draw_par(draw, margin + card_pad, y, "示例标题：把它换成图要承载的那个判断",
                 f_title, (17, 24, 39), text_max, 44)
    y += 12
    y = draw_bullet(draw, margin + card_pad, y, "◆ ",
                    "示例条目：写清机制而不是复述标题，超宽会自动换行且不会越出右边界",
                    f_body, (55, 65, 81), text_max, 28)
    y = draw_bullet(draw, margin + card_pad, y + 10, "◆ ",
                    "含 ASCII 的条目（#00FF00、cubic-bezier(0.34, 1.56, 0.64, 1)）整块换行不被拆开",
                    f_body, (55, 65, 81), text_max, 28)

    os.makedirs(OUT, exist_ok=True)
    out = os.path.join(OUT, "示例图.png")
    img.save(out, "PNG")
    print("saved:", out, "| 渲染后记得按区域放大看右边缘和底部，确认无越界")


if __name__ == "__main__":
    render()
