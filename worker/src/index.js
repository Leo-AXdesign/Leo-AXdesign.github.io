/**
 * 디자인 허브 — 댓글 서버 (Cloudflare Worker + D1)
 *
 * 방문자는 로그인 없이 이름과 내용만 적어 글을 남깁니다.
 * 주소는 /comments 하나이고, 메서드로 동작이 갈립니다.
 *
 *   GET    /comments?page=talk        글 목록
 *   POST   /comments                  글 남기기  {page, name, body, website, elapsed}
 *   DELETE /comments?id=12            글 지우기  (Authorization: Bearer <ADMIN_TOKEN>)
 *
 * 스팸은 네 겹으로 거릅니다: 숨은 입력칸(봇만 채움), 작성 시간, 링크 개수, 같은 사람 연속 작성 제한.
 * 접속 IP 는 그대로 두지 않고 해시로 바꿔 저장합니다.
 */

const MAX_NAME = 20;
const MAX_BODY = 1000;
const MIN_ELAPSED_MS = 3000;     // 페이지를 열고 3초 안에 보내면 봇으로 봅니다
const COOLDOWN_MS = 30 * 1000;   // 같은 사람은 30초에 한 번
const DAILY_LIMIT = 10;          // 같은 사람 하루 10개
const MAX_LINKS = 2;

function cors(origin) {
  return {
    "Access-Control-Allow-Origin": origin,
    "Access-Control-Allow-Methods": "GET, POST, DELETE, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type, Authorization",
    "Access-Control-Max-Age": "86400",
    "Vary": "Origin",
  };
}

function json(data, status, origin) {
  return new Response(JSON.stringify(data), {
    status,
    headers: { "Content-Type": "application/json; charset=utf-8", ...cors(origin) },
  });
}

/** 허용한 주소에서 온 요청인지 봅니다. 로컬 확인용 주소도 열어 둡니다. */
function pickOrigin(req, env) {
  const origin = req.headers.get("Origin") || "";
  const list = (env.ALLOW_ORIGIN || "").split(",").map(s => s.trim()).filter(Boolean);
  if (list.includes(origin)) return origin;
  if (/^http:\/\/localhost(:\d+)?$/.test(origin)) return origin;
  return list[0] || "https://designrefs.com";
}

/** IP 를 그대로 저장하지 않기 위해 소금을 섞어 해시로 바꿉니다. */
async function idOf(req, env) {
  const raw = (req.headers.get("CF-Connecting-IP") || "0.0.0.0") + "|" + (env.IP_SALT || "designrefs");
  const buf = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(raw));
  return [...new Uint8Array(buf)].slice(0, 8).map(b => b.toString(16).padStart(2, "0")).join("");
}

function clean(s, max) {
  return String(s == null ? "" : s)
    .replace(/[\u0000-\u0008\u000B\u000C\u000E-\u001F]/g, "")  // 보이지 않는 제어문자 제거
    .replace(/\r\n/g, "\n")
    .replace(/\n{3,}/g, "\n\n")
    .trim()
    .slice(0, max);
}

async function list(env, page, origin) {
  const { results } = await env.DB.prepare(
    "SELECT id, name, body, at FROM comments WHERE page = ?1 AND hidden = 0 ORDER BY id ASC LIMIT 300"
  ).bind(page).all();
  return json({ ok: true, items: results || [] }, 200, origin);
}

async function create(req, env, origin) {
  let data;
  try { data = await req.json(); }
  catch { return json({ ok: false, error: "내용을 읽지 못했습니다." }, 400, origin); }

  // 숨은 입력칸은 사람 눈에 보이지 않습니다. 채워져 있으면 봇입니다.
  // 봇이 실패를 알아채고 다시 시도하지 않도록 성공한 척 돌려보냅니다.
  if (clean(data.website, 50)) return json({ ok: true, items: null }, 200, origin);

  const page = clean(data.page, 60) || "talk";
  const name = clean(data.name, MAX_NAME);
  const body = clean(data.body, MAX_BODY);
  const elapsed = Number(data.elapsed) || 0;

  if (!name) return json({ ok: false, error: "이름을 적어 주세요." }, 400, origin);
  if (body.length < 2) return json({ ok: false, error: "내용을 적어 주세요." }, 400, origin);
  if (elapsed < MIN_ELAPSED_MS) return json({ ok: false, error: "조금만 천천히 보내 주세요." }, 429, origin);
  if ((body.match(/https?:\/\//gi) || []).length > MAX_LINKS)
    return json({ ok: false, error: "링크는 두 개까지 넣을 수 있습니다." }, 400, origin);

  const who = await idOf(req, env);
  const now = Date.now();
  const last = await env.DB.prepare(
    "SELECT at FROM comments WHERE who = ?1 ORDER BY id DESC LIMIT 1"
  ).bind(who).first();
  if (last && now - last.at < COOLDOWN_MS)
    return json({ ok: false, error: "조금 뒤에 다시 남겨 주세요." }, 429, origin);

  const day = await env.DB.prepare(
    "SELECT COUNT(*) AS n FROM comments WHERE who = ?1 AND at > ?2"
  ).bind(who, now - 86400000).first();
  if (day && day.n >= DAILY_LIMIT)
    return json({ ok: false, error: "오늘은 여기까지 남길 수 있습니다." }, 429, origin);

  const hidden = env.MODERATE === "1" ? 1 : 0;
  const res = await env.DB.prepare(
    "INSERT INTO comments (page, name, body, at, who, hidden) VALUES (?1, ?2, ?3, ?4, ?5, ?6)"
  ).bind(page, name, body, now, who, hidden).run();

  return json({
    ok: true,
    pending: hidden === 1,
    item: hidden === 1 ? null : { id: res.meta.last_row_id, name, body, at: now },
  }, 200, origin);
}

async function remove(req, env, url, origin) {
  const token = (req.headers.get("Authorization") || "").replace(/^Bearer\s+/i, "");
  if (!env.ADMIN_TOKEN || token !== env.ADMIN_TOKEN)
    return json({ ok: false, error: "권한이 없습니다." }, 401, origin);
  const id = Number(url.searchParams.get("id"));
  if (!id) return json({ ok: false, error: "지울 글 번호가 없습니다." }, 400, origin);
  await env.DB.prepare("DELETE FROM comments WHERE id = ?1").bind(id).run();
  return json({ ok: true }, 200, origin);
}

export default {
  async fetch(req, env) {
    const url = new URL(req.url);
    const origin = pickOrigin(req, env);

    if (req.method === "OPTIONS") return new Response(null, { status: 204, headers: cors(origin) });
    if (url.pathname !== "/comments")
      return json({ ok: false, error: "없는 주소입니다." }, 404, origin);

    try {
      if (req.method === "GET") return await list(env, clean(url.searchParams.get("page"), 60) || "talk", origin);
      if (req.method === "POST") return await create(req, env, origin);
      if (req.method === "DELETE") return await remove(req, env, url, origin);
    } catch (err) {
      return json({ ok: false, error: "서버에서 처리하지 못했습니다." }, 500, origin);
    }
    return json({ ok: false, error: "허용하지 않는 방식입니다." }, 405, origin);
  },
};
