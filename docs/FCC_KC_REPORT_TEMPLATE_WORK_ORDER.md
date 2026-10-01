# Blue Report FCC/KC 맞춤형 보고서 템플릿 작업 지시서

이 문서는 HCT **Blue Report** 디자인 시스템을 `Blue Report FCC/KC Insight` 분석
보고서에 확장하기 위한 에이전트용 실행 지시서다. 단일 예제 보고서가 아니라 플러그인이
동적으로 사용할 수 있는 기본 템플릿, 특수분석 템플릿, 데이터 슬롯, 검사 규칙과 통합
문서를 함께 만드는 것이 목표다.

저장소 루트에서 에이전트에게 다음 한 줄을 지시한다.

```text
docs/FCC_KC_REPORT_TEMPLATE_WORK_ORDER.md를 처음부터 끝까지 읽고, 안전 경계를 지키면서 실제 템플릿 제작과 검증까지 수행해라.
```

## 1. 역할과 최종 목표

당신은 HCT Blue Report 디자인 시스템 담당 에이전트다. 기존 Blue Report의 디자인 언어를
기본값으로 유지하면서, `Blue Report FCC/KC Insight`의 다양한 분석 결과를 정확하고 일관되게
표현할 수 있는 재사용 가능한 보고서 템플릿 패키지를 제작한다.

단순히 보기 좋은 샘플 PDF 한 개를 만드는 것으로 끝내지 않는다. 다음 결과가 함께 있어야
한다.

- 목적별 기본 템플릿 A/B/C
- 분석 업무별 특수 템플릿
- 공통 디자인 토큰과 의미 기반 컴포넌트
- 템플릿 manifest와 샘플 fixture schema
- HTML/PDF 기준 시안과 DOCX/PPTX 이식 기준
- 자동 검사와 시각 검수 결과
- Blue Report 1.3.1 Report Model 통합 가이드

## 2. 작업 위치와 안전 경계

모든 수정은 현재 `blue-report` 체크아웃 안에서만 수행한다. 저장소 안의 경로는
반드시 저장소 루트 기준 상대 경로로 사용한다.

Blue Report 플러그인 1.3.1 후보 worktree가 같은 PC에 있다면 다음 경로를 읽기 전용 참고
자료로 사용할 수 있다.

```text
D:\HCT-FCC-KC-MINI-SERVER-ALL-IN-ONE-20260722\runtime\development\worktrees\1.3.1
```

이 경로가 없는 환경에서는 이 문서에 포함된 제품·계약 설명을 기준으로 진행하고, 없는
플러그인 파일을 추측으로 대체하지 않는다.

반드시 지킬 사항은 다음과 같다.

- 작업 전 `AGENTS.md`와 `git status`를 확인한다.
- 기존 사용자 변경을 덮어쓰지 않는다.
- 플러그인 1.3.1 worktree는 읽기만 하고 수정하지 않는다.
- 배포된 1.3.0 런타임, 운영 서버, 서비스, 스케줄러와 터널을 수정하거나 재시작하지 않는다.
- deploy, publish, migration, 원격 업로드를 실행하지 않는다.
- 명시적 요청 없이 commit, push, pull, reset 또는 브랜치 삭제를 실행하지 않는다.
- 토큰, 쿠키, 비밀번호, OAuth subject, 실제 클라이언트 IP, 내부 절대경로와 사용자 질문
  전문을 템플릿·fixture·로그·보고서에 넣지 않는다.
- 이번 작업은 개인 Codex Template Gallery용 스킬 생성이 아니라 Blue Report 저장소용
  제품 템플릿 패키지 제작이다.

## 3. 먼저 읽을 자료

작업을 시작하기 전에 다음 Blue Report 파일을 전부 읽는다.

- `AGENTS.md`
- `README.md`
- `.claude/skills/blue-report/README.md`
- `.claude/skills/blue-report/SKILL.md`
- `.claude/skills/blue-report/references/rules.md`
- `.claude/skills/blue-report/assets/blue-report.css`
- `.claude/skills/blue-report/assets/blue-doc.css`
- `.claude/skills/blue-report/assets/doc-*.html`
- `brand/hct/brand.json`
- `docs/CODEX_DECK_PROMPT.md`

1.3.1 후보 worktree가 있다면 아래 자료도 읽기 전용으로 확인한다.

- `docs/REPORT-TEMPLATE-SYSTEM-1.3.1.md`
- `docs/REPORT-CONTRACT-1.3.1.md`
- `plugin/skills/fcc-kc-reporting/references/report-tool-contract.md`
- `plugin/skills/fcc-kc-reporting/references/brand-guidelines.md`
- `runtime/app/report_model.py`
- `runtime/app/enhanced_report_renderers.py`
- `runtime/app/render_report_pptx.mjs`
- `runtime/app/test_report_131.py`
- `report-design/prototypes/README.md`
- `report-design/prototypes/Blue Report-REPORT-TEMPLATE-A-EXECUTIVE-EDITORIAL.docx`
- `report-design/prototypes/Blue Report-REPORT-TEMPLATE-B-ANALYTICAL-DASHBOARD.docx`
- `report-design/prototypes/Blue Report-REPORT-TEMPLATE-C-EVIDENCE-DOSSIER.docx`

## 4. Blue Report FCC/KC Insight 제품 설명

Blue Report FCC/KC Insight는 FCC/KC PUBLIC 인증 데이터를 서버에서 결정론적으로 분석하고,
AI가 검증된 결과를 해석하는 분석 플러그인이다.

주요 분석 업무는 다음과 같다.

- 인증 건수와 기간별 추이
- 제조사·신청자·시험기관 비교
- 두 개 이상 코호트 비교
- 제조사/신청자 360° 프로필
- 시험기관 360° 프로필
- 시험기관 이동·재진입 흐름
- 제품군·기술분류·인증분류 교차 분석
- 데이터 품질과 집계 기준 설명
- 데이터 버전 간 변경 내역
- 텔레매틱스 특수 분류 분석
- 최대 20개 엔터티 일괄 비교
- 특정 인증의 정확한 근거와 공개 연락처
- 증거 목록, 출처와 데이터 계보 추적

정확한 건수, 기간, 정렬, 모집단, 중복 제거, 엔터티 해소와 커버리지 판정은 서버가
계산한다. 템플릿이나 AI는 전달받은 수치를 다시 합산, 재분류 또는 재정렬하면 안 된다.
AI는 비교, 의미 해석, 위험, 제한사항과 다음 행동을 작성할 수 있다. 검증된 사실, AI 해석,
사용자 또는 검토자 메모는 시각적으로 구분한다.

모든 보고서는 가능한 범위에서 다음 신뢰 정보를 보존한다.

- `sourceDataVersion`
- `sourceWatermark`
- `appliedPeriod`
- `appliedFilters`
- `entityResolution`
- `populationDefinition`
- `recordGrain`
- `coverageComplete`
- `recordsCoverageComplete` 또는 bounded-evidence 상태
- 서버 계산 `metrics`
- 품질 요약과 `warnings`
- evidence identifiers와 source references
- snapshot, report-model, consistency와 lineage checksum

이 보고서는 법률 자문, 인증 승인 예측, 시장점유율, 매출 또는 CRM의 진실을 의미하지
않는다.

## 5. 목표 브랜드 구조

기존 1.3.1 시안의 `h_inno` 개인 서비스 브랜드는 1.3.0 호환용 레거시로 보존한다. 이번
작업은 이를 덮어쓰지 않고 다음 신규 브랜드 프로필의 시각 기준을 만든다.

- 브랜드 프로필 ID: `hct_blue_report`
- 발행사/회사 브랜드: HCT, 주식회사 에이치시티
- 제품명: Blue Report FCC/KC Insight
- 기본 디자인 시스템: HCT Blue Report

표현 원칙은 다음과 같다.

- HCT를 주 발행 브랜드로 사용한다.
- Blue Report FCC/KC Insight는 제품명 또는 서비스 서명으로 사용한다.
- 두 개의 경쟁하는 대형 로고를 배치하지 않는다.
- HCT 로고는 각 페이지 우측 상단의 고정 브랜드 마크로 사용한다.
- 제품명은 표지 제목, 헤더 또는 푸터의 제품 서명으로 표현한다.
- 본문 페이지에는 기존 HCT 심볼 워터마크를 제한적으로 사용한다.
- 밝은 배경과 어두운 배경에 맞는 기존 로고 변형을 정확히 사용한다.
- 로고를 자르거나 늘리거나 재색칠하지 않는다.
- 회사 연락처가 비어 있으면 임의 연락처를 만들지 않는다.

Blue Report의 딥네이비 표지, 밝은 A4 지면, 코발트 강조, 편집형 정보 위계와 넓은
여백을 유지한다. 카드, 장식용 색 띠와 불필요한 테두리를 남용하지 않는다. 파이 차트는
사용하지 않으며 필요한 경우 검산 가능한 도넛을 사용한다. 색만으로 상태를 구분하지 않고
라벨, 기호 또는 패턴을 함께 쓴다.

모든 색은 기존 `--br-*` 토큰 또는 정식으로 추가한 공유 토큰으로 사용한다. 개별
템플릿에 raw hex를 직접 작성하지 않는다.

## 6. 형식별 공통 기준

### A4 문서

- 세로 210×297mm, 가로 297×210mm
- 인쇄 본문 최소 10.5pt
- 본문 대비 최소 4.5:1
- 각 페이지에 독립적인 헤더, 푸터와 출처 표시
- 표가 다음 페이지로 넘어가면 헤더 행 반복
- 긴 식별자와 한·영 혼합 문자열 줄바꿈
- 페이지 번호, 보고서 제목, 데이터 버전과 계보 식별자 표시

### PPTX

- 발표 문구는 개조식·명사형 사용
- 한 슬라이드에 하나의 핵심 주장
- A4 문서와 동일한 Report Model의 수치와 근거 사용
- 가능한 차트는 편집 가능한 네이티브 객체 사용
- 별도로 복제한 수동 수치와 문구를 원본처럼 관리하지 않음

### 교차 형식

PDF, DOCX와 PPTX는 하나의 immutable Report Model에서 파생되는 것을 전제로 한다.
다음 값은 형식이 달라도 일치해야 한다.

- 데이터 버전과 watermark
- 기간, 필터와 엔터티 해소
- 모집단 정의와 레코드 단위
- 커버리지 상태
- 서버 계산 지표
- evidence와 품질 상태
- consistency projection checksum

## 7. 기본 템플릿 3종

현재 1.3.1의 A/B/C 개념을 유지하되 HCT Blue Report 스타일로 재설계한다. 세 템플릿은
색상만 다른 변형이 아니라 정보 구조와 시각적 우선순위가 달라야 한다.

### A — Executive Editorial

- 기본 방향: A4 세로
- 대상: 경영진, 영업 책임자, 의사결정자
- 목적: 결론, 위험, 권고와 다음 행동
- 권장 분량: 4~6페이지
- 흐름: 결정 제목과 검증 범위 → 핵심 결론과 서버 KPI → 결정적 비교 또는 추이 →
  해석과 의사결정 경계 → 권고·위험·다음 행동 → 근거와 계보 요약

### B — Analytical Dashboard

- 기본 방향: A4 가로
- 대상: 분석가, 영업 운영, 프로젝트 실무자
- 목적: 수치 비교, 추이, 분류와 순위 검토
- 권장 분량: 3~8페이지
- 흐름: 분석 범위와 필터 계약 → KPI 매트릭스 → 기간 추이 → 코호트/엔터티 비교 →
  제품·기술·시험기관 구성 → 품질 상태와 제한사항 → 근거 드릴다운

### C — Evidence Dossier

- 기본 방향: A4 세로
- 대상: 품질, 심사, 감사와 증거 검토 담당
- 목적: 재현성, 근거 제출과 예외 확인
- 권장 분량: 4~40페이지
- 흐름: 문서 통제와 범위 → 모집단·레코드 단위·필터·엔터티 해소 → 서버 수치와
  원본 필드 대응 → 품질 예외와 제한사항 → bounded evidence register → checksum과
  lineage → 선택적 검토/승인란

## 8. 개별 특수분석 템플릿 11종

A/B/C만 만들고 끝내지 않는다. 아래 분석마다 독립적으로 열고 검증할 수 있는 완성형
템플릿을 제작한다. 공통 컴포넌트와 토큰은 공유하되 페이지 순서와 핵심 시각화는 분석
질문에 맞게 달라야 한다.

### 1. Certification Trend Report

- 월·분기·연도별 인증 추이
- 부분 기간을 실선, 점선, 음영과 명시적 라벨로 구분
- 전년 동기와 전체 연도 비교를 혼동하지 않도록 경고
- 추세 변화와 실제 인증 상태 변화를 동일시하지 않음

### 2. Cohort Comparison Report

- 두 개 이상 코호트의 동일 기준 비교
- 모집단이나 기간이 다르면 비교 가능 여부 표시
- 동일 축과 단위 사용
- 총량, 변화율과 구성 차이 분리

### 3. Manufacturer/Applicant 360 Report

- 엔터티 해소 결과와 별칭
- 인증 추이, 제품 포트폴리오, 사용 시험기관과 최근 변화
- 공개 근거와 공개 연락처
- 관측 인증 기록을 시장점유율 또는 매출로 표현하지 않음

### 4. Test Lab 360 Report

- 시험기관 엔터티 해소
- 기간별 처리 기록, 제조사 구성과 제품/기술 구성
- 유입, 이탈과 재진입 요약
- 순위의 모집단과 기준을 함께 표시

### 5. Lab Flow & Re-entry Report

- 시험기관 간 이동, 유입, 이탈과 재진입 표현
- 데이터에 맞는 흐름도와 전이 매트릭스
- 흐름 총합과 고유 엔터티 수를 혼동하지 않음
- 관측된 순서를 인과관계로 해석하지 않음

### 6. Product × Technology Taxonomy Report

- 제품군, 기술과 인증분류 매트릭스 또는 히트맵
- 행/열 합계와 교차 셀의 집계 단위 표시
- 다중 분류가 있으면 비가산성 경고
- 주요 조합과 미분류 영역 분리

### 7. Data Quality & Count Semantics Report

- 전체 모집단, 반환 행, 고유 인증과 고유 엔터티 구분
- 결측, 중복, 미해소, 모호한 엔터티와 커버리지 상태
- 수치가 다른 이유를 설명하는 count-semantics 패널
- 품질 경고를 숨기거나 작은 각주로 축소하지 않음

### 8. Data Version Change Digest

- 기준 버전과 비교 버전
- 신규, 변경, 제외와 미확정 항목 분리
- 데이터셋에서 사라진 항목을 인증 취소로 단정하지 않음
- 영향받은 엔터티, 제품, 시험기관과 근거 표시

### 9. Telematics Special Analysis Report

- 4개 상호배타 분류
- 6개 집계형 그룹
- 3개 독립 순위 목록
- 위 세 체계를 별도 시각 영역으로 분리
- 집계형 그룹을 합산하거나 상호배타 분류처럼 표현하지 않음
- 분류 정의와 포함/제외 기준을 첫 부분에 표시

### 10. Batch Entity Review Report

- 최대 20개 제조사 또는 시험기관 비교
- 작은 배수, 비교표, 상태 배지와 예외 요약
- 긴 엔터티명과 별칭 처리
- 페이지 분할 시 열 제목과 엔터티 식별 정보 반복

### 11. Exact Evidence & Public Contacts Report

- 정확한 인증 식별자와 source reference
- bounded-evidence 상태
- 공개 출처에서 확인된 연락처만 표시
- 연락처별 출처와 확인 상태 표시
- 추정 연락처와 비공개 개인정보 금지
- 긴 evidence register와 계보 부록 지원

각 특수 템플릿의 manifest에는 다음을 선언한다.

- `templateId`
- `templateVersion`
- `displayName`
- `recommendedReportPurpose`
- `recommendedLayoutProfile`
- `defaultOrientation`
- `supportedFormats`
- `minimumPages`
- `maximumPages`
- `requiredSections`
- `optionalSections`
- `supportedVisualModules`
- `sampleFixture`
- `knownLimitations`

## 9. 필수 시각 모듈

기존 ranked bar, line과 clustered column만 반복하지 않고 아래 모듈을 Blue Report 문법으로
설계한다.

공통 모듈:

- report cover
- document control
- verified scope/filter band
- server metric card
- AI interpretation block
- warning/limitation banner
- recommendation/action block
- ranked horizontal bar
- time-series line chart
- cohort comparison chart
- quality summary panel
- evidence register
- public contact table
- lineage/checksum block
- long-table continuation
- empty-state와 insufficient-data state

특수 모듈:

- partial-period trend
- entity identity-resolution panel
- lab flow diagram
- transition matrix
- product×technology heatmap
- count-semantics reconciliation panel
- version-delta cards
- telematics exclusive-class panel
- telematics aggregate-group panel
- independent-ranking panel
- batch-entity small multiples
- evidence-coverage indicator

모듈은 특정 회사명이나 샘플 수치에 하드코딩하지 않고 의미 기반 클래스와 슬롯을 사용한다.

```html
<span data-field="sourceDataVersion"></span>
<span data-field="populationDefinition"></span>
<span data-field="recordGrain"></span>
<span data-field="coverageComplete"></span>
<div data-metric-id="..."></div>
<tr data-evidence-ref="..."></tr>
<section data-narrative-origin="server_fact|ai_interpretation|human_note"></section>
```

## 10. fixture와 데이터 규칙

운영 수치를 템플릿에 하드코딩하지 않는다. 시각 검증용 fixture를 별도 JSON으로 만들고
모든 샘플 페이지를 같은 fixture 계약에 기반시킨다.

모든 샘플에는 눈에 잘 보이게 다음 문구를 표시한다.

```text
DESIGN FIXTURE · 운영 분석 결과 아님
```

fixture는 다음 경우를 포함해야 한다.

- 정상적인 완전 커버리지
- 일부 evidence만 반환된 상태
- 부분 연도 또는 부분 월
- 0건 데이터
- 단일 코호트와 2~5개 코호트
- 최대 20개 엔터티
- 긴 한글/영문 엔터티명
- 결측값
- 미해소 또는 모호한 엔터티
- 공개 연락처 없음
- 긴 evidence identifier
- 1페이지를 넘는 표
- 불완전 coverage 경고
- 특수문자와 한·영 혼합 텍스트

공통 fixture schema는 최소한 다음 의미를 지원한다.

- report metadata
- scope와 filters
- entity resolution
- server-origin metrics
- chart specifications와 series
- quality와 warnings
- bounded AI narrative
- evidence register
- public contacts
- lineage와 checksums

차트는 fixture가 전달한 값과 순서를 그대로 표시한다. 템플릿 코드에서 합계, 비율과
순위를 새로 계산하지 않는다.

## 11. 산출물

### A. 저장소에 남길 템플릿 소스

- FCC/KC 보고서 전용 additive style layer
- A/B/C 기본 템플릿 3종
- 특수분석 템플릿 11종
- 공통 재사용 컴포넌트
- 템플릿 manifest
- JSON fixture와 schema
- 템플릿 선택 규칙

현재 저장소 구조에 맞춰 배치하되 권장 구조는 다음과 같다.

```text
.claude/skills/blue-report/assets/fcc-kc/
  templates/
  components/
  fixtures/
  schemas/
  manifest.json
```

기존 `blue-report.css`와 `blue-doc.css`를 우선 재사용한다. FCC/KC 전용 CSS는 additive
layer로 만들고 기존 토큰이나 색 체계를 복제하지 않는다.

### B. 개별 시각 샘플

- A/B/C 기본 템플릿의 HTML과 PDF
- 특수분석 11종 각각의 독립 실행 가능한 HTML과 PDF
- 모든 페이지의 PNG 렌더
- 생성 결과는 `decks-out/fcc-kc/`처럼 gitignored 출력 폴더에 배치
- 모든 샘플에 DESIGN FIXTURE 표시

### C. DOCX/PPTX 이식 기준

수동으로 서로 다른 수치와 내용을 가진 문서를 중복 작성하지 않는다. 다음을 제공한다.

- A/B/C 각각의 대표 DOCX 디자인 시안
- A/B/C 각각의 대표 PPTX 디자인 시안
- 모든 특수 모듈의 DOCX/PPTX 변환을 보여주는 module catalog
- HTML/PDF/DOCX/PPTX 간 동일성 규칙
- 편집 가능한 차트와 이미지로 고정해야 하는 차트의 구분
- 세 형식에서 일치해야 할 consistency-projection 항목

### D. 통합 문서

다음 문서를 작성한다.

1. `docs/FCC_KC_REPORT_TEMPLATE_SYSTEM.md`
   - 브랜드 구조, 템플릿 종류, 선택 규칙, 토큰, 모듈, 데이터 슬롯과 제한사항
2. `docs/FCC_KC_REPORT_INTEGRATION_GUIDE.md`
   - 1.3.1 Report Model 필드와 템플릿 슬롯 매핑
   - `report_model.py`에 필요한 domain adapter 목록
   - PDF/DOCX/PPTX 렌더러 적용 방법
   - 레거시 `h_inno`와 신규 `hct_blue_report` 공존 방법
   - 후속 플러그인 개발자가 수정할 파일 목록
   - 마이그레이션 순서, 회귀 위험과 템플릿별 테스트
3. 템플릿 매트릭스
   - 보고 목적, 기본 A/B/C, 방향, 필수 차트, 필수 근거, 권장 페이지 수와 지원 형식

## 12. 자동 검사

기존 Blue Report 검사 체계를 확장하여 새 템플릿도 기계적으로 검증한다. 최소 검사 항목은
다음과 같다.

- A4 크기와 방향
- 페이지 overflow
- 최소 글자 크기와 본문 대비
- raw hex 금지
- HCT 로고와 배경별 변형
- 모든 페이지의 헤더와 푸터
- Blue Report 제품명
- 데이터 버전, 기간, 모집단과 레코드 단위
- 커버리지 상태, 페이지 번호와 계보/evidence 정보
- 파이 차트 금지와 도넛 수치 검산
- 데이터 라벨 누락
- 색만으로 상태를 표현하는지 여부
- 표 헤더 반복과 긴 문자열 clipping
- 한국어 인코딩 깨짐
- fixture 수치와 표시 수치의 일치
- 서버 사실, AI 해석과 사람 메모의 구분
- 텔레매틱스 분류 의미 위반
- 부분 기간 경고 누락
- DESIGN FIXTURE 표시
- 비밀값, 로컬 경로와 개인정보 패턴

새 템플릿과 검사기를 `scripts/verify_repo.py`에 포함하고 기존 템플릿의 회귀도 함께
검증한다. 필요하면 `check_doc.py`를 확장하거나 FCC/KC 전용 검사기를 추가하되 동일 규칙을
여러 스크립트에 중복 구현하지 않는다.

## 13. 시각 검수

자동 검사만으로 완료 처리하지 않는다.

- 모든 HTML 페이지를 PNG로 렌더한다.
- PDF도 페이지별 PNG로 렌더해 HTML과 비교한다.
- DOCX와 PPTX는 사용 가능한 렌더러로 이미지 검수한다.
- 겹침, 잘림, 과도한 여백, 표 밀도, 축 라벨과 각주 가독성을 확인한다.
- 밝은 면과 어두운 면의 로고 변형을 확인한다.
- A/B/C가 실제로 다른 정보 위계를 갖는지 확인한다.
- 11개 특수 템플릿이 일반 막대 차트 보고서로 퇴화하지 않았는지 확인한다.
- 렌더러가 없어 특정 형식을 검수하지 못하면 추정으로 통과 처리하지 말고 정확히 보고한다.

## 14. 완료 조건

다음 조건을 모두 충족해야 완료다.

- A/B/C 기본 템플릿 3종 존재
- 특수분석 템플릿 11종 존재
- 각 특수 템플릿이 독립적으로 열리고 렌더됨
- 공통 디자인 토큰과 컴포넌트 공유
- HCT 발행 브랜드와 Blue Report 제품명의 올바른 공존
- 기존 Blue Report 템플릿 회귀 없음
- fixture, schema, manifest와 선택 규칙 존재
- 통합 가이드 존재
- HTML/PDF 샘플과 페이지 PNG 존재
- DOCX/PPTX 대표 시안과 모듈 매핑 존재
- 자동 검사 실패 0
- `python scripts/verify_repo.py` 통과
- 모든 템플릿에 신뢰, 근거와 계보 정보 표시
- 운영 데이터나 비밀값 포함 없음
- `git diff`에 의도한 파일만 포함

실패가 남아 있으면 완료라고 보고하지 않는다.

## 15. 최종 보고 형식

최종 보고는 한국어로 작성하고 다음을 포함한다.

1. 구현한 템플릿 목록
2. A/B/C와 특수분석 매핑 표
3. 생성·수정한 파일
4. 디자인 시스템의 주요 결정
5. 플러그인 Report Model과의 통합 방법
6. 실행한 검사 명령
7. 검사별 통과/주의/실패 수
8. HTML/PDF/DOCX/PPTX/PNG 산출물 경로
9. 시각 검수 결과
10. 기존 Blue Report 회귀 결과
11. 플러그인 개발 단계에서 남은 작업
12. 알려진 제한사항
13. 최종 `git status`

먼저 현재 저장소와, 존재한다면 1.3.1 보고서 구조를 조사해 짧은 구현 계획을 세운 뒤
사용자 확인을 기다리지 말고 위 범위 안에서 실제 제작과 검증까지 계속 진행한다. 안전
경계를 벗어나야 하는 경우에만 중단하고 이유를 보고한다.
