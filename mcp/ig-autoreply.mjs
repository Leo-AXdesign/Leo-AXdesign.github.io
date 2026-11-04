#!/usr/bin/env node
/**
 * 인스타 댓글 자동 답장 (게시물 하나의 모든 댓글 → 공개 답글 + DM)
 *
 * 켜 둔 게시물의 새 댓글마다
 *   1) 댓글 단 사람에게 DM을 보냅니다 (메타의 '댓글 비공개 답장', 댓글 하나당 한 번만 됩니다)
 *   2) DM이 갔으면 댓글에 공개 답글을 답니다 ("DM으로 보내드렸어요!")
 * 처리한 댓글은 기록해 두고 다시 보내지 않습니다. 내 계정 댓글은 건너뜁니다.
 *
 * 켤 게시물 목록: ~/.designhub/autoreply.json   (Claude 의 ig_autoreply_* 도구가 고칩니다)
 *   { "campaigns": [ { "media_id": "...", "dm": "보낼 DM", "replies": ["공개 답글", ...],
 *                      "until": "2026-11-11T00:00:00+09:00", "paused": false } ] }
 * 처리 기록:       ~/.designhub/autoreply-log.jsonl  (한 줄에 댓글 하나)
 *
 * 실행
 *   node ig-autoreply.mjs            켜 둔 게시물을 한 번 훑고 끝납니다 (launchd 가 5분마다 부릅니다)
 *   node ig-autoreply.mjs --dry-run  보내지 않고 무엇을 보낼지만 보여 줍니다
 *
 * 토큰은 Claude 설정 파일에 있는 designhub 서버의 INSTAGRAM_ACCESS_TOKEN 을 그대로 씁니다.
 * 외부 패키지 없이 Node.js 18 이상만 있으면 됩니다.
 */
import fs from "node:fs";
import os from "node:os";
import path from "node:path";

const IG = "https://graph.instagram.com/v23.0";
const DIR = path.join(os.homedir(), ".designhub");
const CAMPAIGNS = path.join(DIR, "autoreply.json");
const LOG = path.join(DIR, "autoreply-log.jsonl");
const LOCK = path.join(DIR, "autoreply.lock");
const CONFIG = path.join(os.homedir(), "Library/Application Support/Claude/claude_desktop_config.json");
const DRY = process.argv.includes("--dry-run");
const PER_RUN = 20;               // 한 번 돌 때 최대 처리 수 (몰아서 보내지 않게)
const GAP = [8000, 20000];        // 댓글 사이 쉬는 시간(밀리초) 범위
const MAX_AGE = 7 * 24 * 3600e3;  // 메타 규칙: 댓글 7일 안에만 비공개 답장 가능

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const now = () => new Date().toISOString();
const say = (...a) => console.log(new Date().toLocaleString("sv-SE", { timeZone: "Asia/Seoul" }), ...a);

function token() {
  if (process.env.INSTAGRAM_ACCESS_TOKEN) return process.env.INSTAGRAM_ACCESS_TOKEN;
  try {
    const c = JSON.parse(fs.readFileSync(CONFIG, "utf8"));
    for (const s of Object.values(c.mcpServers || {}))
      if ((s.args || []).some((a) => String(a).includes("designhub-social")) && s.env?.INSTAGRAM_ACCESS_TOKEN)
        return s.env.INSTAGRAM_ACCESS_TOKEN;
  } catch {}
  throw new Error("인스타 토큰을 찾지 못했습니다. Claude 설정 파일의 designhub 서버에 INSTAGRAM_ACCESS_TOKEN 이 있어야 합니다.");
}
const TOKEN = token();
const hide = (s) => String(s).split(TOKEN).join("[토큰]");

class MetaError extends Error {
  constructor(e, status) {
    super(hide(`메타 API 오류 ${e.code ?? status}${e.error_subcode ? "/" + e.error_subcode : ""}: ${e.error_user_msg || e.message || status}`));
    this.code = e.code; this.sub = e.error_subcode;
  }
  get permission() { return [10, 200, 3, 190].includes(this.code) || /permission|권한/i.test(this.message); }
}

async function api(method, p, { query = {}, json } = {}) {
  const url = new URL(p.startsWith("http") ? p : IG + p);
  for (const [k, v] of Object.entries(query)) url.searchParams.set(k, v);
  const res = await fetch(url, {
    method,
    headers: { Authorization: `Bearer ${TOKEN}`, ...(json ? { "Content-Type": "application/json" } : {}) },
    ...(json ? { body: JSON.stringify(json) } : {}),
  });
  const data = await res.json().catch(() => ({}));
  if (!res.ok || data.error) throw new MetaError(data.error || {}, res.status);
  return data;
}

// ---------- 파일 ----------
function readCampaigns() {
  try { return JSON.parse(fs.readFileSync(CAMPAIGNS, "utf8")).campaigns || []; } catch { return []; }
}
function readLog() {
  try { return fs.readFileSync(LOG, "utf8").split("\n").filter(Boolean).map((l) => JSON.parse(l)); } catch { return []; }
}
function writeLog(row) {
  fs.mkdirSync(DIR, { recursive: true });
  fs.appendFileSync(LOG, JSON.stringify({ at: now(), ...row }) + "\n");
}

async function allComments(mediaId) {
  const out = [];
  let next = `/${mediaId}/comments`;
  let query = { fields: "id,text,username,timestamp", limit: "50" };
  while (next) {
    const d = await api("GET", next, { query });
    out.push(...(d.data || []));
    next = d.paging?.next || null;
    query = {};
  }
  return out;
}

// ---------- 한 번 훑기 ----------
async function run() {
  const active = readCampaigns().filter((c) => !c.paused && (!c.until || new Date(c.until) > new Date()));
  if (!active.length) return say("켜 둔 게시물이 없습니다.");

  // 이미 끝난 댓글 (DM 보냄, 또는 다시 해도 안 되는 것)
  const done = new Set(readLog().filter((r) => r.status !== "error").map((r) => r.comment_id));
  const me = await api("GET", "/me", { query: { fields: "user_id,username" } });
  let sent = 0;

  for (const c of active) {
    const comments = await allComments(c.media_id);
    const todo = comments.filter((x) => !done.has(x.id)).sort((a, b) => a.timestamp.localeCompare(b.timestamp));
    say(`게시물 ${c.media_id}: 댓글 ${comments.length}개, 새로 처리할 것 ${todo.length}개`);

    for (const x of todo) {
      const base = { media_id: c.media_id, comment_id: x.id, username: x.username };
      if (x.username === me.username) { if (!DRY) writeLog({ ...base, status: "skip", why: "내 댓글" }); continue; }
      if (Date.now() - new Date(x.timestamp) > MAX_AGE) { if (!DRY) writeLog({ ...base, status: "skip", why: "7일 지난 댓글" }); continue; }
      if (sent >= PER_RUN) return say(`이번에는 ${PER_RUN}개까지만 보냈습니다. 나머지는 다음 차례에 보냅니다.`);

      const reply = (c.replies && c.replies.length) ? c.replies[Math.floor(Math.random() * c.replies.length)] : "";
      if (DRY) { say(`[시험] @${x.username} "${(x.text || "").slice(0, 30)}" → DM 보내고 답글 "${reply}"`); sent++; continue; }

      // 1) DM
      try {
        await api("POST", `/${me.user_id}/messages`, { json: { recipient: { comment_id: x.id }, message: { text: c.dm } } });
      } catch (e) {
        if (e.permission) {
          writeLog({ ...base, status: "error", why: e.message });
          say("DM 권한이 없어 멈춥니다:", e.message);
          process.exitCode = 2;
          return;
        }
        // 이미 비공개 답장을 보낸 댓글 등: 다시 해도 안 되니 끝난 것으로 적습니다
        writeLog({ ...base, status: "skip", why: e.message });
        say(`@${x.username} DM 실패(건너뜀):`, e.message);
        continue;
      }
      // 2) 공개 답글 (DM이 간 뒤에만)
      let replyErr = "";
      if (reply) {
        try { await api("POST", `/${x.id}/replies`, { query: { message: reply } }); }
        catch (e) { replyErr = e.message; }
      }
      writeLog({ ...base, status: "sent", reply, ...(replyErr ? { reply_error: replyErr } : {}) });
      say(`@${x.username} DM 보냄${reply ? (replyErr ? ", 답글 실패: " + replyErr : ", 답글 담") : ""}`);
      sent++;
      await sleep(GAP[0] + Math.random() * (GAP[1] - GAP[0]));
    }
  }
  say(`끝. 이번에 ${DRY ? "보낼" : "보낸"} DM ${sent}개`);
}

// 같은 때에 두 번 돌지 않게 (10분 넘은 잠금은 끊긴 것으로 봅니다)
function lock() {
  try {
    const st = fs.statSync(LOCK);
    if (Date.now() - st.mtimeMs < 10 * 60e3) { say("이미 도는 중이라 건너뜁니다."); return false; }
  } catch {}
  fs.mkdirSync(DIR, { recursive: true });
  fs.writeFileSync(LOCK, String(process.pid));
  return true;
}

if (lock()) {
  try { await run(); }
  catch (e) { say("오류:", hide(e.message)); process.exitCode = 1; }
  finally { fs.rmSync(LOCK, { force: true }); }
}
