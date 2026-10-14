/**
 * 모션 릴스 만들기 (Remotion)
 *   node video/render.mjs <props.json> <out.mp4> [cover.jpg]
 *
 * props.json: { kicker, scenes: [...], music: "auto" | "<저장소 기준 음원 경로>" | null }
 * - 그림(figure 장면의 image)은 저장소 기준 경로. video/public/r/ 에 복사해서 씁니다.
 * - music 이 "auto" 면 music.mjs 로 장면 전환 박자에 맞춘 음악을 만들어 넣습니다.
 * - 진행 상황을 "PROGRESS <0~100> <단계>" 줄로 출력합니다 (스튜디오 진행 막대용).
 */
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { bundle } from "@remotion/bundler";
import { ensureBrowser, renderMedia, renderStill, selectComposition } from "@remotion/renderer";
import { makeMusic } from "./music.mjs";
import { FPS, sceneFrames } from "./src/timing.js";

const HERE = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.dirname(HERE);
const PUB = path.join(HERE, "public");
const [propsFile, outFile, coverFile] = process.argv.slice(2);
if (!propsFile || !outFile) {
  console.error("쓰는 법: node video/render.mjs <props.json> <out.mp4> [cover.jpg]");
  process.exit(1);
}
const say = (pct, stage) => console.log(`PROGRESS ${Math.round(pct)} ${stage}`);

const props = JSON.parse(fs.readFileSync(propsFile, "utf8"));
fs.rmSync(path.join(PUB, "r"), { recursive: true, force: true });
fs.mkdirSync(path.join(PUB, "r"), { recursive: true });

// 그림 복사
props.scenes.forEach((s, i) => {
  if (s.image) {
    const dst = `r/${i}-${path.basename(s.image)}`;
    fs.copyFileSync(path.join(ROOT, s.image), path.join(PUB, dst));
    s.image = dst;
  }
});

// 음악
const frames = props.scenes.reduce((a, s) => a + sceneFrames(s), 0);
const seconds = frames / FPS;
if (props.music === "auto") {
  const cuts = [];
  let t = 0;
  for (const s of props.scenes) { cuts.push(t / FPS); t += sceneFrames(s); }
  makeMusic(seconds, cuts, path.join(PUB, "r", "music.wav"));
  props.music = "r/music.wav";
} else if (props.music) {
  const dst = `r/music${path.extname(props.music)}`;
  fs.copyFileSync(path.join(ROOT, props.music), path.join(PUB, dst));
  props.music = dst;
}
say(3, "음악 준비 완료");

const browserExecutable = process.env.REMOTION_BROWSER || null;
// 처음 한 번은 영상용 브라우저(약 100MB)를 받습니다
await ensureBrowser({ browserExecutable, onBrowserDownload: () => {
  say(3, "처음 한 번만: 영상용 브라우저 받는 중");
  return { version: null, onProgress: ({ percent }) => say(3 + percent * 0.05, "처음 한 번만: 영상용 브라우저 받는 중") };
} });
const serveUrl = await bundle({
  entryPoint: path.join(HERE, "src", "index.jsx"),
  publicDir: PUB,
  onProgress: (p) => say(3 + p * 0.12, "영상 틀 묶는 중"),
});
const composition = await selectComposition({ serveUrl, id: "Reel", inputProps: props, browserExecutable });
let last = -1;
await renderMedia({
  serveUrl, composition, inputProps: props, browserExecutable,
  codec: "h264", crf: 20, pixelFormat: "yuv420p", colorSpace: "bt709", audioCodec: "aac", enforceAudioTrack: true,
  outputLocation: outFile,
  onProgress: ({ progress }) => {
    const pct = Math.round(15 + progress * 80);
    if (pct !== last) { last = pct; say(pct, "장면 그리는 중"); }
  },
});
if (coverFile) {
  await renderStill({ serveUrl, composition, inputProps: props, browserExecutable,
    frame: Math.min(45, frames - 1), output: coverFile, imageFormat: "jpeg", jpegQuality: 90 });
}
say(100, "완료");
console.log(`DONE ${seconds.toFixed(1)}`);
