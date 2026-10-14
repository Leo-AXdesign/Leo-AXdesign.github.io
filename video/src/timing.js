// 장면 길이(박자). Reel.jsx 와 render.mjs(음악 컷 위치)가 같이 씁니다.
export const FPS = 30;
export const BEAT = 15;   // 120BPM 한 박 = 15프레임

export function sceneFrames(s) {
  const beats = { hook: 6, site: 6, term: 6, lead: 8, figure: 7, outro: 7 }[s.type]
    ?? (s.type === "tip" ? 4 + 2 * (s.points || []).length : 6);
  return beats * BEAT;
}
