-- 댓글 표. wrangler d1 execute 로 한 번만 실행하면 됩니다.
CREATE TABLE IF NOT EXISTS comments (
  id     INTEGER PRIMARY KEY AUTOINCREMENT,
  page   TEXT    NOT NULL,              -- 어느 페이지에 달린 글인지
  name   TEXT    NOT NULL,
  body   TEXT    NOT NULL,
  at     INTEGER NOT NULL,              -- 남긴 시각 (1970년부터 밀리초)
  who    TEXT,                          -- 접속 IP 를 해시로 바꾼 값 (스팸 방지용)
  hidden INTEGER NOT NULL DEFAULT 0     -- 1 이면 화면에 보이지 않음
);
CREATE INDEX IF NOT EXISTS idx_comments_page ON comments (page, id);
CREATE INDEX IF NOT EXISTS idx_comments_who  ON comments (who, at);
