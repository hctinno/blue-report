#!/usr/bin/env python3
"""블루 리포트 팔레트 계산기 — 단조 램프 생성과 대비 검증.

블루 리포트의 두 규칙을 코드로 강제한다.
  - 데이터 마크는 지면 대비 2:1 이상
  - 인접 구간 같은 색 금지, 값이 클수록 진한 단조 램프

라이브러리로도, CLI로도 쓴다.

    python3 palette.py --check                 # 토큰 팔레트 전체 대비표
    python3 palette.py --cat                   # 계열색 6종 — 대비와 색각 이상 판별
    python3 palette.py --steps 7               # 밝은 지면용 7단계 램프
    python3 palette.py --steps 5 --dark        # 다크면용 5단계 램프
"""
import argparse
import os
import re

PAGE = "#f4f6f8"
DARK = "#101827"
COVER = "#071b45"

# 램프 양 끝. 밝은 끝은 지면 대비 2.10:1로, 2:1 경계를 넘지 않게 고정한다.
LIGHT_ENDS = ("#0b2a6b", "#86b0da")
DARK_ENDS = ("#dbe9ff", "#2a5fc0")

MIN_DATA_CONTRAST = 2.0


def _rgb(h):
    h = h.lstrip("#")
    return [int(h[i:i + 2], 16) for i in (0, 2, 4)]


def _hex(t):
    return "#%02x%02x%02x" % tuple(max(0, min(255, int(round(v)))) for v in t)


def luminance(h):
    def f(c):
        c /= 255
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = _rgb(h)
    return .2126 * f(r) + .7152 * f(g) + .0722 * f(b)


def contrast(a, b):
    la, lb = luminance(a), luminance(b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + .05) / (lo + .05)


def ramp(n, dark=False):
    """n단계 단조 램프. 값이 클수록 진한 색이 앞에 온다."""
    if n < 2:
        return [LIGHT_ENDS[0] if not dark else DARK_ENDS[0]]
    a, b = (DARK_ENDS if dark else LIGHT_ENDS)
    ra, rb = _rgb(a), _rgb(b)
    out = [_hex([ra[k] + (rb[k] - ra[k]) * i / (n - 1) for k in range(3)]) for i in range(n)]
    if len(set(out)) != len(out):
        raise ValueError(f"{n}단계는 중복 색을 만든다. 구간을 줄이거나 묶는다.")
    return out


def audit(colors, background, label=""):
    """데이터 색 목록이 대비 규칙을 지키는지 검사한다. 위반 목록을 돌려준다."""
    problems = []
    for i, c in enumerate(colors):
        r = contrast(c, background)
        if r < MIN_DATA_CONTRAST:
            problems.append(f"{label}{c}: 배경 {background} 대비 {r:.2f}:1 — 2:1 미달")
        if i and c == colors[i - 1]:
            problems.append(f"{label}{c}: 인접 구간과 같은 색")
    return problems


# 값을 여기 적지 않는다. blue-report.css 를 읽는다.
# 예전에는 이 자리에 hex 를 박아 뒀는데, --br-cobalt 가 #1140d6 에서 #2f4a9c 로 바뀐 뒤에도
# 여기만 옛 값을 들고 있었다. 즉 존재하지 않는 색의 대비를 재서 보고하고 있었다.
# donut.py 가 같은 병에 걸려 있었고 같은 방법으로 고쳤다.
CSS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   "assets", "blue-report.css")


def css_tokens():
    """blue-report.css 의 :root 에서 hex 값을 가진 --br-* 를 전부 읽는다."""
    text = open(CSS, encoding="utf-8").read()
    root = text[text.index(":root"):text.index("/* ====", text.index(":root"))]
    return dict(re.findall(r"--br-([a-z0-9-]+)\s*:\s*(#[0-9a-fA-F]{6})\s*;", root))


def group(prefix, n):
    """--br-<prefix>-1..n 을 순서대로 돌려준다. 하나라도 없으면 멈춘다."""
    t = css_tokens()
    out = []
    for i in range(1, n + 1):
        k = f"{prefix}-{i}"
        if k not in t:
            raise SystemExit(f"토큰 없음: --br-{k} (blue-report.css)")
        out.append(t[k])
    return out


# ── 색각 이상 모의 (Machado-Oliveira-Fernandes 2009, severity 1.0) ──────────
# 계열색이 갈리는지 보려면 정상 시각만으로는 모자란다. 적록색각 이상은 남성 8%다.
# 행렬 세 벌이면 되므로 외부 라이브러리를 들이지 않는다.
CVD = {
    "protan": ((0.152286, 1.052583, -0.204868),
               (0.114503, 0.786281, 0.099216),
               (-0.003882, -0.048116, 1.051998)),
    "deutan": ((0.367322, 0.860646, -0.227968),
               (0.280085, 0.672501, 0.047413),
               (-0.011820, 0.042940, 0.968881)),
}


def _lin(c):
    c /= 255
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def _oklab(h):
    r, g, b = (_lin(v) for v in _rgb(h))
    l = (0.4122214708 * r + 0.5363325363 * g + 0.0514459929 * b) ** (1 / 3)
    m = (0.2119034982 * r + 0.6806995451 * g + 0.1073969566 * b) ** (1 / 3)
    s = (0.0883024619 * r + 0.2817188376 * g + 0.6299787005 * b) ** (1 / 3)
    return (0.2104542553 * l + 0.7936177850 * m - 0.0040720468 * s,
            1.9779984951 * l - 2.4285922050 * m + 0.4505937099 * s,
            0.0259040371 * l + 0.7827717662 * m - 0.8086757660 * s)


def _unlin(c):
    c = max(0.0, min(1.0, c))
    return 12.92 * c if c <= 0.0031308 else 1.055 * c ** (1 / 2.4) - 0.055


def _simulate(h, kind):
    """색각 이상 모의. 행렬은 선형 RGB 에서 돈다 — 감마 인코딩된 0~255 에 그대로
    곱하면 값이 어긋난다. 처음에 그렇게 짰다가 dataviz 검증기와 deutan 한 쌍에서
    3.0 벌어져 찾았다. 선형화 → 행렬 → 재인코딩 순서를 지킨다."""
    m = CVD[kind]
    lin = [_lin(v) for v in _rgb(h)]
    out = []
    for row in m:
        v = sum(row[i] * lin[i] for i in range(3))
        out.append(max(0, min(255, round(_unlin(v) * 255))))
    return _hex(out)


def delta_e(a, b):
    """OKLab 유클리드 거리 x100. dataviz 규격이 쓰는 것과 같은 척도."""
    pa, pb = _oklab(a), _oklab(b)
    return 100 * sum((x - y) ** 2 for x, y in zip(pa, pb)) ** .5


# 인접쌍 기준. dataviz 규격의 값을 그대로 쓴다.
MIN_DE_CVD = 8.0       # 색각 이상에서 이웃한 두 색이 갈리는 최소치
MIN_DE_NORMAL = 15.0   # 정상 시각에서의 하한. 이건 타협하지 않는다


def check_categorical(colors, background, label):
    """계열색 한 벌을 판정한다. 실패 목록을 돌려준다."""
    bad = []
    for c in colors:
        r = contrast(c, background)
        if r < 3.0:
            bad.append(f"{c} 지면 대비 {r:.2f}:1 — 3:1 미달")
    for i in range(len(colors) - 1):
        a, b = colors[i], colors[i + 1]
        dn = delta_e(a, b)
        if dn < MIN_DE_NORMAL:
            bad.append(f"{a}<->{b} 정상 시각 ΔE {dn:.1f} — {MIN_DE_NORMAL} 미달")
        for kind in CVD:
            d = delta_e(_simulate(a, kind), _simulate(b, kind))
            if d < MIN_DE_CVD:
                bad.append(f"{a}<->{b} {kind} ΔE {d:.1f} — {MIN_DE_CVD} 미달")
    return bad


def main():
    ap = argparse.ArgumentParser(description="블루 리포트 팔레트 계산기")
    ap.add_argument("--steps", type=int, help="생성할 램프 단계 수")
    ap.add_argument("--dark", action="store_true", help="다크면(#101827)용")
    ap.add_argument("--check", action="store_true", help="토큰 팔레트 대비표 출력")
    ap.add_argument("--cat", action="store_true",
                    help="계열색 검사 — 지면 대비 3:1 · 인접쌍 색각 이상 판별")
    a = ap.parse_args()

    if a.check:
        marks = ["cobalt", "cyan", "navy", "coral", "accent-on-dark", "amber",
                 "soft-1", "soft-2", "soft-3"]
        t = css_tokens()
        for bg, name in ((PAGE, "밝은 지면"), (DARK, "다크 정리면"), (COVER, "표지·간지")):
            print(f"\n[{name} {bg}]")
            for k in marks:
                v = t.get(k)
                if not v:
                    continue
                r = contrast(v, bg)
                mark = "OK " if r >= MIN_DATA_CONTRAST else "미달"
                print(f"  --br-{k:<18} {v}  {r:6.2f}:1  {mark}")
        print("\n※ '미달'은 그 배경의 데이터 마크로 쓰지 않는다. 텍스트·장식에는 별도 기준을 적용한다.")

    if a.cat:
        fails = 0
        for prefix, bg, name in (("cat", PAGE, "밝은 지면"),
                                 ("cat-dark", DARK, "다크면")):
            cols = group(prefix, 6)
            print(f"\n[계열색 {name} {bg}]")
            for i, c in enumerate(cols, 1):
                print(f"  --br-{prefix}-{i}  {c}  지면 대비 {contrast(c, bg):5.2f}:1")
            bad = check_categorical(cols, bg, name)
            if bad:
                fails += len(bad)
                for b in bad:
                    print(f"  실패 — {b}")
            else:
                worst = min(delta_e(cols[i], cols[i + 1]) for i in range(len(cols) - 1))
                print(f"  판정: 전 슬롯 통과 · 최악 인접쌍 정상 시각 ΔE {worst:.1f}")
        if fails:
            raise SystemExit(f"\n계열색 검사 실패 {fails}건. 순서를 바꾸거나 한 슬롯을 옮긴다.")

    if a.steps:
        cols = ramp(a.steps, dark=a.dark)
        bg = DARK if a.dark else PAGE
        print(f"\n{a.steps}단계 램프 (배경 {bg})")
        for i, c in enumerate(cols):
            print(f"  {i+1}. {c}   대비 {contrast(c, bg):5.2f}:1")
        bad = audit(cols, bg)
        print("  판정:", "전 단계 통과" if not bad else "위반 " + "; ".join(bad))
        print("\n  CSS:", " ".join(cols))

    if not a.check and not a.steps and not a.cat:
        ap.print_help()


if __name__ == "__main__":
    main()
