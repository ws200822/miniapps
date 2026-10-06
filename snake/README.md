# 贪吃蛇（PWA 单文件小程序）

手机优先的 Canvas 贪吃蛇，可离线游玩，可添加到 iOS 主屏幕。

## 文件说明

| 文件 | 作用 |
|---|---|
| `index.html` | 全部逻辑：布局 + 样式 + 游戏引擎，零依赖 |
| `manifest.webmanifest` | PWA 清单：名称、图标、`display: standalone` |
| `sw.js` | Service Worker：离线缓存 |
| `apple-touch-icon.png` | iOS 主屏图标（180×180，满幅不透明，iOS 自动裁圆角） |
| `icon-192.png` / `icon-512.png` | Android / manifest 图标 |
| `icon-1024.png` | 高清备用（上架、商店素材） |
| `make_icon.py` | 图标生成脚本，改配色后 `python3 make_icon.py` 重新出图 |
| `icon-preview.png` | 预览图，方便快速看效果 |

## 玩法

- 棋盘内**滑动**，或点底部**方向键**转向
- 吃一个 +1 分并提速 3ms（150ms → 最快 70ms/步）
- 最高分存在 `localStorage`，切后台自动暂停
- 电脑上可用方向键 / WASD / 空格暂停调试

棋盘为 20 列 × 自适应行数（14–30 行），按屏幕高度计算，竖屏能充分利用空间。

## 本地预览

```bash
python3 -m http.server 8899
# 打开 http://127.0.0.1:8899/
```

必须走 http 服务，直接双击打开 `file://` 会导致 Service Worker 无法注册。

## 部署到线上（添加到主屏幕的前提）

「添加到主屏幕」只在 **Safari + http(s) 页面** 下可用。任选一个静态托管：

- **GitHub Pages** —— 建仓库 → 上传文件 → Settings → Pages → Source 选分支 → 得到
  `https://<用户名>.github.io/<仓库名>/`
- **Cloudflare Pages** —— 连 Git 仓库或直接上传，国内访问速度通常更好
- **Netlify Drop** —— 拖文件夹上传，最快但需登录才能保留

部署后在 **Safari** 打开那个网址 → 底部分享按钮 → **添加到主屏幕**。

## 更新代码后怎么生效

- **HTML** 走 network-first，联网刷新即见新版，无需改动
- **图标 / 清单** 走 cache-first；若这些改了，把 `sw.js` 里的 `VERSION` 从 `v1` 改成 `v2`，
  用户下次打开旧缓存会被清掉

## 注意

- iOS 主屏 Web App 的存储（localStorage）与 Safari **相互独立**，分数不会互通
- 想改配色：搜 `:root` 里的 CSS 变量，`--accent` / `--accent2` / `--bg` / `--panel`
