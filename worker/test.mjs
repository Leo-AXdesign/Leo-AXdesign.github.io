/**
 * 댓글 서버 검사. 진짜 데이터베이스 대신 메모리에 담아 두고 돌립니다.
 *
 *   node worker/test.mjs
 *
 * 서버 코드를 고쳤으면 배포 전에 한 번 돌려 보세요.
 */
import worker from "./src/index.js";

const rows = [];
let tries = [];
let next = 1;

// D1 대신 쓰는 아주 작은 가짜 데이터베이스
const DB = {
  prepare(sql) {
    let args = [];
    const api = {
      bind(...a) { args = a; return api; },
      async all() {
        if (sql.includes("SELECT id, name, body, at"))
          return { results: rows.filter(r => r.page === args[0] && r.hidden === 0)
            .map(({ id, name, body, at }) => ({ id, name, body, at })).reverse() };
        return { results: [] };
      },
      async first() {
        if (sql.includes("SELECT at FROM comments WHERE who")) {
          const r = rows.filter(r => r.who === args[0]).pop();
          return r ? { at: r.at } : null;
        }
        if (sql.includes("COUNT(*) AS n FROM comments"))
          return { n: rows.filter(r => r.who === args[0] && r.at > args[1]).length };
        if (sql.includes("COUNT(*) AS n FROM tries"))
          return { n: tries.filter(t => t.who === args[0] && t.at > args[1]).length };
        if (sql.includes("SELECT pw FROM comments"))
          return rows.find(r => r.id === args[0]) || null;
        return null;
      },
      async run() {
        if (sql.startsWith("INSERT INTO comments")) {
          rows.push({ id: next, page: args[0], name: args[1], body: args[2],
                      at: args[3], who: args[4], pw: args[5], hidden: args[6] });
          return { meta: { last_row_id: next++ } };
        }
        if (sql.startsWith("INSERT INTO tries")) { tries.push({ who: args[0], at: args[1] }); return { meta: {} }; }
        if (sql.startsWith("DELETE FROM tries")) { tries = tries.filter(t => t.at >= args[0]); return { meta: {} }; }
        if (sql.startsWith("DELETE FROM comments")) {
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

const post = (body, ip = "1.1.1.1") => new Request("https://x/comments", {
  method: "POST",
  headers: { Origin: ORIGIN, "Content-Type": "application/json", "CF-Connecting-IP": ip },
  body: JSON.stringify(body),
});
const del = (id, body, ip = "9.9.9.9", token) => new Request(`https://x/comments?id=${id}`, {
  method: "DELETE",
  headers: {
    Origin: ORIGIN, "Content-Type": "application/json", "CF-Connecting-IP": ip,
    ...(token ? { Authorization: "Bearer " + token } : {}),
  },
  body: body === undefined ? undefined : JSON.stringify(body),
});

const ok = [], bad = [];
const check = (label, cond) => (cond ? ok : bad).push(label);
const good = { page: "talk", name: "박태현", body: "눈누 링크 잘 쓰고 있습니다.", pw: "1234", elapsed: 5000 };

/* ---------- 글 남기기 ---------- */
let r = await worker.fetch(post(good), env);
let d = await r.json();
check("정상 등록", r.status === 200 && d.ok && d.item.name === "박태현");
check("CORS 헤더", r.headers.get("Access-Control-Allow-Origin") === ORIGIN);
check("비밀번호는 원문으로 저장하지 않음", rows[0].pw !== "1234" && rows[0].pw.includes("$"));

r = await worker.fetch(new Request("https://x/comments?page=talk", { headers: { Origin: ORIGIN } }), env);
d = await r.json();
check("목록 조회", d.ok && d.items.length === 1 && d.items[0].body.includes("눈누"));
check("목록에 비밀번호·해시 미노출", !JSON.stringify(d).includes("pw") && !JSON.stringify(d).includes("who"));

d = await (await worker.fetch(post({ ...good, website: "http://spam.example" }, "2.2.2.2"), env)).json();
check("허니팟 차단", d.ok && d.items === null && rows.length === 1);

d = await (await worker.fetch(post({ ...good, elapsed: 500 }, "3.3.3.3"), env)).json();
check("너무 빠른 전송 차단", !d.ok);

d = await (await worker.fetch(post({ ...good, body: "http://a.com http://b.com http://c.com" }, "4.4.4.4"), env)).json();
check("링크 과다 차단", !d.ok && d.error.includes("링크"));

d = await (await worker.fetch(post({ ...good, name: "" }, "5.5.5.5"), env)).json();
check("이름 필수", !d.ok);

d = await (await worker.fetch(post({ ...good, pw: "123" }, "5.5.5.6"), env)).json();
check("비밀번호 4자 미만 거부", !d.ok && d.error.includes("비밀번호"));

d = await (await worker.fetch(post({ ...good, pw: "1234567890123" }, "5.5.5.7"), env)).json();
check("비밀번호 12자 초과 거부", !d.ok);

d = await (await worker.fetch(post({ ...good, pw: "" }, "5.5.5.8"), env)).json();
check("비밀번호 없이 등록 불가", !d.ok);

d = await (await worker.fetch(post(good, "1.1.1.1"), env)).json();
check("연속 작성 차단", !d.ok && d.error.includes("조금"));

d = await (await worker.fetch(post({ ...good, name: "가".repeat(50), body: "나".repeat(2000) }, "6.6.6.6"), env)).json();
check("길이 자르기", d.ok && d.item.name.length === 20 && d.item.body.length === 1000);

d = await (await worker.fetch(post({ ...good, body: "<script>alert(1)</script> 안녕" }, "7.7.7.7"), env)).json();
check("태그는 그대로 저장(출력에서 이스케이프)", d.ok && d.item.body.includes("<script>"));

r = await worker.fetch(new Request("https://x/comments?page=talk", { headers: { Origin: ORIGIN } }), env);
d = await r.json();
check("최신 글이 맨 위", d.items.length > 1 && d.items[0].id > d.items[d.items.length - 1].id);

/* ---------- 글 지우기 ---------- */
const mine = (await (await worker.fetch(post({ ...good, pw: "비번1234" }, "8.8.8.8"), env)).json()).item.id;

r = await worker.fetch(del(mine, {}), env);
check("비밀번호 없이 삭제 거부", r.status === 400);

r = await worker.fetch(del(mine, { pw: "틀린비번" }), env);
check("틀린 비밀번호 거부", r.status === 403 && rows.some(x => x.id === mine));

r = await worker.fetch(del(mine, { pw: "비번1234" }), env);
check("맞는 비밀번호로 삭제", r.status === 200 && !rows.some(x => x.id === mine));

r = await worker.fetch(del(9999, { pw: "비번1234" }), env);
check("없는 글 삭제 시 404", r.status === 404);

const other = (await (await worker.fetch(post({ ...good, pw: "aaaa" }, "8.8.8.9"), env)).json()).item.id;
for (let i = 0; i < 20; i++) await worker.fetch(del(other, { pw: "zzzz" }, "7.7.7.1"), env);
r = await worker.fetch(del(other, { pw: "aaaa" }, "7.7.7.1"), env);
check("여러 번 틀리면 잠시 막힘", r.status === 429 && rows.some(x => x.id === other));

r = await worker.fetch(del(other, { pw: "아무거나" }, "5.5.5.1", "s3cret"), env);
check("관리자 토큰은 비밀번호 없이 삭제", r.status === 200 && !rows.some(x => x.id === other));

r = await worker.fetch(del(1, { pw: "x" }, "5.5.5.2", "wrong-token"), env);
check("틀린 관리자 토큰은 비밀번호 경로로", r.status === 403 || r.status === 400);

/* ---------- 그 밖 ---------- */
r = await worker.fetch(new Request("https://x/other", { headers: { Origin: ORIGIN } }), env);
check("없는 주소 404", r.status === 404);
r = await worker.fetch(new Request("https://x/comments", { method: "OPTIONS", headers: { Origin: ORIGIN } }), env);
check("프리플라이트 204", r.status === 204);

d = await (await worker.fetch(post({ ...good, pw: "5678" }, "4.4.4.9"), { ...env, MODERATE: "1" })).json();
check("승인 모드", d.ok && d.pending === true && d.item === null);

console.log("통과 " + ok.length + "개");
ok.forEach(x => console.log("  ✓ " + x));
if (bad.length) { console.log("실패 " + bad.length + "개"); bad.forEach(x => console.log("  ✗ " + x)); process.exit(1); }
