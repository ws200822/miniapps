#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成音乐播放器的 PWA 图标。
风格跟随 music1.html：近黑底 + 冷白前景，无彩色、无描边。
图形为连梁八分音符（♫），整体轻微倾斜，避免呆板。
"""
import os
from PIL import Image, ImageDraw

SS = 1024
BG_TOP, BG_BOT = (0x16, 0x16, 0x1a), (0x0a, 0x0a, 0x0b)
FG = (0xec, 0xec, 0xef)
TILT = 8          # 逆时针倾斜角度


def lerp(a, b, t):
    return tuple(int(round(a[i] + (b[i] - a[i]) * t)) for i in range(3))


def background():
    img = Image.new('RGB', (SS, SS), BG_BOT)
    d = ImageDraw.Draw(img)
    for y in range(SS):
        d.line([(0, y), (SS, y)], fill=lerp(BG_TOP, BG_BOT, y / (SS - 1)))
    return img


def glyph():
    """在透明层上画音符，便于整体旋转"""
    layer = Image.new('RGBA', (SS, SS), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    c = FG + (255,)

    rx, ry = 122, 94                      # 椭圆音符头半径（略扁）
    h1 = (372, 726)                       # 左音符头
    h2 = (752, 636)                       # 右音符头
    sw = 36                               # 符干宽度

    # 符干：贴在音符头右侧，向上延伸
    s1x = h1[0] + rx - sw
    s2x = h2[0] + rx - sw
    beam_l, beam_r = s1x, s2x + sw        # 连梁左右边界
    top1, top2 = 266, 190                 # 连梁在两侧的上沿高度
    bt = 68                               # 连梁厚度

    d.rectangle([s1x, top1 + bt - 10, s1x + sw, h1[1]], fill=c)
    d.rectangle([s2x, top2 + bt - 10, s2x + sw, h2[1]], fill=c)

    # 连梁：从左到右微微上扬的梯形
    d.polygon([(beam_l, top1), (beam_r, top2),
               (beam_r, top2 + bt), (beam_l, top1 + bt)], fill=c)

    # 音符头压在符干上
    for (cx, cy) in (h1, h2):
        d.ellipse([cx - rx, cy - ry, cx + rx, cy + ry], fill=c)

    return layer.rotate(TILT, resample=Image.BICUBIC, center=(SS / 2, SS / 2))


def main():
    out = os.path.dirname(os.path.abspath(__file__))

    g = glyph()
    g = g.crop(g.getbbox())                       # 去掉透明边，拿到真实包围盒
    scale = (SS * 0.70) / max(g.size)             # 长边占画幅 70%
    g = g.resize((int(g.width * scale), int(g.height * scale)), Image.LANCZOS)

    img = background()
    img.paste(g, ((SS - g.width) // 2, (SS - g.height) // 2), g)   # 居中

    for name, size in [('apple-touch-icon.png', 180), ('icon-192.png', 192),
                       ('icon-512.png', 512), ('icon-1024.png', 1024)]:
        img.resize((size, size), Image.LANCZOS).save(os.path.join(out, name), 'PNG', optimize=True)
        print('  wrote %-24s %dx%d' % (name, size, size))

    img.resize((256, 256), Image.LANCZOS).save(os.path.join(out, 'icon-preview.png'), 'PNG')


if __name__ == '__main__':
    main()
