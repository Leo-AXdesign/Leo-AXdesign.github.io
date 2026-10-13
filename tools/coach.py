#!/usr/bin/env python3
"""
AI 편집장 — 발행된 읽을거리와 SNS 글을 Claude 에게 검토받습니다. (스튜디오가 씁니다)

- review_article(slug): 글을 읽고, 발행 뒤 바뀐 소식을 웹에서 찾아 보고,
  사실 확인·업데이트·추가·다듬기 제안을 돌려줍니다. 제안마다 본문의 어느 문장을 바꿀지(before)
  또는 어느 문장 뒤에 넣을지(anchor)를 함께 받아서, 스튜디오에서 [적용]을 누르면 바로 고칠 수 있습니다.
- review_post(kind, text): 인스타 캡션이나 스레드 글을 발행 전에 다듬어 줍니다.
- apply(slug, suggestion): 제안 하나를 content/articles/<slug>.md 에 반영하고 updated 날짜를 고칩니다.

API 키
- ANTHROPIC_API_KEY 환경 변수, `ant auth login` 프로필, 또는 스튜디오 화면에서 넣은 키
  (~/.config/designhub/anthropic-key, 나만 읽을 수 있는 권한)를 씁니다.
- Claude API 사용료는 Claude 구독과 따로 청구됩니다. 글 한 편 검토에 보통 수십~수백 원 정도입니다.
"""
import datetime, json, os, pathlib, re

TOOLS = pathlib.Path(__file__).resolve().parent
ROOT = TOOLS.parent
KO_DIR = ROOT / "content" / "articles"
KEY_FILE = pathlib.Path.home() / ".config" / "designhub" / "anthropic-key"
MODEL = "claude-opus-5-5"


class CoachError(Exception):
    """화면에 그대로 보여 줄 오류"""


# ---------- 키와 클라이언트 ----------

def saved_key():
    try:
        return KEY_FILE.read_text().strip() or None
    except OSError:
        return None


def save_key(key):
    KEY_FILE.parent.mkdir(parents=True, exist_ok=True)
    KEY_FILE.write_text(key.strip())
    KEY_FILE.chmod(0o600)


def forget_key():
    KEY_FILE.unlink(missing_ok=True)


def ready():
    """쓸 수 있는 상태인지: (SDK 설치 여부, 키 출처)"""
    try:
        import anthropic  # noqa: F401
    except ImportError:
        return False, None
    if saved_key():
        return True, "saved"
    if os.environ.get("ANTHROPIC_API_KEY") or os.environ.get("ANTHROPIC_AUTH_TOKEN"):
        return True, "env"
    return True, None


def client():
    try:
        import anthropic
    except ImportError:
        raise CoachError("AI 편집장을 쓰려면 먼저 설치가 필요합니다. 터미널에서: python3 -m pip install --user anthropic")
    key = saved_key()
    # 화면에서 넣은 키가 있으면 그걸, 없으면 환경 변수나 `ant auth login` 프로필을 씁니다
    return anthropic.Anthropic(api_key=key) if key else anthropic.Anthropic()


def call(system, user, *, web=False, effort="high"):
    """Claude 를 한 번 부르고, 웹 검색이 길어져 멈추면(pause_turn) 이어서 끝까지 받습니다."""
    import anthropic
    c = client()
    tools = [{"type": "web_search_20260209", "name": "web_search", "max_uses": 5}] if web else []
    messages = [{"role": "user", "content": user}]
    try:
        for _ in range(5):
            kwargs = dict(model=MODEL, max_tokens=16000, system=system, messages=messages,
                          output_config={"effort": effort},
                          # 안전 분류기가 거절하면 서버가 알맞은 다른 모델로 다시 시도합니다
                          betas=["server-side-fallback-2026-07-01"], fallbacks="default")
            if tools:
                kwargs["tools"] = tools
            try:
                r = c.beta.messages.create(**kwargs)
            except TypeError:
                # 맥 기본 파이썬(3.9)에는 예전 SDK 가 깔려 새 인자를 모를 수 있어, 같은 요청을 본문에 직접 실어 보냅니다
                extra = {"fallbacks": kwargs.pop("fallbacks"), "output_config": kwargs.pop("output_config")}
                kwargs.pop("betas")
                r = c.messages.create(**kwargs, extra_headers={"anthropic-beta": "server-side-fallback-2026-07-01"},
                                      extra_body=extra)
            if r.stop_reason == "pause_turn":
                messages = [{"role": "user", "content": user}, {"role": "assistant", "content": r.content}]
                continue
            break
    except anthropic.AuthenticationError:
        raise CoachError("API 키가 맞지 않습니다. 스튜디오의 'AI 편집장 키'를 다시 넣어 주세요.")
    except anthropic.RateLimitError:
        raise CoachError("요청이 많아 잠시 막혔습니다. 1분쯤 뒤에 다시 눌러 주세요.")
    except anthropic.APIStatusError as err:
        raise CoachError(f"Claude API 오류 ({err.status_code}): {err.message}")
    except anthropic.APIConnectionError:
        raise CoachError("Claude 에 연결하지 못했습니다. 인터넷 연결을 확인해 주세요.")
    if r.stop_reason == "refusal":
        raise CoachError("Claude 가 이 요청을 처리하지 않았습니다. 글 내용을 확인한 뒤 다시 시도해 주세요.")
    text = "\n".join(b.text for b in r.content if b.type == "text")
    sources = []
    for b in r.content:
        if b.type == "web_search_tool_result" and isinstance(b.content, list):
            sources += [{"title": x.title, "url": x.url} for x in b.content if getattr(x, "url", None)]
    return text, sources, r.usage


def parse_json(text):
    """답 끝의 ```json 블록(없으면 마지막 { ... })을 읽습니다."""
    m = re.findall(r"```json\s*(\{.*?\})\s*```", text, re.S)
    raw = m[-1] if m else text[text.find("{"): text.rfind("}") + 1]
    try:
        return json.loads(raw)
    except ValueError:
        raise CoachError("AI 답을 읽지 못했습니다. 한 번 더 눌러 주세요.\n\n" + text[:1500])


# ---------- 글 검토 ----------

STYLE = """디자인 허브(designrefs.com)는 디자이너를 위한 레퍼런스 사이트이고, '읽을거리'는 AI와 디자인 소식을 쉽게 풀어 쓴 글이다.
글의 원칙:
- 담담한 평서체(~다). 과장하지 않는다. 디자이너가 실무에서 바로 쓸 수 있는 내용 위주.
- '먼저 밝혀 둘 것'에서 한계를 솔직히 적는다. 확인하지 못한 숫자와 주장은 쓰지 않는다.
- 표 바로 아래 '※ 출처:' 줄, 글 끝에 출처 목록. 숫자에는 출처가 있어야 한다.
- '## 그래서 지금은'에 실천 팁 3개."""

ARTICLE_SYSTEM = f"""너는 디자인 허브의 편집장이다. 이미 발행된 글을 다시 읽고, 독자에게 더 정확하고 쓸모 있게 만들 제안을 한다.
{STYLE}

할 일:
1. 글의 주장·숫자·날짜·가격·제품 이름을 확인한다. 필요하면 웹 검색으로 발행일 이후 바뀐 소식(가격 변경, 정식 출시, 정정 보도 등)을 찾는다.
2. 제안은 많아도 6개. 확신이 있는 것만. 사소한 맞춤법 지적은 하지 않는다.
3. 각 제안의 종류: 사실 확인 / 업데이트 / 추가 / 다듬기 / 삭제
4. 본문을 고칠 때는 아래 둘 중 하나를 반드시 채운다:
   - before: 바꾸거나 지울 본문 문장을 '글자 하나 틀리지 않게' 그대로 복사 (after 로 바뀜, 삭제면 after 는 빈 문자열)
   - anchor: 새 문단을 넣을 자리 바로 앞 문장을 그대로 복사 (그 문단 뒤에 after 가 들어감)
   본문 수정이 아닌 제안(예: 새 글 아이디어)은 둘 다 비운다.
5. after 는 글의 말투(담담한 평서체)를 그대로 따른다. 새 사실을 넣을 때는 출처 링크를 문장 안에 마크다운으로 단다.
6. 오늘 날짜를 기준으로 판단한다.

마지막에 아래 형식의 JSON 을 ```json 블록 하나로만 낸다:
{{
  "summary": "한두 문장 총평",
  "suggestions": [
    {{"type": "업데이트", "priority": "높음|보통|낮음", "title": "짧은 제목", "reason": "왜 필요한지, 근거",
      "before": "", "anchor": "", "after": "", "sources": ["https://..."]}}
  ],
  "sns": {{"thread": "이 글을 소개하는 스레드 글 (500자 이내, 담담한 평서체, 링크 제외)", "hook": "인스타 캡션 첫 줄 후보"}}
}}"""


def read_article(slug):
    path = KO_DIR / f"{slug}.md"
    if not re.fullmatch(r"[a-z0-9-]+", slug or "") or not path.exists():
        raise CoachError("없는 글입니다.")
    return path, path.read_text(encoding="utf-8")


def review_article(slug):
    _, md = read_article(slug)
    today = datetime.date.today().isoformat()
    user = (f"오늘은 {today} 이다. 아래 글을 검토해 줘.\n\n"
            f"<article slug=\"{slug}\" url=\"https://designrefs.com/articles/{slug}/\">\n{md}\n</article>")
    text, sources, usage = call(ARTICLE_SYSTEM, user, web=True, effort="high")
    data = parse_json(text)
    # 제안마다 지금 본문에 그대로 적용할 수 있는지 미리 확인해 둡니다
    for i, s in enumerate(data.get("suggestions", [])):
        s["id"] = i
        s["applicable"] = bool((s.get("before") and s["before"] in md) or (s.get("anchor") and s["anchor"] in md and s.get("after")))
    data["searched"] = sources[:12]
    data["usage"] = {"input": usage.input_tokens, "output": usage.output_tokens}
    return data


def apply(slug, s):
    """제안 하나를 본문에 반영합니다. 실패하면 이유를 알려 줍니다."""
    path, md = read_article(slug)
    before, anchor, after = s.get("before", ""), s.get("anchor", ""), s.get("after", "")
    if before:
        if before not in md:
            raise CoachError("본문에서 바꿀 문장을 찾지 못했습니다. 이미 고쳤거나 글이 바뀌었을 수 있어요.")
        md = md.replace(before, after, 1)
    elif anchor and after:
        i = md.find(anchor)
        if i < 0:
            raise CoachError("새 문단을 넣을 자리를 찾지 못했습니다.")
        end = md.find("\n\n", i)
        end = len(md) if end < 0 else end
        md = md[:end] + "\n\n" + after.strip() + md[end:]
    else:
        raise CoachError("이 제안은 본문을 바로 고치는 종류가 아닙니다.")
    md = touch_updated(md)
    path.write_text(md, encoding="utf-8")
    return {"ok": True}


def touch_updated(md):
    """frontmatter 의 updated 를 오늘로 (없으면 date 아래에 추가)"""
    today = datetime.date.today().isoformat()
    head_end = md.find("\n---", 4)
    head, body = md[:head_end], md[head_end:]
    if re.search(r"^updated:", head, re.M):
        head = re.sub(r"^updated:.*$", f"updated: {today}", head, flags=re.M)
    else:
        head = re.sub(r"^(date:.*)$", rf"\1\nupdated: {today}", head, count=1, flags=re.M)
    return head + body


# ---------- SNS 글 다듬기 ----------

POST_SYSTEM = f"""너는 디자인 허브의 SNS 편집자다.
{STYLE}
채널별 원칙:
- 인스타 캡션: 첫 줄에 저장할 이유. 장마다 한 줄 요약. 해시태그 5개 이내. 2,200자 이내.
- 스레드: 경험 → 생각 → 한 줄 정리. 담담한 평서체, 홍보 문구 없이. 500자 이내. 해시태그 없음.
- [ ] 로 비워 둔 자리는 사용자가 실제 경험을 넣을 곳이다. 지어내서 채우지 말고 그대로 남긴다.

주어진 글을 다듬고, 마지막에 ```json 블록 하나로만 답한다:
{{"summary": "한 문장 총평", "points": ["고친 점 1", "고친 점 2"], "revised": "다듬은 전체 글"}}"""


def review_post(kind, text):
    if not text.strip():
        raise CoachError("다듬을 글이 비어 있어요.")
    name = {"thread": "스레드 글", "caption": "인스타 캡션"}.get(kind, "글")
    out, _, _ = call(POST_SYSTEM, f"아래 {name}을 다듬어 줘.\n\n<post>\n{text}\n</post>", effort="medium")
    data = parse_json(out)
    limit = 500 if kind == "thread" else 2200
    if len(data.get("revised", "")) > limit:
        data["points"] = data.get("points", []) + [f"주의: 다듬은 글이 {limit}자를 넘습니다. 조금 줄여 주세요."]
    return data
