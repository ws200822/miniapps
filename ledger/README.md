# 小账本

手机优先的记账本，单文件 HTML，零依赖、零后端。数据存在 `localStorage`，不上传任何服务器。

打开：https://ws200822.github.io/miniapps/ledger/

## 功能

- **记账**：底部弹出数字键盘，按分类 chips 选类别，可加备注和日期；点任意流水直接改
- **流水**：按日分组带小计，行左滑 1:1 跟手删除，删错了 toast 里 4 秒内可撤销
- **预算**：设月生活费，概览卡显示本月可用、已用百分比、进度条（蓝→橙→红）
- **统计**：环形预算进度、分类构成排行、近 6 个月收支双柱
- **分类**：默认 10 个支出 + 5 个收入，可增删改，换 42 个 emoji / 10 色板
- **数据**：导出 JSON 备份、导出 CSV（带 BOM，Excel 直接开）、从备份恢复
- **外观**：跟随系统 / 浅色 / 深色；响应 `prefers-reduced-motion` 等无障碍偏好

## 交互实现

动效不是 CSS transition，是手写的弹簧求解器（`k=(2π/response)²`、`c=4πζ/response`，半隐式欧拉双步积分）。默认临界阻尼 ζ=1.0 不过冲；sheet 和甩动类用 ζ≈0.82 带轻微回弹。

左滑删除的手势链：8px 迟滞锁方向 → 1:1 跟手 → 越界橡皮筋 `(o·dim·0.55)/(dim+0.55|o|)` → 释放速度投射 `(v/1000)·0.998/(1−0.998)` 决定吸附点，速度符号优先于位置。

细节见 `DESIGN-NOTES.md`。

## 文件

| 文件 | 说明 |
| --- | --- |
| `index.html` | 全部代码（HTML + CSS + JS），单文件 |
| `manifest.webmanifest` | PWA 清单，可添加到主屏幕 |
| `sw.js` | Service Worker，HTML 走 network-first，静态资源 cache-first |
| `make_icon.py` | 图标生成脚本（Pillow，4x 超采样） |
| `DESIGN-NOTES.md` | 交互与视觉的实现约束清单 |

## 数据

`localStorage` 键名 `xiaozhangben.v2`：

```js
{
  v: 2,
  settings: { budget: 2000, theme: "auto" },
  cats:     [{ id, name, emoji, color, type: "expense" | "income" }],
  records:  [{ id, type, amount, categoryId, note, date: "YYYY-MM-DD", ts }]
}
```

清浏览器缓存会丢数据，重要账目请定期用「我的 → 导出备份」。

## 本地跑

直接双击 `index.html` 即可，没有构建步骤。要试 PWA 的离线能力，起个静态服务器：

```sh
python3 -m http.server 8000
```

重新生成图标：

```sh
python3 make_icon.py   # 需要 Pillow
```
