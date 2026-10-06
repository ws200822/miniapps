# 歌单搜索代理

## 为什么需要

网易云的歌单搜索接口 `https://music.163.com/api/search/get/web?s=关键词&type=1000`
能正常返回歌单数据，但它：

- **不返回 `Access-Control-Allow-Origin`** → 浏览器 fetch 被同源策略拦掉
- **不支持 JSONP** → 没法用 `<script>` 绕过

所以只能由一台服务器帮你转发。App 里的「歌单搜索代理」就是填这台服务器的地址。

> 不配代理也不影响使用：歌单依然可以用**链接或 ID** 打开，只是不能用关键词搜。

## 填法

App → 右上角齿轮 →「歌单搜索代理」，填：

```
<代理地址>?url=
```

App 会把目标地址 URL 编码后拼在后面，例如实际请求：

```
https://你的代理/?url=https%3A%2F%2Fmusic.163.com%2Fapi%2Fsearch%2Fget%2Fweb%3Fs%3D...
```

## 选哪个平台

从你的网络实测过的结果：

| 平台 | 域名 | 你的网络 |
|---|---|---|
| Cloudflare Workers | `*.workers.dev` | ❌ DNS 被污染（解析到 Facebook 段） |
| Vercel | `*.vercel.app` | ❌ 不通 |
| **Cloudflare Pages** | `*.pages.dev` | ✅ 可达 |
| **Netlify** | `*.netlify.app` | ✅ 可达 |
| GitHub Pages | `*.github.io` | ✅ 可达，但只能托管静态文件，跑不了代理 |

仓库里两个平台的函数代码都写好了，**任选一个**部署即可。

## 方案 A：Cloudflare Pages（推荐）

函数文件：`functions/netease-proxy.js`

1. 打开 https://dash.cloudflare.com → 注册/登录（免费，不要信用卡）
2. 左侧 **Workers & Pages** → **Create** → **Pages** → **Connect to Git**
3. 授权 GitHub，选 `miniapps` 仓库
4. 构建设置全部留空：
   - Build command：**留空**
   - Build output directory：**`/`**
5. **Save and Deploy**，等一分钟
6. 得到 `https://<项目名>.pages.dev`

填进 App 的代理地址：

```
https://<项目名>.pages.dev/netease-proxy?url=
```

## 方案 B：Netlify

函数文件：`netlify/functions/netease-proxy.js`

1. 打开 https://app.netlify.com → 注册/登录
2. **Add new site** → **Import an existing project** → GitHub → 选 `miniapps`
3. 构建设置：
   - Build command：**留空**
   - Publish directory：**`/`**
   - Functions directory：默认 `netlify/functions`，不用改
4. **Deploy**
5. 得到 `https://<站点名>.netlify.app`

填进 App 的代理地址：

```
https://<站点名>.netlify.app/.netlify/functions/netease-proxy?url=
```

## 自检

部署完在浏览器直接访问（把目标地址整段编码后拼上）：

```
https://<你的代理>?url=https%3A%2F%2Fmusic.163.com%2Fapi%2Fsearch%2Fget%2Fweb%3Fs%3Djay%26type%3D1000%26limit%3D2
```

看到 `{"result":{"playlists":[...]}}` 就成功了。如果报 `only music.163.com is allowed`，
说明 URL 没编码对。

## 安全说明

函数里限制了**只能转发 `music.163.com`**，不会被别人当开放代理刷。
如果还想更严，可以把 `ALLOW` 收窄成具体的接口路径。
