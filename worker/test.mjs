import worker from "./src/index.js";

// D1 대신 쓰는 아주 작은 가짜 데이터베이스
const rows = [];
let next = 1;
const DB = {
  prepare(sql) {
    let args = [];
    const api = {
      bind(...a) { args = a; return api; },
      async all() {
        if (sql.includes("SELECT id, name, body, at"))
          return { results: rows.filter(r => r.page === args[0] && r.hidden === 0)
            .map(({ id, name, body, at }) => ({ id, name, body, at })) };
        return { results: [] };
      },
      async first() {
        if (sql.includes("SELECT at FROM comments WHERE who"))
          { const r = rows.filter(r => r.who === args[0]).pop(); return r ? { at: r.at } : null; }
        if (sql.includes("COUNT(*)"))
          return { n: rows.filter(r => r.who === args[0] && r.at > args[1]).length };
        return null;
      },
      async run() {
        if (sql.startsWith("INSERT")) {
          rows.push({ id: next, page: args[0], name: args[1], body: args[2], at: args[3], who: args[4], hidden: args[5] });
          return { meta: { last_row_id: next++ } };
        }
        if (sql.startsWith("DELETE")) {
          const i = rows.findIndex(r => r.id === args[0]);
          if (i > -1) rows.splice(i, 1);
          return { meta: {} };
        }
        return { meta: {} };
      },
    };
    return api;
  },
};
const env = { DB, ALLOW_ORIGIN: "https://designrefs.com", ADMIN_TOKEN: "s3cret", IP_SALT: "salt", MODERATE: "0" };
const ORIGIN = "https://designrefs.com";

function post(body, ip = "1.1.1.1") {
  return new Request("https://x/comments", {
    method: "POST", headers: { Origin: ORIGIN, "Content-Type": "application/json", "CF-Connecting-IP": ip },
    body: JSON.stringify(body),
  });
}
const ok = [], bad = [];
const check = (label, cond) => (cond ? ok : bad).push(label);
const good = { page: "talk", name: "박태현", body: "눈누 링크 잘 쓰고 있습니다.", elapsed: 5000 };

let r = await worker.fetch(post(good), env);
let d = await r.json();
check("정상 등록", r.status === 200 && d.ok && d.item.name === "박태현");
check("CORS 헤더", r.headers.get("Access-Control-Allow-Origin") === ORIGIN);

r = await worker.fetch(new Request("https://x/comments?page=talk", { headers: { Origin: ORIGIN } }), env);
d = await r.json();
check("목록 조회", d.ok && d.items.length === 1 && d.items[0].body.includes("눈누"));
check("해시 비공개", !JSON.stringify(d).includes("who"));

d = await (await worker.fetch(post({ ...good, website: "http://spam.example" }, "2.2.2.2"), env)).json();
check("허니팟 차단", d.ok && d.items === null && rows.length === 1);

d = await (await worker.fetch(post({ ...good, elapsed: 500 }, "3.3.3.3"), env)).json();
check("너무 빠른 전송 차단", !d.ok);

d = await (await worker.fetch(post({ ...good, body: "http://a.com http://b.com http://c.com" }, "4.4.4.4"), env)).json();
check("링크 과다 차단", !d.ok && d.error.includes("링크"));

d = await (await worker.fetch(post({ ...good, name: "" }, "5.5.5.5"), env)).json();
check("이름 필수", !d.ok);

d = await (await worker.fetch(post(good, "1.1.1.1"), env)).json();
check("연속 작성 차단", !d.ok && d.error.includes("조금"));

d = await (await worker.fetch(post({ ...good, name: "가".repeat(50), body: "나".repeat(2000) }, "6.6.6.6"), env)).json();
check("길이 자르기", d.ok && d.item.name.length === 20 && d.item.body.length === 1000);

d = await (await worker.fetch(post({ ...good, body: "<script>alert(1)</script> 안녕" }, "7.7.7.7"), env)).json();
check("태그는 그대로 저장(출력에서 이스케이프)", d.ok && d.item.body.includes("<script>"));

r = await worker.fetch(new Request("https://x/comments?id=1", { method: "DELETE", headers: { Origin: ORIGIN } }), env);
check("토큰 없이 삭제 거부", r.status === 401);
r = await worker.fetch(new Request("https://x/comments?id=1", {
  method: "DELETE", headers: { Origin: ORIGIN, Authorization: "Bearer s3cret" } }), env);
check("관리자 삭제", r.status === 200 && !rows.some(x => x.id === 1));

r = await worker.fetch(new Request("https://x/other", { headers: { Origin: ORIGIN } }), env);
check("없는 주소 404", r.status === 404);
r = await worker.fetch(new Request("https://x/comments", { method: "OPTIONS", headers: { Origin: ORIGIN } }), env);
check("프리플라이트 204", r.status === 204);

r = await worker.fetch(post(good, "8.8.8.8"), { ...env, MODERATE: "1" });
d = await r.json();
check("승인 모드", d.ok && d.pending === true && d.item === null);

console.log("통과 " + ok.length + "개");
ok.forEach(x => console.log("  ✓ " + x));
if (bad.length) { console.log("실패 " + bad.length + "개"); bad.forEach(x => console.log("  ✗ " + x)); process.exit(1); }
