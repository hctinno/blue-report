# Blue Report FCC/KC 보고서 템플릿 — 플러그인 통합 가이드

이 템플릿 묶음을 1.3.1 플러그인의 Report Model 에 붙이는 방법이다. 무엇이
있는지는 `docs/FCC_KC_REPORT_TEMPLATE_SYSTEM.md` 에 있다.

> **먼저 확인할 것.** 이 가이드는 1.3.1 후보 워크트리를 읽지 못한 환경에서
> 작성됐다. 아래 필드 이름은 작업 지시서 4장의 제품 설명을 근거로 잡은 것이며,
> **실제 `report_model.py` 와 대조가 필요하다.** 대조 전에는 이름이 다를 수 있다는
> 전제로 읽는다. 없는 파일을 짐작으로 대체하지 않았다.

## 1. 붙이는 순서

1. 템플릿 묶음을 플러그인이 읽을 수 있는 자리에 둔다(복사 또는 서브모듈).
2. `manifest.json` 을 읽어 템플릿 목록과 선택 규칙을 로드한다.
3. Report Model → 데이터 슬롯 매핑 어댑터를 만든다(3장).
4. 렌더러가 슬롯을 채우고 시안 도장(`.fk-fixture`)을 지운다.
5. 형식 간 일관성 값(6장)을 검증한다.
6. 레거시 `h_inno` 프로필과 공존시킨다(7장).

## 2. 파일 배치

```text
.claude/skills/blue-report/assets/fcc-kc/
  fcc-kc.css                     덧층 — 색·크기를 새로 만들지 않는다
  manifest.json                  템플릿 14종 · 선택 규칙
  schemas/report-model.schema.json  fixture 계약
  fixtures/*.json                14종 · 경계 조건 포함
  templates/tpl-a-executive.html
  templates/tpl-b-dashboard.html
  templates/tpl-c-dossier.html
  templates/special/tpl-s01..s11-*.html
```

앞의 셋(`blue-report.css` · `blue-doc.css` · `doc-viewer.css`)과 폰트가 함께 있어야
한다. 폰트는 `assets/fonts/` 에서 `@font-face` 로 불러오므로 바깥 링크가 없다.

## 3. Report Model → 슬롯 매핑

렌더러가 채울 자리와, 그 자리에 들어갈 값의 출처다. **왼쪽은 지면의 자리,
오른쪽은 서버가 준 값이다. 템플릿이 다시 계산하는 값은 하나도 없다.**

| 슬롯 | 값 | 비고 |
|---|---|---|
| `data-field="scope.sourceDataVersion"` | `sourceDataVersion` | 표지·범위 띠 |
| `data-field="scope.sourceWatermark"` | `sourceWatermark` | 계보 블록 |
| `data-field="scope.appliedPeriod"` | `appliedPeriod` | 부분 기간이면 아래 참조 |
| `data-field="scope.appliedFilters"` | `appliedFilters` | ` · ` 로 이어 붙인다 |
| `data-field="scope.populationDefinition"` | `populationDefinition` | |
| `data-field="scope.recordGrain"` | `recordGrain` | 사람이 읽는 말로 옮긴다 |
| `data-field="scope.coverageComplete"` | `coverageComplete` | `.fk-cov--full/bounded/none` 로 클래스도 바꾼다 |
| `data-field="entityResolution.*"` | `entityResolution` | 해소 패널 |
| `data-metric-id="<id>"` | `metrics[id]` | 값·단위·주석 |
| `data-chart-id="<id>"` | `charts[id]` | 계열 순서 그대로 |
| `data-narrative-origin` | 서술의 출처 | 아래 4장 |
| `.fk-evi` 행 | `evidence.items[]` | `data-evidence-ref` 에 식별자 |
| 연락처 표 | `publicContacts[]` | 출처·확인일 필수 |
| `data-field="lineage.*"` | 체크섬 4종 | |
| `.fk-fixture` | — | 운영 렌더링에서 **삭제** |

### 필요한 도메인 어댑터

`report_model.py` 에 아래 변환이 필요하다. 이름은 대조 후 확정한다.

| 어댑터 | 하는 일 |
|---|---|
| `to_scope_band()` | 기간·필터·모집단·레코드 단위·커버리지를 지면 문구로 |
| `to_metric_cards()` | 지표를 `{id, label, value, unit, note, state}` 로 |
| `to_ranked_series()` | 순위 계열을 **서버 순서 그대로** `{label, value, emphasis}` 로 |
| `to_timeseries()` | 부분 기간 인덱스(`partialFromIndex`)를 함께 넘긴다 |
| `to_narrative_blocks()` | 서버 사실·AI 해석·사람 메모를 출처별로 나눈다 |
| `to_evidence_rows()` | 근거와 상태(verified/bounded) |
| `to_quality_panel()` | 반환 행·고유 인증·미해소 + 경고·제한 |
| `to_lineage()` | 체크섬 4종 |

**어댑터가 값을 고치지 않는다.** 정렬·합계·반올림을 여기서 하면 지면과 서버가
갈라진다. 표시 형식(천 단위 쉼표, 소수 자릿수)만 다룬다.

## 4. 서술 출처를 반드시 나눈다

```html
<div class="fk-narr" data-narrative-origin="server_fact">…</div>
<div class="fk-narr" data-narrative-origin="ai_interpretation">…</div>
<div class="fk-narr" data-narrative-origin="human_note">…</div>
```

세 가지를 한 블록에 섞지 않는다. 섞으면 AI 문장이 서버 검증 사실처럼 읽힌다.
머리표(`■ 서버 검증 사실` · `▲ AI 해석` · `✎ 검토자 메모`)는 CSS 가 붙이므로
렌더러가 지우지 않는다.

## 5. DOCX · PPTX 이식 기준

A/B/C 대표 시안을 만든다.

```bash
python3 .claude/skills/blue-report/scripts/build_fcc_office.py
```

`decks-out/fcc-kc/` 에 DOCX 3벌과 PPTX 3벌이 나온다. 값은 `fixture-baseline.json`
하나에서 파생하므로 HTML·PDF 와 수치가 갈라지지 않는다. **손으로 다른 수치를 적은
문서를 따로 관리하지 않는다.**

색은 `blue-report.css` 의 `--br-*` 를 읽어 쓴다. 파이썬 쪽에 hex 를 적지 않는다.

**세 종은 순서가 다르다.** 색만 다른 변형이 아니다.

| | DOCX 구성 | PPTX |
|---|---|---|
| A | 결론 → 뒷받침 → 해석·경계 → 권고 → 근거·계보 | 7장 · 지표 먼저 |
| B | 계약 → 지표 → 추이·순위 → 품질·근거 (**가로**) | 8장 · 계약 먼저 |
| C | 문서 통제 → 집계 의미 → 필드 대응 → 품질 예외 → 근거 → 계보·검토란 | 8장 · 통제 먼저 |

### 검수 방법과 한계

**LibreOffice 가 이 환경에서 돌지 않아 그림으로 검수하지 못했다.** 텍스트 파일
변환조차 실패한다(`Error: source file could not be loaded`). 추정으로 통과 처리하지
않고, 파일을 다시 열어 **구조로 판정**한다.

```bash
python3 .claude/skills/blue-report/scripts/build_fcc_office.py --check
```

방향(A·C 세로 · B 가로) · 구성 순서 · 시안 도장 개수 · 범위 계약 · 서술 출처 3종 ·
근거와 체크섬 · 네이티브 차트 2개 · zip 무결성을 본다. **지면의 여백과 밀도는
사람이 열어 봐야 한다** — Word·PowerPoint 가 있는 환경에서 한 번 확인한다.

### 모듈 변환 표

| 모듈 | DOCX | PPTX | 이미지 고정 |
|---|---|---|---|
| 표지 · 제품 서명 | 표지 구역 | 표지 슬라이드 | 아니오 |
| 검증 범위 띠 | 2열 표 | 상단 캡션 표 | 아니오 |
| 서버 지표 카드 | 표(테두리 없음) | 지표 4칸 | 아니오 |
| 서술 출처 블록 | 스타일 3종(사실·해석·메모) | 텍스트 상자 3종 | 아니오 |
| 경고 · 제한 배너 | 음영 문단 | 강조 상자 | 아니오 |
| 순위 가로 막대 | **네이티브 가로 막대 차트** | **네이티브 차트** | 아니오 |
| 추이 선 | **네이티브 꺾은선** | **네이티브 차트** | 아니오 |
| 코호트 비교 | 네이티브 묶은 막대 | 네이티브 차트 | 아니오 |
| 교차 히트맵 | 표 + 셀 음영 | 표 + 셀 음영 | 아니오 |
| 전이 행렬 | 표 | 표 | 아니오 |
| 흐름 단계 | 표 3열 | 도형 3개 + 화살표 | 아니오 |
| 작은 배수 20칸 | 표 4열 x 5행 | 표 | 아니오 |
| 텔레매틱스 세 패널 | 표 3개 · 제목 유지 | 슬라이드 3장 | 아니오 |
| 근거 목록 | 표 · **머리행 반복 켬** | 표 | 아니오 |
| 계보 · 체크섬 | 2열 표 · 고정폭 | 부록 슬라이드 | 아니오 |
| 부분 기간 음영 | 차트 서식 | 차트 서식 | **예 — 서식 재현 불가 시** |

**편집 가능한 차트를 이미지로 굳히지 않는다.** 이미지로 굳혀야 하는 것은
서식 재현이 불가능한 경우뿐이고, 그때는 대체 텍스트에 값을 적는다.

### 형식이 달라도 같아야 하는 값

- 데이터 버전 · watermark
- 기간 · 필터 · 엔터티 해소
- 모집단 정의 · 레코드 단위
- 커버리지 상태
- 서버 계산 지표
- 근거 상태와 식별자
- consistency projection checksum

**수동으로 서로 다른 수치를 가진 문서를 중복 작성하지 않는다.** 네 형식은 하나의
Report Model 에서 파생한다.

## 6. 남은 작업

| 항목 | 내용 |
|---|---|
| 필드 대조 | `report_model.py` · `REPORT-CONTRACT-1.3.1.md` 와 3장 표 대조 |
| DOCX·PPTX 눈 검수 | Word·PowerPoint 가 있는 환경에서 여백·밀도 확인 |
| 특수 11종 이식 | 지금은 A/B/C 만 · 특수 템플릿의 DOCX·PPTX 는 미작성 |
| 렌더러 연결 | 슬롯 채움 · 시안 도장 제거 · 커버리지 클래스 전환 |
| 회귀 시험 | 템플릿별 스냅샷 · fixture 14종 교차 |

## 7. 레거시 공존

| | `h_inno` (레거시) | `hct_blue_report` (신규) |
|---|---|---|
| 용도 | 1.3.0 호환 | 1.3.1 이후 |
| 발행 브랜드 | 개인 서비스 | HCT |
| 템플릿 | 기존 A/B/C | 이 묶음 14종 |

프로필 ID 로 가른다. **레거시를 덮어쓰지 않는다.** 두 프로필이 같은 Report Model
을 읽되 템플릿과 브랜드 자산만 달리 고른다.

## 8. 수정할 파일 (플러그인 쪽)

지시서 11장 D 가 요구한 목록이다. 실제 경로는 워크트리 대조 후 확정한다.

| 파일 | 할 일 |
|---|---|
| `runtime/app/report_model.py` | 도메인 어댑터 8종 추가 |
| `runtime/app/enhanced_report_renderers.py` | 슬롯 채움 · 템플릿 선택 |
| `runtime/app/render_report_pptx.mjs` | PPTX 매핑(5장 표) |
| `plugin/skills/fcc-kc-reporting/references/brand-guidelines.md` | `hct_blue_report` 프로필 추가 |
| `plugin/skills/fcc-kc-reporting/references/report-tool-contract.md` | 템플릿 ID 목록 갱신 |
| `runtime/app/test_report_131.py` | fixture 14종 회귀 |

## 9. 마이그레이션 순서와 위험

1. 신규 프로필을 **추가만** 한다(레거시 그대로).
2. 특수 템플릿 하나(추이)로 끝단까지 연결해 본다.
3. 기본 A/B/C 를 붙인다.
4. 나머지 특수 10종.
5. 레거시 전환은 마지막 — 전환 전까지 두 프로필 병행.

| 위험 | 징후 | 대응 |
|---|---|---|
| 필드 이름 불일치 | 슬롯이 `—` 로 남음 | 빈 슬롯이 보이게 둔 까닭 · 3장 대조 |
| 커버리지 클래스 미전환 | 항상 「완전」으로 표시 | 렌더러가 `.fk-cov--*` 를 바꾸는지 확인 |
| 시안 도장 잔존 | 운영 보고서에 DESIGN FIXTURE | 렌더러가 `.fk-fixture` 를 지우는지 확인 |
| 서술 출처 뭉개짐 | AI 문장이 사실처럼 읽힘 | `data-narrative-origin` 유지 확인 |
| 부분 기간 표시 누락 | 마지막 점이 실선 | `partialFromIndex` 전달 확인 |
