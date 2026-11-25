#!/usr/bin/env python3
"""
사이트에 올리기 — 관리자의 '사이트에 올리기'와 같은 일을 명령 한 줄로 합니다.

  python3 tools/publish.py "커밋 메시지"

최신 내용 받기 → 빌드 → 커밋 → 푸시. Claude 데스크톱의 designhub 도구(site_publish)가 씁니다.
"""
import importlib.util, pathlib, sys

TOOLS = pathlib.Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("admin", TOOLS / "admin.py")
admin = importlib.util.module_from_spec(spec)
spec.loader.exec_module(admin)

if __name__ == "__main__":
    msg = " ".join(sys.argv[1:]) or "글 고침"
    try:
        r = admin.publish({"message": msg})
    except (admin.Oops, SystemExit) as err:
        print(str(err))
        sys.exit(1)
    print(r.get("message", ""))
