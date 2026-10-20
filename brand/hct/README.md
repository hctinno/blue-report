# HCT 브랜드 자산

블루 리포트 발표 템플릿에 쓰는 회사 자산이다. 사내 보고서용이라 연락처는 넣지 않는다.

## 파일

| 파일 | 용도 |
|---|---|
| `hct-logo-source.png` | 사용자가 제공한 원본. 흰 배경 574×348, 로고 영역 264×86 |
| `hct-logo-white.png` | 흰색 녹아웃. **표지·간지·마무리 등 다크면 전용** |
| `hct-logo-color.png` | 흰 배경을 투명으로 뺀 원색판. 밝은 지면용 |
| `brand.json` | 회사명·워드마크·저작권 설정 |

## 왜 두 가지인가

블루 리포트의 표지·간지는 딥네이비 `#071b45`, 핵심 정리면은 `#101827`이다.
로고 원색 `#2f4a9c`는 딥네이비 대비 **2.06 : 1**로 거의 보이지 않는다.
밝은 지면 `#f4f6f8`에서는 7.51 : 1로 충분하다. 그래서 면에 따라 나눠 쓴다.

두 파생본은 스크립트로 만들었고 재실행하면 동일한 파일이 나온다.

```bash
python3 .claude/skills/blue-report/scripts/make_logo_variants.py \
        brand/hct/hct-logo-source.png --out-dir brand/hct --name hct-logo
```

## 덱 만들기

```bash
python3 .claude/skills/blue-report/scripts/apply_brand.py \
        --brand brand/hct/brand.json --single-file -o HCT-보고서.html
```

## 확인이 필요한 것

- 원본 로고 영역이 **264×86px**이다. 화면 발표(1920×1080에서 64px 표시)에는 충분하지만
  인쇄나 큰 확대에는 부족하다. **SVG 또는 고해상도 원본**이 있으면 교체한다.
- 흰색 녹아웃은 원본에서 파생한 것이다. 사내 브랜드 가이드에 별도 규정된
  반전 로고가 있으면 그것으로 교체한다.

## 강조색은 교체가 끝났다

`blue-report.css`의 `--br-cobalt`는 이미 HCT 로고색 `#2f4a9c`다. 블루 리포트 원래
기본값은 `#1140d6`이었고, 이 저장소를 분리하면서 회사 지정색으로 바꿨다.
밝은 지면 `#f4f6f8` 대비 7.51 : 1로 강조색 요건을 만족하므로 더 손댈 것이 없다.

바꿀 일이 생기면 `.claude/skills/blue-report/assets/blue-report.css`의 `--br-cobalt`
한 줄만 고친다. 슬라이드에는 hex 를 직접 적지 않으므로 그 한 줄이 전부다.
