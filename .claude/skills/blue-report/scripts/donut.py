#!/usr/bin/env python3
"""도넛 차트 SVG 조각 생성기.

블루 리포트는 파이를 쓰지 않는다. 도넛만 쓰고, 손으로 적은 <path d="M…A…"> 대신
원주 기반 stroke-dasharray로 그린다. 수치와 각도가 어긋나지 않게 하는 유일한 방법이다.

    C    = 2 * pi * r
    dash = C * pct/100 - C * gap/360      (구간 사이 간격)
    rot  = 누적pct * 3.6 - 90             (12시 방향에서 시작)

사용:
    python3 donut.py 41.9 34.9 23.2
    python3 donut.py --labels 중소기업,중견기업,대기업 41.9 34.9 23.2
    python3 donut.py --r 78 --w 36 --gap 1.5 41.9 34.9 23.2

라이브 덱(--live) — rem 으로 크기가 정해지는 .bl-donut-box 한 벌을 낸다. 인라인 px 가
없고, 조각 · 범례에 data-k 가 붙어 손을 대면 가운데에 그 항목이 뜬다. 장에 들어올 때
조각이 차례로 그려진다(--dash). 가운데 합계 · 단위 · 설명을 줄 수 있다.
    python3 donut.py --live --labels 가,나,다 --total 46 --unit 개 --caption "전체 계정" 50 30 20
    python3 donut.py --live --raw --labels 가,나,다 27 12 7      # 값이 건수 — 비율은 스크립트가 낸다
"""
import argparse
import math
import os
import re
import sys

# 램프를 여기 적어 두지 않는다. blue-report.css 의 --br-data-* 를 읽는다.
# 예전에는 hex 를 박아 두었고, CSS 의 --br-data-2 가 #1140d6 에서 #2f4a9c 로
# 바뀌었을 때 이 파일만 옛 값에 남아 갈라졌다. pptx/tokens.js 가 CSS 를 파싱하는
# 것과 같은 이유로 여기서도 CSS 를 읽는다.
CSS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   "assets", "blue-report.css")


def _ramp(prefix):
    """--br-<prefix>-1..N 을 번호 순서대로 읽는다. 값이 아니라 var() 이름을 돌려준다.

    슬라이드에 hex 를 직접 적으면 check_deck.py 가 실패시킨다. 생성 결과를 그대로
    붙여 넣을 수 있어야 하므로 처음부터 토큰 이름으로 낸다."""
    try:
        css = open(CSS, encoding="utf-8").read()
    except OSError:
        raise SystemExit(f"오류: 토큰 파일을 읽지 못했다 — {CSS}")
    found = re.findall(rf"--br-{prefix}-(\d+)\s*:", css)
    if not found:
        raise SystemExit(f"오류: blue-report.css 에 --br-{prefix}-* 가 없다.")
    return [f"var(--br-{prefix}-{n})" for n in sorted(set(found), key=int)]


def build(values, labels=None, r=78, width=36, gap=1.5, dark=False, delay_start=5):
    """구간별 circle 요소와 범례를 만든다. values는 퍼센트(합 100 근사)."""
    total = sum(values)
    if total <= 0:
        raise SystemExit("오류: 값의 합이 0이다.")
    if abs(total - 100) > 0.5:
        print(f"# 경고: 값의 합이 {total:.1f}%다. 100%가 아니면 비율이 왜곡된다.",
              file=sys.stderr)

    ramp = _ramp("data-dark") if dark else _ramp("data")
    if len(values) > len(ramp):
        raise SystemExit(f"오류: 구간 {len(values)}개는 램프 {len(ramp)}색을 넘는다. "
                         "구간을 묶거나 막대 차트로 바꾼다.")

    C = 2 * math.pi * r
    gap_len = C * gap / 360

    # 값이 클수록 진한 색: 큰 값부터 램프 앞쪽 색을 배정한다.
    order = sorted(range(len(values)), key=lambda i: -values[i])
    color_of = {}
    for rank, idx in enumerate(order):
        color_of[idx] = ramp[rank]

    # 인접 구간 같은 색 금지 검사 (배정 규칙상 발생하지 않지만 값이 같으면 생길 수 있다)
    seq = [color_of[i] for i in range(len(values))]
    for i in range(len(seq)):
        if seq[i] == seq[(i + 1) % len(seq)]:
            print(f"# 경고: 구간 {i+1}과 {((i+1) % len(seq))+1}의 색이 같다. 값을 확인한다.",
                  file=sys.stderr)

    lines, legend = [], []
    cum = 0.0
    size = (r + width / 2) * 2 + 4
    for i, v in enumerate(values):
        pct = v / total * 100
        dash = C * pct / 100 - gap_len
        if dash <= 0:
            print(f"# 경고: 구간 {i+1}({v})이 간격보다 작아 보이지 않는다. 기타로 묶는다.",
                  file=sys.stderr)
            dash = max(dash, 1)
        rot = cum * 3.6 - 90
        d = min(delay_start + i, 12)
        lines.append(
            f'      <circle class="dsh d{d}" r="{r}" stroke="{color_of[i]}" '
            f'stroke-width="{width}" stroke-dasharray="{dash:.1f} {C:.1f}" '
            f'transform="rotate({rot:.2f})"></circle>'
        )
        name = labels[i] if labels and i < len(labels) else f"구간 {i+1}"
        legend.append(
            f'    <div class="br-legend-item"><div class="br-legend-name">'
            f'<span class="br-dot" style="background:{color_of[i]}"></span>{name}</div>'
            f'<div class="br-legend-val">{v}<span class="br-sup">%</span></div></div>'
        )
        cum += pct

    svg = (f'  <svg class="br-donut" viewBox="0 0 {size:.0f} {size:.0f}" '
           f'style="width:{size:.0f}px;height:{size:.0f}px" role="img" aria-label="비율 분포">\n'
           f'    <g transform="translate({size/2:.0f},{size/2:.0f})">\n'
           + "\n".join(lines) + "\n    </g>\n  </svg>")
    leg = '  <div class="br-legend">\n' + "\n".join(legend) + "\n  </div>"

    print(f"# C = 2*pi*{r} = {C:.1f} · 간격 {gap}도 = {gap_len:.1f}"
          f" · 램프 {'--br-data-dark-*' if dark else '--br-data-*'} ({len(ramp)}색)")
    print(svg)
    print(leg)
    return svg, leg


def build_live(values, labels=None, r=110, width=48, gap=1.5, raw=False, total=None, unit="",
               caption="", aria="비율 분포"):
    """라이브 덱용 .bl-donut-box. 각도 계산은 build() 와 같은 식이다.

    raw 면 값을 건수로 읽고 비율은 합계로 낸다 — 범례에는 건수, 풍선에는 비율이 뜬다.
    raw 가 아니면 값이 퍼센트라 합이 100 근처여야 한다(아니면 경고)."""
    s = sum(values)
    if s <= 0:
        raise SystemExit("오류: 값의 합이 0이다.")
    if not raw and abs(s - 100) > 0.5:
        print(f"# 경고: 값의 합이 {s:.1f}%다. 건수라면 --raw 를 준다.", file=sys.stderr)
    ramp = _ramp("data")
    if len(values) > len(ramp):
        raise SystemExit(f"오류: 구간 {len(values)}개는 램프 {len(ramp)}색을 넘는다. 구간을 묶거나 막대로 바꾼다.")
    C = 2 * math.pi * r
    gap_len = C * gap / 360
    order = sorted(range(len(values)), key=lambda k: -values[k])
    color = {idx: ramp[rank] for rank, idx in enumerate(order)}
    size = (r + width / 2) * 2 + 4
    segs, legs, cum = [], [], 0.0

    def num(v):
        return f"{v:,.0f}" if raw or float(v).is_integer() else f"{v:.1f}"

    for k, v in enumerate(values):
        pct = v / s * 100
        dash = max(C * pct / 100 - gap_len, 1)
        rot = cum * 3.6 - 90
        segs.append(f'      <circle class="bl-donut-s" data-k="{k}" r="{r:g}" stroke="{color[k]}" '
                    f'stroke-width="{width:g}" stroke-dasharray="{dash:.1f} {C:.1f}" '
                    f'transform="rotate({rot:.2f})" style="--i:{k};--dash:{dash:.1f}"></circle>')
        name = labels[k] if labels and k < len(labels) else f"구간 {k + 1}"
        shown = num(v) + (unit if raw else "%")
        legs.append(f'    <li data-k="{k}" data-p="{pct:.1f}%"><i style="background:{color[k]}"></i>'
                    f'<span>{name}</span><b>{shown}</b></li>')
        cum += pct
    if total is None:
        tot = num(s) if raw else "100"
    else:
        # 쉼표 없이 준 수도 범례와 같은 표기로 — 「2140」과 「1,070」이 한 그림에 섞이지 않게
        try:
            tot = num(float(str(total).replace(",", "")))
        except ValueError:
            tot = str(total)
    cap = f'<span class="bl-cap">{caption}</span>' if caption else ""
    # 가운데 숫자 폭(em). 구멍보다 넓으면 CSS 가 글자를 줄인다(.bl-donut-c b 의 --w).
    # 「2,140시간」처럼 길면 고리를 덮었다 — 단위는 짧게(h · 건 · %) 두는 편이 낫다
    def _em(t):
        w = 0.0
        for ch in t:
            w += .58 if ch.isdigit() else .28 if ch in ",." else 1.0 if ord(ch) >= 0x1100 else .6
        return w
    wem = _em(tot) + .5 * _em(unit) + .1   # 단위는 .42em 이지만 1rem 아래로 내려가지 않는다 — 넉넉히 .5
    out = ('<div class="bl-donut-box">\n'
           f'  <figure class="bl-donut" role="img" aria-label="{aria}">\n'
           f'    <svg viewBox="0 0 {size:.0f} {size:.0f}" aria-hidden="true"><g transform="translate({size / 2:.0f},{size / 2:.0f})">\n'
           + "\n".join(segs) + "\n    </g></svg>\n"
           f'    <figcaption class="bl-donut-c"><b style="--w: {wem:.2f}">{tot}<small>{unit}</small></b>{cap}</figcaption>\n'
           '  </figure>\n'
           '  <ul class="bl-donut-leg">\n' + "\n".join(legs) + "\n  </ul>\n</div>")
    # 출력을 통째로 붙여도 지면에 글자가 찍히지 않게 설명 줄은 HTML 주석으로 낸다
    print(f"<!-- donut.py 라이브 출력 · 둘레 2πr = {C:.1f} · 간격 {gap}도 · 램프 br-data -->")
    print(out)
    return out


def main():
    ap = argparse.ArgumentParser(description="블루 리포트 도넛 SVG 생성기")
    ap.add_argument("values", nargs="+", type=float, help="구간 퍼센트 값")
    ap.add_argument("--labels", help="쉼표로 구분한 구간 이름")
    ap.add_argument("--r", type=float, default=78, help="반지름 (기본 78)")
    ap.add_argument("--w", type=float, default=36, help="선 두께 (기본 36)")
    ap.add_argument("--gap", type=float, default=1.5, help="구간 간격 각도 (기본 1.5)")
    ap.add_argument("--dark", action="store_true", help="다크면용 램프 사용")
    ap.add_argument("--live", action="store_true", help="라이브 덱용 .bl-donut-box 로 낸다 (rem · 손대면 강조)")
    ap.add_argument("--raw", action="store_true", help="--live 에서 값을 건수로 읽는다")
    ap.add_argument("--total", help="--live 가운데 큰 숫자 (기본: 합계)")
    ap.add_argument("--unit", default="", help="--live 가운데 숫자 · 범례 값의 단위")
    ap.add_argument("--caption", default="", help="--live 가운데 숫자 밑 설명")
    a = ap.parse_args()
    labels = a.labels.split(",") if a.labels else None
    if a.live:
        build_live(a.values, labels, r=a.r if a.r != 78 else 110, width=a.w if a.w != 36 else 48,
                   gap=a.gap, raw=a.raw, total=a.total, unit=a.unit, caption=a.caption)
        return
    build(a.values, labels, r=a.r, width=a.w, gap=a.gap, dark=a.dark)


if __name__ == "__main__":
    main()
