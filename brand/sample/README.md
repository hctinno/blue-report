# 견본 브랜드

**이 폴더는 자리표시자다.** 실제 회사 로고가 아니라 도형으로 그린 견본이며,
쓰는 쪽이 자기 회사 자산으로 갈아 끼우는 자리다.

## 파일

| 파일 | 용도 |
|---|---|
| `sample-logo-source.png` | 원본. 흰 배경에 [심볼] / 빈 띠 / [글자] 구조 |
| `sample-logo-white.png` | 흰색 녹아웃. **표지·간지·마무리 등 다크면 전용** |
| `sample-logo-color.png` | 흰 배경을 투명으로 뺀 원색판. 밝은 지면용 |
| `sample-logo-symbol-white.png` | 글자를 뗀 심볼 녹아웃. 다크면 워터마크용 |
| `sample-logo-symbol-color.png` | 같은 심볼의 원색판. 밝은 지면 워터마크용 |
| `brand.json` | 회사명·워드마크·저작권·로고 파일 지정 |

## 왜 네 벌인가

표지·간지는 딥네이비 `#071b45`, 핵심 정리면은 `#101827` 이다. 원색 로고를 그대로
올리면 배경에 묻히고, 흰 배경째 올리면 흰 사각형이 생긴다. 그래서 면에 따라 나눠 쓴다.

배경 워터마크는 심볼만 쓴다. 전체 로고를 키우면 글자까지 함께 커져 본문 괘선과 겹친다.
우측 상단 마크는 작게 들어가 전체 로고가 그대로 읽히므로 거기서는 자르지 않는다.

`check_deck.py` 가 지면 밝기에 맞는 변형을 썼는지, 워터마크가 마크와 다른 자산인지를
기계로 판정한다. 네 벌이 다 있어야 통과한다.

## 자기 브랜드로 바꾸기

폴더를 새로 만들고 원본 로고 한 장만 넣으면 나머지 네 벌은 스크립트가 만든다.

```bash
mkdir -p brand/mycompany
cp ~/내회사로고.png brand/mycompany/mycompany-logo-source.png

python3 .claude/skills/blue-report/scripts/make_logo_variants.py \
        brand/mycompany/mycompany-logo-source.png \
        --out-dir brand/mycompany --name mycompany-logo
```

`brand.json` 을 복사해 회사명·워드마크·파일명을 고친 뒤 `--brand` 로 지목한다.

```bash
python3 .claude/skills/blue-report/scripts/apply_brand.py \
        --brand brand/mycompany/brand.json --deck internal --single-file -o 보고서.html
```

원본 로고가 [심볼] / 빈 띠 / [글자] 구조가 아니면 심볼 분리가 되지 않는다. 그때는
심볼만 따로 잘라 `*-symbol-*.png` 두 벌을 손으로 넣는다.

## 강조색

`assets/blue-report.css` 의 `--br-cobalt` 한 줄이 강조색이다. 슬라이드에는 hex 를
직접 적지 않으므로 그 한 줄만 고치면 전부 따라온다. 다만 팔레트는 지면 대비
기준으로 검증된 값이라, 바꾼 뒤 `scripts/verify_repo.py` 의 계열색 검사를 다시 돌린다.
