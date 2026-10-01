# Codex 발표 덱 작업 지시서

이 문서는 사람이 읽는 설명서가 아니라 **에이전트에게 그대로 건네는 작업 지시**다.
Codex·Gemini 등 Claude Code 가 아닌 에이전트는 `.claude/skills/` 를 인식하지 못하므로
이 파일이 진입점 역할을 한다.

---

## 사람이 칠 한 줄

저장소 안에서 에이전트를 띄운 뒤 이렇게 친다. **경로는 저장소 루트 기준 상대 경로이므로
어느 PC 어느 폴더에 클론했든 그대로 통한다.**

```
docs/CODEX_DECK_PROMPT.md 를 읽고 그대로 수행해라. 용도는 사내 보고, 주제는 8월 월간 업무 보고.
```

용도와 주제를 빼고 파일만 지목해도 된다. 그 경우 에이전트가 먼저 물어본다.

| 넘길 값 | 고르는 것 |
|---|---|
| 용도 | 사내 월간 · 주간 · AX 주간 · 팀 압축 주간 · 경영진 · 전직원 · 외부 제안 · 프로젝트 · 교육 · 전략 · 고밀도 · A4 문서 · 웹 보드 |
| 주제 | 덱 제목과 내용 |
| 형식 | HTML(기본) · PDF · PPTX. 여러 개 가능. 보드는 HTML 만 |

저장소가 아직 없는 PC라면 먼저 받는다. 폴더 이름과 위치는 아무래도 좋다.

```bash
git clone -b main https://github.com/hctinno/blue-report.git
cd blue-report
```

매번 이 파일을 지목하는 것이 번거로우면 에이전트의 전역 지침에 한 번만 심어 둔다.
그러면 어느 폴더에서 시작하든 에이전트가 스스로 저장소를 받아 온다 —
`docs/AGENT_WIRING.md` 가 붙여넣을 문단과 설치기를 담고 있다.

---

## 여기서부터가 에이전트에게 주는 지시다

### 0. 준비와 사전 확인

**모든 경로는 저장소 루트 기준 상대 경로다.** 절대 경로를 쓰지 않는다. 저장소가 어느
드라이브 어느 폴더에 있든 상관없어야 한다. 먼저 저장소 루트로 이동해 `git pull` 로
최신 기본 브랜치(`main`)를 받는다.

명령 예시는 `python` 으로 적었다. macOS·Linux 에서는 `python3` 으로 바꿔 쓴다.
경로 구분자는 `/` 로 통일했다. Windows 에서도 그대로 동작한다.

아래 5개가 실재하는지 먼저 확인한다. **하나라도 없으면 작업을 멈추고 그 사실을 보고한다.**
없는 파일을 짐작으로 대체하지 않는다.

```
.claude/skills/blue-report/README.md
.claude/skills/blue-report/references/rules.md
.claude/skills/blue-report/assets/deck-template.html
.claude/skills/blue-report/scripts/check_deck.py
brand/hct/brand.json
```

### 1. 규격 읽기

`.claude/skills/blue-report/README.md` 를 **전부** 읽는다. 이것이 규격서다.
색값, 타입 스케일, 간격, 차트 계산법, 문체 규칙이 전부 여기 있다.

`.claude/skills/blue-report/references/rules.md` 는 같은 내용의 압축본이다. 함께 읽는다.

규격을 읽지 않고 시작하지 않는다. 이 시스템은 "파란색을 쓴다" 수준의 지침이 아니라
값과 계산식이 정해진 체계다.

### 2. 덱 고르기 — 새로 만들지 말고 골라서 내용만 바꾼다

**그냥 「보고서」·「발표자료」를 만들라는 지시라면 답은 기준 덱 `standard` 다.**
`assets/live-standard.html` 을 복사해 내용만 바꾼다. 회사 발표 덱의 표준 모양이
그 파일에 다 들어 있다 — 머리띠, 꼬리띠, 로고, 워터마크, 진행선, 제목 형광 밴드.
다른 계통은 용도가 분명할 때만 고른다(1920x1080 고정 지면이 필요하다, PPTX 로 내보내야
한다, 인쇄용 A4 다, 화면에서 상태를 바꾸는 보드다).

`.claude/skills/blue-report/assets/` 에 완성된 덱이 11종, 레이아웃 카탈로그 1종,
A4 세로 문서가 4종, 웹 보드가 5종, 기준·라이브 덱이 2종 있다. 용도에 맞는 것을 복사해
**내용만** 교체한다. 레이아웃과 스타일을 새로 설계하지 않는다.

#### 기준 덱 · 라이브 덱 2종 — 고정 지면이 없는 계통

| 파일 | `--deck` 이름 | 용도 | 장수 |
|---|---|---|---|
| `live-standard.html` | `standard` | **기준 덱 — 새 보고서의 출발점** | 13 |
| `live-brief.html` | `live` | 라이브 브리핑 (짧은 브리핑 견본) | 8 |

한 장이 `100dvh` 이고 루트 글자 크기가 `clamp(10.5px, min(1vw, 1.78vh), 20px)` 로 창을
따라간다. 안의 치수는 **전부 `rem`** 이다. `px` 를 적으면 그 값만 창과 무관하게 굳어
작은 창에서 그 요소만 커진다 — `check_live.py` 가 막는다.

복사할 때 다음 4개를 같은 폴더에 함께 둔다.

```
assets/blue-report.css      색·폰트 토큰
assets/blue-live.css        배율·띠·부품
assets/live-viewer.js       뷰어
assets/fonts/               폰트 서브셋
```

**지면 크롬은 장식이 아니라 필수다.** 장마다 전부 있어야 하고, 하나라도 빠지면
`check_live.py` 가 실패로 잡는다.

| 부품 | 마크업 | 담는 것 |
|---|---|---|
| 머리띠 | `<header class="bl-hd">` | `<span class="bl-code"><b>01</b>절이름</span>` + `.bl-sp` + `.br-mark` |
| 꼬리띠 | `<footer class="bl-rf">` | `.bl-rf-name`(문서명) + `.bl-pg`(쪽번호) |
| 워터마크 | `<div class="br-watermark" data-on="…">` | 우하단에 옅게 깔리는 로고타입 |
| 진행선 | `<div id="bl-prog">` | 덱에 하나 · `<main>` 앞 |

`.br-mark` 와 `.br-watermark` 안의 자리표시자 마크업은 **손대지 않는다.**
4절의 `apply_brand.py` 가 `brand.json` 의 로고로 채운다.

`data-on` 이 지면과 **반대**인 점을 놓치기 쉽다. `data-on` 은 「이 마크가 어떤 배경 위에
앉는가」인데, 머리띠 마크가 앉는 곳은 지면이 아니라 띠이고 띠 색은 지면과 반대다.

| 지면 | 띠 색 | 머리띠 마크 | 워터마크 |
|---|---|---|---|
| 밝은 장 (기본) | 짙음 | `data-on="dark"` | `data-on="light"` |
| 어두운 장 `bl-sl--dark` | 흼 | `data-on="light"` | `data-on="dark"` |

제목의 핵심구는 `<em>` 으로 감싼다. 형광 밴드가 거기에만 걸린다.

#### 슬라이드 덱 12종 — 1920x1080 고정 지면

| 파일 | `--deck` 이름 | 용도 | 장수 |
|---|---|---|---|
| `deck-internal-report.html` | `internal` | 사내 보고 (월간) | 9 |
| `deck-weekly-report.html` | `weekly` | 조직 주간보고 | 7 |
| `deck-ax-weekly.html` | `ax` | AX 조직 1장 보고 + 부록 | 5 |
| `deck-team-weekly.html` | `team` | 팀 압축 주간보고 (2장 · 팀장 보고용) | 2 |
| `deck-exec-report.html` | `exec` | 경영진 보고 (결론 먼저) | 6 |
| `deck-allhands.html` | `allhands` | 전직원 보고 (타운홀) | 9 |
| `deck-sales-proposal.html` | `sales` | 외부 제안·영업 | 10 |
| `deck-project-report.html` | `project` | 프로젝트 착수·완료 | 9 |
| `deck-training.html` | `training` | 교육·기술 설명 | 8 |
| `deck-strategy-report.html` | `strategy` | 전략 보고 (논증형 결정 요청 · 16장) | 16 |
| `deck-report.html` | `report` | 고밀도 보고 (본문 14 + 부록 5 · 도해 중심) | 19 |
| `deck-template.html` | `catalog` | 레이아웃 19종 카탈로그 | 19 |

발표 덱이 아니라 **A4 세로 문서**가 필요하면 아래 이름을 같은 `--deck` 에 준다.
1920x1080 이 아니라 794x1123 지면이고, 검사기도 `check_doc.py` 로 다르다.

| 파일 | `--deck` 이름 | 용도 | 쪽수 |
|---|---|---|---|
| `doc-minutes.html` | `minutes` | 회의록 | 4 |
| `doc-policy.html` | `policy` | 사규·규정 | 6 |
| `doc-manual.html` | `manual` | 매뉴얼·가이드 | 6 |
| `doc-notice.html` | `notice` | 공지 (1쪽 완결) | 2 |

읽는 물건이 아니라 **화면에서 상태를 바꾸는 것**이면 웹 보드를 쓴다. 지면 크기가 없고
화면 폭에 따라 흐른다. 글자 하한이 12.5px 로 다르고 검사기도 `check_board.py` 다.
PPTX·PDF 대상이 아니다.

| 파일 | `--deck` 이름 | 용도 | 특징 |
|---|---|---|---|
| `board-task.html` | `board` | 과제 실행보드 (가장 작은 견본) | 레일 · KPI · 필터 표 · 메모 |
| `board-manage.html` | `manage` | 관리보드 (대시보드형) | 절 12 · 표 8 · 일정 격자 |
| `board-exec.html` | `execboard` | 실행보드 (항목 상태 · 메모) | 상태 알약 4단 순환 · 진행판 |
| `board-team.html` | `teamboard` | 팀보드 (칸반) | 칸반 4열 · 주차 격자 · 겹칩 |
| `board-gap.html` | `gapcheck` | 점검보드 (공백 대조) | 공백 부모 + 대응 자식 · 대조표 |

보드는 `blue-report.css` 와 `blue-web.css` 두 벌을 함께 부른다. 복사할 때 덱용 3개가
아니라 이 둘을 옮긴다.

같은 레이아웃을 쓰되 배치 순서가 용도에 맞게 다르다. 사내 보고는 다크 요약이 3번째에
있고(경영진이 앞부분만 보고 넘어간다), 외부 제안은 9번째에 있다(문제 제기부터 설득한 뒤
정리한다). 그러므로 용도가 다르면 파일도 달라야 한다.

**용도를 지시받지 못했으면 임의로 고르지 말고 사람에게 먼저 묻는다.**

복사할 때 다음 3개를 같은 폴더에 함께 둔다. 없으면 스타일이 전혀 적용되지 않는다.

```
assets/blue-report.css
assets/deck-viewer.css
assets/deck-viewer.js
```

한 파일로 만들려면 4절의 `--single-file` 을 쓴다. 그 경우 위 3개를 옮기지 않아도 된다.

### 3. 어겨선 안 되는 것

- **색은 `--br-*` CSS 변수만 쓴다.** 새 hex 값을 슬라이드에 직접 적지 않는다.
- **파이 차트 금지.** 도넛만 쓴다. `<path d="M…A…">` 로 부채꼴을 그리지 않는다.
  도넛 SVG 는 `scripts/donut.py` 로 생성한다. 각도를 손으로 계산하지 않는다.
- **문체는 개조식**(명사형 종결). `~합니다`, `~됩니다`, `~입니다` 를 쓰지 않는다.
- **슬라이드는 정확히 1920x1080.** 넘치면 행 높이를 줄인다. 축소하지 않는다.
- **글자는 24px 이상.** `%` 첨자(`.br-sup`)만 예외다.
- **데이터 마크는 배경 대비 2:1 이상.** 밝은 지면에 `--br-soft-*` 를 쓰지 않는다.
- **로고는 모든 슬라이드 우측 상단** `.br-mark` 자리에 들어간다.
  그 자리(상단 여백 띠)에 본문 콘텐츠를 붙이지 않는다.
- **예시 수치·부서명·문구는 자리표시자가 아니라 사용법 견본이다.** 실제 내용으로 바꾼다.
  바꾸지 않고 남기면 남의 회사 숫자가 그대로 발표된다.
- **기준·라이브 덱은 치수를 `rem` 으로만 적는다.** `px` 는 1px 테두리와 blur 반경만 예외다.
- **기준·라이브 덱은 머리띠·꼬리띠·쪽번호·로고·워터마크를 장마다 단다.** 하나라도 빼면
  `check_live.py` 가 실패로 잡는다. 이것이 「우리 양식으로 만들었다」와 실제로 회사 문서로
  보이는 것의 차이다.
- **기준 덱 산출물은 `apply_brand.py --deck <파일> --single-file` 로 만든다.** 견본의 로고 자리는
  「COMPANY NAME」이다. 복사해 내용만 바꾸고 끝내면 로고도 워터마크도 없다.
- **근거가 있는 수치에는 출처 칩을 단다.** 수치 옆 `<button type="button" class="bl-ev" data-ev="E1">출처</button>`,
  문서 끝 `<script type="application/json" id="bl-evidence">` 에 근거(제목·등급·사실·출처·날짜).
  등급은 A 1차 공식 · B 학술·전문 · C 언론·2차 · R 직접 조회·집계. 근거 없는 칩은 실패다.

### 4. 브랜드 적용과 출력

저장소 루트에서 실행한다. **산출물은 `decks-out/` 에 넣는다.** 이 폴더는 `.gitignore`
처리돼 있어 저장소를 더럽히지 않는다. 저장소 루트에 결과 파일을 흩어 놓지 않는다.

```bash
# HTML — 회사명·로고·저작권을 넣어 한 파일로 만든다
python .claude/skills/blue-report/scripts/apply_brand.py --brand brand/hct/brand.json --deck internal --single-file -o decks-out/deck.html

# --deck 은 위 표의 이름 또는 HTML 파일 경로. A4 문서와 웹 보드도 같은 --deck 으로 준다
#   --deck minutes   A4 회의록      --deck manage   관리보드
# 내용을 직접 편집한 덱이면 파일 경로를 준다:
#   --deck decks-out/my-deck.html

# PDF — 발표용. --notes 를 주면 발표자 노트를 마지막 장에 붙인다
python .claude/skills/blue-report/scripts/to_pdf.py decks-out/deck.html

# PowerPoint — 내용은 pptx/content.js 에 있다
node .claude/skills/blue-report/pptx/build.js --brand brand/hct/brand.json --out decks-out
```

PPTX 는 HTML 덱과 내용을 따로 들고 있다. **HTML 쪽이 기준이므로 내용을 바꿀 때는
`assets/deck-*.html` 과 `pptx/content.js` 두 곳을 함께 고친다.** 색은 두 판이
`assets/blue-report.css` 의 토큰을 같이 읽으므로 갈라지지 않는다.

한쪽만 고쳤는지는 스크립트가 잡는다. 템플릿 자체를 고쳤다면 돌린다.

```bash
python scripts/check_content_sync.py
```

슬라이드 수 · 문서명 · 발표자 노트 · 막대 · 도넛 · 표를 두 곳에서 뽑아 견주고,
어긋나면 어느 덱 몇 장 어느 항목인지 찍는다.

필요한 것(Pillow · Chromium · node_modules)은 스크립트가 스스로 받는다. 미리 설치하지
않아도 된다. 설치를 막으려면 환경변수 `BLUE_REPORT_NO_INSTALL=1` 을 준다. 그 경우
필요한 명령만 출력하고 멈춘다.

### 5. 완료 조건

```bash
# 계통마다 검사기가 다르다. 만든 것에 맞는 것을 돌린다.
python .claude/skills/blue-report/scripts/check_deck.py  decks-out/deck.html   # 슬라이드 덱
python .claude/skills/blue-report/scripts/check_live.py  decks-out/deck.html   # 기준·라이브 덱
python .claude/skills/blue-report/scripts/check_doc.py   decks-out/doc.html    # A4 문서
python .claude/skills/blue-report/scripts/check_board.py decks-out/board.html  # 웹 보드
```

`check_deck.py` 가 17항목, `check_live.py` 가 22항목을 기계로 판정한다.
`check_live.py` 의 22항목 중 여섯이 지면 크롬이다 — 머리띠 · 꼬리띠 · 쪽번호 ·
머리띠 브랜드 마크 · 워터마크 · 마크 배경 짝. 넷은 산출물이 회사 문서로 나왔는지다 —
로고 자리표시자 · 스타일 · 본문 폰트 · 지면 끝. 출처 칩이 있으면 근거에 이어지는지도 본다.
조작판이 꼬리띠의 문서명·쪽번호를 덮는지는 1600·760·400px 세 폭에서 잰다.

check_deck.py 가 판정하는 것:

문체 · 파이 차트 금지 · 도넛 dasharray 검산 · 토큰 밖 raw hex · 슬라이드 크기 ·
최소 글자 크기 · 데이터 마크 대비 · 본문 겹침 · 브랜드 마크 존재 · 마크와 본문 겹침 ·
배경 워터마크 배치(표지 제외) · 배경 밝기와 로고 변형 일치 · 워터마크 자산 구분 ·
지시선 주석 잘림.

**실패가 0 이 아니면 완료가 아니다.** 실패가 남은 채로 "완료"라고 쓰지 않는다.

덱 하나가 아니라 템플릿·스크립트·문서를 고쳤다면 저장소 전체를 본다. GitHub Actions 가
push·PR 마다 이 한 줄을 그대로 돌린다.

```bash
python scripts/verify_repo.py
```

`주의`는 허용된다. 도넛을 쓰지 않은 덱에서 나오는 정상 결과다.

레이아웃 검수까지 하려면 `--shots 폴더명` 을 붙여 슬라이드별 PNG 를 남기고 눈으로 본다.
겹침은 스크립트가 잡지만 어색한 여백은 잡지 못한다.

### 5-1. HTML 덱은 발표에 쓴다

만든 HTML 을 넘길 때 조작법을 함께 알린다. 모르면 발표를 못 한다.

| 키 · 버튼 | 하는 일 |
|---|---|
| `F` · 「발표」 | 전체화면 발표 모드 — 버튼과 노트가 사라진다 |
| `←` `→` `Space` · 클릭 | 슬라이드 넘김 |
| `Esc` | 발표 모드 나가기 |
| `N` · 「노트」 | 발표자 노트 |
| 「목록」 | 전 슬라이드 세로 나열 (검수용, 발표용 아님) |

**「목록」을 발표용으로 안내하지 않는다.** 세로 스크롤이라 발표가 되지 않는다.

### 6. 보고 형식

보고는 **한국어로** 쓴다. 다음을 반드시 포함한다.

- 실행한 명령 (그대로)
- `check_deck.py` 결과의 통과 / 주의 / 실패 수
- 산출물 파일 경로
- 바꾸지 못했거나 확신이 없는 내용

검사를 돌리지 않았으면 그 사실을 쓴다. 돌린 것처럼 쓰지 않는다.

---

## 참고 — 이 저장소 밖에서 쓸 때

다른 프로젝트 폴더에서 작업한다면 스킬 폴더를 통째로 복사한다. `--target` 을 생략하면
사용자 스킬 폴더(`~/.claude/skills/blue-report`)에 설치되어 그 PC 의 모든 프로젝트에서 쓸 수 있다.

```bash
python scripts/install_blue_report_skill.py                      # 사용자 스킬 폴더
python scripts/install_blue_report_skill.py --target <프로젝트경로>   # 특정 프로젝트
```

Claude Code 라면 저장소를 클론하지 않고 플러그인으로 받을 수도 있다. PC 마다 한 번만
실행하면 된다.

```bash
claude plugin marketplace add hctinno/blue-report
claude plugin install blue-report@blue-tools
```

파일도 줄 수 없는 환경(웹 UI 등)이라면 `.claude/skills/blue-report/README.md` 내용을
통째로 붙여넣고 "이 규격을 따라 1920x1080 HTML 슬라이드를 만들어라"라고 지시한다.
다만 이 경우 완성된 덱 템플릿과 검증 스크립트가 없어 품질이 떨어진다.
