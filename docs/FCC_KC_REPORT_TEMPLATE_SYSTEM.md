# Blue Report FCC/KC 보고서 템플릿 시스템

`Blue Report FCC/KC Insight` 분석 결과를 HCT **Blue Report** 디자인 언어로 찍어 내는
템플릿 묶음이다. 이 문서는 무엇이 있고 언제 무엇을 고르는지를 적는다. 만드는
방법은 `docs/FCC_KC_REPORT_TEMPLATE_WORK_ORDER.md`, 플러그인에 붙이는
방법은 `docs/FCC_KC_REPORT_INTEGRATION_GUIDE.md` 에 있다.

## 1. 브랜드 구조

| 자리 | 값 |
|---|---|
| 브랜드 프로필 ID | `hct_blue_report` |
| 발행사 | HCT · 주식회사 에이치시티 |
| 제품명 | Blue Report FCC/KC Insight |
| 디자인 시스템 | HCT Blue Report |

**발행 브랜드는 HCT 하나다.** 제품명은 로고가 아니라 글자로 적는다 — 표지 하단의
제품 서명(`.fk-signature`)과 문서 제목이 그 자리다. 경쟁하는 큰 로고 둘을 나란히
놓지 않는다. HCT 로고는 모든 쪽 머리말 오른쪽의 고정 마크(`.br-mark`)로만 쓴다.

기존 1.3.1 의 `h_inno` 개인 서비스 브랜드는 1.3.0 호환용 레거시로 남긴다. 이
템플릿은 그것을 덮어쓰지 않는다.

## 2. 템플릿 14종

### 기본 3종 — 무엇을 하려는 문서인가

| ID | 이름 | 방향 | 쪽 | 대상 | 목적 |
|---|---|---|---|---|---|
| `fcc-kc-a-executive-editorial` | A — Executive Editorial | 세로 | 6 | 경영진 · 영업 책임자 | 결론 · 위험 · 권고 |
| `fcc-kc-b-analytical-dashboard` | B — Analytical Dashboard | **가로** | 5 | 분석가 · 실무자 | 수치 비교 · 추이 · 순위 |
| `fcc-kc-c-evidence-dossier` | C — Evidence Dossier | 세로 | 6 | 품질 · 심사 · 감사 | 재현성 · 근거 제출 |

셋은 색만 다른 변형이 아니다. **정보 위계가 다르다.**

- **A** 는 2쪽에서 결론과 서버 지표를 먼저 내놓고, 근거는 뒤로 미룬다. 경영진이
  앞 두 쪽만 보고 결정할 수 있어야 한다.
- **B** 는 결론을 앞세우지 않는다. 범위 계약 → 지표 → 추이·순위 → 비교·구성 →
  품질 → 근거 순으로, 읽는 사람이 스스로 판단하도록 늘어놓는다.
- **C** 는 문서 통제와 모집단 정의가 1·2쪽이다. 수치보다 **어떻게 나온 수치인지**가
  먼저다. 필드 대응표와 체크섬, 검토란이 있다.

### 특수 분석 11종

| ID | 분석 | 앞세우는 도해 |
|---|---|---|
| `fcc-kc-s-certification-trend` | 인증 추이 | 부분 기간을 가른 추이선 |
| `fcc-kc-s-cohort-comparison` | 코호트 비교 | 두 계열 막대 · 비교 가능 여부 판정 |
| `fcc-kc-s-manufacturer-360` | 제조사 360 | 엔터티 해소 패널 + 포트폴리오 순위 |
| `fcc-kc-s-test-lab-360` | 시험기관 360 | 제조사 구성 순위 + 유입·이탈 표 |
| `fcc-kc-s-lab-flow-reentry` | 시험기관 이동 | 흐름 단계 + 전이 행렬 |
| `fcc-kc-s-product-technology-taxonomy` | 제품군 × 기술 | 교차 히트맵 |
| `fcc-kc-s-data-quality-count-semantics` | 품질·집계 의미 | 집계 의미 대조표 |
| `fcc-kc-s-data-version-change-digest` | 버전 변경 | 신규·변경·제외·미확정 카드 |
| `fcc-kc-s-telematics-special` | 텔레매틱스 | 세 체계를 가른 세 패널 |
| `fcc-kc-s-batch-entity-review` | 일괄 비교 | 같은 축 작은 배수 20칸 |
| `fcc-kc-s-exact-evidence-contacts` | 근거·연락처 | 커버리지 지표 + 근거 목록 |

특수 11종은 모두 **4쪽**이다 — 범위·지표 / 분석 핵심 / 품질·제한 / 근거·계보.
신뢰 정보가 늘 같은 쪽에 있어야 읽는 사람이 매번 찾지 않는다.

### 고르는 규칙

1. 분석 종류가 정해져 있으면 **특수 템플릿을 먼저** 쓴다.
2. 정해지지 않았으면 목적으로 고른다 — 결정이면 A, 검토면 B, 제출이면 C.
3. 대상이 경영진인데 근거 전량이 필요하면 **A + C 두 벌**을 낸다. 한 벌에
   섞으면 둘 다 못 쓴다.

`assets/fcc-kc/manifest.json` 이 이 규칙과 각 템플릿의 필수·선택 구획,
지원 형식, 알려진 제한사항을 기계가 읽을 수 있는 꼴로 담는다.

## 3. 색과 활자

**새로 만든 색이 없다.** 전부 `--br-*` 토큰이고, 크기는 `--bd-fs-*` 다.
FCC/KC 덧층(`assets/fcc-kc/fcc-kc.css`)은 색과 크기를 **읽기만** 한다.

| 쓰임 | 토큰 |
|---|---|
| 주인공 데이터 마크 | `--br-cobalt` |
| 맥락 데이터 마크 | `--br-mark-mute` |
| 값의 크기(히트맵) | `--br-bar-1` ~ `--br-bar-7` 단조 램프 |
| 코호트 두 계열 | `--br-cat-1` · `--br-cat-2` |
| 서술 출처 — AI | `--br-cat-3` |
| 경고 | `--br-warn-*` |
| 위험 | `--br-alert-*` |

**상태를 색만으로 말하지 않는다.** 커버리지·근거 상태·서술 출처·버전 변경은
모두 기호(●◐○ ■▲✎ +−)와 낱말을 함께 쓴다. 흑백 인쇄와 색각 이상에서 색은
사라지지만 낱말은 남는다.

## 4. 시각 모듈

공통 16종과 특수 12종이 있다. 클래스 이름은 전부 `fk-` 로 시작한다.

| 모듈 | 클래스 |
|---|---|
| 표지 · 제품 서명 | `.fk-cover-title` · `.fk-signature` |
| 검증 범위 띠 | `.fk-scope` · `.fk-cov` |
| 서버 지표 카드 | `.fk-metrics` · `.fk-metric` |
| 서술 출처 블록 | `.fk-narr` + `data-narrative-origin` |
| 경고 · 제한 배너 | `.fk-warn` · `.fk-warn--limit` |
| 권고 · 다음 행동 | `.fk-actions` · `.fk-act` |
| 순위 가로 막대 | `.fk-rank` |
| 추이 선 (부분 기간 표시) | `.fk-line` · `.fk-path--partial` |
| 품질 요약 | `.fk-quality` |
| 근거 목록 | `.fk-evi` |
| 공개 연락처 | 표 + 출처·확인일 열 |
| 계보 · 체크섬 | `.fk-lineage` |
| 이어지는 표 표시 | `.fk-cont` |
| 빈 상태 | `.fk-empty` |
| 시안 도장 | `.fk-fixture` |
| 가로 지면 · 2단 | `.bd-page--land` · `.fk-cols` |
| 교차 히트맵 | `.fk-hm` |
| 전이 행렬 | `.fk-mx` |
| 흐름 단계 | `.fk-flow` |
| 작은 배수 | `.fk-sm` |
| 버전 변경 카드 | `.fk-delta` |
| 텔레매틱스 세 패널 | `.fk-tele--excl` · `--agg` · `--rank` |
| 집계 의미 대조 | `.fk-cnt` |
| 코호트 비교 | `.fk-coh` |
| 근거 커버리지 | `.fk-covind` |
| 엔터티 해소 패널 | `.fk-idp` |

## 5. 데이터 슬롯

모듈은 회사명·수치를 품지 않는다. 렌더러가 채우는 자리만 있다.

```html
<span data-field="scope.sourceDataVersion"></span>
<span data-field="scope.populationDefinition"></span>
<span data-field="scope.recordGrain"></span>
<span data-field="scope.coverageComplete"></span>
<div  data-metric-id="cert_total"></div>
<div  data-chart-id="trend_monthly"></div>
<tr   data-evidence-ref="..."></tr>
<section data-narrative-origin="server_fact|ai_interpretation|human_note"></section>
<div  data-template-id="fcc-kc-a-executive-editorial"></div>
```

빈 슬롯은 지면에서 `—` 로 보인다. 조용히 사라지면 안 채운 것을 모른다.

## 6. fixture

`assets/fcc-kc/fixtures/` 에 14종이 있다. 계약은
`assets/fcc-kc/schemas/report-model.schema.json` 이고, `verify_repo.py` 가
14종 전부를 이 스키마로 검증한다.

| fixture | 재현하는 경우 |
|---|---|
| `fixture-baseline` | 정상 · 완전 커버리지 · 부분 기간 1개월 |
| `fixture-bounded-evidence` | 근거 일부만 반환 |
| `fixture-zero-rows` | 0건 |
| `fixture-unresolved-entities` | 미해소 27 · 모호 9 |
| `fixture-batch-20-entities` | 20개사 상한 |
| `fixture-long-identifiers` | 긴 식별자·긴 법인명 |
| `fixture-all-partial-period` | 전 구간 부분 기간 |
| `fixture-no-public-contacts` | 공개 연락처 없음 |
| `fixture-mixed-text` | 한·영 혼합 · 특수문자 |
| `fixture-long-table` | 1쪽을 넘는 표 |
| `fixture-single-cohort` / `-five-cohorts` | 코호트 1개 / 5개 |
| `fixture-missing-values` | 결측값 |
| `fixture-incomplete-coverage` | 불완전 커버리지 |

모든 샘플은 `DESIGN FIXTURE · 운영 분석 결과 아님` 을 쪽마다 찍는다.
**운영 수치를 템플릿이나 fixture 에 넣지 않는다.**

## 7. 검사

```bash
python3 scripts/verify_repo.py --only fcc
```

다섯 가지를 본다.

1. **재생성 대조** — `build_fcc_templates.py` 산출물과 저장소 파일이 같은가
2. **A4 규칙** — 14종이 `check_doc.py` 9항목을 통과하는가
3. **제품 규칙** — 시안 도장 · 범위 계약(버전·기간·모집단·레코드 단위·커버리지)
   · 서술 출처 구분 · 근거와 계보 · 제품 서명 · 템플릿 식별자를 지면이 밝히는가
4. **fixture 계약** — 14종이 schema 를 지키는가
5. **안전** — 비밀값 · 로컬 절대경로 · 개인정보 패턴이 섞이지 않았는가

**자동 검사만으로 완료로 보지 않는다.** `--shots` 로 쪽마다 PNG 를 남겨 눈으로
본다. 겹침은 스크립트가 잡지만 어색한 여백과 밀도는 잡지 못한다.

## 8. 고칠 때

템플릿 HTML 을 손으로 고치지 않는다. **`scripts/build_fcc_templates.py` 를 고치고
다시 만든다.** 부품 하나를 고치면 14종에 함께 반영되어야 하기 때문이다.
손으로 고치면 재생성 대조가 잡는다.

```bash
python3 .claude/skills/blue-report/scripts/build_fcc_templates.py
python3 scripts/verify_repo.py --only fcc
```

## 9. 알려진 제한

- **DOCX·PPTX 대표 시안은 A/B/C 세 종만 있다.** 특수 11종은 HTML·PDF 만 있다.
  만드는 법과 검수 한계는 통합 가이드 5장에 적었다.
- **LibreOffice 가 이 환경에서 돌지 않아 DOCX·PPTX 를 그림으로 검수하지 못했다.**
  구조 판정만 했다. Word·PowerPoint 가 있는 환경에서 한 번 열어 봐야 한다.
- 1.3.1 워크트리를 읽지 못한 환경에서 만들었다. `report_model.py` 필드 이름은
  지시서 4장의 설명을 근거로 잡았으므로, 실제 필드와 대조가 필요하다.
- 가로 지면(B)과 세로 지면을 한 파일에 섞으면 인쇄 시 `@page` 크기를 쪽마다
  바꿀 수 없다. B 는 가로 전용 문서로 뽑는다.
