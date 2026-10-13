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
- Claude API 사용료는 Claude 구독과 따로 청구됩니다. 모드에 따라 글 검토 약 5~250원, SNS 다듬기 약 1~50원.
- 요금 없이 하려면 Claude 데스크톱에서 designhub 의 review_article / polish_post 를 쓰세요(구독 안에서 처리).
"""
import datetime, json, os, pathlib, re

TOOLS = pathlib.Path(__file__).resolve().parent
ROOT = TOOLS.parent
KO_DIR = ROOT / "content" / "articles"
KEY_FILE = pathlib.Path.home() / ".config" / "designhub" / "anthropic-key"
# 작업마다 고를 수 있는 모델. 기본값: SNS 다듬기는 절약(Haiku), 글 검토는 기본(Sonnet)
MODES = {
    "haiku": {"model": "claude-haiku-5-5", "label": "절약 · Haiku 5.5"},
    "sonnet": {"model": "claude-sonnet-5-5", "label": "기본 · Sonnet 5.5"},
    "opus": {"model": "claude-opus-5-5", "label": "정밀 · Opus 5.5"},
}
DEFAULT = {"article": "sonnet", "post": "haiku"}
MODEL = MODES[DEFAULT["article"]]["model"]
GUIDE = TOOLS / "editor-guide.md"


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
    if not key and not (os.environ.get("ANTHROPIC_API_KEY") or os.environ.get("ANTHROPIC_AUTH_TOKEN")):
        raise CoachError("API 키가 없어서 여기서는 바로 할 수 없어요. "
                         "'데스크톱에 보낼 문장 복사'를 눌러 Claude 데스크톱에 붙여 넣으면 무료로 할 수 있습니다. "
                         "(여기서 바로 하려면 AI 편집장 탭에 API 키를 넣어 주세요.)")
    # 화면에서 넣은 키가 있으면 그걸, 없으면 환경 변수를 씁니다
    return anthropic.Anthropic(api_key=key) if key else anthropic.Anthropic()


def call(system, user, *, mode="sonnet", web=0, effort="medium"):
    """Claude 를 한 번 부르고, 웹 검색이 길어져 멈추면(pause_turn) 이어서 끝까지 받습니다.
    web: 웹 검색 최대 횟수 (0 이면 검색 안 함). 검색 1회에 약 14원이 더 듭니다."""
    import anthropic
    c = client()
    model = MODES.get(mode, MODES["sonnet"])["model"]
    # Haiku 는 기본 웹 검색 도구를, Sonnet·Opus 는 결과를 걸러 읽는 새 도구를 씁니다
    search = "web_search_20250305" if mode == "haiku" else "web_search_20260209"
    tools = [{"type": search, "name": "web_search", "max_uses": web}] if web else []
    messages = [{"role": "user", "content": user}]
    try:
        for _ in range(5):
            kwargs = dict(model=model, max_tokens=16000, system=system, messages=messages,
                          output_config={"effort": effort})
            if mode != "haiku":
                # 안전 분류기가 거절하면 서버가 알맞은 다른 모델로 다시 시도합니다 (Haiku 는 지원 안 함)
                kwargs.update(betas=["server-side-fallback-2026-07-01"], fallbacks="default")
            if tools:
                kwargs["tools"] = tools
            try:
                r = c.beta.messages.create(**kwargs)
            except TypeError:
                # 맥 기본 파이썬(3.9)에는 예전 SDK 가 깔려 새 인자를 모를 수 있어, 같은 요청을 본문에 직접 실어 보냅니다
                extra = {"output_config": kwargs.pop("output_config")}
                headers = {}
                if kwargs.pop("betas", None):
                    extra["fallbacks"] = kwargs.pop("fallbacks")
                    headers["anthropic-beta"] = "server-side-fallback-2026-07-01"
                r = c.messages.create(**kwargs, extra_headers=headers, extra_body=extra)
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

def guide():
    return GUIDE.read_text(encoding="utf-8")


ARTICLE_FORMAT = """마지막에 아래 형식의 JSON 을 ```json 블록 하나로만 낸다.
before 는 바꾸거나 지울 원문(글자 그대로), anchor 는 새 문단을 넣을 자리 바로 앞 문장(글자 그대로).
본문 수정이 아닌 제안은 둘 다 비운다. 삭제면 after 를 비운다.
{
  "summary": "한두 문장 총평",
  "suggestions": [
    {"type": "업데이트", "priority": "높음|보통|낮음", "title": "짧은 제목", "reason": "왜 필요한지, 근거",
     "before": "", "anchor": "", "after": "", "sources": ["https://..."]}
  ],
  "sns": {"thread": "이 글을 소개하는 스레드 글", "hook": "인스타 캡션 첫 줄 후보"}
}"""


def article_system():
    return "너는 디자인 허브의 편집장이다. 이미 발행된 글을 다시 읽고, 독자에게 더 정확하고 쓸모 있게 만들 제안을 한다.\n\n" + guide() + "\n\n" + ARTICLE_FORMAT


def post_system():
    return ("너는 디자인 허브의 SNS 편집자다.\n\n" + guide() + "\n\n주어진 글을 다듬고, 마지막에 ```json 블록 하나로만 답한다:\n"
            '{"summary": "한 문장 총평", "points": ["고친 점 1", "고친 점 2"], "revised": "다듬은 전체 글"}')


def read_article(slug):
    path = KO_DIR / f"{slug}.md"
    if not re.fullmatch(r"[a-z0-9-]+", slug or "") or not path.exists():
        raise CoachError("없는 글입니다.")
    return path, path.read_text(encoding="utf-8")


def review_article(slug, mode=None, web=3):
    mode = mode or DEFAULT["article"]
    _, md = read_article(slug)
    today = datetime.date.today().isoformat()
    user = (f"오늘은 {today} 이다. 아래 글을 검토해 줘.\n\n"
            f"<article slug=\"{slug}\" url=\"https://designrefs.com/articles/{slug}/\">\n{md}\n</article>")
    text, sources, usage = call(article_system(), user, mode=mode, web=web, effort="medium")
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

def review_post(kind, text, mode=None):
    mode = mode or DEFAULT["post"]
    if not text.strip():
        raise CoachError("다듬을 글이 비어 있어요.")
    name = {"thread": "스레드 글", "caption": "인스타 캡션"}.get(kind, "글")
    out, _, _ = call(post_system(), f"아래 {name}을 다듬어 줘.\n\n<post>\n{text}\n</post>", mode=mode, effort="low")
    data = parse_json(out)
    limit = 500 if kind == "thread" else 2200
    if len(data.get("revised", "")) > limit:
        data["points"] = data.get("points", []) + [f"주의: 다듬은 글이 {limit}자를 넘습니다. 조금 줄여 주세요."]
    return data


# ---------- 원하는 대로 고치기 (사용자가 편집점을 직접 요청) ----------

EDIT_FORMAT = """사용자의 요청대로만 고친다. 요청하지 않은 곳은 건드리지 않는다.
마지막에 아래 형식의 JSON 을 ```json 블록 하나로만 낸다. before 는 바꿀 원문(글자 그대로), anchor 는 새 문단을 넣을 자리 바로 앞 문장(글자 그대로).
{"summary": "무엇을 어떻게 고쳤는지 한두 문장",
 "edits": [{"title": "짧은 제목", "before": "", "anchor": "", "after": ""}]}"""


def edit_article(slug, request, mode=None):
    """읽을거리 글을 사용자가 요청한 대로 고칠 수정안을 받습니다. [적용]은 apply() 로."""
    if not (request or "").strip():
        raise CoachError("어떻게 고칠지 적어 주세요.")
    mode = mode or DEFAULT["article"]
    _, md = read_article(slug)
    system = "너는 디자인 허브의 편집자다. 사용자가 원하는 편집을 글에 정확히 반영한다.\n\n" + guide() + "\n\n" + EDIT_FORMAT
    user = f"<request>\n{request}\n</request>\n\n<article slug=\"{slug}\">\n{md}\n</article>"
    text, _, _ = call(system, user, mode=mode, effort="medium")
    data = parse_json(text)
    sugs = []
    for i, e in enumerate(data.get("edits", [])):
        e.update(id=i, type="요청", priority="", reason="", sources=[])
        e["applicable"] = bool((e.get("before") and e["before"] in md) or (e.get("anchor") and e["anchor"] in md and e.get("after")))
        sugs.append(e)
    return {"summary": data.get("summary", ""), "suggestions": sugs, "searched": []}


def edit_post(kind, text, request, mode=None):
    """캡션·스레드 글을 사용자가 요청한 대로 고친 수정본을 받습니다."""
    if not text.strip() or not (request or "").strip():
        raise CoachError("고칠 글과 요청을 모두 적어 주세요.")
    mode = mode or DEFAULT["post"]
    name = {"thread": "스레드 글", "caption": "인스타 캡션"}.get(kind, "글")
    system = ("너는 디자인 허브의 SNS 편집자다. 사용자가 원하는 편집을 정확히 반영하고, 요청하지 않은 곳은 그대로 둔다.\n\n"
              + guide() + "\n\n스레드 글에 '---' 한 줄이 있으면 첫 글과 댓글을 나누는 표시다. 표시를 지키고, 나뉜 글 하나하나가 500자를 넘지 않게 한다.\n"
              "\n마지막에 ```json 블록 하나로만 답한다:\n"
              '{"summary": "무엇을 고쳤는지 한 문장", "points": ["고친 점"], "revised": "고친 전체 글"}')
    out, _, _ = call(system, f"<request>\n{request}\n</request>\n\n<{name}>\n{text}\n</{name}>", mode=mode, effort="low")
    data = parse_json(out)
    limit = 500 if kind == "thread" else 2200
    parts = [x for x in data.get("revised", "").split("\n---\n")] if kind == "thread" else [data.get("revised", "")]
    if any(len(x.strip()) > limit for x in parts):
        data["points"] = data.get("points", []) + [f"주의: 고친 글이 {limit}자를 넘습니다."]
    return data
