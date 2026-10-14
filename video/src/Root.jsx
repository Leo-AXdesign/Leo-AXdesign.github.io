import React from "react";
import { Composition } from "remotion";
import { Reel, FPS, sceneFrames } from "./Reel.jsx";

// 미리보기(npm run studio)용 예시. 실제 영상은 render.mjs 가 묶음마다 props 를 넣어 만듭니다.
const sample = {
  kicker: "레퍼런스 · 컬러",
  scenes: [
    { type: "hook", title: "컬러 막힐 때\n열어 볼 사이트 5", sub: "끝까지 보고 저장해 두세요" },
    { type: "site", n: 1, total: 2, name: "Coolors", host: "coolors.co", text: "스페이스바로 팔레트를 빠르게 생성", tags: ["팔레트", "무료"] },
    { type: "site", n: 2, total: 2, name: "Realtime Colors", host: "realtimecolors.com", text: "팔레트를 실제 웹 UI에 바로 적용해 보며 확인", tags: ["미리보기"] },
    { type: "tip", title: "고르기 전에", points: ["배경과 글자 대비부터", "색은 다섯 개 이내로"] },
    { type: "outro", title: "컬러 사이트 24곳,\n한 페이지에 모아 뒀어요", url: "designrefs.com/color" },
  ],
  music: null,
};

export const Root = () => (
  <Composition
    id="Reel"
    component={Reel}
    width={1080}
    height={1920}
    fps={FPS}
    durationInFrames={300}
    defaultProps={sample}
    calculateMetadata={({ props }) => ({
      durationInFrames: props.scenes.reduce((a, s) => a + sceneFrames(s), 0),
    })}
  />
);
