# hugs

# paper

[Jukebox: A Generative Model for Music](https://cdn.openai.com/papers/jukebox.pdf)

# Web Application Structure

![hug flask server project construction img](https://user-images.githubusercontent.com/41173953/85829483-ab622e00-b7c5-11ea-82bf-6031636af112.png)

- Flask template engine : Jinja
- Flask WSGI toolkit : Werkzeug
- External framework : Bootstrap
- External library : jquery
- Database : MySQL
- Database adapter library : pymysql

# Task Lists
- [x] 회원가입
  - [x] input validation verificate
  - [x] connect local database(test)
  - [x] connect cloud database(gcp)
- [x] 로그인
  - [x] check input with local database user data(test)
  - [x] check input with cloud database user data(gcp)
  - [x] session
- [x] 로그아웃
  - [x] pop the session
- [x] 뮤직리스트
  - [x] load all of public music(database)
- [ ] 마이뮤직리스트
  - [ ] save prefer public music and maked-myself music
- [ ] 플레이리스트
  - [ ] create a new playlist
  - [ ] delete a playlist
  - [ ] rename a playlist
  - [ ] add a new song into playlist
  - [ ] remove a song of playlist
- [ ] 노래 업로드 
- [ ] 노래 다운로드
- [ ] 노래 생성 기능(장르, 분위기, 가사, 노래길이 반영)
  - [ ] save genre
  - [ ] save atmosphere
  - [ ] save lyrics
  - [ ] save length
- [ ] 백그라운드 노래 생성(노래 생성중에도 사용자가 다른 작업을 할 수 있어야함)
  - [ ] processing AI in the background
  - [ ] send a push-notification to notice the end of processing
