---
slug: figma-shader-plugin-version-restore
title: "아까 효과가 더 나았어요" 메일 한 통, 피그마 셰이더와 생성 플러그인에 버전 기록이 생겼다
desc: 피그마 에이전트가 만든 셰이더와 생성 플러그인을 고치면 이제 이전 버전이 남고, 되돌릴 수 있다. 10월 27일 릴리스 노트와 개발자 문서에서 확인된 것, 화면에서 어디서 보는지 같은 비어 있는 부분, 수정 전에 해 둘 일을 적었다.
date: 2026-10-30
order: 1
tag: AI 디자인
related: ai, tools, ui-ux
---

클라이언트 메일은 짧다. "아까 그 빛 번지는 효과가 더 나았어요. 그걸로 다시 보여 주세요."

피그마 에이전트에게 셰이더를 만들어 달라고 했고, 마음에 안 드는 부분을 두세 번 고쳐 달라고 했다. 그사이 처음 버전은 사라졌다. 이런 장면이 이제는 덜 곤란해질 수 있다. (가정해서 그린 장면이다. 내가 겪은 일은 아니다.)

10월 27일 피그마 릴리스 노트에 항목이 하나 올라왔다. 제목은 "View and restore previous versions of your generative plugins and shaders"다. 이 글은 직접 써 본 후기가 아니다. 릴리스 노트, 피그마 도움말과 포럼 공지, 개발자 문서를 열어 확인한 내용만 적었다. 버전 목록이 화면의 어느 메뉴에 있는지는 내가 연 자료 어디에도 나오지 않았다.

![피그마 릴리스 노트의 10월 27일 항목 (출처: https://www.figma.com/release-notes/, 캡처일 2026-10-30)](https://designrefs.com/articles/img/figma-shader-plugin-version-restore-shot1.webp)
## 먼저, 셰이더와 생성 플러그인이 무엇인가

셰이더는 화면의 픽셀을 실시간으로 바꾸는 작은 그래픽 프로그램이다. 이미지나 레이어에 효과로 얹거나(셰이더 효과), 도형의 채우기로 쓴다(셰이더 채우기). 도움말에는 효과 쪽 예로 Bloom, Dither, Halftone, Gooey merge, Warp가, 채우기 쪽 예로 Clouds, Fractal noise, Mesh gradient, Water caustics가 올라 있다.

생성 플러그인은 코드로 돌아가는 도구다. 레이아웃을 만들어 주거나 QR 코드를 그려 주는 식이다. 둘 다 에이전트에게 말로 부탁하면 만들어 준다. 9월 1일 피그마 블로그에서 제품 디자이너 로지 킹은 "한 번의 간단한 프롬프트로, 맞추려면 두 번쯤"이면 같은 셰이더를 만들 수 있었다고 적었다.

## 릴리스 노트에 적힌 것

본문은 세 덩어리다.

- 생성 플러그인과 셰이더를 고치면 이제 새 버전이 만들어지고, 이전 버전은 보존되어 다시 보거나 복원할 수 있다.
- 새 버전마다 에이전트가 쓴 설명이 붙어 변경 기록(change log)이 된다. 현재 게시된 버전이 무엇인지도 볼 수 있다.
- "Rolling out this week." 이번 주에 순차 적용된다.

| 항목 | 릴리스 노트에 적힌 내용 |
|---|---|
| 날짜 | 2026년 10월 27일, 이번 주 순차 적용 |
| 대상 | 생성 플러그인, 셰이더 |
| 되는 일 | 이전 버전 보기, 복원 |
| 변경 기록 | 버전마다 에이전트가 쓴 설명 |
| 보는 위치 | 언급 없음 |
| 플랜 | 언급 없음 |

※ 출처: [Figma Release Notes](https://www.figma.com/release-notes/) (2026-10-30 확인). 표의 '언급 없음'은 노트에 해당 내용이 없다는 뜻이다.

이 항목에는 도움말 링크도 붙어 있지 않았다. 그래서 버튼 이름이나 클릭 순서는 적을 수 없다.

## 변경 기록을 에이전트가 쓴다는 점

사람이 버전 이름을 붙이는 일은 대개 하다 만다. "최종", "최종2", "진짜최종"이 되기 십상이다. 이번 항목은 새 버전마다 에이전트가 설명을 붙인다고 했으니, 적어도 목록에서 "무엇이 바뀐 버전인지"는 글로 남는다.

다만 그 설명이 얼마나 정확한지는 모른다. 에이전트가 "빛 번짐을 약하게 조정"이라고 적어 놓고 실제로는 색도 바꿨을 수 있다. 설명을 믿기 전에 버전을 열어 눈으로 확인하는 편이 안전하다. 이것은 일반적인 주의이고, 이 기능에서 그런 오류가 났다는 보고를 본 것은 아니다.

## 이 버전 기록은 어디까지 닿나

개발자 문서(생성 플러그인과 셰이더, Figma MCP 서버)에도 버전 이야기가 나온다. 다만 이것은 릴리스 노트의 복원 기능과 별개의 이야기다.

- 읽기 도구는 선택 항목으로 `version`을 받는다. 40자리 커밋 해시(SHA)다. 비워 두면 최신 버전을 돌려준다. 특정 버전으로 파일이 쓰는 코드를 그대로 읽거나, 두 버전을 비교하는 데 쓰라고 적혀 있다.
- 수정 요청은 호출 안에서 곧바로 빌드, 버전 부여, 배포까지 된다. "There's no separate publish step." 따로 게시 단계가 없다.
- 수정은 기존 파일을 통째로 바꾸는 방식만 된다. 셰이더는 `main.ts`, 플러그인은 `code.ts`와 `ui.html`만 바꿀 수 있다. 애니메이션과 마우스 반응을 정하는 `features.json`이나 `manifest.json`은 못 바꾼다.
- 소스 코드는 접근 권한이 있는 누구에게나 보인다. 비밀번호나 키를 넣으면 안 된다고 문서가 경고한다.
- 빌드가 실패하면 에이전트는 컴파일러가 알려 준 가장 작은 수정을 한 번 더 시도하고, 그래도 안 되면 오류를 보여 준다.

여기서 눈에 띄는 대목은 "별도 게시 단계가 없다"는 줄이다. 외부 에이전트로 수정을 부탁하면 곧바로 반영된다. 되돌릴 길이 없으면 부담스러운 구조인데, 이번 버전 기록이 그 빈자리를 메우는 것으로 보인다. 다만 개발자 문서가 이 복원 기능을 언급하는지는 확인하지 못했다. 둘이 어떻게 이어지는지는 나의 짐작이다.

## 같은 시기에 확인되는 것들

10월 7일 포럼 공지에는 이 기능들의 확장이 정리돼 있다.

- 마우스 움직임에 반응하는 모션 셰이더를 에이전트에게 만들어 달라고 할 수 있다.
- 만든 셰이더와 생성 플러그인을 피그마 커뮤니티에 게시할 수 있다.
- 조직 안에서만 공유하는 비공개 게시는 Organization과 Enterprise 플랜에서만 된다.
- 셰이더와 플러그인의 코드를 피그마 안에서 보고 내려받을 수 있다.
- 외부 에이전트가 MCP로 생성 플러그인과 셰이더를 보고 고칠 수 있다. 셰이더를 입힌 디자인을 외부 에이전트에 복사하면 생성된 React 코드에서도 셰이더가 제대로 그려진다고 한다.

도움말에는 사용 가능한 플랜이 Starter, Professional, Education, Organization, Enterprise로 적혀 있고, 파일 편집 권한이 필요하다. 셰이더는 아직 오픈 베타라서 "기능이 바뀔 수 있고 성능 문제가 생길 수 있다"고 안내한다.

※ 출처: [Figma 포럼: Updates to generative plugins and shaders](https://forum.figma.com/product-updates-3/updates-to-generative-plugins-and-shaders-57397), [Figma 도움말: 피그마가 만든 셰이더·플러그인 목록](https://help.figma.com/hc/en-us/articles/41409034424215), [Figma MCP 서버 문서](https://developers.figma.com/docs/figma-mcp-server/generative-plugins-and-shaders/)

![Figma MCP 서버 문서의 생성 플러그인과 셰이더 페이지 (출처: https://developers.figma.com/docs/figma-mcp-server/generative-plugins-and-shaders/, 캡처일 2026-10-30)](https://designrefs.com/articles/img/figma-shader-plugin-version-restore-shot2.webp)
## 크레딧은 어디서 나가나

에이전트에게 효과를 고쳐 달라고 하면 고칠 때마다 크레딧이 들 수 있다. 10월 6일 릴리스 노트에는 피그마 에이전트가 정식 출시되며 그날부터 AI 크레딧을 쓴다고 적혀 있다. 9월 1일 블로그는 베타 기간에는 무료이고 "몇 주 뒤"부터 크레딧을 쓴다고 했다. 이 둘을 합치면 지금은 크레딧이 드는 쪽으로 보인다.

그런데 셰이더 한 번 수정에 몇 크레딧이 드는지는 내가 연 자료에 없었다. 버전을 복원하는 동작에 크레딧이 드는지도 나오지 않는다. 크레딧이 어떤 순서로 빠지는지는 [피그마 에이전트 크레딧](https://designrefs.com/articles/figma-agent-ai-credits-ga/)에서 정리했다.

## 아직 모르는 것

- **버전 목록을 여는 위치.** 릴리스 노트에 화면 설명이 없다.
- **보존되는 버전의 수와 기간.** 몇 개까지, 얼마 동안 남는지 적혀 있지 않다.
- **복원하면 무엇이 되는가.** 그 버전으로 덮어쓰는지, 새 버전으로 복사되는지는 확인하지 못했다.
- **이미 만든 것도 해당되나.** 적용 이후에 고친 것부터 기록되는지, 예전 수정도 남아 있는지 알 수 없다.
- **외부 에이전트가 MCP로 고친 것도 버전에 남나.** 개발자 문서와 릴리스 노트가 서로를 가리키지 않는다.
- **적용 시점.** "이번 주 순차 적용"이라서 내 계정에서 보이는지는 확인하지 못했다.

## 그래서 지금은

**고치기 전에 지금 상태를 한 번 이름 붙여 둔다.** 변경 기록은 에이전트가 쓴다. 클라이언트가 "이 느낌"이라고 한 버전이라면, 수정 요청 전에 파일 안에 "시안A 승인" 같은 메모나 복제본을 따로 남겨 둔다. 기능이 아직 내 계정에 없을 수도 있다.

**수정은 한 번에 한 가지씩 시킨다.** 색, 번짐 정도, 움직임을 한 문장에 몰아 넣으면 버전 설명도 뭉뚱그려진다. 나눠서 시키면 버전 하나가 변화 하나에 대응하고, 돌아갈 지점도 선명해진다. 크레딧을 아끼려면 반대로 모아 보내는 편이 낫다. 두 방법이 충돌하니 작업 크기에 따라 고르면 된다.

**복원한 뒤 결과를 눈으로 비교한다.** 복원이 정확히 무엇을 되돌리는지 아직 모른다. 복원한 직후 캔버스에서 효과를 켜 보고, 클라이언트에게 보낸 이미지와 나란히 놓고 본다. 코드 레이어로 눌리는 시안을 만드는 쪽은 [피그마 코드 레이어 오픈 베타](https://designrefs.com/articles/figma-code-layers-open-beta/)에서, 다른 작업의 크레딧 감각은 [메이크의 모델 선택기](https://designrefs.com/articles/figma-make-gemini-4-argon-model-picker/)에서 이어서 볼 수 있다.

※ 출처: [Figma Release Notes](https://www.figma.com/release-notes/), [Figma 포럼: Updates to generative plugins and shaders](https://forum.figma.com/product-updates-3/updates-to-generative-plugins-and-shaders-57397), [Figma 도움말: 셰이더·플러그인 목록](https://help.figma.com/hc/en-us/articles/41409034424215), [Figma MCP 서버 문서: Generative plugins and shaders](https://developers.figma.com/docs/figma-mcp-server/generative-plugins-and-shaders/), [Behind the build: Generative plugins and shaders at Figma](https://www.figma.com/blog/how-we-built-generative-plugins-and-shaders/)
