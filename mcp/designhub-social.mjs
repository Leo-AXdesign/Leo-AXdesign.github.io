#!/usr/bin/env node
/**
 * 디자인 허브 SNS MCP 서버 (인스타그램 · 스레드)
 *
 * Claude 데스크톱에서 인스타그램(사진·캐러셀·릴스·스토리)과 스레드에 글을 올리고 계정 정보를 봅니다.
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

// ---------- MCP (stdio, JSON-RPC) ----------

const send = (msg) => process.stdout.write(JSON.stringify({ jsonrpc: "2.0", ...msg }) + "\n");

async function handle(req) {
  const { id, method, params = {} } = req;
  if (id === undefined) return; // 알림은 답하지 않습니다
  try {
    if (method === "initialize") {
      return send({ id, result: {
        protocolVersion: params.protocolVersion || "2025-06-18",
        capabilities: { tools: {} },
        serverInfo: { name: "designhub-social", version: "1.2.0" },
      } });
    }
    if (method === "ping") return send({ id, result: {} });
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
