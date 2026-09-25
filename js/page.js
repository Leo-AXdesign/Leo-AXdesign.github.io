/* 디자인 허브 — 정적 페이지(카테고리 · 읽을거리 · 디자인 잡담 등) 공통 스크립트.
   메인 화면은 app.js 가 같은 일을 합니다.

   - 메뉴의 즐겨찾기 개수를 브라우저 저장소에서 읽어 채웁니다
   - 좁은 화면에서 햄버거 버튼으로 메뉴 서랍을 엽니다
   - 서랍 안의 테마 전환 · 목록/격자 버튼 (메인 화면과 같은 저장소 값을 씁니다) */
(function () {
  'use strict';

  /* ---------- 즐겨찾기 개수 ---------- */
  try {
    const raw = localStorage.getItem('designhub:bookmarks');
    const n = raw ? JSON.parse(raw).length : 0;
    document.querySelectorAll('[data-bm-count]').forEach(el => { el.textContent = n; });
  } catch (e) { /* 저장소를 못 쓰는 환경이면 0 으로 둡니다 */ }

  /* ---------- 모바일 메뉴 ---------- */
  const drawer = document.getElementById('drawer');
  const openBtn = document.getElementById('menu-open');
  const closeBtn = document.getElementById('menu-close');
  if (!drawer || !openBtn || !closeBtn) return;

  let lastFocus = null;

  function open() {
    lastFocus = document.activeElement;
    drawer.hidden = false;
    // 다음 프레임에 클래스를 붙여야 열리는 움직임이 보입니다
    requestAnimationFrame(() => drawer.classList.add('is-open'));
    document.body.classList.add('drawer-open');
    openBtn.setAttribute('aria-expanded', 'true');
    closeBtn.focus();
  }

  function close() {
    if (drawer.hidden) return;
    drawer.classList.remove('is-open');
    document.body.classList.remove('drawer-open');
    openBtn.setAttribute('aria-expanded', 'false');
    setTimeout(() => { drawer.hidden = true; }, 260);
    if (lastFocus && lastFocus.focus) lastFocus.focus();
  }

  /* ---------- 보기: 테마 · 목록/격자 ---------- */
  function load(k) { try { return localStorage.getItem(k); } catch (e) { return null; } }
  function save(k, v) { try { localStorage.setItem(k, v); } catch (e) { /* 무시 */ } }

  const themeBtn = document.getElementById('drawer-theme');
  if (themeBtn) themeBtn.addEventListener('click', () => {
    const next = document.documentElement.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
    if (next === 'dark') document.documentElement.setAttribute('data-theme', 'dark');
    else document.documentElement.removeAttribute('data-theme');
    save('designhub:theme', next);
  });

  // 목록/격자는 메인 화면의 보기 방식이라, 고르면 저장하고 메인으로 갑니다
  const view = load('designhub:view') === 'list' ? 'list' : 'grid';
  drawer.querySelectorAll('.drawer__opt[data-view]').forEach(b => {
    b.classList.toggle('is-active', b.dataset.view === view);
    b.addEventListener('click', () => {
      save('designhub:view', b.dataset.view);
      location.href = 'https://designrefs.com/';
    });
  });

  openBtn.addEventListener('click', open);
  closeBtn.addEventListener('click', close);
  document.getElementById('drawer-backdrop').addEventListener('click', close);
  document.addEventListener('keydown', e => { if (e.key === 'Escape') close(); });
})();
