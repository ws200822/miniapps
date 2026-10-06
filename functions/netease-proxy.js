/* ============================================================
   网易云歌单搜索 CORS 代理 —— Cloudflare Pages Functions

   选它的理由：你的网络实测 workers.dev 被 DNS 污染，
   但 pages.dev 可达（Cloudflare 的另一个域名，没被污染）。

   部署：
   1. Cloudflare 控制台 → Workers & Pages → Create → Pages
      → Connect to Git → 选 miniapps 仓库
   2. 构建设置全部留空（本仓库是纯静态 + 一个函数）：
      Build command:        （留空）
      Build output directory: /
   3. 部署完成后把这段填进 App 设置 →「歌单搜索代理」：
      https://<项目名>.pages.dev/netease-proxy?url=

   注意：函数文件必须放在仓库根目录的 functions/ 下，
   访问路径由文件名决定（functions/netease-proxy.js → /netease-proxy）。
   ============================================================ */

const ALLOW = /(^|\.)music\.163\.com$/;

const CORS = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Methods': 'GET, OPTIONS',
  'Access-Control-Allow-Headers': '*',
};

function reply(status, body) {
  return new Response(body, {
    status: status,
    headers: Object.assign({}, CORS, {
      'Content-Type': 'application/json; charset=utf-8',
      'Cache-Control': 'public, max-age=300',
    }),
  });
}

export function onRequest(context) {
  const req = context.request;

  if (req.method === 'OPTIONS') return new Response(null, { headers: CORS });
  if (req.method !== 'GET') return reply(405, JSON.stringify({ error: 'method not allowed' }));

  const target = new URL(req.url).searchParams.get('url');
  if (!target) return reply(400, JSON.stringify({ error: 'missing ?url=' }));

  let u;
  try {
    u = new URL(target);
  } catch (e) {
    return reply(400, JSON.stringify({ error: 'bad url' }));
  }

  if (u.protocol !== 'https:' || !ALLOW.test(u.hostname)) {
    return reply(403, JSON.stringify({ error: 'only music.163.com is allowed' }));
  }

  return fetch(u.toString(), {
    headers: {
      'Referer': 'https://music.163.com/',
      'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) ' +
                    'AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 ' +
                    'Mobile/15E148 Safari/604.1',
      'Accept': 'application/json, text/plain, */*',
    },
  }).then(function (res) {
    return res.text().then(function (body) {
      return reply(res.status, body);
    });
  }).catch(function (e) {
    return reply(502, JSON.stringify({ error: 'upstream failed', detail: String(e) }));
  });
}
