"""최초 1회: 브라우저에서 구글 로그인 → token.json 생성."""
import yaml
from pathlib import Path
from .blogger import get_service, get_blog_id

if __name__ == "__main__":
    svc = get_service(interactive=True)
    cfg = yaml.safe_load(Path("config.yaml").read_text(encoding="utf-8"))
    print("연결 완료. 블로그 ID:", get_blog_id(svc, cfg["blog_url"]))
