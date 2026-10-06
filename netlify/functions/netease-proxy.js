/* ============================================================
   网易云歌单搜索 CORS 代理 —— Netlify Functions（v1 写法，零配置）

   为什么需要它：
   网易云的歌单搜索接口 https://music.163.com/api/search/get/web
   既不返回 Access-Control-Allow-Origin，也不支持 JSONP，
   浏览器直连必被同源策略拦掉。必须有一台服务器帮你转发。

   部署（二选一）：
   A. Netlify 网页端：Site configuration → Functions → 确认
      Functions directory 为 netlify/functions（默认值，通常不用改）。
      仓库里本文件路径必须是：netlify/functions/netease-proxy.js
   B. 已经连好 Git 仓库的，push 后自动部署。

   部署完成后把这段填进 App 的设置 →「歌单搜索代理」：
      https://<你的站点>.netlify.app/.netlify/functions/netease-proxy?url=
   ============================================================ */

const ALLOW = /(^|\.)music\.163\.com$/;

const CORS = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Methods': 'GET, OPTIONS',
  'Access-Control-Allow-Headers': '*',
};

function reply(statusCode, body, extra) {
  return {
    statusCode: statusCode,
    headers: Object.assign({}, CORS, {
      'Content-Type': 'application/json; charset=utf-8',
      'Cache-Control': 'public, max-age=300',
    }, extra || {}),
    body: body,
  };
}

exports.handler = async function (event) {
  if (event.httpMethod === 'OPTIONS') {
    return { statusCode: 204, headers: CORS, body: '' };
  }
  if (event.httpMethod !== 'GET') {
    return reply(405, JSON.stringify({ error: 'method not allowed' }));
  }

  const q = event.queryStringParameters || {};
  const target = q.url;
  if (!target) {
    return reply(400, JSON.stringify({ error: 'missing ?url=' }));
  }

  let u;
  try {
    u = new URL(target);
  } catch (e) {
    return reply(400, JSON.stringify({ error: 'bad url' }));
  }

  // 只放行网易云，避免被当成任意网站的开放代理
  if (u.protocol !== 'https:' || !ALLOW.test(u.hostname)) {
    return reply(403, JSON.stringify({ error: 'only music.163.com is allowed' }));
  }

  try {
    const res = await fetch(u.toString(), {
      headers: {
        'Referer': 'https://music.163.com/',
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) ' +
                      'AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 ' +
                      'Mobile/15E148 Safari/604.1',
        'Accept': 'application/json, text/plain, */*',
      },
    });
    const body = await res.text();
    return reply(res.status, body);
  } catch (e) {
    return reply(502, JSON.stringify({ error: 'upstream failed', detail: String(e) }));
  }
};
