"""기존 테마(백업)에 designrefs 스타일을 덧입힌 테마 파일 생성.

  python theme/build_reskin.py   →  theme/ai-hanip-reskin.xml  (Blogger → 테마 → HTML 편집에 붙여넣기)
위젯·광고·페이지 목록 등 기존 구조는 그대로 두고 CSS·스크립트만 추가합니다.
"""
from pathlib import Path

HERE = Path(__file__).parent
base = (HERE / "backup-contempo-20261015.xml").read_text(encoding="utf-8")
css = (HERE / "reskin.css").read_text(encoding="utf-8")
js = (HERE / "reskin.js").read_text(encoding="utf-8")
assert "]]>" not in css and "]]>" not in js

head = """<link crossorigin='anonymous' href='https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/variable/pretendardvariable-dynamic-subset.min.css' rel='stylesheet'/>
<script>//<![CDATA[
(function(){try{var t=localStorage.getItem('theme');if(t==='dark'||(!t&&matchMedia('(prefers-color-scheme: dark)').matches))document.documentElement.setAttribute('data-theme','dark');}catch(e){}})();
//]]></script>
"""
i = base.index("]]></b:skin>")
out = base[:i] + "\n/* ===== AI 한입 리스킨 ===== */\n" + css + "\n" + base[i:]
out = out.replace("</head>", head + "</head>", 1)
j = out.rindex("</body>")
out = out[:j] + "<script>//<![CDATA[\n" + js + "\n//]]></script>\n" + out[j:]
(HERE / "ai-hanip-reskin.xml").write_text(out, encoding="utf-8")
print("테마:", HERE / "ai-hanip-reskin.xml", len(out))
