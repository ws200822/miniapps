/* ============================================================
   Cloudflare Pages 高级模式 Worker（_worker.js）
   一个文件干两件事：
     1. /netease-proxy  → 网易云歌单搜索的 CORS 代理
     2. 其余请求        → 交给静态资源（env.ASSETS）
   用高级模式而不是 functions/ 目录，是因为直传部署时
   Pages 不会在线编译 functions/，必须走 _worker.js 这条路。
   ============================================================ */

const ALLOW = /(^|\.)music\.163\.com$/;

const CORS = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Methods': 'GET, OPTIONS',
  'Access-Control-Allow-Headers': '*',
};

function json(status, obj) {
  return new Response(JSON.stringify(obj), {
    status: status,
    headers: Object.assign({}, CORS, {
      'Content-Type': 'application/json; charset=utf-8',
    }),
  });
}

async function proxy(request) {
  const target = new URL(request.url).searchParams.get('url');
  if (!target) return json(400, { error: 'missing ?url=' });

  let u;
  try {
    u = new URL(target);
  } catch (e) {
    return json(400, { error: 'bad url' });
  }

  // 只放行网易云，避免被当成任意网站的开放代理
  if (u.protocol !== 'https:' || !ALLOW.test(u.hostname)) {
    return json(403, { error: 'only music.163.com is allowed' });
  }

  const res = await fetch(u.toString(), {
    headers: {
      'Referer': 'https://music.163.com/',
      'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) ' +
                    'AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 ' +
                    'Mobile/15E148 Safari/604.1',
      'Accept': 'application/json, text/plain, */*',
    },
    cf: { cacheTtl: 300, cacheEverything: true },
  });

  const body = await res.text();
  return new Response(body, {
    status: res.status,
    headers: Object.assign({}, CORS, {
      'Content-Type': 'application/json; charset=utf-8',
      'Cache-Control': 'public, max-age=300',
    }),
  });
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);

    if (url.pathname === '/netease-proxy') {
      if (request.method === 'OPTIONS') return new Response(null, { headers: CORS });
      if (request.method !== 'GET') return json(405, { error: 'method not allowed' });
      try {
        return await proxy(request);
      } catch (e) {
        return json(502, { error: 'upstream failed', detail: String(e) });
      }
    }

    return env.ASSETS.fetch(request);
  },
};
