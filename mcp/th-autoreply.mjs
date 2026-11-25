#!/usr/bin/env node
/**
 * 스레드 댓글 자동 답글
 *
 * 스레드는 DM을 보내는 API가 없어서, 켜 둔 게시물의 새 댓글에 공개 답글(가이드 링크 등)을 답니다.
 * 캠페인에 dm 을 적어 두면 'DM 보낼 사람 목록'에 쌓고 맥 알림으로 알려 줍니다. DM은 스레드 앱에서 직접 보냅니다.
 * 처리한 댓글은 기록해 두고 다시 답하지 않습니다. 내 계정 댓글은 건너뜁니다.
 *
 * 켤 게시물 목록: ~/.designhub/th-autoreply.json   (Claude 의 th_autoreply_* 도구가 고칩니다)
 *   { "campaigns": [ { "post_id": "..." 또는 "all", "keywords": ["스킬"], "replies": ["답글", ...],
 *                      "account": "designhub", "until": "...", "paused": false } ] }
 *   - post_id 가 "all" 이면 최근 7일 안에 올린 내 글 전부를 봅니다
 *   - keywords 가 비어 있으면 모든 댓글에, 있으면 그 말이 들어간 댓글에만 답합니다 (대소문자 무시)
 * 처리 기록:       ~/.designhub/th-autoreply-log.jsonl
 *
 * 실행
 *   node th-autoreply.mjs            한 번 훑고 끝납니다 (launchd 가 5분마다 부릅니다)
 *   node th-autoreply.mjs --dry-run  답글을 달지 않고 무엇을 달지만 보여 줍니다
 *   node th-autoreply.mjs --queue    DM 보낼 사람 목록과 보낼 문구를 봅니다
 *   node th-autoreply.mjs --done 아이디1 아이디2   DM 보낸 사람을 목록에서 지웁니다 (--done all 은 전부)
 *
 * 토큰: 디자인 허브 계정은 Claude 설정 파일 designhub 서버의 THREADS_ACCESS_TOKEN,
 *       다른 계정은 ~/.designhub/accounts.json 의 threads_token 을 씁니다.
 */
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { spawnSync } from "node:child_process";

const TH = "https://graph.threads.net/v1.0";
const DIR = path.join(os.homedir(), ".designhub");
const CAMPAIGNS = path.join(DIR, "th-autoreply.json");
const LOG = path.join(DIR, "th-autoreply-log.jsonl");
const LOCK = path.join(DIR, "th-autoreply.lock");
const QUEUE = path.join(DIR, "th-dm-queue.jsonl");
const ACCOUNTS = path.join(DIR, "accounts.json");
const CONFIG = path.join(os.homedir(), "Library/Application Support/Claude/claude_desktop_config.json");
const DRY = process.argv.includes("--dry-run");
const PER_RUN = 20;
const GAP = [8000, 20000];
const RECENT = 7 * 24 * 3600e3;

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const say = (...a) => console.log(new Date().toLocaleString("sv-SE", { timeZone: "Asia/Seoul" }), "[스레드]", ...a);

function tokenFor(account) {
  if (account && account !== "designhub") {
    const a = JSON.parse(fs.readFileSync(ACCOUNTS, "utf8"))[account];
    if (!a?.threads_token) throw new Error(`스레드 계정 '${account}' 토큰이 없습니다.`);
    return a.threads_token;
  }
  if (process.env.THREADS_ACCESS_TOKEN) return process.env.THREADS_ACCESS_TOKEN;
  const c = JSON.parse(fs.readFileSync(CONFIG, "utf8"));
  for (const s of Object.values(c.mcpServers || {}))
    if ((s.args || []).some((x) => String(x).includes("designhub-social")) && s.env?.THREADS_ACCESS_TOKEN)
      return s.env.THREADS_ACCESS_TOKEN;
  throw new Error("스레드 토큰을 찾지 못했습니다.");
}

const TOKENS = new Set();
const hide = (s) => [...TOKENS].reduce((t, k) => t.split(k).join("[토큰]"), String(s));

async function api(token, method, p, params = {}) {
  TOKENS.add(token);
  const url = new URL(p.startsWith("http") ? p : TH + p);
  const body = new URLSearchParams(params);
  if (method === "GET") for (const [k, v] of body) url.searchParams.set(k, v);
  url.searchParams.set("access_token", token);
  const res = await fetch(url, method === "GET" ? {} : { method, body });
  const data = await res.json().catch(() => ({}));
  if (!res.ok || data.error) {
    const e = data.error || {};
    const err = new Error(hide(`스레드 API 오류 ${e.code ?? res.status}: ${e.error_user_msg || e.message || res.statusText}`));
    err.code = e.code;
    throw err;
  }
  return data;
}

function readJson(f, d) { try { return JSON.parse(fs.readFileSync(f, "utf8")); } catch { return d; } }
function readLog() {
  try { return fs.readFileSync(LOG, "utf8").split("\n").filter(Boolean).map((l) => JSON.parse(l)); } catch { return []; }
}
function writeLog(row) {
  fs.mkdirSync(DIR, { recursive: true });
  fs.appendFileSync(LOG, JSON.stringify({ at: new Date().toISOString(), ...row }) + "\n");
}

// ---------- DM 보낼 사람 목록 ----------
function readQueue() {
  try { return fs.readFileSync(QUEUE, "utf8").split("\n").filter(Boolean).map((l) => JSON.parse(l)); } catch { return []; }
}
function writeQueue(rows) {
  fs.mkdirSync(DIR, { recursive: true });
  fs.writeFileSync(QUEUE, rows.map((r) => JSON.stringify(r)).join("\n") + (rows.length ? "\n" : ""));
}
function notify(title, text) {
  // 맥 알림 (launchd 로 돌 때도 뜹니다). 실패해도 넘어갑니다
  try {
    const q = (s) => '"' + String(s).replace(/["\\]/g, "") + '"';
    spawnSync("osascript", ["-e", `display notification ${q(text)} with title ${q(title)}`]);
  } catch {}
}
function showQueue() {
  const rows = readQueue().filter((r) => r.status === "pending");
  if (!rows.length) return console.log("DM 보낼 사람이 없습니다.");
  const byText = {};
  for (const r of rows) (byText[r.dm] ||= []).push(r);
  for (const [dm, rs] of Object.entries(byText)) {
    console.log(`\n보낼 문구 (${rs.length}명):\n${dm}\n`);
    for (const r of rs) console.log(`  @${r.username}  https://www.threads.com/@${r.username}  (댓글: ${(r.text || "").slice(0, 30)})`);
  }
  console.log(`\n보낸 뒤: node th-autoreply.mjs --done ${rows.map((r) => r.username).join(" ")}`);
}
function markDone(names) {
  const all = names.includes("all");
  const set = new Set(names.map((n) => n.replace(/^@/, "")));
  let n = 0;
  const rows = readQueue().map((r) => {
    if (r.status === "pending" && (all || set.has(r.username))) { n++; return { ...r, status: "sent", sent_at: new Date().toISOString() }; }
    return r;
  });
  writeQueue(rows);
  console.log(`${n}명을 보낸 것으로 표시했습니다.`);
}

async function waitReady(token, id) {
  for (let i = 0; i < 15; i++) {
    const { status, error_message } = await api(token, "GET", `/${id}`, { fields: "status,error_message" });
    if (status === "FINISHED") return;
    if (status === "ERROR" || status === "EXPIRED") throw new Error(`스레드가 답글을 처리하지 못했습니다: ${error_message || status}`);
    await sleep(2000);
  }
  throw new Error("스레드 답글 처리가 30초 넘게 끝나지 않았습니다.");
}

async function reply(token, uid, toId, text) {
  const { id } = await api(token, "POST", `/${uid}/threads`, { media_type: "TEXT", text, reply_to_id: toId });
  await waitReady(token, id);
  return api(token, "POST", `/${uid}/threads_publish`, { creation_id: id });
}

async function postsFor(token, c) {
  if (c.post_id !== "all") return [c.post_id];
  const d = await api(token, "GET", "/me/threads", { fields: "id,timestamp", limit: "25" });
  return (d.data || []).filter((x) => Date.now() - new Date(x.timestamp) < RECENT).map((x) => x.id);
}

async function run() {
  const active = (readJson(CAMPAIGNS, {}).campaigns || [])
    .filter((c) => !c.paused && (!c.until || new Date(c.until) > new Date()));
  if (!active.length) return say("켜 둔 게시물이 없습니다.");

  const done = new Set(readLog().filter((r) => r.status !== "error").map((r) => r.reply_id));
  let sent = 0;
  let queued = 0;

  for (const c of active) {
    const token = tokenFor(c.account);
    const me = await api(token, "GET", "/me", { fields: "id,username" });
    const kws = (c.keywords || []).map((k) => k.toLowerCase()).filter(Boolean);
    for (const postId of await postsFor(token, c)) {
      const d = await api(token, "GET", `/${postId}/replies`, { fields: "id,text,username,timestamp" });
      const todo = (d.data || []).filter((x) => !done.has(x.id)).sort((a, b) => a.timestamp.localeCompare(b.timestamp));
      if (todo.length) say(`글 ${postId}: 새 댓글 ${todo.length}개`);
      for (const x of todo) {
        const base = { account: c.account || "designhub", post_id: postId, reply_id: x.id, username: x.username };
        if (x.username === me.username) { if (!DRY) writeLog({ ...base, status: "skip", why: "내 댓글" }); continue; }
        if (kws.length && !kws.some((k) => (x.text || "").toLowerCase().includes(k))) {
          if (!DRY) writeLog({ ...base, status: "skip", why: "키워드 없음" });
          continue;
        }
        if (sent >= PER_RUN) return say(`이번에는 ${PER_RUN}개까지만 답했습니다. 나머지는 다음 차례에 답합니다.`);
        if (c.dm && readQueue().some((r) => r.username === x.username && r.dm === c.dm)) {
          // 같은 사람이 댓글을 여러 번 달아도 DM 은 한 번만
          if (!DRY) writeLog({ ...base, status: "skip", why: "이미 DM 목록에 있음" });
          continue;
        }
        const text = c.replies[Math.floor(Math.random() * c.replies.length)];
        if (DRY) { say(`[시험] @${x.username} "${(x.text || "").slice(0, 30)}" → 답글 "${text.slice(0, 40)}"`); sent++; continue; }
        try {
          const r = await reply(token, me.id, x.id, text);
          writeLog({ ...base, status: "sent", my_reply_id: r.id });
          if (c.dm) {
            writeQueue([...readQueue(), { at: new Date().toISOString(), status: "pending", username: x.username, text: x.text, post_id: postId, reply_id: x.id, dm: c.dm }]);
            queued++;
          }
          say(`@${x.username} 답글 담${c.dm ? ", DM 목록에 넣음" : ""}`);
        } catch (e) {
          // 권한·토큰 문제는 다음에 다시 시도하도록 error 로 남기고 멈춥니다
          writeLog({ ...base, status: "error", why: e.message });
          say(`@${x.username} 답글 실패:`, e.message);
          if ([10, 190, 200].includes(e.code)) { process.exitCode = 2; return; }
          continue;
        }
        sent++;
        await sleep(GAP[0] + Math.random() * (GAP[1] - GAP[0]));
      }
    }
  }
  say(`끝. 이번에 ${DRY ? "달" : "단"} 답글 ${sent}개`);
  if (queued) {
    const n = readQueue().filter((r) => r.status === "pending").length;
    notify("스레드 DM 보낼 차례", `새로 ${queued}명, 모두 ${n}명이 기다려요. Claude 에서 'DM 목록 보여 줘'라고 하세요.`);
  }
}

function lock() {
  try { if (Date.now() - fs.statSync(LOCK).mtimeMs < 10 * 60e3) { say("이미 도는 중이라 건너뜁니다."); return false; } } catch {}
  fs.mkdirSync(DIR, { recursive: true });
  fs.writeFileSync(LOCK, String(process.pid));
  return true;
}

const args = process.argv.slice(2);
if (args[0] === "--queue") { showQueue(); process.exit(0); }
if (args[0] === "--done") { markDone(args.slice(1)); process.exit(0); }

if (lock()) {
  try { await run(); }
  catch (e) { say("오류:", hide(e.message)); process.exitCode = 1; }
  finally { fs.rmSync(LOCK, { force: true }); }
}
