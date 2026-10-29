import React from "react";
import {
  AbsoluteFill, Audio, Img, Sequence, continueRender, delayRender, interpolate, spring, staticFile,
  useCurrentFrame, useVideoConfig,
} from "remotion";

import { BEAT, FPS, sceneFrames } from "./timing.js";

export { FPS, sceneFrames };

const C = { bg: "#F4F4F4", ink: "#111111", mute: "#6B6B6B", dot: "#A3A3A3", line: "#DDDDDD", white: "#FFFFFF" };
const FONT = '"Pretendard Variable", Pretendard, "Apple SD Gothic Neo", "Noto Sans KR", sans-serif';

// ---------- 글꼴 (Pretendard) ----------
const fontHandle = typeof window !== "undefined" ? delayRender("Pretendard 글꼴") : null;
if (typeof window !== "undefined") {
  const f = new FontFace("Pretendard Variable",
    "url(https://cdn.jsdelivr.net/npm/pretendard@1.3.9/dist/web/variable/woff2/PretendardVariable.woff2)",
    { weight: "45 920" });
  f.load().then((ff) => { document.fonts.add(ff); continueRender(fontHandle); })
    .catch(() => continueRender(fontHandle));   // 못 받으면 기본 글꼴로라도 만듭니다
}

// ---------- 움직임 도구 ----------
const useSpring = (delay = 0, config = { damping: 200 }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  return spring({ frame: frame - delay, fps, config });
};

// 아래에서 위로 올라오며 나타나는 한 줄 (가림막 안에서)
const Rise = ({ children, delay = 0, style }) => {
  const p = useSpring(delay, { damping: 18, stiffness: 140, mass: 0.6 });
  return (
    <div style={{ overflow: "hidden", ...style }}>
      <div style={{ transform: `translateY(${(1 - p) * 110}%)` }}>{children}</div>
    </div>
  );
};

// 낱말마다 차례로 나타나는 문장
const Words = ({ text, delay = 0, step = 2, style }) => {
  const frame = useCurrentFrame();
  return (
    <div style={{ display: "flex", flexWrap: "wrap", columnGap: "0.28em", rowGap: 6, wordBreak: "keep-all", ...style }}>
      {String(text).split(/\s+/).map((w, i) => {
        const t = frame - delay - i * step;
        return (
          <span key={i} style={{
            opacity: interpolate(t, [0, 6], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }),
            transform: `translateY(${interpolate(t, [0, 8], [18, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" })}px)`,
          }}>{w}</span>
        );
      })}
    </div>
  );
};

const Lines = ({ text, delay = 0, step = 5, size, weight = 800, color }) => (
  <div style={{ fontSize: size, fontWeight: weight, color, lineHeight: 1.14, letterSpacing: "-0.045em", wordBreak: "keep-all" }}>
    {String(text).split("\n").map((ln, i) => <Rise key={i} delay={delay + i * step}>{ln}</Rise>)}
  </div>
);

// 장면이 들어올 때 살짝 당겨지는 느낌
const Enter = ({ children, dark }) => {
  const frame = useCurrentFrame();
  const s = interpolate(frame, [0, 7], [1.035, 1], { extrapolateRight: "clamp" });
  return (
    <AbsoluteFill style={{ background: dark ? C.ink : C.bg, transform: `scale(${s})` }}>
      {children}
    </AbsoluteFill>
  );
};

// ---------- 장면 ----------
const Hook = ({ s }) => {
  const bar = useSpring(16, { damping: 20 });
  const frame = useCurrentFrame();
  return (
    <Enter>
      <AbsoluteFill style={{ padding: "0 96px", justifyContent: "center" }}>
        <Lines text={s.title} size={s.title.length > 22 ? 104 : 124} color={C.ink} />
        <div style={{ height: 14, width: 220 * bar, background: C.ink, marginTop: 56 }} />
        <div style={{ marginTop: 40, fontSize: 40, color: C.mute, fontWeight: 600,
          opacity: interpolate(frame, [22, 32], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }) }}>
          {s.sub}
        </div>
      </AbsoluteFill>
    </Enter>
  );
};

const Site = ({ s, dark }) => {
  const num = useSpring(0, { damping: 16, stiffness: 120 });
  const name = useSpring(4, { damping: 13, stiffness: 160, mass: 0.7 });
  const pill = useSpring(10, { damping: 16 });
  const frame = useCurrentFrame();
  const fg = dark ? C.white : C.ink, sub = dark ? "#B5B5B5" : C.mute;
  return (
    <Enter dark={dark}>
      <AbsoluteFill style={{ padding: "0 96px", justifyContent: "center" }}>
        <div style={{ display: "flex", alignItems: "baseline", gap: 18, transform: `translateX(${(1 - num) * -80}px)`, opacity: num }}>
          <span style={{ fontSize: 220, fontWeight: 900, letterSpacing: "-0.06em", color: dark ? "#3A3A3A" : C.line, lineHeight: 0.9 }}>
            {String(s.n).padStart(2, "0")}
          </span>
          {s.total ? <span style={{ fontSize: 44, fontWeight: 700, color: C.dot }}>/ {String(s.total).padStart(2, "0")}</span> : null}
        </div>
        {s.label ? <div style={{ marginTop: 26, fontSize: 36, fontWeight: 700, color: C.dot }}>{s.label}</div> : null}
        <div style={{ marginTop: 26, fontSize: s.name.length > 14 ? 104 : 132, fontWeight: 850, letterSpacing: "-0.045em", lineHeight: 1.05,
          color: fg, transform: `translateY(${(1 - name) * 60}px) scale(${0.92 + 0.08 * name})`, transformOrigin: "left bottom", opacity: name,
          wordBreak: "keep-all" }}>
          {s.name}
        </div>
        {s.host ? (
          <div style={{ marginTop: 34, alignSelf: "flex-start", fontSize: 36, fontWeight: 600, padding: "14px 30px", borderRadius: 999,
            background: dark ? C.white : C.ink, color: dark ? C.ink : C.white, transform: `scale(${pill})`, transformOrigin: "left center" }}>
            {s.host}
          </div>
        ) : null}
        <Words text={s.text} delay={14} style={{ marginTop: 52, fontSize: 52, fontWeight: 600, lineHeight: 1.38, color: sub }} />
        <div style={{ display: "flex", gap: 14, marginTop: 44 }}>
          {(s.tags || []).slice(0, 3).map((t, i) => (
            <span key={t} style={{ fontSize: 30, padding: "10px 22px", borderRadius: 999, border: `2px solid ${dark ? "#444" : C.line}`,
              color: sub, opacity: interpolate(frame, [30 + i * 3, 38 + i * 3], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }) }}>
              #{t}
            </span>
          ))}
        </div>
      </AbsoluteFill>
    </Enter>
  );
};

// 사이트 투어: 위에는 이름·주소·한 줄, 아래 폰 화면 안에서 실제 사이트가 위→아래로 스크롤됩니다
const FRAME_W = 820, FRAME_H = 1040, BORDER = 12;
const Shot = ({ s, dark }) => {
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();
  const head = useSpring(0, { damping: 16, stiffness: 140 });
  const phone = useSpring(4, { damping: 18, stiffness: 110 });
  const inner = FRAME_W - BORDER * 2;
  const imgH = (s.shot_h || 3000) * inner / 1080;
  const dist = Math.max(0, Math.min(imgH - (FRAME_H - BORDER * 2), 2200));
  // 잠깐 멈췄다가 천천히 내려가고, 끝에서 잠깐 멈춥니다
  const t = interpolate(frame, [BEAT, durationInFrames - BEAT * 1.5], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const ease = t < 0.5 ? 2 * t * t : 1 - Math.pow(-2 * t + 2, 2) / 2;
  const fg = dark ? C.white : C.ink, sub = dark ? "#B5B5B5" : C.mute;
  return (
    <Enter dark={dark}>
      <div style={{ position: "absolute", top: 230, left: 80, right: 80, opacity: head, transform: `translateY(${(1 - head) * 30}px)` }}>
        <div style={{ display: "flex", alignItems: "center", gap: 18 }}>
          <span style={{ fontSize: 34, fontWeight: 800, color: C.dot }}>{String(s.n).padStart(2, "0")} / {String(s.total).padStart(2, "0")}</span>
          <span style={{ fontSize: 30, fontWeight: 600, padding: "8px 22px", borderRadius: 999,
            background: dark ? C.white : C.ink, color: dark ? C.ink : C.white }}>{s.host}</span>
        </div>
        <div style={{ marginTop: 14, fontSize: s.name.length > 16 ? 72 : 92, fontWeight: 850, letterSpacing: "-0.045em", color: fg, lineHeight: 1.05 }}>{s.name}</div>
        <Words text={s.text} delay={8} style={{ marginTop: 16, fontSize: 40, fontWeight: 600, color: sub, lineHeight: 1.35 }} />
      </div>
      <div style={{ position: "absolute", left: (1080 - FRAME_W) / 2, top: 640, width: FRAME_W, height: FRAME_H,
        borderRadius: 64, border: `${BORDER}px solid ${dark ? "#2A2A2A" : C.ink}`, overflow: "hidden", background: C.white,
        boxShadow: "0 40px 90px rgba(0,0,0,0.18)", transform: `translateY(${(1 - phone) * 500}px)` }}>
        <Img src={staticFile(s.shot)} style={{ width: inner, display: "block", transform: `translateY(${-dist * ease}px)` }} />
      </div>
    </Enter>
  );
};

// 사이트 투어 (데스크톱): 데스크톱 화면이 영상 전체를 채우고 위→아래로 스크롤, 위엔 주소창, 아래엔 이름·한 줄
const Web = ({ s }) => {
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();
  const enter = useSpring(0, { damping: 20, stiffness: 120 });
  const text = useSpring(6, { damping: 16, stiffness: 140 });
  const BAR = 96, TOP = 210;                       // 주소창 높이, 주소창이 놓이는 위치
  const viewH = 1920 - TOP - BAR;
  const dist = Math.max(0, Math.min((s.shot_h || 3000) - viewH, 2600));
  const t = interpolate(frame, [BEAT * 1.5, durationInFrames - BEAT], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const ease = t < 0.5 ? 2 * t * t : 1 - Math.pow(-2 * t + 2, 2) / 2;
  const zoom = interpolate(enter, [0, 1], [1.08, 1]);
  return (
    <AbsoluteFill style={{ background: C.ink }}>
      {/* 사이트 화면 */}
      <div style={{ position: "absolute", top: TOP + BAR, left: 0, width: 1080, height: viewH, overflow: "hidden", background: C.white,
        transform: `scale(${zoom})`, transformOrigin: "50% 0%", opacity: enter }}>
        <Img src={staticFile(s.shot)} style={{ width: 1080, display: "block", transform: `translateY(${-dist * ease}px)` }} />
      </div>
      {/* 브라우저 주소창 */}
      <div style={{ position: "absolute", top: TOP, left: 0, right: 0, height: BAR, background: "#202020", display: "flex",
        alignItems: "center", gap: 22, padding: "0 34px", opacity: enter }}>
        {["#FF5F57", "#FEBC2E", "#28C840"].map((c) => <span key={c} style={{ width: 22, height: 22, borderRadius: 99, background: c }} />)}
        <div style={{ flex: 1, height: 56, borderRadius: 14, background: "#353535", color: "#E8E8E8", fontSize: 30, fontWeight: 600,
          display: "flex", alignItems: "center", padding: "0 26px", gap: 14 }}>
          <span style={{ width: 16, height: 16, borderRadius: 4, border: "3px solid #9A9A9A", flex: "none" }} />{s.host}
        </div>
      </div>
      {/* 아래 설명 띠 */}
      <div style={{ position: "absolute", left: 0, right: 0, bottom: 0, height: 760,
        background: "linear-gradient(to bottom, rgba(17,17,17,0) 0%, rgba(17,17,17,0.82) 42%, rgba(17,17,17,0.96) 100%)" }} />
      <div style={{ position: "absolute", left: 72, right: 72, bottom: 230, opacity: text, transform: `translateY(${(1 - text) * 40}px)` }}>
        {s.n ? <div style={{ fontSize: 34, fontWeight: 800, color: "#B5B5B5" }}>{String(s.n).padStart(2, "0")} / {String(s.total).padStart(2, "0")}</div> : null}
        <div style={{ marginTop: 10, fontSize: s.name.length > 16 ? 76 : 96, fontWeight: 850, letterSpacing: "-0.045em", color: C.white, lineHeight: 1.05 }}>{s.name}</div>
        <Words text={s.text} delay={10} style={{ marginTop: 18, fontSize: 44, fontWeight: 600, color: "#D6D6D6", lineHeight: 1.35 }} />
      </div>
    </AbsoluteFill>
  );
};

const Lead = ({ s }) => (
  <Enter>
    <AbsoluteFill style={{ padding: "0 96px", justifyContent: "center" }}>
      <Rise><div style={{ fontSize: 40, fontWeight: 700, color: C.dot }}>{s.label}</div></Rise>
      <Words text={s.text} delay={6} step={2} style={{ marginTop: 40, fontSize: 64, fontWeight: 750, lineHeight: 1.36, color: C.ink, letterSpacing: "-0.03em" }} />
    </AbsoluteFill>
  </Enter>
);

const Figure = ({ s }) => {
  const up = useSpring(0, { damping: 18, stiffness: 110 });
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();
  const zoom = interpolate(frame, [0, durationInFrames], [1, 1.05]);
  return (
    <Enter>
      <AbsoluteFill style={{ padding: "0 64px", justifyContent: "center", alignItems: "center" }}>
        {s.label ? (   // 그림 위 이름표 (예: 현상소 양식 이름)
          <div style={{ alignSelf: "flex-start", display: "flex", alignItems: "center", gap: 18, marginBottom: 36, opacity: up }}>
            {s.n ? <span style={{ fontSize: 34, fontWeight: 800, color: C.dot }}>{String(s.n).padStart(2, "0")} / {String(s.total).padStart(2, "0")}</span> : null}
            <span style={{ fontSize: 64, fontWeight: 850, letterSpacing: "-0.04em", color: C.ink }}>{s.label}</span>
          </div>
        ) : null}
        <div style={{ width: "100%", borderRadius: 36, overflow: "hidden", background: C.white,
          boxShadow: "0 30px 80px rgba(0,0,0,0.12)", transform: `translateY(${(1 - up) * 300}px)`, opacity: up }}>
          <Img src={staticFile(s.image)} style={{ width: "100%", display: "block", transform: `scale(${zoom})` }} />
        </div>
      </AbsoluteFill>
    </Enter>
  );
};

const Tip = ({ s }) => {
  const frame = useCurrentFrame();
  return (
    <Enter dark>
      <AbsoluteFill style={{ padding: "0 96px", justifyContent: "center" }}>
        <Lines text={s.title} size={96} color={C.white} />
        <div style={{ marginTop: 70, display: "flex", flexDirection: "column", gap: 44 }}>
          {(s.points || []).map((p, i) => {
            const t = frame - (BEAT * 2 + i * BEAT * 2);
            const o = interpolate(t, [0, 8], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
            return (
              <div key={i} style={{ display: "flex", gap: 30, alignItems: "flex-start", opacity: o, transform: `translateX(${(1 - o) * 60}px)` }}>
                <span style={{ flex: "none", width: 76, height: 76, borderRadius: 999, background: C.white, color: C.ink,
                  fontSize: 40, fontWeight: 800, display: "flex", alignItems: "center", justifyContent: "center" }}>{i + 1}</span>
                <span style={{ fontSize: 54, fontWeight: 700, color: C.white, lineHeight: 1.3, wordBreak: "keep-all" }}>{p}</span>
              </div>
            );
          })}
        </div>
      </AbsoluteFill>
    </Enter>
  );
};

const Outro = ({ s }) => {
  const pill = useSpring(14, { damping: 12, stiffness: 150 });
  const frame = useCurrentFrame();
  const bob = Math.sin((frame / BEAT) * Math.PI) * 6;   // 박자에 맞춰 살짝 들썩
  return (
    <Enter>
      <AbsoluteFill style={{ padding: "0 96px", justifyContent: "center" }}>
        <Lines text={s.title} size={96} color={C.ink} />
        <div style={{ marginTop: 70, alignSelf: "flex-start", fontSize: 54, fontWeight: 800, padding: "26px 46px", borderRadius: 999,
          background: C.ink, color: C.white, transform: `scale(${pill}) translateY(${bob}px)`, transformOrigin: "left center" }}>
          {s.url} →
        </div>
        <div style={{ marginTop: 50, fontSize: 40, fontWeight: 600, color: C.mute,
          opacity: interpolate(frame, [26, 36], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }) }}>
          {s.sub || "저장해 두면 필요할 때 바로 꺼내 볼 수 있어요"}
        </div>
      </AbsoluteFill>
    </Enter>
  );
};

const SCENES = { hook: Hook, site: Site, term: Site, shot: Shot, web: Web, lead: Lead, figure: Figure, tip: Tip, outro: Outro };

// ---------- 전체 ----------
const Chrome = ({ scenes, starts, kicker }) => {
  const frame = useCurrentFrame();
  const i = Math.max(0, starts.findLastIndex((st) => frame >= st));
  const dark = scenes[i].type === "web" || (["site", "term", "shot"].includes(scenes[i].type) ? scenes[i].n % 2 === 0 : scenes[i].type === "tip");
  const fg = dark ? C.white : C.ink;
  return (
    <AbsoluteFill style={{ pointerEvents: "none" }}>
      <div style={{ position: "absolute", top: 70, left: 64, right: 64, display: "flex", gap: 8 }}>
        {scenes.map((s, k) => {
          const len = sceneFrames(s);
          const p = Math.min(1, Math.max(0, (frame - starts[k]) / len));
          return (
            <div key={k} style={{ flex: 1, height: 7, borderRadius: 9, background: dark ? "rgba(255,255,255,0.22)" : "rgba(0,0,0,0.1)", overflow: "hidden" }}>
              <div style={{ width: `${p * 100}%`, height: "100%", background: fg }} />
            </div>
          );
        })}
      </div>
      <div style={{ position: "absolute", top: 112, left: 64, right: 64, display: "flex", justifyContent: "space-between", alignItems: "baseline" }}>
        <span style={{ fontSize: 58, fontWeight: 900, color: fg, letterSpacing: "-0.05em" }}>d<span style={{ color: C.dot }}>.</span></span>
        <span style={{ fontSize: 30, fontWeight: 600, color: dark ? "#B5B5B5" : C.mute }}>{kicker}</span>
      </div>
      <div style={{ position: "absolute", bottom: 150, left: 64, fontSize: 30, fontWeight: 600, color: dark ? "#8A8A8A" : C.dot }}>
        designrefs.com
      </div>
    </AbsoluteFill>
  );
};

export const Reel = ({ scenes, kicker, music }) => {
  const starts = [];
  let t = 0;
  for (const s of scenes) { starts.push(t); t += sceneFrames(s); }
  return (
    <AbsoluteFill style={{ fontFamily: FONT, background: C.bg }}>
      {scenes.map((s, k) => {
        const Scene = SCENES[s.type] || Lead;
        const dark = (s.type === "site" || s.type === "term" || s.type === "shot") && s.n % 2 === 0;
        return (
          <Sequence key={k} from={starts[k]} durationInFrames={sceneFrames(s)}>
            <Scene s={s} dark={dark} />
          </Sequence>
        );
      })}
      <Chrome scenes={scenes} starts={starts} kicker={kicker} />
      {music ? <Audio src={staticFile(music)} /> : null}
    </AbsoluteFill>
  );
};
