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
        <div class="talk__list" id="talk-list"><p class="talk__empty">불러오는 중입니다.</p></div>
        <form class="talk__form" id="talk-form" autocomplete="off">
          <p class="talk__formtitle">글 남기기</p>
          <div class="talk__row">
            <input class="talk__name" id="talk-name" type="text" maxlength="20" placeholder="이름" value="${esc(saved)}" required />
            <input class="talk__pw" id="talk-pw" type="password" minlength="4" maxlength="12"
              placeholder="비밀번호 4~12자" autocomplete="new-password" required />
            <span class="talk__hint">비밀번호는 나중에 이 글을 지울 때 씁니다</span>
          </div>
          <textarea class="talk__body" id="talk-body" rows="4" maxlength="1000"
            placeholder="요즘 하는 작업, 쓰는 툴, 막힌 것, 찾은 레퍼런스. 디자인 얘기면 뭐든 좋습니다." required></textarea>
          <input class="talk__trap" id="talk-web" type="text" tabindex="-1" aria-hidden="true" autocomplete="off" />
          <div class="talk__foot">
            <span class="talk__msg" id="talk-msg" role="status"></span>
            <button class="talk__send" id="talk-send" type="submit">남기기</button>
          </div>
        </form>
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
    const count = document.querySelector('.section__head [data-count]');
    if (count) count.textContent = items.length;
    if (!items.length) {
      box.innerHTML = '<p class="talk__empty">아직 글이 없습니다. 아래에서 처음으로 남겨 보세요.</p>';
      return;
    }
    box.innerHTML = items.map(x => `
      <article class="talk__item" data-id="${x.id}">
        <p class="talk__meta"><b>${esc(x.name)}</b><span>${when(x.at)}</span>
          <button class="talk__del" type="button" data-del="${x.id}">지우기</button></p>
        <p class="talk__text">${bodyHtml(x.body)}</p>
        <form class="talk__delbox" data-form="${x.id}" hidden>
          <input class="talk__pw talk__pw--del" type="password" minlength="4" maxlength="12"
            placeholder="글 쓸 때 정한 비밀번호" autocomplete="off" required />
          <button class="talk__delok" type="submit">삭제</button>
          <button class="talk__delno" type="button" data-cancel="${x.id}">취소</button>
          <span class="talk__msg" data-msg="${x.id}"></span>
        </form>
      </article>`).join('');
    box.querySelectorAll('[data-del]').forEach(b => b.addEventListener('click', () => {
      const f = box.querySelector(`[data-form="${b.dataset.del}"]`);
      f.hidden = !f.hidden;
      if (!f.hidden) f.querySelector('input').focus();
    }));
    box.querySelectorAll('[data-cancel]').forEach(b => b.addEventListener('click', () => {
      box.querySelector(`[data-form="${b.dataset.cancel}"]`).hidden = true;
    }));
    box.querySelectorAll('[data-form]').forEach(f => f.addEventListener('submit', ev => {
      ev.preventDefault();
      wipe(f.dataset.form, f);
    }));
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

  function wipe(id, form) {
    const pw = form.querySelector('input').value;
    const msg = form.querySelector('[data-msg]');
    const btn = form.querySelector('.talk__delok');
    msg.className = 'talk__msg';
    msg.textContent = '';
    btn.disabled = true;

    fetch(TALK_API + '?id=' + encodeURIComponent(id), {
      method: 'DELETE',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ pw: pw }),
    })
      .then(r => r.json())
      .then(d => {
        if (!d || !d.ok) throw new Error((d && d.error) || '지우지 못했습니다.');
        load();
      })
      .catch(err => {
        msg.className = 'talk__msg is-bad';
        msg.textContent = err.message || '지우지 못했습니다.';
      })
      .then(() => { btn.disabled = false; });
  }

  function send(e) {
    e.preventDefault();
    const name = document.getElementById('talk-name');
    const body = document.getElementById('talk-body');
    const pw = document.getElementById('talk-pw');
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
        pw: pw.value,
        website: document.getElementById('talk-web').value,
        elapsed: Date.now() - openedAt,
      }),
    })
      .then(r => r.json())
      .then(d => {
        if (!d || !d.ok) throw new Error((d && d.error) || '남기지 못했습니다.');
        try { localStorage.setItem(NAME_KEY, name.value.trim()); } catch (err) { /* 무시 */ }
        body.value = '';
        pw.value = '';
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
