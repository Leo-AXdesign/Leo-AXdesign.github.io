"""AI 한입 자동 포스팅.

  python -m autopost.main --slot morning   # 9시: 큰 이슈 있으면 이슈 글, 없으면 주제 목록 다음 글 (매일 1개)
  python -m autopost.main --slot evening   # 18시: 오늘 안 다룬 큰 이슈가 있을 때만 1개 더
  python -m autopost.main                  # 슬롯 없이: 주제 목록 다음 글
  python -m autopost.main --dry-run        # 업로드/등록 없이 output/ 에 미리보기만
  python -m autopost.main --topic "주제"   # 직접 지정
  python -m autopost.main --draft          # 이번만 임시저장
"""
import argparse
import datetime as dt
import json
import sys
from pathlib import Path

import yaml
from dotenv import load_dotenv

from . import blogger, capture, indexing, media, render, scout, writer

ROOT = Path.cwd()
LOG = ROOT / "posted.jsonl"  # 올린 글 기록 (중복 이슈 방지·하루 개수 확인·색인 확인용)


def load_yaml(p):
    return yaml.safe_load((ROOT / p).read_text(encoding="utf-8"))


def next_topic(topics):
    for t in topics["topics"]:
        if t.get("status", "pending") == "pending":
            return t
    return None


def read_log() -> list:
    if not LOG.exists():
        return []
    return [json.loads(l) for l in LOG.read_text(encoding="utf-8").splitlines() if l.strip()]


def append_log(row: dict):
    with LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")


def pick_topic(args, cfg, topics, log, recent_titles):
    """반환: (topic, source, issue_key) 또는 (None, 이유, None)"""
    if args.topic:
        return {"title": args.topic, "note": args.note}, "manual", None

    today = str(dt.date.today())
    today_rows = [r for r in log if r["date"] == today and not r.get("draft")]
    done_keys = [r["key"] for r in log if r.get("key")]

    if args.slot == "evening" and len(today_rows) >= 2:
        return None, "오늘 이미 2개를 올렸어요", None
    if args.slot == "morning" and today_rows:
        return None, "오늘 아침 글은 이미 올라갔어요", None

    if args.slot in ("morning", "evening"):
        print("■ 오늘의 AI 이슈 살펴보는 중...")
        issue = scout.find_issue(recent_titles, done_keys, cfg)
        if issue:
            print(f"   큰 이슈 발견 → {issue['title']}")
            note = issue["note"] + "\n(오늘 나온 소식을 초보자 눈높이로 정리. 무엇이 바뀌었는지 → 써보는 법 → 주의점 순서)"
            return {"title": issue["title"], "note": note}, "issue", issue["key"]
        if args.slot == "evening":
            if today_rows:
                return None, "큰 이슈가 없어 저녁 글은 건너뜁니다 (오늘 1개)", None
            print("   오늘 아직 글이 없어서 주제 목록에서 1개 올립니다.")

    t = next_topic(topics)
    if t:
        return t, "queue", None
    print("■ 주제 목록이 비어서 새 주제를 정하는 중...")
    t = scout.new_topic(recent_titles, cfg)
    topics["topics"].append({**t, "status": "pending", "auto": True})
    return topics["topics"][-1], "queue", None


def check_index(cfg, log):
    """3일 전에 발행한 글의 색인 상태를 로그에 남김."""
    today = dt.date.today()
    rows = [r for r in log if r.get("url") and not r.get("draft")
            and (today - dt.date.fromisoformat(r["date"])).days == 3]
    for r in rows:
        try:
            print(f"   색인 상태 {r['title'][:30]}… : {indexing.inspect(cfg['blog_url'], r['url'])}")
        except Exception as e:
            print(f"   ! 색인 조회 실패: {str(e)[:150]}")
            return


def main():
    load_dotenv(ROOT / ".env")
    ap = argparse.ArgumentParser()
    ap.add_argument("--slot", choices=["morning", "evening"])
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--draft", action="store_true")
    ap.add_argument("--publish", action="store_true")  # 예전 옵션 호환
    ap.add_argument("--topic")
    ap.add_argument("--note", default="")
    args = ap.parse_args()

    cfg = load_yaml("config.yaml")
    topics = load_yaml("topics.yaml")
    log = read_log()

    svc = blog_id = None
    recent = []
    if not args.dry_run:
        svc = blogger.get_service()
        blog_id = blogger.get_blog_id(svc, cfg["blog_url"])
        recent = blogger.recent_posts(svc, blog_id)
    recent_titles = [p["title"] for p in recent] + [r["title"] for r in log[-30:]]

    topic, source, issue_key = pick_topic(args, cfg, topics, log, recent_titles)
    if not topic:
        print(f"■ {source}")
        if not args.dry_run:
            check_index(cfg, log)
        return 0
    print(f"■ 주제 ({source}): {topic['title']}")

    print("■ 글 작성 중...")
    post = writer.generate_post(topic, recent, cfg, ROOT / "style_guide.md")
    stamp = dt.datetime.now().strftime("%Y%m%d-%H%M")
    slug = f"{stamp}-{post['slug']}"[:80]
    out_dir = ROOT / "output" / slug
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"■ 캡처 {len(post['media'])}개...")
    files = capture.capture_all(post["media"], out_dir / "media", cfg)

    urls, unreachable = {}, []
    if args.dry_run:
        urls = {k: f"media/{v.name}" for k, v in files.items() if v}
    else:
        print("■ 미디어 업로드...")
        for mid, f in files.items():
            if not f:
                continue
            try:
                urls[mid] = media.upload(f, f"{dt.date.today():%Y/%m}/{slug}/{f.name}", cfg["github"])
            except Exception as e:
                print(f"   ! 업로드 실패 {mid}: {e}")
        unreachable = media.ensure_reachable(urls)
        if unreachable:
            print(f"   ! 열리지 않는 이미지 {len(unreachable)}개 → 임시저장으로 올립니다.")

    html, missing = render.render(post["body_html"], post["media"], urls)
    (out_dir / "post.html").write_text(
        f"<!doctype html><meta charset=utf-8><title>{post['title']}</title>"
        f"<body style='max-width:720px;margin:40px auto;font-family:sans-serif;line-height:1.8'>"
        f"<h1>{post['title']}</h1>{html}</body>", encoding="utf-8")
    (out_dir / "post.json").write_text(json.dumps(post, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"■ 미리보기: {out_dir / 'post.html'}")

    if args.dry_run:
        return 0

    draft = args.draft or (cfg.get("draft", False) and not args.publish)
    if missing:
        print(f"   ! 캡처 못 한 자리 {len(missing)}개 → 임시저장으로 올립니다.")
        draft = True
    if unreachable:
        draft = True
    res = blogger.create_post(svc, blog_id, post["title"], html, post["labels"], draft=draft)
    edit = f"https://www.blogger.com/blog/post/edit/{blog_id}/{res['id']}"
    print(f"■ Blogger 등록 완료 ({'임시저장' if draft else '발행'}): {res.get('url') or edit}")
    print(f"   편집: {edit}")

    append_log({"date": str(dt.date.today()), "time": dt.datetime.now().strftime("%H:%M"),
                "slot": args.slot, "source": source, "key": issue_key, "title": post["title"],
                "url": None if draft else res.get("url"), "id": res["id"], "draft": draft})

    if source == "queue":
        topic["status"] = "done"
        topic["posted"] = f"{dt.date.today()}"
        (ROOT / "topics.yaml").write_text(
            yaml.safe_dump(topics, allow_unicode=True, sort_keys=False), encoding="utf-8")

    if not draft:
        try:
            print(f"■ 구글 색인 요청: 사이트맵 제출 {indexing.submit_sitemap(cfg['blog_url'])}")
        except Exception as e:
            print(f"   ! 사이트맵 제출 실패 (Search Console 에 블로그가 등록돼 있는지 확인): {str(e)[:200]}")
        check_index(cfg, log)
    return 0


if __name__ == "__main__":
    sys.exit(main())
