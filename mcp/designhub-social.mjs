#!/usr/bin/env node
/**
 * 디자인 허브 SNS MCP 서버 (인스타그램 · 스레드)
 *
 * Claude 데스크톱에서 인스타그램(사진·캐러셀·릴스·스토리)과 스레드에 글을 올리고 계정 정보를 봅니다.
 * 읽을거리 글을 읽고 고치고 사이트에 반영하는 도구와, 검토·다듬기 프롬프트도 있습니다 (구독 안에서, API 요금 없음).
 * - 인스타그램: "Instagram 로그인이 포함된 API" 토큰(IGAA…)을 씁니다. graph.instagram.com
 * - 스레드:     Threads API 토큰을 씁니다. graph.threads.net
 * - 외부 패키지 없이 Node.js 18 이상만 있으면 됩니다.
 * - 토큰은 Claude 설정 파일의 env 에서만 읽고, 메타 서버 말고는 어디에도 보내지 않습니다.
 *
 * env
 *   INSTAGRAM_ACCESS_TOKEN  (필수: 인스타그램 도구)
 *   INSTAGRAM_USER_ID       (선택: 없으면 /me 로 알아냅니다)
 *   THREADS_ACCESS_TOKEN    (필수: 스레드 도구)
 *   THREADS_USER_ID         (선택)
 */
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import readline from "node:readline";
import { spawn } from "node:child_process";

const IG = "https://graph.instagram.com/v23.0";
const TH = "https://graph.threads.net/v1.0";
const CONFIG = path.join(os.homedir(), "Library/Application Support/Claude/claude_desktop_config.json");
const env = process.env;
const log = (...a) => console.error("[designhub-social]", ...a);
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

// ---------- 메타 API 호출 ----------

function hide(text) {
  // 오류 메시지에 토큰이 섞여 나오지 않도록 지웁니다
  let s = String(text);
  for (const t of [env.INSTAGRAM_ACCESS_TOKEN, env.THREADS_ACCESS_TOKEN]) if (t) s = s.split(t).join("[토큰]");
  return s;
}

async function call(base, token, method, p, params = {}) {
  if (!token) throw new Error(base === IG ? "INSTAGRAM_ACCESS_TOKEN 이 설정되지 않았습니다." : "THREADS_ACCESS_TOKEN 이 설정되지 않았습니다.");
  const q = new URLSearchParams({ ...params, access_token: token });
  const url = p.startsWith("http") ? p : base + p;
  const res = method === "GET"
    ? await fetch(url + (url.includes("?") ? "&" : "?") + q)
    : await fetch(url, { method, body: q });
  const data = await res.json().catch(() => ({}));
  if (!res.ok || data.error) {
    const e = data.error || {};
    throw new Error(hide(`메타 API 오류 ${e.code ?? res.status}: ${e.error_user_msg || e.message || res.statusText}`));
  }
  return data;
}
const ig = (m, p, params) => call(IG, env.INSTAGRAM_ACCESS_TOKEN, m, p, params);
const th = (m, p, params) => call(TH, env.THREADS_ACCESS_TOKEN, m, p, params);

let igId = env.INSTAGRAM_USER_ID || "";
let thId = env.THREADS_USER_ID || "";
async function igUser() {
  if (!igId) igId = (await ig("GET", "/me", { fields: "user_id" })).user_id;
  return igId;
}
async function thUser() {
  if (!thId) thId = (await th("GET", "/me", { fields: "id" })).id;
  return thId;
}

// 컨테이너(올릴 준비가 된 미디어)가 다 만들어질 때까지 기다립니다
async function waitIg(id, tries = 30) {
  for (let i = 0; i < tries; i++) {
    const { status_code, status } = await ig("GET", `/${id}`, { fields: "status_code,status" });
    if (status_code === "FINISHED") return;
    if (status_code === "ERROR" || status_code === "EXPIRED") throw new Error(`인스타그램이 미디어를 처리하지 못했습니다: ${status || status_code}`);
    await sleep(2000);
  }
  throw new Error(`인스타그램 미디어 처리가 ${Math.round(tries * 2 / 60)}분 넘게 끝나지 않았습니다. 잠시 뒤 ig_recent_media 로 올라갔는지 확인하세요.`);
}
async function waitTh(id) {
  for (let i = 0; i < 30; i++) {
    const { status, error_message } = await th("GET", `/${id}`, { fields: "status,error_message" });
    if (status === "FINISHED") return;
    if (status === "ERROR" || status === "EXPIRED") throw new Error(`스레드가 게시물을 처리하지 못했습니다: ${error_message || status}`);
    await sleep(2000);
  }
  throw new Error("스레드 게시물 처리가 1분 넘게 끝나지 않았습니다.");
}


// ---------- 읽을거리 글 (Claude 구독으로 검토·수정, API 요금 없음) ----------
// DESIGNHUB_REPO: 이 맥의 사이트 저장소 폴더 (setup-studio.sh 가 설정 파일에 넣어 둡니다)

function repo() {
  const r = env.DESIGNHUB_REPO;
  if (!r || !fs.existsSync(path.join(r, "tools", "admin.py")))
    throw new Error("사이트 저장소 폴더를 모릅니다. 터미널에서 설치 한 줄(setup-studio.sh)을 다시 실행해 주세요.");
  return r;
}

function articlePath(slug) {
  if (!/^[a-z0-9-]+$/.test(slug || "")) throw new Error("글 주소(slug)는 영문 소문자·숫자·하이픈만 됩니다.");
  const f = path.join(repo(), "content", "articles", `${slug}.md`);
  if (!fs.existsSync(f)) throw new Error(`없는 글입니다: ${slug}`);
  return f;
}

function frontmatter(md) {
  const m = md.match(/^---\n([\s\S]*?)\n---/);
  const meta = {};
  if (m) for (const line of m[1].split("\n")) { const i = line.indexOf(":"); if (i > 0) meta[line.slice(0, i).trim()] = line.slice(i + 1).trim(); }
  return meta;
}

function touchUpdated(md) {
  const today = new Date().toLocaleDateString("sv-SE", { timeZone: "Asia/Seoul" });
  const end = md.indexOf("\n---", 4);
  let head = md.slice(0, end);
  const body = md.slice(end);
  head = /^updated:/m.test(head) ? head.replace(/^updated:.*$/m, `updated: ${today}`) : head.replace(/^(date:.*)$/m, `$1\nupdated: ${today}`);
  return head + body;
}

function guide() {
  try { return fs.readFileSync(path.join(repo(), "tools", "editor-guide.md"), "utf8"); }
  catch { return "디자인 허브 편집 기준 파일(tools/editor-guide.md)을 찾지 못했습니다."; }
}

function runPublish(message) {
  return new Promise((resolve, reject) => {
    const p = spawn("python3", ["tools/publish.py", message], { cwd: repo() });
    let out = "";
    p.stdout.on("data", (d) => (out += d));
    p.stderr.on("data", (d) => (out += d));
    const timer = setTimeout(() => { p.kill(); reject(new Error("5분이 지나도 끝나지 않았습니다.")); }, 300000);
    p.on("close", (code) => { clearTimeout(timer); code === 0 ? resolve(out.trim()) : reject(new Error(out.trim().slice(-1500))); });
  });
}

// ---------- 도구 ----------

const TOOLS = {
  card_sets: {
    description: "디자인 허브가 미리 만들어 둔 인스타 카드뉴스 묶음 목록(이미지 주소, 캡션 초안)을 봅니다. 캐러셀을 올릴 때 먼저 이걸로 이미지 주소와 캡션을 가져오세요.",
    schema: { type: "object", properties: { id: { type: "string", description: "선택: 묶음 id (예: fonts-pick). 비우면 전체 목록" } } },
    run: async ({ id }) => {
      const res = await fetch("https://designrefs.com/social/cards/index.json", { cache: "no-store" });
      if (!res.ok) throw new Error(`카드 목록을 불러오지 못했습니다 (${res.status})`);
      const { sets } = await res.json();
      if (id) {
        const s = sets.find((x) => x.id === id);
        if (!s) throw new Error(`없는 묶음입니다: ${id}. 있는 것: ${sets.map((x) => x.id).join(", ")}`);
        return s;
      }
      return sets.map(({ id, title, count }) => ({ id, title, count }));
    },
  },

  ig_profile: {
    description: "인스타그램 계정 정보(아이디, 이름, 팔로워, 게시물 수, 소개)를 봅니다.",
    schema: { type: "object", properties: {} },
    run: async () => ig("GET", "/me", {
      fields: "user_id,username,name,account_type,profile_picture_url,followers_count,follows_count,media_count,biography,website",
    }),
  },

  ig_recent_media: {
    description: "인스타그램 최근 게시물 목록(캡션, 링크, 좋아요, 댓글 수)을 봅니다.",
    schema: { type: "object", properties: { limit: { type: "number", description: "가져올 개수 (기본 10, 최대 50)" } } },
    run: async ({ limit = 10 }) => ig("GET", `/${await igUser()}/media`, {
      fields: "id,caption,media_type,permalink,timestamp,like_count,comments_count",
      limit: String(Math.min(Math.max(1, limit), 50)),
    }),
  },

  ig_publish_image: {
    description: "인스타그램에 사진 한 장을 공개 게시합니다. 이미지는 공개된 https 주소의 JPEG여야 합니다. 되돌릴 수 없는 공개 게시이니, 사용자가 내용을 확인한 뒤에만 쓰세요.",
    schema: {
      type: "object",
      properties: {
        image_url: { type: "string", description: "공개 https 이미지 주소 (JPEG 권장)" },
        caption: { type: "string", description: "캡션 (해시태그 포함 가능, 최대 2,200자)" },
      },
      required: ["image_url"],
    },
    run: async ({ image_url, caption = "" }) => {
      const uid = await igUser();
      const { id } = await ig("POST", `/${uid}/media`, { image_url, caption });
      await waitIg(id);
      const post = await ig("POST", `/${uid}/media_publish`, { creation_id: id });
      return ig("GET", `/${post.id}`, { fields: "id,permalink,timestamp" });
    },
  },

  ig_publish_carousel: {
    description: "인스타그램에 여러 장(2~10장) 캐러셀을 공개 게시합니다. 카드뉴스용. 되돌릴 수 없는 공개 게시이니, 사용자가 내용을 확인한 뒤에만 쓰세요.",
    schema: {
      type: "object",
      properties: {
        image_urls: { type: "array", items: { type: "string" }, description: "공개 https 이미지 주소 2~10개, 순서대로" },
        caption: { type: "string", description: "캡션" },
      },
      required: ["image_urls"],
    },
    run: async ({ image_urls, caption = "" }) => {
      if (!Array.isArray(image_urls) || image_urls.length < 2 || image_urls.length > 10)
        throw new Error("캐러셀은 이미지가 2~10장이어야 합니다.");
      const uid = await igUser();
      const children = [];
      for (const image_url of image_urls) {
        const { id } = await ig("POST", `/${uid}/media`, { image_url, is_carousel_item: "true" });
        await waitIg(id);
        children.push(id);
      }
      const { id } = await ig("POST", `/${uid}/media`, { media_type: "CAROUSEL", children: children.join(","), caption });
      await waitIg(id);
      const post = await ig("POST", `/${uid}/media_publish`, { creation_id: id });
      return ig("GET", `/${post.id}`, { fields: "id,permalink,timestamp" });
    },
  },

  reel_list: {
    description: "디자인 허브가 미리 만들어 둔 릴스 영상 목록(영상·커버 주소, 길이, 캡션 초안)을 봅니다. 릴스를 올릴 때 먼저 이걸로 주소와 캡션을 가져오세요.",
    schema: { type: "object", properties: { id: { type: "string", description: "선택: 릴스 id (예: fonts-pick-tour)" } } },
    run: async ({ id }) => {
      const res = await fetch("https://designrefs.com/social/reels/index.json", { cache: "no-store" });
      if (!res.ok) throw new Error(`릴스 목록을 불러오지 못했습니다 (${res.status})`);
      const { reels } = await res.json();
      if (id) {
        const r = reels.find((x) => x.id === id);
        if (!r) throw new Error(`없는 릴스입니다: ${id}. 있는 것: ${reels.map((x) => x.id).join(", ")}`);
        return r;
      }
      return reels.map(({ id, title, seconds }) => ({ id, title, seconds }));
    },
  },

  ig_publish_reel: {
    description: "인스타그램에 릴스(세로 영상)를 공개 게시합니다. 영상은 공개 https 주소의 MP4(H.264)여야 합니다. 배경음악은 API 로 넣을 수 없습니다. 처리에 몇 분 걸릴 수 있습니다. 되돌릴 수 없는 공개 게시이니, 사용자가 내용을 확인한 뒤에만 쓰세요.",
    schema: {
      type: "object",
      properties: {
        video_url: { type: "string", description: "공개 https MP4 주소" },
        caption: { type: "string", description: "캡션" },
        cover_url: { type: "string", description: "선택: 커버 이미지 주소 (JPEG)" },
        share_to_feed: { type: "boolean", description: "피드에도 보이게 할지 (기본 true)" },
      },
      required: ["video_url"],
    },
    run: async ({ video_url, caption = "", cover_url, share_to_feed = true }) => {
      const uid = await igUser();
      const params = { media_type: "REELS", video_url, caption, share_to_feed: String(share_to_feed) };
      if (cover_url) params.cover_url = cover_url;
      const { id } = await ig("POST", `/${uid}/media`, params);
      await waitIg(id, 150);
      const post = await ig("POST", `/${uid}/media_publish`, { creation_id: id });
      return ig("GET", `/${post.id}`, { fields: "id,permalink,timestamp" });
    },
  },

  ig_publish_story: {
    description: "인스타그램 스토리에 사진 또는 영상 한 개를 올립니다(24시간 노출). 공개 https 주소여야 합니다. 사용자가 확인한 뒤에만 쓰세요.",
    schema: {
      type: "object",
      properties: {
        image_url: { type: "string", description: "사진 주소 (JPEG). image_url 과 video_url 중 하나" },
        video_url: { type: "string", description: "영상 주소 (MP4)" },
      },
    },
    run: async ({ image_url, video_url }) => {
      if (!image_url === !video_url) throw new Error("image_url 과 video_url 중 하나만 주세요.");
      const uid = await igUser();
      const params = image_url ? { media_type: "STORIES", image_url } : { media_type: "STORIES", video_url };
      const { id } = await ig("POST", `/${uid}/media`, params);
      await waitIg(id, video_url ? 150 : 30);
      const post = await ig("POST", `/${uid}/media_publish`, { creation_id: id });
      return { id: post.id, note: "스토리는 24시간 동안 보입니다." };
    },
  },

  ig_publish_limit: {
    description: "인스타그램 24시간 게시 한도와 지금까지 쓴 양을 봅니다.",
    schema: { type: "object", properties: {} },
    run: async () => ig("GET", `/${await igUser()}/content_publishing_limit`, { fields: "quota_usage,config" }),
  },

  threads_profile: {
    description: "스레드 계정 정보(아이디, 이름, 소개)를 봅니다.",
    schema: { type: "object", properties: {} },
    run: async () => th("GET", "/me", { fields: "id,username,name,threads_profile_picture_url,threads_biography" }),
  },

  threads_recent_posts: {
    description: "스레드 최근 게시물 목록을 봅니다.",
    schema: { type: "object", properties: { limit: { type: "number", description: "가져올 개수 (기본 10, 최대 50)" } } },
    run: async ({ limit = 10 }) => th("GET", `/${await thUser()}/threads`, {
      fields: "id,text,media_type,permalink,timestamp",
      limit: String(Math.min(Math.max(1, limit), 50)),
    }),
  },

  threads_publish: {
    description: "스레드에 글을 공개 게시합니다. 글만, 또는 글+사진 한 장. 링크를 넣으면 미리보기 카드가 붙습니다. 되돌릴 수 없는 공개 게시이니, 사용자가 내용을 확인한 뒤에만 쓰세요.",
    schema: {
      type: "object",
      properties: {
        text: { type: "string", description: "본문 (최대 500자)" },
        image_url: { type: "string", description: "선택: 공개 https 이미지 주소" },
        link_attachment: { type: "string", description: "선택: 미리보기로 붙일 링크 (글만 올릴 때)" },
      },
      required: ["text"],
    },
    run: async ({ text, image_url, link_attachment }) => {
      const uid = await thUser();
      const params = image_url
        ? { media_type: "IMAGE", image_url, text }
        : { media_type: "TEXT", text, ...(link_attachment ? { link_attachment } : {}) };
      const { id } = await th("POST", `/${uid}/threads`, params);
      await waitTh(id);
      const post = await th("POST", `/${uid}/threads_publish`, { creation_id: id });
      return th("GET", `/${post.id}`, { fields: "id,permalink,timestamp" });
    },
  },

  editor_guide: {
    description: "디자인 허브 편집 기준(말투·출처·검토 방법·SNS 규칙)을 읽습니다. 글을 검토하거나 SNS 글을 다듬기 전에 먼저 읽으세요.",
    schema: { type: "object", properties: {} },
    run: async () => guide(),
  },

  article_list: {
    description: "발행된 읽을거리 글 목록(주소 slug, 제목, 날짜)을 최신순으로 봅니다.",
    schema: { type: "object", properties: {} },
    run: async () => {
      const dir = path.join(repo(), "content", "articles");
      return fs.readdirSync(dir).filter((f) => f.endsWith(".md")).map((f) => {
        const m = frontmatter(fs.readFileSync(path.join(dir, f), "utf8"));
        return { slug: m.slug || f.replace(/\.md$/, ""), title: m.title, date: m.date, updated: m.updated || "" };
      }).sort((a, b) => String(b.date).localeCompare(String(a.date)));
    },
  },

  article_read: {
    description: "읽을거리 글 한 편의 원문(마크다운)을 읽습니다.",
    schema: { type: "object", properties: { slug: { type: "string", description: "글 주소, 예: ai-draft-client-pixel-pusher" } }, required: ["slug"] },
    run: async ({ slug }) => fs.readFileSync(articlePath(slug), "utf8"),
  },

  article_edit: {
    description: "읽을거리 글 본문을 고칩니다(이 맥의 파일만, 사이트 반영은 site_publish). before 를 after 로 바꾸거나(after 가 빈칸이면 삭제), anchor 문장이 있는 문단 뒤에 after 를 새 문단으로 넣습니다. before·anchor 는 원문을 글자 그대로 인용해야 합니다. 사용자가 고르거나 동의한 제안만 적용하세요.",
    schema: {
      type: "object",
      properties: {
        slug: { type: "string" },
        before: { type: "string", description: "바꾸거나 지울 원문 문장 (그대로 인용)" },
        anchor: { type: "string", description: "새 문단을 넣을 자리 바로 앞 문장 (그대로 인용)" },
        after: { type: "string", description: "바뀔 문장 또는 새 문단" },
      },
      required: ["slug"],
    },
    run: async ({ slug, before = "", anchor = "", after = "" }) => {
      const f = articlePath(slug);
      let md = fs.readFileSync(f, "utf8");
      if (before) {
        if (!md.includes(before)) throw new Error("본문에서 before 문장을 찾지 못했습니다. article_read 로 원문을 다시 확인해 주세요.");
        md = md.replace(before, () => after);   // after 안의 $ 기호를 그대로 두려고 함수로 넘깁니다
      } else if (anchor && after) {
        const i = md.indexOf(anchor);
        if (i < 0) throw new Error("본문에서 anchor 문장을 찾지 못했습니다.");
        let end = md.indexOf("\n\n", i);
        if (end < 0) end = md.length;
        md = md.slice(0, end) + "\n\n" + after.trim() + md.slice(end);
      } else {
        throw new Error("before 또는 anchor+after 가 필요합니다.");
      }
      fs.writeFileSync(f, touchUpdated(md));
      return { ok: true, note: "이 맥의 글을 고쳤습니다. 다 고친 뒤 site_publish 로 사이트에 반영하세요. 영어판(content/articles-en)은 바뀌지 않습니다." };
    },
  },

  site_publish: {
    description: "고친 글을 사이트에 반영합니다(빌드 → GitHub 에 올리기, 1~2분 뒤 designrefs.com 에 보임). 사용자가 확인한 뒤에만 쓰세요.",
    schema: { type: "object", properties: { message: { type: "string", description: "무엇을 고쳤는지 한 줄" } } },
    run: async ({ message = "글 고침" }) => runPublish(message),
  },

  refresh_tokens: {
    description: "인스타그램·스레드 장기 토큰(60일)을 새로 연장하고 Claude 설정 파일에 자동으로 저장합니다. 한 달에 한 번쯤 실행하면 만료되지 않습니다. 발급 후 24시간이 지나야 연장됩니다.",
    schema: { type: "object", properties: {} },
    run: async () => {
      const out = {};
      const conf = JSON.parse(fs.readFileSync(CONFIG, "utf8"));
      const me = Object.values(conf.mcpServers || {}).find((s) => (s.args || []).some((a) => String(a).includes("designhub-social")));
      if (!me) throw new Error("설정 파일에서 이 서버를 찾지 못했습니다.");
      if (env.INSTAGRAM_ACCESS_TOKEN) {
        try {
          const r = await call(IG, env.INSTAGRAM_ACCESS_TOKEN, "GET", "https://graph.instagram.com/refresh_access_token", { grant_type: "ig_refresh_token" });
          me.env.INSTAGRAM_ACCESS_TOKEN = env.INSTAGRAM_ACCESS_TOKEN = r.access_token;
          out.instagram = `연장됨 (약 ${Math.round(r.expires_in / 86400)}일 남음)`;
        } catch (e) { out.instagram = e.message; }
      }
      if (env.THREADS_ACCESS_TOKEN) {
        try {
          const r = await call(TH, env.THREADS_ACCESS_TOKEN, "GET", "https://graph.threads.net/refresh_access_token", { grant_type: "th_refresh_token" });
          me.env.THREADS_ACCESS_TOKEN = env.THREADS_ACCESS_TOKEN = r.access_token;
          out.threads = `연장됨 (약 ${Math.round(r.expires_in / 86400)}일 남음)`;
        } catch (e) { out.threads = e.message; }
      }
      fs.copyFileSync(CONFIG, CONFIG + ".bak");
      fs.writeFileSync(CONFIG, JSON.stringify(conf, null, 2));
      return out;
    },
  },
};

// ---------- 프롬프트 (Claude 데스크톱의 + 메뉴에서 고르는 작업) ----------

const PROMPTS = {
  review_article: {
    description: "발행된 읽을거리 글을 편집장 기준으로 검토하고, 고를 수 있는 수정 제안을 받습니다 (구독으로, 추가 요금 없음)",
    arguments: [{ name: "slug", description: "글 주소 (비우면 최신 글)", required: false }],
    text: ({ slug }) => `designhub 도구로 읽을거리 글을 검토해 줘.

1. editor_guide 로 편집 기준을 먼저 읽어.
2. ${slug ? `article_read 로 '${slug}' 글을 읽어.` : "article_list 로 최신 글을 찾고 article_read 로 읽어."}
3. 웹 검색으로 발행일 이후 바뀐 소식이 있는지 확인해.
4. 제안을 번호 붙여 보여 줘. 각 제안마다 종류·중요도, 이유와 근거 링크, 바꿀 원문(그대로 인용) → 바뀔 문장.
5. 마지막에 이 글을 소개하는 스레드 글 초안 하나.
6. 내가 번호를 고르면 그것만 article_edit 로 적용하고, 다 끝나면 site_publish 해도 되는지 물어봐.`,
  },
  polish_post: {
    description: "인스타 캡션이나 스레드 글을 편집 기준에 맞게 다듬습니다 (구독으로, 추가 요금 없음)",
    arguments: [{ name: "text", description: "다듬을 글", required: true }],
    text: ({ text = "" }) => `editor_guide 로 편집 기준을 읽고, 아래 글을 기준에 맞게 다듬어 줘. 고친 점을 짧게 적고 다듬은 전체 글을 보여 줘. [ ] 자리는 지어내지 말고 남겨 둬.\n\n${text}`,
  },
};

// ---------- MCP (stdio, JSON-RPC) ----------

const send = (msg) => process.stdout.write(JSON.stringify({ jsonrpc: "2.0", ...msg }) + "\n");

async function handle(req) {
  const { id, method, params = {} } = req;
  if (id === undefined) return; // 알림은 답하지 않습니다
  try {
    if (method === "initialize") {
      return send({ id, result: {
        protocolVersion: params.protocolVersion || "2025-06-18",
        capabilities: { tools: {}, prompts: {} },
        serverInfo: { name: "designhub-social", version: "1.3.0" },
      } });
    }
    if (method === "ping") return send({ id, result: {} });
    if (method === "prompts/list") {
      return send({ id, result: { prompts: Object.entries(PROMPTS).map(([name, p]) => ({ name, description: p.description, arguments: p.arguments })) } });
    }
    if (method === "prompts/get") {
      const p = PROMPTS[params.name];
      if (!p) return send({ id, error: { code: -32602, message: `없는 프롬프트: ${params.name}` } });
      return send({ id, result: { description: p.description, messages: [{ role: "user", content: { type: "text", text: p.text(params.arguments || {}) } }] } });
    }
    if (method === "tools/list") {
      return send({ id, result: { tools: Object.entries(TOOLS).map(([name, t]) => ({ name, description: t.description, inputSchema: t.schema })) } });
    }
    if (method === "tools/call") {
      const tool = TOOLS[params.name];
      if (!tool) return send({ id, error: { code: -32602, message: `없는 도구: ${params.name}` } });
      try {
        const result = await tool.run(params.arguments || {});
        return send({ id, result: { content: [{ type: "text", text: JSON.stringify(result, null, 2) }] } });
      } catch (e) {
        return send({ id, result: { isError: true, content: [{ type: "text", text: hide(e.message) }] } });
      }
    }
    send({ id, error: { code: -32601, message: `지원하지 않는 요청: ${method}` } });
  } catch (e) {
    send({ id, error: { code: -32603, message: hide(e.message) } });
  }
}

readline.createInterface({ input: process.stdin }).on("line", (line) => {
  if (!line.trim()) return;
  let req;
  try { req = JSON.parse(line); } catch { return log("JSON 이 아닌 입력을 무시합니다"); }
  handle(req);
});
log("시작됨");
