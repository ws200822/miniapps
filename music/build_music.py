#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
把 netease/music1.html 构建成可部署的 PWA。

源文件保持干净不动，本脚本负责：
  1. 注入 PWA 所需的 meta / link 标签（幂等，重复执行不会叠加）
  2. 注入 Service Worker 注册代码
  3. 重命名为 index.html 输出到 miniapps/music/，让网址是 /music/ 而不是 /music/music1.html

用法: python3 build_music.py
"""
import os
import re
import shutil

SRC = '/var/minis/mounts/Local/netease/music1.html'
OUT = '/var/minis/workspace/deploy/miniapps/music/index.html'

HEAD_TAGS = """<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta name="apple-mobile-web-app-title" content="音乐播放器">
<link rel="manifest" href="./manifest.webmanifest">
<link rel="apple-touch-icon" href="./apple-touch-icon.png">
<link rel="icon" type="image/png" href="./icon-192.png">
"""

SW_REGISTER = """
/* ---------- PWA：离线缓存 ---------- */
/* 只在 http/https 下注册；本地打开文件时自动跳过 */
if ('serviceWorker' in navigator && /^https?:$/.test(location.protocol)) {
  window.addEventListener('load', function () {
    navigator.serviceWorker.register('./sw.js').catch(function () {});
  });
}
"""

MARK_META = '<!-- pwa:meta -->'
MARK_SW = '/* pwa:sw */'


def main():
    html = open(SRC, encoding='utf-8').read()
    before = len(html)

    # ---- 1. head 标签：插在 theme-color 之后 ----
    if MARK_META not in html:
        anchor = '<meta name="theme-color" content="#0a0a0b">'
        if anchor not in html:
            raise SystemExit('找不到 theme-color 锚点，源文件结构可能变了')
        html = html.replace(anchor, anchor + '\n' + MARK_META + '\n' + HEAD_TAGS.rstrip(), 1)
        print('  注入 PWA meta 标签')
    else:
        print('  meta 标签已存在，跳过')

    # ---- 2. SW 注册：插在末尾的 IIFE 收尾之前 ----
    if MARK_SW not in html:
        tail = '})();\n</script>'
        idx = html.rfind(tail)
        if idx == -1:
            raise SystemExit('找不到脚本收尾锚点，源文件结构可能变了')
        html = html[:idx] + SW_REGISTER.strip() + '\n' + MARK_SW + '\n' + html[idx:]
        print('  注入 Service Worker 注册')
    else:
        print('  SW 注册已存在，跳过')

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    open(OUT, 'w', encoding='utf-8').write(html)
    print('  输出 %s  (%d → %d 字节)' % (OUT, before, len(html)))

    # 静态资源就位（脚本与产物同目录，同文件时跳过）
    here = os.path.dirname(os.path.abspath(__file__))
    out_dir = OUT.rsplit('/', 1)[0]
    if os.path.realpath(here) != os.path.realpath(out_dir):
        for f in ('manifest.webmanifest', 'sw.js', 'apple-touch-icon.png',
                  'icon-192.png', 'icon-512.png', 'icon-1024.png'):
            src = os.path.join(here, f)
            if os.path.exists(src):
                shutil.copy2(src, os.path.join(out_dir, f))


if __name__ == '__main__':
    main()
