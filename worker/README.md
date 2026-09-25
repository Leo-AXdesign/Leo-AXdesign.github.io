# 이야기 페이지 댓글 서버

`/talk/` 페이지에 남긴 글을 받아서 저장하는 작은 서버입니다. Cloudflare Worker 와 D1(데이터베이스)로 돌아갑니다.
방문자는 가입도 로그인도 하지 않고 이름만 적으면 글을 남길 수 있습니다.

무료 한도는 하루 요청 10만 건입니다. 이 사이트 규모에서는 걸릴 일이 없습니다.

## 처음 한 번만 하는 설정

터미널에서 이 폴더(`worker/`)로 들어간 다음 순서대로 실행하세요.

```bash
cd worker
npx wrangler login
```

브라우저가 열리면 Cloudflare 계정으로 허용을 누릅니다. 도메인을 사면서 만든 그 계정입니다.

```bash
npx wrangler d1 create designrefs-talk
```

`database_id = "..."` 가 출력됩니다. 그 값을 `wrangler.toml` 의 같은 자리에 붙여넣으세요.

```bash
npx wrangler d1 execute designrefs-talk --remote --file=schema.sql
npx wrangler secret put ADMIN_TOKEN
npx wrangler secret put IP_SALT
npx wrangler deploy
```

- `ADMIN_TOKEN` 은 글을 지울 때 쓰는 비밀번호입니다. 아무 문자열이나 길게 정하고 따로 적어 두세요.
- `IP_SALT` 는 접속 IP 를 해시로 바꿀 때 섞는 값입니다. 역시 아무 긴 문자열이면 됩니다.
- 둘 다 파일에 저장되지 않고 Cloudflare 에만 들어갑니다.

마지막 `deploy` 가 끝나면 주소가 찍힙니다.

```
https://designrefs-talk.<계정이름>.workers.dev
```

이 주소를 `js/talk.js` 맨 위 `TALK_API` 에 `/comments` 를 붙여서 넣으세요.

```js
const TALK_API = 'https://designrefs-talk.<계정이름>.workers.dev/comments';
```

고친 뒤 커밋하고 push 하면 이야기 페이지가 살아납니다.

## 글 지우기

지우고 싶은 글의 번호를 알아야 합니다. 목록을 보려면:

```bash
curl "https://designrefs-talk.<계정이름>.workers.dev/comments?page=talk"
```

지우기:

```bash
curl -X DELETE -H "Authorization: Bearer <ADMIN_TOKEN>" \
  "https://designrefs-talk.<계정이름>.workers.dev/comments?id=12"
```

Cloudflare 대시보드의 D1 화면에서 표를 직접 열어 지워도 됩니다.

## 스팸이 들어오기 시작하면

`wrangler.toml` 의 `MODERATE` 를 `"1"` 로 바꾸고 다시 `npx wrangler deploy` 하세요.
새 글이 바로 보이지 않고, 대시보드에서 `hidden` 을 `0` 으로 바꾼 글만 올라갑니다.

지금 걸러 내고 있는 것:

- 사람 눈에 안 보이는 입력칸(봇만 채웁니다)
- 페이지를 열고 3초 안에 보낸 글
- 링크가 세 개 이상인 글
- 같은 사람이 30초 안에 또 쓰는 것, 하루 10개 넘게 쓰는 것

## 고친 뒤 확인

서버 코드를 고쳤으면 배포 전에 한 번 돌려 보세요. 가짜 데이터베이스로 규칙이 그대로인지 검사합니다.

```bash
node worker/test.mjs
```
