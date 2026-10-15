"""오늘의 AI 이슈 탐색 + 주제 목록이 비었을 때 새 주제 정하기 (writer 와 같은 Claude 사용)."""
import datetime as dt

from .writer import _extract_json, _write_with_api, _write_with_cli

ISSUE_RULES = """
당신은 'AI 한입' 블로그(AI 초보자 대상, 하루 한입 AI 활용법)의 편집장입니다.
웹 검색으로 최근 24시간 안에 나온 AI 소식을 확인하고, 이 블로그 독자에게 '오늘 꼭 알려줄 만한 큰 이슈'가 있는지 판단하세요.

큰 이슈의 기준 (하나 이상 해당하고, 일반인이 직접 써보거나 영향을 받는 것):
- 챗GPT·제미나이·클로드 등 대중 서비스의 새 기능 출시, 무료 공개, 요금·한도 변경
- 많은 사람이 쓰는 앱(카카오톡, 네이버, 갤럭시, 아이폰 등)에 AI 기능이 새로 들어옴
- 개인정보·보안 사고처럼 사용자가 당장 조심해야 하는 일
큰 이슈가 아닌 것: 투자·주가·인사·연구 논문·개발자 전용 API·루머·단순 예고

이미 다룬 글과 같은 소식이면 큰 이슈가 아닙니다.
확실한 공식 발표나 신뢰할 만한 보도가 있는 것만 고르세요.

아래 JSON 하나만 출력하세요. 앞뒤 설명 없이.
{"big": true, "title": "블로그 글 제목 초안", "note": "무슨 일이 있었는지, 초보자가 써보는 법·주의점 등 글 방향 (출처 언론사·공식 발표 포함)", "key": "같은 소식 중복 방지용 영문 키 (예: chatgpt-voice-free-2026-10)"}
큰 이슈가 없으면: {"big": false, "reason": "한 줄 이유"}
"""

TOPIC_RULES = """
당신은 'AI 한입' 블로그(AI 초보자 대상, 하루 한입 AI 활용법)의 편집장입니다.
아래 이전 글 목록과 겹치지 않는, 초보자가 바로 따라 할 수 있는 실용 주제 하나를 정하세요.
(예: 특정 서비스의 특정 기능 사용법, 생활·업무 속 활용 예시, 주의할 점)
아래 JSON 하나만 출력하세요. 앞뒤 설명 없이.
{"title": "블로그 글 제목 초안", "note": "글 방향 메모"}
"""


def _ask(system: str, user_msg: str, cfg: dict) -> dict:
    run = _write_with_api if cfg.get("writer", "cli") == "api" else _write_with_cli
    return _extract_json(run(system, user_msg, cfg))


def find_issue(recent_titles: list, done_keys: list, cfg: dict):
    """큰 이슈가 있으면 {title, note, key}, 없으면 None."""
    user = (f"오늘 날짜: {dt.date.today()}\n\n이미 다룬 글:\n"
            + ("\n".join(f"- {t}" for t in recent_titles) or "(없음)")
            + "\n\n이미 다룬 이슈 키: " + (", ".join(done_keys) or "(없음)"))
    res = _ask(ISSUE_RULES, user, cfg)
    if not res.get("big") or not res.get("title"):
        print(f"   큰 이슈 없음: {res.get('reason', '')}")
        return None
    if res.get("key") in done_keys:
        print(f"   이미 다룬 이슈: {res['key']}")
        return None
    return {"title": res["title"], "note": res.get("note", ""), "key": res.get("key", "")}


def new_topic(recent_titles: list, cfg: dict) -> dict:
    user = "이전 글 목록:\n" + ("\n".join(f"- {t}" for t in recent_titles) or "(없음)")
    res = _ask(TOPIC_RULES, user, cfg)
    return {"title": res["title"], "note": res.get("note", "")}
