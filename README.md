# HCT 발표 템플릿

주식회사 에이치시티 사내 공용 발표 슬라이드 디자인 시스템. **블루 리포트**라 부른다.

한 소스에서 **HTML · PDF · PowerPoint** 세 형식을 만들고, 규칙을 사람 눈이 아니라 스크립트가 판정한다.

---

## 쓰는 법 — 다섯 가지

다섯 다 같은 규격을 뜨게 하지만 **미치는 범위와 갱신 방식이 다르다.**

| | 어디까지 뜨나 | 최신판 유지 | 손이 가는 횟수 |
|---|---|---|---|
| 0. 계정 지침 | **에이전트 종류를 가리지 않는다** — Claude 전 세션 · Codex · 그 밖의 도구 | 없음 — 경로만 적혀 저절로 최신 | 계정·도구마다 한 번 |
| 1. 플러그인 | 그 PC 의 모든 프로젝트 | `plugin marketplace update` 로 당긴다 | PC 마다 한 번 |
| 2. 계정 스킬 | **그 계정의 모든 세션** — claude.ai · 각 PC · 원격 | 판올림마다 다시 올린다 | 계정에 한 번 |
| 3. 클론 | 그 폴더 안에서만 | `git pull` | 쓸 때마다 |
| 4. 복사 | 그 PC 의 모든 프로젝트 | 다시 복사한다 | PC 마다 한 번 |

**0 과 1 을 같이 쓰는 것이 무난하다.** 0 으로 어느 도구에서 시작하든 저장소를 가지러 오게
해 두고, 주로 쓰는 PC 에는 1 을 깔아 미리 받아 둔다.

### 0. 계정 지침 — 에이전트가 스스로 저장소를 가지러 온다

GitHub 계정을 연결했다는 사실만으로 에이전트가 이 템플릿을 쓰지는 않는다. 어느 플랫폼도
사용자의 GitHub 계정을 훑어 스킬을 찾아 오지 않기 때문이다. 에이전트는 자기가 열려 있는
저장소만 본다.

그래서 계정 지침에 **"회사 양식 요청을 받으면 이 저장소를 가져와라"** 한 문단을 심는다.
그때부터 GitHub 권한이 실제로 쓰이고, 다른 프로젝트에서 시작한 세션도 이 규격을 따른다.
지침에는 경로만 들어가고 색값·덱 목록은 들어가지 않으므로 판올림해도 손댈 일이 없다.

붙여넣을 문단과 확인 방법은 **[`docs/AGENT_WIRING.md`](docs/AGENT_WIRING.md)** 에 있다.
Codex 처럼 전역 지침 파일을 쓰는 도구는 설치기로 심을 수 있다.

```bash
python3 scripts/install_codex_pointer.py --check     # 상태만 본다
python3 scripts/install_codex_pointer.py             # 설치 또는 갱신
```


### 1. Claude Code — 플러그인 (권장)

저장소를 클론하지 않아도 되고, PC 마다 한 번만 실행하면 그 PC 의 모든 프로젝트에서 쓸 수 있다.

```bash
claude plugin marketplace add hctinno/blue-report
claude plugin install blue-report@blue-tools
```

설치 뒤 **세션을 새로 시작**하면 다음 중 어느 말로 불러도 스킬이 뜬다.

```
보고서 템플릿 활용해서 8월 사내 월간보고 만들어줘.
우리 회사 양식으로 주간보고 덱 만들어줘.
블루 리포트로 경영진 보고 만들어줘.
```

「보고서 템플릿」 · 「사내 보고서 템플릿」 · 「회사 양식」 · 「우리 템플릿」 ·
「HCT 템플릿」 · 「블루 리포트」 · 「AX 리포트 스타일」 · 「딥 코발트」 가 모두 스위치다.
설치 직후 실행 중인 세션은 새 스킬을 읽지 않는다 — 반드시 세션을 새로 연다.

> `.claude/settings.json` 의 `extraKnownMarketplaces` 는 마켓플레이스를 **등록**만 한다. 설치는 하지 않는다. `plugin install` 은 PC 마다 한 번 실행해야 한다.

### 2. Claude 계정 스킬 — 계정 전체에 한 번

플러그인은 **PC 마다** 깔아야 한다. 계정 스킬로 올리면 그 계정의 모든 세션
— claude.ai 대화, 각 PC 의 Claude Code, 원격 세션 — 에 자동으로 동기화된다.
PC 를 바꾸거나 원격 세션을 새로 띄워도 따라온다.

```bash
python3 scripts/build_account_skill_bundle.py
```

`decks-out/blue-report-skill-v<버전>.zip` 이 뜬다.
claude.ai → Settings → Capabilities → Skills 에서 이 zip 을 올린다.

묶음은 저장소 판과 두 가지가 다르다. 홀로 돌아야 하기 때문이다.

| | 저장소 판 | 계정 스킬 묶음 |
|---|---|---|
| 브랜드 자산 | 루트의 `brand/hct/` 를 `../../../` 로 가리킨다 | 안에 넣는다 (`brand/hct/`) |
| `pptx/node_modules` | 있다 | 뺀다 — `cd pptx && npm install` |
| `dist/` | 있다 | 뺀다 — 스킬이 읽지 않는다 |

**판올림하면 묶음을 다시 떠서 다시 올린다.** 계정 스킬은 저장소를 보고 있지 않다.
자동으로 최신판이 되는 것은 1번 플러그인 쪽뿐이다(`plugin marketplace update`).

### 3. Codex 등 다른 에이전트 — 클론

Codex 는 `.claude/skills/` 를 인식하지 못한다. 파일이 디스크에 있어야 한다.

```bash
git clone https://github.com/hctinno/blue-report.git
cd blue-report
```

그 폴더에서 에이전트를 띄우고 한 줄 친다.

```
docs/CODEX_DECK_PROMPT.md 를 읽고 그대로 수행해라. 용도는 사내 보고, 주제는 8월 월간 업무 보고.
```

용도와 주제를 빼도 된다. 그 경우 에이전트가 먼저 묻는다.

### 4. 그 PC 안에서만 복사

계정을 거치지 않고 이 PC 의 사용자 스킬 폴더(`~/.claude/skills/`)에만 두고 싶을 때다.
그 PC 의 모든 프로젝트에서 뜨지만 다른 PC 나 원격 세션에는 따라가지 않는다.

```bash
python scripts/install_blue_report_skill.py                       # 사용자 스킬 폴더
python scripts/install_blue_report_skill.py --target <프로젝트경로>   # 특정 프로젝트
```

---

## 덱 12종

같은 레이아웃을 쓰되 배치 순서와 장수가 용도에 맞게 다르다. 조직 주간보고는 매주 반복하므로 목차를 두지 않고 타임라인이 요일 단위다. 사내 보고는 다크 요약이 3번째에 있고(경영진이 앞부분만 보고 넘어간다), 외부 제안은 9번째에 있다(문제 제기부터 설득한 뒤 정리한다).

| 파일 | 용도 | 장수 |
|---|---|---|
| `deck-internal-report.html` | 사내 보고 (월간) | 9 |
| `deck-weekly-report.html` | 조직 주간보고 | 7 |
| `deck-ax-weekly.html` | AX 조직 1장 보고 + 부록 | 5 |
| `deck-team-weekly.html` | 팀 압축 주간보고 | 2 |
| `deck-exec-report.html` | 경영진 보고 (결론 먼저) | 6 |
| `deck-allhands.html` | 전직원 보고 (타운홀) | 9 |
| `deck-sales-proposal.html` | 외부 제안·영업 | 10 |
| `deck-project-report.html` | 프로젝트 착수·완료 | 9 |
| `deck-training.html` | 교육·기술 설명 | 8 |
| `deck-strategy-report.html` | 전략 보고 (논증형 결정 요청) | 16 |
| `deck-report.html` | 고밀도 보고 (본문 14 + 부록 5 · 도해 중심) | 19 |
| `deck-template.html` | 레이아웃 19종 카탈로그 | 19 |

전부 `.claude/skills/blue-report/assets/` 에 있다.

---

## 기준 덱과 라이브 덱 2종

**새 보고서는 기준 덱 `standard` 에서 시작한다.** 회사 발표 덱의 표준 모양이 여기 다 들어 있다 —
머리띠(절 번호 + 절 이름 + 로고), 꼬리띠(문서명 + 쪽번호), 진행선, 우하단 워터마크, 제목 형광 밴드,
상단 강조선 카드, 결론 줄. 복사해서 내용만 바꾸면 회사 문서가 된다.

고정 지면이 없는 계통이다. 한 장이 `100dvh` 이고 루트 글자 크기가 뷰포트를 따라간다.

```css
html { font-size: clamp(10.5px, min(1vw, 1.78vh), 20px) }
```

`1.78vh` 가 16:9 다(100 / 56.25). 가로·세로 중 빡빡한 쪽을 따르므로 어느 창에서도 잘리지 않고,
배율 계산이 이 한 줄로 끝난다. 넘김은 브라우저의 `scroll-snap` 이 하므로 **JS 없이 열어도
세로로 스크롤하면 전부 읽힌다.** 축 하나만 바꾸면 가로 발표 모드다.

| 파일 | `--deck` 이름 | 용도 |
|---|---|---|
| `live-standard.html` | `standard` | **기준 덱 — 새 보고서의 출발점.** 레이아웃 어휘 13장 · 사내 발표 덱 짜임새 |
| `live-brief.html` | `live` | 라이브 브리핑 — 짧은 브리핑용 (견본) |

글자 하한이 **본문 1.0rem · 주석 0.78rem** 이다(슬라이드 24px). 한 장에 훨씬 많이 담는 대신
발표 거리가 아니라 화면 거리에서 읽히는 것을 택한 계통이다.

### 지면 크롬은 선택이 아니다

`check_live.py` 가 22항목을 판정하고, 그중 여섯이 크롬이다 — 머리띠 · 꼬리띠 · 쪽번호 ·
머리띠 브랜드 마크 · 워터마크 · **마크 배경 짝**. 하나라도 빠지면 실패다.

넷은 산출물이 실제로 회사 문서로 나왔는지를 본다 — 로고 자리에 「COMPANY NAME」이 남지
않았는가, 계통 CSS 와 본문 폰트가 렌더에서 붙었는가, 지면이 화면 끝까지 닿는가, 출처 칩이
근거에 이어지는가. 앞의 셋은 견본을 복사해 내용만 바꾸거나 `--single-file` 없이 낸 산출물을
옮겼을 때 실제로 깨졌던 자리다.

### 사내 발표 덱과 같은 부품

| 부품 | 무엇 |
|---|---|
| 표지 | 눈썹(연도 + 무엇의 보고) · 제목 + (안) · 구분선 · 한 줄 메시지 · 우하단 발표자 블록 |
| 보고 요지 | 왼쪽 결론 + 결정 요청 상자 · 오른쪽 근거 세 줄 |
| 로드맵 | 과제 행 × 기간 열 + 확인할 결과 · 행마다 범주 색 |
| 출처 칩 | 수치 옆 「출처」 → 근거 패널(등급 A·B·C·R · 사실 · 출처 · 날짜 · 원문) |
| 조작판 | 펼침 E · 가로 H · 메모 N · 발표 F · 대본 S · 도움말 ? |
| 세는 숫자 | 쪽번호·장 번호·서수는 IBM Plex Mono(OFL 1.1, 공식 분할 파일 그대로) |

규칙을 글로만 두었을 때 실제로 무슨 일이 있었는가 — 규격서에 로고와 워터마크가 적혀 있었지만
강제하는 것이 없었고, 그래서 이 템플릿을 쓴다고 하면서 로고도 워터마크도 띠도 없는 덱이 나왔다.
「우리 양식」이라면서 회사 문서로 보이지 않았다. 지금은 검사기가 막는다.

브랜드 마크의 `data-on` 이 지면과 **반대**인 점을 놓치기 쉽다. `data-on` 은 「이 마크가 어떤 배경
위에 앉는가」인데, 마크가 앉는 곳은 지면이 아니라 띠이고 띠 색은 지면과 반대다.

| 지면 | 머리띠 색 | 머리띠 마크 | 워터마크 |
|---|---|---|---|
| 밝은 장 | 짙음 | `data-on="dark"` | `data-on="light"` |
| 어두운 장 (`bl-sl--dark`) | 흼 | `data-on="light"` | `data-on="dark"` |

눈으로는 알아채기 어렵다 — 틀려도 로고가 배경에 묻힐 뿐 사라지지는 않는다. 검사기가 짝을 맞춘다.

치수는 `rem` 으로만 적는다. `px` 를 섞으면 그 값만 창 크기와 무관하게 고정돼 작은 창에서
그 요소만 커진다 — 검사기가 막는다.

## 웹 보드 5종

슬라이드도 A4 도 아닌 제3의 계통이다. 지면 크기가 없고 화면 폭에 따라 흐르며,
**읽는 물건이 아니라 상태를 바꾸는 화면**이다. 회차 중간에 값이 바뀌고 다음 사람이
이어받는다. PPTX·PDF 대상이 아니다.

| 파일 | 용도 | 특징 |
|---|---|---|
| `board-task.html` | 과제 실행보드 (가장 작은 견본) | 레일 내비 · KPI 스트립 · 필터 표 · 메모 |
| `board-manage.html` | 관리보드 (대시보드형) | 절 12 · 표 8 · 일정 격자 · 가로 막대 |
| `board-exec.html` | 실행보드 (항목 상태 · 메모) | 상태 알약 4단 순환 · 설비 진행판 · 주차 막대 |
| `board-team.html` | 팀보드 (칸반) | 칸반 4열 · 주차 격자 · 상세 겹칩 |
| `board-gap.html` | 점검보드 (공백 대조) | 공백 부모 + 대응 자식 · 비율 띠 · 대조표 |

보드는 `blue-report.css` + `blue-web.css` 두 파일을 함께 부른다. 글자 하한이
12.5px 이고 `check_board.py` 가 11항목을 판정한다.

---

## A4 문서

회의록 · 사규 · 매뉴얼 · 공지는 발표 슬라이드가 아니라 A4 세로 문서다.
지면 794×1123px(210×297mm @96dpi)이고 인쇄하면 그대로 A4 한 장이다.

| 파일 | 용도 | 쪽 |
|---|---|---|
| `doc-minutes.html` | 회의록 | 2 |
| `doc-policy.html` | 사규·규정 (조·항·호 · 개정 이력 · 결재란) | 3 |
| `doc-manual.html` | 매뉴얼·가이드 (목차 · 절차 단계 · 캡처 자리) | 3 |
| `doc-notice.html` | 공지 (1쪽 완결) | 1 |

색·타입·간격 토큰은 슬라이드와 같다. `blue-doc.css` 는 토큰을 선언하지 않고
`blue-report.css` 를 전제하므로 두 파일을 함께 불러야 한다. 그래서 슬라이드와
문서의 색이 갈라질 수 없다.

머리말에 로고, 꼬리말에 회사명이 쪽마다 들어간다. 한 장씩 떼어 돌려 보고 인쇄해
철하는 물건이라 어느 쪽을 집어도 출처가 보여야 하기 때문이다. 쪽번호 · 문서명 ·
문서번호는 뷰어가 채우므로 손으로 적지 않는다.

```bash
python .claude/skills/blue-report/scripts/check_doc.py decks-out/회의록.html
```

9항목을 기계로 판정한다. 슬라이드와 기준이 다른 곳은 글자 하한(10.5pt = 14px)과
본문 대비(인쇄물이라 4.5:1)다.

---

## 만들기

저장소 루트에서 실행한다. 산출물은 `decks-out/` 에 넣는다(gitignore 처리돼 있다).
macOS·Linux 는 `python` 대신 `python3`.

```bash
# HTML — 회사명·로고·저작권을 넣어 한 파일로
python .claude/skills/blue-report/scripts/apply_brand.py --brand brand/hct/brand.json --deck internal --single-file -o decks-out/deck.html

# PDF — --notes 를 주면 발표자 노트를 마지막 장에 붙인다
python .claude/skills/blue-report/scripts/to_pdf.py decks-out/deck.html

# PowerPoint
node .claude/skills/blue-report/pptx/build.js --brand brand/hct/brand.json --out decks-out
```

`--deck` 은 덱 이름(`catalog` · `internal` · `weekly` · `ax` · `team` · `exec` · `allhands` · `sales` · `project` · `training` · `strategy`), A4 문서 이름(`minutes` · `policy` · `manual` · `notice`), 또는 HTML 파일 경로를 받는다.

덱을 웹페이지로 올려 링크로 공유하려면 Artifact 발행용 단일 파일을 만든다. `<html>` 껍데기를 뺀 판이다.

```bash
python .claude/skills/blue-report/scripts/build_single_file.py \
       --artifact --deck ax --brand brand/hct/brand.json -o decks-out/ax-artifact.html

python .claude/skills/blue-report/scripts/build_single_file.py \
       --artifact --deck minutes --brand brand/hct/brand.json -o decks-out/회의록.html
```

**`--artifact` 없이 만든 파일을 Artifact 로 올리지 않는다.** 그쪽은 `<!doctype>` ·
`<head>` · `<body>` 가 붙은 온전한 문서라, 발행 시점에 껍데기가 한 겹 더 씌워져 겹친다.
브라우저가 관대해 보이기는 하지만 파서가 안쪽 태그를 버린다.

필요한 것(Pillow · Chromium · node_modules)은 스크립트가 스스로 받는다. 미리 설치하지 않아도 된다. 막으려면 `BLUE_REPORT_NO_INSTALL=1` 을 준다.

---

## 완료 조건

```bash
python .claude/skills/blue-report/scripts/check_deck.py decks-out/deck.html
```

17항목을 기계로 판정한다.

문체(금지 어미) · 파이 차트 금지 · 도넛 dasharray 검산 · 토큰 밖 raw hex · 슬라이드 크기 1920x1080 · 최소 글자 24px · 데이터 마크 대비 2:1 · **본문 영역 겹침** · 브랜드 마크 존재 · 마크와 본문 겹침 · 배경 밝기와 로고 변형 일치.

**실패가 0 이 아니면 완료가 아니다.** `주의`는 허용된다(도넛을 쓰지 않은 덱에서 나오는 정상 결과).

`--shots <폴더>` 를 붙이면 슬라이드별 PNG 를 남긴다. 겹침은 스크립트가 잡지만 어색한 여백은 잡지 못하므로 눈으로 한 번 본다.

### 템플릿 자체를 고쳤다면

덱 하나가 아니라 템플릿·스크립트·문서를 고쳤을 때는 저장소 전체를 본다.

```bash
python3 scripts/verify_repo.py            # 전부
python3 scripts/verify_repo.py --shots out  # 슬라이드 PNG 77장도 남긴다
```

덱 12종을 만들어 `check_deck.py` 로, A4 문서 4종을 `check_doc.py` 로, 라이브 덱을 `check_live.py` 로, 웹 보드 5종을
`check_board.py` 로 판정하고, PPTX 11종 생성과 무결성 · `dist/` 재생성 대조 ·
한국어 인코딩 · 배포 매니페스트 · 내용 동기화 · 버전 올림을 함께 본다.
실패가 있으면 종료 코드가 1 이다.

**GitHub Actions 가 push·PR 마다 이 스크립트를 그대로 돌린다**(`.github/workflows/verify.yml`).
CI 와 로컬이 같은 한 줄을 쓰므로 결과가 갈라지지 않는다. 워크플로를 수동 실행할 때
`shots` 를 켜면 슬라이드 PNG 를 아티팩트로 내려받을 수 있다.

---

## 브랜드

`brand/hct/brand.json` 한 곳에서 회사명·로고·저작권을 관리한다.

로고는 **두 벌**이 필요하다. 마크가 모든 슬라이드 우측 상단에 들어가는데 배경이 딥네이비(`#071b45` · `#101827`)와 밝은 지면(`#f4f6f8`)을 오가므로 한 벌로는 반드시 한쪽에서 안 보인다.

| 항목 | 쓰이는 곳 | 파일 |
|---|---|---|
| `logo` | 표지 · 파트 간지 · 다크 요약 | `hct-logo-white.png` (흰색 녹아웃) |
| `logoOnLight` | 그 밖의 모든 본문 슬라이드 | `hct-logo-color.png` (원색) |

원본 한 장에서 두 벌을 뽑는 스크립트가 있다.

```bash
python .claude/skills/blue-report/scripts/make_logo_variants.py 로고.png --out-dir . --name mylogo
```

HCT 브랜드 파랑은 로고 원본에서 측정한 `#2f4a9c` 다. 밝은 지면 대비 7.51:1, 표지 `#071b45` 위에서는 2.06:1 이라 녹아웃이 필요하다.

**현재 로고 원본의 마크 영역은 264x86px 이다.** 화면용으로는 충분하지만 인쇄에는 모자란다. SVG 나 고해상도 원본이 생기면 교체한다.

---

## 규격서

`.claude/skills/blue-report/README.md` 가 자기완결 사양서다. 색값 · 타입 스케일 · 간격 · 차트 계산법 · 문체 규칙이 전부 들어 있어, 파일을 줄 수 없는 환경(웹 UI 등)에서는 이 문서를 통째로 붙여넣고 쓸 수 있다.

`.claude/skills/blue-report/references/rules.md` 는 같은 내용의 압축본이다.

규격을 바꾼 근거(외부 자료 실측·대조)는 `.claude/skills/blue-report/references/decisions/`
에 주제별로 모아 둔다. `CHANGELOG.md` 가 "무엇을 바꿨는가"라면 이쪽은 "왜 그렇게
판단했는가"의 원본이다.

---

## 구성

```
.claude-plugin/marketplace.json          플러그인 마켓플레이스 정의
.claude/skills/blue-report/
  SKILL.md                               스킬 트리거 정의
  README.md                              자기완결 사양서
  references/rules.md                    압축 규칙
  references/decisions/                  규격을 바꾼 근거(실측·대조) 원본 — README.md 가 색인
  assets/blue-report.css                 토큰 77개 — 단일 소스
  assets/deck-*.html                     완성 덱 11종 + 레이아웃 카탈로그 19종
  assets/blue-doc.css                    A4 문서 파운데이션 — 토큰은 위 파일 것을 쓴다
  assets/doc-*.html · doc-viewer.*       A4 문서 4종과 그 뷰어
  assets/blue-web.css                    웹 보드 파운데이션 — 토큰은 위 파일 것을 쓴다
  assets/board-*.html                    웹 보드 5종
  assets/blue-live.css                   라이브 계통 파운데이션 — 토큰은 위 파일 것을 쓴다
  assets/live-standard.html              기준 덱 — 새 보고서의 출발점
  assets/live-brief.html · live-viewer.js 라이브 브리핑 견본과 그 뷰어
  scripts/check_deck.py                  슬라이드 17항목 자동 점검
  scripts/check_doc.py                   A4 문서 9항목 자동 점검
  scripts/check_board.py                 웹 보드 11항목 자동 점검
  scripts/apply_brand.py                 브랜드 일괄 적용
  scripts/to_pdf.py                      PDF 내보내기
  scripts/make_logo_variants.py          로고 두 벌 생성
  scripts/donut.py · palette.py          도넛 SVG · 대비 검증
  scripts/ensure_deps.py                 의존성 자동 확보
  pptx/                                  PowerPoint 생성기
brand/hct/                               기본 브랜드 — 회사 정보와 로고
brand/sample/                            중립 견본 — 자기 브랜드를 만들 때 복사할 자리
AGENTS.md                                저장소를 연 에이전트가 자동으로 읽는 지침
docs/CODEX_DECK_PROMPT.md                Codex 등 외부 에이전트용 작업 지시서
docs/AGENT_WIRING.md                     다른 곳에서 시작한 에이전트를 이 저장소에 붙이는 법
scripts/verify_repo.py                   저장소 전체 점검 — CI 가 이것을 돌린다
scripts/check_content_sync.py            HTML 덱과 PPTX 내용 갈라짐 검사
CHANGELOG.md                             판올림 기록. 스킬을 고치면 여기에 적는다
scripts/install_blue_report_skill.py     오프라인 복사 설치기
scripts/install_codex_pointer.py         전역 지침에 이 저장소를 가리키는 문단을 심는다
.github/workflows/verify.yml             push·PR 자동 점검
```

`pptx/tokens.js` 가 `blue-report.css` 의 `--br-*` 를 파싱하므로 HTML 판과 PPTX 판의 색이 갈라질 수 없다.

내용은 그렇게 할 수 없어 `assets/deck-*.html` 과 `pptx/content.js` 두 곳에 따로 있다. HTML 이 기준이다. 두 곳을 합치지 않는 대신 `scripts/check_content_sync.py` 가 갈라짐을 잡고, CI 가 이것을 돌린다.

---

## 라이선스

MIT. `LICENSE` 를 본다. 견본 브랜드와 견본 데이터는 자리표시자이므로
자기 것으로 갈아 끼워 쓴다.
