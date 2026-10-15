"""Claude로 글 + 캡처 계획(JSON)을 생성.

writer: cli (기본) → 설치된 Claude Code(`claude -p`)로 작성. 구독 사용량 안에서 처리, API 키 불필요.
writer: api        → Anthropic API로 작성. .env 의 ANTHROPIC_API_KEY 필요(유료).
"""
import json
import os
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

FORMAT_RULES = """
아래 JSON 하나만 출력하세요. 앞뒤 설명이나 ``` 없이 JSON만.

{
  "title": "글 제목",
  "slug": "영문-소문자-하이픈",
  "labels": ["챗GPT", "AI 기초"],
  "summary": "검색 설명용 1~2문장",
  "body_html": "<p>...</p><h2>...</h2> ... {{media:s1}} ...",
  "media": [
    {
      "id": "s1",
      "kind": "screenshot",
      "url": "https://claude.ai",
      "needs_login": false,
      "actions": [
        {"do": "wait", "ms": 1500},
        {"do": "click", "text": "버튼에 보이는 글자"},
        {"do": "scroll", "y": 600},
        {"do": "type", "selector": "textarea", "value": "입력할 문장"}
      ],
      "full_page": false,
      "caption": "이미지 아래 설명 (한 줄)",
      "mockup_html": "<div style=\\"...\\">이 화면을 흉내 낸 HTML</div>"
    }
  ]
}

항목 설명:
- slug: 파일명용. kind: screenshot 또는 video. url: 공식 공개 페이지만.
- needs_login: 로그인해야 보이는 화면이면 true. actions: 선택, 최소한으로.
- mockup_html: 실제 캡처가 봇 확인 등으로 막힐 때 대신 찍을 '재현 화면'. 모든 media에 필수.
  · 1280x800 화면을 채우는 HTML 조각. 스타일은 style 속성이나 <style> 하나로만. 스크립트·외부 이미지·외부 글꼴 금지.
  · 그 서비스의 화면 배치(입력창, 사이드바, 버튼 위치)를 단순하게 흉내 내고, 이 글의 예시 프롬프트와 짧은 예시 답변을 실제 글자로 넣는다.
  · 로고 이미지는 그리지 말고 서비스 이름을 글자로만 쓴다. 개인정보처럼 보이는 이름·이메일은 넣지 않는다.
- JSON 안에 주석(//)을 쓰지 않는다. body_html 속 큰따옴표는 \" 로 이스케이프한다.

규칙:
- body_html: h2, p, ul/ol/li, blockquote, b, a 태그만. h1 금지(제목은 따로 들어감).
- 이미지/영상이 들어갈 자리에 {{media:ID}} 를 단독 줄로 넣고, media 목록과 ID를 맞춘다.
- media는 2~6개. 따라하는 동작(클릭 순서 등)을 보여줄 때만 kind=video, 나머지는 screenshot.
- 확실히 존재하는 공식 URL만 쓴다. 회원가입 완료, 로그인 제출, 결제, 메시지 전송 버튼 클릭은 절대 계획하지 않는다.
- 이전 글 목록이 주어지면 관련 글 1~2개를 <a href>로 자연스럽게 연결한다.
- 화면 구성이나 요금·한도처럼 바뀔 수 있는 정보는 단정하지 말고, 확실하지 않은 숫자는 쓰지 않는다.
- 실제로 하지 않은 일을 한 것처럼 쓰지 않는다. "직접 비교해 봤더니", "제가 써보니 ○○가 더 좋았어요",
  "실험 결과"처럼 실제 사용·테스트·측정을 했다고 읽히는 문장과, 특정 AI의 실제 답변을 지어낸 인용은 금지.
  비교·실험 주제는 '독자가 직접 해보는 방법'으로 쓰고, 서비스별 특징은 공식 발표나 웹 검색으로 확인한 내용만 출처와 함께 쓴다.
  공감·경험담은 "처음엔 다들 헷갈려해요"처럼 일반적인 이야기로만 쓴다.
- 재현 화면(mockup_html) 속 AI 답변은 '예시'임이 캡션에서 드러나게 한다.
"""


def _extract_json(text: str) -> dict:
    text = re.sub(r"```(?:json)?", "", text).strip()
    start, end = text.find("{"), text.rfind("}")
    if start == -1 or end == -1:
        raise ValueError("응답에서 JSON을 찾지 못했습니다:\n" + text[:500])
    # // 주석이 섞여 나오는 경우 제거 (URL의 // 는 유지)
    raw = re.sub(r'(?<!:)//[^\n"]*\n', "\n", text[start:end + 1])
    return json.loads(raw, strict=False)  # 문자열 속 줄바꿈 허용


def _claude_bin() -> str:
    # cron 은 PATH 가 짧아서 기본 설치 위치도 직접 확인
    for c in (shutil.which("claude"), Path.home() / ".local/bin/claude"):
        if c and Path(c).exists():
            return str(c)
    raise RuntimeError("claude 명령을 찾지 못했습니다. (curl -fsSL https://claude.ai/install.sh | bash)")


def _write_with_cli(system: str, user_msg: str, cfg: dict) -> str:
    tools = "WebSearch,WebFetch" if cfg.get("use_web_search", True) else ""
    cmd = [_claude_bin(), "-p", "--output-format", "json",
           "--system-prompt", system, "--tools", tools,
           "--allowedTools", tools,  # 도구를 켜는 것과 별개로 '사용 허락'도 줘야 실제로 검색함
           "--strict-mcp-config", "--setting-sources", ""]
    if cfg.get("model"):
        cmd += ["--model", cfg["model"]]
    env = {k: v for k, v in os.environ.items() if k != "ANTHROPIC_API_KEY"}  # 구독 로그인으로 쓰도록
    with tempfile.TemporaryDirectory() as tmp:  # 프로젝트 파일·설정 영향 없이 빈 폴더에서 실행
        r = subprocess.run(cmd, input=user_msg, capture_output=True, text=True,
                           cwd=tmp, env=env, timeout=1800)  # 웹검색이 길면 20분 가까이 걸리기도 함
    try:
        out = json.loads(r.stdout)
    except json.JSONDecodeError:
        raise RuntimeError(f"claude 실행 실패 (code {r.returncode}): {(r.stderr or r.stdout)[:500]}")
    if out.get("is_error"):
        raise RuntimeError("claude 오류: " + str(out.get("result"))[:500]
                           + "\n로그인이 풀렸다면 터미널에서 claude 를 실행해 다시 로그인하세요.")
    return out.get("result", "")


def _write_with_api(system: str, user_msg: str, cfg: dict) -> str:
    import anthropic

    client = anthropic.Anthropic()
    kwargs = dict(
        model=cfg.get("model", "claude-sonnet-5-5"),
        max_tokens=16000,
        system=system,
        messages=[{"role": "user", "content": user_msg}],
    )
    if cfg.get("use_web_search", True):
        kwargs["tools"] = [{"type": "web_search_20260209", "name": "web_search", "max_uses": 5}]

    # 웹검색이 길어지면 pause_turn 으로 끊겨 오므로, 이어서 계속 생성
    blocks = []
    for _ in range(5):
        resp = client.messages.create(**kwargs)
        blocks += resp.content
        if resp.stop_reason != "pause_turn":
            break
        kwargs["messages"] = [kwargs["messages"][0], {"role": "assistant", "content": blocks}]
    if resp.stop_reason == "max_tokens":
        raise ValueError("글이 너무 길어 중간에 끊겼습니다. max_tokens를 늘리거나 분량을 줄이세요.")
    if resp.stop_reason == "refusal":
        raise ValueError("모델이 이 주제의 작성을 거절했습니다.")
    # 웹검색 인용이 붙으면 text 블록이 여러 조각으로 나뉘므로 그대로 이어 붙임
    return "".join(b.text for b in blocks if getattr(b, "type", "") == "text")


def generate_post(topic: dict, recent_posts: list, cfg: dict, style_path: Path) -> dict:
    style = style_path.read_text(encoding="utf-8")

    recent = "\n".join(f"- {p['title']} : {p['url']}" for p in recent_posts) or "(없음)"
    user_msg = (
        f"이번 글 주제: {topic['title']}\n"
        f"방향 메모: {topic.get('note', '')}\n\n"
        f"이 블로그의 이전 글 목록:\n{recent}\n\n"
        "필요하면 웹 검색으로 현재 화면 구성과 최신 정보를 확인한 뒤 작성하세요."
    )
    system = style + "\n\n" + FORMAT_RULES
    if cfg.get("writer", "cli") == "api":
        text = _write_with_api(system, user_msg, cfg)
    else:
        text = _write_with_cli(system, user_msg, cfg)
    post = _extract_json(text)

    for key in ("title", "body_html", "media"):
        if key not in post:
            raise ValueError(f"생성된 글에 '{key}' 항목이 없습니다.")
    post.setdefault("labels", [])
    post.setdefault("slug", "post")
    return post
