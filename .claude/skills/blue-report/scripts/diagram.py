#!/usr/bin/env python3
"""구조 도해 SVG 조각 생성기.

블루 리포트는 도해를 손으로 그리지 않는다. donut.py 가 각도를 계산하듯
여기서는 **행진 간격**을 계산한다. 항목 수가 바뀌면 좌표가 다시 유도되므로
한 번 만든 도해에 항목을 끼워 넣다가 간격이 어긋나는 일이 없다.

다루는 것은 좌표가 항목 순번 i 의 1차식으로 떨어지는 네 가지다.

    cycle    x  = pad + (boxW + gap)*i                 되돌아오는 순환 고리
    gate     cx = c0 + step*i                          통과 관문 사다리
    stair    x  = x0 + w*i, y = y0 - dh*i, h = h0+dh*i 올라가는 계단
    track    cx = m + (W-2m)/(n-1)*i                   실적/계획이 갈리는 연표

좌표가 값에서 나오지 않는 것(개념 흐름도·일러스트)은 여기서 만들지 않는다.
그런 것은 손으로 그리되 viewBox 와 글자 클래스만 규격에 맞춘다.

viewBox 는 본문 폭 1728(=1920-96*2)에 1:1 로 맞춘다. 그래야 SVG 안의
font-size 가 화면 px 과 같아지고, 24px 하한을 이 스크립트가 지킬 수 있다.
viewBox 를 줄이면 글자가 따라 줄어 check_deck.py 5번에 걸린다.

사용:
    python3 diagram.py cycle 선정,제작,코칭,공유,자산화 --back "한 회차"
    python3 diagram.py gate 기술검증,현장적용,비용회수,조직정착 --out 성과
    python3 diagram.py stair 인식,시범,확산,정착
    python3 diagram.py track 2024,2025,2026,2027 --done 2 --unit 년
"""
import argparse
import os
import re
import sys

# 색은 여기 적지 않는다. donut.py 와 같은 이유로 blue-report.css 에서 읽는다.
CSS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   "assets", "blue-report.css")

W = 1728          # 본문 폭. 슬라이드 1920 에서 좌우 여백 96 씩을 뺀 값
FS_TITLE = 30     # 도해 안 제목
FS_BODY = 25      # 도해 안 본문
FS_MIN = 24       # 하한. 이보다 작은 글자를 내보내면 check_deck.py 5번이 실패시킨다

# 한글 한 글자의 대략 폭(글자 크기 대비). 라벨이 칸에 들어가는지 재는 데 쓴다.
# 정확한 값은 폰트 메트릭이 필요하지만, 넘침을 걸러 내는 데는 이 근사로 충분하다.
CH_RATIO = 1.0


def _ramp(prefix="data"):
    """--br-<prefix>-1..N 을 번호 순서대로 읽어 var() 이름으로 돌려준다."""
    try:
        css = open(CSS, encoding="utf-8").read()
    except OSError:
        raise SystemExit(f"오류: 토큰 파일을 읽지 못했다 — {CSS}")
    found = re.findall(rf"--br-{prefix}-(\d+)\s*:", css)
    if not found:
        raise SystemExit(f"오류: blue-report.css 에 --br-{prefix}-* 가 없다.")
    return [f"var(--br-{prefix}-{n})" for n in sorted(set(found), key=int)]


def _fit(label, box_w, fs):
    """라벨이 칸 안에 들어가는가. 넘치면 경고하고 True 를 돌려준다."""
    need = len(label) * fs * CH_RATIO
    if need > box_w - 24:
        print(f"# 경고: '{label}'({len(label)}자)가 폭 {box_w:.0f}px 칸에 넘친다. "
              f"필요 {need:.0f}px. 라벨을 줄이거나 항목 수를 줄인다.", file=sys.stderr)
        return True
    return False


def _esc(s):
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def _svg(body, h, label):
    """공통 액자. viewBox 를 본문 폭에 1:1 로 맞춘다."""
    return (f'<svg class="br-dg" viewBox="0 0 {W} {h}" '
            f'style="width:100%;height:auto" role="img" aria-label="{_esc(label)}">\n'
            + body + "\n</svg>")


# ── cycle ────────────────────────────────────────────────────────────────────
def cycle(items, back="", gap=28, box_h=150, arc_h=110):
    """되돌아오는 순환 고리. 마지막에서 첫으로 아크가 돌아온다.

    기존 「3단계 로드맵」은 한 방향으로만 간다. 회차가 돌아오는 일(선정→…→
    자산화→다시 선정)은 그 조판으로 말할 수 없어 이 도해가 필요하다."""
    n = len(items)
    if not 3 <= n <= 6:
        raise SystemExit(f"오류: 순환 고리는 3~6칸이다. {n}칸은 담기지 않는다.")
    ramp = _ramp()
    box_w = (W - gap * (n - 1)) / n
    over = False
    rows = []
    for i, it in enumerate(items):
        x = (box_w + gap) * i
        over |= _fit(it, box_w, FS_TITLE)
        rows.append(
            f'  <rect x="{x:.1f}" y="0" width="{box_w:.1f}" height="{box_h}" rx="18" '
            f'fill="{ramp[i % len(ramp)]}"></rect>\n'
            f'  <text x="{x + box_w/2:.1f}" y="{box_h/2 + 11:.0f}" text-anchor="middle" '
            f'font-size="{FS_TITLE}" font-weight="700" fill="var(--br-on-dark)">'
            f'{_esc(it)}</text>')
        if i < n - 1:                      # 칸 사이 전진 화살표
            ax = x + box_w + gap / 2
            rows.append(
                f'  <path d="M{ax - 9:.1f} {box_h/2 - 9:.0f} L{ax + 8:.1f} {box_h/2:.0f} '
                f'L{ax - 9:.1f} {box_h/2 + 9:.0f}" fill="none" '
                f'stroke="var(--br-text-3)" stroke-width="3" stroke-linejoin="round"/>')

    # 회귀 아크 — 끝 칸 아래에서 첫 칸 아래로. 제어점은 두 끝점에서 유도한다.
    x0, x1 = box_w / 2, W - box_w / 2
    by, ty = box_h + 8, box_h + arc_h - 34
    rows.append(
        f'  <path d="M{x1:.1f} {by} C{x1:.1f} {ty} {x0:.1f} {ty} {x0:.1f} {by}" '
        f'fill="none" stroke="var(--br-coral)" stroke-width="3" '
        f'stroke-dasharray="10 8" marker-end="url(#br-dg-a)"/>')
    if back:
        rows.append(
            f'  <text x="{W/2:.0f}" y="{ty + 18:.0f}" text-anchor="middle" '
            f'font-size="{FS_BODY}" font-weight="600" fill="var(--br-coral)">'
            f'{_esc(back)}</text>')

    defs = ('  <defs><marker id="br-dg-a" viewBox="0 0 10 10" refX="9" refY="5" '
            'markerWidth="6" markerHeight="6" orient="auto-start-reverse">'
            '<path d="M0 0 L10 5 L0 10 z" fill="var(--br-coral)"/></marker></defs>')
    print(f"# cycle · {n}칸 · box_w = ({W} - {gap}*{n-1}) / {n} = {box_w:.1f}"
          + ("  ※ 라벨 넘침 있음" if over else ""))
    return _svg(defs + "\n" + "\n".join(rows), box_h + arc_h, "순환 고리")


# ── gate ─────────────────────────────────────────────────────────────────────
def gate(items, out="성과", drop="여기서 멈춤", r=75, gap=90, base=210):
    """통과 관문 사다리. 넷을 다 넘어야 끝에 닿는다.

    「하나라도 못 넘으면 성과가 없다」를 말하는 자리다. 3단계 로드맵은
    각 단계가 독립해 보이지만 이것은 직렬 조건임을 형태로 말한다."""
    n = len(items)
    if not 2 <= n <= 5:
        raise SystemExit(f"오류: 관문은 2~5개다. {n}개는 담기지 않는다.")
    ramp = _ramp()
    step = 2 * r + gap
    span = step * (n - 1) + 2 * r
    out_w = 250
    if span + out_w + 40 > W:
        raise SystemExit(f"오류: 관문 {n}개가 폭 {W}px 를 넘는다({span + out_w + 40:.0f}px). "
                         "관문을 줄이거나 반지름을 줄인다.")
    m = (W - span - out_w - 40) / 2
    rows, over = [], False
    for i, it in enumerate(items):
        cx = m + r + step * i
        rows.append(
            f'  <path d="M{cx - r:.1f} {base} A{r} {r} 0 0 1 {cx + r:.1f} {base}" '
            f'fill="none" stroke="{ramp[i % len(ramp)]}" stroke-width="14" '
            f'stroke-linecap="round"/>')
        over |= _fit(it, 2 * r + gap - 20, FS_BODY)
        rows.append(
            f'  <text x="{cx:.1f}" y="{base - r - 22:.0f}" text-anchor="middle" '
            f'font-size="{FS_TITLE}" font-weight="700" fill="var(--br-text)">'
            f'{i+1}</text>')
        rows.append(
            f'  <text x="{cx:.1f}" y="{base + 42:.0f}" text-anchor="middle" '
            f'font-size="{FS_BODY}" font-weight="600" fill="var(--br-text-2)">'
            f'{_esc(it)}</text>')

    rows.append(f'  <line x1="0" y1="{base}" x2="{m + span + 16:.1f}" y2="{base}" '
                f'stroke="var(--br-card-line)" stroke-width="2"/>')
    ox = m + span + 40
    rows.append(
        f'  <rect x="{ox:.1f}" y="{base - 54}" width="{out_w}" height="108" rx="16" '
        f'fill="var(--br-mark)"></rect>\n'
        f'  <text x="{ox + out_w/2:.1f}" y="{base + 11}" text-anchor="middle" '
        f'font-size="{FS_TITLE}" font-weight="800" fill="var(--br-on-dark)">'
        f'{_esc(out)}</text>')
    # 탈락 문구는 아치 줄에 붙인다. 지면 왼쪽 끝에 띄워 두면 어느 지점에서
    # 떨어진다는 말인지 형태가 말해 주지 못한다. 기준선에서 내려오는 짧은
    # 갈래를 그어 「관문 앞에서 빠진다」를 보이게 한다.
    dx = m - 34
    rows.append(
        f'  <path d="M{dx:.1f} {base} L{dx:.1f} {base + 92} L{dx + 26:.1f} {base + 92}" '
        f'fill="none" stroke="var(--br-coral)" stroke-width="3" stroke-dasharray="7 6"/>')
    rows.append(
        f'  <text x="{dx + 38:.1f}" y="{base + 101:.0f}" font-size="{FS_BODY}" '
        f'font-weight="600" fill="var(--br-coral)">{_esc(drop)}</text>')
    print(f"# gate · {n}관문 · step = 2*{r} + {gap} = {step} · 좌여백 {m:.1f}"
          + ("  ※ 라벨 넘침 있음" if over else ""))
    return _svg("\n".join(rows), base + 140, "통과 관문")


# ── stair ────────────────────────────────────────────────────────────────────
def stair(items, dh=58, top=40):
    """올라가는 계단. 단마다 다음 단이 높아진다.

    좌표가 전부 순번 i 의 1차식이다 — x, y, h 셋 다."""
    n = len(items)
    if not 3 <= n <= 6:
        raise SystemExit(f"오류: 계단은 3~6단이다. {n}단은 담기지 않는다.")
    ramp = _ramp()
    gap = 22
    w = (W - gap * (n - 1)) / n
    h0 = 96
    base = top + h0 + dh * (n - 1)
    rows, over = [], False
    for i, it in enumerate(items):
        x = (w + gap) * i
        h = h0 + dh * i
        y = base - h
        over |= _fit(it, w, FS_BODY)
        rows.append(
            f'  <rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="14" '
            f'fill="{ramp[i % len(ramp)]}"></rect>\n'
            f'  <text x="{x + w/2:.1f}" y="{y - 16:.1f}" text-anchor="middle" '
            f'font-size="{FS_BODY}" font-weight="700" fill="var(--br-text)">'
            f'{_esc(it)}</text>\n'
            f'  <text x="{x + w/2:.1f}" y="{y + 42:.1f}" text-anchor="middle" '
            f'font-size="{FS_TITLE}" font-weight="800" fill="var(--br-on-dark)">'
            f'{i+1}</text>')
    rows.append(f'  <line x1="0" y1="{base:.1f}" x2="{W}" y2="{base:.1f}" '
                f'stroke="var(--br-text-3)" stroke-width="2"/>')
    print(f"# stair · {n}단 · w = ({W} - {gap}*{n-1}) / {n} = {w:.1f} · 단높이 {dh}"
          + ("  ※ 라벨 넘침 있음" if over else ""))
    return _svg("\n".join(rows), base + 30, "단계 계단")


# ── track ────────────────────────────────────────────────────────────────────
def track(items, done=0, unit="", margin=130):
    """실적과 계획이 갈리는 연표. 분기점은 상태가 바뀌는 두 노드의 중점이다.

    done 은 실적으로 볼 앞쪽 개수다. 실적 구간은 실선, 계획 구간은 파선으로
    긋고 그 경계에 「현재」 선을 세운다."""
    n = len(items)
    if not 3 <= n <= 8:
        raise SystemExit(f"오류: 연표는 3~8점이다. {n}점은 담기지 않는다.")
    if not 0 <= done <= n:
        raise SystemExit(f"오류: --done 은 0~{n} 이다.")
    y = 120
    step = (W - 2 * margin) / (n - 1)
    cx = [margin + step * i for i in range(n)]
    rows = []
    if done >= 2:
        rows.append(f'  <line x1="{cx[0]:.1f}" y1="{y}" x2="{cx[done-1]:.1f}" y2="{y}" '
                    f'stroke="var(--br-mark)" stroke-width="4"/>')
    if done < n:
        a = cx[done - 1] if done >= 1 else cx[0]
        rows.append(f'  <line x1="{a:.1f}" y1="{y}" x2="{cx[-1]:.1f}" y2="{y}" '
                    f'stroke="var(--br-mark-mute)" stroke-width="4" '
                    f'stroke-dasharray="12 10"/>')
    if 1 <= done < n:                        # 분기점 = 마지막 실적과 첫 계획의 중점
        mid = (cx[done - 1] + cx[done]) / 2
        rows.append(f'  <line x1="{mid:.1f}" y1="{y - 66}" x2="{mid:.1f}" y2="{y + 52}" '
                    f'stroke="var(--br-coral)" stroke-width="3" stroke-dasharray="7 6"/>')
        rows.append(f'  <text x="{mid:.1f}" y="{y - 78}" text-anchor="middle" '
                    f'font-size="{FS_BODY}" font-weight="700" fill="var(--br-coral)">'
                    f'현재</text>')
    for i, it in enumerate(items):
        fill = "var(--br-mark)" if i < done else "var(--br-card)"
        stroke = "var(--br-mark)" if i < done else "var(--br-mark-mute)"
        rows.append(
            f'  <circle cx="{cx[i]:.1f}" cy="{y}" r="15" fill="{fill}" '
            f'stroke="{stroke}" stroke-width="4"/>\n'
            f'  <text x="{cx[i]:.1f}" y="{y + 58}" text-anchor="middle" '
            f'font-size="{FS_TITLE}" font-weight="700" fill="var(--br-text)">'
            f'{_esc(it)}{_esc(unit)}</text>')
        _fit(it + unit, step, FS_TITLE)
    print(f"# track · {n}점 · step = ({W} - 2*{margin}) / {n-1} = {step:.1f} · 실적 {done}점")
    return _svg("\n".join(rows), y + 90, "연표")


# ── interval (HTML) ──────────────────────────────────────────────────────────
def interval(rows_spec, lo=0, hi=24, unit="시", ticks=4):
    """시간축 위 구간 블록. SVG 가 아니라 HTML 이다 — 폭을 %로 주면 끝난다.

        left  = (시작 - lo) / (hi - lo) * 100%
        width = (끝   - 시작) / (hi - lo) * 100%

    기존 「일정 타임라인」은 마일스톤형이라 구간의 길이를 말하지 못한다.
    하루 안에서 어느 시간대에 무엇이 일어났는지는 이 조판이라야 보인다.

    rows_spec 한 줄 형식:  이름|시작-끝:라벨[:종류],시작-끝:라벨[:종류],...
    """
    span = hi - lo
    if span <= 0:
        raise SystemExit("오류: --domain 의 끝이 시작보다 커야 한다.")
    ramp = _ramp()
    kinds, out = {}, []
    lanes = 0        # 블록 밖으로 뺀 라벨이 몇 단까지 올라갔나. 축을 그만큼 밀어 올린다.
    # 트랙 폭(px) = 본문폭 - 이름칸 300 - 간격 28
    track_px = W - 300 - 28
    for spec in rows_spec:
        if "|" not in spec:
            raise SystemExit(f"오류: '{spec}' 에 '|' 가 없다. 이름|구간,구간 형식이다.")
        name, body = spec.split("|", 1)
        cells = []
        prev_end = None
        last_out = None        # 밖으로 뺀 직전 라벨 (왼쪽px, 필요폭px, 단)
        for seg in body.split(","):
            parts = seg.split(":")
            if len(parts) < 2:
                raise SystemExit(f"오류: 구간 '{seg}' 는 시작-끝:라벨 형식이다.")
            rng, label = parts[0], parts[1]
            kind = parts[2] if len(parts) > 2 else label
            try:
                s, e = (float(x) for x in rng.split("-"))
            except ValueError:
                raise SystemExit(f"오류: 구간 '{rng}' 을 숫자로 읽지 못했다.")
            if not (lo <= s < e <= hi):
                raise SystemExit(f"오류: 구간 {s}-{e} 가 도메인 {lo}~{hi} 를 벗어난다.")
            if prev_end is not None and s < prev_end:
                print(f"# 경고: '{name}' 에서 구간이 겹친다 ({prev_end} 뒤에 {s}).",
                      file=sys.stderr)
            prev_end = e
            if kind not in kinds and len(kinds) >= len(ramp):
                raise SystemExit(
                    f"오류: 구간 종류가 {len(kinds)+1}개다. 램프는 {len(ramp)}색뿐이라 "
                    "색이 겹친다. 종류를 묶거나 ':종류' 를 붙여 같은 것끼리 합친다.")
            kinds.setdefault(kind, ramp[len(kinds) % len(ramp)])
            left, width = (s - lo) / span * 100, (e - s) / span * 100
            # 라벨이 블록 안에 들어가는가. 안 들어가면 블록 밖 위쪽으로 뺀다.
            block_px = width / 100 * track_px
            inside = len(label) * FS_MIN * CH_RATIO + 24 <= block_px
            if inside:
                inner = (f'<span style="font:700 {FS_MIN}px/1 var(--br-font-kr);'
                         f'color:var(--br-on-dark)">{_esc(label)}</span>')
                last_out = None
            else:
                # 밖으로 뺀 라벨끼리도 겹친다. 앞 라벨의 오른쪽 끝을 넘지 못하면
                # 한 줄 위로 올려 엇갈리게 둔다. 두 줄로도 모자라면 실패시킨다.
                left_px = left / 100 * track_px
                need = len(label) * FS_MIN * CH_RATIO
                lane = 0
                if last_out is not None and left_px < last_out[0] + last_out[1] + 12:
                    lane = 1 - last_out[2]
                    if lane == last_out[2]:
                        raise SystemExit(
                            f"오류: '{label}' 을 놓을 자리가 없다. 앞 라벨과 겹친다. "
                            "구간을 묶거나 라벨을 줄인다.")
                last_out = (left_px, need, lane)
                lanes = max(lanes, lane + 1)
                bottom = 6 + lane * (FS_MIN + 8)
                inner = (f'<span style="position:absolute;left:0;'
                         f'bottom:calc(100% + {bottom}px);'
                         f'white-space:nowrap;font:700 {FS_MIN}px/1 var(--br-font-kr);'
                         f'color:var(--br-text-2)">{_esc(label)}</span>')
                print(f"# 알림: '{label}' 이 블록({block_px:.0f}px)에 안 들어가 "
                      f"위 {lane+1}단으로 뺐다.", file=sys.stderr)
            cells.append(
                f'      <div class="br-iv-seg" style="left:{left:.3f}%;'
                f'width:{width:.3f}%;background:{kinds[kind]}">{inner}</div>')
        out.append(f'    <div class="br-iv-row">\n'
                   f'      <div class="br-iv-name">{_esc(name)}</div>\n'
                   f'      <div class="br-iv-track">\n' + "\n".join(cells) +
                   f'\n      </div>\n    </div>')

    axis = "".join(
        f'<span>{lo + span * i / ticks:.0f}{_esc(unit)}</span>'
        for i in range(ticks + 1))
    # 축 눈금과 밖으로 뺀 라벨이 같은 띠를 쓰면 겹친다. 쓴 단 수만큼 축을 올린다.
    gap_px = 10 + lanes * (FS_MIN + 8)
    legend = "".join(
        f'<div class="br-legend-item"><div class="br-legend-name">'
        f'<span class="br-dot" style="background:{c}"></span>{_esc(k)}</div></div>'
        for k, c in kinds.items())
    print(f"# interval · 도메인 {lo}~{hi}{unit} · 트랙 {len(rows_spec)}줄 · 종류 {len(kinds)}"
          f" · 밖으로 뺀 라벨 {lanes}단 → 축 간격 {gap_px}px")
    return (f'  <div class="br-iv" style="--br-iv-gap:{gap_px}px">\n'
            f'    <div class="br-iv-axis">{axis}</div>\n'
            + "\n".join(out) + "\n"
            f'    <div class="br-legend br-legend--row">{legend}</div>\n'
            '  </div>')


def main():
    ap = argparse.ArgumentParser(description="블루 리포트 구조 도해 생성기")
    sub = ap.add_subparsers(dest="kind", required=True)

    p = sub.add_parser("cycle", help="되돌아오는 순환 고리 (3~6칸)")
    p.add_argument("items", help="쉼표로 구분한 칸 이름")
    p.add_argument("--back", default="", help="회귀 아크에 붙일 말")

    p = sub.add_parser("gate", help="통과 관문 사다리 (2~5관문)")
    p.add_argument("items", help="쉼표로 구분한 관문 이름")
    p.add_argument("--out", default="성과", help="끝 상자 문구")
    p.add_argument("--drop", default="여기서 멈춤", help="탈락 문구")

    p = sub.add_parser("stair", help="올라가는 계단 (3~6단)")
    p.add_argument("items", help="쉼표로 구분한 단 이름")

    p = sub.add_parser("track", help="실적/계획이 갈리는 연표 (3~8점)")
    p.add_argument("items", help="쉼표로 구분한 시점")
    p.add_argument("--done", type=int, default=0, help="앞에서부터 실적인 점 개수")
    p.add_argument("--unit", default="", help="시점 뒤에 붙일 단위 (예: 년)")

    p = sub.add_parser("interval", help="시간축 위 구간 블록 (HTML)")
    p.add_argument("row", nargs="+", help="이름|시작-끝:라벨[:종류],... 형식")
    p.add_argument("--domain", nargs=2, type=float, default=[0, 24],
                   metavar=("시작", "끝"))
    p.add_argument("--unit", default="시", help="축 단위")
    p.add_argument("--ticks", type=int, default=4, help="축 눈금 칸 수")

    a = ap.parse_args()
    if a.kind == "cycle":
        out = cycle([s.strip() for s in a.items.split(",")], a.back)
    elif a.kind == "gate":
        out = gate([s.strip() for s in a.items.split(",")], a.out, a.drop)
    elif a.kind == "stair":
        out = stair([s.strip() for s in a.items.split(",")])
    elif a.kind == "track":
        out = track([s.strip() for s in a.items.split(",")], a.done, a.unit)
    else:
        out = interval(a.row, a.domain[0], a.domain[1], a.unit, a.ticks)
    print(out)


if __name__ == "__main__":
    main()
