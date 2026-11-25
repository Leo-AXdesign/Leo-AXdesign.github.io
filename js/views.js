/**
 * 읽을거리 조회수.
 * 글 페이지의 <span data-views> 에 "조회 123" 을 채웁니다.
 * 한 사람이 같은 글을 하루에 여러 번 열어도 서버에서 1번만 셉니다.
 * 서버에 닿지 않으면 아무것도 보이지 않고 넘어갑니다.
 */
(function () {
  var VIEWS_API = 'https://designrefs-talk.designrefs-talk.workers.dev/views';
  var box = document.querySelector('[data-views]');
  if (!box) return;
  var path = location.pathname.replace(/index\.html$/, '');
  if (!/\/$/.test(path)) path += '/';
  var en = document.documentElement.lang === 'en';

  // 같은 탭에서 새로고침할 때는 다시 올리지 않고 읽기만 합니다
  var key = 'viewed:' + path, seen = false;
  try { seen = sessionStorage.getItem(key) === '1'; } catch (e) { /* 저장소를 못 쓰는 브라우저 */ }

  var req = seen
    ? fetch(VIEWS_API + '?path=' + encodeURIComponent(path))
    : fetch(VIEWS_API, { method: 'POST', headers: { 'Content-Type': 'application/json' },
                         body: JSON.stringify({ path: path }), keepalive: true });

  req.then(function (r) { return r.json(); }).then(function (d) {
    if (!d || !d.ok || !d.n) return;
    try { sessionStorage.setItem(key, '1'); } catch (e) { /* 무시 */ }
    var n = d.n.toLocaleString(en ? 'en-US' : 'ko-KR');
    box.textContent = en ? ' · ' + n + (d.n === 1 ? ' view' : ' views') : ' · 조회 ' + n;
    box.hidden = false;
  }).catch(function () { /* 서버가 아직 준비되지 않았을 때 */ });
})();
