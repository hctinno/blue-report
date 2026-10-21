# 블루 리포트 디자인 시스템

사내 공용 발표 슬라이드 · 보고서 디자인 시스템. 딥 코발트 계열 단일 팔레트, 1920×1080 HTML 슬라이드,
개조식 문체를 하나로 묶은 규격이다.

이 문서는 **자기완결 사양서**다. 다른 AI 도구(ChatGPT, Gemini, v0, Cursor 등)에 이 파일 전체를
붙여넣으면 별도 자료 없이 같은 결과를 만들 수 있다.

---

## 제작 전 기획과 이미지 선택

이 문서는 디자인·구성 요소 규격이다. 새 발표자료는 먼저 SKILL.md와 references/business-presentation-intake.md에 따라 목적·청중·용도·형식·분량·효과를 구체화한다.
references/visual-style-selection.md에 따라 같은 내용의 표지·본문을 PNG로 렌더링하고 사용자의 선택 또는 명시적 위임을 받은 뒤 전체 제작으로 이어간다.
양식 이름을 자동으로 고르는 것은 이 기획·선택 절차를 생략한다는 의미가 아니다.

## 파일 구성

```
blue-report/
├─ SKILL.md                    Claude Code용 스킬 정의 ("블루 리포트" 트리거)
├─ README.md                   이 문서 — 다른 AI 도구에 붙여넣는 자기완결 사양서
├─ assets/
│  ├─ blue-report.css          토큰(색·타입·간격) + 파운데이션 + 애니메이션
│  ├─ blue-doc.css             A4 문서 파운데이션 (토큰은 blue-report.css 를 씀)
│  ├─ doc-viewer.css           문서 뷰어 껍데기
│  ├─ doc-viewer.js            쪽번호 자동 · 축척 · 인쇄
│  ├─ doc-minutes.html         회의록 2쪽
│  ├─ deck-viewer.css          뷰어 껍데기 (디자인 시스템 아님)
│  ├─ deck-viewer.js           넘김 · 축척 · 전체화면 발표 · 쪽번호 자동 · 노트
│  ├─ board-manage.html        관리보드 (웹 보드)
│  ├─ blue-live.css            라이브 계통 — 배율 · 띠 · 부품 38종 · 움직임 12계열 · 아이콘 135종
│  ├─ live-viewer.js           라이브 엔진 — 넘김 · 단계 · 쪽 이동 · 발표 · 레이저 · 대본 창 · 겹창 · 위젯
│  ├─ live-standard.html       기준 덱 15장 — 새 보고서의 출발점
│  ├─ live-patterns.html       패턴첩 63장 + 응용 견본 — 디자인 언어 용례(내용은 가상)
│  ├─ blue-pattern.css         패턴 장(.xf) 본문 CSS — 패턴첩 장을 쓰는 덱이 함께 부른다
│  ├─ live-catalog.html        라이브 부품 카탈로그 52장 — 그대로 · 고쳐 · 참고해 쓴다
│  ├─ archive/                 보관 양식 — 고정 지면 덱 12종(PPTX 원본) · A4 3종 · 보드 4종 · 브리핑 · FCC/KC
│  ├─ LICENSE-Lucide.txt       아이콘 저작권 고지 (ISC · MIT)
│  └─ brand.example.json       회사명·연락처·로고 설정 견본
├─ MOTION.md                  효과 라이브러리 — 요청 시 고르는 연출 패턴 · 단일 효과 22종 · 단계 흐리게
├─ DESIGN.md                  발표 덱 디자인 규칙 — 톤 · 위계 · 그릴 것 · 움직임 절제 · 토큰. 먼저 읽는다
├─ references/
│  ├─ rules.md                 차트 계산법 · 레이아웃 체크리스트 · 문체 규칙 전문
│  └─ decisions/                규격을 바꾼 근거(실측·대조) 원본. README.md 가 색인이다
├─ pptx/                       PowerPoint 판 생성기
│  ├─ tokens.js                blue-report.css 의 토큰을 읽어 온다 (색 값 중복 없음)
│  ├─ layouts.js               카드 · 칩 · 머리말 · 꼬리말 등 원자 helper
│  ├─ slides.js                슬라이드 종류별 생성기 11종
│  ├─ content.js               용도별 덱 11종의 내용
│  └─ build.js                 실행 진입점
└─ scripts/
   ├─ donut.py                 도넛 SVG 생성 (각도 손계산 금지 · --live 는 라이브 덱용)
   ├─ palette.py               N단계 램프 생성 + 대비 검증
   ├─ check_deck.py            덱 자동 점검 17항목 + 슬라이드별 PNG
   ├─ check_doc.py             A4 문서 점검 9항목 + 쪽별 PNG
   ├─ check_live.py            라이브 덱 점검 30항목 (엔진 기동 · 근거 JSON · 단계 · 클래스 · 세로 넘침 · 맞춤 CSS · 본문 표현 · 움직임 절제)
   ├─ make_icons.py            Lucide 아이콘 → blue-live.css 마스크 (--check 는 오프라인)
   ├─ make_font_subset.py      Pretendard 서브셋 (한글 · 라틴 · 기호)
   ├─ ensure_deps.py           필요한 것을 스스로 갖춘다 (수동 설치 불필요)
   ├─ apply_brand.py           회사 정보·로고를 덱에 일괄 적용
   ├─ to_pdf.py                덱 HTML → 발표용 PDF (슬라이드 1장 = 1페이지)
   ├─ make_logo_variants.py    흰 배경 로고 → 투명 원색판 + 흰색 녹아웃
   └─ build_single_file.py     CSS 인라인 단일 파일 빌드
```

설치기 `install_blue_report_skill.py`는 이 저장소의 `scripts/`에 있다.

### 고르는 양식 — 넷

| 무엇을 만드나 | `--deck` | 파일 |
|---|---|---|
| 보고서 · 발표 덱 (기본) | `standard` | `assets/live-standard.html` — 「6-3」 |
| 본문 디자인 기준 | `patterns` | 문법 `references/design-language.md` · 용례 `assets/live-patterns.html` — 베끼지 않고 응용 |
| 부품 재사용 · 참고 | `livecatalog` | `assets/live-catalog.html` — 「6-3」 |
| 회의록 (A4) | `minutes` | `assets/doc-minutes.html` |
| 고쳐 가며 쓰는 현황판 | `manage` | `assets/board-manage.html` |

발표·보고는 용도가 달라도 전부 기준 덱이다. 아래 고정 지면 덱 표와 A4·보드의 나머지는
`assets/archive/` 에 **보관**했다 — 이름으로 부르면 그대로 만들어지고 검사도 같지만, 사용자가
이름을 짚거나 PowerPoint 파일이 꼭 필요할 때만 쓴다. 보관 파일은 CSS·뷰어를 `../` 로 부르므로
손으로 복사하지 말고 `apply_brand.py` 로 만든다.

### 보관 고정 지면 덱 (`assets/archive/`)

`archive/deck-template.html`은 레이아웃 19종을 모아 둔 **카탈로그**다. 각 덱은 슬라이드 순서와
내용 골격이 그 용도에 맞춰져 있다. PPTX 빌드(`pptx/content.js`)가 이 덱들과 내용을 맞춘다.

| 용도 | 파일 | 장수 | 구성 |
|---|---|---|---|
| 사내 보고 (월간) | `deck-internal-report.html` | 9 | 표지 · 목차 · **요약(다크)** · 지표 표 · 막대 · 비교 2열 · 최대 이슈 · 타임라인 · 결정 요청 |
| 조직 주간보고 | `deck-weekly-report.html` | 7 | 표지 · **요약(다크)** · 조직별 표 · 막대 · 지난주 대비 2열 · 요일 타임라인 · 지원 요청 |
| AX 조직 1장 보고 | `deck-ax-weekly.html` | 5 | **한 장 보고(문서형)** · 단계 표 · 자원 표 · 병목 · 요일 타임라인 |
| 팀 압축 주간보고 | `deck-team-weekly.html` | 2 | **이번 주·다음 주 표(문서형)** · 부록(상세 표 + 특이사항 2열) |
| 경영진 보고 | `deck-exec-report.html` | 6 | 표지 · **결론(다크)** · 부문 막대 · 도넛 · 최대 위험 · 결정 요청 |
| 전직원 보고 (타운홀) | `deck-allhands.html` | 9 | 표지 · 오늘 이야기할 것 · **한 문장(다크)** · 달라진 것 · 오해 풀기 · 부서별 타임라인 · 오늘 가져갈 것 · 할 일 2건 · 마무리 |
| 외부 제안·영업 | `deck-sales-proposal.html` | 10 | 표지 · 목차 · 문제 · 도넛 · 3단계 · 효과 · 사례 표 · 일정 · 요약(다크) · CTA |
| 프로젝트 착수·완료 | `deck-project-report.html` | 9 | 표지 · 목차 · 범위 2열 · 타임라인 · 산출물 표 · 달성 막대 · 미달 · 판정(다크) · 승인 요청 |
| 교육·기술 설명 | `deck-training.html` | 8 | 표지 · 학습 목표 · 3단계 절차 · 방식 비교 · 도넛 · 체크리스트 표 · 요약(다크) · 다음 학습 |
| 전략 보고 (논증형 결정 요청) | `deck-strategy-report.html` | 16 | 표지 · 관점 대비 · 기준 정의 · 지표 표 · 도넛 · 로드맵 · 단일 수치 · 요약(다크) · 결정 요청 |
| 고밀도 보고 (본문+부록 2부) | `deck-report.html` | 19 | **본문 14** — 표지 · 목차 · 파트 간지 · 인식 대조 · 구간 블록 · 관문 · 대안 표 · 단일 수치 · 연표 · 순환 고리 · 요약(다크) · 결정 요청 · 마무리<br>**부록 5** — 간지 · 용어 · 부서별 표 · 도넛 · 예상 질문 |

용도가 요청에 드러나면 그대로 고르고, 드러나지 않을 때만 추천을 붙여 묻는 것이 기본 동작이다.
판단 기준은 `SKILL.md` 2절에 있다.

**AX 덱은 1장이 보고서 전부다** — 뒤 4장은 부록이며 질문이 나온 항목만 편다. 간지를 두지 않아 부록이 바로 이어진다.

한 장의 뼈대는 **업무 카테고리 × 이번 주·다음 주** 표다. 주간보고의 본체가 그 대조이기 때문이다.
그 위에 지표 4개를 한 줄 띠로 얹는데, 신생조직 보고를 받는 관리자의 질문에 1:1로 대응한다 —
①언제 성과가 나오나(첫 성과 시점) ②될 것 같나(파이프라인) ③사람·돈(인력·예산) ④내가 뭘(결정 요청).
**리스크는 따로 두지 않는다** — 해당 업무 행의 상태 칩이 말한다.
조판은 **문서형**이다. 카드·라운드를 쓰지 않고 왼쪽 라벨 열과 괘선으로만 구획한다.
다른 덱은 카드 조판을 쓰므로 이 덱만 다르다 — 한 장에 밀도를 높이면서도 대시보드처럼
보이지 않게 하려는 의도다. 색과 타입은 `--br-*` 토큰 그대로다.

**팀 압축 주간보고는 AX 덱을 2장으로 더 줄인 것이다.** 파트·소규모 팀이 팀장에게
매주 올리는 보고용이며, 부록이 4장이 아니라 1장이다. 1장은 **업무 × 이번 주·다음 주**
표만 둔다 — 지표 띠도, 결정 요청도 없다. 상세와 특이사항은 질문이 나올 때만 펴는
2장 부록으로 미룬다. 2장은 좌우 2열로 나뉜다: 왼쪽은 담당·진척을 더한 상세 표,
오른쪽은 그 주에 발생한 특이사항을 라벨(주의·지연)과 함께 적는다 — AX 덱의
「결정 요청」과 같은 라벨 열 + 괘선 조판이다. 조판은 AX 덱과 같은 문서형이다.

**경영진 보고에는 목차를 두지 않는다.** 6장이 상한이고, 6장짜리 보고에 목차를 넣으면
목차가 전체의 6분의 1이 된다. 결론이 두 번째 장이고 마지막 장은 반드시 결정 요청이다.
**나쁜 소식을 한 장 넣는다** — 없으면 신뢰를 잃는다. 애니메이션은 끈다(`data-no-anim`).

**전직원 보고에는 오해 풀기 장이 있다.** 실제로 들어온 걱정을 그대로 적고 얼버무리지
않는다. 이 장을 빼면 복도에서 소문으로 돈다. 한 장에 담는 항목 수를 경영진 보고보다
적게 잡는다 — 뒷줄에서도 읽혀야 한다. 발표 자리이므로 애니메이션은 켠 채로 둔다.

**진척률만 적지 않는다.** 진척률은 팀이 스스로 매긴 노력의 양이라 받는 사람이 판단 기준으로
쓸 수 없다. 관문 날짜를 함께 적고, 결정 요청에는 미결 시 결과를 붙인다.
한 장 안에 판정 제목 · 지표 4 · 과제 진척 · 이슈 · 결정 요청이 모두 들어간다.
상위 관리자가 앞 장만 보고 판단을 끝내는 자리에 쓴다. 밀도가 높아 내용을 늘리면
겹침 검사(7번)가 실패하므로, 늘리는 대신 부록으로 내린다.

**주간보고에는 목차가 없다** — 매주 반복하는 보고라 목차가 시간만 쓴다. 타임라인도 주차가
아니라 요일(월~금) 단위다. 월간 보고와 헷갈리면 주기로 가른다. 매주면 `weekly`, 매달이면 `internal`.

**사내 보고는 요약을 앞에 둔다** — 경영진이 앞부분만 보고 넘어가는 경우가 많다.
**외부 제안은 요약을 뒤에 둔다** — 문제부터 설득한 뒤 정리하는 순서가 맞는다.

### 빠른 시작

```bash
# 보관 고정 지면 덱 — apply_brand 가 경로·로고를 맞춘 단일 파일을 만든다
python3 scripts/apply_brand.py --brand brand.json --deck internal --single-file -o ./deck.html
# 슬라이드 편집 후
python3 scripts/check_deck.py ./deck.html --shots ./out/
```

회사 정보까지 한 번에 넣으려면 `apply_brand.py`가 덱 선택과 단일 파일 묶기를 함께 처리한다.

```bash
python3 scripts/apply_brand.py --brand ./brand.json --deck internal --single-file -o ./보고서.html
# --deck: 덱 12 · 기준·라이브 4(standard · patterns · livecatalog · live) · A4 4 · 보드 5 의 이름, 또는 HTML 파일 경로
#         전체 목록은 python3 scripts/apply_brand.py --help
```

### PowerPoint(.pptx)로 만들기

파워포인트로 직접 편집해야 하는 사람이 있으면 같은 내용을 .pptx 로 낸다.

```bash
node pptx/build.js --brand brand/hct/brand.json --out dist/pptx
node pptx/build.js --brand brand.json --deck internal    # 한 종만
```

색·크기는 `blue-report.css` 의 토큰을 그대로 읽으므로(`pptx/tokens.js`) 값이 두 벌로 갈라지지 않는다.
캔버스 1920x1080px 를 13.333x7.5in 로 옮기며 **1in = 144px, 1pt = 2px** 다. HTML 과 물리적으로 같은 크기다.

**HTML 판과 다른 점** — 형식의 한계이며 의도한 차이다.

| 항목 | HTML | PPTX |
|---|---|---|
| 등장 애니메이션 | 있음 | 없음 (PowerPoint 애니메이션은 넣지 않는다) |
| 폰트 | 프리텐다드 (저장소 내장 서브셋) | 프리텐다드 (PC 설치 폰트) |
| 도넛 · 막대 | SVG · CSS | **PowerPoint 네이티브 차트** — 값을 직접 고칠 수 있다 |
| 막대 기준선 | 차트에 선으로 표시 | 제목 아래 문장으로 표시 |
| 목록 | 글머리 기호 | `키워드 — 내용` 구조만 |
| 표 상태 | 알약 칩 | 색 있는 글자 |
| 질문 칩 · 아이소타입 · 지시선 | 있음 | **없음** — HTML 전용 부품이다 |
| 발표자 노트 | `N` 키로 표시 | 슬라이드 노트 창 |

PPTX 는 PC 에 설치된 폰트만 쓴다. 프리텐다드를 사내 배포하지 않았다면 `pptx/tokens.js` 의
`F` 세 줄을 `'맑은 고딕'` 으로 되돌린다.

#### 내용이 두 곳에 있다 — 합치지 않고 갈라짐을 검사한다

덱 내용은 `assets/archive/deck-*.html` 과 `pptx/content.js` 두 곳에 따로 있다.
**HTML 이 기준이므로 내용을 고칠 때는 두 곳을 함께 고친다.**

합치지 않기로 했다. HTML 덱을 손으로 고치는 것이 이 시스템의 사용법이고
(`deck-*.html` 을 복사해 내용만 바꾼다), HTML 을 데이터에서 만들어 내는 생성물로
바꾸면 그 사용법이 사라진다. 색이 갈라지지 않는 것은 `tokens.js` 가 CSS 를 읽기
때문이지만, 내용은 그렇게 한쪽이 다른 쪽을 읽을 수 없다.

대신 갈라짐을 사람 눈이 아니라 스크립트가 잡는다.

```bash
python3 ../../../scripts/check_content_sync.py            # 저장소 루트 기준
python3 scripts/check_content_sync.py --deck internal
```

슬라이드 수 · 문서명 · 발표자 노트 36개 · 세로 막대 이름과 값 · 도넛 범례 · 표 머리글과
행을 두 곳에서 뽑아 견준다. 어긋나면 어느 덱 몇 장 어느 항목인지까지 찍는다.
`verify_repo.py` 와 CI 가 이것을 함께 돌리므로 한쪽만 고친 채로는 통과하지 못한다.

단위(`%` · `h`)와 표의 `colspan` 은 형식 차이라 대조에서 제외한다. 단위는 PPTX 생성기가
붙이고, HTML 은 지면에 직접 찍기 때문이다.

### A4 문서판 — 슬라이드가 아닌 문서

회의록 · 사규 · 매뉴얼 · 공지는 발표 슬라이드가 아니라 **A4 세로 문서**다.
지면 794×1123px(210×297mm @96dpi)이고 인쇄하면 그대로 A4 한 장이다.

```bash
cp assets/doc-minutes.html ./회의록.html
cp assets/blue-report.css assets/blue-doc.css assets/doc-viewer.css assets/doc-viewer.js ./
python3 scripts/check_doc.py ./회의록.html --shots out/
```

**색·타입·간격 토큰은 슬라이드와 같은 것을 쓴다.** `blue-doc.css` 는 토큰을
선언하지 않고 `blue-report.css` 를 전제한다. 두 파일을 함께 불러야 한다.
그래서 슬라이드와 문서의 색이 갈라질 수 없다.

| 항목 | 슬라이드 | A4 문서 |
|---|---|---|
| 지면 | 1920×1080 가로 | 794×1123 세로 |
| 글자 하한 | 24px (멀리서 봄) | 10.5pt = 14px (손에 듦) |
| 본문 대비 | 데이터 마크 2:1 | 본문 4.5:1 (인쇄물) |
| 애니메이션 | 있음 (끌 수 있음) | 없음 |
| 머리말·꼬리말 | 꼬리말만 | 쪽마다 둘 다 |
| 브랜드 | 우측 상단 마크 | 머리말 로고 + 꼬리말 회사명 |
| 검사기 | `check_deck.py` 17항목 | `check_doc.py` 9항목 |

파일 구성도 덱과 같은 방식으로 나뉜다.

| 파일 | 역할 |
|---|---|
| `blue-doc.css` | 문서 파운데이션. raw hex 0, `--br-*` 토큰만 참조 |
| `doc-viewer.css` · `doc-viewer.js` | 껍데기 — 회색 바탕 · 조작 막대 · 인쇄 · 쪽번호 자동 |
| `doc-minutes.html` | 회의록 2쪽 |
| `archive/doc-policy.html` | 사규·규정 3쪽 — 조·항·호 · 부칙 · 개정 이력 · 결재란 |
| `archive/doc-manual.html` | 매뉴얼·가이드 3쪽 — 목차 · 절차 단계 · 화면 캡처 자리 |
| `archive/doc-notice.html` | 공지 1쪽 — 게시판용. 한 쪽을 넘기지 않는다 |

**쪽번호와 문서명은 뷰어가 채운다.** `.bd-foot` 을 비워 두고 숫자를 적지 않는다.
쪽을 넣거나 빼도 번호가 어긋나지 않으며, 손으로 적으면 `check_doc.py` 가 실패시킨다.
문서명은 `.bd-doc` 의 `data-doc-title`, 문서번호는 `data-doc-no` 한 곳에서 읽는다.

**회사 로고와 명칭은 쪽마다 들어간다.** 슬라이드는 우측 상단 마크 하나지만, 문서는
한 장씩 떼어 돌려 보고 인쇄해 철하므로 어느 쪽을 집어도 어디서 나온 문서인지
보여야 한다. 머리말에 로고, 꼬리말에 회사명이다.

```html
<div class="bd-head">
  <div class="br-mark" data-on="light"><span class="br-wordmark">COMPANY NAME</span></div>
  <span class="bd-docno"></span>
</div>
...
<div class="bd-foot">
  <span><span class="bd-company">COMPANY NAME</span> · <span class="bd-doctitle"></span></span>
  <span class="bd-pageno"></span>
</div>
```

덱과 같은 `.br-mark` 자리표시자다. `apply_brand.py` 가 `brand.json` 의 `logo`(다크용)·
`logoOnLight`(밝은 지면용)로 바꾸고, `.bd-company` 에 회사명을 넣는다. 문서 지면은
밝으므로 `data-on="light"` 다. `.bd-head` 안에서는 마크가 `position:static` 이 되어
문서번호와 같은 줄에 놓인다(슬라이드는 우측 상단 절대 배치다). 빠뜨리면
`check_doc.py` 5번 항목이 실패시킨다.

| 자리 | 채우는 주체 | 무엇 |
|---|---|---|
| `.br-mark` | `apply_brand.py` | 로고 이미지 · 워드마크 |
| `.bd-company` | `apply_brand.py` | 회사명 |
| `.bd-docno` | `doc-viewer.js` | `data-doc-no` |
| `.bd-doctitle` | `doc-viewer.js` | `data-doc-title` |
| `.bd-pageno` | `doc-viewer.js` | `n / 총쪽` |

**Artifact 로 올릴 때는 `--artifact` 판을 쓴다.**

```bash
python3 scripts/build_single_file.py --artifact --deck minutes \
        --brand ../../../brand/hct/brand.json -o ./회의록.html

`--brand` 경로는 실행 위치에 따라 다르다. 스킬 폴더에서는 `../../../brand/hct/brand.json`,
저장소 루트와 계정 스킬 설치본에서는 `brand/hct/brand.json` 이다. 설치본은 묶음 안에
`brand/` 를 담고 있어 루트와 같은 경로를 쓴다.
```

`--deck` 은 덱 이름과 A4 문서 이름(`minutes`)을 함께 받는다. `--artifact` 를 빼면
`<!doctype>`·`<head>`·`<body>` 가 붙은 온전한 문서가 나오는데, Artifact 는 발행
시점에 그 껍데기를 스스로 씌우므로 한 겹이 겹친다. 브라우저가 관대해 보이기는
하지만 파서가 안쪽 태그를 버린다. 지면 바깥 바탕색은 뷰어 CSS 에서 읽어 오므로
덱(`#111`)과 문서(`#8a8f96`)가 저절로 갈린다.

**서명란은 결재 문서에만 넣는다.** `.bd-sign` 이 있지만 회의록에는 쓰지 않는다.
사규·품의처럼 결재선이 필요한 문서의 마지막 쪽에만 붙인다(보관 `archive/doc-policy.html` 참조).
`.bd-body` **안이 아니라** `.bd-page` 직계로 둔다 — `.bd-page` 가 세로 flex 이고
`.bd-body` 가 `flex:1` 이라 그것만으로 지면 바닥에 붙는다. 안에 두면 본문 흐름을 따라
중간에 뜬다.

**문서 전용 조판 도구.**

| 클래스 | 쓰는 곳 |
|---|---|
| `.bd-toc` (`.bd-toc--sub`) | 목차. 쪽번호는 편집자가 아는 값이라 손으로 적는다 |
| `.bd-steps` · `.bd-step` | 절차 단계. 번호는 자동이라 단계를 끼워 넣어도 다시 매겨진다 |
| `.bd-figure` · `.bd-figure-box` | 화면 캡처 자리. 실제 `<img>` 로 갈아 끼운다 |
| `.bd-callout--danger` · `--info` | 경고 · 참고. 기본은 주의(노랑) |
| `.bd-list--legal` | 조·항·호 괄호 번호 |

**조 번호는 손으로 적는다.** 절차 단계와 반대다. 사규는 개정 때 조를 끼워 넣으면
번호가 법적으로 달라지므로 자동 번호를 쓰면 안 된다.

**한 쪽을 넘치면 쪽을 나눈다.** `.bd-page` 가 `overflow:hidden` 이라 넘친 내용은
잘려 보이지 않고 꼬리말과 겹친다. `check_doc.py` 7번 항목이 이것을 잡는다.

---

### PDF로 내보내기

사내 배포나 이메일 첨부에는 PDF가 필요하다. 슬라이드 1장이 1페이지가 되고
크기는 **20in × 11.25in (정확히 16:9)** 다. 텍스트는 이미지가 아니라 실제 글자로 남아
복사와 검색이 된다.

```bash
python3 scripts/to_pdf.py ./보고서.html -o ./보고서.pdf --notes
```

`--notes` 를 주면 발표자 노트를 슬라이드별로 모아 마지막 페이지에 붙인다.
인쇄해서 손에 들기 위한 용도다.

### 준비물은 스크립트가 알아서 받는다

미리 설치할 것이 없다. 스크립트를 실행하면 없는 것만 골라 스스로 받고, 이미 있으면
아무것도 하지 않는다.

| 필요한 것 | 언제 | 받는 방법 |
|---|---|---|
| Pillow | 로고 변환 | `pip install Pillow` |
| Playwright + Chromium | 렌더 점검 · PDF | `pip install playwright` → `playwright install chromium` (약 150MB) |
| pptxgenjs | PPTX | `npm install` |

```bash
python3 scripts/ensure_deps.py          # 무엇이 있고 없는지만 본다
python3 scripts/ensure_deps.py --all    # 미리 다 받아 둔다
BLUE_REPORT_NO_INSTALL=1 …              # 자동 설치를 막고 명령만 안내받는다
```

### 회사 정보와 로고 넣기

회사명·워드마크·이메일·전화·저작권·로고 자리는 덱 안 8군데에 흩어져 있다. 손으로 고치면
빠뜨리기 쉬우므로 `brand.json` 한 곳에서 읽어 일괄 적용한다.

```bash
cp assets/brand.example.json ./brand.json
# brand.json 편집 후
python3 scripts/apply_brand.py --brand ./brand.json --single-file -o ./우리덱.html
```

```json
{
  "company": "주식회사 한빛테크",
  "wordmark": "한빛테크",
  "email": "contact@company.co.kr",
  "phone": "02-3456-7890",
  "copyrightYear": "2026",
  "logo": "mylogo-white.png",
  "logoOnLight": "mylogo-color.png",
  "logoHeight": 40
}
```

#### 로고는 두 벌이 필요하다

마크가 **모든 슬라이드의 우측 상단**에 들어가는데, 이 덱은 딥네이비 표지(`#071b45`)와
밝은 지면(`#f4f6f8`)을 오간다. 한 벌로는 반드시 한쪽에서 안 보인다.

| 항목 | 쓰이는 곳 | 필요한 로고 |
|---|---|---|
| `logo` | 표지 · 파트 간지 · 다크 요약 | 흰색 녹아웃 |
| `logoOnLight` | 그 밖의 모든 본문 슬라이드 | 원색(브랜드 파랑) |

원본 한 장에서 두 벌을 자동으로 뽑는다.

```bash
python3 scripts/make_logo_variants.py 로고.png --out-dir . --name mylogo
# mylogo-white.png  다크면용 흰색 녹아웃  → brand.json 의 logo
# mylogo-color.png  밝은 지면용 투명 원색판 → brand.json 의 logoOnLight
```

`logoOnLight`를 비워 두면 밝은 슬라이드는 워드마크 텍스트로 대체된다. 흰 로고를 흰 지면에
얹어 보이지 않게 만드는 대신 일부러 이렇게 실패시킨다. `check_deck.py`가 배경 광도를 재서
변형이 뒤바뀐 슬라이드를 잡아낸다.

- **로고** — PNG · JPG · SVG · WEBP. `brand.json` 기준 상대 경로 또는 절대 경로.
  data URI로 덱에 박히므로 완성된 HTML 하나만 들고 다니면 된다. 200KB 이하를 권한다.
- **`logoHeight`** — 우측 상단 마크의 높이(px). 기본 40, 권장 32~48. 상하 여백 띠
  (일반 슬라이드 84px · 표지 110px) 안에 들어가야 본문과 겹치지 않는다. 너무 키우면
  `check_deck.py`의 겹침 검사가 실패한다.
- **연락처가 없으면** `email` · `website` · `phone`을 빈 문자열로 둔다. 해당 줄과 행이
  통째로 사라진다. 사내 배포용 덱은 대개 이쪽이 맞다.
- **로고가 없으면** `logo`와 `logoOnLight`를 `null`로 둔다. `wordmark` 텍스트가 대신 들어가며,
  배경에 맞춰 밝은 면은 브랜드 파랑, 어두운 면은 흰색으로 자동 전환한다.
  프리텐다드 한 벌이 한글과 라틴을 모두 담으므로 폰트가 갈리지 않는다.
- 항상 원본 템플릿에서 새로 만들기 때문에 몇 번을 실행해도 결과가 같다.
  로고를 바꾸면 다시 실행하기만 하면 된다.
- 자리표시자 주석은 적용 후에도 남는다. 나중에 위치를 다시 찾기 쉽게 하기 위함이다.

본문 슬라이드의 예시 내용(수치 · 부서명 · 문구)은 자리표시자가 아니라 사용법을 보여주는
견본이다. 실제 발표 내용으로 직접 바꾼다.

### 다른 프로젝트에서 쓰기

이 폴더가 저장소 안(`<repo>/.claude/skills/blue-report`)에 있으면 **그 저장소에서만** 로드된다.
다른 프로젝트에서도 쓰려면 두 가지 방법이 있다.

#### 방법 1 — GitHub 플러그인 (권장)

저장소를 클론하지 않아도 되고, 저장소를 갱신하면 자동으로 최신판을 받는다.

```
/plugin marketplace add hctinno/blue-report
/plugin install blue-report@blue-tools
```

터미널에서는 한 줄로 붙여넣을 수 있다. **새 PC 에서 하는 일은 이 한 줄이 전부다.**

```bash
claude plugin marketplace add hctinno/blue-report && claude plugin install blue-report@blue-tools
```

한 번만 실행하면 그 PC의 모든 프로젝트에서 쓸 수 있다.
터미널에서 바로 하려면 `claude plugin marketplace add …` · `claude plugin install …` 를 쓴다.

`owner/repo` 짧은 형식은 기본 브랜치(`main`)에서 `.claude-plugin/marketplace.json` 을 찾는다.
아직 병합하지 않은 브랜치의 판을 쓰려면 URL 뒤에 브랜치를 붙인다.

```
/plugin marketplace add https://github.com/hctinno/blue-report.git#브랜치이름
```

설치 뒤 스킬 이름은 `blue-report:blue-report` 로 바뀐다(플러그인 이름이 앞에 붙는다).

이 저장소의 `.claude/settings.json` 에 마켓플레이스가 등록돼 있어, 이 저장소를 여는 사람은
`marketplace add` 없이 `install` 만 하면 된다.

> **설정만으로는 설치되지 않는다.** `extraKnownMarketplaces` 와 `enabledPlugins` 를
> 설정 파일에 적어 두어도 플러그인이 저절로 받아지지는 않는다. 설정을 남긴 채
> 플러그인 캐시를 지우고 세션을 두 번 띄워 확인했다 — 마켓플레이스는 다시 받아오지만
> `installed_plugins.json` 은 비어 있었고 스킬도 잡히지 않았다.
> 설정이 줄여 주는 것은 `marketplace add` 한 줄뿐이며, `install` 은 반드시 한 번 실행해야 한다.
> 새 PC 에서 명령을 0 으로 만드는 방법은 없다.

#### 방법 2 — 파일 복사 (오프라인·사내망)

GitHub 에 접근할 수 없는 환경에서 쓴다.

```bash
python3 scripts/install_blue_report_skill.py --check     # 설치 상태 확인, 변경 없음
python3 scripts/install_blue_report_skill.py --dry-run   # 바뀔 내용만 출력
python3 scripts/install_blue_report_skill.py             # ~/.claude/skills/blue-report 로 설치
```

- 멱등하다. 다시 실행해도 같은 내용이면 아무것도 쓰지 않는다.
- 기존 설치본을 덮어쓰기 전 `blue-report.backup-<타임스탬프>`로 통째 백업한다.
- 재생성 가능한 `dist/shots/`와 `__pycache__`는 설치본에서 제외한다.
- **설치 후 Claude Code 세션을 새로 시작한다.** 실행 중인 세션은 새 스킬을 즉시 읽지 않는다.

특정 프로젝트에만 넣으려면 `--target <프로젝트>/.claude/skills/blue-report`를 준다.
폴더를 직접 복사해도 동작한다. 스크립트는 상대 경로만 쓰므로 위치를 가리지 않는다.

| 설치 위치 | 적용 범위 |
|---|---|
| `~/.claude/skills/blue-report` | 내 모든 프로젝트 |
| `<프로젝트>/.claude/skills/blue-report` | 그 프로젝트만. 팀과 공유하려면 저장소에 커밋 |

브라우저에서 `deck.html`을 열면 좌우 화살표로 넘긴다.

| 키 · 버튼 | 하는 일 |
|---|---|
| `←` `→` `Space` `PageUp/Down` | 슬라이드 넘김 |
| `Home` `End` | 처음 · 마지막 |
| **`F` · 「발표」** | **전체화면 발표 모드** — 버튼과 노트가 사라지고 지면이 화면을 채운다 |
| `Esc` | 발표 모드 나가기 |
| `N` · 「노트」 | 발표자 노트 |
| 「목록」 | 전 슬라이드 세로 나열 (검수용) |

**발표할 때는 `F` 를 쓴다.** 브라우저 `F11` 도 발표 모드로 인식한다. 발표 중에는
마우스 클릭으로도 넘어가고, 2초간 움직임이 없으면 커서가 사라진다.

「목록」은 발표용이 아니다 — 전 슬라이드를 세로로 늘어놓아 한눈에 훑거나 스크린샷을
뜨려는 것이다. 예전 이름이 「전체 보기」였는데 전체화면으로 읽혀서 바꿨다.
`deck.html?all=1`은 전 슬라이드를 원본 크기로 세로 나열한다(스크린샷 · PDF 내보내기용).

**화면 크기와 무관하게 지면 전체가 보인다.** 1920x1080 지면을 창에 맞춰 줄이되
가로·세로 중 빡빡한 쪽에 맞추므로(contain) 잘리는 곳이 없다. 16:9 가 아닌 화면에서는
위아래(4:3 · 5:4)나 좌우(21:9)에 검은 여백이 남는다 — 지면을 늘려 채우지 않는다.
HUD 띠 높이도 빼 두므로 꼬리말이 띠 뒤로 들어가지 않는다. F11 전체화면도 같은 계산이다.

해상도 8종(1024x768 ~ 3440x1440)으로 실제로 띄워 보는 검사가 있다.

```bash
python3 scripts/verify_repo.py --only viewer
```

**쪽번호와 문서명은 뷰어가 자동으로 채운다.** 푸터에 숫자를 적지 않는다.
슬라이드를 넣거나 빼도 번호가 어긋나지 않는다. 문서명은 `#stage`의 `data-deck-title`
한 곳에서 읽으며, `apply_brand.py --title "문서명"` 으로 덮어쓴다.
표지 · 파트 간지 · 마무리에는 `.br-footer`가 없어 번호가 찍히지 않는다.

**발표자 노트**는 각 `.br-frame`의 `data-notes` 속성에 적는다.

---

## 1. 색

배경은 **밝은 지면 1개 + 다크면 2개까지**만 쓴다. 그 외 장식색은 금지한다.

### 지면과 카드

| 역할 | 값 | CSS 토큰 |
|---|---|---|
| 본문 지면 | `#f4f6f8` | `--br-page` |
| 카드 배경 | `#ffffff` | `--br-card` |
| 카드 테두리 | `#dbe3ec` | `--br-card-line` |
| 카드 그림자 | `0 10px 28px rgba(11,42,107,.07)` | `--br-card-shadow` |
| 기준선 · 구분선 | `#c3cedb` | `--br-hairline` |
| 알약 칩 테두리 | `#c8d1dc` | `--br-chip-line` |

**다크면 가운데에 회사 마크를 아주 옅게 깐다.** `.br-watermark` 다. 720px · 불투명도
5% 로 본문 뒤(`z-index:-1`)에 깔린다. 단색 한 장으로 지면이 죽는 것을 막는 장치이고,
새 색을 들이지 않는다 — 같은 흰색의 투명도만 쓴다.

```html
<section class="br-slide br-slide--dark">
  <div class="br-mark" data-on="dark">…</div>
  <div class="br-watermark" data-on="dark"><span class="br-wordmark">COMPANY NAME</span></div>
```

**워터마크에는 심볼만 쓴다.** 전체 로고를 720px 로 키우면 국문 병기까지 함께 커져
본문 괘선과 겹치고, 읽히지도 않으면서 자리만 차지한다. 우측 상단 마크는 40px 로 작게
들어가 전체 로고가 그대로 읽히므로 거기서는 자르지 않는다.

심볼 판은 손으로 자르지 않는다. `make_logo_variants.py` 가 만든다.

```bash
python3 scripts/make_logo_variants.py 로고.png --out-dir brand/hct --name hct-logo
#   심볼 분리: 58행에서 자름 (국문은 66행부터) → (264, 58)
#   워터마크용 : brand/hct/hct-logo-symbol-white.png
```

로고는 대개 `[심볼] / 빈 띠 / [국문 병기]` 구조다. 스크립트가 아래쪽 절반에서 가장 넓은
빈 가로 띠를 찾아 그 위에서 자른다. 띠를 못 찾으면 심볼만 있는 로고로 보고 넘어가며,
그때는 `watermark` 를 비워 두면 `logo` 가 그대로 쓰인다.

나온 파일을 `brand.json` 의 `watermark` 에 넣는다.

```json
"logo":             "hct-logo-white.png",
"logoOnLight":      "hct-logo-color.png",
"watermark":        "hct-logo-symbol-white.png",
"watermarkOnLight": "hct-logo-symbol-color.png"
```

**비율은 마크와 따로 잡는다.** 심볼은 국문이 빠져 마크보다 납작하다(4.55 대 3.07).
PPTX 생성기가 `logoRatio` 하나로 둘을 그리면 한쪽이 찌그러지므로 `watermarkRatio` 를
따로 둔다.

**표지 한 장만 뺀다.** 그 밖의 모든 지면에 깔린다. 표지는 본문이 왼쪽에 몰려 있어
가운데 마크와 제목이 겹치고, 우측 상단 마크와 안내선으로 이미 브랜드가 선다.
마무리 장은 표지와 같은 `--br-cover` 조판이지만 표지가 아니므로 깔린다.

**지면 밝기에 따라 잉크와 농도가 다르다.** 마크와 같은 규칙이다.

| 지면 | `data-on` | 자산 | 불투명도 |
|---|---|---|---|
| 다크 · 표지 조판 | `dark` | `watermark` (흰색 녹아웃) | 5% |
| 밝은 지면 | `light` | `watermarkOnLight` (원색) | 3% |

밝은 지면을 3% 로 낮추는 이유 — 진한 잉크는 같은 값이면 훨씬 세게 보이고 본문 대비를
갉아먹는다. 3% 에서 본문 대비 변화는 16.5:1 → 15.6:1 로 무시할 수준이다.

**`.br-slide` 에 `isolation:isolate` 가 필요하다.** 이것이 없으면 `z-index:-1` 이
슬라이드 배경보다 뒤로 내려가 아예 보이지 않는다. `position:relative` 만으로는 쌓임
맥락이 생기지 않는다.

불투명도가 5% 라 원본 해상도를 넘겨 키워도 흐림이 드러나지 않는다. HCT 로고 원본은
264×86 이고 720px 로 2.7배 확대되지만 눈에 띄지 않는다. `check_deck.py` 의 겹침 검사는
`.br-watermark` 를 배경 장치로 보고 건너뛴다.

**카드는 밝은 지면에서만 판이다.** 다크면(`--br-cover` · `--br-dark`)에서는 `.br-card`
마크업을 그대로 써도 판이 그려지지 않는다 — 바탕과 테두리를 걷어내고 상단 괘선
2px(`--br-accent-on-dark`)으로만 구획한다. `blue-report.css` 가 알아서 처리하므로
슬라이드에서 따로 할 일은 없다.

짙은 지면 위에 짙은 판을 얹으면 경계가 뭉개진다. 예전에 쓰던 `#182238` 카드는
지면 `#101827` 과 대비가 **1.12:1**, 테두리 `#2b3852` 도 **1.52:1** 이었다.
사람 눈에는 초점이 안 맞는 얼룩으로 보인다. 그래서 다크면 카드 바탕 토큰을 없앴다.

### 텍스트

| 역할 | 값 | CSS 토큰 |
|---|---|---|
| 본문 | `#10151c` | `--br-text` |
| 보조 | `#54606e` | `--br-text-2` |
| 약함 | `#8b98a6` | `--br-text-3` |

### 강조

| 역할 | 값 | CSS 토큰 |
|---|---|---|
| 강조 1 · 주 | `#2f4a9c` | `--br-cobalt` |
| 강조 2 (시안) | `#35b8f0` | `--br-cyan` |
| 깊은 값 · 키워드 볼드 (딥네이비) | `#0b2a6b` | `--br-navy` |
| 경고 · 핵심 단일 수치 (코랄) | `#ff7a59` | `--br-coral` |

### 주의 콜아웃

| 역할 | 값 | CSS 토큰 |
|---|---|---|
| 테두리 | `#f0c469` | `--br-warn-line` |
| 배경 | `#fff7e4` | `--br-warn-bg` |
| 텍스트 | `#8a5a00` | `--br-warn-text` |

### 지연 · 위험 상태

| 역할 | 값 | CSS 토큰 |
|---|---|---|
| 배경 | `#fff1ec` | `--br-alert-bg` |
| 텍스트 | `#a33418` | `--br-alert-text` |
| 테두리 | `#ff7a59` | `--br-coral` |

### 다크면

| 역할 | 값 | CSS 토큰 |
|---|---|---|
| 표지 · 파트 간지 | `#071b45` | `--br-cover` |
| 핵심 정리 | `#101827` | `--br-dark` |
| 다크면 구분선 | `#2b3852` | `--br-dark-line` |
| 다크면 본문 | `#f4f6f8` | `--br-on-dark` |
| 다크면 보조 | `#a9bcd6` | `--br-on-dark-2` |
| 다크면 약함 | `#6b7c96` | `--br-on-dark-3` |
| 표지 보조 | `#a6c2e6` | `--br-on-cover-2` |
| 표지 약함 | `#8aa3c4` | `--br-on-cover-3` |
| 다크면 강조 · 숫자 | `#6fa8ff` | `--br-accent-on-dark` |
| 다크면 마지막 단계 강조 | `#ffcf6b` | `--br-amber` |

### 참조 덱에서 가져온 부품 넷

| 부품 | 클래스 | 언제 쓰나 |
|---|---|---|
| 질문 칩 | `.br-ask` | 설문 문항 · 판정 질문. **「무엇을 물었나」를 답과 분리한다** |
| 아이소타입 | `.br-iso` / `.br-iso-cell(--on)` | 비율을 개수로. **분모가 눈에 보인다** |
| 다크 요약장 | `.br-sumgrid` / `.br-sumcard` | Part 가 끝날 때마다 한 장. 구간 종료 신호 |
| 지시선 주석 | `.br-note(--left)` | 문제 지점 하나를 ㄱ자로 끌어내 한 줄. **세로 막대 전용** |

넷 다 HTML 전용이다. PPTX 생성기는 그리지 않는다 — 의도한 차이다. 그래서 부품이
말하는 내용(질문 문장 · 도해 설명 · 주석 한 줄)은 `content.js` 쪽에 문장으로 남긴다.

**어느 덱이 무엇을 쓰는가**

| 덱 | 질문 칩 | 아이소타입 | 다크 요약장 | 지시선 |
|---|---|---|---|---|
| 카탈로그 | 6장 도넛 | 9장 지표 표 | 4장 핵심 정리 | 7장 막대 |
| 사내 월간 | 7장 최대 이슈 | 4장 과제별 진척 | 3장 이번 달 요약 | 5장 팀별 적용 |
| 주간 | 6장 다음 주 계획 | 3장 조직별 현황 | 2장 이번 주 요약 | 4장 부서별 완료 |
| AX 주간 | 4장 최대 병목 | 3장 자원 현황 | — 다크면 없음 | — 세로 막대 없음 |
| 경영진 | 4장 절감액 구성 | 5장 최대 위험 | 2장 결론 | — 세로 막대 없음 |
| 전사 | 5장 오해 풀기 | — | 7장 오늘 가져갈 것 | 4장 달라진 것 |
| 외부 제안 | 4장 현황 분석 | 7장 도입 사례 | 9장 제안 요약 | — 세로 막대 없음 |
| 프로젝트 | 8장 완료 판정 | 5장 산출물 | 8장 완료 판정 | 6장 달성 현황 |
| 교육 | 5장 사전 수준 | 6장 실습 체크리스트 | 7장 요약 | — 세로 막대 없음 |

빈칸은 자리가 없어서가 아니라 **그 덱에 그 부품이 설 자리가 없어서**다. 지시선은
세로 막대에만 달리고, 다크 요약장은 구간을 끊는 장이 있어야 성립한다. 자리가 없는
덱에 억지로 넣지 않는다.

**아이소타입은 분모가 정수 칸으로 떨어질 때만 쓴다.** 104/123 을 10칸 중 8칸으로
반올림하면 도해가 거짓말을 한다. 떨어지지 않으면 이 도해를 쓰지 않는다.
빈 칸도 데이터다 — 분모를 말하므로 셀 수 있어야 하고, 그래서 트랙 회색이 아니라
맥락 마크 색(2.22:1)을 쓴다.

**지시선 주석은 한 지면에 하나만.** 둘이 되면 둘 다 안 읽힌다. 참조 덱은 50장
내내 빨강을 이 용도로만 썼다. 지면 오른쪽 끝을 짚을 때는 `--left` 로 왼쪽으로 연다 —
`--w` 를 음수로 주면 요소가 슬라이드 밖으로 나가 크기 검사에 걸린다.

**지시선은 세로 막대(`.br-bar-v`) 안에만 둔다.** 가로 막대에 넣으면
`.br-bar-track` 이 `overflow:hidden` 이라 점과 글자를 통째로 잘라 낸다 — 잘려도
다른 검사는 다 통과하므로 `check_deck.py` 16번이 대신 잡는다. 가로 막대의 한 줄
주석은 `.br-bar-sub--alert` 가 맡는다.

**빨강은 나쁜 소식에만 쓴다.** 지시선의 점과 글자는 `--br-alert-text` 다. 가장 크게
좋아진 막대를 이 색으로 짚으면 청중은 사고로 읽는다. 자랑할 것은 제목과 리드가 맡는다.

**지시선을 붙이고 나서 반드시 PNG 를 본다.** 글자는 340px 폭으로 절대 배치되므로
옆 막대와 겹칠 수 있다. 겹침 검사는 슬라이드 직계 형제만 보기 때문에 같은 차트
안의 충돌은 잡지 못한다. `--h` 를 옆 막대보다 높게 올리거나 `--left` 로 방향을
바꿔 빈 자리를 찾는다.

**다크 요약장에 짙은 카드를 얹지 않는다.** 참조 덱은 그렇게 하지만 우리 지면에서
대비가 1.16:1 이라 초점이 안 맞는 얼룩으로 보인다. 상단 괘선으로 구획한다.

값이 숫자가 아니라 판정어(`충족` · `조건부`)일 때는 `.br-sumcard-v--word` 를 함께
준다. 52px 숫자 크기로 한글을 쓰면 낱말이 수치처럼 읽히고 글자 칸을 밀어낸다.
카드가 셋이면 `grid-template-columns:repeat(3,1fr)` 로 열어도 된다 — 기본은 2열이다.

부품을 넣어 지면이 넘칠 때는 **내용을 덜기 전에 같은 말을 두 번 하고 있지 않은지**
본다. 개수는 도해가 말하므로 리드는 까닭만 적으면 된다. 그래도 모자라면 표에
`.br-table--tight` 를 주어 행간만 줄인다(8행 이상일 때만. 글자 크기는 건드리지 않는다).

### 면을 나누는 방법 — 테두리가 아니라 그림자

**카드에 테두리를 두르지 않는다.** 흰 카드를 밝은 지면 위에 올리고 그림자로만 띄운다.
테두리와 그림자를 함께 쓰면 그림자가 하는 일이 사라지고, 카드가 「떠 있는 면」이 아니라
「그려 놓은 상자」로 읽힌다. 참조 덱 50장을 실측했을 때 가장 큰 차이가 이것이었다.

| 클래스 | 쓰임 |
|---|---|
| `.br-card` | **요점.** 흰 바탕 + 그림자 |
| `.br-card--mute` | **대조군.** `--br-tint` 바탕, 그림자 없음 |

그림자 유무가 위계를 만든다. **색을 더 쓰지 않는다.**

`--br-card-line` 은 이름과 달리 표 행 구분선과 A4 문서 괘선이 쓴다. 카드 테두리를
없앤다고 이 토큰을 비우면 안 된다 — 한 번 비웠다가 표에서 행 구분선이 통째로 사라졌다.

### 마크 색 — 먼저 이것부터 정한다

**차트 색은 값의 크기가 아니라 "무엇을 보라"로 정한다.** 크기는 막대 길이가 이미
말하고 있다. 7개 부서를 파랑 농담 7단계로 칠하면 "누가 평균을 넘었나"를 색이
말해 주지 않는다.

| 토큰 | 값 | 지면 대비 | 쓰임 |
|---|---|---|---|
| `--br-mark` | `--br-cat-1` | 7.51 : 1 | 주인공 — 문장이 지목하는 것 |
| `--br-mark-mid` | `#5b7fb5` | 3.77 : 1 | 3단계가 필요할 때의 중간 |
| `--br-mark-mute` | `#9aabc0` | 2.16 : 1 | 맥락 — 비교 대상 |

마크업은 `background` 를 직접 적지 않는다. 클래스로 역할만 말한다.

```html
<div class="br-bar-v"></div>                     <!-- 주인공 -->
<div class="br-bar-v br-bar-v--mute"></div>      <!-- 맥락 -->
<div class="br-col-name br-col-name--mute">…     <!-- 이름도 함께 물린다 -->
```

몇 개를 주인공으로 둘지는 **제목이 정한다.** 제목이 "상위 3개"라면 셋만 색을 준다.
`--mark` 는 다크면에서 자동으로 다크면 값으로 바뀐다.

### 데이터 램프 — 순서가 있는 구간에만

**단조 램프는 크기의 단계를 나타낼 때만 쓴다** — 소득 구간, 연차 구간처럼 순서
자체가 뜻을 가질 때다. 부서·제품처럼 순서가 없는 항목에 쓰면 안 된다.
값이 클수록 진한 램프. **5색 전부 지면 `#f4f6f8` 대비 2:1 이상**이다.

| 토큰 | 값 | 지면 대비 |
|---|---|---|
| `--br-data-1` | `#0b2a6b` | 12.44 : 1 |
| `--br-data-2` | `#2f4a9c` | 7.51 : 1 |
| `--br-data-3` | `#2f7ff0` | 3.58 : 1 |
| `--br-data-4` | `#5b9bd5` | 2.73 : 1 |
| `--br-data-5` | `#86b0da` | 2.10 : 1 |

구간이 6개 이상이면 양 끝(`#0b2a6b` → `#86b0da`)을 고정한 보간 램프를 쓴다.
7단계는 토큰에 이미 있다: `#0b2a6b #20407e #345790 #486da2 #5d83b5 #729ac8 #86b0da`
(`--br-bar-1` ~ `--br-bar-7`, 전 단계 2:1 통과).

### 소프트 램프 — 다크면 전용

`--br-soft-1` `#7fb6f5` · `--br-soft-2` `#9dc4f2` · `--br-soft-3` `#a4c4e5`

> **주의.** 이 3색은 밝은 지면 `#f4f6f8`에서 각각 **1.96 / 1.67 / 1.67 : 1**로
> "데이터 마크 2:1 이상" 규칙에 미달한다. 밝은 면의 데이터 마크로 쓰지 않는다.
> 다크면 `#101827` 위에서는 6.9~8.4 : 1로 안전하다. 밝은 면에서는 보조 텍스트·구분선 등
> 비데이터 요소에만 쓴다.

---

## 2. 타입

폰트는 **프리텐다드** 하나다. 저장소가 파일을 들고 있고 바깥에서 받아 오지 않는다.
HTML 에 폰트 `<link>` 를 적지 않는다 — `blue-report.css` 의 `@font-face` 가 처리한다.

```
assets/fonts/PretendardVariable.subset.woff2   425KB · 굵기 45~930 · KS X 1001 한글 2,350자
assets/fonts/LICENSE-Pretendard.txt            SIL OFL 1.1 (재배포 조건)
```

가변 폰트 한 벌에 전 굵기가 들어 있다. 정적 폰트로 여섯 굵기를 받으면 965KB 인데
이건 425KB 로 끝나고, 굵기를 하나 더 쓰기로 해도 파일이 늘지 않는다.

| 용도 | 폰트 | 토큰 |
|---|---|---|
| 한글 제목 · 본문 | 프리텐다드 | `--br-font-kr` |
| 숫자 | 프리텐다드 + `tabular-nums` | `--br-font-num` |
| 섹션 라벨 | 프리텐다드 600 + `letter-spacing:.14em` 대문자 | `--br-font-label` |

세 토큰은 지금 같은 값이다(`--br-font-num` 과 `--br-font-label` 이 `--br-font-kr` 을
가리킨다). 나눠 둔 것은 나중에 숫자나 라벨만 다른 폰트로 갈아 끼울 자리를 남기려는 것이다.

**폰트를 다시 만들 때** — 손으로 받아 넣지 않는다.

```bash
python3 scripts/make_font_subset.py           # npm 에서 받아 잘라 넣는다
python3 scripts/make_font_subset.py --check   # 지금 것이 규격에 맞는지만 본다
```

`--check` 는 크기만 보지 않는다. `tnum`(고정폭 숫자)과 `kern` 이 살아 있는지, 굵기 축이
300~900 을 덮는지, 넣기로 한 글자가 다 들어갔는지를 본다. `tnum` 이 빠지면 표의 숫자
자리가 흔들리는데 눈으로는 잘 안 보인다.

- 제목은 **weight 300과 900을 한 문장에서 대비**시킨다. `가벼운 앞말 + <strong>굵은 핵심</strong>`
- **1920×1080에서 24px 하한.** 예외는 큰 숫자에 붙는 `%` 첨자(`.br-sup`, `.44em`)뿐이다.
- 전역으로 `word-break:keep-all; overflow-wrap:break-word` — 한글이 음절 단위로 잘리는 것을 막는다.

### 크기 척도

| 토큰 | 값 | 용도 |
|---|---|---|
| `--br-fs-cover` | 108px | 표지 제목 |
| `--br-fs-display` | 96px | 마무리 CTA 제목 |
| `--br-fs-part` | 84px | 파트 번호 |
| `--br-fs-h2` | 62px | 슬라이드 제목 |
| `--br-fs-h2-sm` | 54px | 두 줄 이상 제목 |
| `--br-fs-h3` | 38px | 목차 항목 |
| `--br-fs-card-title` | 32px | 카드 제목 |
| `--br-fs-lede` | 28px | 제목 아래 요약 |
| `--br-fs-label` | 26px | 섹션 라벨 |
| `--br-fs-body` | 25px | 본문 |
| `--br-fs-foot` | 24px | 푸터 · 하한 |
| `--br-fs-stat-hero` | 200px | 단일 수치 강조 |
| `--br-fs-stat` | 56px | 카드 안 수치 |
| `--br-fs-stat-sm` | 32px | 막대 값 |

---

## 3. 간격과 형태

- 슬라이드 여백 — 본문 `84px 96px 60px`, 표지·간지 `110px 120px 80px`
- 간격 척도 — `8 / 14 / 22 / 34 / 52 / 84 px` (`--br-sp-1` ~ `--br-sp-6`)
- 카드 라운드 **18px**, 알약 칩 **999px**, 좁은 막대 **2px**, 넓은 세로 막대 **8px**
- 알약 칩은 **한 줄 전용**이고 **그림자를 주지 않는다.** 두 줄이 되면 라운드 18px 사각형으로 바꾼다.
- 제목 밑줄, 장식용 색 띠, 사이드 스트라이프, 블루프린트 `+` 코너 마크를 쓰지 않는다.

---

## 4. 차트 규칙 (엄수)

### 도넛 — 파이 금지

```
C    = 2 × π × r                       원주
dash = C × pct/100  −  C × 1.5/360     구간 길이 (1.5도 간격 차감)
rot  = 누적pct × 3.6 − 90              12시에서 시작
```

```html
<circle class="dsh" r="110" stroke="#0b2a6b" stroke-width="48"
        stroke-dasharray="400.8 691.2" transform="rotate(-90)"></circle>
```

- `stroke-dasharray`의 **두 번째 값은 항상 원주 C**다. 다르면 구간이 반복된다.
- 손으로 적은 `<path d="M0 0 L… A…">` 파이는 금지한다. 수치와 각도가 어긋난다.
- 구간은 3~5개. 6개를 넘으면 막대로 바꾸거나 하위를 '기타'로 묶는다.
- 라벨은 **도넛 밖**에. 좁은 홀에 텍스트를 넣지 않는다.
  필요하면 꺾은 리더 라인 + 구간색 점(r=6)으로 연결한다.

### 막대

- **값은 막대 안이 아니라 전용 컬럼 또는 막대 위 줄에.** 퍼센트 폭 안에 넣으면 짧은 값에서 삐져나온다.
- 이름은 차트와 **다른 그리드 컬럼 / flex 형제**에 둔다. 절대 위치로 막대 위에 올리지 않는다.
- 높이 = `값 / 최댓값 × 채널높이`. 채널 470px 기준.
- `border-radius = 높이/2`인 막대는 값이 높이보다 좁아지면 전부 같은 캡슐로 보인다 → 좁은 채널은 2px.

### 공통

- **데이터 마크(호·막대·버블·범례 스와치)는 지면 대비 2:1 이상.** 배경·구분선 톤을 데이터에 쓰지 않는다.
- 인접 구간에 같은 색 금지. 값이 클수록 진한 단조 램프.
- 버블은 면적 비례: `d = k × √value`. 지름 비례는 큰 값을 과장한다.

---

## 5. 문체 (엄수)

- **개조식 · 명사형.** 슬라이드 본문은 명사로 끝낸다.
  - 존댓말 종결 금지 — `~합니다 / ~습니다 / ~입니다 / ~됩니다 / ~해요 / ~어요`
  - **평서형 종결도 금지** — `~한다 / ~된다 / ~없다 / ~았다·었다` 등 `다` 로 끝나는 서술
  - 예: `진단으로 푼다` → `진단으로 해결`, `시작도 안 됐다` → `시작 전`
  예외는 설문 문항과 응답 선택지 원문뿐이며, 그 줄에 `<!-- 원문 -->` 주석을 남긴다.
  **발표자 노트(`data-notes`)는 대상이 아니다** — 노트는 `~한다` 형으로 적는다.
- 긴 서술은 `키워드 — 내용`으로 쪼갠다.
- 핵심 수치·개념은 `<strong style="font-weight:700;color:#0b2a6b">`로 강조한다 (`.br-key`).
- **한 슬라이드 = 한 주장.** 문장 수를 줄이고 한눈에 스캔되게 한다.

---

## 6. 진입 애니메이션

슬라이드가 활성화되면 `[data-deck-active]`가 붙고 **제목 → 본문 → 차트** 순으로 등장한다.

| 클래스 | 동작 | 쓰는 자리 |
|---|---|---|
| `.a` | fade-up | 제목·본문·카드 기본값 |
| `.ad` | fade-down | 섹션 라벨 |
| `.f` | fade | 푸터·축 이름 |
| `.bx` | scale-X | 가로 막대 |
| `.by` | scale-Y | 세로 막대 |
| `.p` | pop | 단일 수치 강조 |
| `.dsh` | dasharray | 도넛 구간 |

딜레이 `.d1` ~ `.d12` = **80ms 단위**. 마지막 딜레이가 1초를 넘지 않게 한다.
넘으면 요소가 너무 많은 것이므로 슬라이드를 쪼갠다.
`prefers-reduced-motion: reduce`에서는 전부 꺼지므로, 애니메이션에 의존해 정보를 전달하지 않는다.

**덱 단위로 끌 수 있다.** `#stage` 에 `data-no-anim` 을 주면 등장 효과가 전부 꺼진다.

```html
<div id="stage" data-no-anim data-deck-title="…">
```

주간보고처럼 화면에 띄워 놓고 읽거나 인쇄해서 돌리는 문서는 꺼 두는 편이 낫다.
넘길 때마다 요소가 하나씩 나타나면 표를 훑는 속도가 느려진다.
`weekly` 와 `ax` 덱은 이미 꺼져 있고, 발표용 덱(`internal` · `sales` · `project` · `training` · `catalog`)은 켜져 있다.

```css
@keyframes br-fu   { from { opacity:0; transform:translateY(22px) } }
@keyframes br-fd   { from { opacity:0; transform:translateY(-16px) } }
@keyframes br-fi   { from { opacity:0 } }
@keyframes br-gx   { from { transform:scaleX(0) } }
@keyframes br-gy   { from { transform:scaleY(0) } }
@keyframes br-pop  { from { opacity:0; transform:scale(.8) } }
@keyframes br-dash { from { stroke-dasharray:0 4000 } }
```

---

## 6-2. 웹 보드 (제3 계통)

슬라이드도 A4 도 아니다. 지면 크기가 없고 화면 폭에 따라 흐르며, 읽는 물건이
아니라 **상태를 바꾸는 화면**이다. 회차 중간에 값이 바뀌고 다음 사람이 이어받는다.

```html
<link rel="stylesheet" href="blue-report.css">   <!-- 색·폰트 -->
<link rel="stylesheet" href="blue-web.css">      <!-- 웹 크기·부품 -->
```

`blue-web.css` 는 **색을 선언하지 않는다.** `blue-doc.css` 와 같은 방식으로
자기 이름공간(`--bw-*`)을 `:root` 에 새로 선언하고 색은 규격에서 빌려 쓴다.
**`--br-fs-*` 를 덮어쓰지 않는다** — 컨테이너에 얹으면 부모인 `body` 가 그 값을
못 보고, 덮어쓰면 같은 문서에서 슬라이드 조각을 쓸 수 없다.

| 항목 | 슬라이드 | A4 문서 | 웹 보드 |
|---|---|---|---|
| 지면 | 1920×1080 고정 | 794×1123 고정 | 없음 (흐름) |
| 글자 하한 | 24px | 10.5pt | **12.5px** |
| 토큰 | `--br-fs-*` | `--bd-fs-*` | `--bw-fs-*` |
| 검사기 | `check_deck.py` (17) | `check_doc.py` (9) | `check_board.py` (11) |
| 내보내기 | HTML·PDF·PPTX | HTML·PDF·DOCX | HTML 만 |

**표의 고정 머리행과 가로 스크롤은 같이 쓸 수 없다.** `overflow-x:auto` 가 그
상자를 스크롤포트로 만들어 `sticky` 머리행이 화면이 아니라 그 상자에 붙고,
상자는 세로로 스크롤하지 않으므로 머리행이 따라오지 않는다. 기본은 머리행
고정이고, 열이 많은 표만 `.bw-scroll` 로 감싸 고정을 포기한다. 검사기가
둘을 같이 쓰면 실패시킨다.

### 보드 — 관리보드 1종 + 보관 4종

| 용도 | `--deck` | 파일 | 특징 |
|---|---|---|---|
| 과제 실행보드 | `board` | `archive/board-task.html` | 가장 작은 견본. 레일 · KPI · 필터 표 · 메모 |
| 관리보드 | `manage` | `board-manage.html` | 절 12 · 표 8 · 일정 격자 · 가로 막대 |
| 실행보드 | `execboard` | `archive/board-exec.html` | 상태 알약 4단 순환 · 설비 진행판 · 주차 막대 |
| 팀보드 | `teamboard` | `archive/board-team.html` | 칸반 4열 · 주차 격자 · 상세 겹칩 |
| 점검보드 | `gapcheck` | `archive/board-gap.html` | 공백 부모 + 대응 자식 · 비율 띠 · 대조표 · 단계 목록 |

뒤 네 벌은 사내에서 따로 만들어 쓰던 보드를 옮긴 것이다. 옮기며 드러난 것들.

- **같은 일을 하는 상자가 세 이름으로 흩어져 있었다** — `.pm-strip` · `.tf-strip`
  · `.branch`. 크기가 제각각인 이유도 이름이 달라서였다. 이름이 하나면 크기도 하나다.
- **`--br-fs-*` 를 컨테이너에 얹은 벌이 둘 있었다.** `body` 가 그 값을 못 봐
  실측 계산값이 슬라이드 값 그대로였다. `--bw-*` 병렬 선언이 이 함정을 구조적으로 없앤다.
- **죽은 `sticky` 머리행** — 가로 스크롤 상자 안에 있어 한 번도 따라오지 않았다.
- **그려지지 않는 막대** — 폭을 계산해 놓고 쓰지 않은 코드가 한 벌에 있었다.
- **`.bw-ov` 는 `[hidden]` 을 이긴다.** `display:flex` 가 브라우저 기본 규칙을
  덮어 겹칩이 닫히지 않았다. `.bw-ov[hidden] { display:none }` 한 줄이 필요하다.

### 채널 위 램프

`.bw-bar` 는 지면이 아니라 채널(`--br-track`) 위에 놓인다. `--br-bar-*` 7단 램프는
**지면** 대비로 잡은 값이라 밝은 쪽이 채널 위에서 2:1 에 미달한다(`--br-bar-7` 은
지면 2.16 · 채널 1.86). 채널 안에 6단 이상을 깔 때는 `--br-chan-1..6` 을 쓴다.

### JS 로 그린 글자의 문체

보드는 내용을 JS 데이터로 들고 그리는 일이 많다. 원문만 보는 문체 검사는 그 글자를
한 자도 못 본다 — `<script>` 안은 규칙상 걷어내기 때문이다. `check_board.py` 의
11번째 항목이 **그려진 뒤의 DOM** 을 한 번 더 읽어 실제로 화면에 뜬 글자를 판정한다.

인용 원문 예외 표시(`원문` · `설문 문항`)도 **주석 안에** 있어야 한다. 낱말만 보면
본문에 "원문"이 들어간 줄이 통째로 검사 밖으로 나간다 — JS 로 그린 표는 한 줄이라
셀 하나에 "원문"이 있으면 표 전체가 빠졌다.

---

## 6-3. 라이브 덱 — 기준 덱 · 부품 카탈로그 · 발표 엔진

고정 지면이 없는 발표 계통이다. 한 장이 화면 한 면(`100dvh`)이고 치수가 전부 `rem` 이다.
루트 글자 크기가 창을 따라가므로(`clamp(10.5px, min(1vw, 1.78vh), 20px)`) 1366×768
노트북과 1920×1080 화면의 짜임이 같다. 사내 발표 덱 56장을 렌더해 장 짜임새 · 부품 38종 ·
애니메이션 12계열 · 발표 기능을 뽑아 이 계통으로 옮겼다. 원본의 수치 · 조직 · 인물 · 원문은
옮기지 않았다 — 견본은 전부 가상 시나리오다.

**먼저 `DESIGN.md`(디자인 규칙 한 장)를 읽는다.** 이 절은 그 규칙을 받치는 규격 전문이다.

**새 보고서는 기준 덱을 틀로 삼는다.** 머리띠 · 꼬리띠 · 로고 · 워터마크 · 진행선 · 제목 밴드는
그대로 두고, 본문은 내용에 맞게 짠다 — 카탈로그 부품을 그대로 · 고쳐 쓰거나, 없으면 새로 짠다
(아래 「본문 맞춤 디자인」).

| 파일 | `--deck` | 장 | 쓰는 법 |
|---|---|---|---|
| `assets/live-standard.html` | `standard` | 15 | **출발점.** 표지 · 목차 · 보고 요지 · 장 간지 · 본문 · 로드맵 · 결정 요청 · 마무리 · 부록 간지 · 예상 질문 · 용어 |
| `assets/live-patterns.html` | `patterns` | 63 | 패턴첩. 사내 발표 덱 최종본의 디자인 언어 용례 63장 + 응용 견본(내용은 가상). 문법(`references/design-language.md`)으로 내용에 맞게 짠다 — 맞는 장은 고쳐 쓰고 아니면 새로 짠다 · 덱 머리에 `blue-pattern.css` |
| `assets/live-catalog.html` | `livecatalog` | 52 | 부품첩. 맞는 장을 복사해 그대로 · 고쳐 쓰거나, 참고해 새로 짠다. `own` 장(X01)이 맞춤 본문 견본 |

```bash
# 1. 기준 덱을 틀로 복사한다. 본문은 카탈로그 부품을 쓰거나 고치거나 <style data-own> 으로 새로 짠다
cp assets/live-standard.html 작업/보고서.html
# 2. 회사 정보 · 로고를 넣고 CSS · 뷰어 JS · 폰트까지 한 파일로 묶는다 (권장)
#    --title 을 빼면 brand.json 의 docTitle 이 덱 제목을 덮는다 — 장마다 꼬리띠 문서명이 바뀐다
python3 scripts/apply_brand.py --brand brand.json --deck 작업/보고서.html --title "문서명" --single-file -o 보고서.html
# 3. 30항목 검사. 실패 0 이어야 완료다. 장마다 남는 PNG 를 눈으로 넘겨 본다
python3 scripts/check_live.py 보고서.html --shots out/
```

**작업본 미리 보기** — 작업 폴더의 HTML 을 바로 열면 CSS · 엔진이 없어 맨 글자만 보인다.
`assets/` 의 `blue-report.css` · `blue-live.css` · `live-viewer.js` · `fonts/` 를 작업 파일 옆에 같이 둔다.

**문서명 길이** — 꼬리띠 문서명은 조작판 왼쪽 끝에서 말줄임(…)으로 잘린다. 16:9 화면에서 24자,
760px 창에서 20자, 600px 안팎과 휴대폰 폭에서 12자 정도까지 다 보인다. 긴 제목은 표지에 두고
문서명은 짧게 쓴다.

`--single-file` 없이 내면 `blue-report.css` · `blue-live.css` · `live-viewer.js` · `fonts/` 가
결과물 옆에 복사된다. 그중 하나라도 떼어 옮기면 지면이 깨지거나(CSS) 발표 기능이 전부
죽는다(JS). 검사기 23번 항목이 엔진이 떴는지까지 본다.

### 문서 뼈대

```html
<link rel="stylesheet" href="blue-report.css">   <!-- 색 · 폰트 토큰. 먼저 부른다 -->
<link rel="stylesheet" href="blue-live.css">     <!-- 배율 · 띠 · 부품 · 움직임 · 아이콘 -->

<div id="bl-prog"></div>                          <!-- 맨 위 진행선 -->
<main class="bl-deck" id="deck" data-deck-title="문서명" tabindex="0">
  <section class="bl-sl" id="kpi" data-notes="발표자 노트 — ~한다 형">
    <header class="bl-hd">
      <span class="bl-code"><b>02</b>절 이름</span><span class="bl-sp"></span>
      <div class="br-mark" data-on="dark"><!-- 로고 자리 --><span class="br-wordmark">COMPANY NAME</span></div>
    </header>
    <div class="bl-bd">
      <h2 class="bl-title">주장 — <em>핵심구</em></h2>
      <p class="bl-lede">기준 · <strong>굵은 결론</strong><button type="button" class="bl-ev" data-ev="E1">출처</button></p>
      <div class="bl-mid"> … 본문 덩어리 하나 … </div>
    </div>
    <footer class="bl-rf"><span class="bl-rf-name"></span><span class="bl-pg"></span></footer>
    <div class="br-watermark" data-on="light"><!-- 워터마크 자리 --><span class="br-wordmark">COMPANY NAME</span></div>
  </section>
</main>

<div class="bl-hud" role="toolbar" aria-label="덱 조작">
  <button type="button" data-act="prev" aria-label="이전 장">‹</button>
  <span data-pg aria-live="polite"></span>
  <button type="button" data-act="next" aria-label="다음 장">›</button>
  <span class="bl-hud-sep" aria-hidden="true"></span>
  <button type="button" data-act="expand" aria-pressed="true">펼침<kbd>X</kbd></button>
  <button type="button" data-act="horiz" aria-pressed="false">가로<kbd>V</kbd></button>
  <button type="button" data-act="notes" aria-pressed="false">메모<kbd>M</kbd></button>
  <button type="button" data-act="laser" aria-pressed="false">레이저<kbd>L</kbd></button>
  <button type="button" data-act="pen" aria-pressed="false">펜<kbd>P</kbd></button>
  <button type="button" data-act="present">발표<kbd>Shift+F5</kbd></button>
  <button type="button" data-act="script">대본<kbd>Alt+F5</kbd></button>
  <button type="button" data-act="help" aria-label="단축키 도움말">?</button>
</div>
<div id="bl-jump" hidden aria-hidden="true"></div>
<script type="application/json" id="bl-evidence">{"ev": { … }}</script>
<script src="live-viewer.js"></script>
<!-- 장 전용 스크립트는 여기, 뷰어 뒤에 둔다 -->
```

- 쪽번호와 문서명은 엔진이 채운다. `.bl-pg` · `.bl-rf-name` 은 비워 둔다.
- 조작판은 `data-act` 로 묶는다. `<span data-pg>` 에 쪽번호와 단계(` · 2/3`)가 뜬다.
  600px 이하에서는 ‹ › 만 남는다.
- 브랜드 마크와 워터마크 안의 자리표시자는 그대로 둔다. `apply_brand.py` 가 채운다.
- JS 가 없어도 세로로 스크롤하면 전부 읽힌다. 숨김(등장 전 모습)은 엔진이 `html.bl-anim`
  을 달았을 때만 걸린다.

### 본문 맞춤 디자인 — 고정 영역은 그대로, 본문은 내용에 맞게

기준 덱은 **틀**이지 본문 모양의 상한이 아니다. 지면을 둘로 나눈다.

| 구역 | 무엇 | 규칙 |
|---|---|---|
| 고정 영역 | 머리띠 `.bl-hd`(코드 · 브랜드 마크) · 꼬리띠 `.bl-rf`(문서명 · 쪽번호) · 워터마크 `.br-watermark` · 진행선 `#bl-prog` · 제목 형광 밴드 `.bl-title` · 조작판 `.bl-hud` · 겹창 · 발표 엔진 | 기준 덱 그대로. 맞춤 CSS 선택자에 이 이름을 넣지 않는다 |
| 자유 영역 | `.bl-bd` 안, 제목 · 리드 아래 본문 전부 | 내용에 맞게 짠다 — 카탈로그 부품 그대로 · 변형 · 새 도식 · 새 레이아웃 · 새 애니메이션 |

**순서** — 장마다 내용의 성격을 먼저 정하고 표현을 고른다. 표 · 목록은 마지막 선택이다.

| 내용 | 먼저 볼 카탈로그 부품 | 맞지 않으면 새로 짤 것의 예 |
|---|---|---|
| 흐름 · 경로 · 유입 | 흐름도 `flow` · 노선도 `route` · 파이프라인 `pipe` · 바통 `baton` | 깔때기(`own` 장) · 경로 지도 SVG · 분기 트리 |
| 일정 · 단계 · 연혁 | 간트 `gantt` · 레인 `lanes` · 연혁 `history` · 실행 길 `decide` | 연도 열 간트 · 마일스톤 띠 · 계단 로드맵 |
| 비교 · 선택 | 좌우 대비 `vs` · 두 해 `years` · 매트릭스 `matrix` | 2×2 포지셔닝 · 점수 막대 쌍 · 레이더 대용 막대 |
| 구성 · 비율 | 도넛 `kpi` · 누적 막대 `stack` · 랙 `rack` · 와플 `waffle` | 트리맵 칸 · 비율 띠 |
| 수치 · 추세 | 수치 타일 `kpi` · 워터폴 `stack` · 계단 `stair` · 히어로 `hero` | 스파크 선 · 목표 대비 게이지 |
| 구조 · 조직 · 체계 | 조직도 `org` · 구성도 `net` · RACI `raci` | 계층 블록 · 영역 경계도 |
| 화면 · 시연 | 목업 `explorer` · 포털 `portal` · 캡처 `shot` · 탭 `tabs` · 장면 `coach` | 화면 위 주석 화살 · 전후 슬라이더 |

**맞춤 CSS 쓰는 법** — 견본은 카탈로그 `own` 장(X01 깔때기). 장째 복사하면 CSS 도 함께 따라간다.

```html
<section class="bl-sl" id="funnel" data-notes="…">
  <style data-own>
    #funnel .x-steps { display: grid; gap: .55rem }                       /* 범위: 장 id + 자기 접두어 */
    #funnel .x-step  { padding: .85rem 2.2rem; background: var(--br-navy);  /* 색: 토큰만 */
                       color: var(--br-on-dark); clip-path: polygon(…) }    /* 치수: rem 만 */
    @media (prefers-reduced-motion: no-preference) {                        /* 움직임 줄이기 분기 */
      html.bl-anim #funnel:not(.in) .x-step { opacity: 0 }                  /* 들어오기 전 */
      #funnel.in .x-step { animation: xGrow .7s var(--bl-ease-out) both }   /* 장에 들어오면 */
    }
    @keyframes xGrow { from { opacity: 0; transform: scaleX(.3) } to { opacity: 1; transform: none } }
  </style>
  <header class="bl-hd">…그대로…</header>
  <div class="bl-bd">
    <h2 class="bl-title">주장 — <em>핵심구</em></h2>
    <div class="bl-mid"><ol class="x-steps">…</ol></div>
  </div>
  <footer class="bl-rf">…그대로…</footer> <div class="br-watermark">…그대로…</div>
</section>
```

| 해도 된다 | 하지 않는다 (검사기 28번 실패) |
|---|---|
| 장 안 `<style data-own>` · 인라인 SVG · CSS 격자 · `clip-path` · 그라데이션(토큰 색) | 고정 영역 클래스를 선택자에 넣기(`.bl-hd` · `.bl-rf` · `.bl-pg` · `.br-mark` · `.br-watermark` · `.bl-title` · `#bl-prog` · `.bl-hud` …) |
| 카탈로그 부품을 장 안에서 고쳐 쓰기 — `#장id .bl-tc { … }` | 범위 없는 선택자(`.bl-bd p` · `table`) — 모든 장이 바뀐다 |
| 자기 클래스 · 자기 변수 — `x-` 등 `bl-` · `br-` 아닌 접두어, `--x-*` | `bl-` · `br-` 이름 새로 짓기, `--br-*` · `--bl-*` 토큰 덮어쓰기 |
| `var(--br-*)` · `var(--bl-*)` · `currentColor` · `transparent` | hex · `rgb()` · `hsl()` · 색 이름(`white` 등). 그림자의 검정 · 흰 반투명만 예외 |
| `rem` · `%` · `fr` · `em` · 테두리 `1px` | 그 밖의 `px` |
| 글꼴 `var(--br-font-kr)` · `--br-font-num` · `--br-font-label` · `var(--bl-font-mono)` | 다른 `font-family`, 글꼴 자리가 빈 `font:` 단축 |
| 모서리 `var(--bl-r-xs \| s \| m \| l \| pill)` · `0` · `50%`(원) | 그 밖의 `border-radius` 값 |
| 그림자 `var(--bl-shadow)` · `var(--bl-shadow-up)` · `none` · 테두리 고리 `inset 0 0 0 .16rem var(--br-*)` | 직접 적은 그림자, `text-shadow` |
| 곡선 `var(--bl-ease)` · `var(--bl-ease-out)` · `var(--bl-ease-pop)` · 무한 반복은 `linear` | `ease` · `ease-in-out` · `cubic-bezier()` · `steps()`, 곡선 생략(기본 `ease`) |
| 길이 0.15 ~ 2.4초 · 무한 반복(흐르는 점 · 도는 표식)은 12초까지 | 그보다 짧거나 긴 움직임 |
| 새 `@keyframes` — 움직임 줄이기 분기 안에서 | 장 자체(`#장id { padding … }` · `.bl-sl`) · `html` · `body` 를 대상으로 삼기, `@font-face` · `@import` |

**형태 · 움직임도 한 덱의 말투다.** 색만 토큰이면 장마다 모서리 · 그림자 · 속도가 달라 여러 덱을
이어 붙인 것처럼 보인다. 위 표의 눈금이 계통 부품이 실제로 쓰는 값이다. 인라인 `style=` 도 같은
검사를 받는다. 움직임은 **먼저 기존 12계열(`bl-a` — 카탈로그 `motion` 장)로 표현**하고, 없을 때만
새 `@keyframes` 를 짠다.

맞춤 장도 글자 하한(본문 1.0rem) · 대비 · 16:9 한 화면 · 좁은 폭 접힘을 그대로 검사받는다.
900px 이하에서 접히도록 `@media (max-width: 900px)` 분기를 함께 적는다. 움직임에 정보를 싣지 않는다
— 감속 모드에서는 처음부터 최종 모습이어야 한다.

검사기 29번 「본문 표현」은 표지 · 간지 · 마무리 · 부록을 뺀 내용 장 중 글 · 표만 있는 장이 절반을
넘으면 **주의**를 낸다. 실패는 아니지만, 뜨면 그 장들을 위 대응표로 다시 본다.

### 장 종류와 쪽번호

| 장 | 클래스 · 속성 | 쪽번호 | 머리띠 마크 · 워터마크 `data-on` |
|---|---|---|---|
| 표지 | `bl-sl bl-sl--dark bl-sl--cover` | 없음 · 숫자 `0` 으로 이동 | `light` · `dark` |
| 목차 | 본문 장 + `.bl-agenda` | `01 / NN` | `dark` · `light` |
| 장 간지 | `bl-sl bl-sl--chapter` + `.bl-chapter` | 본문과 같이 센다 · 배정 5초 | `dark` · `light` |
| 본문 | `bl-sl` | `NN / 전체` | `dark` · `light` |
| 어두운 본문 | `bl-sl bl-sl--dark` | 본문과 같다 | `light` · `dark` |
| 마무리 | 본문 장 + `.bl-bd.bl-fin` | 본문과 같다 | `dark` · `light` |
| 부록 간지 | `bl-sl bl-sl--dark bl-sl--apxdiv` + `.bl-apxdiv` | 「부록」 · 배정 0초 | `light` · `dark` |
| 부록 장 | 장에 `data-apx` | `부록 NN / MM` · 배정 0초 | 장 밝기를 따른다 |
| 빽빽한 장 | `bl-sl--dense` 추가 | — | 글자를 한 단 줄인다(본문 하한은 지킴) |

숫자 이동(숫자 + Enter)은 **화면에 찍힌 쪽번호**로 간다. `a` 를 먼저 누르면 부록 쪽번호다.
워터마크는 표지에도 깐다 — 표지는 크게 · 진하게(고정 지면 덱은 표지에서 뺀다. 계통이 다르다).
마무리 문장은 「질의응답」으로 닫는다 — 지면 본문은 존댓말 종결(감사합니다 등)을 쓰지 않는다.

### 배치 — 92rem 판 · 세로 가운데

- 본문은 가운데 `--bl-max: 92rem` 판에 모인다. 좌우 여백 `--bl-gut` 은 띠 · 본문 · 꼬리띠가
  함께 쓴다. 띠의 바탕은 화면 끝까지 닿는다.
- **`.bl-mid`** — 제목 · 리드는 위에 고정하고 본문 덩어리를 남는 높이의 가운데에 둔다.
  사내 발표 덱의 짜임새다. 덩어리가 여럿이면 하나로 감싸고 거기에 단다.
- **`.bl-fill`** — 남는 높이를 먹는다. 그 안 격자 행까지 늘리려면 **`.bl-grow`** 를 함께 준다.
- 비율 격자 — `.bl-split`(1:1) · `--wide`(1.35:1) · `--main`(1.72:1) · `--side`(1:1.72) ·
  `--3`(1:2:1.2) · `.bl-cols--3` · `--4` · `--5` · `.bl-flow--2` · `--3w` · `--4` · `--5`
  (카드 사이 `.bl-conn` 연결자) · `.bl-stack-v`(세로 묶음) · `.bl-row`(가로 줄) · `.bl-push`(아래로 밀기).
  비율을 인라인 style 로 적지 않는다.
- 새 부품의 열은 **900px 에서만** 접는다. 1050~2000px 창은 rem 으로 잰 지면 폭이 늘 100rem
  이라 1400px 에서 접으면 줄만 늘어 고정 높이 지면 아래가 잘린다.
- **900px 이하는 읽는 폭이다.** 열이 한 줄로 접히고 장이 내용만큼 늘어나 세로 스크롤로 전부
  읽힌다. 띠는 제 최소 높이로 고정된다. 조작판에서 가로 · 레이저 · 대본이 빠진다. 열을 접을 수
  없는 부품(간트 · 레인 · 흐름도 · 매트릭스 · 히트맵 · 누적 막대 · 개념 곡선)은 읽히는 폭을
  지키고 옆으로 스크롤한다. 실행 길(`.bl-road2`)은 세로로 접힌다. 발표 · 가로 보기는 그대로
  한 화면 한 장이다.
- **16:9 한 화면에 다 들어가야 한다.** 지면은 한 화면 높이에 `overflow: hidden` 이라 넘친 줄은
  잘려 사라진다. 검사기 27번 항목이 장마다 잰다. 넘치면 행 · 카드를 줄이거나 장을 둘로 나누고,
  부록 표처럼 꼭 빽빽해야 하는 장만 `bl-sl--dense` 를 준다.

### 색 — `data-c`

색은 인라인 style 에 적지 않는다. 부품에 `data-c` 를 주면 그 요소에서 `--c`(선 · 채움) ·
`--cl`(옅은 바탕) · `--cm`(중간 바탕)이 다시 계산된다.

| `data-c` | 토큰 | 쓰는 자리 |
|---|---|---|
| `1` ~ `6` | `--br-cat-N` (어두운 장은 `--br-cat-dark-N`) | 범주 · 부서 · 단계 |
| `navy` | `--br-navy` | 기준 · 본사 |
| `ok` · `warn` · `alert` | 완료 · 협의 · 지연 텍스트색 | 상태 |
| `mute` | `--br-mark-mute` | 참고 · 계획 |

### 글자 — 본문 1.0rem · 라벨 계열만 그 아래

본문은 1.0rem 이상, 절대 하한 0.78rem. 1.0rem 아래 글자는 아래 클래스(또는 그 안)에만 준다.
검사기(`check_live.py` 의 `NOTE_CLS`)가 렌더한 화면에서 잰다.

- 주석 · 띠 — `.bl-note` · `.bl-src` · `.bl-chip` · `.bl-eyebrow` · `.bl-stat-t` · `.bl-rf` · `.bl-ord` ·
  `.bl-code` · `.bl-pg` · `.bl-ev`
- 라벨 — `.bl-lbl` · `.bl-cap` · `.bl-mini` · `.bl-axis` · `.bl-dl`(막대 안 값) · `.bl-leg`(범례) ·
  `.bl-num`(번호 원) · `.bl-pill` · `.bl-badge` · `.bl-delta` · `.bl-asof` · `.bl-pgref` · `.bl-stamp` ·
  `.bl-conf` · `.bl-seg`
- 조작 단추 — `.bl-fig-ab` · `.bl-replay` · `.bl-shot-open` · `.bl-route-st` · `.bl-sc-pick`

본문을 담는 그릇(카드 · 행)은 여기 없다. 카드 문장에 라벨 클래스를 덧씌워 하한을 피하지 않는다.

표기 부품 — 확신도 `.bl-conf--fixed|plan|open|none`(넷으로 고정) · 번호 원
`.bl-num--solid|ring|gold|sq|sm|lg` · 알약 `.bl-pill--solid|tint|dash` · 배지 `.bl-badge(--line)` ·
증감 `.bl-delta(--down|--flat)` · 기준일 `.bl-asof` · 쪽 링크 `.bl-pgref` · 도장 `.bl-stamp`.

### 부품 색인 — 카탈로그의 어느 장을 복사하나

장 id 는 `live-catalog.html` 의 `<section id>` 다. 주소 끝에 `#장id` 를 붙여 열면 그 장에서
시작한다. 머리띠 왼쪽의 코드(C01 · T03 …)가 같은 장을 가리킨다.

| 분류 | 부품 | 주 클래스 | 장 id · 코드 |
|---|---|---|---|
| 장 짜임새 | 목차 | `.bl-agenda` | `agenda` · 00 |
| | 장 간지 | `.bl-sl--chapter` · `.bl-chapter` · `.bl-chapter-nav` | `ch1` ~ `ch5` |
| | 마무리 | `.bl-fin` · `.bl-fin-l1` · `.bl-fin-l2` · `.bl-fin-mk` · `.bl-fin-ty` | `fin` |
| | 부록 간지 | `.bl-sl--apxdiv` · `.bl-apxdiv` | `apx` |
| | 예상 질문 | `.bl-qa` | `qa` |
| 카드 | 상단 색띠 카드 · 연결자 · 결론 띠 | `.bl-tc` · `.bl-conn--tri` · `.bl-tc-out` | `tcard` · C01 |
| | 좌측 색띠 행 · 초점 행 | `.bl-lc` · `.bl-focusset` | `focusrow` · C02 |
| | 색 머리 열 카드 · 준비도 눈금 | `.bl-hc` · `.bl-meter` | `hcard` · C03 |
| | 표기 모음 | `.bl-chip` · `.bl-num` · `.bl-pill` · `.bl-badge` · `.bl-stamp` · `.bl-conf` | `marks` · C04 |
| 시간 · 조직 | 이중 레인 연표 | `.bl-lanes` | `lanes` · T01 |
| | 단계 연혁 · 기간 브래킷 · 점 타임라인 | `.bl-span` · `.bl-dots` | `history` · T02 |
| | 간트 (오늘 선 · 빗금 계획) | `.bl-gantt` · `.bl-gantt-bar[data-s]` · `.bl-gantt-today` | `gantt` · T03 |
| | 조직도 (위임 화살 · TF 열) | `.bl-org` · `.bl-org-units` | `org` · T04 |
| | 역할 매트릭스 | `.bl-matrix` | `matrix` · T05 |
| | 작은 조직 · 개념 곡선 | `.bl-orgtree` · `.bl-avatar` · `.bl-svgbox` | `team` · T06 |
| | 역할 분담표 (RACI) | `.bl-raci` | `raci` |
| | 월별 실행 표 | `.bl-road` | `monthly` |
| 수치 · 차트 | 수치 타일 · 도넛 · 강조 막대 | `.bl-kpis` · `.bl-donut-box` · `.bl-bar--key` | `kpi` · N01 |
| | 100% 누적 가로 막대 · 워터폴 | `.bl-stack` · `.bl-wf` | `stack` · N02 |
| | 조작형 누적 막대 (비율/금액 · 보기 · 대상) | `.bl-sc` | `sc` · N03 |
| | 랙형 100% 세로 막대 · 세그먼트 | `.bl-rack` · `.bl-seg` · `data-when` | `rack` · N04 |
| | 체크 목록 · 와플 · 카드 고르기 | `.bl-checks` · `.bl-waffle` · `.bl-pickset` | `waffle` · N05 |
| | 격자 히트맵 · 검색 결과 목업 | `.bl-heat` · `.bl-mock` | `heat` · N06 |
| | 계단형 상승 열 | `.bl-stair` | `stair` · N07 |
| | 쉐브론 띠 · 그룹 표 | `.bl-chev` · `.bl-tbl` | `chev` · N08 |
| | 히어로 띠 · 비용 막대 | `.bl-hero` | `hero` · N09 |
| 흐름 · 결정 | 좌우 대비 (지양 · 지향) | `.bl-vs` | `vs` · F01 |
| | 두 해 나란히 (확정 실선 · 검토 점선) | `.bl-vs--years` | `years` · F02 |
| | 대기열 시뮬레이션 | `.bl-simq` | `simq` · F03 |
| | 결정 요청 판 · 도장 · 실행 길 | `.bl-decide` · `.bl-road2` | `decide` · F04 |
| | 파이프라인 열 · 되먹임 호 | `.bl-pipe` | `pipe` · F05 |
| | SVG 흐름도 (곡선 연결 · 움직이는 점) | `.bl-flowbox` · `.bl-fl` · `.bl-fl-dot` · `.bl-node` | `flow` · F06 |
| | 구성도 (경계 · 차단선) · 성숙도 카드 | `.bl-fl-zone` · `.bl-fl--cut` | `net` · F07 |
| | 바통 흐름 · 고스트 번호 열 | `.bl-baton` · `.bl-ghost` | `baton` · F08 |
| 화면 · 시연 | 탭 (단계와 묶기) | `.bl-tabset` · `data-at` | `tabs` · S01 |
| | 코치 마크 장면 | `.bl-scenebox` · `.bl-scene` | `coach` · S02 |
| | 화면 데모 (목업 행 · 커서 · 캡션 바) | `.bl-mock` · `.bl-cursor` · `.bl-capbar` · `.bl-replay` | `explorer` · S03 |
| | 포털 목업 · 시안 탭 | `.bl-mock-app` | `portal` · S04 |
| | 캡처 + 주석 열 | `.bl-shot` | `shot` · S05 |
| | 시안 토글 그림 | `.bl-fig` · `.bl-fig-ab` | `fig` · S06 |
| | 노선도 (역 자동 순환) | `.bl-route` | `route` · S07 |
| | 상태 격자 시뮬레이션 | `.bl-simg` | `simg` · S08 |
| | 근거 패널 · 원문 · 영상 | `.bl-ev` · `[data-doc]` · `[data-video]` | `media` · S09 |
| 연출 패턴 | 패턴첩 장의 연출(데이터 그리기 · 경로 그리기 · 전과 후 · 흐름 · 화면 시연 …) · 단계 전개 + 흐리게(`data-dim`) — `MOTION.md` 「2」 | `bl-a` 조합 · `data-dim` | `mx-data` · `mx-path` · `mx-steps` · `mx-swap` · M01~M04 |
| 맞춤 본문 | 장 안 `<style data-own>` 으로 새로 짠 깔때기 — 범위 · 토큰 · rem · 움직임 분기 견본 | 자기 접두어 `x-` | `own` · X01 |
| 참고 | 아이콘 135종 · 움직임 견본 · 조작 요약 | `.bl-i` · `.bl-a` | `icons` · `motion` · `keys` |

### 부품 속성 — 값으로 모양을 바꾸는 자리

장째 복사한 뒤 숫자를 바꾸거나 모양을 고칠 때 본다. 값은 전부 마크업의 `data-*` 또는 `style="--변수: 값"` 이다.

| 부품 | 자리 | 뜻 |
|---|---|---|
| 간트 `.bl-gantt` | `style="--bl-gantt-n: 12"` | 기간 열 수. 1열은 과제 이름 |
| | 막대 `<i class="bl-gantt-bar" data-s="now" style="grid-column: 2 / 4">` | 칸 자리 — 2열이 첫 기간, `2 / 4` 는 2·3열(끝 번호 앞까지). `data-s` 는 `done` 완료 · `now` 진행 · `plan` 계획(빗금) · `hold` 협의 · `risk` 지연 · `mute` 참고 |
| | `<i class="bl-gantt-today" style="--at: .37">` | 오늘 선. 시간 영역에서의 비율 0~1 (이름 열 제외) |
| | 행 `.bl-gantt-r.is-focus` · 묶음 `.bl-gantt-g` | 강조 행 · 묶음 머리 행 |
| | 머리 `.bl-gantt-h` 의 `<b style="grid-column: span 4">10월</b>` | 머리 칸이 기간 열 몇 개를 덮는가(월 하나 = 주 넷 등) |
| 숨은 단계 표식 | `<i class="bl-mk" data-f="1"></i>` | 크기 없는 단계. 탭 · 장면 · 초점 행이 열린 표식 수를 세어 상태를 바꾼다 |
| 탭 `.bl-tabset` | 첫 단추는 `data-at` 없음 · 둘째부터 `data-at="1"` · `"2"` … | 첫 탭은 0단계(장에 들어온 직후) 기본 판. 단계 n 이 열리면 `data-at="n"` 탭으로 넘어간다. 탭 수 − 1 개의 `.bl-mk` 표식과 노트의 `[클릭]` 을 같이 둔다. 첫 탭에도 `data-at="1"` 을 주면 첫 클릭이 헛클릭이 된다. 검토(펼침)에서는 첫 탭이 보인다 |
| 100% 누적 가로 막대 `.bl-stack` | 칸 `style="--v: 42"` · `.is-est` | 칸 폭(비율 숫자 · 합이 100 이 아니어도 된다) · 추정치 빗금. 끝 값은 `.bl-stack-val` |
| 랙 `.bl-rack` | 칸 `style="--v: 40"` · 열 수 `style="--n: 8"` | 칸 높이 비율 |
| 세로 막대 · 워터폴 | `.bl-vbar` 의 `--v` · `.bl-wf` 칸의 `--lo` · `--hi` | 최댓값 100 기준 높이 · 시작과 끝 |
| 막대 기준선 · 게이지 · 진행 | `.bl-bar-ref` 의 `--at` · `.bl-gauge` · `.bl-prog` 의 `--v` | 0~1 비율 |
| 준비도 눈금 `.bl-meter` | `data-v="3"` | 다섯 칸 중 채울 칸 수 |
| 계단 `.bl-stair` | 칸 `style="--lv: 2"` · 열 수 `--n` | 높이 단 |
| 와플 `.bl-waffle` | `data-total` · `data-on` · `data-alt` · `data-cols` · `data-icon` | 칸 수 · 켠 칸 · 다른 색 칸 · 열 수 · 아이콘 칸(`user` 등) |
| RACI `.bl-raci` | `<td data-r="A">` (`A` · `R` · `C` · `I`) | 책임 표시 칸 |
| 흐름도 `.bl-flowbox` | `style="--ar: 2.857"` · 마디 `.bl-node` 의 `--x` · `--y` · `--w` | `--ar` 은 SVG viewBox 의 가로 ÷ 세로(1200 ÷ 420 = 2.857). 마디 자리는 viewBox 좌표를 % 로 — 가운데 (150, 60) → `--x: 12.5; --y: 14.3`, 폭 228 → `--w: 19`. 선(`.bl-fl` 의 `d`)은 같은 viewBox 좌표로 마디 가장자리에서 시작 · 끝낸다. 마디 수를 바꾸면 마디 가운데 y 를 같은 간격으로 다시 잡아 % 로 바꾸고(넷이면 60 · 160 · 260 · 360) 선 끝점도 같이 옮긴다 |
| 개념 곡선 `.bl-svgbox` | `--ar` · 라벨 `.bl-svgbox-l` 의 `--x` · `--y` · `data-a="l"` 또는 `"r"` | 상자 비율 · 라벨 자리(%) · 정렬 |
| 커서 데모 `.bl-cursor` | `--x0` · `--y0` · `--x1` · `--y1` · `--x2` · `--y2` | 시작 · 누를 곳 · 끝 자리(%) |
| 캡션 바 `.bl-capbar` | 문구마다 `style="--i: 0"` … | 차례로 바뀌고 마지막 문구가 남는다 |
| 상태 격자 `.bl-simg` | 칸 `data-s` (`a` · `m` · `w` · `i`) | 녹 · 황토 · 회 · 적 |
| 점 타임라인 `.bl-dots` | 점 `li` 의 `is-done` · `is-now` · `is-plan` · `is-goal` | 완료(채운 점) · 지금(테두리 · 맥박) · 계획(회색 글자) · 목표(마름모) |
| 도넛 `.bl-donut` | `style="--bl-donut-size: 18rem"` · 범례 `li` 의 `data-v` | 도넛 크기(기본 15rem) · 손댈 때 가운데에 올릴 글자(없으면 범례 값). 가운데 숫자는 구멍에 맞춰 저절로 줄고 단위는 1rem 아래로 내려가지 않는다 |
| 등장 · 차례 | `.bl-a` 의 `--i` · `--d` | 순번(80ms 씩) · 추가 지연(초) |

기준 덱에 이미 있는 어휘 — 표지 `.bl-cover-k` · `.bl-sig` · 보고 요지 `.bl-gist` · `.bl-ask` ·
로드맵 `.bl-road` · 카드 `.bl-card` · 수치 `.bl-stat` · 막대 `.bl-bars` · 표 `.bl-tbl` ·
결론 줄 `.bl-concl` — 은 `live-standard.html` 에서 가져온다.

### 움직임 — `.bl-a` 12계열 · 내장 움직임 · 단계

장이 처음 화면의 55% 를 넘을 때 엔진이 장에 `.in` 을 단다. 한 번 달면 떼지 않는다 —
돌아와도 다시 재생하지 않는다. 다시 보이려면 장 안에 `.bl-replay` 단추를 둔다.

```html
<div class="bl-tc bl-a bl-a--up" style="--i: 2">…</div>   <!-- --i 순번 · 80ms 씩 늦게 -->
<b class="bl-stamp bl-a bl-a--stamp" style="--d: .6s">결정</b>   <!-- --d 추가 지연 -->
```

| 계열 | 클래스 | 쓰는 자리 |
|---|---|---|
| 등장 | `--up` · `--left` · `--fade` · `--pop` · `--drop` | 카드 · 행 · 마디 |
| 강조 | `--stamp` · `--pulse` · `--ripple` · `--glow` · `--blink` · `--shake` | 결정 도장 · 현재 단계 · 경고 |
| 성장 | `--gx` · `--gy` | 막대 · 면 |
| 선 | `--draw` · `--flow` | SVG 경로 그리기 · 흐르는 점선 |
| 이동 | `--run` · `--spin` | 경로 위 이동 · 회전 |
| 글자 | `--type` · `--strike` · `--tint` | 타자 · 취소선 · 흑백→컬러 |

- **내장 움직임** — 막대 · 간트 막대 · 누적 막대 성장, 도넛 그리기, 도장, 마무리 형광 막대,
  노선도 열차, 흐름선 점, 커서 이동은 클래스 없이 저절로 돈다.
- **숫자** — `data-count` 를 단 숫자는 장에 들어올 때 0 에서 제 값까지 오른다(1.1초).
  `data-count="roll"` 은 자리마다 굴러 멈춘다. 소수 자리는 `data-dec`.
- **차례** — `data-stagger` 를 단 부모는 자식마다 `--i` 를 달아 준다(값을 주면 그 선택자로 센다).
- **단계 전개** — 요소에 `data-f="1"` · `"2"` … 같은 번호는 함께 열린다. 발표 모드나 펼침(E)을
  끈 상태에서만 접힌다. → 가 장보다 단계를 먼저 연다. 발표자 노트의 `[클릭]` 과 맞춘다.
- JS 가 없거나 감속 모드(`prefers-reduced-motion`) · 인쇄면 처음부터 최종 모습이다.
  **애니메이션에 정보를 싣지 않는다.**

### 위젯 — 속성만 달면 엔진이 움직인다

| 위젯 | 마크업 | 동작 |
|---|---|---|
| 탭 | `.bl-tabset` > `.bl-tabs > button[data-v]` + `.bl-pane[data-v]` | 누르면 그 판. 둘째 단추부터 `data-at="단계"` 를 주면 발표 중 그 단계에서 넘어간다 — 단계는 장 안의 `<i class="bl-mk" data-f="n">` 표식이 만든다. 첫 단추에는 `data-at` 을 주지 않는다 |
| 세그먼트 | `.bl-seg[data-key="view"] > button[data-v]` · `[data-when="view=plan"]` | 고른 값이 가장 가까운 `[data-scope]`(없으면 장)에 붙고 맞는 요소만 보인다. `&` 로 조건을 잇는다 |
| 시안 토글 | `.bl-fig > [data-v]` + `.bl-fig-ab > button[data-v]` | 시안 전환 · 그림을 누르면 크게 보기 |
| 노선도 | `.bl-route-st[data-i]` + `.bl-route-card[data-i]` | 역이 2.6초마다 돈다. 누르면 고정 · 다시 누르면 풀림 |
| 장면 | `.bl-scenebox` > `.bl-scene[data-sc]` + `.bl-scene-nav button[data-k]` | 열린 단계 수만큼 장면이 넘어간다. 목록을 누르면 5.6초마다 끝까지 |
| 초점 행 | `.bl-focusset` > 행 `[data-i]` + `.bl-focus-cards > [data-i]` | 열린 단계 번호의 행을 밝히고 짝 카드를 연다. 행을 누르면 고정 |
| 카드 고르기 | `.bl-pickset` > `[data-pick]` · `[data-when-pick]` | 고른 카드만 남기고 흐림 · 짝 설명이 열린다 |
| 도넛 | `scripts/donut.py --live` 출력 | 조각 · 범례에 손을 대면 그 항목이 가운데로 올라온다 |
| 와플 | `.bl-waffle[data-total][data-on]` (`data-alt` · `data-cols` · `data-icon`) | 칸을 깔아 준다 |
| 조작형 누적 막대 | `.bl-sc` 안 `<script type="application/json" class="bl-sc-data">` | 비율/금액 · 보기 · 대상 고르기 · 값 풍선 |
| 시뮬레이션 | `.bl-simq` · `.bl-simg` | 장이 화면에 있을 때만 돈다. 난수 고정 — 매번 같은 장면 |

조작형 누적 막대 데이터:

```json
{"unit": "백만원",
 "cats":   [{"k": "lab", "name": "인건비", "c": "1"}],
 "groups": {"h": "본사", "b": "지사"},
 "views":  {"nat": "성격별", "fn": "단계별"},
 "rows":   [{"id": "h1", "name": "본사 고객지원", "sub": "전화 · 메일", "grp": "h",
             "total": 420, "rate": -6.2, "key": true,
             "nat": [["lab", 260], ["out", 80, true]], "fn": [["ans", 180]],
             "note": "…", "src": "…"}]}
```

`views` 가 없으면 행마다 `parts` 배열을 쓴다. 항목의 셋째 값 `true` 는 추정치(빗금)다.
`"pick": false` 인 행은 대상 고르기에서 처음에 빠져 있다.

### 겹창 — 근거 · 부록 겹쳐 보기 · 원문 · 영상 · 크게 보기

겹창이 열려 있는 동안 키는 겹창 것이다. → 를 눌러도 뒤의 장이 넘어가지 않는다. Esc 로 닫는다.

**근거 패널** — 수치 옆 출처 칩 `<button class="bl-ev" data-ev="E1">출처</button>` 이 문서 끝
JSON 한 벌을 연다. `data-ev="E1,E2"` 는 탭으로 뜬다. `data-claim` 은 패널 위 「주장」 줄이다.

```json
{"ev": {
   "E1": {"title": "주간 문의 접수 기록 — 4주 집계", "grade": "R", "key": "접수 대장 · 2026-09",
          "facts": ["주간 평균 360건 · 휴일 제외 20일 기준", "같은 고객 7일 안 재문의 18%"],
          "hl": ["주간 평균 360건"],
          "src": "고객지원팀 접수 대장", "date": "2026-10-02", "url": "https://…",
          "note": "…", "gnote": "등급 근거", "use": "이 근거를 쓴 곳",
          "doc": "doc-guide", "dochl": 1,
          "imgs": [["cap-log", "접수 대장 화면 — 강조 줄 둘"]]}},
 "img": {"cap-log": "data:image/…"},
 "hl":  {"cap-log": [[0.05, 0.376, 0.9, 0.061]]},
 "grades": {"S": "사내 규정"}}
```

- 필수는 `title` · `grade` · `src`. 등급은 A 1차 공식 자료 · B 학술·전문기관 · C 언론·2차 자료 ·
  R 직접 조회·집계. `grades` 로 늘릴 수 있다.
- `facts` 는 배열이거나 ` / ` 로 나눈 문자열이다. `hl` 문구는 형광으로 칠한다.
- `imgs` 의 id 는 `img` 표에 있어야 하고, `hl` 상자는 캡처 위 0~1 사각형 `[x, y, w, h]` 다.
  캡처가 있으면 확대 · 끌기 · 맞춤 · 하이라이트 상자로 바로 가는 뷰어가 붙는다.
- `doc` 은 원문 보기 단추를 붙인다. 원문을 닫으면 근거 패널로 돌아온다.
- 검사기가 칩 키 · 필수 항목 · 캡처 id · 상자 값 · 원문 id 를 전부 맞춰 본다.

**부록 겹쳐 보기** — `<button data-peek="raci">` 는 그 장을 지금 장 위에 겹쳐 연다.
발표 중 `data-peek-seq` 를 단 단추들은 화면 클릭마다 차례로 열고 닫는다.

**원문** — `<button data-doc="doc-guide">` · 같은 id 의 `<script type="application/json">` 에
`{"title", "html", "file": {"name", "type", "b64"}}`. `html` 안의 `.bl-hl` 단락(`data-label`)이
강조이고 단추마다 그 강조로 바로 간다. `file` 을 주면 원본 내려받기가 생긴다.

**영상** — `<button data-video="vid-demo">` · 같은 id 의 `<script type="text/plain"
data-type="video/webm">` 에 base64. 처음 열 때 한 번만 풀어 둔다. 파일 경로를 줘도 된다.

**크게 보기** — `.bl-fig` 안의 그림 · `.bl-shot` 의 캡처(`.bl-shot-open`) · `[data-zoom]` 을
누르면 화면 가득 띄운다. 시안이 여럿이면 ← → 로 넘긴다.

### 발표 — 키 · 모드 · 대본 창

**단축키는 파워포인트 슬라이드 쇼와 같다.** 파워포인트를 써 본 사람이면 따로 배우지 않고 발표한다.
파워포인트에 없는 우리 기능(메모 · 펼침 · 가로)만 파워포인트가 쓰지 않는 글자에 두었다.

| 조작 | 키 | 비고 |
|---|---|---|
| 처음부터 발표 | F5 | 전체화면 · 조작판 · 진행선 · 커서 숨김 · 레이저 저절로 켜짐 |
| 이 장부터 발표 | Shift+F5 (F) | 다시 누르면 끝. 창을 화면 크기로 키우거나 F11 도 발표 |
| 발표자 보기(대본 창) | Alt+F5 (S) | 두 번째 화면용. 팝업이 막히면 같은 창 오른쪽에 |
| 다음 | → ↓ · PgDn · Space · Enter · N | 단계가 있으면 단계부터. 발표 중 화면 클릭도 다음 |
| 이전 | ← ↑ · PgUp · Backspace | |
| 처음 · 끝 | Home · End | |
| 쪽 이동 | 숫자 Enter · `0` 표지 · `a` 숫자 Enter | 세 자리까지 · 3초 안에 · Backspace 지움 · 없는 쪽은 「없음」 |
| 검은 화면 · 흰 화면 | B (.) · W (,) | 아무 키나 누르면 돌아온다 |
| 펜 | P · Ctrl+P | 화면에 쓴다. 다시 누르거나 Esc 로 끄면 레이저로 돌아간다. 도구판에서 색(빨강 · 파랑 · 검정) |
| 형광펜 · 지우개 | Ctrl+I · Ctrl+E | 지우개는 닿은 획을 지운다 |
| 필기 지우기 · 숨기기 | E · Ctrl+M | E 는 이 장만. 필기는 장마다 남고 창을 닫으면 사라진다(파일에 안 남음) |
| 펜 끄기 | Ctrl+A · Esc | |
| 레이저 | Ctrl+L (L) | 발표 모드에서는 저절로 켜진다 |
| 메모 | M | 지금 장의 발표자 노트를 지면 아래에 |
| 펼침 | X | 단계 전부 보기 ↔ 한 단계씩 |
| 가로 보기 | V | 휠 한 칸 = 한 장 |
| 도움말 · 닫기 | F1 (?) · Esc | Esc 는 겹창 → 숫자 입력 → 도움말 → 펜 → 발표 순으로 닫는다 |

괄호 안은 예전 키(별칭)다. 그대로 듣지만 조작판에는 파워포인트 키를 적는다.

**키를 바꾸려면** 덱 끝(뷰어 스크립트 앞)에 JSON 을 둔다. 적은 동작만 바뀌고 나머지는 그대로다.
도움말 · 조작판 단추 글자가 함께 바뀐다.

```html
<script type="application/json" id="bl-keys">{"pen": ["p", "ctrl+p"], "notes": ["m"]}</script>
```

동작 이름 — `next` `prev` `first` `last` `fromStart` `fromHere` `presenter` `black` `white` `pen`
`highlighter` `eraser` `erase` `ink` `arrow` `laser` `notes` `expand` `horiz` `help`.
키 이름 — 글자 · `f1`~`f12` · `arrowright` 등 · `space` · `enter` · `backspace` · `pageup` · `home` ·
`.` `,` `?`. 조합은 `ctrl+` · `alt+` · `shift+` (맥의 ⌘ 는 `ctrl`).

- 글자 키는 물리 위치로 읽는다 — 한글 입력 상태에서도 P · B · W · M 이 그대로 듣는다.
- 발표 중 화면 아래 끝에 마우스를 대면 조작판이 잠깐 보인다. 창을 화면 크기로 키우거나
  F11 을 눌러도 발표 모드로 들어간다.
- 발표 중 화면 클릭은 「다음」이다. 단추 · 칩 · 탭 · 고르기 카드 같은 조작 요소는 빠진다.
  장 전용 스크립트가 장 안 요소에 클릭 처리기를 달면 엔진이 그 요소를 저절로 뺀다.
- 가로 보기에서는 휠 한 칸이 한 장이다. 세로 보기에서는 옆으로 60px 넘게 밀면 넘긴다(단계 포함).

**발표자 노트** `data-notes` — 여는 태그와 같은 줄에 적는다. 문체는 `~한다` 형(지면 문체 규칙의
예외). 빈 줄로 문단을 나눈다.

| 문법 | 대본 창 표시 |
|---|---|
| `[클릭]` | 「클릭 n」 배지. 지금 단계와 맞춰 지난 것 · 다음 것을 칠한다 |
| `[넘김]` · `[임의]` | 회색 배지 |
| `**굵게**` | 강조 |
| `→ 전환: …` | 다음 장으로 넘어가는 말. 따로 상자 |
| `※ …` | 읽지 않는 메모. 배정 시간에서 뺀다 |

**대본 창** — 지금 · 다음 장 노트, 경과 시간, 장별 배정 시간과 누적. 배정은 읽는 글자 수를
분당 300자로 나눠 5초 단위로 올린다(최소 20초 · 간지 5초 · 부록 0초). 경과 시간이 지금 장의
예정 구간보다 45초 넘게 늦거나 이르면 시계 색이 바뀐다. 노트는 대본 창에서 고칠 수 있고 이 브라우저에 저장된다
(`localStorage` 키 `bl-script:문서명`). 「수정분 내보내기 · 수정분 복사 · 전체 대본 · 전부 원복」
단추가 있다. 고친 내용은 HTML 에 반영되지 않으므로 내보낸 뒤 `data-notes` 에 옮긴다.

### 아이콘 · 기호

```html
<i class="bl-i bl-i--server" aria-hidden="true"></i>        <!-- 글자색 · 글자 크기를 따른다 -->
<span class="bl-itile" data-c="2"><i class="bl-i bl-i--users"></i></span>   <!-- 색 타일 -->
```

Lucide 1.52.0 의 135종을 CSS 마스크로 `blue-live.css` 에 심었다(ISC · 고지는
`assets/LICENSE-Lucide.txt`). 목록에 없는 이름은 그려지지 않는다 — 늘리려면
`scripts/make_icons.py` 의 `ICONS` 에 더하고 다시 돌린다.

| 묶음 | 이름 |
|---|---|
| 사람 · 조직 | user users user-check user-round user-cog building-2 building briefcase landmark handshake graduation-cap hand store |
| 문서 | file-text files file-search file-check file-spreadsheet folder folder-open clipboard-check clipboard-list book-open notebook-pen pen-line stamp presentation receipt inbox ticket tag image video play |
| 수치 | chart-column chart-bar chart-line chart-area chart-spline chart-no-axes-combined trending-up trending-down activity gauge sigma coins wallet scale |
| 기술 | server database hard-drive cpu circuit-board cloud monitor laptop smartphone globe network cable radio-tower plug bot brain sparkles scan-search |
| 보안 | lock lock-open shield-check shield-alert key-round eye gavel |
| 흐름 | workflow git-branch git-merge waypoints route map repeat refresh-cw arrow-right arrow-up-right send upload download share-2 link layers boxes blocks package layout-grid |
| 판단 | check circle-check x circle-x triangle-alert info circle-help lightbulb target flag badge-check award trophy list-checks list-todo search filter star circle-alert |
| 도구 · 현장 | settings cog wrench rocket zap factory flask-conical microscope thermometer mouse-pointer-click megaphone mail message-square messages-square phone headset bell map-pin |
| 시간 | clock calendar calendar-check timer hourglass |

본문 폰트(Pretendard 서브셋)에 기호를 넣어 두었다 — 로마 숫자 Ⅰ~Ⅹ · 원 숫자 ①~⑫ ·
화살표 ↑ ↓ ↔ ↕ ↗ ↘ ↵ ↻ ⇒ · 수식 ∑ − √ ≈ ≠ ≤ ≥ · 도형 □ ▪ △ ▶ ▷ ▽ ◀ ◆ ◇ ○ ◦ ✗ ·
괄호 〈 〉 《 》 「 」 『 』 【 】. 다른 기호는 시스템 글꼴로 떨어져 모양이 갈라진다 —
필요하면 `scripts/make_font_subset.py` 의 `SYMBOLS` 에 더해 다시 만든다.

### 스크립트

```bash
# 도넛 — 각도를 손으로 적지 않는다. --raw 는 건수, 가운데 숫자 · 단위 · 설명을 준다
python3 scripts/donut.py --live --raw --total 360 --unit 건 --caption "주간 문의" \
        --labels "전화,메일,채팅,방문" 182 96 64 18
# 출력 첫 줄은 HTML 주석이라 통째로 붙여도 된다. --total 은 범례처럼 천 단위 쉼표로 찍힌다.
# 가운데 숫자는 구멍에 맞춰 저절로 줄지만, 단위는 짧게(h · 건 · %) 두는 편이 읽기 좋다
python3 scripts/make_icons.py --check         # 아이콘 CSS 가 목록과 맞는가 (오프라인)
python3 scripts/make_font_subset.py --check   # 폰트 서브셋이 글자 목록과 맞는가
python3 scripts/check_live.py 보고서.html --shots out/   # 30항목 + 장마다 화면 PNG
```

### 검사기가 보는 것 · 눈으로 볼 것

`check_live.py` 30항목 — 문체(원문 · 그려진 글자) · 토큰 밖 hex · 두 CSS · rem · 노트 · 머리띠 ·
꼬리띠 · 쪽번호 · 마크 · 워터마크 · 마크 짝 · 브랜드 자리 · 근거 JSON · 스타일 · 폰트 · 지면 끝 ·
조작판 겹침 · 글자 하한 둘 · 가로 넘침 · 데이터 마크 대비 · 엔진 기동 · 단계와 `[클릭]` ·
정의 없는 클래스 · 보이지 않는 글자 · 세로 넘침(16:9 한 화면 · 좁은 폭 꼬리띠) · 맞춤 CSS(고정 영역 ·
범위 · 토큰 · rem · 이름 · 움직임 분기) · 본문 표현(글 · 표뿐인 장 비율 — 주의만).

검사기가 못 보는 것 — 제목 핵심구 `<em>` · 장 종류 표시(`data-apx` 등) · 여백과 균형 · 내용의
맞고 틀림 · 고르지 않은 탭 판(검토에서는 첫 판만 보인다) · 겹쳐 놓인 그림 마디끼리의 겹침.
`--shots` 로 남긴 장별 PNG 를 넘겨 보고, 탭 · 세그먼트가 있는 장은 판마다 눌러 본다.

### 엔진 API · 이벤트

장 전용 스크립트는 `live-viewer.js` **뒤에** 둔다.

```js
blDeck.go(3); blDeck.next(); blDeck.prev();       // 장 이동 (0 이 첫 장)
blDeck.present(); blDeck.laser(true); blDeck.presenter();
blDeck.index; blDeck.step; blDeck.slides;         // 지금 장 · 단계 · 장 목록
document.addEventListener('deck:sync', e => { /* e.detail: el · cur · list · step · steps · staged */ });
// deck:present {on} · deck:presenter {open} · deck:laser {on}
```

점검 순서는 `references/rules.md` §2-2 에 있다.

---

## 7. 슬라이드 19종

| # | 슬라이드 | 배경 | 쓰는 자리 |
|---|---|---|---|
| 01 | 표지 | `#071b45` | 문서 첫 장 |
| 02 | 목차 | `#f4f6f8` | 파트 4~5개까지 |
| 03 | 파트 간지 | `#071b45` | 파트 시작 |
| 04 | 핵심 정리 | `#101827` | 파트 끝. 카드 6개가 상한 |
| 05 | 단일 수치 강조 | `#f4f6f8` | 한 슬라이드 = 한 주장 |
| 06 | 도넛 차트 | `#f4f6f8` | 구성비 3~5구간 |
| 07 | 막대 차트 | `#f4f6f8` | 순위·비교 7구간까지 |
| 08 | 비교 2열 | `#f4f6f8` | 전후 · A안B안 · 평균대비 |
| 09 | 지표 표 | `#f4f6f8` | 과제·지표 목록. 행 7개가 상한 |
| 10 | 3단계 로드맵 | `#f4f6f8` | 실행 계획 |
| 11 | 일정 타임라인 | `#f4f6f8` | 기간 병행과 마일스톤 |
| 12 | 순환 고리 | `#f4f6f8` | 회차가 되돌아옴. 칸 3~6개 · `diagram.py cycle` |
| 13 | 통과 관문 | `#f4f6f8` | 넷을 다 넘어야 성과. 관문 2~5개 · `diagram.py gate` |
| 14 | 단계 계단 | `#f4f6f8` | 단마다 기준 상승. 단 3~6개 · `diagram.py stair` |
| 15 | 연표 | `#f4f6f8` | 실적과 계획이 갈리는 지점. 시점 3~8개 · `diagram.py track` |
| 16 | 구간 블록 | `#f4f6f8` | 시간축 위 구간. 「언제부터 언제까지 얼마나」 · `diagram.py interval` |
| 17 | 결정 요청 표 | `#f4f6f8` | 지표 표의 변형. 「미결 시 영향」 열 필수. 행 4개가 상한 |
| 18 | 부록 간지 | `#071b45` | 본문과 부록의 경계. 이후 지면에 `data-apx` |
| 19 | 마무리 CTA | `#071b45` | 행동 하나만 제시 |

---

## 8. 레이아웃 체크리스트

새 슬라이드를 만들면 반드시 확인한다.

1. `section.scrollHeight === 1080`, `scrollWidth === 1920`
   넘치면 `flex:1` 컨테이너에 `min-height:0`을 주고 행 높이를 줄인다.
2. 절대 위치 라벨이 차트를 덮지 않는가 → 차트와 라벨을 다른 그리드 컬럼 / flex 형제로 분리
3. 푸터가 콘텐츠와 겹치지 않는가 → 항상 마지막 형제, `flex-shrink:0`
4. 24px 미만 텍스트가 없는가 (`%` 첨자만 예외)
5. 데이터 마크 대비 2:1 이상, 인접 색 중복 없음
6. 파이 `<path>` 없음, 도넛 dasharray가 원주와 일치
7. 토큰 밖 raw hex 없음
8. 우측 상단 `.br-mark`가 있고, 본문과 겹치지 않으며, 배경 밝기와 변형이 맞는가
   → 마크는 상단 여백 띠 안에만 둔다. 우측 상단에 콘텐츠를 붙이지 않는다.

`python3 scripts/check_deck.py deck.html --shots out/`이 위 1·4·5·6·7·8과 문체를 자동
검사하고 슬라이드별 PNG를 남긴다. 판정은 17항목이다.

| # | 항목 | 실패하면 |
|---|---|---|
| 1 | 문체 — 존댓말·평서형 종결 없음 | `~합니다` · `~한다` 로 끝나는 말을 명사형으로 고친다 |
| 2 | 파이 없음 — 도넛만 사용 | 손으로 적은 `<path d="M…A…">` 를 `donut.py` 산출물로 바꾼다 |
| 3 | 색 — 토큰 밖 raw hex 없음 | 슬라이드의 hex 를 `--br-*` 변수로 바꾼다 |
| 4 | 슬라이드 크기 1920x1080 | `flex:1` 컨테이너에 `min-height:0` 을 주고 행 높이를 줄인다 |
| 5 | 글자 크기 24px 미만 없음 | `%` 첨자(`.br-sup`) 외에는 24px 이상으로 올린다 |
| 6 | 데이터 마크 대비 2:1 이상 | 밝은 지면에서 `--br-soft-*` 를 빼고 데이터 램프를 쓴다 |
| — | 데이터 마크가 실제로 그려지는가 | `var()` 하나가 풀리지 않으면 값이 조용히 사라진다 |
| — | 막대 길이가 값에 비례하는가 | 단위가 섞인 그룹과 `data-bar-scale="row"` 는 제외 |
| — | 본문 안전영역 | 본문 잉크가 y 1000px 아래로 내려가지 않는다. 푸터까지 완충을 둔다 |
| 7 | 본문 영역이 위아래로 겹치지 않는다 | 여백을 줄이거나 내용을 덜어 아래 영역을 밀어내지 않게 한다 |
| 8 | 브랜드 마크가 우측 상단에 있다 | `.br-mark` 를 빠뜨린 슬라이드에 넣는다 |
| 9 | 브랜드 마크가 본문과 겹치지 않는다 | `logoHeight` 를 줄이거나 본문을 여백 띠 밖으로 뺀다 |
| 10 | 로고 변형이 배경 밝기와 맞는다 | `data-on` 값과 `logo` · `logoOnLight` 짝을 맞춘다 |
| 11 | 도넛 dasharray 검산 | `donut.py` 로 다시 생성한다. 손계산하지 않는다 |
| 12 | 배경 워터마크가 마크와 다른 자산인가 | 심볼만 잘라 낸 판을 `watermark` 에 준다 |
| — | 지시선 주석이 잘리지 않고 점과 글자를 잇는가 | 세로 막대 안에 두고, 세로획을 글자 쪽 끝에 둔다 |

11번은 도넛을 쓰지 않은 덱에서 `주의`로 나온다. **`주의`는 허용되고 `실패`만 완료를 막는다.**

**실패가 0이어도 PNG를 눈으로 확인한다.** 어색한 여백은 스크립트가 잡지 못한다.

---

## 9. 브랜드 자리

교체 지점은 두 곳뿐이다. 하나는 끝났고 하나는 남아 있다.

### 브랜드 마크 — 적용 완료

모든 슬라이드 우측 상단의 `.br-mark`. 표지도 본문도 같은 자리다.
`data-on="dark"`는 딥네이비·다크 배경, `data-on="light"`는 밝은 지면을 뜻하며
`apply_brand.py`가 이 값을 보고 로고 변형을 고른다.

이 저장소에는 HCT 로고 두 벌이 `brand/hct/`에 들어와 있고 `brand.json`이 가리킨다.
로고를 지정하지 않은 브랜드에서는 `.br-wordmark`의 회사명 텍스트가 대신 들어간다.

**남은 것** — 원본 로고의 마크 영역이 264×86px 이다. 화면 발표에는 충분하지만 인쇄에는
모자란다. SVG 나 고해상도 원본이 생기면 교체하고 `make_logo_variants.py`로 두 벌을
다시 뽑는다.

### 사내 폰트 — 프리텐다드로 확정

HTML 은 저장소가 들고 있는 서브셋을 쓰므로 어디서 열어도 같은 글자가 나온다.

**PPTX 는 다르다.** PowerPoint 는 PC 에 설치된 폰트만 쓰고 `assets/fonts/` 의 파일을
보지 못한다. `pptx/tokens.js` 의 `F` 가 이름으로 `Pretendard` 를 지목하지만, 설치되지
않은 PC 에서는 PowerPoint 가 제멋대로 대체한다. pptxgenjs 는 대체 목록을 받지 않아
한 이름만 적을 수 있다.

- 사내 PC 에 프리텐다드를 배포했다면 → 그대로 둔다
- 아직 배포 전이라면 → `F` 세 줄을 `'맑은 고딕'` 으로 되돌려 쓴다

설치용 파일은 https://github.com/orioncactus/pretendard 의 릴리스에서 받는다.
`assets/fonts/` 의 것은 KS X 1001 로 잘라 낸 웹용이라 설치용으로 쓰지 않는다.

### 연락처

`brand.json`의 `email` · `website` · `phone`에 적는다. 빈 문자열로 두면 해당 줄과 행이
통째로 사라진다. 사내 배포용 덱은 대개 이쪽이 맞고, `brand/hct/brand.json`도 그렇게 돼 있다.
