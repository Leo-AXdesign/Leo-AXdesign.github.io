/**
 * 릴스 배경음악을 코드로 만듭니다 (저작권 걱정 없는 직접 만든 소리).
 *
 * - 120BPM, A단조(Am–F–C–G) 짧은 루프: 킥·클랩·하이햇 + 베이스 + 패드 + 짧은 훅 멜로디
 * - 장면이 바뀌는 순간(cuts, 초)에 '쉭' 하는 전환음과 타격음을 넣어 화면 전환과 박자를 맞춥니다.
 * - 외부 패키지 없이 WAV(44.1kHz, 16bit, 스테레오)로 씁니다.
 */
import fs from "node:fs";

const SR = 44100;
export const BPM = 120;
export const BEAT = 60 / BPM;              // 0.5초
const BAR = BEAT * 4;

// 화음 근음(Hz)과 화음 구성음(반음): Am F C G
const CHORDS = [
  { root: 55.0, notes: [57, 60, 64] },      // Am  (A3 C4 E4)
  { root: 43.65, notes: [53, 57, 60] },     // F   (F3 A3 C4)
  { root: 65.41, notes: [55, 60, 64] },     // C   (G3 C4 E4)
  { root: 49.0, notes: [55, 59, 62] },      // G   (G3 B3 D4)
];
// 8분음표 훅 멜로디 (MIDI, 0 은 쉼) — 두 마디 반복
const HOOK = [69, 72, 76, 0, 74, 72, 69, 0, 67, 69, 72, 0, 76, 74, 72, 0];
const midi = (n) => 440 * 2 ** ((n - 69) / 12);

// 같은 결과가 나오도록 고정 씨앗 난수
let seed = 7;
const rnd = () => ((seed = (seed * 16807) % 2147483647) / 2147483647) * 2 - 1;

export function makeMusic(seconds, cuts = [], out = "music.wav") {
  const n = Math.ceil((seconds + 0.6) * SR);
  const L = new Float32Array(n), R = new Float32Array(n);
  const add = (i, v, pan = 0) => {
    if (i < 0 || i >= n) return;
    L[i] += v * (1 - Math.max(0, pan));
    R[i] += v * (1 + Math.min(0, pan));
  };

  const kicks = [];
  const kick = (t, gain = 1) => {
    kicks.push(t);
    let ph = 0;
    const s = Math.round(t * SR);
    for (let i = 0; i < 0.4 * SR; i++) {
      const x = i / SR;
      ph += (2 * Math.PI * (48 + 110 * Math.exp(-x * 28))) / SR;
      add(s + i, Math.sin(ph) * Math.exp(-x * 8) * 0.9 * gain);
    }
  };
  const clap = (t) => {
    const s = Math.round(t * SR);
    let prev = 0;
    for (let i = 0; i < 0.22 * SR; i++) {
      const x = i / SR, w = rnd(), hp = w - prev;
      prev = w;
      const env = Math.exp(-x * 16) * (x < 0.012 ? 0.6 : 1);
      add(s + i, hp * env * 0.32 + Math.sin(2 * Math.PI * 185 * x) * Math.exp(-x * 30) * 0.12, (i % 2 ? 0.1 : -0.1));
    }
  };
  const hat = (t, open = false, gain = 1) => {
    const s = Math.round(t * SR);
    let prev = 0;
    for (let i = 0; i < (open ? 0.18 : 0.05) * SR; i++) {
      const w = rnd(), hp = w - prev;
      prev = w;
      add(s + i, hp * Math.exp(-(i / SR) * (open ? 14 : 70)) * 0.11 * gain, 0.25);
    }
  };
  // 전환음: 컷 직전 0.3초 동안 커지는 바람 소리 + 컷 순간 타격
  const whoosh = (t) => {
    const len = 0.32 * SR, s = Math.round(t * SR - len);
    let lp = 0;
    for (let i = 0; i < len; i++) {
      const p = i / len, a = 0.05 + 0.6 * p;   // 갈수록 밝아지는 소리
      lp += a * (rnd() - lp);
      add(s + i, lp * p * p * 0.35, Math.sin(p * Math.PI) * 0.5 - 0.25);
    }
  };
  const crash = (t) => {
    const s = Math.round(t * SR);
    let prev = 0;
    for (let i = 0; i < 1.4 * SR; i++) {
      const w = rnd(), hp = w - prev;
      prev = w;
      add(s + i, hp * Math.exp(-(i / SR) * 3.2) * 0.12, (i % 3) * 0.1 - 0.1);
    }
  };

  const bars = Math.ceil(seconds / BAR);
  for (let b = 0; b < bars; b++) {
    const t0 = b * BAR, ch = CHORDS[b % 4];
    // 드럼: 킥 1·3박(+ 4박 뒤 엇박), 클랩 2·4박, 하이햇 8분
    kick(t0); kick(t0 + 2 * BEAT); kick(t0 + 3.5 * BEAT, 0.7);
    clap(t0 + BEAT); clap(t0 + 3 * BEAT);
    for (let k = 0; k < 8; k++) hat(t0 + k * BEAT / 2, k === 7, k % 2 ? 0.7 : 1);
    // 베이스: 근음 8분음표
    for (let k = 0; k < 8; k++) {
      const s = Math.round((t0 + k * BEAT / 2) * SR), f = ch.root * (k === 6 ? 2 : 1);
      for (let i = 0; i < BEAT / 2 * SR * 0.9; i++) {
        const x = i / SR, ph = 2 * Math.PI * f * x;
        const env = Math.min(1, x * 200) * (0.55 + 0.45 * Math.exp(-x * 9));
        add(s + i, (Math.sin(ph) + 0.35 * Math.sin(2 * ph) + 0.12 * Math.sin(3 * ph)) * env * 0.3);
      }
    }
    // 패드: 화음을 부드러운 톱니(배음 합)로, 좌우 살짝 다르게
    const s = Math.round(t0 * SR), len = BAR * SR;
    for (let i = 0; i < len; i++) {
      const x = i / SR, env = Math.min(1, x * 6) * Math.min(1, (BAR - x) * 8);
      let vL = 0, vR = 0;
      for (const m of ch.notes) {
        const f = midi(m);
        for (let h = 1; h <= 5; h++) {
          vL += Math.sin(2 * Math.PI * f * h * 1.0015 * x) / h;
          vR += Math.sin(2 * Math.PI * f * h * 0.9985 * x) / h;
        }
      }
      L[s + i] += vL * env * 0.022;
      R[s + i] += vR * env * 0.022;
    }
    // 훅 멜로디: 첫 마디(표지) 다음부터, 플럭 소리 + 점8분 메아리
    if (b >= 1) {
      for (let k = 0; k < 8; k++) {
        const note = HOOK[(b % 2) * 8 + k];
        if (!note) continue;
        const f = midi(note), st = t0 + k * BEAT / 2;
        for (const [delay, g, pan] of [[0, 1, 0], [BEAT * 0.75, 0.35, 0.5], [BEAT * 1.5, 0.15, -0.5]]) {
          const s2 = Math.round((st + delay) * SR);
          for (let i = 0; i < 0.35 * SR; i++) {
            const x = i / SR, ph = 2 * Math.PI * f * x;
            add(s2 + i, (Math.sin(ph) + 0.25 * Math.sin(3 * ph)) * Math.exp(-x * 11) * 0.11 * g, pan);
          }
        }
      }
    }
  }
  // 장면 전환: 쉭 + 컷 순간 강조 (첫 장면은 크래시로 시작)
  crash(0);
  for (const c of cuts) {
    if (c <= 0.05 || c >= seconds - 0.05) continue;
    whoosh(c);
    hat(c, true, 1.2);
  }
  crash(Math.max(0, seconds - BAR));

  // 킥이 칠 때 나머지를 살짝 눌러 리듬을 살립니다 (사이드체인 느낌)
  // → 간단히: 전체를 부드럽게 눌러 담기 + 끝 1초 페이드아웃
  let peak = 0;
  for (let i = 0; i < n; i++) peak = Math.max(peak, Math.abs(L[i]), Math.abs(R[i]));
  const g = 0.95 / (peak || 1);
  const buf = Buffer.alloc(44 + n * 4);
  const fadeFrom = (seconds - 1.0) * SR, end = seconds * SR;
  for (let i = 0; i < n; i++) {
    const fade = i < fadeFrom ? 1 : Math.max(0, 1 - (i - fadeFrom) / (end - fadeFrom));
    const l = Math.tanh(L[i] * g * 1.4) * 0.85 * fade, r = Math.tanh(R[i] * g * 1.4) * 0.85 * fade;
    buf.writeInt16LE(Math.round(l * 32767), 44 + i * 4);
    buf.writeInt16LE(Math.round(r * 32767), 46 + i * 4);
  }
  // WAV 머리말
  buf.write("RIFF", 0); buf.writeUInt32LE(36 + n * 4, 4); buf.write("WAVE", 8);
  buf.write("fmt ", 12); buf.writeUInt32LE(16, 16); buf.writeUInt16LE(1, 20); buf.writeUInt16LE(2, 22);
  buf.writeUInt32LE(SR, 24); buf.writeUInt32LE(SR * 4, 28); buf.writeUInt16LE(4, 32); buf.writeUInt16LE(16, 34);
  buf.write("data", 36); buf.writeUInt32LE(n * 4, 40);
  fs.writeFileSync(out, buf);
  return out;
}

// 단독 실행: node music.mjs 20 out.wav
if (process.argv[1] && process.argv[1].endsWith("music.mjs")) {
  const sec = Number(process.argv[2] || 20);
  console.log(makeMusic(sec, [3, 6, 9, 12, 15, 18], process.argv[3] || "music.wav"));
}
