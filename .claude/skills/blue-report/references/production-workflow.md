# 제작 세부 절차

기획 대화에서 목적·청중·형식·효과를 정한 뒤 실제 제작할 때 읽는다. 아래 파일 경로는 references/가 아니라 스킬 루트를 기준으로 해석한다. 기본 브랜드는 스킬 루트의 brand/hct/brand.json이다. 보관 양식, 차트, PDF, PPTX, 검사 절차 중 요청한 형식에 필요한 절을 적용한다.

## 2-1. 보관 양식 — 이름을 짚거나 PowerPoint 가 꼭 필요할 때만

아래는 `assets/archive/` 에 보관한 양식이다. 안내 목록에서는 뺐지만 이름으로 부르면 그대로
만들어지고 검사도 같다. **사용자가 이름을 짚었거나 `.pptx` 파일이 꼭 필요할 때만 쓴다.**
먼저 고르지 않는다.

| 묶음 | `--deck` 이름 | 비고 |
|---|---|---|
| 고정 지면 덱 1920x1080 · 12종 | `internal` · `weekly` · `ax` · `team` · `exec` · `allhands` · `sales` · `project` · `training` · `strategy` · `report` · `catalog`(레이아웃 19종) | PPTX 빌드(`pptx/`)의 원본. PowerPoint 가 필요하면 여기서 |
| A4 문서 3종 | `policy`(사규) · `manual`(매뉴얼) · `notice`(공지) | |
| 웹 보드 4종 | `board` · `execboard` · `teamboard` · `gapcheck` | |
| 라이브 브리핑 | `live` | 기준 덱의 축소판 |
| FCC/KC 보고서 14종 | `assets/archive/fcc-kc/` | 인증 시험 보고서 전용 |

고정 지면 덱은 `check_deck.py`(17항목), 보관 A4 는 `check_doc.py`, 보관 보드는 `check_board.py`
가 판정한다. 보관 파일은 CSS·뷰어를 `../` 로 부르므로 **손으로 복사하지 말고 `apply_brand.py` 로
만든다** — 산출물에서는 경로를 알아서 맞춘다.

```bash
# 보관 고정 지면 덱도 회사 정보까지 한 번에
python3 scripts/apply_brand.py --brand brand.json --deck internal --single-file -o 보고서.html
```

템플릿의 `<div class="br-frame">` 블록이 슬라이드 1장이다. 필요한 종류만 남기고 지우거나,
같은 블록을 복사해 늘린다. 보관 카탈로그(`archive/deck-template.html`)의 19종은 다음과 같다.

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

## 2-2. 기준 덱 · 라이브 덱 — 새 보고서의 기본

고정 지면 없이 화면 비율을 따라가는 발표 계통이다. 사내 발표 덱의 장 짜임새 · 부품 38종 ·
애니메이션 12계열 · 발표 기능을 그대로 담았다. **용도가 따로 정해지지 않은 새 보고서는 여기서
시작한다.** 전체 사양(장 종류 · 부품 색인 · 위젯 속성 · 근거 JSON · 키)은 `README.md` 「6-3」.

| 용도 | `--deck` | 파일 | 장수 |
|---|---|---|---|
| 기준 덱 — 출발점 | `standard` | `live-standard.html` | 15 |
| 부품 카탈로그 — 재사용 · 참고 | `livecatalog` | `live-catalog.html` | 52 |

1. `live-standard.html` 을 복사해 뼈대로 쓴다. **고정 영역**(머리띠 · 꼬리띠 · 쪽번호 · 로고 ·
   워터마크 · 진행선 · 제목 형광 밴드 · 조작판 · 엔진)은 그대로 둔다.
2. **본문은 내용에 맞게 짠다.** 장마다 먼저 「이 내용은 무엇인가」를 정한다 — 흐름 · 일정 ·
   비교 · 구성 · 수치 · 구조 · 화면. 그다음 그것을 그릴 표현을 고른다(README 「6-3 본문 맞춤
   디자인」의 대응표).
   - 카탈로그(`live-catalog.html`)에 맞는 부품이 있으면 그 장을 복사해 쓰거나 고쳐 쓴다.
     장마다 머리띠 왼쪽에 부품 이름과 코드(C01 · T03 …)가 적혀 있다.
   - 없거나 내용에 안 맞으면 **새로 짠다** — 장 안 `<style data-own>` 에 CSS · SVG ·
     애니메이션을 직접 적는다. 견본은 카탈로그 `own` 장(X01). 규칙: 장 id(`#장id`)나 자기
     접두어(`x-` 등)로 범위를 묶고, 색은 `var(--br-*)` · `var(--bl-*)` 토큰만, 치수는 `rem`,
     `bl-` · `br-` 이름은 새로 짓지 않고, 고정 영역 클래스는 선택자에 넣지 않는다.
     형태 · 움직임도 계통 눈금만 — 글꼴 `var(--br-font-*)` · 모서리 `var(--bl-r-*)` · 그림자
     `var(--bl-shadow*)` · 곡선 `var(--bl-ease*)` · 길이 0.15~1.2초. 움직임은 먼저 `bl-a` 12계열로.
   - 표 · 목록만으로 장을 채우지 않는다. 표가 맞는 장(부록 · 상세 비교)만 표로 둔다.
3. 도넛은 `python3 scripts/donut.py --live …` 로 만든다. 아이콘은 `<i class="bl-i bl-i--이름">`
   (Lucide 135종 — 목록은 카탈로그 `icons` 장).
4. 수치 옆에 출처 칩 `<button class="bl-ev" data-ev="E1">` 을 달고 근거는 문서 끝
   `#bl-evidence` JSON 한 벌에 적는다(제목 · 등급 · 출처 필수).
5. 장마다 발표자 노트 `data-notes` 를 적는다 — `~한다` 형 · `[클릭]` · `**굵게**` · `→ 전환:` · `※ 메모`.
   단계 전개는 요소에 `data-f="1"` 부터 주고 노트의 `[클릭]` 과 맞춘다.
6. `python3 scripts/apply_brand.py --brand <brand.json> --deck <파일> --title "문서명" --single-file -o <결과>.html`
   로 로고 · CSS · 엔진을 한 파일에 묶는다. **`--title` 을 빼면 brand.json 의 `docTitle` 이 덱 제목을
   덮어 장마다 꼬리띠 문서명이 회사 기본값으로 바뀐다.**
7. `python3 scripts/check_live.py <결과>.html --shots out/` 30항목 실패 0 을 확인하고, `out/` 에
   장마다 남는 PNG 를 눈으로 넘겨 본다(여백 · 균형 · 겹침은 검사기가 못 본다). 29번 「본문 표현」
   주의가 뜨면 글 · 표뿐인 장을 그림으로 바꾼다.

작업본을 브라우저로 바로 보려면 `assets/` 의 `blue-report.css` · `blue-live.css` · `live-viewer.js` ·
`fonts/` 를 작업 파일 옆에 같이 둔다.

지킬 것 — 치수는 `rem` · 색은 `data-c` 와 `--br-*` 토큰(hex · rgb · 색 이름 금지, 맞춤 CSS 도 같다) · 본문 1.0rem 이상(라벨 계열만
그 아래) · 제목은 「주장 — `<em>`핵심구`</em>`」 · 본문 덩어리는 `.bl-mid` 로 세로 가운데 ·
지면 본문은 개조식 · 마무리는 「질의응답」으로 닫는다 · 쪽번호와 문서명은 비워 둔다(엔진이 채운다).

발표 키 — **파워포인트 슬라이드 쇼와 같다.** F5 처음부터 · Shift+F5 이 장부터 · Alt+F5 발표자 보기(대본) ·
→ Space Enter N 다음 · ← Backspace 이전 · 숫자 Enter 쪽 이동 · B/W 검은·흰 화면 · P(Ctrl+P) 펜 · Ctrl+I 형광펜 ·
Ctrl+E 지우개 · E 필기 지우기 · Ctrl+M 필기 숨김 · Ctrl+L 레이저 · F1 도움말 · Esc 닫기. 우리 기능은 M 메모 ·
X 펼침 · V 가로. 덱마다 바꾸려면 `<script type="application/json" id="bl-keys">` — README 「6-3」.

## 3. 차트와 도해는 반드시 스크립트로 만든다

> 이 절의 치수(viewBox 1728 · 글자 24px)는 **고정 지면 덱** 기준이다. 라이브 덱은
> `donut.py --live` 와 카탈로그의 흐름도(`.bl-flowbox`) · 개념 곡선(`.bl-svgbox`)을 쓴다 — README 「6-3」.

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

사용자가 배포용 PDF를 요청했을 때 만든다. 슬라이드 1장이 1페이지, 20in x 11.25in(16:9)이며
텍스트가 실제 글자로 남는다.

```bash
python3 scripts/to_pdf.py 보고서.html -o 보고서.pdf --notes
```

## 5. PowerPoint 판이 필요하면

사용자가 PPTX를 선택했거나 파워포인트 편집을 원하면 이 경로를 따른다. 형식 선택은 기획 대화에서 정한 값을 사용한다.

```bash
node pptx/build.js --brand <brand.json> --out <폴더> [--deck internal]
```

**설치를 사용자에게 시키지 않는다.** 스크립트가 실행될 때 없는 것만 골라 스스로 받는다
(Pillow · Playwright · Chromium · pptxgenjs). "먼저 npm install 하세요" 같은 안내를 하지 않는다.
자동 설치를 막으려면 `BLUE_REPORT_NO_INSTALL=1` 을 준다. 상태만 보려면
`python3 scripts/ensure_deps.py --for pptx --check`. 필요한 도구만 준비하려면 --prepare를 쓴다.

색·크기는 `blue-report.css` 토큰을 읽는다. 애니메이션은 없고, 폰트는 맑은 고딕·Arial 로 내린다.
도넛과 막대는 PowerPoint 네이티브 차트라 값을 직접 고칠 수 있다.
덱 내용은 `pptx/content.js` 에 있으며 HTML 덱과 함께 고친다.

만든 뒤에는 반드시 검증한다.

```bash
python3 scripts/check_pptx.py 결과.pptx
```

내장 검사기는 파일 구조·연결·텍스트를 확인한다. 실제 렌더링과 편집 가능 여부는 별도로 확인하고 그 범위를 보고한다. 다른 PPTX 스킬이 없어도 이 절차를 수행할 수 있다.

## 6. 만들고 나면 반드시 점검한다

```bash
python3 scripts/check_deck.py <작업경로>/deck.html --shots out/
```

11개 항목(개조식 문체, 파이 금지, 토큰 밖 raw hex, 슬라이드 크기 1920x1080, 24px 하한,
데이터 대비 2:1, 본문 영역 겹침, 브랜드 마크 존재, 마크와 본문 겹침, 로고 변형과 배경 밝기,
도넛 검산)을 검사하고 슬라이드별 PNG를 남긴다.

라이브 덱(기준 덱 포함)은 `python3 scripts/check_live.py <파일> --shots out/` 이 30항목을 본다 —
문체 · rem · 토큰 · 띠 · 마크 짝 · 근거 JSON · 글자 하한 · 가로 · 세로 넘침 · 조작판 겹침 ·
엔진 기동 · 단계와 [클릭] · 정의 없는 클래스 · 보이지 않는 글자 · 맞춤 CSS(고정 영역 · 토큰 · rem ·
이름) · 본문 표현(글 · 표뿐인 장 비율, 주의만) · 움직임 절제(장마다 등장 2종 · 반복 1종, 주의만). `--shots` 는 장마다 PNG 를 남긴다.

**`실패`가 0이 아니면 완료가 아니다.** `주의`는 허용된다 — 도넛을 쓰지 않은 덱에서
도넛 검산 항목이 `주의`로 나오는 것이 정상이다.
**실패가 0이어도 PNG를 눈으로 확인한다.** 겹침과 어색한 여백은 스크립트가 잡지 못한다.

## 7. 절대 어기지 않을 것

- 배경은 밝은 지면 `#f4f6f8` 1개 + 다크면 `#071b45`(표지·간지), `#101827`(핵심 정리) 2개까지. 그 외 장식색 금지.
- 파이 차트 금지. 도넛만. 손으로 적은 `<path d="M…A…">` 금지.
- 밝은 지면의 데이터 마크에 `--br-soft-*`를 쓰지 않는다. 대비 2:1에 미달한다.
- 24px 미만 텍스트 금지(고정 지면 덱). 예외는 `%` 첨자(`.br-sup`)뿐. 라이브 덱은 본문 1.0rem ·
  절대 하한 0.78rem(라벨 계열만) — `check_live.py` 가 잰다.
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
