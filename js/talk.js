/* 디자인 허브 — 이야기 페이지의 글 목록과 입력칸.
   서버는 worker/ 폴더의 Cloudflare Worker 입니다.

   ★ 워커를 배포한 뒤, 아래 주소를 받은 주소로 바꾸세요.
     (npx wrangler deploy 를 하면 터미널에 주소가 찍힙니다) */
const TALK_API = 'https://designrefs-talk.designrefs-talk.workers.dev/comments';

(function () {
  'use strict';

  const PAGE = 'talk';
  const NAME_KEY = 'designhub:talkname';
  const root = document.getElementById('talk');
  if (!root) return;

  const openedAt = Date.now();
  const ready = !/여기를-바꾸세요/.test(TALK_API);

  function esc(s) {
    return String(s)
      .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;').replace(/'/g, '&#39;');
  }
  /* 줄바꿈은 살리고 태그는 살리지 않습니다 */
  function bodyHtml(s) { return esc(s).replace(/\n/g, '<br />'); }

  function when(ms) {
    const gap = Date.now() - ms;
    if (gap < 60000) return '방금';
    if (gap < 3600000) return Math.floor(gap / 60000) + '분 전';
    if (gap < 86400000) return Math.floor(gap / 3600000) + '시간 전';
    if (gap < 7 * 86400000) return Math.floor(gap / 86400000) + '일 전';
    const d = new Date(ms);
    return d.getFullYear() + '. ' + (d.getMonth() + 1) + '. ' + d.getDate();
  }

  function view() {
    const saved = (function () { try { return localStorage.getItem(NAME_KEY) || ''; } catch (e) { return ''; } })();
    root.innerHTML = `
      <div class="talk">
        <form class="talk__form" id="talk-form" autocomplete="off">
          <div class="talk__row">
            <input class="talk__name" id="talk-name" type="text" maxlength="20" placeholder="이름" value="${esc(saved)}" required />
            <span class="talk__hint">이름만 적으면 됩니다. 가입도 로그인도 없습니다.</span>
          </div>
          <textarea class="talk__body" id="talk-body" rows="4" maxlength="1000"
            placeholder="빠진 사이트 제보, 안 열리는 링크, 글에 대한 의견, 아무 이야기나 남겨 주세요." required></textarea>
          <input class="talk__trap" id="talk-web" type="text" tabindex="-1" aria-hidden="true" autocomplete="off" />
          <div class="talk__foot">
            <span class="talk__msg" id="talk-msg" role="status"></span>
            <button class="talk__send" id="talk-send" type="submit">남기기</button>
          </div>
        </form>
        <div class="talk__list" id="talk-list"><p class="talk__empty">불러오는 중입니다.</p></div>
      </div>`;
    document.getElementById('talk-form').addEventListener('submit', send);
  }

  function offline(reason) {
    root.innerHTML = `
      <div class="talk">
        <p class="ptext">${esc(reason)}</p>
        <p class="ptext">그동안은 메일로 받겠습니다.
          <a href="mailto:nisov0924@gmail.com">nisov0924@gmail.com</a></p>
      </div>`;
  }

  function draw(items) {
    const box = document.getElementById('talk-list');
    if (!box) return;
    if (!items.length) {
      box.innerHTML = '<p class="talk__empty">아직 남겨진 이야기가 없습니다. 처음으로 남겨 보세요.</p>';
      return;
    }
    box.innerHTML = `<p class="talk__count">${items.length}개의 이야기</p>` + items.map(x => `
      <article class="talk__item">
        <p class="talk__meta"><b>${esc(x.name)}</b><span>${when(x.at)}</span></p>
        <p class="talk__text">${bodyHtml(x.body)}</p>
      </article>`).join('');
  }

  function load() {
    fetch(TALK_API + '?page=' + encodeURIComponent(PAGE), { headers: { Accept: 'application/json' } })
      .then(r => r.json())
      .then(d => { if (d && d.ok) draw(d.items || []); else throw new Error(); })
      .catch(() => {
        const box = document.getElementById('talk-list');
        if (box) box.innerHTML = '<p class="talk__empty">이야기를 불러오지 못했습니다. 잠시 뒤에 새로고침 해 주세요.</p>';
      });
  }

  function send(e) {
    e.preventDefault();
    const name = document.getElementById('talk-name');
    const body = document.getElementById('talk-body');
    const btn = document.getElementById('talk-send');
    const msg = document.getElementById('talk-msg');
    msg.className = 'talk__msg';
    msg.textContent = '';
    btn.disabled = true;

    fetch(TALK_API, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        page: PAGE,
        name: name.value.trim(),
        body: body.value.trim(),
        website: document.getElementById('talk-web').value,
        elapsed: Date.now() - openedAt,
      }),
    })
      .then(r => r.json())
      .then(d => {
        if (!d || !d.ok) throw new Error((d && d.error) || '남기지 못했습니다.');
        try { localStorage.setItem(NAME_KEY, name.value.trim()); } catch (err) { /* 무시 */ }
        body.value = '';
        msg.className = 'talk__msg is-ok';
        msg.textContent = d.pending ? '확인 후 올라갑니다. 고맙습니다.' : '올렸습니다. 고맙습니다.';
        load();
      })
      .catch(err => {
        msg.className = 'talk__msg is-bad';
        msg.textContent = err.message || '남기지 못했습니다.';
      })
      .then(() => { btn.disabled = false; });
  }

  if (!ready) {
    offline('이야기 공간을 준비하고 있습니다.');
    return;
  }
  view();
  load();
})();
