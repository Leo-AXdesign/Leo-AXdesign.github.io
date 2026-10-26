---
slug: macos-27-ai-off-switch
title: 맥에서 AI를 한 번에 끄는 스위치가 사라졌다, '끄는 버튼'도 디자인이다
desc: macOS 27에서 애플 인텔리전스를 통째로 끄던 스위치가 없어졌다. 사용자들은 외부 도구까지 만들어 AI를 지우고 있다. 무엇이 바뀌었는지, 디자이너의 맥에서는 무엇을 확인할지, AI 기능을 설계하는 사람에게 남는 질문을 정리했다.
date: 2026-10-11
order: 1
tag: AI 디자인
related: ai, ui-ux
---

이번 주 맥 사용자들 사이에서 조용히 퍼진 도구가 있다. 이름은 RemoveMacAI. 맥에 깔린 애플의 AI 기능을 끄고, 그 AI가 쓰는 모델 파일까지 지워 준다. 지우고 나면 12GB 넘는 저장 공간이 돌아온다는 후기가 여럿 올라왔다.

이런 도구가 나온 데는 이유가 있다. 올가을 나온 macOS 27에서, AI 기능 전체를 한 번에 끄던 스위치가 사라졌다.

애플은 스위치를 없앤 이유를 따로 설명하지 않았다. 이 도구도 macOS 27에서 직접 돌려 보지는 않았고, 맥 전문 매체들의 보도를 따라 정리했다.

## 무엇이 바뀌었나

![macOS 26에서는 스위치 하나로 AI 기능을 모두 껐고, macOS 27에서는 기능마다 따로 꺼야 한다. 보도를 바탕으로 그린 개념도.](https://designrefs.com/articles/img/macos27-ai-switch.svg)

macOS 26까지는 '애플 인텔리전스' 전체를 끄는 스위치가 있었다. 누르면 글쓰기 도구, 젠모지, 이미지 플레이그라운드 같은 기능이 다 꺼지고 모델 파일도 지워졌다.

macOS 27에서는 그 스위치가 없다. 기능을 하나씩 찾아 꺼야 하고, 보도에 따르면 끌 곳이 여러 설정 화면에 흩어져 열 개 남짓이다. 더 큰 차이는 꺼도 모델 파일이 그대로 남는다는 점이다. 애플이 밝힌 크기로는 M3 이상 맥에서 최대 14GB다.

RemoveMacAI는 그 빈자리를 채운다. 애플이 기업용으로 마련해 둔 설정 방식(구성 프로파일)을 써서 기능을 끄고, 모델을 지우고, 다시 내려받지 못하게 막는다. 시스템 파일을 직접 건드리지 않고 되돌릴 수 있다고 개발자는 설명한다. 다만 애플이 공식으로 권하는 방법은 아니다.

## 디자이너의 맥에서 확인할 것

디자이너가 이 소식을 그냥 넘기기 어려운 이유가 두 가지 있다.

**저장 공간.** 디자이너의 맥은 늘 공간이 모자란다. PSD 몇 개, 영상 소스 몇 개면 금방 찬다. 쓰지 않는 AI 모델이 14GB를 차지하고 있다면 신경 쓰이는 크기다.

**클라이언트 자료.** 글쓰기 도구는 선택한 글을 고쳐 주고, ChatGPT 연결은 내용을 바깥 서비스로 보낼 수 있다. 계약서나 출시 전 자료를 다루는 사람이라면, 어떤 기능이 켜져 있는지 한 번은 알고 있어야 한다.

| 확인할 것 | 어디서 | 왜 |
|---|---|---|
| 글쓰기 도구 | 시스템 설정 > Apple Intelligence & Siri | 고객사 문서에서 무심코 쓰지 않도록 |
| ChatGPT 연결 | 같은 곳 | 외부 서비스로 내용이 갈 수 있는 경로 |
| 이미지 플레이그라운드·젠모지 | 같은 곳 (화면 시간 설정도 확인) | 쓰지 않으면 끄기 |
| 모델이 쓰는 공간 | 시스템 설정 > 일반 > 저장 공간 | 꺼도 남는 모델 파일 크기 확인 |
※ 출처: [MacRumors](https://www.macrumors.com/2026/10/06/strip-apple-intelligence-from-macos-27/), [Digital Trends](https://www.digitaltrends.com/computing/macos-27-removed-the-apple-intelligence-off-switch-heres-how-to-get-rid-of-it-anyway/), [Futurism](https://futurism.com/artificial-intelligence/mac-users-nuking-every-trace-of-apple-ai). 메뉴 이름과 위치는 macOS 버전에 따라 다를 수 있다.

외부 도구로 모델까지 지우는 건 각자 판단할 일이다. 회사 맥이라면 IT 담당자와 먼저 이야기하는 게 좋다. 구성 프로파일은 회사 관리 설정과 부딪힐 수 있다.

## '끄는 버튼'도 디자인이다

이 이야기는 맥 설정에서 끝나지 않는다. 지금 많은 디자이너가 자기 서비스에 AI 기능을 넣는 일을 하고 있다. 그래서 같은 질문이 우리 앞에도 놓인다. 사용자가 이 기능을 끄고 싶을 때, 쉽게 끌 수 있나?

애플의 선택은 좋은 반면교사다.

- **켜는 건 한 번, 끄는 건 열 번.** 켤 때는 기본값으로 켜져 있고, 끌 때는 여러 화면을 돌아다녀야 한다. 사용자는 이걸 "끄지 말라는 뜻"으로 읽는다.
- **꺼도 남는 것.** 기능을 꺼도 파일이 남으면, 사용자는 정말 꺼진 건지 믿지 못한다. 그래서 외부 도구를 찾는다.
- **설명 없는 변경.** 있던 스위치가 이유 없이 사라지면, 사람들은 가장 나쁜 쪽으로 추측한다.

반대로 하면 된다. AI 기능을 설계한다면 끄는 곳을 한 군데에 모으고, 끄면 무엇이 꺼지고 무엇이 남는지 한 줄로 알려 주자. 기능을 바꿨다면 왜 바꿨는지 말하자. 사용자가 외부 도구를 찾기 시작했다면, 그건 설정 화면의 디자인이 실패했다는 신호다.

## 그래서 지금은

1. **내 맥부터 확인.** 위 표대로 켜져 있는 AI 기능과 모델이 쓰는 공간을 한 번 살펴보자. 쓰지 않는 건 끄면 된다.
2. **만드는 서비스에도 같은 질문.** 지금 작업 중인 AI 기능에 '끄기'가 어디 있는지, 몇 번 눌러야 하는지 세어 보자. 세 번이 넘으면 다시 볼 일이다.
3. **바꿀 때는 이유와 함께.** 설정을 바꾸거나 없앨 일이 있다면, 업데이트 노트 한 줄이라도 이유를 적자.

AI가 화면을 직접 그리는 시대에 규칙을 누가 정하는지는 [AI가 화면을 직접 그리기 시작한 주](https://designrefs.com/articles/chatgpt-intelligent-ui-figma-agent/)에, UI 레퍼런스는 [UI/UX 레퍼런스](https://designrefs.com/ui-ux/)에 모아 두었다.

※ 출처: [Futurism](https://futurism.com/artificial-intelligence/mac-users-nuking-every-trace-of-apple-ai), [MacRumors](https://www.macrumors.com/2026/10/06/strip-apple-intelligence-from-macos-27/), [MacRumors (저장 공간)](https://www.macrumors.com/2026/10/05/apple-intelligence-removal-tool-frees-mac-storage/), [Digital Trends](https://www.digitaltrends.com/computing/macos-27-removed-the-apple-intelligence-off-switch-heres-how-to-get-rid-of-it-anyway/), [Daring Fireball](https://daringfireball.net/linked/2026/10/06/cli-tool-removes-apple-intelligence-from-macos-27).
