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


def main():
    ap = argparse.ArgumentParser(description="블루 리포트 도넛 SVG 생성기")
    ap.add_argument("values", nargs="+", type=float, help="구간 퍼센트 값")
    ap.add_argument("--labels", help="쉼표로 구분한 구간 이름")
    ap.add_argument("--r", type=float, default=78, help="반지름 (기본 78)")
    ap.add_argument("--w", type=float, default=36, help="선 두께 (기본 36)")
    ap.add_argument("--gap", type=float, default=1.5, help="구간 간격 각도 (기본 1.5)")
    ap.add_argument("--dark", action="store_true", help="다크면용 램프 사용")
    a = ap.parse_args()
    build(a.values, a.labels.split(",") if a.labels else None,
          r=a.r, width=a.w, gap=a.gap, dark=a.dark)


if __name__ == "__main__":
    main()
