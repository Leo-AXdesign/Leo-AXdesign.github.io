/* =========================================================
   스타일 현상소 (/lab/)
   - 사진을 스타일 사전의 양식으로 '현상'합니다. 모든 처리는 브라우저 안에서만 합니다.
     사진과 결과를 어디에도 보내지 않습니다. 글자를 얹는 기능은 두지 않습니다(사진 자체를 바꾸는 도구).
   - 처리 순서: 구도(확대·이동·뒤집기) → 분석(작은 크기, 보정·면 정리) → 양식 그리기(저장 크기)
                → 마감(원본 섞기·입자·종이·가장자리) → 테두리 → 사이트 표시
   - 패널은 기본 항목을 먼저 보여 주고, adv: true 인 항목과 공통 옵션은 '더 다듬기'를 펼쳐야 보입니다.
   - 양식 하나 = STYLES 의 객체 하나 (조절 항목 + 색 조합 + prep + render). 새 양식은 하나 더하면 됩니다.
   - 크기에 따라 달라지는 값은 폭 1000px 기준이고 s(= W/1000)를 곱합니다. 미리보기와 저장 결과가 같은 모양이 됩니다.
   ========================================================= */
(() => {
  const $ = q => document.querySelector(q);
  const root = $('#lab');
  if (!root) return;

  const PREVIEW_MAX = 1100;   // 화면 미리보기의 긴 변
  const ANALYZE_MAX = 1000;   // 분석(보정·면 정리·색 뽑기)의 긴 변. 휴대폰 메모리를 생각해 작게
  const THUMB = 180;          // 양식 카드 미리보기의 긴 변
  const FONT = '"Pretendard Variable", Pretendard, -apple-system, "Apple SD Gothic Neo", sans-serif';
  const RATIOS = { '4:5': [4, 5], '9:16': [9, 16], '1:1': [1, 1], '3:4': [3, 4], '16:9': [16, 9], '원본': null };
  const SAVE_SIZES = { '인스타 1080': 1080, '2K': 2048, '최대': 3000 };
  const DEMOS = [
    { src: '/assets/lab/demo-portrait.webp', label: '인물' },
    { src: '/assets/lab/demo-cafe.webp', label: '카페' },
  ];

  /* ================= 작은 도구들 ================= */
  const clamp = (v, a = 0, b = 1) => (v < a ? a : v > b ? b : v);
  const smooth = (a, b, v) => { const t = clamp((v - a) / (b - a)); return t * t * (3 - 2 * t); };
  const rgb = h => { const n = parseInt(h.slice(1), 16); return [(n >> 16) & 255, (n >> 8) & 255, n & 255]; };
  const css = c => `rgb(${c[0] | 0},${c[1] | 0},${c[2] | 0})`;
  const hash = (x, y, s) => { let h = (x * 374761393 + y * 668265263 + s * 982451653) | 0; h = Math.imul(h ^ (h >>> 13), 1274126177); return ((h ^ (h >>> 16)) >>> 0) / 4294967296; };
  function vnoise(x, y, s) {
    const xi = Math.floor(x), yi = Math.floor(y), xf = x - xi, yf = y - yi;
    const u = xf * xf * (3 - 2 * xf), v = yf * yf * (3 - 2 * yf);
    const a = hash(xi, yi, s), b = hash(xi + 1, yi, s), c = hash(xi, yi + 1, s), d = hash(xi + 1, yi + 1, s);
    return a + (b - a) * u + (c - a) * v + (a - b - c + d) * u * v;
  }
  const canvas = (w, h) => { const c = document.createElement('canvas'); c.width = Math.max(1, Math.round(w)); c.height = Math.max(1, Math.round(h)); return c; };
  const ctx2d = c => c.getContext('2d', { willReadFrequently: true });
  const pick = a => a[Math.floor(Math.random() * a.length)];
  // 같은 seed 면 같은 배치가 나오는 난수 (미리보기와 저장 결과가 같아야 하니까)
  const rng = seed => { let a = (seed * 2654435761) >>> 0; return () => { a = (a + 0x6D2B79F5) >>> 0; let t = Math.imul(a ^ (a >>> 15), a | 1); t ^= t + Math.imul(t ^ (t >>> 7), t | 61); return ((t ^ (t >>> 14)) >>> 0) / 4294967296; }; };
  const newSeed = () => 1 + Math.floor(Math.random() * 1e6);

  /* ---------- 구도: 확대·이동·뒤집기를 반영해 w×h 로 자르기 ---------- */
  function cover(img, w, h, g) {
    const c = canvas(w, h), x = ctx2d(c);
    const sc = Math.max(w / img.width, h / img.height) * g.zoom, dw = img.width * sc, dh = img.height * sc;
    const ox = (w - dw) / 2 - g.px * (dw - w) / 2, oy = (h - dh) / 2 - g.py * (dh - h) / 2;
    x.imageSmoothingQuality = 'high';
    if (g.flip) { x.translate(w, 0); x.scale(-1, 1); }
    x.drawImage(img, g.flip ? w - ox - dw : ox, oy, dw, dh);
    return c;
  }

  /* ---------- 분석: 보정 → 면 정리 ---------- */
  function autoLevels(d) {
    const hist = new Uint32Array(256), n = d.length / 4;
    for (let i = 0; i < d.length; i += 4) hist[(0.2126 * d[i] + 0.7152 * d[i + 1] + 0.0722 * d[i + 2]) | 0]++;
    let lo = 0, hi = 255, acc = 0;
    for (; lo < 255; lo++) { acc += hist[lo]; if (acc > n * 0.01) break; }
    acc = 0;
    for (; hi > 0; hi--) { acc += hist[hi]; if (acc > n * 0.01) break; }
    const k = 255 / Math.max(30, hi - lo);
    for (let i = 0; i < d.length; i += 4) for (let c = 0; c < 3; c++) d[i + c] = (d[i + c] - lo) * k;
  }
  // 밝기·대비·채도 (사용자가 '사진' 구역에서 고른 값)
  function adjust(d, g) {
    if (!g.bright && !g.contrast && !g.sat) return;
    const ct = 1 + g.contrast, bt = g.bright * 128, st = 1 + g.sat;
    for (let i = 0; i < d.length; i += 4) {
      const l = 0.2126 * d[i] + 0.7152 * d[i + 1] + 0.0722 * d[i + 2];
      for (let c = 0; c < 3; c++) d[i + c] = ((l + (d[i + c] - l) * st) - 128) * ct + 128 + bt;
    }
  }

  // 쿠와하라 필터: 경계는 살리고 면은 평평하게. 적분 영상으로 계산해서 반경이 커져도 빠릅니다
  function kuwahara(d, w, h, r) {
    if (r < 1) return d;
    const W1 = w + 1, N = W1 * (h + 1);
    const sR = new Float64Array(N), sG = new Float64Array(N), sB = new Float64Array(N), sL = new Float64Array(N), sQ = new Float64Array(N);
    for (let y = 0; y < h; y++) {
      let r0 = 0, g0 = 0, b0 = 0, l0 = 0, q0 = 0;
      for (let x = 0; x < w; x++) {
        const i = (y * w + x) * 4, l = 0.2126 * d[i] + 0.7152 * d[i + 1] + 0.0722 * d[i + 2];
        r0 += d[i]; g0 += d[i + 1]; b0 += d[i + 2]; l0 += l; q0 += l * l;
        const j = (y + 1) * W1 + x + 1, u = y * W1 + x + 1;
        sR[j] = sR[u] + r0; sG[j] = sG[u] + g0; sB[j] = sB[u] + b0; sL[j] = sL[u] + l0; sQ[j] = sQ[u] + q0;
      }
    }
    const box = (S, x0, y0, x1, y1) => S[y1 * W1 + x1] - S[y0 * W1 + x1] - S[y1 * W1 + x0] + S[y0 * W1 + x0];
    const out = new Uint8ClampedArray(d.length);
    for (let y = 0; y < h; y++) for (let x = 0; x < w; x++) {
      let best = Infinity, br = 0, bg = 0, bb = 0;
      for (let q = 0; q < 4; q++) {
        const x0 = q & 1 ? x : Math.max(0, x - r), x1 = q & 1 ? Math.min(w, x + r + 1) : x + 1;
        const y0 = q & 2 ? y : Math.max(0, y - r), y1 = q & 2 ? Math.min(h, y + r + 1) : y + 1;
        const n = (x1 - x0) * (y1 - y0), m = box(sL, x0, y0, x1, y1) / n;
        const v = box(sQ, x0, y0, x1, y1) / n - m * m;
        if (v < best) { best = v; br = box(sR, x0, y0, x1, y1) / n; bg = box(sG, x0, y0, x1, y1) / n; bb = box(sB, x0, y0, x1, y1) / n; }
      }
      const i = (y * w + x) * 4;
      out[i] = br; out[i + 1] = bg; out[i + 2] = bb; out[i + 3] = 255;
    }
    return out;
  }
  function lumaOf(d) {
    const L = new Float32Array(d.length / 4);
    for (let i = 0, j = 0; j < L.length; i += 4, j++) L[j] = (0.2126 * d[i] + 0.7152 * d[i + 1] + 0.0722 * d[i + 2]) / 255;
    return L;
  }
  function boxBlur(L, w, h, r) {
    const t = new Float32Array(L.length), o = new Float32Array(L.length), n = 2 * r + 1;
    for (let y = 0; y < h; y++) {
      let acc = 0;
      for (let x = -r; x <= r; x++) acc += L[y * w + clamp(x, 0, w - 1)];
      for (let x = 0; x < w; x++) { t[y * w + x] = acc / n; acc += L[y * w + Math.min(x + r + 1, w - 1)] - L[y * w + Math.max(x - r, 0)]; }
    }
    for (let x = 0; x < w; x++) {
      let acc = 0;
      for (let y = -r; y <= r; y++) acc += t[clamp(y, 0, h - 1) * w + x];
      for (let y = 0; y < h; y++) { o[y * w + x] = acc / n; acc += t[Math.min(y + r + 1, h - 1) * w + x] - t[Math.max(y - r, 0) * w + x]; }
    }
    return o;
  }
  // 분석본: { w, h, d(RGBA), L } — 저장 크기와 상관없이 작게 만듭니다
  function analyze(src, kuwa, g) {
    const k = Math.min(1, ANALYZE_MAX / Math.max(src.width, src.height));
    const w = Math.round(src.width * k), h = Math.round(src.height * k);
    const c = canvas(w, h), x = ctx2d(c);
    x.imageSmoothingQuality = 'high'; x.drawImage(src, 0, 0, w, h);
    let d = x.getImageData(0, 0, w, h).data;
    if (g.auto) autoLevels(d);
    adjust(d, g);
    if (kuwa) d = kuwahara(d, w, h, Math.max(1, Math.round(kuwa * w / 1000)));
    return { w, h, d, L: lumaOf(d) };
  }
  function sampler(A, W, H) {
    const fx = (A.w - 1) / Math.max(1, W - 1), fy = (A.h - 1) / Math.max(1, H - 1);
    return (arr, x, y) => {
      const ax = clamp(x * fx, 0, A.w - 1), ay = clamp(y * fy, 0, A.h - 1);
      const x0 = ax | 0, y0 = ay | 0, x1 = Math.min(x0 + 1, A.w - 1), y1 = Math.min(y0 + 1, A.h - 1), tx = ax - x0, ty = ay - y0;
      const a = arr[y0 * A.w + x0], b = arr[y0 * A.w + x1], c = arr[y1 * A.w + x0], e = arr[y1 * A.w + x1];
      return (a + (b - a) * tx) * (1 - ty) + (c + (e - c) * tx) * ty;
    };
  }
  function edges(L, w, h) {
    const E = new Float32Array(L.length);
    for (let y = 1; y < h - 1; y++) for (let x = 1; x < w - 1; x++) {
      const i = y * w + x;
      const gx = -L[i - w - 1] - 2 * L[i - 1] - L[i + w - 1] + L[i - w + 1] + 2 * L[i + 1] + L[i + w + 1];
      const gy = -L[i - w - 1] - 2 * L[i - w] - L[i - w + 1] + L[i + w - 1] + 2 * L[i + w] + L[i + w + 1];
      E[i] = Math.sqrt(gx * gx + gy * gy);
    }
    return E;
  }

  /* ---------- 망점 ----------
     shape: '원'(동그란 점) · '선'(평행선) · '입자'(무작위 입자). 반환 함수: (x, y, 농도함수) → 0~1 덮임 */
  function screen(cell, angle, shape = '원', seed = 1) {
    const ca = Math.cos(angle), sa = Math.sin(angle), gs = Math.max(1.5, cell * 0.38);
    // 입자: 칸마다 정해진 문턱값보다 진하면 찍힘. 문턱값을 약간 위로 몰아 밝은 곳이 깨끗하게 남도록
    if (shape === '입자') return (x, y, at) => (at(x, y) > 0.08 + 0.92 * hash((x / gs) | 0, (y / gs) | 0, seed) ? 1 : 0);
    return (x, y, at) => {
      const u = (x * ca + y * sa) / cell, v = (-x * sa + y * ca) / cell;
      const cu = Math.round(u), cv = Math.round(v);
      if (shape === '선') {
        const cx = x - (v - cv) * cell * -sa, cy = y - (v - cv) * cell * ca;
        const dd = at(cx, cy); if (dd <= 0.002) return 0;
        return clamp(cell * 0.5 * dd * 1.05 - Math.abs(v - cv) * cell + 0.5);
      }
      const cx = (cu * ca - cv * sa) * cell, cy = (cu * sa + cv * ca) * cell;
      const dd = at(cx, cy); if (dd <= 0.002) return 0;
      return clamp(cell * 0.5 * Math.sqrt(dd) * 1.18 - Math.hypot((u - cu) * cell, (v - cv) * cell) + 0.5);
    };
  }

  /* ---------- 글자 (사이트 표시용) ---------- */
  function setFont(x, weight, size, spacing = 0) {
    x.font = `${weight} ${Math.round(size)}px ${FONT}`;
    if ('letterSpacing' in x) x.letterSpacing = `${(size * spacing).toFixed(1)}px`;
  }
  function resetText(x) { x.textAlign = 'left'; x.textBaseline = 'alphabetic'; if ('letterSpacing' in x) x.letterSpacing = '0px'; }
  const mixInk = (r, g, b, ink, k) => [r * (1 - k * (1 - ink[0] / 255)), g * (1 - k * (1 - ink[1] / 255)), b * (1 - k * (1 - ink[2] / 255))];

  // 색이 필요한 양식은 분석본에 R·G·B 를 따로 둡니다 (sampler 로 한 채널씩 읽으려고)
  function withRGB(A) {
    const n = A.w * A.h; A.R = new Float32Array(n); A.G = new Float32Array(n); A.B = new Float32Array(n);
    for (let i = 0, j = 0; j < n; i += 4, j++) { A.R[j] = A.d[i]; A.G[j] = A.d[i + 1]; A.B[j] = A.d[i + 2]; }
    return A;
  }
  // 그림을 상자에 꽉 차게. bias 는 세로로 어디를 남길지 (0 위 · 0.5 가운데). 얼굴은 대개 위쪽에 있어서 틀 안에서는 위를 남깁니다
  function fitInto(x, src, bx, by, bw, bh, bias = 0.5) {
    const k = Math.max(bw / src.width, bh / src.height), dw = src.width * k, dh = src.height * k;
    x.drawImage(src, bx + (bw - dw) / 2, by + (bh - dh) * bias, dw, dh);
  }
  // VHS: 빨강·파랑이 옆으로 번지고, 주사선과 아래쪽 트래킹 띠, 노이즈
  function vhs(x, W, H, p, s) {
    if (p.vhs <= 0 && p.noise <= 0) return;
    const im = x.getImageData(0, 0, W, H), d = im.data, src = new Uint8ClampedArray(d);
    const off = Math.round((1 + 7 * p.vhs) * s), line = Math.max(2, Math.round(3 * s));
    const bands = [[0.83, 0.03], [0.91, 0.01]];
    for (let y = 0; y < H; y++) {
      let shift = 0, hot = 0;
      for (const [a, b] of bands) if (p.vhs > 0 && Math.abs(y / H - a) < b) { shift = Math.round((hash((y / (2 * s)) | 0, 3, 71) - 0.5) * W * 0.05 * p.vhs); hot = 1; }
      const sc = (y / line | 0) % 2 ? 1 : 1 - p.vhs * 0.2, row = y * W;
      for (let xx = 0; xx < W; xx++) {
        const sx = clamp(xx + shift, 0, W - 1), i = (row + xx) * 4;
        const r = src[(row + clamp(sx - off, 0, W - 1)) * 4], g = src[(row + sx) * 4 + 1], b = src[(row + clamp(sx + off, 0, W - 1)) * 4 + 2];
        const nz = (hash(xx, y, 73) - 0.5) * 36 * p.noise + (hot ? (hash(xx, y, 79) - 0.5) * 110 * p.vhs : 0);
        d[i] = r * sc + nz; d[i + 1] = g * sc + nz; d[i + 2] = b * sc + nz;
      }
    }
    x.putImageData(im, 0, 0);
  }
  // 번짐: 작게 줄였다 키운 사본을 '스크린'으로 겹칩니다 (ctx.filter 없는 사파리에서도 같게)
  function bloom(x, W, H, k) {
    const sm = canvas(W / 14, H / 14), smx = ctx2d(sm);
    smx.imageSmoothingQuality = 'high'; smx.drawImage(x.canvas, 0, 0, sm.width, sm.height);
    x.save(); x.globalCompositeOperation = 'screen'; x.globalAlpha = k; x.imageSmoothingQuality = 'high';
    x.drawImage(sm, 0, 0, W, H); x.restore();
  }

  /* ================= 양식들 ================= */
  const STYLES = [
    {
      id: 'riso', name: '리소그래프', thumb: 'risograph',
      note: '형광 잉크를 한 색씩 찍어 겹친 인쇄. 종이의 흰 바탕, 굵은 망점, 판 어긋남이 남습니다.',
      controls: [
        { key: 'cell', label: '망점 크기', min: 4, max: 16, step: 1, value: 7 },
        { key: 'shift', label: '판 어긋남', min: 0, max: 16, step: 1, value: 5 },
        { key: 'ink', label: '잉크 양', min: 0.6, max: 1.4, step: 0.05, value: 1 },
        { key: 'inks', label: '잉크 수', type: 'choice', options: ['2색', '3색'], value: '2색', adv: true },
        { key: 'shape', label: '망점 모양', type: 'choice', options: ['원', '선', '입자'], value: '원', adv: true },
        { key: 'angle', label: '망점 각도', min: 0, max: 90, step: 5, value: 15, adv: true },
        { key: 'paperTone', label: '종이', type: 'choice', options: ['흰 종이', '크림', '회색'], value: '크림', adv: true },
        { key: 'blot', label: '잉크 얼룩', min: 0, max: 1, step: 0.05, value: 0.5, adv: true },
      ],
      slots: ['밝은 잉크', '어두운 잉크', '셋째 잉크'],
      palettes: [
        { name: '핑크 + 블루', colors: ['#ff48b0', '#0078bf', '#ffe800'] },
        { name: '오렌지 + 틸', colors: ['#ff6c2f', '#00838a', '#ffe800'] },
        { name: '옐로 + 블루', colors: ['#ffd800', '#3255a4', '#ff48b0'] },
        { name: '레드 + 블랙', colors: ['#ff665e', '#1d1d1d', '#ffd800'] },
        { name: '핑크 + 퍼플', colors: ['#ff48b0', '#4b2a8f', '#ffe800'] },
      ],
      prep: (src, p, g) => analyze(src, 2, g),
      render(c, A, W, H, p, s) {
        const S = sampler(A, W, H), [inkA, inkB, inkC] = p.colors.map(rgb), three = p.inks === '3색';
        const n = A.w * A.h, dA = new Float32Array(n), dB = new Float32Array(n), dC = three ? new Float32Array(n) : null;
        for (let i = 0; i < n; i++) {
          const l = A.L[i], warm = (A.d[i * 4] - A.d[i * 4 + 2]) / 255;
          dA[i] = clamp(smooth(0.93, 0.42, l) * 0.78 + clamp(warm * 1.6) * 0.32 * smooth(0.98, 0.6, l)) * p.ink;
          dB[i] = clamp(smooth(0.5, 0.06, l) * 1.1) * p.ink;
          if (three) dC[i] = clamp(smooth(0.99, 0.7, l) * 0.55 * (1 - smooth(0.45, 0.2, l)) + clamp(warm) * 0.2) * p.ink;
        }
        const cell = p.cell * s, off = p.shift * s, a0 = p.angle * Math.PI / 180;
        const sA = screen(cell, a0 + Math.PI / 3, p.shape, 1), sB = screen(cell, a0, p.shape, 2), sC = screen(cell, a0 + Math.PI / 4 * 0.5, p.shape, 3);
        const atA = (x, y) => S(dA, x - off * 0.6, y - off * 0.3), atB = (x, y) => S(dB, x + off * 0.4, y + off * 0.5), atC = (x, y) => S(dC, x - off * 0.2, y + off * 0.6);
        const paper = { '흰 종이': [250, 249, 245], '크림': [246, 242, 233], '회색': [228, 226, 221] }[p.paperTone];
        const im = c.createImageData(W, H), d = im.data, gk = 1 / (3 * s);
        for (let y = 0; y < H; y++) for (let x = 0; x < W; x++) {
          const blot = 1 - p.blot * 0.36 * (1 - vnoise(x * gk * 0.06, y * gk * 0.06, 3)), grain = hash(x, y, 7);
          let r = paper[0] - grain * 7, gg = paper[1] - grain * 7, b = paper[2] - grain * 8;
          if (three) { const a3 = sC(x, y, atC) * blot; if (a3 > 0) [r, gg, b] = mixInk(r, gg, b, inkC, a3 * 0.9); }
          const a1 = sA(x, y, atA) * blot * (grain > 0.06 ? 1 : 0.4); if (a1 > 0) [r, gg, b] = mixInk(r, gg, b, inkA, a1 * 0.92);
          const a2 = sB(x, y, atB) * blot * (grain < 0.94 ? 1 : 0.4); if (a2 > 0) [r, gg, b] = mixInk(r, gg, b, inkB, a2 * 0.9);
          const i = (y * W + x) * 4;
          d[i] = r; d[i + 1] = gg; d[i + 2] = b; d[i + 3] = 255;
        }
        c.putImageData(im, 0, 0);
      },
    },

    {
      id: 'pop', name: '팝아트', thumb: 'pop-art',
      note: '평평하게 칠한 원색 면, 굵은 검정 윤곽, 만화 인쇄의 망점(벤데이 점).',
      controls: [
        { key: 'simplify', label: '단순하게', min: 3, max: 12, step: 1, value: 8 },
        { key: 'cell', label: '망점 크기', min: 6, max: 22, step: 1, value: 11 },
        { key: 'line', label: '윤곽 굵기', min: 0, max: 3, step: 1, value: 2 },
        { key: 'dotWhere', label: '망점 자리', type: 'choice', options: ['중간톤', '밝은 곳', '없음'], value: '중간톤', adv: true },
        { key: 'shape', label: '망점 모양', type: 'choice', options: ['원', '선'], value: '원', adv: true },
        { key: 'bias', label: '어두운 면', min: -0.15, max: 0.15, step: 0.01, value: 0, adv: true },
      ],
      slots: ['윤곽·그림자', '어두운 면', '망점', '밝은 면', '바탕'],
      palettes: [
        { name: '만화 원색', colors: ['#121212', '#1450c8', '#e8222e', '#ffd21f', '#fffaee'] },
        { name: '실크스크린', colors: ['#1b1b1b', '#00a3a1', '#ff3d8b', '#ffb000', '#fff6e8'] },
        { name: '흑백 + 빨강', colors: ['#111111', '#5a5a5a', '#e4002b', '#d9d9d9', '#fbf8f2'] },
        { name: '레트로 만화', colors: ['#2b1d16', '#3f6f8f', '#e0533a', '#f2c14e', '#f4ead5'] },
        { name: '네온', colors: ['#120c1e', '#5b2bff', '#ff2e88', '#29f0c5', '#fff7fb'] },
      ],
      prep(src, p, g) {
        const A = analyze(src, p.simplify, g);
        A.L = boxBlur(A.L, A.w, A.h, Math.max(1, Math.round(3 * A.w / 1000)));
        A.E = edges(A.L, A.w, A.h);
        return A;
      },
      render(c, A, W, H, p, s) {
        const S = sampler(A, W, H), [ink, deep, dotC, light, paper] = p.colors.map(rgb);
        const scr = screen(p.cell * s, 45 * Math.PI / 180, p.shape), flat = () => 0.42, b = p.bias;
        let E = A.E;
        if (p.line > 0) {
          const t = new Float32Array(E.length), rr = p.line;
          for (let y = 0; y < A.h; y++) for (let x = 0; x < A.w; x++) {
            let m = 0;
            for (let dy = -rr; dy <= rr; dy++) for (let dx = -rr; dx <= rr; dx++) {
              if (dx * dx + dy * dy > rr * rr + 1) continue;
              const v = E[clamp(y + dy, 0, A.h - 1) * A.w + clamp(x + dx, 0, A.w - 1)];
              if (v > m) m = v;
            }
            t[y * A.w + x] = m;
          }
          E = t;
        }
        const im = c.createImageData(W, H), d = im.data;
        for (let y = 0; y < H; y++) for (let x = 0; x < W; x++) {
          const l = S(A.L, x, y);
          let col;
          if (l < 0.24 + b) col = ink;
          else if (l < 0.46 + b) col = deep;
          else if (l < 0.7) col = p.dotWhere === '중간톤' && scr(x, y, flat) > 0.5 ? dotC : (p.dotWhere === '중간톤' ? paper : dotC);
          else if (l < 0.86) col = p.dotWhere === '밝은 곳' && scr(x, y, flat) > 0.5 ? dotC : light;
          else col = paper;
          if (p.line > 0 && S(E, x, y) > 0.55) col = ink;
          const i = (y * W + x) * 4;
          d[i] = col[0]; d[i + 1] = col[1]; d[i + 2] = col[2]; d[i + 3] = 255;
        }
        c.putImageData(im, 0, 0);
      },
    },

    {
      id: 'pixel', name: '픽셀 아트', thumb: 'pixel-art',
      note: '큰 픽셀과 적은 색. 경계는 계단처럼, 윤곽은 한 단계 어둡게.',
      controls: [
        { key: 'cells', label: '가로 칸 수', min: 24, max: 128, step: 4, value: 60 },
        { key: 'ncolors', label: '색 수', min: 3, max: 16, step: 1, value: 8 },
        { key: 'outline', label: '윤곽', min: 0, max: 1, step: 0.05, value: 0.75 },
        { key: 'dither', label: '디더', type: 'choice', options: ['없음', '격자', '오차 확산'], value: '없음', adv: true },
        { key: 'shape', label: '픽셀 모양', type: 'choice', options: ['네모', '둥근 점', 'LED'], value: '네모', adv: true },
        { key: 'grid', label: '격자선', type: 'toggle', value: false, adv: true },
      ],
      slots: null,   // 사진에서 뽑는 색이라 직접 고르기 대신 팔레트만
      palettes: [
        { name: '사진에서 뽑은 색', colors: ['#c94f4f', '#e8b04a', '#4f8a5b', '#3d5a99', '#2a2a2a'], adaptive: true },
        { name: '16색 게임기', colors: ['#000000', '#1d2b53', '#7e2553', '#008751', '#ab5236', '#5f574f', '#c2c3c7', '#fff1e8', '#ff004d', '#ffa300', '#ffec27', '#00e436', '#29adff', '#83769c', '#ff77a8', '#ffccaa'] },
        { name: '게임보이', colors: ['#0f380f', '#306230', '#8bac0f', '#c4d97a'], ramp: true },
        { name: '흑백 1비트', colors: ['#141414', '#f2efe6'], ramp: true },
        { name: '노을 5색', colors: ['#1a1033', '#5a2a6e', '#c4456a', '#f59c5b', '#ffe3a3'], ramp: true },
      ],
      prep: (src, p, g) => analyze(src, 5, g),
      render(c, A, W, H, p) {
        const gw = Math.round(p.cells), px = W / gw, gh = Math.max(1, Math.round(H / px));
        const small = canvas(gw, gh), sx = ctx2d(small);
        const a = canvas(A.w, A.h); ctx2d(a).putImageData(new ImageData(A.d, A.w, A.h), 0, 0);
        sx.imageSmoothingQuality = 'high'; sx.drawImage(a, 0, 0, gw, gh);
        const im = sx.getImageData(0, 0, gw, gh), d = im.data, n = gw * gh;
        let P = p.palette.colors.map(rgb);
        if (p.palette.adaptive) P = medianCut(d, Math.round(p.ncolors));
        else if (!p.palette.ramp && P.length > p.ncolors) P = P.slice(0, Math.max(3, Math.round(p.ncolors)));
        const lum = q => 0.2126 * q[0] + 0.7152 * q[1] + 0.0722 * q[2];
        const order = P.map((_, i) => i).sort((x, y) => lum(P[x]) - lum(P[y]));
        const nearest = (r, g, b) => {
          if (p.palette.ramp) return order[clamp(Math.round(lum([r, g, b]) / 255 * (order.length - 1)), 0, order.length - 1)];
          let best = 0, bd = 1e9;
          for (let k = 0; k < P.length; k++) {
            const dr = r - P[k][0], dg = g - P[k][1], db = b - P[k][2], dist = 2 * dr * dr + 4 * dg * dg + 3 * db * db;
            if (dist < bd) { bd = dist; best = k; }
          }
          return best;
        };
        const buf = new Float32Array(n * 3);
        for (let i = 0; i < n; i++) { buf[i * 3] = d[i * 4]; buf[i * 3 + 1] = d[i * 4 + 1]; buf[i * 3 + 2] = d[i * 4 + 2]; }
        // 밝기 단계 팔레트(게임보이·1비트·노을)는 밝기 분포를 고르게 펴서 씁니다. 안 그러면 중간톤이 한 색으로 뭉쳐 얼굴이 사라집니다
        if (p.palette.ramp) {
          const hist = new Float32Array(256);
          for (let i = 0; i < n; i++) hist[clamp(lum([buf[i * 3], buf[i * 3 + 1], buf[i * 3 + 2]]), 0, 255) | 0]++;
          for (let k = 1; k < 256; k++) hist[k] += hist[k - 1];
          for (let i = 0; i < n; i++) {
            const l = clamp(lum([buf[i * 3], buf[i * 3 + 1], buf[i * 3 + 2]]), 0, 255), e = hist[l | 0] / n * 255, v = e * 0.75 + l * 0.25;
            buf[i * 3] = buf[i * 3 + 1] = buf[i * 3 + 2] = v;
          }
        }
        const BAYER = [0, 8, 2, 10, 12, 4, 14, 6, 3, 11, 1, 9, 15, 7, 13, 5], step = 255 / Math.max(2, P.length);
        const idx = new Int16Array(n), Lc = new Float32Array(n);
        for (let y = 0; y < gh; y++) for (let x = 0; x < gw; x++) {
          const i = y * gw + x;
          let r = buf[i * 3], g = buf[i * 3 + 1], b = buf[i * 3 + 2];
          if (p.dither === '격자') { const t = ((BAYER[(y & 3) * 4 + (x & 3)] + 0.5) / 16 - 0.5) * step; r += t; g += t; b += t; }
          const k = nearest(r, g, b); idx[i] = k; Lc[i] = lum(P[k]);
          if (p.dither === '오차 확산') {
            const er = r - P[k][0], eg = g - P[k][1], eb = b - P[k][2];
            const push = (xx, yy, f) => { if (xx < 0 || xx >= gw || yy >= gh) return; const q = (yy * gw + xx) * 3; buf[q] += er * f; buf[q + 1] += eg * f; buf[q + 2] += eb * f; };
            push(x + 1, y, 7 / 16); push(x - 1, y + 1, 3 / 16); push(x, y + 1, 5 / 16); push(x + 1, y + 1, 1 / 16);
          }
        }
        const darker = k => { const pos = order.indexOf(k); return order[Math.max(0, pos - 1 - (p.outline > 0.75 ? 1 : 0))]; };
        const out = new Int16Array(idx);
        if (p.outline > 0) {
          const th = 255 * (0.42 - p.outline * 0.3);
          for (let y = 0; y < gh; y++) for (let x = 0; x < gw; x++) {
            const i = y * gw + x, nb = [x > 0 ? i - 1 : i, x < gw - 1 ? i + 1 : i, y > 0 ? i - gw : i, y < gh - 1 ? i + gw : i];
            if (nb.some(j => Lc[j] - Lc[i] > th)) out[i] = darker(idx[i]);
          }
        }
        if (p.shape === '네모') {
          for (let i = 0; i < n; i++) { const q = P[out[i]]; d[i * 4] = q[0]; d[i * 4 + 1] = q[1]; d[i * 4 + 2] = q[2]; d[i * 4 + 3] = 255; }
          sx.putImageData(im, 0, 0);
          c.imageSmoothingEnabled = false; c.drawImage(small, 0, 0, gw * px, gh * px); c.imageSmoothingEnabled = true;
        } else {
          const dark = P[order[0]];
          c.fillStyle = css([dark[0] * 0.6, dark[1] * 0.6, dark[2] * 0.6]); c.fillRect(0, 0, W, H);
          for (let y = 0; y < gh; y++) for (let x = 0; x < gw; x++) {
            c.fillStyle = css(P[out[y * gw + x]]);
            if (p.shape === '둥근 점') { c.beginPath(); c.arc((x + 0.5) * px, (y + 0.5) * px, px * 0.44, 0, Math.PI * 2); c.fill(); }
            else { const g2 = px * 0.12; c.beginPath(); c.roundRect ? c.roundRect(x * px + g2, y * px + g2, px - g2 * 2, px - g2 * 2, px * 0.18) : c.rect(x * px + g2, y * px + g2, px - g2 * 2, px - g2 * 2); c.fill(); }
          }
        }
        if (p.grid) {
          c.fillStyle = 'rgba(0,0,0,0.18)';
          for (let x = 1; x < gw; x++) c.fillRect(Math.round(x * px), 0, 1, H);
          for (let y = 1; y < gh; y++) c.fillRect(0, Math.round(y * px), W, 1);
        }
      },
    },

    {
      id: 'punk', name: '펑크 복사기', thumb: 'punk', shuffle: true,
      note: '복사기로 몇 번 돌린 흑백 사진을 찢어 다시 붙이고, 테이프로 대충 고정한 진(zine) 한 장.',
      controls: [
        { key: 'cut', label: '검정 양', min: 0.3, max: 0.7, step: 0.02, value: 0.48 },
        { key: 'pieces', label: '찢은 조각', min: 1, max: 5, step: 1, value: 3 },
        { key: 'tapes', label: '테이프', min: 0, max: 6, step: 1, value: 3 },
        { key: 'scatter', label: '흐트러짐', min: 0, max: 1, step: 0.05, value: 0.5, adv: true },
        { key: 'dirt', label: '토너 얼룩', min: 0, max: 1, step: 0.05, value: 0.5, adv: true },
        { key: 'streak', label: '복사기 줄', min: 0, max: 1, step: 0.05, value: 0.4, adv: true },
        { key: 'invert', label: '반전', type: 'toggle', value: false, adv: true },
      ],
      slots: ['토너', '종이', '강조색'],
      palettes: [
        { name: '흑백 + 빨강', colors: ['#141414', '#f1ede4', '#e10600'] },
        { name: '흑백 + 형광', colors: ['#141414', '#f1ede4', '#f2ff3a'] },
        { name: '흑백 + 핑크', colors: ['#141414', '#f1ede4', '#ff3d9a'] },
        { name: '청사진', colors: ['#14306b', '#eef1f6', '#ffd400'] },
      ],
      prep: (src, p, g) => analyze(src, 1, g),
      render(c, A, W, H, p, s) {
        const S = sampler(A, W, H);
        let [ink, paper, accent] = p.colors.map(rgb);
        if (p.invert) [ink, paper] = [paper, ink];
        const pc = canvas(W, H), pcx = ctx2d(pc), im = pcx.createImageData(W, H), d = im.data, g = 1 / s;
        for (let y = 0; y < H; y++) for (let x = 0; x < W; x++) {
          let l = S(A.L, x, y);
          l -= smooth(0.38, 0.75, Math.hypot(x / W - 0.5, y / H - 0.5)) * 0.35;
          l -= (vnoise(x * g * 0.004, y * g * 0.25, 11) - 0.5) * 0.3 * p.streak;
          const t = p.cut + (vnoise(x * g * 0.02, y * g * 0.02, 5) - 0.5) * 0.18 * p.dirt + (hash(x, y, 2) - 0.5) * 0.16;
          let k = l < t ? 1 : 0;
          const spk = hash((x * g / 2) | 0, (y * g / 2) | 0, 9);
          if (spk > 1 - 0.0025 * p.dirt) k = 1;
          if (spk < 0.0015 * p.dirt) k = 0;
          const col = k ? ink : paper, i = (y * W + x) * 4;
          d[i] = col[0]; d[i + 1] = col[1]; d[i + 2] = col[2]; d[i + 3] = 255;
        }
        pcx.putImageData(im, 0, 0);

        // 배치는 seed 로 정합니다. '배치 섞기'를 누를 때마다 seed 가 바뀝니다
        const R = rng(p.seed), rr = (a, b) => a + R() * (b - a), m = Math.min(W, H), sc = p.scatter;
        const horiz = R() < 0.6, U = horiz ? W : H, V = horiz ? H : W;
        const at = (u, v) => (horiz ? [u, v] : [v, u]);
        // 찢는 선: 조각 수만큼 가로(또는 세로)로 나누고, 선마다 들쭉날쭉한 가장자리를 만듭니다
        const n = Math.round(p.pieces), cuts = [];
        for (let i = 1; i < n; i++) cuts.push(V * (i / n + (R() - 0.5) * 0.5 / n));
        const jag = cuts.map(() => { const pts = [], step = U / 26; for (let u = -U * 0.1; u <= U * 1.1 + step; u += step) pts.push([u, (R() - 0.5) * m * 0.03]); return pts; });
        const gap = m * 0.006 * (0.4 + sc);
        c.fillStyle = css(paper); c.fillRect(0, 0, W, H);
        for (let i = 0; i < n; i++) {
          const path = new Path2D();
          const top = i === 0 ? [[-U * 0.1, -V * 0.1], [U * 1.1, -V * 0.1]] : jag[i - 1].map(([u, j]) => [u, cuts[i - 1] + j + gap]);
          const bot = i === n - 1 ? [[U * 1.1, V * 1.1], [-U * 0.1, V * 1.1]] : jag[i].map(([u, j]) => [u, cuts[i] + j - gap]).reverse();
          [...top, ...bot].forEach(([u, v], k) => { const [x, y] = at(u, v); k ? path.lineTo(x, y) : path.moveTo(x, y); });
          path.closePath();
          const mid = i === 0 ? (cuts[0] ?? V) / 2 : i === n - 1 ? (cuts[i - 1] + V) / 2 : (cuts[i - 1] + cuts[i]) / 2;
          const [mx, my] = at(U / 2, mid), [dx, dy] = at((R() - 0.5) * U * 0.07 * sc, (R() - 0.5) * m * 0.02 * sc), rot = n > 1 ? (R() - 0.5) * 0.07 * sc : 0;
          const place = () => { c.translate(mx + dx, my + dy); c.rotate(rot); c.translate(-mx, -my); };
          c.save(); place(); c.translate(m * 0.006, m * 0.009); c.fillStyle = 'rgba(0,0,0,0.28)'; c.fill(path); c.restore();
          c.save(); place(); c.clip(path); c.drawImage(pc, 0, 0); c.restore();
        }
        // 테이프: 절반쯤은 찢은 자리를 붙잡고, 나머지는 가장자리에 아무렇게나
        for (let k = 0; k < Math.round(p.tapes); k++) {
          let x, y, a;
          if (cuts.length && R() < 0.6) { const ci = (R() * cuts.length) | 0; [x, y] = at((R() < 0.5 ? rr(0.04, 0.3) : rr(0.7, 0.96)) * U, cuts[ci]); a = (horiz ? Math.PI / 2 : 0) + rr(-0.5, 0.5); }
          else { const e = (R() * 4) | 0; x = e < 2 ? rr(0.05, 0.95) * W : e === 2 ? rr(0, 0.08) * W : rr(0.92, 1) * W; y = e === 0 ? rr(0, 0.07) * H : e === 1 ? rr(0.93, 1) * H : rr(0.08, 0.92) * H; a = rr(-0.6, 0.6) + (e > 1 ? Math.PI / 2 : 0); }
          const tw = W * rr(0.16, 0.3), th = m * rr(0.045, 0.065), masking = R() < 0.3;
          c.save(); c.translate(x, y); c.rotate(a);
          c.globalAlpha = masking ? 0.78 : 0.9; c.fillStyle = masking ? 'rgb(232,226,206)' : css(accent);
          c.beginPath(); c.moveTo(-tw / 2, -th / 2);
          for (let q = 0; q <= 6; q++) c.lineTo(tw / 2 + (q % 2 ? th * 0.08 : 0), -th / 2 + th * q / 6);
          for (let q = 6; q >= 0; q--) c.lineTo(-tw / 2 - (q % 2 ? th * 0.08 : 0), -th / 2 + th * q / 6);
          c.closePath(); c.fill(); c.restore();
        }
        c.globalAlpha = 1;
      },
    },

    {
      id: 'constructivism', name: '구성주의', thumb: 'constructivism', shuffle: true,
      note: '망점으로 찍은 사진, 붉은 사선, 원과 막대. 1920년대 러시아 포스터의 말투. 배치는 섞을 때마다 바뀝니다.',
      controls: [
        { key: 'frame', label: '사진 모양', type: 'choice', options: ['사각형', '원', '반원'], value: '사각형' },
        { key: 'shapes', label: '도형 수', min: 0, max: 9, step: 1, value: 5 },
        { key: 'photoSize', label: '사진 크기', min: 0.45, max: 0.95, step: 0.05, value: 0.72 },
        { key: 'cell', label: '사진 망점', min: 4, max: 14, step: 1, value: 6, adv: true },
        { key: 'photo', label: '사진 처리', type: 'choice', options: ['망점', '두 색', '사진 그대로'], value: '망점', adv: true },
        { key: 'tilt', label: '기울기', min: 0, max: 1.6, step: 0.05, value: 1, adv: true },
      ],
      slots: ['붉은색', '검정', '종이'],
      palettes: [
        { name: '빨강 + 검정', colors: ['#d7261e', '#141414', '#ece3cf'] },
        { name: '주황 + 검정', colors: ['#f05a28', '#141414', '#efe6d4'] },
        { name: '빨강 + 남색', colors: ['#d7261e', '#1b2a4a', '#ece3cf'] },
        { name: '초록 + 검정', colors: ['#1f8a4c', '#141414', '#ebe5d3'] },
      ],
      prep: (src, p, g) => analyze(src, 1, g),
      render(c, A, W, H, p, s) {
        const [red, ink, paper] = p.colors, K = rgb(ink), P = rgb(paper), Rc = rgb(red);
        const photo = canvas(W, H), px = ctx2d(photo), S = sampler(A, W, H);
        const im = px.createImageData(W, H), d = im.data;
        const scr = screen(p.cell * s, 45 * Math.PI / 180), dens = (x, y) => clamp(smooth(0.9, 0.12, S(A.L, x, y)) * 1.05);
        for (let y = 0; y < H; y++) for (let x = 0; x < W; x++) {
          const i = (y * W + x) * 4, l = S(A.L, x, y);
          let col;
          if (p.photo === '망점') { const a = scr(x, y, dens); col = [P[0] + (K[0] - P[0]) * a, P[1] + (K[1] - P[1]) * a, P[2] + (K[2] - P[2]) * a]; }
          else if (p.photo === '두 색') col = l < 0.32 ? K : l < 0.58 ? Rc : P;
          else { const v = clamp((l - 0.5) * 1.3 + 0.5); col = [K[0] + (P[0] - K[0]) * v, K[1] + (P[1] - K[1]) * v, K[2] + (P[2] - K[2]) * v]; }
          d[i] = col[0]; d[i + 1] = col[1]; d[i + 2] = col[2]; d[i + 3] = 255;
        }
        px.putImageData(im, 0, 0);
        c.fillStyle = paper; c.fillRect(0, 0, W, H);

        const R = rng(p.seed), rr = (a, b) => a + R() * (b - a), m = Math.min(W, H);
        // 화면 전체가 하나의 사선 방향을 공유합니다. 도형은 그 방향, 직각, 수평 가운데 하나를 따릅니다
        const ang = (R() < 0.5 ? -1 : 1) * rr(0.3, 0.65) * p.tilt;
        const pw = W * p.photoSize, ph = H * p.photoSize * rr(0.72, 0.92);
        const cx = W / 2 + (R() - 0.5) * (W - pw) * 0.95, cy = H / 2 + (R() - 0.5) * (H - ph) * 0.95;
        const prot = p.frame === '원' ? 0 : p.frame === '반원' ? ang * 0.5 : rr(-0.22, 0.22) * p.tilt;
        const kinds = ['원', '막대', '막대', '삼각형', '고리', '사분원', '띠'];
        const items = [];
        for (let i = 0; i < Math.round(p.shapes); i++) {
          const kind = i === 0 ? '띠' : kinds[(R() * kinds.length) | 0];
          const it = { kind, x: rr(0.1, 0.9) * W, y: rr(0.08, 0.92) * H, r: rr(0.05, 0.15) * m, len: rr(0.25, 0.7) * W, a: [ang, ang, ang + Math.PI / 2, 0][(R() * 4) | 0], col: R() < 0.62 ? red : ink, front: R() < 0.5 };
          if (kind === '띠') { it.r = rr(0.06, 0.13) * m; it.col = i === 0 ? red : it.col; it.a = ang; if (i === 0) { it.x = cx + rr(-0.3, 0.3) * pw; it.y = cy + (R() < 0.5 ? -1 : 1) * ph * rr(0.3, 0.55); } }
          // 사진 위로 올라오는 건 가는 막대뿐이고, 그것도 사진 한가운데(대개 얼굴)는 피합니다. 나머지 도형은 사진 뒤로
          if (kind === '막대' && it.front) {
            const fx = cx, fy = cy - ph * 0.08, hw = pw * 0.36 + m * 0.02, hh = ph * 0.42 + m * 0.02;
            for (let t = -0.5; t <= 0.5 && it.front; t += 0.05) {
              const qx = it.x + Math.cos(it.a) * it.len * t, qy = it.y + Math.sin(it.a) * it.len * t;
              if (Math.abs(qx - fx) < hw && Math.abs(qy - fy) < hh) it.front = false;
            }
          } else it.front = false;
          items.push(it);
        }
        const drawItem = it => {
          c.save(); c.translate(it.x, it.y); c.rotate(it.a); c.fillStyle = it.col; c.strokeStyle = it.col;
          c.beginPath();
          if (it.kind === '띠') c.rect(-W * 1.5, -it.r / 2, W * 3, it.r);
          else if (it.kind === '원') c.arc(0, 0, it.r, 0, Math.PI * 2);
          else if (it.kind === '막대') c.rect(-it.len / 2, -m * 0.012, it.len, m * 0.024);
          else if (it.kind === '삼각형') { c.moveTo(0, -it.r * 1.2); c.lineTo(it.r, it.r * 0.8); c.lineTo(-it.r, it.r * 0.8); c.closePath(); }
          else if (it.kind === '사분원') { c.moveTo(0, 0); c.arc(0, 0, it.r * 1.4, 0, Math.PI / 2); c.closePath(); }
          if (it.kind === '고리') { c.lineWidth = it.r * 0.22; c.arc(0, 0, it.r, 0, Math.PI * 2); c.stroke(); } else c.fill();
          c.restore();
        };
        items.filter(it => !it.front).forEach(drawItem);
        // 사진: 모양 안에 꽉 차게 넣습니다
        c.save(); c.translate(cx, cy); c.rotate(prot); c.beginPath();
        let bw = pw, bh = ph, top = null;
        if (p.frame === '원') { const r = Math.min(pw, ph) * 0.55; c.arc(0, 0, r, 0, Math.PI * 2); bw = bh = r * 2; }
        else if (p.frame === '반원') { const r = Math.min(pw * 0.62, ph); c.arc(0, r * 0.4, r, Math.PI, Math.PI * 2); c.closePath(); bw = r * 2; bh = r; top = -r * 0.6; }
        else c.rect(-pw / 2, -ph / 2, pw, ph);
        c.save(); c.clip(); c.rotate(-prot);
        // 반원은 사진 윗부분을 담습니다. 가운데를 자르면 얼굴이 반원 꼭대기에서 잘려 나갑니다
        const k = Math.max(bw / W, bh / H) * 1.05, ih = H * k;
        c.drawImage(photo, -W * k / 2, top === null ? -ih / 2 : top - ih * 0.14, W * k, ih);
        c.restore();
        if (p.frame !== '사각형') { c.strokeStyle = ink; c.lineWidth = m * 0.01; c.stroke(); }
        c.restore();
        items.filter(it => it.front).forEach(drawItem);
      },
    },

    {
      id: 'cyber', name: '사이버펑크', thumb: 'cyberpunk',
      note: '네온 그라데이션, 어긋난 RGB, 찢어진 화면과 주사선. 고장 난 모니터로 본 밤거리.',
      controls: [
        { key: 'split', label: '색 어긋남', min: 0, max: 24, step: 1, value: 7 },
        { key: 'glitch', label: '화면 찢김', min: 0, max: 1, step: 0.05, value: 0.35 },
        { key: 'scan', label: '주사선', min: 0, max: 1, step: 0.05, value: 0.45 },
        { key: 'glow', label: '번짐', min: 0, max: 1, step: 0.05, value: 0.45, adv: true },
        { key: 'steps', label: '색 단계', type: 'choice', options: ['부드럽게', '계단'], value: '부드럽게', adv: true },
        { key: 'dir', label: '찢김 방향', type: 'choice', options: ['가로', '세로'], value: '가로', adv: true },
      ],
      slots: ['어둠', '중간', '밝음', '하이라이트'],
      palettes: [
        { name: '네온 핑크', colors: ['#0c0420', '#4b1c8c', '#ff2a6d', '#ffd9ec'] },
        { name: '시안 밤', colors: ['#02091a', '#0b4a8a', '#05d9e8', '#eafcff'] },
        { name: '노을 도시', colors: ['#14031c', '#7a1745', '#ff6c11', '#ffe3a1'] },
        { name: '애시드', colors: ['#050805', '#164d24', '#39ff14', '#f2ffe2'] },
        { name: '흑백 모니터', colors: ['#060606', '#3a3a3a', '#bdbdbd', '#ffffff'] },
      ],
      prep: (src, p, g) => analyze(src, 1, g),
      render(c, A, W, H, p, s) {
        const S = sampler(A, W, H), P = p.colors.map(rgb), n = P.length - 1;
        // 밝기 → 색 (그라데이션 맵). 256칸 표로 미리 만들어 둡니다
        const lut = new Float32Array(256 * 3);
        for (let k = 0; k < 256; k++) {
          let l = k / 255; if (p.steps === '계단') l = Math.round(l * 5) / 5;
          const t = l * n, j = Math.min(n - 1, t | 0), f = t - j;
          for (let ch = 0; ch < 3; ch++) lut[k * 3 + ch] = P[j][ch] + (P[j + 1][ch] - P[j][ch]) * f;
        }
        const at = (x, y) => clamp(S(A.L, x, y) * 1.08 - 0.03, 0, 1) * 255 | 0;
        // 찢김: 띠마다 정해진 만큼 밀어냅니다. 작은 띠와 큰 띠를 섞어 불규칙하게
        const vert = p.dir === '세로', len = vert ? W : H, span = vert ? H : W;
        const shift = new Float32Array(len), hot = new Uint8Array(len);
        for (let a = 0; a < len; a++) {
          const bi = (a / (9 * s)) | 0, bj = (a / (41 * s)) | 0;
          if (hash(bi, 1, 51) < p.glitch * 0.16 || hash(bj, 2, 53) < p.glitch * 0.1) {
            shift[a] = (hash(bi, 3, 55) - 0.5) * span * 0.18 * p.glitch; hot[a] = 1;
          }
        }
        const off = p.split * s, im = c.createImageData(W, H), d = im.data, line = Math.max(2, Math.round(3 * s));
        for (let y = 0; y < H; y++) for (let x = 0; x < W; x++) {
          const a = vert ? x : y, sx = vert ? x : x + shift[a], sy = vert ? y + shift[a] : y, o = off * (hot[a] ? 2.2 : 1);
          const r = lut[at(sx - o, sy) * 3], g = lut[at(sx, sy) * 3 + 1], b = lut[at(sx + o, sy) * 3 + 2];
          const sc = (y / line | 0) % 2 ? 1 : 1 - p.scan * 0.32, nz = (hash(x, y, 57) - 0.5) * 14;
          const i = (y * W + x) * 4;
          d[i] = r * sc + nz; d[i + 1] = g * sc + nz; d[i + 2] = b * sc + nz; d[i + 3] = 255;
        }
        c.putImageData(im, 0, 0);
        if (p.glow > 0) bloom(c, W, H, p.glow * 0.55);
      },
    },
    {
      id: 'vapor', name: '바포웨이브', thumb: 'vaporwave',
      note: '분홍과 하늘색으로 물든 사진, 줄무늬 태양과 끝없는 격자 바닥, 늘어진 VHS 테이프. 1990년대 인터넷을 향한 향수.',
      controls: [
        { key: 'frame', label: '틀', type: 'choice', options: ['태양과 격자', '옛날 창', '사진 가득'], value: '태양과 격자' },
        { key: 'tone', label: '색 세기', min: 0.4, max: 1, step: 0.05, value: 0.85 },
        { key: 'vhs', label: 'VHS 줄', min: 0, max: 1, step: 0.05, value: 0.45 },
        { key: 'sun', label: '태양 크기', min: 0.24, max: 0.44, step: 0.01, value: 0.34, adv: true },
        { key: 'grid', label: '격자 촘촘함', min: 6, max: 24, step: 1, value: 12, adv: true },
        { key: 'glow', label: '번짐', min: 0, max: 1, step: 0.05, value: 0.35, adv: true },
        { key: 'noise', label: '노이즈', min: 0, max: 1, step: 0.05, value: 0.3, adv: true },
      ],
      slots: ['어둠', '중간', '밝음', '하늘', '태양', '격자'],
      palettes: [
        { name: '마이애미', colors: ['#2a0f5c', '#ff4fa3', '#7df9ff', '#ff8fd8', '#ffe45e', '#ff2fd0'] },
        { name: '파스텔 몰', colors: ['#3b2a6e', '#f7a8d8', '#d4f8ff', '#b8a4ff', '#fff4a8', '#ff71ce'] },
        { name: '청록 노을', colors: ['#0d1b4c', '#01cdfe', '#fffb96', '#ff71ce', '#fff6c2', '#05ffa1'] },
        { name: '보라 밤', colors: ['#140726', '#7b2cbf', '#ff9ef5', '#4a1d8f', '#ff6ad5', '#b967ff'] },
      ],
      prep: (src, p, g) => withRGB(analyze(src, 0, g)),
      render(c, A, W, H, p, s) {
        const [dk, md, lt, sky, sun, grd] = p.colors.map(rgb), m = Math.min(W, H);
        // 사진: 밝기를 어둠 → 중간 → 밝음 그라데이션으로. '색 세기'만큼 원래 색에서 옮겨 갑니다
        const S = sampler(A, W, H), photo = canvas(W, H), px = ctx2d(photo), im = px.createImageData(W, H), d = im.data;
        for (let y = 0; y < H; y++) for (let x = 0; x < W; x++) {
          const l = clamp(S(A.L, x, y) * 1.1 - 0.05), t = l * 2, j = t < 1 ? 0 : 1, f = t - j, a = j ? md : dk, b = j ? lt : md, i = (y * W + x) * 4;
          const o = [S(A.R, x, y), S(A.G, x, y), S(A.B, x, y)];
          for (let ch = 0; ch < 3; ch++) d[i + ch] = o[ch] + (a[ch] + (b[ch] - a[ch]) * f - o[ch]) * p.tone;
          d[i + 3] = 255;
        }
        px.putImageData(im, 0, 0);
        const vgrad = (y0, y1, a, b) => { const gr = c.createLinearGradient(0, y0, 0, y1); gr.addColorStop(0, css(a)); gr.addColorStop(1, css(b)); return gr; };

        if (p.frame === '사진 가득') c.drawImage(photo, 0, 0);
        else if (p.frame === '태양과 격자') {
          const hz = H * 0.64;
          c.fillStyle = vgrad(0, hz, dk, sky); c.fillRect(0, 0, W, hz);
          // 태양 = 사진. 아래쪽 절반에만 줄무늬 틈을 내서 얼굴은 그대로 둡니다
          const r = W * p.sun, sx = W / 2, sy = hz - r * 0.55, sc = canvas(r * 2, r * 2), sx2 = ctx2d(sc);
          sx2.beginPath(); sx2.arc(r, r, r, 0, Math.PI * 2); sx2.clip();
          fitInto(sx2, photo, 0, 0, r * 2, r * 2, 0.3);
          sx2.globalCompositeOperation = 'source-atop'; sx2.globalAlpha = 0.3;
          sx2.fillStyle = (() => { const gr = sx2.createLinearGradient(0, 0, 0, r * 2); gr.addColorStop(0, css(sun)); gr.addColorStop(1, css(md)); return gr; })();
          sx2.fillRect(0, 0, r * 2, r * 2);
          sx2.globalCompositeOperation = 'destination-out'; sx2.globalAlpha = 1;
          for (let i = 0; i < 6; i++) sx2.fillRect(0, r * (1.18 + i * 0.085), r * 2, r * (0.012 + i * 0.01));
          c.save(); c.shadowColor = css(sun); c.shadowBlur = r * 0.35; c.fillStyle = css(sun); c.globalAlpha = 0.55;
          c.beginPath(); c.arc(sx, sy, r * 0.97, 0, Math.PI * 2); c.fill(); c.restore();
          c.drawImage(sc, sx - r, sy - r);
          // 바닥: 소실점으로 모이는 격자
          c.fillStyle = vgrad(hz, H, dk.map((v, k) => v + (sky[k] - v) * 0.18), dk); c.fillRect(0, hz, W, H - hz);
          c.save(); c.strokeStyle = css(grd); c.lineWidth = Math.max(1, 2.2 * s); c.shadowColor = css(grd); c.shadowBlur = 10 * s;
          const n = Math.round(p.grid), bot = W * 3 / n;
          c.beginPath();
          for (let i = -n; i <= n; i++) { c.moveTo(W / 2 + i * bot * 0.1, hz); c.lineTo(W / 2 + i * bot, H); }
          const rows = Math.round(n * 0.8);
          for (let k = 0; k <= rows; k++) { const y = hz + (H - hz) * Math.pow(k / rows, 2.1); c.moveTo(0, y); c.lineTo(W, y); }
          c.stroke(); c.restore();
        } else {
          // 옛날 창: 그라데이션 하늘 + 모눈 위에 90년대 컴퓨터 창 두 개 (글자는 넣지 않습니다)
          c.fillStyle = vgrad(0, H, dk, sky); c.fillRect(0, 0, W, H);
          c.save(); c.strokeStyle = css(lt); c.globalAlpha = 0.16; c.lineWidth = Math.max(1, 1.4 * s); c.beginPath();
          const gs = W / Math.round(p.grid);
          for (let x = gs; x < W; x += gs) { c.moveTo(x, 0); c.lineTo(x, H); }
          for (let y = gs; y < H; y += gs) { c.moveTo(0, y); c.lineTo(W, y); }
          c.stroke(); c.restore();
          const win = (x, y, w, h, fill) => {
            const b = Math.max(2, m * 0.011), tb = m * 0.05, hi = '#ffffff', lo = '#3a3a3a', face = '#c6c6c6';
            c.fillStyle = css(dk); c.globalAlpha = 0.55; c.fillRect(x + m * 0.022, y + m * 0.022, w, h); c.globalAlpha = 1;
            const bevel = (x2, y2, w2, h2, a, z) => { c.fillStyle = face; c.fillRect(x2, y2, w2, h2); c.fillStyle = a; c.fillRect(x2, y2, w2, b * 0.5); c.fillRect(x2, y2, b * 0.5, h2); c.fillStyle = z; c.fillRect(x2, y2 + h2 - b * 0.5, w2, b * 0.5); c.fillRect(x2 + w2 - b * 0.5, y2, b * 0.5, h2); };
            bevel(x, y, w, h, hi, lo);
            const gr = c.createLinearGradient(x, 0, x + w, 0); gr.addColorStop(0, css(dk)); gr.addColorStop(1, css(md));
            c.fillStyle = gr; c.fillRect(x + b, y + b, w - b * 2, tb);
            const bs = tb * 0.72, by = y + b + (tb - bs) / 2;
            for (let k = 0; k < 3; k++) {
              const bx = x + w - b * 1.6 - (bs + b * 0.4) * (3 - k);
              bevel(bx, by, bs, bs, hi, lo);
              c.strokeStyle = '#111'; c.lineWidth = Math.max(1, bs * 0.12); c.beginPath();
              if (k === 0) { c.moveTo(bx + bs * 0.28, by + bs * 0.7); c.lineTo(bx + bs * 0.62, by + bs * 0.7); }
              else if (k === 1) c.rect(bx + bs * 0.28, by + bs * 0.28, bs * 0.44, bs * 0.4);
              else { c.moveTo(bx + bs * 0.3, by + bs * 0.3); c.lineTo(bx + bs * 0.7, by + bs * 0.7); c.moveTo(bx + bs * 0.7, by + bs * 0.3); c.lineTo(bx + bs * 0.3, by + bs * 0.7); }
              c.stroke();
            }
            const ix = x + b * 1.5, iy = y + b * 2 + tb, iw = w - b * 3, ih = h - b * 3.5 - tb;
            c.fillStyle = lo; c.fillRect(ix - b * 0.5, iy - b * 0.5, iw + b, ih + b);
            fill(ix, iy, iw, ih);
          };
          win(W * 0.06, H * 0.05, W * 0.5, H * 0.26, (x, y, w, h) => { c.fillStyle = vgrad(y, y + h, lt, sky); c.fillRect(x, y, w, h); });
          win(W * 0.11, H * 0.15, W * 0.8, H * 0.74, (x, y, w, h) => { c.save(); c.beginPath(); c.rect(x, y, w, h); c.clip(); fitInto(c, photo, x, y, w, h, 0.3); c.restore(); });
          // 반짝이 몇 개
          const R = rng(7);
          c.fillStyle = css(lt);
          for (let k = 0; k < 5; k++) {
            const x = (0.08 + R() * 0.84) * W, y = (k < 2 ? 0.92 + R() * 0.05 : R() < 0.5 ? 0.04 + R() * 0.08 : 0.35 + R() * 0.3) * H, r = m * (0.012 + R() * 0.02);
            if (k >= 2 && x > W * 0.08 && x < W * 0.93 && y > H * 0.13) continue;
            c.beginPath(); c.moveTo(x, y - r * 2); c.quadraticCurveTo(x, y, x + r * 2, y); c.quadraticCurveTo(x, y, x, y + r * 2); c.quadraticCurveTo(x, y, x - r * 2, y); c.quadraticCurveTo(x, y, x, y - r * 2); c.fill();
          }
        }
        vhs(c, W, H, p, s);
        if (p.glow > 0) bloom(c, W, H, p.glow * 0.5);
      },
    },

    {
      id: 'psych', name: '사이키델릭', thumb: 'psychedelic', shuffle: '무늬 섞기',
      note: '녹아 흐르는 사진과 등고선처럼 겹친 색 띠. 1960년대 샌프란시스코 공연 포스터의 환각. 무늬는 섞을 때마다 바뀝니다.',
      controls: [
        { key: 'melt', label: '녹임', min: 0, max: 1, step: 0.05, value: 0.5 },
        { key: 'bands', label: '색 띠 수', min: 3, max: 12, step: 1, value: 6 },
        { key: 'swirl', label: '소용돌이', min: 0, max: 1, step: 0.05, value: 0.35 },
        { key: 'scale', label: '무늬 크기', min: 0.5, max: 2, step: 0.05, value: 1, adv: true },
        { key: 'edge', label: '띠 경계', type: 'choice', options: ['딱딱하게', '부드럽게'], value: '딱딱하게', adv: true },
        { key: 'face', label: '얼굴 살리기', type: 'toggle', value: true, adv: true },
      ],
      slots: ['색 1', '색 2', '색 3', '색 4', '색 5'],
      palettes: [
        { name: '공연 포스터', colors: ['#2b1055', '#d7263d', '#f46036', '#ffd23f', '#1b998b'] },
        { name: '사탕', colors: ['#3a0ca3', '#ff006e', '#fb5607', '#ffbe0b', '#3a86ff'] },
        { name: '자두와 이끼', colors: ['#3d0c45', '#9b2d6f', '#e86a33', '#f2c14e', '#5f8d4e'] },
        { name: '흑백', colors: ['#141414', '#f1ebe0', '#5c5c5c', '#f1ebe0', '#141414'] },
      ],
      prep: (src, p, g) => analyze(src, 0, g),
      render(c, A, W, H, p, s) {
        const S = sampler(A, W, H), P = p.colors.map(rgb), n = P.length, m = Math.min(W, H);
        const ink = P.reduce((a, b) => (a[0] + a[1] + a[2] < b[0] + b[1] + b[2] ? a : b));
        const R = rng(p.seed), rr = (a, b) => a + R() * (b - a), sd = (R() * 1000) | 0;
        const f = 0.0032 / p.scale, amp = p.melt * 120, hard = p.edge === '딱딱하게';
        // 소용돌이 중심: 얼굴 살리기를 켜면 아래쪽 구석으로 비켜 둡니다
        const scx = (p.face ? (R() < 0.5 ? rr(0.08, 0.3) : rr(0.7, 0.92)) : rr(0.25, 0.75)) * W, scy = (p.face ? rr(0.6, 0.92) : rr(0.25, 0.75)) * H;
        const im = c.createImageData(W, H), d = im.data;
        for (let y = 0; y < H; y++) for (let x = 0; x < W; x++) {
          const u = x / s, v = y / s;
          // 얼굴 자리(가운데 위쪽)는 덜 휩니다
          const w = p.face ? 0.15 + 0.85 * smooth(0.75, 1.5, Math.hypot((x / W - 0.5) / 0.26, (y / H - 0.4) / 0.3)) : 1;
          const q1 = vnoise(u * f, v * f, sd), q2 = vnoise(u * f + 3.1, v * f + 7.7, sd + 1);
          let qx = x + (vnoise(u * f * 1.7 + q1 * 2.6, v * f * 1.7 + q2 * 2.6, sd + 2) - 0.5) * 2 * amp * w * s;
          let qy = y + (vnoise(u * f * 1.7 + q2 * 2.6 + 5, v * f * 1.7 + q1 * 2.6, sd + 3) - 0.5) * 2 * amp * w * s;
          if (p.swirl > 0) {
            const ox = qx - scx, oy = qy - scy, dd = Math.hypot(ox, oy) / (m * 0.5), a = p.swirl * 4 * Math.exp(-dd * dd) * w, ca = Math.cos(a), sa = Math.sin(a);
            qx = scx + ox * ca - oy * sa; qy = scy + ox * sa + oy * ca;
          }
          const t = clamp(S(A.L, qx, qy) * 1.05 - 0.02) * p.bands * 0.999 + (q1 - 0.5) * 1.4 * w;
          const k = Math.floor(t), fr = t - k, a = P[((k % n) + n) % n], b = P[(((k + 1) % n) + n) % n], i = (y * W + x) * 4;
          let col = a;
          if (!hard) { const e = smooth(0.5, 1, fr); col = [a[0] + (b[0] - a[0]) * e, a[1] + (b[1] - a[1]) * e, a[2] + (b[2] - a[2]) * e]; }
          else if (fr > 0.94) col = ink;
          d[i] = col[0]; d[i + 1] = col[1]; d[i + 2] = col[2]; d[i + 3] = 255;
        }
        c.putImageData(im, 0, 0);
      },
    },

    {
      id: 'memphis', name: '멤피스', thumb: 'memphis', shuffle: true,
      note: '파스텔 바탕, 굵은 검정 테두리, 꼬불선과 지그재그와 색종이 조각. 1980년대 밀라노 디자인 그룹의 장난기. 배치는 섞을 때마다 바뀝니다.',
      controls: [
        { key: 'frame', label: '사진 모양', type: 'choice', options: ['아치', '원', '사각형'], value: '아치' },
        { key: 'shapes', label: '무늬 수', min: 0, max: 14, step: 1, value: 8 },
        { key: 'photoSize', label: '사진 크기', min: 0.45, max: 0.85, step: 0.05, value: 0.62 },
        { key: 'bg', label: '바탕 무늬', type: 'choice', options: ['점', '줄', '격자', '없음'], value: '점', adv: true },
        { key: 'shadow', label: '그림자 거리', min: 0, max: 1, step: 0.05, value: 0.5, adv: true },
        { key: 'line', label: '선 굵기', min: 0.5, max: 2, step: 0.1, value: 1, adv: true },
        { key: 'photo', label: '사진 처리', type: 'choice', options: ['그대로', '두 색', '망점'], value: '그대로', adv: true },
      ],
      slots: ['바탕', '색 1', '색 2', '색 3', '검정'],
      palettes: [
        { name: '민트 + 핑크', colors: ['#f6efe4', '#ff6f91', '#2ec4b6', '#ffd23f', '#151515'] },
        { name: '바나나', colors: ['#fff3b0', '#ff5d8f', '#3a86ff', '#00c49a', '#151515'] },
        { name: '라벤더', colors: ['#e9e3ff', '#ff8c42', '#00b4d8', '#ffd166', '#151515'] },
        { name: '분홍 바탕', colors: ['#ffd1e3', '#3a86ff', '#ffbe0b', '#06d6a0', '#151515'] },
      ],
      prep: (src, p, g) => withRGB(analyze(src, 0, g)),
      render(c, A, W, H, p, s) {
        const [bg, c1, c2, c3, ink] = p.colors, K = rgb(ink), B = rgb(bg), C1 = rgb(c1), cols = [c1, c2, c3];
        const m = Math.min(W, H), lw = Math.max(1.5, m * 0.008 * p.line), R = rng(p.seed), rr = (a, b) => a + R() * (b - a);
        c.fillStyle = bg; c.fillRect(0, 0, W, H);
        // 바탕 무늬
        c.save(); c.fillStyle = ink; c.strokeStyle = ink; c.globalAlpha = 0.2;
        const sp = 34 * s;
        if (p.bg === '점') { for (let y = sp / 2, r = 0; y < H; y += sp, r++) for (let x = (r % 2 ? sp : sp / 2); x < W; x += sp) { c.beginPath(); c.arc(x, y, 2.8 * s, 0, Math.PI * 2); c.fill(); } }
        else if (p.bg === '줄') { c.lineWidth = 3 * s; c.beginPath(); for (let k = -H; k < W; k += sp * 0.9) { c.moveTo(k, 0); c.lineTo(k + H, H); } c.stroke(); }
        else if (p.bg === '격자') { c.lineWidth = 1.6 * s; c.beginPath(); for (let x = sp; x < W; x += sp) { c.moveTo(x, 0); c.lineTo(x, H); } for (let y = sp; y < H; y += sp) { c.moveTo(0, y); c.lineTo(W, y); } c.stroke(); }
        c.restore();

        // 사진 처리
        const S = sampler(A, W, H), photo = canvas(W, H), px = ctx2d(photo), im = px.createImageData(W, H), d = im.data;
        const scr = screen(7 * s, Math.PI / 4), dens = (x, y) => clamp(smooth(0.92, 0.1, S(A.L, x, y)) * 1.05);
        for (let y = 0; y < H; y++) for (let x = 0; x < W; x++) {
          const i = (y * W + x) * 4, l = S(A.L, x, y);
          let col;
          if (p.photo === '두 색') col = l < 0.36 ? K : l < 0.64 ? C1 : B;
          else if (p.photo === '망점') { const a = scr(x, y, dens); col = [B[0] + (K[0] - B[0]) * a, B[1] + (K[1] - B[1]) * a, B[2] + (K[2] - B[2]) * a]; }
          else { const o = [S(A.R, x, y), S(A.G, x, y), S(A.B, x, y)], lv = l * 255; col = o.map(v => (lv + (v - lv) * 1.25 - 128) * 1.08 + 128); }
          d[i] = col[0]; d[i + 1] = col[1]; d[i + 2] = col[2]; d[i + 3] = 255;
        }
        px.putImageData(im, 0, 0);

        // 사진 자리와 모양
        const pw = W * p.photoSize, ph = Math.min(H * 0.84, pw * rr(1.05, 1.3));
        const cx = W / 2 + (R() - 0.5) * (W - pw) * 0.9, cy = H / 2 + (R() - 0.5) * (H - ph) * 0.9;
        const shape = new Path2D();
        let bx = cx - pw / 2, by = cy - ph / 2, bw = pw, bh = ph;
        if (p.frame === '원') { const r = Math.min(pw, ph) / 2; shape.arc(cx, cy, r, 0, Math.PI * 2); bx = cx - r; by = cy - r; bw = bh = r * 2; }
        else if (p.frame === '아치') { shape.moveTo(bx, by + pw / 2); shape.arc(cx, by + pw / 2, pw / 2, Math.PI, Math.PI * 2); shape.lineTo(bx + pw, by + ph); shape.lineTo(bx, by + ph); shape.closePath(); }
        else shape.rect(bx, by, bw, bh);

        // 무늬: 사진과 겹치지 않는 자리를 먼저 찾고, 끝내 못 찾으면 사진 뒤에 둡니다
        const KINDS = ['꼬불선', '지그재그', '삼각형', '원', '점박이', '색종이', '반원', '고리'];
        // 오른쪽 아래 사이트 표시 자리도 비워 둡니다
        const hits = (x, y, r) => { const qx = clamp(x, bx, bx + bw), qy = clamp(y, by, by + bh); return Math.hypot(x - qx, y - qy) < r || (x + r > W * 0.7 && y + r > H * 0.9); };
        const items = [];
        for (let i = 0; i < Math.round(p.shapes); i++) {
          const kind = KINDS[(R() * KINDS.length) | 0], sz = rr(0.05, 0.095) * m, reach = sz * (['꼬불선', '지그재그', '색종이'].includes(kind) ? 1.6 : 0.75);
          let x, y, behind = true;
          for (let t = 0; t < 16 && behind; t++) { x = rr(0.06, 0.94) * W; y = rr(0.05, 0.95) * H; behind = hits(x, y, reach); }
          items.push({ kind, x, y, sz, behind, a: rr(0, Math.PI * 2), col: R() < 0.18 ? ink : cols[(R() * 3) | 0], fill: R() < 0.7, seed: (R() * 1e6) | 0 });
        }
        const drawItem = it => {
          const z = it.sz;
          c.save(); c.translate(it.x, it.y); c.rotate(it.a);
          c.fillStyle = it.col; c.strokeStyle = it.col; c.lineCap = 'round'; c.lineJoin = 'round';
          if (it.kind === '꼬불선' || it.kind === '지그재그') {
            c.lineWidth = lw * 1.7; c.beginPath();
            for (let k = 0; k <= 48; k++) {
              const t = k / 48, xx = (t - 0.5) * z * 3.2;
              const yy = it.kind === '꼬불선' ? Math.sin(t * Math.PI * 6) * z * 0.22 : (Math.abs(((t * 6) % 2) - 1) - 0.5) * z * 0.55;
              k ? c.lineTo(xx, yy) : c.moveTo(xx, yy);
            }
            c.stroke();
          } else if (it.kind === '색종이') {
            const r2 = rng(it.seed);
            c.lineWidth = lw * 1.9;
            for (let k = 0; k < 6; k++) {
              const a = r2() * Math.PI * 2, dd = r2() * z * 1.3, l = z * (0.22 + r2() * 0.18), ang = r2() * Math.PI;
              c.strokeStyle = k % 3 === 0 ? ink : cols[(r2() * 3) | 0];
              c.beginPath(); c.moveTo(Math.cos(a) * dd - Math.cos(ang) * l / 2, Math.sin(a) * dd - Math.sin(ang) * l / 2); c.lineTo(Math.cos(a) * dd + Math.cos(ang) * l / 2, Math.sin(a) * dd + Math.sin(ang) * l / 2); c.stroke();
            }
          } else {
            c.beginPath();
            if (it.kind === '삼각형') { c.moveTo(0, -z * 0.7); c.lineTo(z * 0.65, z * 0.45); c.lineTo(-z * 0.65, z * 0.45); c.closePath(); }
            else if (it.kind === '반원') { c.arc(0, 0, z * 0.6, Math.PI, Math.PI * 2); c.closePath(); }
            else c.arc(0, 0, z * (it.kind === '점박이' ? 0.6 : it.kind === '고리' ? 0.5 : 0.45), 0, Math.PI * 2);
            if (it.kind === '고리') { c.lineWidth = z * 0.16; c.stroke(); }
            else if (it.kind === '점박이') {
              c.fill(); c.save(); c.clip(); c.fillStyle = ink;
              const g2 = z * 0.2; for (let yy = -z; yy < z; yy += g2) for (let xx = -z; xx < z; xx += g2) { c.beginPath(); c.arc(xx, yy, z * 0.035, 0, Math.PI * 2); c.fill(); }
              c.restore(); c.strokeStyle = ink; c.lineWidth = lw; c.stroke();
            } else {
              if (it.fill || it.col === ink) c.fill(); else { c.lineWidth = lw * 1.4; c.stroke(); }
              if (it.fill && it.col !== ink) { c.strokeStyle = ink; c.lineWidth = lw; c.stroke(); }
            }
          }
          c.restore();
        };
        // 사진 뒤 큰 색 면: 사진 모서리 하나에 걸쳐 둡니다
        if (p.shapes >= 1) {
          const qx = R() < 0.5 ? bx : bx + bw, qy = R() < 0.5 ? by : by + bh, big = rr(0.2, 0.3) * m;
          c.save(); c.translate(qx + (R() - 0.5) * big * 0.6, qy + (R() - 0.5) * big * 0.6); c.rotate(rr(-0.5, 0.5));
          c.fillStyle = cols[(R() * 3) | 0]; c.beginPath();
          if (R() < 0.5) c.arc(0, 0, big, 0, Math.PI * 2); else c.rect(-big * 1.2, -big * 0.45, big * 2.4, big * 0.9);
          c.fill(); c.strokeStyle = ink; c.lineWidth = lw; c.stroke(); c.restore();
        }
        items.filter(it => it.behind).forEach(drawItem);
        // 그림자: 한 색으로 칠하거나 빗금
        const off = m * 0.045 * p.shadow;
        if (off > 0) {
          c.save(); c.translate(off, off); c.fillStyle = cols[(R() * 3) | 0]; c.fill(shape);
          if (R() < 0.45) { c.clip(shape); c.strokeStyle = ink; c.lineWidth = lw * 0.7; c.beginPath(); for (let k = -bh; k < bw; k += lw * 3.2) { c.moveTo(bx + k, by); c.lineTo(bx + k + bh, by + bh); } c.stroke(); }
          c.restore();
        }
        c.save(); c.clip(shape); fitInto(c, photo, bx, by, bw, bh, p.frame === '사각형' ? 0.4 : 0.25); c.restore();
        c.strokeStyle = ink; c.lineWidth = lw * 1.3; c.stroke(shape);
        items.filter(it => !it.behind).forEach(drawItem);
      },
    },
  ];

  function medianCut(d, n) {
    const px = [];
    for (let i = 0; i < d.length; i += 4 * 3) px.push([d[i], d[i + 1], d[i + 2]]);
    let boxes = [px];
    while (boxes.length < n) {
      let bi = -1, bc = 0, br = -1;
      boxes.forEach((b, i) => {
        if (b.length < 2) return;
        for (let ch = 0; ch < 3; ch++) {
          let lo = 255, hi = 0;
          for (const q of b) { if (q[ch] < lo) lo = q[ch]; if (q[ch] > hi) hi = q[ch]; }
          if (hi - lo > br) { br = hi - lo; bi = i; bc = ch; }
        }
      });
      if (bi < 0) break;
      const b = boxes[bi].sort((x, y) => x[bc] - y[bc]), mid = b.length >> 1;
      boxes.splice(bi, 1, b.slice(0, mid), b.slice(mid));
    }
    return boxes.map(b => {
      const s3 = [0, 0, 0]; b.forEach(q => { s3[0] += q[0]; s3[1] += q[1]; s3[2] += q[2]; });
      const m = s3.map(v => v / b.length), avg = (m[0] + m[1] + m[2]) / 3;
      return m.map(v => clamp((avg + (v - avg) * 1.28 - 128) * 1.12 + 128, 0, 255));
    });
  }

  /* ================= 공통 옵션 ('더 다듬기'에서 펼침) ================= */
  const GLOBAL = {
    photo: [
      { key: 'auto', label: '자동 보정', type: 'toggle', value: true },
      { key: 'bright', label: '밝기', min: -0.5, max: 0.5, step: 0.02, value: 0 },
      { key: 'contrast', label: '대비', min: -0.5, max: 0.8, step: 0.02, value: 0 },
      { key: 'sat', label: '채도', min: -1, max: 1, step: 0.05, value: 0 },
      { key: 'zoom', label: '확대', min: 1, max: 3, step: 0.05, value: 1 },
      { key: 'px', label: '좌우 위치', min: -1, max: 1, step: 0.02, value: 0 },
      { key: 'py', label: '위아래 위치', min: -1, max: 1, step: 0.02, value: 0 },
      { key: 'flip', label: '좌우 뒤집기', type: 'toggle', value: false },
    ],
    finish: [
      { key: 'mix', label: '효과 세기', min: 0.4, max: 1, step: 0.05, value: 1 },
      { key: 'grain', label: '필름 입자', min: 0, max: 1, step: 0.05, value: 0 },
      { key: 'paper', label: '종이 질감', min: 0, max: 1, step: 0.05, value: 0 },
      { key: 'vignette', label: '비네팅', min: 0, max: 1, step: 0.05, value: 0 },
      { key: 'frame', label: '테두리', type: 'choice', options: ['없음', '흰 여백', '폴라로이드'], value: '없음' },
      { key: 'frameColor', label: '테두리 색', type: 'choice', options: ['흰색', '크림', '검정'], value: '흰색' },
    ],
    save: [
      { key: 'format', label: '파일 형식', type: 'choice', options: ['PNG', 'JPG'], value: 'PNG' },
      { key: 'out', label: '저장 크기', type: 'choice', options: Object.keys(SAVE_SIZES), value: '최대' },
    ],
  };
  const PHOTO_KEYS = ['auto', 'bright', 'contrast', 'sat', 'zoom', 'px', 'py', 'flip'];

  /* ================= 상태 ================= */
  const defaults = list => Object.fromEntries(list.map(c => [c.key, c.value]));
  const state = {
    img: null, style: STYLES[0], ratio: '4:5', mark: true, more: false,
    vals: {}, pal: {}, custom: {}, picking: false,
    g: { ...defaults(GLOBAL.photo), ...defaults(GLOBAL.finish), ...defaults(GLOBAL.save) },
  };
  const fresh = st => ({ ...defaults(st.controls), seed: 1 });
  STYLES.forEach(st => { state.vals[st.id] = fresh(st); state.pal[st.id] = 0; });

  const el = {
    canvas: $('#lab-canvas'), empty: $('#lab-empty'), file: $('#lab-file'), drop: $('#lab-drop'),
    panel: $('#lab-panel'), demos: $('#lab-demos'), compare: $('#lab-compare'),
  };

  function params(st) {
    const palette = st.palettes[state.pal[st.id]];
    const colors = state.custom[st.id] && state.custom[st.id].base === state.pal[st.id] ? state.custom[st.id].colors : palette.colors;
    return { ...state.vals[st.id], palette, colors };
  }

  function size(maxSide, ratio = state.ratio) {
    let [a, b] = RATIOS[ratio] || (state.img ? [state.img.width, state.img.height] : [4, 5]);
    const srcMax = state.img ? Math.max(state.img.width, state.img.height) : maxSide;
    const long = Math.min(maxSide, Math.max(720, srcMax));
    return a >= b ? [long, Math.round(long * b / a)] : [Math.round(long * a / b), long];
  }

  // 테두리: 그림이 들어갈 안쪽 자리
  function frameBox(W, H) {
    const f = state.g.frame;
    if (f === '흰 여백') { const m = Math.round(Math.min(W, H) * 0.05); return { x: m, y: m, w: W - m * 2, h: H - m * 2 }; }
    if (f === '폴라로이드') { const m = Math.round(W * 0.055); return { x: m, y: m, w: W - m * 2, h: H - m - Math.round(H * 0.16) }; }
    return { x: 0, y: 0, w: W, h: H };
  }

  // 분석본은 (양식, 크기, 사진에 영향 주는 값)이 같으면 다시 만들지 않습니다
  const cache = new Map();
  function prepared(st, w, h) {
    const p = params(st), g = state.g;
    const key = [st.id, w, h, st.id === 'pop' ? p.simplify : '', ...PHOTO_KEYS.map(k => g[k])].join('|');
    if (!cache.has(key)) {
      if (cache.size > 24) cache.clear();
      const k = Math.min(1, ANALYZE_MAX / Math.max(w, h));
      cache.set(key, st.prep(cover(state.img, w * k, h * k, g), p, g));
    }
    return cache.get(key);
  }

  // 마감: 효과 세기(원본 섞기)·필름 입자·종이 질감·가장자리
  function finish(x, w, h) {
    const g = state.g;
    if (g.mix < 1) { x.globalAlpha = 1 - g.mix; x.drawImage(cover(state.img, w, h, g), 0, 0); x.globalAlpha = 1; }
    if (g.grain > 0 || g.paper > 0) {
      const im = x.getImageData(0, 0, w, h), d = im.data, s = w / 1000;
      for (let y = 0; y < h; y++) for (let xx = 0; xx < w; xx++) {
        const i = (y * w + xx) * 4;
        const n = g.grain ? (hash(xx, y, 31) - 0.5) * 34 * g.grain : 0;
        const pp = g.paper ? 1 - g.paper * 0.14 * vnoise(xx / (6 * s), y / (6 * s), 41) - g.paper * 0.06 * hash((xx / 2) | 0, (y / 2) | 0, 43) : 1;
        d[i] = (d[i] + n) * pp; d[i + 1] = (d[i + 1] + n) * pp * 0.99; d[i + 2] = (d[i + 2] + n) * pp * 0.96;
      }
      x.putImageData(im, 0, 0);
    }
    if (g.vignette > 0) {
      const gr = x.createRadialGradient(w / 2, h / 2, Math.min(w, h) * 0.3, w / 2, h / 2, Math.hypot(w, h) / 2);
      gr.addColorStop(0, 'rgba(0,0,0,0)'); gr.addColorStop(1, `rgba(0,0,0,${0.65 * g.vignette})`);
      x.fillStyle = gr; x.fillRect(0, 0, w, h);
    }
  }

  function watermark(x, W, H) {
    const fs = Math.max(10, Math.round(W * 0.019)), pad = Math.round(W * 0.03);
    const d = x.getImageData(Math.max(0, W - pad - fs * 8), Math.max(0, H - pad - fs), fs * 8, fs).data;
    let sum = 0; for (let i = 0; i < d.length; i += 4) sum += d[i] + d[i + 1] + d[i + 2];
    const dark = sum / (d.length / 4) / 765 < 0.5;
    setFont(x, 600, fs, 0.01); x.textAlign = 'right';
    x.fillStyle = dark ? 'rgba(255,255,255,0.8)' : 'rgba(17,17,17,0.6)';
    x.fillText('designrefs.com', W - pad, H - pad);
    resetText(x);
  }

  function draw(target, maxSide, opts = {}) {
    const st = opts.style || state.style, ratio = opts.ratio || state.ratio;
    const [W, H] = size(maxSide, ratio);
    target.width = W; target.height = H;
    const x = ctx2d(target);
    if (opts.original) { x.drawImage(cover(state.img, W, H, state.g), 0, 0); return; }
    const fb = opts.noFrame ? { x: 0, y: 0, w: W, h: H } : frameBox(W, H);
    const inner = canvas(fb.w, fb.h), ix = ctx2d(inner);
    st.render(ix, prepared(st, inner.width, inner.height), inner.width, inner.height, params(st), inner.width / 1000);
    if (!opts.noFinish) finish(ix, inner.width, inner.height);
    if (fb.w !== W || fb.h !== H) {
      x.fillStyle = { '흰색': '#fbfaf7', '크림': '#efe7d6', '검정': '#141414' }[state.g.frameColor];
      x.fillRect(0, 0, W, H);
    }
    x.drawImage(inner, fb.x, fb.y);
    if (state.mark && !opts.noMark) watermark(x, W, H);
  }

  let queued = false;
  function refresh() {
    syncTouch();
    if (!state.img || queued) return;
    queued = true;
    setTimeout(() => { queued = false; draw(el.canvas, PREVIEW_MAX); }, 16);
  }

  let thumbTimer = 0;
  function thumbs() {
    if (!state.img) return;
    clearTimeout(thumbTimer);
    thumbTimer = setTimeout(() => STYLES.forEach((st, i) => setTimeout(() => {
      const b = el.panel.querySelector(`[data-id="${st.id}"] canvas`); if (!b) return;
      draw(b, THUMB, { style: st, ratio: '1:1', noMark: true, noFrame: true, noFinish: true });
      b.closest('.lab__style').classList.add('is-live');
    }, i * 40)), 250);
  }

  /* ================= 패널 ================= */
  function control(c, v, scope) {
    const id = `lab-${scope}-${c.key}`;
    if (c.type === 'choice') return `<div class="lab__row"><span class="lab__label">${c.label}</span><div class="lab__seg">${c.options.map(o =>
      `<button type="button" data-scope="${scope}" data-key="${c.key}" data-val="${o}" class="${v === o ? 'is-on' : ''}">${o}</button>`).join('')}</div></div>`;
    if (c.type === 'toggle') return `<label class="lab__row lab__row--toggle" for="${id}"><span class="lab__label">${c.label}</span>
      <input type="checkbox" class="lab__switch" id="${id}" data-scope="${scope}" data-key="${c.key}"${v ? ' checked' : ''} /></label>`;
    return `<label class="lab__row"><span class="lab__label">${c.label}</span>
      <input type="range" data-scope="${scope}" data-key="${c.key}" min="${c.min}" max="${c.max}" step="${c.step}" value="${v}" /></label>`;
  }
  const sec = (n, title, body, extra = '') => `<section class="lab__sec"${extra}><h2 class="lab__h"><b>${n}</b>${title}</h2>${body}</section>`;

  function renderPanel() {
    const st = state.style, v = state.vals[st.id], M = state.more, g = state.g;
    const pal = params(st);
    let n = 0, num = () => String(++n).padStart(2, '0');
    let html = sec(num(), '양식', `<div class="lab__styles">${STYLES.map(s2 => `
      <button type="button" class="lab__style${s2 === st ? ' is-on' : ''}" data-id="${s2.id}" aria-pressed="${s2 === st}">
        <span class="lab__thumb"><img src="/assets/styles/${s2.thumb}.webp" alt="" width="96" height="96" loading="lazy" /><canvas></canvas></span>
        <span>${s2.name}</span></button>`).join('')}</div><p class="lab__note">${st.note}</p>`);
    html += sec(num(), '다듬기', (st.shuffle ? `<button type="button" class="lab__btn lab__shuffle" id="lab-shuffle">${st.shuffle === true ? '배치 섞기' : st.shuffle}</button>` : '') + st.controls.filter(c => !c.adv).map(c => control(c, v[c.key], 'style')).join(''));
    const mine = !!state.custom[st.id], picking = st.slots && (mine || state.picking);
    html += sec(num(), '색', `<div class="lab__pals">${st.palettes.map((p2, i) => `
      <button type="button" class="lab__pal${!mine && state.pal[st.id] === i ? ' is-on' : ''}" data-i="${i}" title="${p2.name}">
        <span class="lab__dots">${[...new Set(p2.colors)].slice(0, 5).map(c => `<i style="background:${c}"></i>`).join('')}</span><span>${p2.name}</span>
      </button>`).join('')}${st.slots ? `
      <button type="button" class="lab__pal lab__pal--mine${mine ? ' is-on' : ''}" id="lab-mine" aria-expanded="${!!picking}">
        <span class="lab__dots">${mine ? [...new Set(pal.colors)].slice(0, 5).map(c => `<i style="background:${c}"></i>`).join('') : '<i class="lab__wheel"></i>'}</span><span>직접 고르기</span>
      </button>` : ''}</div>` + (picking ? `<div class="lab__colors">${st.slots.map((name, i) => pal.colors[i] ? `
        <label class="lab__color"><input type="color" data-slot="${i}" value="${pal.colors[i]}" /><span>${name}</span></label>` : '').join('')}</div>` : ''));
    html += sec(num(), '비율', `<div class="lab__seg">${Object.keys(RATIOS).map(r =>
      `<button type="button" data-r="${r}" class="${state.ratio === r ? 'is-on' : ''}">${r}</button>`).join('')}</div>` +
      `<label class="lab__check"><input type="checkbox" id="lab-mark"${state.mark ? ' checked' : ''} /> 오른쪽 아래에 designrefs.com 표시</label>`);
    // 더 다듬기: 양식 세부, 사진, 질감, 저장 형식은 필요할 때만 펼칩니다
    const advCtrls = st.controls.filter(c => c.adv);
    html += `<button type="button" class="lab__more" id="lab-more" aria-expanded="${M}">
        <span>${M ? '접기' : '더 다듬기'}</span><small>${[advCtrls.length ? '양식 세부' : '', '사진', '질감', '저장 형식'].filter(Boolean).join(' · ')}</small>
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m6 9 6 6 6-6"/></svg>
      </button>`;
    if (M) {
      html += '<div class="lab__adv">';
      if (advCtrls.length) html += sec(num(), '양식 세부', advCtrls.map(c => control(c, v[c.key], 'style')).join(''));
      html += sec(num(), '사진', GLOBAL.photo.map(c => control(c, g[c.key], 'g')).join('') + '<p class="lab__hint2">확대한 뒤에는 미리보기를 끌어서 위치를 옮길 수도 있습니다</p>');
      html += sec(num(), '질감 · 마감', GLOBAL.finish.map(c => control(c, g[c.key], 'g')).join(''));
      html += sec(num(), '저장 형식', GLOBAL.save.map(c => control(c, g[c.key], 'g')).join(''));
      html += '</div>';
    }
    html += `<div class="lab__actions">
        <button type="button" class="lab__btn lab__btn--main" id="lab-save">${g.format} 저장</button>
        <button type="button" class="lab__btn" id="lab-random" title="이 양식의 값을 무작위로">무작위</button>
        <button type="button" class="lab__btn" id="lab-reset" title="이 양식을 처음 값으로">처음으로</button>
      </div>
      <button type="button" class="lab__link" id="lab-change">다른 사진 열기</button>`;
    // 양식 카드의 내 사진 미리보기는 패널을 다시 그려도 그대로 둡니다.
    // 새 빈 캔버스로 바뀌면 견본 그림이 잠깐 비쳤다가 미리보기로 돌아와 깜빡여 보였습니다.
    const live = {};
    el.panel.querySelectorAll('.lab__style.is-live').forEach(b => { live[b.dataset.id] = b.querySelector('canvas'); });
    const y = window.scrollY;
    el.panel.innerHTML = html;
    window.scrollTo(0, y);
    Object.entries(live).forEach(([id, cv]) => {
      const b = el.panel.querySelector(`.lab__style[data-id="${id}"]`); if (!b) return;
      b.querySelector('canvas').replaceWith(cv); b.classList.add('is-live');
    });
    thumbs();
  }

  function setVal(scope, key, val) {
    if (scope === 'style') state.vals[state.style.id][key] = val; else state.g[key] = val;
  }

  el.panel.addEventListener('click', e => {
    const t = e.target.closest('button'); if (!t) return;
    if (t.id === 'lab-more') { state.more = !state.more; renderPanel(); return; }
    if (t.dataset.id) { state.style = STYLES.find(x => x.id === t.dataset.id); renderPanel(); refresh(); return; }
    if (t.dataset.val !== undefined && t.dataset.key) { setVal(t.dataset.scope, t.dataset.key, t.dataset.val); renderPanel(); refresh(); return; }
    if (t.dataset.i !== undefined) { state.pal[state.style.id] = +t.dataset.i; delete state.custom[state.style.id]; state.picking = false; renderPanel(); refresh(); return; }
    if (t.id === 'lab-mine') { state.picking = !state.picking || !!state.custom[state.style.id]; renderPanel(); return; }
    if (t.dataset.r) { state.ratio = t.dataset.r; renderPanel(); refresh(); return; }
    if (t.id === 'lab-save') return save(t);
    if (t.id === 'lab-change') return el.file.click();
    if (t.id === 'lab-reset') {
      state.vals[state.style.id] = fresh(state.style); state.pal[state.style.id] = 0; delete state.custom[state.style.id];
      renderPanel(); refresh(); return;
    }
    if (t.id === 'lab-shuffle') { state.vals[state.style.id].seed = newSeed(); refresh(); thumbs(); return; }
    if (t.id === 'lab-random') {
      const st = state.style, v = state.vals[st.id];
      v.seed = newSeed();
      st.controls.forEach(c => {
        if (!state.more && c.adv) return;
        if (c.type === 'choice') v[c.key] = pick(c.options);
        else if (c.type === 'toggle') v[c.key] = Math.random() < 0.5;
        else { const steps = Math.round((c.max - c.min) / c.step); v[c.key] = +(c.min + Math.round((0.2 + Math.random() * 0.6) * steps) * c.step).toFixed(4); }
      });
      state.pal[st.id] = Math.floor(Math.random() * st.palettes.length); delete state.custom[st.id];
      renderPanel(); refresh();
    }
  });
  el.panel.addEventListener('input', e => {
    const t = e.target;
    if (t.dataset.slot !== undefined) {
      const st = state.style, base = state.pal[st.id];
      if (!state.custom[st.id] || state.custom[st.id].base !== base) state.custom[st.id] = { base, colors: [...st.palettes[base].colors] };
      state.custom[st.id].colors[+t.dataset.slot] = t.value; refresh(); return;
    }
    if (!t.dataset.key) return;
    if (t.type === 'range') setVal(t.dataset.scope, t.dataset.key, parseFloat(t.value));
    refresh();
  });
  el.panel.addEventListener('change', e => {
    const t = e.target;
    if (t.id === 'lab-mark') { state.mark = t.checked; refresh(); return; }
    if (t.dataset.slot !== undefined) { renderPanel(); return; }
    if (t.type === 'checkbox' && t.dataset.key) { setVal(t.dataset.scope, t.dataset.key, t.checked); refresh(); }
    if (t.dataset.key === 'format') renderPanel();
    if (t.type === 'range' && (t.dataset.scope === 'g' || t.dataset.key === 'simplify')) thumbs();
  });

  /* ---------- 미리보기: 끌어서 위치 옮기기, 원본 비교 ---------- */
  let drag = null;
  // 확대했을 때만 끌어서 옮깁니다. 확대 전에는 휴대폰에서 이미지 위를 쓸어 페이지를 스크롤할 수 있어야 하니까요
  function syncTouch() { el.canvas.style.touchAction = state.g.zoom > 1.001 ? 'none' : 'pan-y'; el.canvas.classList.toggle('is-pannable', state.g.zoom > 1.001); }
  el.canvas.addEventListener('pointerdown', e => {
    if (!state.img || state.g.zoom <= 1.001) return;
    e.preventDefault();
    drag = { x: e.clientX, y: e.clientY, px: state.g.px, py: state.g.py, w: el.canvas.getBoundingClientRect().width };
    el.canvas.setPointerCapture(e.pointerId);
  });
  el.canvas.addEventListener('pointermove', e => {
    if (!drag) return;
    const [W, H] = size(PREVIEW_MAX), fb = frameBox(W, H), z = state.g.zoom;
    const sc = Math.max(fb.w / state.img.width, fb.h / state.img.height) * z;
    const slackX = state.img.width * sc - fb.w, slackY = state.img.height * sc - fb.h, k = W / drag.w;
    if (slackX > 1) state.g.px = clamp(drag.px - (e.clientX - drag.x) * k * 2 / slackX * (state.g.flip ? -1 : 1), -1, 1);
    if (slackY > 1) state.g.py = clamp(drag.py - (e.clientY - drag.y) * k * 2 / slackY, -1, 1);
    refresh();
  });
  ['pointerup', 'pointercancel'].forEach(t => el.canvas.addEventListener(t, () => { if (drag) { drag = null; if (state.more) renderPanel(); thumbs(); } }));
  const showOriginal = on => { if (state.img) on ? draw(el.canvas, PREVIEW_MAX, { original: true }) : refresh(); };
  el.compare.addEventListener('pointerdown', e => { e.preventDefault(); showOriginal(true); });
  ['pointerup', 'pointerleave', 'pointercancel'].forEach(t => el.compare.addEventListener(t, () => showOriginal(false)));

  /* ================= 사진 불러오기 ================= */
  async function load(blob) {
    if (!blob || (blob.type && !/^image\//.test(blob.type))) return;
    if (blob.size > 40 * 1024 * 1024) { alert('40MB 보다 작은 사진을 골라 주세요.'); return; }
    try {
      state.img = 'createImageBitmap' in window
        ? await createImageBitmap(blob, { imageOrientation: 'from-image' })
        : await new Promise((ok, no) => { const i = new Image(); i.onload = () => ok(i); i.onerror = no; i.src = URL.createObjectURL(blob); });
    } catch { alert('이 사진은 열 수 없습니다. JPG나 PNG로 다시 시도해 주세요.'); return; }
    cache.clear();
    Object.assign(state.g, { zoom: 1, px: 0, py: 0, flip: false });
    root.classList.add('has-img');
    el.empty.hidden = true;
    renderPanel(); refresh();
  }
  el.file.addEventListener('change', () => load(el.file.files[0]));
  ['dragenter', 'dragover'].forEach(t => el.drop.addEventListener(t, e => { e.preventDefault(); el.drop.classList.add('is-over'); }));
  ['dragleave', 'drop'].forEach(t => el.drop.addEventListener(t, e => { e.preventDefault(); el.drop.classList.remove('is-over'); }));
  el.drop.addEventListener('drop', e => load(e.dataTransfer.files[0]));
  window.addEventListener('paste', e => { const f = [...(e.clipboardData?.files || [])][0]; if (f) load(f); });
  el.demos.innerHTML = DEMOS.map((d, i) => `<button type="button" data-demo="${i}">${d.label}</button>`).join('');
  el.demos.addEventListener('click', async e => {
    const b = e.target.closest('[data-demo]'); if (!b) return;
    load(await (await fetch(DEMOS[+b.dataset.demo].src)).blob());
  });

  /* ================= 저장 ================= */
  function save(btn) {
    if (!state.img) { el.file.click(); return; }
    const label = btn.textContent, jpg = state.g.format === 'JPG';
    btn.disabled = true; btn.textContent = '만드는 중…';
    setTimeout(() => {
      const out = canvas(1, 1), target = SAVE_SIZES[state.g.out];
      // '인스타 1080' 은 짧은 변을 1080 에 맞춥니다
      const [a, b] = RATIOS[state.ratio] || [state.img.width, state.img.height];
      const long = state.g.out === '인스타 1080' ? Math.round(1080 * Math.max(a, b) / Math.min(a, b)) : target;
      draw(out, long);
      out.toBlob(b2 => {
        const link = document.createElement('a');
        link.href = URL.createObjectURL(b2);
        link.download = `designrefs-${state.style.id}-${state.ratio.replace(':', 'x')}.${jpg ? 'jpg' : 'png'}`;
        document.body.appendChild(link); link.click(); link.remove();
        setTimeout(() => URL.revokeObjectURL(link.href), 4000);
        btn.disabled = false; btn.textContent = label;
      }, jpg ? 'image/jpeg' : 'image/png', 0.92);
    }, 30);
  }

  // /lab/#vaporwave 처럼 열면 그 양식을 고른 채로 시작합니다
  function fromHash() {
    const h = decodeURIComponent(location.hash.slice(1)), st = STYLES.find(x => x.thumb === h || x.id === h);
    if (st && st !== state.style) { state.style = st; renderPanel(); refresh(); }
  }
  window.addEventListener('hashchange', fromHash);
  fromHash();
  renderPanel();
  if (document.fonts && document.fonts.load) document.fonts.load(`600 40px ${FONT}`).then(refresh).catch(() => {});
})();
