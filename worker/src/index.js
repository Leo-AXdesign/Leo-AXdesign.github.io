/**
 * 디자인 허브 — 댓글 서버 (Cloudflare Worker + D1)
 *
 * 방문자는 로그인 없이 이름과 내용만 적어 글을 남깁니다.
 * 주소는 /comments 하나이고, 메서드로 동작이 갈립니다.
 *
 *   GET    /comments?page=talk        글 목록
 *   POST   /comments                  글 남기기  {page, name, body, pw, website, elapsed}
 *   DELETE /comments?id=12            글 지우기  {pw} 또는 Authorization: Bearer <ADMIN_TOKEN>
 *
 * 글쓴이가 정한 비밀번호(4~12자)로 자기 글을 지울 수 있습니다.
 * 비밀번호는 그대로 두지 않고, 글마다 다른 소금과 IP_SALT 를 섞어 해시로만 저장합니다.
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
const PW_MIN = 4;
const PW_MAX = 12;
const TRY_LIMIT = 20;            // 한 시간에 비밀번호를 틀릴 수 있는 횟수
const TRY_WINDOW_MS = 3600000;

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

async function sha256(text) {
  const buf = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(text));
  return [...new Uint8Array(buf)].map(b => b.toString(16).padStart(2, "0")).join("");
}

/** 비밀번호를 "소금$해시" 꼴로 만듭니다. 소금은 글마다 다릅니다. */
async function makePw(pw, env) {
  const salt = crypto.randomUUID().replace(/-/g, "").slice(0, 16);
  return salt + "$" + await sha256((env.IP_SALT || "designrefs") + ":" + salt + ":" + pw);
}

/** 저장해 둔 값과 입력한 비밀번호가 맞는지 봅니다. */
async function checkPw(pw, stored, env) {
  if (!stored || !stored.includes("$")) return false;
  const [salt, hash] = stored.split("$");
  const made = await sha256((env.IP_SALT || "designrefs") + ":" + salt + ":" + pw);
  // 길이가 같을 때 한 글자씩 비교해, 맞는 자리 수로 정답을 좁히지 못하게 합니다
  if (made.length !== hash.length) return false;
  let diff = 0;
  for (let i = 0; i < made.length; i++) diff |= made.charCodeAt(i) ^ hash.charCodeAt(i);
  return diff === 0;
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
  const pw = String(data.pw == null ? "" : data.pw).trim();
  const elapsed = Number(data.elapsed) || 0;

  if (!name) return json({ ok: false, error: "이름을 적어 주세요." }, 400, origin);
  if (body.length < 2) return json({ ok: false, error: "내용을 적어 주세요." }, 400, origin);
  if (pw.length < PW_MIN || pw.length > PW_MAX)
    return json({ ok: false, error: `비밀번호는 ${PW_MIN}~${PW_MAX}자로 적어 주세요.` }, 400, origin);
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
    "INSERT INTO comments (page, name, body, at, who, pw, hidden) VALUES (?1, ?2, ?3, ?4, ?5, ?6, ?7)"
  ).bind(page, name, body, now, who, await makePw(pw, env), hidden).run();

  return json({
    ok: true,
    pending: hidden === 1,
    item: hidden === 1 ? null : { id: res.meta.last_row_id, name, body, at: now },
  }, 200, origin);
}

async function remove(req, env, url, origin) {
  const id = Number(url.searchParams.get("id"));
  if (!id) return json({ ok: false, error: "지울 글 번호가 없습니다." }, 400, origin);

  // 운영자는 비밀번호 없이 지웁니다
  const token = (req.headers.get("Authorization") || "").replace(/^Bearer\s+/i, "");
  if (env.ADMIN_TOKEN && token === env.ADMIN_TOKEN) {
    await env.DB.prepare("DELETE FROM comments WHERE id = ?1").bind(id).run();
    return json({ ok: true }, 200, origin);
  }

  let pw = "";
  try { pw = String(((await req.json()) || {}).pw || "").trim(); } catch { /* 본문 없음 */ }
  if (!pw) return json({ ok: false, error: "비밀번호를 적어 주세요." }, 400, origin);

  // 찍어서 맞히지 못하도록, 틀린 횟수가 많으면 한동안 막습니다
  const who = await idOf(req, env);
  const now = Date.now();
  await env.DB.prepare("DELETE FROM tries WHERE at < ?1").bind(now - TRY_WINDOW_MS).run();
  const tries = await env.DB.prepare(
    "SELECT COUNT(*) AS n FROM tries WHERE who = ?1 AND at > ?2"
  ).bind(who, now - TRY_WINDOW_MS).first();
  if (tries && tries.n >= TRY_LIMIT)
    return json({ ok: false, error: "비밀번호를 여러 번 틀렸습니다. 한 시간 뒤에 다시 해 주세요." }, 429, origin);

  const row = await env.DB.prepare("SELECT pw FROM comments WHERE id = ?1").bind(id).first();
  if (!row) return json({ ok: false, error: "이미 지워진 글입니다." }, 404, origin);
  if (!row.pw)
    return json({ ok: false, error: "비밀번호가 없는 글입니다. 운영자에게 알려 주세요." }, 400, origin);

  if (!await checkPw(pw, row.pw, env)) {
    await env.DB.prepare("INSERT INTO tries (who, at) VALUES (?1, ?2)").bind(who, now).run();
    return json({ ok: false, error: "비밀번호가 맞지 않습니다." }, 403, origin);
  }
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
