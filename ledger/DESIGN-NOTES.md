# Apple Design 自查清单（记账 App 专用）

来源：emilkowalski/skills → skills/apple-design/SKILL.md（WWDC《Designing Fluid Interfaces》等）
本地副本：/var/minis/workspace/ledger/skills/apple-design/SKILL.md

## 一、动效硬规则

- [ ] 按压反馈绑定 `pointerdown`，不是 `click`；`:active` 只做兜底
- [ ] 所有手势驱动的位移用 spring，**禁用 CSS transition / @keyframes**（无法中途抓取反向）
- [ ] 默认 spring：`damping 1.0 / response 0.35`（无过冲）
- [ ] 有甩动惯性时：`damping 0.8 / response 0.3`（轻微回弹）
- [ ] 中断时从**当前屏幕值**起算，绝不从目标值起算
- [ ] 手势结束把释放速度**交接到** spring 的 initialVelocity（无缝）
- [ ] 甩动落点用速度投射：`current + (v/1000)·d/(1-d)`，`d = 0.998`
- [ ] 边界用 rubber-band：`(overshoot·dim·0.55)/(dim + 0.55·|overshoot|)`
- [ ] 反向 vs 提交：看速度**符号**决定回弹还是吸附，不看位置
- [ ] 动画只碰 `transform` / `opacity`

## 二、空间一致性

- [ ] 进出的路径一致（sheet 从底部进 → 从底部出）
- [ ] 弹出物锚定触发源（scale 的 transform-origin 指向按钮）
- [ ] 可逆过渡的 easing 镜像

## 三、材质与层次

- [ ] tab bar / nav 用半透明层：`backdrop-filter: blur() saturate(180%)`，内容从其下方滚过
- [ ] **绝不**在浅色半透明面上再叠浅色半透明面
- [ ] 大表面 = 更重模糊 + 更深阴影
- [ ] 模态配 scrim 压暗背景；非阻塞面板只用半透明 + 位移，不加 scrim
- [ ] 滚动边缘用渐变/模糊遮罩，不用 1px 硬分割线
- [ ] 玻璃面进入时 blur 半径 + scale **同步**动画（materialize），不是纯 opacity 淡入

## 四、排版

- [ ] 大字负字距（`letter-spacing: -0.02em`），正文接近 0，绝不用同一个值通吃
- [ ] 行高随字号反向：大标题紧（1.05），正文松（1.5）
- [ ] 层级 = 字重 + 字号 + 行高**组合**，不是只堆字号
- [ ] 间距用 rem/em，尊重 Dynamic Type
- [ ] 系统字体优先（`-apple-system` / `system-ui`）

## 五、无障碍

- [ ] `prefers-reduced-motion: reduce` → 滑动/弹簧降级为短交叉淡入，去掉过冲
- [ ] `prefers-reduced-transparency: reduce` → 半透明面转实色，去 blur
- [ ] `prefers-contrast: more` → 近实色背景 + 明确描边
- [ ] 深色模式：颜色成对定义，不是简单反色

## 六、八项设计原则（决策时用来命名理由）

Purpose（不做无用功能）· Agency（可撤销，销毁才弹确认）· Responsibility（数据在本地，隐私默认安全）· Familiarity（遵循 iOS 既有隐喻）· Flexibility（适配不同用法，可自定义）· Simplicity（不是极简，是清晰）· Craft（每个数值可辩护）· Delight（前七项的结果，不是撒糖）

## 七、触觉/声音

- [ ] 因果明确（在真正发生的那一帧触发）
- [ ] 视觉 / 声音 / 触觉**同一帧**触发
- [ ] 只在成功、错误、提交、吸附这类有意义的时刻给

## 八、记账场景落地映射

| 场景 | 实现 |
| --- | --- |
| 打开记账 | 底部 sheet 弹簧上升，scrim 淡入 + 背景下沉 8% |
| 数字键盘按键 | pointerdown 即时高亮 + scale 0.96，抬起提交 |
| 分类切换 | 选中态弹簧滑动指示条，锚定触发 chip |
| 列表左滑删除 | 1:1 跟手 + rubber-band + 速度投射吸附 |
| 列表项入场 | 逐个 20ms 错峰上浮淡入，transform only |
| 月份切换 | 数字滚动 + 内容交叉淡入，方向与手势一致 |
| 拖拽关闭 sheet | 跟手 + 释放速度决定回弹/关闭，无量级跳变 |
