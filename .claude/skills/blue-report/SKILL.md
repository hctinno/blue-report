---
name: blue-report
description: "사내 보고서·발표 덱·A4 문서·웹 보드를 회사 공용 양식으로 만든다. \"보고서 템플릿\", \"사내 보고서 템플릿\", \"회사 양식\", \"우리 템플릿\", \"HCT 템플릿\", \"블루 리포트\", \"AX 리포트 스타일\", \"딥 코발트 리포트\", \"Deep Cobalt\" 중 무엇으로 부르든 이 스킬을 쓴다. 사용자가 보고서·슬라이드·덱·발표자료·회의록·공지·매뉴얼·보드·대시보드·실행보드·칸반·점검표·현황판을 요청하면서 템플릿·양식·서식을 활용하라고 하면 반드시 사용한다. 새 스타일을 만들지 않는다. **새 보고서는 기준 덱 live-standard.html(--deck standard)을 복사해 내용만 바꾼다** — 머리띠·꼬리띠·로고·워터마크가 장마다 붙어 있고 검사기가 그것을 강제한다. 1920x1080 HTML 슬라이드 덱 12종(전략 보고·경영진 보고·사내 보고·주간보고·고밀도 보고 등, 레이아웃 19종), A4 문서 4종(회의록·사규·매뉴얼·공지), 화면에서 상태를 바꾸는 웹 보드 5종(관리보드·실행보드·팀보드·점검보드), 고정 지면 없이 화면 비율을 따라가는 기준 덱 1종과 라이브 덱 1종, FCC/KC 보고서 14종, 코발트·딥네이비 팔레트, 도넛·막대 차트 규칙, 개조식 문체를 강제하고 HTML·PDF·PPTX·DOCX 로 내보낸다. 기준 덱은 사내 발표 덱 짜임새(표지 발표자 블록·보고 요지·로드맵·출처 칩과 근거 패널)를 갖는다. 뷰어는 단계 전개·펼침·가로 보기·메모·발표 모드·레이저·대본 창·숫자 점프를 지원한다."
---

# 블루 리포트

사내 공용 발표 슬라이드 디자인 시스템. 색·타입·차트·문체 규칙이 서로 맞물려 있어 하나만
어겨도 덱 전체가 어색해진다. 아래 순서를 그대로 따른다.

## 1. 먼저 읽을 것

- `assets/blue-report.css` — 색·타입·간격 토큰과 파운데이션 클래스. **색은 여기 토큰으로만 쓴다.**
- `assets/deck-template.html` — 슬라이드 10종 완성본. 새 덱은 이 파일을 복사해서 시작한다.
- `references/rules.md` — 차트·문체·레이아웃 규칙 전문. 차트를 그리기 전에 반드시 읽는다.

## 2. 새 덱 만들기

**먼저 용도를 정한다.** `deck-template.html`은 레이아웃 카탈로그이지 완성 덱이 아니다.
아무거나 골라 쓰면 슬라이드 순서가 목적에 맞지 않는다.

판단 기준은 하나다 — **요청에서 용도가 읽히면 묻지 말고 고른다. 읽히지 않을 때만 묻는다.**

- 읽힐 때 → 고른 덱과 이유를 한 줄로 밝히고 바로 만든다. 뻔한 것을 되묻지 않는다.
  예: "월간 실적" · "월간 업무 보고" · "사내 보고" → `internal`
  "주간 보고" · "이번 주 현황" · "조직 주간보고" → `weekly`
  "팀 주간" · "파트 주간보고" · "팀장 보고" · "두 장으로" → `team`
  "한 장으로" · "1장 보고" · "AX 조직" · "요약만" → `ax`
  "경영진 보고" · "임원 보고" · "대표 보고" · "결론부터" → `exec`
  "전직원" · "타운홀" · "전사 공유" · "전사 발표" → `allhands`
  "제안서" · "고객사에 보낼" · "영업" · "견적" → `sales`
  "착수 보고" · "완료 보고" · "킥오프" · "산출물" → `project`
  "교육 자료" · "사내 강의" · "온보딩" · "설명 자료" → `training`
  "전략 보고" · "과제 재개" · "투자 결정" · "대안 비교" · "자체개발 vs 외주" → `strategy`
  "부록까지" · "근거 자료 붙여" · "예상 질문" · "도해로" · "제대로 된 보고서" → `report`
  "보드" · "체크리스트 화면" · "상태 갱신" → `board`
  "관리보드" · "대시보드" · "전사 현황" · "여러 축을 한 화면" → `manage`
  "실행보드" · "항목마다 상태" · "메모 남기며" · "매일 보는 목록" → `execboard`
  "팀보드" · "칸반" · "주간 회의 화면" · "지금 걸린 것만" → `teamboard`
  "점검보드" · "공백 점검" · "빠진 것 찾기" · "대조 점검" → `gapcheck`

  발표가 아니라 인쇄해 철할 문서면 A4 쪽으로 간다.
  "회의록" · "미팅 노트" · "회의 결과" → `minutes`
  "사규" · "규정" · "지침" · "개정" → `policy`
  "매뉴얼" · "가이드" · "절차서" · "사용법" → `manual`
  "공지" · "안내문" · "알림" · "한 쪽으로" → `notice`

  주기로 가른다 — 매주면 `weekly`, 매달이면 `internal`.
  받는 사람으로 가른다 — 임원 한 명이면 `exec`, 전 직원이면 `allhands`, 팀장이면 `team`.
  결론을 먼저 놓으면 `exec`, 근거를 밟아 올라가 결정을 받으면 `strategy`.
  부록에 근거를 붙여야 하면 `report` — 질문이 많이 나올 자리에 쓴다.
  발표하지 않고 **고쳐 가며 쓰는** 물건이면 `board` — 덱도 A4 도 아니다.
- 읽히지 않을 때 → **추천을 붙여서** 묻는다. 선택지만 나열하지 않는다.
  예: "사내 공유용이면 사내 보고, 외부에 보낼 거면 제안서 쪽이 맞다. 어느 쪽인가?"
- 내용을 받아 보니 고른 덱과 안 맞으면 → 그때 말하고 바꾼다. 말없이 다른 구성을 쓰지 않는다.

| 용도 | `--deck` | 파일 | 장수 |
|---|---|---|---|
| 사내 보고 (월간) | `internal` | `deck-internal-report.html` | 9 |
| 조직 주간보고 | `weekly` | `deck-weekly-report.html` | 7 |
| AX 조직 1장 보고 + 부록 | `ax` | `deck-ax-weekly.html` | 5 |
| 팀 압축 주간보고 | `team` | `deck-team-weekly.html` | 2 |
| 경영진 보고 (결론 먼저) | `exec` | `deck-exec-report.html` | 6 |
| 전직원 보고 (타운홀) | `allhands` | `deck-allhands.html` | 9 |
| 외부 제안·영업 | `sales` | `deck-sales-proposal.html` | 10 |
| 프로젝트 착수·완료 | `project` | `deck-project-report.html` | 9 |
| 교육·기술 설명 | `training` | `deck-training.html` | 8 |
| 전략 보고 (논증형 결정 요청) | `strategy` | `deck-strategy-report.html` | 16 |
| 고밀도 보고 (본문+부록 2부) | `report` | `deck-report.html` | 19 |
| 레이아웃 카탈로그 | `catalog` | `deck-template.html` | 19 |

**A4 문서 4종.** 발표 덱이 아니라 인쇄해 철하는 물건이다. 794x1123(A4 세로),
머리말에 로고·꼬리말에 회사명이 쪽마다 들어간다. `--deck` 에 같은 방식으로 넘긴다.

| 용도 | `--deck` | 파일 | 특징 |
|---|---|---|---|
| 회의록 | `minutes` | `doc-minutes.html` | 결정사항 · 액션아이템 표 분리 |
| 사규·규정 | `policy` | `doc-policy.html` | 조·항·호 · 개정 이력 · 결재란 |
| 매뉴얼·가이드 | `manual` | `doc-manual.html` | 목차 · 절차 단계 · 캡처 자리 |
| 공지 | `notice` | `doc-notice.html` | 1쪽 완결 |

A4 문서는 `check_deck.py` 가 아니라 `check_doc.py` 가 판정한다(9항목).

**웹 보드 5종.** 슬라이드도 A4 도 아닌 제3의 계통이다. 지면 크기가 없고 화면 폭에
따라 흐르며, **읽는 물건이 아니라 상태를 바꾸는 화면**이다. PPTX·PDF 대상이 아니다.

| 용도 | `--deck` | 파일 | 특징 |
|---|---|---|---|
| 과제 실행보드 (가장 작은 견본) | `board` | `board-task.html` | 레일 내비 · KPI 스트립 · 필터 표 · 메모 |
| 관리보드 (대시보드형) | `manage` | `board-manage.html` | 절 12 · 표 8 · 일정 격자 · 가로 막대 |
| 실행보드 (항목 상태 · 메모) | `execboard` | `board-exec.html` | 상태 알약 4단 순환 · 설비 진행판 · 주차 막대 |
| 팀보드 (칸반) | `teamboard` | `board-team.html` | 칸반 4열 · 주차 격자 · 상세 겹칩 |
| 점검보드 (공백 대조) | `gapcheck` | `board-gap.html` | 공백 부모 + 대응 자식 · 비율 띠 · 대조표 · 단계 목록 |

뒤 네 벌은 사내에서 따로 만들어 쓰던 보드를 이 계통으로 옮긴 것이다. 넷이 각자
만들어 쓰던 부품(공백 카드 · 칸반 · 단계 목록 · 대조표 · 비율 띠 · 요일 카드 ·
접기 · 겹칩)은 전부 `blue-web.css` 한곳으로 모았다.

보드는 `blue-report.css` + `blue-web.css` 두 파일을 함께 부른다. 글자 하한이
12.5px 이고 `check_board.py` 가 판정한다(11항목).

보드 내용이 JS 데이터에 들어 있으면 원문만 보는 문체 검사가 한 자도 못 본다 —
`<script>` 안은 규칙상 걷어내기 때문이다. 11번째 항목이 **그려진 뒤의 DOM** 을
한 번 더 읽어 실제로 화면에 뜬 글자를 판정한다.

```bash
# 회사 정보까지 한 번에 (권장)
python3 scripts/apply_brand.py --brand brand.json --deck internal --single-file -o 보고서.html

# 또는 파일을 직접 복사해 손으로 편집
cp assets/deck-internal-report.html <작업경로>/deck.html
cp assets/blue-report.css assets/deck-viewer.css assets/deck-viewer.js <작업경로>/
```

템플릿의 `<div class="br-frame">` 블록이 슬라이드 1장이다. 필요한 종류만 남기고 지우거나,
같은 블록을 복사해 늘린다. 12종은 다음과 같다.

| # | 슬라이드 | 배경 | 쓰는 자리 |
|---|---|---|---|
| 01 | 표지 | `--br-cover` | 문서 첫 장 |
| 02 | 목차 | `--br-page` | 파트 4~5개까지 |
| 03 | 파트 간지 | `--br-cover` | 파트 시작 |
| 04 | 핵심 정리 | `--br-dark` | 파트 끝. 카드 6개가 상한 |
| 05 | 단일 수치 강조 | `--br-page` | 한 슬라이드 = 한 주장 |
| 06 | 도넛 차트 | `--br-page` | 구성비 3~5구간 |
| 07 | 막대 차트 | `--br-page` | 순위·비교 7구간까지 |
| 08 | 비교 2열 | `--br-page` | 전후·A안B안·평균대비 |
| 09 | 지표 표 | `--br-page` | 과제·지표 목록. 행 7개가 상한 |
| 10 | 3단계 로드맵 | `--br-page` | 실행 계획 |
| 11 | 일정 타임라인 | `--br-page` | 기간 병행과 마일스톤 |
| 12 | 순환 고리 | `--br-page` | 회차가 되돌아옴. 칸 3~6개 · `diagram.py cycle` |
| 13 | 통과 관문 | `--br-page` | 직렬 조건. 관문 2~5개 · `diagram.py gate` |
| 14 | 단계 계단 | `--br-page` | 단마다 기준 상승. 단 3~6개 · `diagram.py stair` |
| 15 | 연표 | `--br-page` | 실적/계획 분기. 시점 3~8개 · `diagram.py track` |
| 16 | 구간 블록 | `--br-page` | 시간축 위 구간 · `diagram.py interval` |
| 17 | 결정 요청 표 | `--br-page` | 미결 시 영향 열 필수. 행 4개가 상한 |
| 18 | 부록 간지 | `--br-cover` | 본문/부록 경계. 이후 지면에 `data-apx` |
| 19 | 마무리 CTA | `--br-cover` | 행동 하나만 제시 |

읽고 인쇄하는 문서(주간보고 등)는 `#stage` 에 `data-no-anim` 을 주어 등장 효과를 끈다.
발표용 덱은 켠 채로 둔다.

**쪽번호와 문서명은 뷰어가 자동으로 채운다.** 푸터(`.br-footer`)는 비워 두고 숫자를 적지 않는다.
문서명은 `#stage`의 `data-deck-title` 한 곳에서 읽는다. 발표자 노트는 `.br-frame`의
`data-notes` 속성에 적고 뷰어에서 `N` 키로 본다.

## 3. 차트와 도해는 반드시 스크립트로 만든다

각도와 좌표를 손으로 적으면 수치와 그림이 어긋난다. 더 큰 문제는 항목 수가
바뀔 때다 — 손으로 찍은 좌표에 칸을 하나 끼워 넣으면 간격이 어긋난다.

```bash
# 도넛 — 구간 퍼센트를 넘기면 SVG와 범례가 나온다
python3 scripts/donut.py --r 110 --w 48 --labels "일상 사용,주 1~2회,미사용" 58.4 27.9 13.7

# 막대 구간이 6개 이상이면 대비를 만족하는 램프를 생성한다
python3 scripts/palette.py --steps 7

# 팔레트 대비표
python3 scripts/palette.py --check
```

**구조 도해 5종.** 좌표가 항목 순번의 1차식으로 떨어지는 것만 생성한다.
출력을 슬라이드에 그대로 붙인다.

```bash
python3 scripts/diagram.py cycle 선정,제작,코칭,공유,자산화 --back "한 회차 8주"
python3 scripts/diagram.py gate 기술검증,현장적용,비용회수,조직정착 --out 성과
python3 scripts/diagram.py stair 인식,시범,확산,정착
python3 scripts/diagram.py track 2024,2025,2026,2027 --done 2 --unit 년
python3 scripts/diagram.py interval "내부 챔버|8-9:점검:준비,10-12:시험:매뉴얼" --domain 0 24
```

스크립트가 검산까지 한다 — 라벨이 칸에 넘치면 경고하고, 구간이 겹치면 알리고,
구간 종류가 램프 5색을 넘으면 실패시킨다. **경고를 무시하고 붙이지 않는다.**

`viewBox` 를 본문 폭 1728 에 1:1 로 맞춰 두었다. SVG 를 좁은 칸에 넣으려고 폭을
줄이면 안 글자가 같이 줄어 24px 하한을 깬다. 좁혀야 하면 `diagram.py` 의 `W` 를 바꾼다.

**개념 흐름도는 생성하지 않는다.** 좌표가 값에서 나오지 않기 때문이다. 손으로
그리되 `viewBox` 를 1728 기준으로 잡고, 글자는 24px 이상, 색은 `--br-*` 만 쓴다.

### 밀도 높은 지면에 붙이는 두 부품

- `.br-ribbon` — 지면 맨 아래 결론 한 줄. 「무엇을 읽어야 하나」를 닫는다.
  `margin-top:auto` 가 이미 들어 있으므로 슬라이드의 마지막 형제로 둔다.
- `.br-conf` — 확신도 칩 4종(`--fixed` 확정 · `--plan` 제안 · `--open` 협의필요 ·
  `--none` 미정). `.br-status` 가 진행 상태를 말한다면 이쪽은 근거의 굳기를 말한다.
  **어휘를 넷으로 고정한다.** 늘리면 읽는 사람이 등급을 구분하지 못한다.

## 4. PDF로 내보내기

사내 배포·이메일 첨부에는 PDF를 만든다. 슬라이드 1장이 1페이지, 20in x 11.25in(16:9)이며
텍스트가 실제 글자로 남는다.

```bash
python3 scripts/to_pdf.py 보고서.html -o 보고서.pdf --notes
```

## 5. PowerPoint 판이 필요하면

파워포인트로 직접 편집해야 하는 사람이 있을 때만 만든다. 기본은 HTML 이다.

```bash
node pptx/build.js --brand <brand.json> --out <폴더> [--deck internal]
```

**설치를 사용자에게 시키지 않는다.** 스크립트가 실행될 때 없는 것만 골라 스스로 받는다
(Pillow · Playwright · Chromium · pptxgenjs). "먼저 npm install 하세요" 같은 안내를 하지 않는다.
자동 설치를 막으려면 `BLUE_REPORT_NO_INSTALL=1` 을 준다. 상태만 보려면
`python3 scripts/ensure_deps.py`.

색·크기는 `blue-report.css` 토큰을 읽는다. 애니메이션은 없고, 폰트는 맑은 고딕·Arial 로 내린다.
도넛과 막대는 PowerPoint 네이티브 차트라 값을 직접 고칠 수 있다.
덱 내용은 `pptx/content.js` 에 있으며 HTML 덱과 함께 고친다.

만든 뒤에는 반드시 검증한다.

```bash
python3 <pptx 스킬>/scripts/office/validate.py 결과.pptx
```

## 6. 만들고 나면 반드시 점검한다

```bash
python3 scripts/check_deck.py <작업경로>/deck.html --shots out/
```

11개 항목(개조식 문체, 파이 금지, 토큰 밖 raw hex, 슬라이드 크기 1920x1080, 24px 하한,
데이터 대비 2:1, 본문 영역 겹침, 브랜드 마크 존재, 마크와 본문 겹침, 로고 변형과 배경 밝기,
도넛 검산)을 검사하고 슬라이드별 PNG를 남긴다.

**`실패`가 0이 아니면 완료가 아니다.** `주의`는 허용된다 — 도넛을 쓰지 않은 덱에서
도넛 검산 항목이 `주의`로 나오는 것이 정상이다.
**실패가 0이어도 PNG를 눈으로 확인한다.** 겹침과 어색한 여백은 스크립트가 잡지 못한다.

## 7. 절대 어기지 않을 것

- 배경은 밝은 지면 `#f4f6f8` 1개 + 다크면 `#071b45`(표지·간지), `#101827`(핵심 정리) 2개까지. 그 외 장식색 금지.
- 파이 차트 금지. 도넛만. 손으로 적은 `<path d="M…A…">` 금지.
- 밝은 지면의 데이터 마크에 `--br-soft-*`를 쓰지 않는다. 대비 2:1에 미달한다.
- 24px 미만 텍스트 금지. 예외는 `%` 첨자(`.br-sup`)뿐.
- 슬라이드 본문은 명사형으로 끝낸다. 존댓말(`~합니다`)과 평서형(`~한다` · `~없다`) 모두 금지.
  설문 문항 원문만 예외. 발표자 노트는 대상이 아니며 `~한다` 형으로 적는다.
- 제목 밑줄, 장식용 색 띠, 블루프린트 `+` 코너 마크를 쓰지 않는다.

## 8. 회사 정보와 로고

회사명·연락처·저작권·로고는 손으로 고치지 않는다. `brand.json`에 적고 스크립트로 적용한다.

```bash
cp assets/brand.example.json ./brand.json     # 편집 후
python3 scripts/apply_brand.py --brand ./brand.json --single-file -o ./deck.html
```

- **마크는 모든 슬라이드 우측 상단**에 같은 자리로 들어간다(`.br-mark`). 표지도 본문도 같다.
  우측 상단 여백 띠에 콘텐츠를 붙이지 않는다.
- **로고는 두 벌이 필요하다.** 배경이 오가므로 한 벌로는 한쪽에서 안 보인다.
  `logo`는 다크·코발트 배경용 흰색 녹아웃, `logoOnLight`는 밝은 지면용 원색이다.
  `python3 scripts/make_logo_variants.py 로고.png --name mylogo` 가 원본 한 장에서
  `mylogo-white.png`(→ `logo`)와 `mylogo-color.png`(→ `logoOnLight`)를 만든다.
- `logoHeight`는 마크 높이(px). 기본 40, 권장 32~48. 키우면 본문과 겹쳐 검사가 실패한다.
- 로고는 PNG·JPG·SVG·WEBP를 data URI로 박는다. 완성 HTML 하나만 들고 다니면 된다.
- 연락처가 없으면 `email`·`website`·`phone`을 빈 문자열로 둔다. 해당 줄이 통째로 사라진다.
- `logo`·`logoOnLight`가 `null`이면 `wordmark` 텍스트가 들어간다. 한글이면 폰트를
  프리텐다드 한 벌이 한글과 라틴을 모두 담으므로 폰트가 갈리지 않는다. 색은 배경에 맞춰
  밝은 면 브랜드 파랑·어두운 면 흰색으로 전환한다.
- 항상 원본 템플릿에서 새로 만들므로 몇 번 실행해도 결과가 같다.

사내 폰트가 확정되면 `blue-report.css`의 `--br-font-kr`, `--br-font-num`, `--br-font-label`
첫 패밀리만 교체한다.

## 9. 다른 프로젝트에서 쓰기

이 스킬이 저장소 안에 있으면 그 저장소에서만 로드된다. 모든 프로젝트에서 쓰려면 한 번 설치한다.

GitHub 플러그인으로 받는 것이 기본이다. 저장소를 클론하지 않아도 되고 갱신이 자동이다.
새 PC 에서 하는 일은 아래 한 줄이 전부다.

```bash
claude plugin marketplace add hctinno/blue-report && \
claude plugin install blue-report@blue-tools
```

설정 파일(`extraKnownMarketplaces` · `enabledPlugins`)에 적어 두는 것만으로는 설치되지 않는다.
`install` 은 PC 마다 한 번 실행해야 한다.

GitHub 에 접근할 수 없으면 파일 복사로 설치한다.

```bash
python3 <저장소>/scripts/install_blue_report_skill.py --dry-run   # 바뀔 내용 확인
python3 <저장소>/scripts/install_blue_report_skill.py             # ~/.claude/skills/ 로 설치
```

어느 쪽이든 설치 후 Claude Code 세션을 새로 시작해야 읽힌다.
