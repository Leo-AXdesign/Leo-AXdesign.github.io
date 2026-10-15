# AI 한입 자동 포스팅

주제 하나 → **글 작성(Claude) → 스크린샷·화면녹화(Playwright) → 미디어 업로드(GitHub+jsDelivr) → Blogger 등록**까지 한 번에 처리합니다.

```
topics.yaml ──▶ Claude API (웹검색으로 최신 확인, 문체 가이드 적용)
                   │  글 HTML + 캡처 계획(JSON)
                   ▼
              Playwright ──▶ .webp 스크린샷 / .mp4 화면녹화
                   ▼
              GitHub 공개 저장소 ──▶ jsDelivr 주소
                   ▼
              Blogger API ──▶ 임시저장(기본) 또는 발행
```

## 1. 설치 (맥 기준, 최초 1회)

```bash
cd ai-hanip-autopost
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
playwright install chromium     # ffmpeg는 imageio-ffmpeg 패키지로 함께 설치됨 (brew 불필요)
cp config.example.yaml config.yaml
cp .env.example .env
```

## 2. 키 준비 (직접 발급해서 `.env` / 폴더에 넣기)

**글 작성용 Claude** — 기본값(`writer: cli`)은 API 키 없이 **Claude 구독**으로 씁니다.
```bash
curl -fsSL https://claude.ai/install.sh | bash
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc && source ~/.zshrc
claude        # 처음 한 번 로그인 (구독 계정) 후 /exit
```
유료 API를 쓰고 싶으면 `config.yaml`에서 `writer: api`로 바꾸고 `.env`의 `ANTHROPIC_API_KEY`를 채우세요.

**Blogger API**
1. console.cloud.google.com → 새 프로젝트
2. "API 및 서비스 → 라이브러리"에서 **Blogger API v3** 사용 설정
3. "OAuth 동의 화면" 구성 (외부, 테스트 사용자에 본인 구글 계정)
4. "사용자 인증 정보 → OAuth 클라이언트 ID → **데스크톱 앱**" → JSON 다운로드 → 이 폴더에 `client_secret.json`으로 저장
5. `python -m autopost.auth` → 브라우저에서 로그인 → "연결 완료. 블로그 ID: …" 나오면 성공

> ⚠️ 동의 화면이 **"테스트"** 상태면 로그인이 7일마다 풀립니다. 자동 실행하려면 동의 화면에서 **"앱 게시(프로덕션)"**로 바꿔두세요. 본인만 쓰는 앱이라 "확인되지 않은 앱" 경고는 무시하고 진행하면 됩니다.

**미디어 저장소 (GitHub)**
1. 새 **공개(Public)** 저장소 생성 (예: `ai-hanip-media`), README 하나 넣어서 main 브랜치 생성
2. Settings → Developer settings → **Fine-grained token** → 이 저장소 하나만, **Contents: Read and write**
3. `.env`의 `GITHUB_TOKEN`, `config.yaml`의 `github.owner` 입력

> Blogger API는 이미지·영상 업로드를 지원하지 않아서 외부 호스팅이 필요합니다. jsDelivr는 무료 CDN이라 블로그 속도에도 유리해요.

설정을 마치면 `python -m autopost.check` 로 한 번에 점검할 수 있어요(읽기만 함).

## 3. 로그인 화면 캡처 준비 (선택)

챗GPT·클로드·제미나이의 **로그인 후 화면**을 캡처하려면, 자동화 전용 브라우저에 한 번 로그인해두세요.

```bash
python -m autopost.login
```
브라우저가 뜨면 각 탭에서 직접 로그인 → 터미널에서 Enter. 이후엔 이 상태를 재사용합니다.
(자동화용 브라우저라 실제 크롬과 분리돼 있어요.)

## 4. 실행

```bash
python -m autopost.main --dry-run          # 먼저 미리보기 (output/날짜-글/post.html 확인)
python -m autopost.main                    # topics.yaml 다음 주제 → Blogger 임시저장
python -m autopost.main --topic "챗GPT로 엑셀 수식 만드는 법" --note "VLOOKUP 예시"
python -m autopost.main --publish          # 검토 없이 바로 발행
```

## 5. 정기 자동 실행 (매일 9시·18시, launchd)

`~/Library/LaunchAgents/com.aihanip.autopost.plist` 에 등록돼 있고, `run.sh` 를 실행합니다.
맥이 잠자기 중이었으면 깨어날 때 실행되고, 실행 중엔 잠들지 않게 막습니다.

- **9시 (morning)**: 오늘의 AI 이슈를 웹검색으로 확인 → 큰 이슈가 있으면 이슈 글, 없으면 `topics.yaml` 다음 주제. 매일 1개는 올라감.
- **18시 (evening)**: 오늘 아직 안 다룬 큰 이슈가 있을 때만 1개 더. (오늘 글이 없으면 주제 목록에서 1개)
- 주제 목록이 비면 Claude가 지난 글과 겹치지 않는 입문 주제를 새로 정해 `topics.yaml`에 추가합니다.
- 발행하면 Search Console 에 사이트맵을 다시 제출하고, 3일 뒤 실행 때 그 글의 색인 상태를 로그에 남깁니다.
  (구글 Indexing API 는 채용공고·라이브 방송 전용이라 블로그 글엔 쓰지 않습니다.)
- 올린 글 기록: `posted.jsonl`

**최초 1회: 전체 디스크 접근 권한** — 이 폴더가 데스크탑 안이라 필요합니다.
시스템 설정 → 개인정보 보호 및 보안 → 전체 디스크 접근 권한 → `+` → `⌘⇧G` → `/bin/zsh` → 열기 → 켜기

```bash
launchctl kickstart gui/$(id -u)/com.aihanip.autopost      # 지금 한 번 실행 (실제 임시저장)
tail -50 ~/Library/Logs/ai-hanip-autopost.log              # 로그 보기
launchctl bootout gui/$(id -u)/com.aihanip.autopost        # 자동 실행 끄기
launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/com.aihanip.autopost.plist   # 다시 켜기
```
실패하면 맥 알림이 뜹니다. 요일·시간은 plist 의 `StartCalendarInterval` 에서 바꿉니다.

## 운영 팁

- **기본값은 바로 발행**(`draft: false`)입니다. 검토 후 발행하고 싶으면 `draft: true`. 캡처 자리가 비거나 이미지 CDN이 안 열리면 자동으로 임시저장됩니다.
- 봇 확인으로 막힌 화면은 '예시 화면(재현)'으로 대체됩니다.
- 영상은 20초 이하 무음 반복 재생(GIF처럼)으로 들어갑니다. 길이는 `video_max_seconds`로 조절.
- 문체를 바꾸고 싶으면 `style_guide.md`만 고치면 됩니다.
- 안전장치: 결제·가입·전송 같은 버튼 클릭은 캡처 단계에서 자동으로 건너뜁니다.

## 블로그 디자인 (테마)

designrefs.com 과 같은 흑백 미니멀 스타일. 기존 Contempo 테마의 구조(위젯·애드센스·페이지 목록)는 그대로 두고 CSS·스크립트만 덧입힙니다.

- `theme/reskin.css` — 스타일 (다크 모드 포함) / `theme/reskin.js` — 다크 모드 버튼, 홈 머리말, 프롬프트 복사 버튼
- `theme/backup-contempo-20261015.xml` — 적용 전 원래 테마 (되돌릴 때 이걸 붙여넣기)
- 수정 후 적용: `python theme/build_reskin.py` → `theme/ai-hanip-reskin.xml` 을 Blogger → 테마 → ▼ → HTML 편집에 통째로 붙여넣고 **미리보기(눈 아이콘)로 확인한 뒤** 저장
  - 미리보기가 빈 화면이면 먼저 미리보기의 새로고침 버튼을 눌러 보세요(가끔 일시적). 계속 비면 CSS 주석에 `<` `>`가 들어간 게 원인입니다(빌드 스크립트가 자동으로 치환).
  - 편집기가 붙여넣기를 무시하면: XML 을 공개 저장소(raw.githubusercontent.com)에 올린 뒤 편집기 페이지 콘솔에서 `fetch` 로 받아 CodeMirror `setValue` 하는 방법이 확실합니다.
