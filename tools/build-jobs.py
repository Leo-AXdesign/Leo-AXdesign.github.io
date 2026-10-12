#!/usr/bin/env python3
"""
이번 주 디자이너 채용 공고를 모아 /jobs/weekly/ 페이지를 만듭니다.

  python3 tools/build-jobs.py

GitHub Actions(.github/workflows/jobs-weekly.yml)가 매주 월요일 아침에 자동으로 돌립니다.

가져오는 곳 (모두 공고를 다른 곳에 싣도록 열어 둔 공식 통로만 씁니다)
- 사람인 오픈 API     : 국내 디자이너 공고. 환경 변수 SARAMIN_KEY 가 있을 때만
- Remotive 공개 API   : 해외 원격 디자인 공고 (출처 표기·원문 링크 필수)
- We Work Remotely RSS: 해외 원격 디자인 공고
- Remote OK 공개 API  : 해외 원격 디자인 공고 (출처 표기·원문 링크 필수)

원티드·잡코리아처럼 약관으로 자동 수집을 막은 곳은 쓰지 않습니다.
공고는 제목·회사·지역·날짜와 원문 링크만 싣고, 본문은 옮기지 않습니다.

- 한 곳이 실패해도 나머지로 만듭니다. 전부 실패하면 지난 페이지를 그대로 둡니다.
- 가져온 목록은 data/jobs/<연도>-W<주>.json 으로 남겨 둡니다.
"""
import datetime, email.utils, html, json, os, pathlib, re, sys, urllib.parse, urllib.request
import xml.etree.ElementTree as ET

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from shell import document, section_head, SITE, e   # noqa: E402
from nav import menu, footer_links                     # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "jobs" / "weekly"
DATA = ROOT / "data" / "jobs"
KST = datetime.timezone(datetime.timedelta(hours=9))
NOW = datetime.datetime.now(KST)
SINCE = NOW - datetime.timedelta(days=7)
UA = "DesignHubWeeklyJobs/1.0 (+https://designrefs.com/jobs/weekly/)"
PER_SOURCE = 40   # 한 곳에서 싣는 최대 개수

# 해외 공고 중 디자이너 직무만 남길 때 보는 낱말
DESIGN_WORDS = re.compile(r"design|designer|ux|ui\b|brand|visual|graphic|illustrat|motion|art director|creative",
                          re.I)


def get(url, headers=None, timeout=25):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "*/*", **(headers or {})})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def to_dt(v):
    """여러 형식의 날짜를 KST datetime 으로. 모르면 None."""
    if v in (None, ""):
        return None
    try:
        if isinstance(v, (int, float)) or (isinstance(v, str) and v.isdigit()):
            return datetime.datetime.fromtimestamp(int(v), KST)
        if isinstance(v, str) and re.match(r"\d{4}-\d{2}-\d{2}", v):
            d = datetime.datetime.fromisoformat(v.replace("Z", "+00:00"))
            return (d if d.tzinfo else d.replace(tzinfo=datetime.timezone.utc)).astimezone(KST)
        return email.utils.parsedate_to_datetime(v).astimezone(KST)
    except (ValueError, TypeError, OverflowError):
        return None


def job(source, title, company, url, posted, location="", deadline=None):
    return {"source": source, "title": " ".join(str(title or "").split()), "company": " ".join(str(company or "").split()),
            "url": url, "posted": posted.isoformat() if posted else "", "location": " ".join(str(location or "").split()),
            "deadline": deadline.date().isoformat() if deadline else ""}


# ---------- 가져오는 곳 ----------
def saramin():
    key = os.environ.get("SARAMIN_KEY", "").strip()
    if not key:
        return None   # 키가 없으면 건너뜀 (실패가 아님)
    out = []
    for kw in ("디자이너", "UX UI 디자인", "그래픽 디자인"):
        q = urllib.parse.urlencode({"access-key": key, "keywords": kw, "count": 110, "sort": "pd",
                                    "fields": "posting-date,expiration-date"})
        d = json.loads(get("https://oapi.saramin.co.kr/job-search?" + q, {"Accept": "application/json"}))
        for j in (d.get("jobs") or {}).get("job") or []:
            pos = j.get("position") or {}
            posted = to_dt(j.get("posting-timestamp"))
            out.append(job("사람인", pos.get("title"), ((j.get("company") or {}).get("detail") or {}).get("name"),
                           j.get("url"), posted, (pos.get("location") or {}).get("name", "").replace("&gt;", ">"),
                           to_dt(j.get("expiration-timestamp"))))
    return out


def remotive():
    d = json.loads(get("https://remotive.com/api/remote-jobs?category=design&limit=100"))
    return [job("Remotive", j.get("title"), j.get("company_name"), j.get("url"), to_dt(j.get("publication_date")),
                j.get("candidate_required_location") or "Remote") for j in d.get("jobs") or []]


def weworkremotely():
    root = ET.fromstring(get("https://weworkremotely.com/categories/remote-design-jobs.rss"))
    out = []
    for it in root.iter("item"):
        t = (it.findtext("title") or "").strip()
        company, _, title = t.partition(": ")
        if not title:
            company, title = "", t
        out.append(job("We Work Remotely", title, company, (it.findtext("link") or "").strip(),
                       to_dt(it.findtext("pubDate")), it.findtext("region") or "Remote"))
    return out


def remoteok():
    d = json.loads(get("https://remoteok.com/api?tag=design", {"Accept": "application/json"}))
    out = []
    for j in d:
        if not isinstance(j, dict) or not j.get("position"):
            continue   # 첫 줄은 이용 안내
        out.append(job("Remote OK", j.get("position"), j.get("company"), j.get("url") or j.get("apply_url"),
                       to_dt(j.get("epoch") or j.get("date")), j.get("location") or "Remote"))
    return out


SOURCES = [("사람인", saramin, "kr"), ("Remotive", remotive, "global"),
           ("We Work Remotely", weworkremotely, "global"), ("Remote OK", remoteok, "global")]
CREDIT = {
    "사람인": ("사람인", "https://www.saramin.co.kr"),
    "Remotive": ("Remotive", "https://remotive.com"),
    "We Work Remotely": ("We Work Remotely", "https://weworkremotely.com"),
    "Remote OK": ("Remote OK", "https://remoteok.com"),
}


def collect():
    groups, report = {"kr": [], "global": []}, []
    for name, fn, region in SOURCES:
        try:
            items = fn()
        except Exception as err:   # 한 곳이 실패해도 나머지는 계속
            report.append(f"{name}: 실패 ({type(err).__name__}: {str(err)[:80]})")
            continue
        if items is None:
            report.append(f"{name}: 건너뜀 (키 없음)")
            continue
        fresh = []
        for j in items:
            if not j["title"] or not j["url"] or not j["url"].startswith("http"):
                continue
            if region == "global" and not DESIGN_WORDS.search(j["title"]):
                continue
            posted = to_dt(j["posted"])
            if posted and posted < SINCE:
                continue
            fresh.append(j)
        fresh.sort(key=lambda j: j["posted"], reverse=True)
        groups[region] += fresh[:PER_SOURCE]
        report.append(f"{name}: {len(fresh)}건 중 {min(len(fresh), PER_SOURCE)}건")
    for k in groups:   # 같은 공고가 여러 번 잡히면 하나만
        seen, uniq = set(), []
        for j in groups[k]:
            sig = (j["url"].split("?")[0], j["title"].lower(), j["company"].lower())
            if sig[0] in seen or (sig[1], sig[2]) in seen:
                continue
            seen.update({sig[0], (sig[1], sig[2])})
            uniq.append(j)
        groups[k] = sorted(uniq, key=lambda j: j["posted"], reverse=True)
    return groups, report


# ---------- 페이지 ----------
def row(j):
    posted = to_dt(j["posted"])
    when = f"{posted.month}. {posted.day}" if posted else ""
    meta = " · ".join(x for x in (e(j["company"]), e(j["location"]),
                                 f'마감 {j["deadline"][5:].replace("-", ". ")}' if j["deadline"] else "") if x)
    return (f'        <a class="arow" href="{e(j["url"])}" target="_blank" rel="noopener nofollow">\n'
            f'          <span class="arow__date">{when}</span>\n'
            f'          <span class="arow__main">\n'
            f'            <span class="arow__title">{e(j["title"])}</span>\n'
            f'            <span class="arow__desc">{meta}</span>\n'
            f'          </span>\n'
            f'          <span class="arow__tag">{e(j["source"])}</span>\n'
            f'        </a>')


def block(title, desc, items, empty):
    rows = "\n".join(row(j) for j in items) if items else f'        <p class="ptext ptext--note">{e(empty)}</p>'
    return (f'    <section class="section">\n{section_head(title, len(items), desc, level=2)}\n'
            f'      <div class="list list--insight">\n{rows}\n      </div>\n    </section>')


def build(groups, report):
    year, week, _ = NOW.isocalendar()
    start, end = SINCE.date(), NOW.date()
    title = "이번 주 디자이너 채용 공고"
    desc = (f"{start.month}월 {start.day}일부터 {end.month}월 {end.day}일까지 올라온 디자이너 채용 공고를 모았습니다. "
            "국내 공고와 해외 원격 근무 공고를 매주 월요일 새로 정리합니다.")
    kr_skipped = any(r.startswith("사람인: 건너뜀") for r in report)
    used = [n for n, *_ in SOURCES if any(j["source"] == n for g in groups.values() for j in g)]
    credits = " · ".join(f'<a href="{CREDIT[n][1]}" target="_blank" rel="noopener">{CREDIT[n][0]}</a>' for n in used)
    body = f"""    <section class="section">
{section_head(title, sum(len(g) for g in groups.values()), f"{year}년 {week}주차 · 매주 월요일 갱신")}
      <p class="page__intro">{e(desc)}</p>
      <p class="ptext ptext--note">공고를 누르면 원래 올라온 곳으로 갑니다. 지원 조건과 마감은 원문에서 꼭 다시 확인하세요.
      채용 사이트 모음은 <a href="{SITE}jobs/">디자이너 채용 사이트</a>에 있습니다.</p>
    </section>
{block("국내", "사람인 공개 API", groups["kr"],
       "국내 공고는 준비 중입니다." if kr_skipped else "이번 주에 새로 올라온 국내 공고를 가져오지 못했습니다.")}
{block("해외 · 원격 근무", "Remotive · We Work Remotely · Remote OK", groups["global"],
       "이번 주에 새로 올라온 해외 원격 공고를 가져오지 못했습니다.")}
    <p class="ptext ptext--note">공고 출처: {credits or "없음"}. 공고의 저작권은 각 회사와 출처 사이트에 있습니다.
    마지막 갱신 {NOW.strftime("%Y. %m. %d %H:%M")} (한국 시간).</p>"""
    url = SITE + "jobs/weekly/"
    jsonld = {"@context": "https://schema.org", "@type": "CollectionPage", "url": url, "name": title,
              "description": desc, "inLanguage": "ko", "dateModified": NOW.isoformat(),
              "isPartOf": {"@type": "WebSite", "url": SITE, "name": "디자인 허브"},
              "breadcrumb": {"@type": "BreadcrumbList", "itemListElement": [
                  {"@type": "ListItem", "position": 1, "name": "디자인 허브", "item": SITE},
                  {"@type": "ListItem", "position": 2, "name": "디자이너 채용 사이트", "item": SITE + "jobs/"},
                  {"@type": "ListItem", "position": 3, "name": title, "item": url}]}}
    doc = document(title=title, desc=desc, url=url, body=body, jsonld=jsonld, menu=menu("jobs"),
                   footer_nav=footer_links())
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "index.html").write_text(doc, encoding="utf-8")
    DATA.mkdir(parents=True, exist_ok=True)
    (DATA / f"{year}-W{week:02d}.json").write_text(
        json.dumps({"updated": NOW.isoformat(), "since": SINCE.isoformat(), "report": report, **groups},
                   ensure_ascii=False, indent=1), encoding="utf-8")


if __name__ == "__main__":
    groups, report = collect()
    for line in report:
        print(line)
    total = sum(len(g) for g in groups.values())
    if total == 0 and (OUT / "index.html").exists():
        print("가져온 공고가 하나도 없어서 지난 페이지를 그대로 둡니다.")
        sys.exit(0)
    build(groups, report)
    print(f"/jobs/weekly/ 갱신: 국내 {len(groups['kr'])}건, 해외 {len(groups['global'])}건")
