"""{{media:ID}} 자리표시를 실제 이미지/영상 HTML로 교체."""
import html as h
import re

# 모양은 블로그 테마(theme/theme.css 의 .ah-fig / .ah-cap)가 정함. 인라인 스타일은 RSS·메일용 최소한만.
IMG = ('<div class="ah-fig separator" style="text-align:center;margin:2em 0 0;">'
       '<img src="{src}" alt="{alt}" loading="lazy" style="max-width:100%;height:auto;border-radius:12px;" /></div>')
VID = ('<div class="ah-fig" style="text-align:center;margin:2em 0 0;">'
       '<video src="{src}" autoplay muted loop playsinline controls preload="metadata" '
       'style="max-width:100%;border-radius:12px;"></video></div>')
CAP = '<p class="ah-cap" style="text-align:center;font-size:13px;color:#767676;">{cap}</p>'
MISSING = ('<p style="text-align:center;padding:1em;background:#fff4d6;border-radius:8px;">'
           '⚠️ [캡처 필요: {cap}]</p>')


def render(body_html: str, media: list, urls: dict) -> tuple[str, list]:
    """반환: (완성 HTML, 실패한 미디어 id 목록)"""
    by_id = {m["id"]: m for m in media}
    missing = []

    def sub(match):
        mid = match.group(1)
        m = by_id.get(mid, {"caption": mid, "kind": "screenshot"})
        cap = h.escape(m.get("caption", ""))
        if m.get("mockup"):
            cap = f"예시 화면(재현) · {cap}" if cap else "예시 화면(재현)"
        src = urls.get(mid)
        if not src:
            missing.append(mid)
            return MISSING.format(cap=cap or mid)
        tpl = VID if m.get("kind") == "video" else IMG
        return tpl.format(src=src, alt=cap) + (CAP.format(cap=cap) if cap else "")

    out = re.sub(r"(?:<p>\s*)?\{\{media:([\w-]+)\}\}(?:\s*</p>)?", sub, body_html)
    return out, missing
