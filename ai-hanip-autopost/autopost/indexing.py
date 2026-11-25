"""구글 색인: Search Console 에 사이트맵 재제출 + 색인 상태 조회.

※ 구글 Indexing API 는 채용공고·라이브 방송 전용이라 블로그 글에는 쓰지 않습니다(정책 위반).
   대신 공식적으로 허용된 사이트맵 제출로 새 글을 빨리 가져가도록 알립니다.
"""
from googleapiclient.discovery import build

from .blogger import get_creds


def _svc():
    return build("searchconsole", "v1", credentials=get_creds(), cache_discovery=False)


def submit_sitemap(blog_url: str) -> str:
    site = blog_url.rstrip("/") + "/"
    sitemap = site + "sitemap.xml"
    _svc().sitemaps().submit(siteUrl=site, feedpath=sitemap).execute()
    return sitemap


def inspect(blog_url: str, page_url: str) -> str:
    """색인 상태 한 줄 요약 (예: 'PASS · Submitted and indexed')."""
    site = blog_url.rstrip("/") + "/"
    r = _svc().urlInspection().index().inspect(
        body={"inspectionUrl": page_url, "siteUrl": site, "languageCode": "ko-KR"}).execute()
    st = r.get("inspectionResult", {}).get("indexStatusResult", {})
    return f"{st.get('verdict', '?')} · {st.get('coverageState', '')}"


def has_site(blog_url: str) -> bool:
    site = blog_url.rstrip("/") + "/"
    sites = _svc().sites().list().execute().get("siteEntry", [])
    return any(s["siteUrl"] == site and s.get("permissionLevel") != "siteUnverifiedUser" for s in sites)
