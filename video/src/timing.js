// 장면 길이(박자). Reel.jsx 와 render.mjs(음악 컷 위치)가 같이 씁니다.
export const FPS = 30;
export const BEAT = 15;   // 120BPM 한 박 = 15프레임

export function sceneFrames(s) {
  if (s.beats) return s.beats * BEAT;   // 장면마다 길이를 직접 정할 때
  const beats = { hook: 6, site: 6, term: 6, shot: 10, web: 10, lead: 8, figure: 7, outro: 7 }[s.type]
    ?? (s.type === "tip" ? 4 + 2 * (s.points || []).length : 6);
  return beats * BEAT;
}
