#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成小账本的 PWA 图标。
风格跟随 ledger/index.html 的 tint：系统蓝渐变底 + 纯白 ¥。
¥ 用几何线段拼，不用字体（环境里没有可用 TTF，且几何线更统一）。
4x 超采样后降采样，得到干净的抗锯齿边缘。
"""
import os
from PIL import Image, ImageDraw

SS = 4096                     # 超采样画布
TOP = (0x4C, 0xA8, 0xFF)      # 顶部亮蓝
BOT = (0x00, 0x4E, 0xD6)      # 底部深蓝
FG = (0xFF, 0xFF, 0xFF)
OUT = os.path.dirname(os.path.abspath(__file__))

U = SS / 1024.0               # 以 1024 设计稿为基准的单位


def lerp(a, b, t):
    return tuple(int(round(a[i] + (b[i] - a[i]) * t)) for i in range(3))


def background():
    img = Image.new('RGB', (SS, SS), BOT)
    d = ImageDraw.Draw(img)
    for y in range(SS):
        t = (y / (SS - 1)) ** 0.88
        d.line([(0, y), (SS, y)], fill=lerp(TOP, BOT, t))
    # 顶部内高光：Apple 图标的受光面
    glow = Image.new('L', (1, SS), 0)
    gh = int(SS * 0.46)
    for y in range(gh):
        glow.putpixel((0, y), int(56 * (1 - y / gh) ** 1.6))
    glow = glow.resize((SS, gh))
    img.paste(Image.new('RGB', (SS, gh), (255, 255, 255)), (0, 0), glow)
    return img


def rline(d, p1, p2, w, color):
    """带圆头的粗线段"""
    d.line([p1, p2], fill=color, width=int(w))
    r = w / 2.0
    for p in (p1, p2):
        d.ellipse([p[0] - r, p[1] - r, p[0] + r, p[1] + r], fill=color)


def glyph(img):
    """几何 ¥：V 形 + 竖干 + 两道横杠"""
    layer = Image.new('RGBA', (SS, SS), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    c = FG + (255,)
    cx = 512 * U
    w = 66 * U

    y_top = 250 * U          # V 的起笔
    y_mid = 470 * U          # V 的交点
    y_bot = 770 * U          # 竖干收笔
    dx = 175 * U             # V 的横向半宽
    bar_x = 215 * U          # 横杠半长
    bar1, bar2 = 596 * U, 684 * U

    rline(d, (cx - dx, y_top), (cx, y_mid), w, c)
    rline(d, (cx + dx, y_top), (cx, y_mid), w, c)
    rline(d, (cx, y_mid - 6 * U), (cx, y_bot), w, c)
    rline(d, (cx - bar_x, bar1), (cx + bar_x, bar1), w, c)
    rline(d, (cx - bar_x, bar2), (cx + bar_x, bar2), w, c)

    # 竖干顶端与 V 的接缝补一块，避免细缝
    d.ellipse([cx - w / 2, y_mid - w / 2, cx + w / 2, y_mid + w / 2], fill=c)
    return layer


def main():
    base = background().convert('RGBA')
    base.alpha_composite(glyph(base))
    img = base.convert('RGB')

    sizes = [('icon-1024.png', 1024), ('icon-512.png', 512),
             ('icon-192.png', 192), ('apple-touch-icon.png', 180)]
    for name, s in sizes:
        img.resize((s, s), Image.LANCZOS).save(os.path.join(OUT, name),
                                               optimize=True)
        print('wrote', name, s)


if __name__ == '__main__':
    main()
