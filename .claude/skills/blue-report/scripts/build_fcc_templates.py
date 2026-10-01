#!/usr/bin/env python3
"""Blue Report FCC/KC 보고서 템플릿 14종을 조립한다.

## 왜 손으로 쓰지 않고 조립하는가

이 저장소의 발표 덱은 손으로 고치는 것이 사용법이다. 덱은 한 벌씩 내용이
다르기 때문이다. FCC/KC 템플릿은 사정이 다르다 — 14종이 **같은 부품**으로
같은 계약(fixture)을 그리고, 플러그인이 골라 쓰는 진열장이다. 손으로 14벌을
쓰면 부품 하나를 고칠 때마다 14곳을 고쳐야 하고, 실제로는 고치지 않아 갈라진다.

그래서 부품을 여기 한 곳에 두고 조립한다. 산출물 HTML 도 저장소에 커밋한다 —
받아 가는 쪽이 스크립트를 돌리지 않고 바로 열 수 있어야 하기 때문이다.
갈라짐은 verify_repo.py 의 "FCC/KC 템플릿 재생성 대조"가 잡는다.

    python3 scripts/build_fcc_templates.py            # 전부 다시 만든다
    python3 scripts/build_fcc_templates.py --check    # 파일과 다른지만 본다

## 지키는 것

- 수치·순서는 fixture 가 준 그대로 쓴다. 여기서 합계·비율·정렬을 계산하지 않는다.
- 색은 --br-* 토큰만. 이 파일에 hex 를 적지 않는다.
- 문체는 개조식(명사형 종결). A4 문서 검사기가 판정한다.
- 상태는 색만으로 말하지 않는다. 낱말이나 기호를 함께 둔다.
"""
import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SKILL = os.path.dirname(HERE)
FCC = os.path.join(SKILL, "assets", "fcc-kc")
OUT = os.path.join(FCC, "templates")
FIXTURE = os.path.join(FCC, "fixtures", "fixture-baseline.json")

MARK_LIGHT = ('<div class="br-mark" data-on="light"><!-- 로고 자리: apply_brand.py 가 '
              'brand.json 의 logo(다크용)·logoOnLight(밝은면용)로 교체한다 -->'
              '<span class="br-wordmark">COMPANY NAME</span></div>')
MARK_DARK = MARK_LIGHT.replace('data-on="light"', 'data-on="dark"')
STAMP = ('<div class="fk-fixture" data-field="fixture.label">'
         'DESIGN FIXTURE · 운영 분석 결과 아님</div>')


# ------------------------------------------------------------------ 지면 틀

def page(body, dark=False, land=False, pad=None):
    cls = "bd-page"
    if dark:
        cls += " bd-page--dark"
    if land:
        cls += " bd-page--land"
    style = f' style="{pad}"' if pad else ""
    head = f'<div class="bd-head">{MARK_DARK if dark else MARK_LIGHT}<span class="bd-docno"></span></div>'
    foot = ('<div class="bd-foot"><span><span class="bd-company">COMPANY NAME</span> · '
            '<span class="bd-doctitle"></span></span><span class="bd-pageno"></span></div>')
    return (f'<section class="{cls}"{style}>\n  {head}\n  <div class="bd-body">\n'
            + body.rstrip() + f'\n  </div>\n  {foot}\n</section>')


def doc(spec, pages):
    orient = ' data-orientation="landscape"' if spec.get("land") else ""
    # 특수 템플릿은 templates/special/ 아래에 있어 한 단 더 올라가야 한다.
    # 깊이를 파일 경로에서 세어 링크를 만든다 — 손으로 적으면 한쪽만 고쳐 놓는다.
    up = "../" * (spec["file"].count("/") + 2)
    links = "\n".join(f'<link rel="stylesheet" href="{h}">' for h in (
        up + "blue-report.css", up + "blue-doc.css", up + "doc-viewer.css",
        "../" * (spec["file"].count("/") + 1) + "fcc-kc.css"))
    return f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Blue Report FCC/KC · {spec['name']}</title>

<!-- 이 파일은 scripts/build_fcc_templates.py 가 만든다. 손으로 고치지 않는다 —
     고치면 재생성 대조에서 걸린다. 부품과 구성은 그 스크립트에 있다.
     덧층(fcc-kc.css)은 맨 뒤에 온다. 앞의 셋이 토큰·지면·뷰어를 맡는다. -->
{links}
</head>

<body>
<!-- ══════════════════════════════════════════════════════════════════════
     {spec['name']}
     대상: {spec['audience']}
     목적: {spec['purpose']}
     방향: {'A4 가로' if spec.get('land') else 'A4 세로'} · {len(pages)}쪽

     값은 fixtures/fixture-baseline.json 의 계약을 따른다. 지면의 모든 수치는
     서버가 계산한 것을 그대로 옮긴 것이며, 템플릿은 합계·비율·순위를 다시
     계산하지 않는다. [data-field]·[data-metric-id] 가 렌더러가 채우는 자리다.
     ══════════════════════════════════════════════════════════════════ -->
<div class="bd-doc{orient}" data-doc-title="{spec['title']}" data-doc-no="{spec['docNo']}"
     data-template-id="{spec['id']}">

{chr(10).join(pages)}

</div><!-- /.bd-doc -->

<div id="bd-hud">
  <span id="bd-pos"></span>
  <button id="bd-print">인쇄 · PDF</button>
</div>

<script src="{up}doc-viewer.js"></script>
</body>
</html>
"""


# ------------------------------------------------------------------ 공통 부품

def h1(t):
    return f'    <h1 class="bd-h1">{t}</h1>'


def h2(t):
    return f'    <h2 class="bd-h2">{t}</h2>'


def p(t, muted=False):
    st = ' style="color:var(--br-text-2)"' if muted else ""
    return f'    <p class="bd-p"{st}>{t}</p>'


def cover(spec, fx):
    s, r = fx["scope"], fx["report"]
    return f"""    <p class="fk-cover-eyebrow">{spec['coverEyebrow']}</p>
    <h1 class="fk-cover-title" data-field="report.title">{spec['title']}</h1>
    <p class="fk-cover-sub" data-field="report.subtitle">{spec['subtitle']}</p>

    {STAMP}

    <dl class="fk-scope fk-scope--narrow" style="margin-top:26px;border-color:var(--br-dark-line);background:transparent">
      <dt style="color:var(--br-accent-on-dark)">데이터 버전</dt>
      <dd style="color:var(--br-on-dark-2)" data-field="scope.sourceDataVersion">{s['sourceDataVersion']}</dd>
      <dt style="color:var(--br-accent-on-dark)">분석 기간</dt>
      <dd style="color:var(--br-on-dark-2)" data-field="scope.appliedPeriod">{s['appliedPeriod']}</dd>
      <dt style="color:var(--br-accent-on-dark)">커버리지</dt>
      <dd><span class="fk-cov fk-cov--full" data-field="scope.coverageComplete">커버리지</span></dd>
      <dt style="color:var(--br-accent-on-dark)">보고 대상</dt>
      <dd style="color:var(--br-on-dark-2)" data-field="report.audience">{spec['audience']}</dd>
    </dl>

    <div class="fk-signature">
      <span>분석·발행</span>
      <b data-field="report.publisher">{r['publisher']}</b>
      <span>·</span>
      <b data-field="report.product">{r['product']}</b>
      <span data-field="report.issuedAt">{r['issuedAt']}</span>
    </div>"""


def scope_band(fx, narrow=False, full=False):
    """검증 범위 띠. full 이면 데이터 버전·기간까지 싣는다.

    표지가 있는 A/B/C 는 거기서 버전·기간을 밝히므로 여기서 되풀이하지 않는다.
    표지가 없는 특수 템플릿은 이 띠가 유일한 자리라 full 로 쓴다 — 무엇을 센
    것인지 밝히지 않은 지면을 내보내지 않는다."""
    s = fx["scope"]
    cls = "fk-scope fk-scope--narrow" if narrow else "fk-scope"
    head = ("" if not full else
            f"""      <dt>데이터 버전</dt><dd data-field="scope.sourceDataVersion">{s['sourceDataVersion']}</dd>
      <dt>분석 기간</dt><dd data-field="scope.appliedPeriod">{s['appliedPeriod']}</dd>
""")
    return f"""    <dl class="{cls}">
{head}      <dt>모집단</dt><dd data-field="scope.populationDefinition">{s['populationDefinition']}</dd>
      <dt>레코드 단위</dt><dd data-field="scope.recordGrain">인증 건(certification)</dd>
      <dt>적용 필터</dt><dd data-field="scope.appliedFilters">{' · '.join(s['appliedFilters'])}</dd>
      <dt>커버리지</dt><dd><span class="fk-cov fk-cov--full">커버리지</span> · <span data-field="scope.coverageNote">{s['coverageNote']}</span></dd>
    </dl>"""


def metrics(items, cols=None):
    cls = "fk-metrics" + (f" fk-metrics--{cols}" if cols else "")
    rows = []
    for m in items:
        warn = " fk-metric--warn" if m.get("state") == "warn" else ""
        unit = f'<span class="fk-unit">{m["unit"]}</span>' if m.get("unit") else ""
        rows.append(f"""      <div class="fk-metric{warn}" data-metric-id="{m['id']}">
        <div class="fk-metric-k">{m['label']}</div>
        <div class="fk-metric-v">{m['value']}{unit}</div>
        <div class="fk-metric-n">{m.get('note', '')}</div>
      </div>""")
    return f'    <div class="{cls}">\n' + "\n".join(rows) + "\n    </div>"


ORIGIN_KO = {"server_fact": "서버 계산값", "ai_interpretation": "검증된 사실 아님",
             "human_note": "서버·AI 산출물 아님"}


def narr(origin, paras, field=None):
    body = "\n".join(f'      <p class="bd-p">{x}</p>' for x in paras)
    return (f'    <div class="fk-narr" data-narrative-origin="{origin}">\n'
            f'      <span class="fk-narr-k">{ORIGIN_KO[origin]}</span>\n{body}\n    </div>')


def warn(title, items, limit=False):
    cls = "fk-warn fk-warn--limit" if limit else "fk-warn"
    li = "\n".join(f"        <li>{x}</li>" for x in items)
    return (f'    <div class="{cls}">\n      <span class="fk-warn-k">{title}</span>\n'
            f"      <ul>\n{li}\n      </ul>\n    </div>")


def actions(items):
    rows = "\n".join(f"""      <div class="fk-act">
        <span class="fk-act-t">{a['text']}</span>
        <span class="fk-act-w">{a['who']}</span>
      </div>""" for a in items)
    return f'    <div class="fk-actions">\n{rows}\n    </div>'


def rank(rows, chart_id, caption):
    top = max(abs(r["v"]) for r in rows) or 1
    out = []
    for r in rows:
        mute = "" if r.get("subject") else " fk-rank-row--mute"
        w = abs(r["v"]) / top * 100
        out.append(f'      <div class="fk-rank-row{mute}"><span class="fk-rank-n">{r["n"]}</span>'
                   f'<span class="fk-rank-track"><span class="fk-rank-bar" style="--w:{w:.1f}%"></span></span>'
                   f'<span class="fk-rank-v">{r["d"]}</span></div>')
    return (p(caption, muted=True) + "\n" +
            f'    <div class="fk-rank" data-chart-id="{chart_id}">\n' + "\n".join(out) + "\n    </div>")


def line(points, partial_from, ymax, chart_id, caption):
    """추이 선. 부분 기간은 점선·음영과 라벨로 가른다.

    좌표는 여기서 계산한다 — 손으로 적으면 값이 바뀔 때 그림이 거짓말을 한다."""
    W, H, L, T, B = 640, 200, 40, 16, 156
    n = len(points)
    step = (W - L - 16) / max(n, 1)
    xs = [L + step * (i + .5) for i in range(n)]
    ys = [B - (pt["v"] / ymax) * (B - T) for pt in points]
    solid = " ".join(f"{x:.0f},{y:.0f}" for x, y in zip(xs[:partial_from], ys[:partial_from]))
    dash = " ".join(f"{x:.0f},{y:.0f}" for x, y in zip(xs[partial_from - 1:], ys[partial_from - 1:]))
    shade = (f'<rect class="fk-partial-bg" x="{xs[partial_from]-step/2:.0f}" y="{T}" '
             f'width="{W-16-(xs[partial_from]-step/2):.0f}" height="{B-T}"></rect>'
             if partial_from < n else "")
    dots = "".join(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="3"></circle>' for x, y in zip(xs, ys))
    vals = "".join(f'<text x="{x:.0f}" y="{y-12:.0f}" text-anchor="middle">{pt["d"]}</text>'
                   for x, y, pt in zip(xs, ys, points))
    labs = "".join(f'<text x="{x:.0f}" y="172" text-anchor="middle">{pt["l"]}</text>'
                   for x, pt in zip(xs, points))
    partlab = (f'<text x="{xs[-1]:.0f}" y="188" text-anchor="middle" '
               f'style="fill:var(--br-warn-text)">부분</text>' if partial_from < n else "")
    aria = " · ".join(f'{pt["l"]} {pt["d"]}' for pt in points)
    return f"""    <svg class="fk-line" viewBox="0 0 {W} {H}" role="img" aria-label="{caption} — {aria}" data-chart-id="{chart_id}">
      {shade}
      <line class="fk-grid" x1="{L}" y1="{T}" x2="{W-16}" y2="{T}"></line>
      <line class="fk-grid" x1="{L}" y1="{(T+B)//2}" x2="{W-16}" y2="{(T+B)//2}"></line>
      <line class="fk-axis" x1="{L}" y1="{B}" x2="{W-16}" y2="{B}"></line>
      <text x="{L-6}" y="{T+4}" text-anchor="end">{ymax}</text>
      <text x="{L-6}" y="{(T+B)//2+4}" text-anchor="end">{ymax//2}</text>
      <text x="{L-6}" y="{B+4}" text-anchor="end">0</text>
      <polyline class="fk-path" points="{solid}"></polyline>
      <polyline class="fk-path fk-path--partial" points="{dash}"></polyline>
      <g class="fk-dot">{dots}</g>
      <g>{vals}</g>
      <g class="fk-lbl">{labs}{partlab}</g>
    </svg>
    <p class="fk-legend">
      <span><b>실선</b> 마감된 구간</span>
      <span class="fk-legend--partial"><b>점선·음영</b> 부분 기간 · 마감 구간과 같은 자로 비교 불가</span>
    </p>"""


def table(head, rows, cls="bd-table", widths=None, cont=None):
    ws = widths or [None] * len(head)
    th = "".join("<th%s>%s</th>" % (' style="width:%s"' % w if w else "", h)
                 for h, w in zip(head, ws))
    tr = "\n".join("        <tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>" for r in rows)
    out = (f'    <table class="{cls}">\n      <thead><tr>{th}</tr></thead>\n'
           f"      <tbody>\n{tr}\n      </tbody>\n    </table>")
    if cont:
        out += f'\n    <p class="fk-cont">{cont}</p>'
    return out


def quality(items, note=None):
    cells = "\n".join(f'      <div class="fk-q"><div class="fk-q-k">{i["k"]}</div>'
                      f'<div class="fk-q-v">{i["v"]}</div></div>' for i in items)
    out = f'    <div class="fk-quality">\n{cells}\n    </div>'
    if note:
        out += "\n" + p(note, muted=True)
    return out


def lineage(fx):
    l = fx["lineage"]
    return f"""    <dl class="fk-lineage">
      <dt>스냅샷</dt><dd data-field="lineage.snapshotChecksum">{l['snapshotChecksum']}</dd>
      <dt>보고서 모델</dt><dd data-field="lineage.reportModelChecksum">{l['reportModelChecksum']}</dd>
      <dt>형식 간 일관성</dt><dd data-field="lineage.consistencyProjectionChecksum">{l['consistencyProjectionChecksum']}</dd>
      <dt>계보</dt><dd data-field="lineage.lineageChecksum">{l['lineageChecksum']}</dd>
      <dt>생성</dt><dd style="font-family:var(--br-font-kr)" data-field="lineage.generatedBy">{l['generatedBy']}</dd>
    </dl>"""


def evidence(fx, cont=None):
    e = fx["evidence"]
    rows = [[i["certificationId"], i["entity"], i["grantedAt"], i["sourceRef"],
             '<span class="fk-evi-st fk-evi-st--ok">확인</span>'] for i in e["items"]]
    return (p(f'근거 상태 <span class="fk-cov fk-cov--full" data-field="evidence.state">전체</span> · '
              f'반환 <span class="bd-key">{e["returned"]}</span> / 전체 '
              f'<span class="bd-key">{e["total"]}</span>건') + "\n" +
            table(["인증 식별자", "엔터티", "공개일", "출처", "상태"], rows,
                  cls="bd-table fk-evi",
                  widths=["30%", "26%", "14%", None, "12%"], cont=cont))


def empty(k, body):
    return (f'    <div class="fk-empty">\n      <span class="fk-empty-k">{k}</span>\n'
            f"      {body}\n    </div>")


def cols(left, right, mod=""):
    c = "fk-cols" + (f" fk-cols--{mod}" if mod else "")
    return f'    <div class="{c}">\n      <div>\n{left}\n      </div>\n      <div>\n{right}\n      </div>\n    </div>'


# ------------------------------------------------------------- 특수 분석 부품

def heatmap(cols_, rows, caption, scale_note):
    """교차 히트맵. 단조 램프 5단계 + 칸마다 숫자. 색만으로 값을 읽히지 않는다."""
    vals = [v for r in rows for v in r["v"] if v is not None]
    top = max(vals) if vals else 1
    th = "".join(f'<th class="fk-hm-col">{c}</th>' for c in cols_)
    body = []
    for r in rows:
        tds = []
        for v in r["v"]:
            if v is None:
                tds.append('<td><span class="fk-hm-cell fk-hm-cell--l0">—</span></td>')
                continue
            lv = 0 if v == 0 else min(5, max(1, round(v / top * 5)))
            tds.append(f'<td><span class="fk-hm-cell fk-hm-cell--l{lv}">{v}</span></td>')
        body.append(f'        <tr><td>{r["n"]}</td>' + "".join(tds) + "</tr>")
    scale = "".join(f'<i style="background:var(--br-bar-{b})"></i>' for b in (7, 6, 4, 2, 1))
    return (p(caption, muted=True) + "\n"
            + f'    <table class="fk-hm">\n      <thead><tr><th>구분</th>{th}</tr></thead>\n'
            + "      <tbody>\n" + "\n".join(body) + "\n      </tbody>\n    </table>\n"
            + f'    <p class="fk-hm-scale">낮음 {scale} 높음 · {scale_note}</p>')


def matrix(cols_, rows, caption, note):
    """전이 행렬. 대각선(제자리)과 이동을 눈으로 가른다."""
    th = "".join(f"<th>{c}</th>" for c in cols_)
    body = []
    for i, r in enumerate(rows):
        tds = []
        for j, v in enumerate(r["v"]):
            cls = "fk-mx-self" if i == j else ("fk-mx-move" if v else "")
            tds.append(f'<td class="{cls}">{v if v else "·"}</td>')
        body.append(f'        <tr><td>{r["n"]}</td>' + "".join(tds) + "</tr>")
    return (p(caption, muted=True) + "\n"
            + f'    <table class="bd-table bd-table--grid fk-mx">\n'
            + f"      <thead><tr><th>이전 → 이후</th>{th}</tr></thead>\n"
            + "      <tbody>\n" + "\n".join(body) + "\n      </tbody>\n    </table>\n"
            + p(note, muted=True))


def flow(steps):
    out = []
    for i, s in enumerate(steps):
        out.append(f'      <div class="fk-flow-node"><b>{s["n"]}</b>{s["d"]}</div>')
        if i < len(steps) - 1:
            out.append(f'      <div class="fk-flow-arrow">→<small>{s["to"]}</small></div>')
    return '    <div class="fk-flow">\n' + "\n".join(out) + "\n    </div>"


def small_multiples(items, unit):
    """단위는 칸마다 붙이지 않고 설명 한 줄로 뺀다 — 20칸에 20번 적으면 읽기만 방해한다."""
    top = max(abs(i["v"]) for i in items) or 1
    cells = []
    for i in items:
        alert = " fk-sm-c--alert" if i.get("alert") else ""
        cells.append(f"""      <div class="fk-sm-c{alert}">
        <div class="fk-sm-n">{i['n']}</div>
        <div class="fk-sm-v">{i['d']}</div>
        <div class="fk-sm-bar"><i style="--w:{abs(i['v'])/top*100:.0f}%"></i></div>
      </div>""")
    return '    <div class="fk-sm">\n' + "\n".join(cells) + "\n    </div>"


def delta_cards(items):
    cells = "\n".join(f"""      <div class="fk-delta-c fk-delta-c--{i['kind']}">
        <div class="fk-delta-k">{i['k']}</div>
        <div class="fk-delta-v">{i['v']}</div>
        <div class="fk-delta-n">{i['n']}</div>
      </div>""" for i in items)
    return '    <div class="fk-delta">\n' + cells + "\n    </div>"


def tele_panel(kind, title, sub, body):
    return (f'    <div class="fk-tele fk-tele--{kind}">\n'
            f'      <span class="fk-tele-k">{title} <small>{sub}</small></span>\n'
            f"{body}\n    </div>")


def count_semantics(rows):
    out = "\n".join(f'      <div class="fk-cnt-row"><span class="fk-cnt-k"><b>{r["k"]}</b> — {r["d"]}</span>'
                    f'<span class="fk-cnt-v">{r["v"]}</span></div>' for r in rows)
    return '    <div class="fk-cnt">\n' + out + "\n    </div>"


def cohort(rows, a_name, b_name, caption):
    top = max(max(r["a"], r["b"]) for r in rows) or 1
    out = []
    for r in rows:
        out.append(f"""      <div class="fk-coh-row">
        <span class="fk-coh-n">{r['n']}</span>
        <span class="fk-coh-pair">
          <span class="fk-coh-b"><span class="fk-coh-t"><i style="--w:{r['a']/top*100:.0f}%"></i></span><span class="fk-coh-v">{r['da']}</span></span>
          <span class="fk-coh-b fk-coh-b--b"><span class="fk-coh-t"><i style="--w:{r['b']/top*100:.0f}%"></i></span><span class="fk-coh-v">{r['db']}</span></span>
        </span>
      </div>""")
    legend = (f'    <p class="fk-legend"><span><b>위</b> {a_name}</span>'
              f'<span class="fk-legend--b"><b>아래</b> {b_name}</span></p>')
    return (p(caption, muted=True) + "\n" + '    <div class="fk-coh">\n' + "\n".join(out)
            + "\n    </div>\n" + legend)


def coverage_indicator(returned, total, note):
    pct = returned / total * 100 if total else 0
    return f"""    <div class="fk-covind">
      <div class="fk-covind-t"><i style="--w:{pct:.1f}%"></i></div>
      <div class="fk-covind-l"><span>반환 <b>{returned:,}</b>건</span><span>전체 <b>{total:,}</b>건 · {pct:.1f}%</span></div>
    </div>
{p(note, muted=True)}"""


def identity_panel(name, aliases, unresolved, ambiguous, method):
    return f"""    <div class="fk-idp">
      <div class="fk-idp-n" data-field="entityResolution.resolvedName">{name}</div>
      <p class="fk-idp-a">별칭 <b>{aliases}</b> · 미해소 <b>{unresolved}</b> · 모호 <b>{ambiguous}</b></p>
      <p class="fk-idp-a">해소 기준 — {method}</p>
    </div>"""


# ------------------------------------------------------------------ 템플릿 구성
#
# 각 종의 페이지 구성이 곧 그 보고서의 성격이다. A/B/C 는 색만 다른 변형이
# 아니라 정보 위계가 다르고, 특수 11종은 각자의 질문에 맞는 도해를 앞세운다.

def tail_pages(fx, spec, extra_limits=(), cont=None):
    """마지막 쪽 — 품질·제한·근거·계보. 모든 템플릿이 같은 자리에 같은 것을 둔다.

    보고서마다 신뢰 정보의 자리가 다르면 읽는 사람이 매번 찾아야 한다."""
    q = fx["quality"]
    return [
        page("\n".join([
            h1("품질과 제한"),
            quality([{"k": s["label"], "v": f'{s["value"]:,}' if isinstance(s["value"], int) else s["value"]}
                     for s in q["summary"]], "반환 행과 고유 인증이 같은 값 — 중복 없음"),
            warn("이 수치를 읽을 때", q["warnings"]),
            warn("이 보고서로 말할 수 없는 것", list(q["limitations"]) + list(extra_limits), limit=True),
            f"    {STAMP}",
        ])),
        page("\n".join([
            h1("근거와 계보"),
            evidence(fx, cont=cont or "근거 전량과 필드 대응표는 C(Evidence Dossier) 템플릿"),
            h2("계보와 체크섬"),
            lineage(fx),
            p("같은 데이터 버전·필터·기간으로 재실행 시 위 체크섬이 동일 — 값이 다르면 입력이 바뀐 것", muted=True),
            f"    {STAMP}",
        ])),
    ]


def spec_a(fx):
    m = fx["metrics"]
    return [
        page(cover(SPECS_META["a"], fx), dark=True,
             pad="display:flex;flex-direction:column"),
        page("\n".join([
            h1("핵심 결론"),
            scope_band(fx),
            metrics([{"id": x["id"], "label": x["label"], "value": f'{x["value"]:,}' if isinstance(x["value"], int) else x["value"],
                      "unit": x.get("unit"), "note": x.get("note"), "state": x.get("state")} for x in m]),
            narr("server_fact", [x for x in fx["narrative"][0]["paragraphs"]]),
            warn("이 수치를 읽을 때", fx["quality"]["warnings"]),
            quality([{"k": s["label"], "v": f'{s["value"]:,}' if isinstance(s["value"], int) else s["value"]}
                     for s in fx["quality"]["summary"]], "반환 행과 고유 인증이 같은 값 — 중복 없음"),
            f"    {STAMP}",
        ])),
        page("\n".join([
            h1("무엇이 결론을 뒷받침하는가"),
            h2("시험기관별 처리 건수"),
            rank([{"n": pt["label"], "v": pt["value"], "d": f'{pt["value"]:,}',
                   "subject": pt.get("emphasis") == "subject"}
                  for pt in fx["charts"][1]["series"][0]["points"]],
                 "lab_rank", "모집단 1,284건 · 상위 6개 기관 · 서버가 정한 순서 그대로"),
            h2("월별 인증 건수"),
            line([{"l": pt["label"], "v": pt["value"], "d": pt["value"]}
                  for pt in fx["charts"][0]["series"][0]["points"]],
                 fx["charts"][0]["partialFromIndex"], 220, "trend_monthly", "월별 인증 건수"),
            h2("엔터티 해소 상태"),
            table(["항목", "건수", "비고"],
                  [["해소 완료 제조사", "12", "사업자 식별자 우선 · 실패 시 정규화 상호 + 주소 대조"],
                   ["미해소", "3", "상호 표기만 확인 · 제조사 수에 미포함"],
                   ["모호", "1", "동일 상호 복수 법인 · 수기 확인 대기"]],
                  widths=["34%", "16%", None]),
            f"    {STAMP}",
        ])),
        page("\n".join([
            h1("해석과 의사결정 경계"),
            narr("server_fact", ["상위 1개 기관 529건 · 상위 3개 기관 958건 · 하위 9개 기관 326건"]),
            narr("ai_interpretation", fx["narrative"][1]["paragraphs"]),
            narr("human_note", fx["narrative"][2]["paragraphs"]),
            warn("이 보고서로 말할 수 없는 것", fx["quality"]["limitations"], limit=True),
            f"    {STAMP}",
        ])),
        page("\n".join([
            h1("권고와 다음 행동"),
            actions([{"text": r["text"], "who": f'{r["owner"]} · {r["due"]}'} for r in fx["recommendations"]]),
            h2("결정에 필요한 추가 확인"),
            table(["확인 항목", "확인처", "결정 영향"],
                  [["시험기관 A 4분기 예약 가용량", "기관 직접 문의", "분산 비율 결정"],
                   ["미해소 엔터티 3건 실체", "사업자 등록 대조", "제조사 수 · 순위 변동"],
                   ["처리 기간 분포", "공개 데이터 밖", "일정 위험 판단"]],
                  widths=["36%", "26%", None]),
            empty("공개 연락처 — 1건만 확인",
                  "공개 출처에서 확인된 것만 게재 · 추정 연락처 미작성. 전체 목록은 C(Evidence Dossier) 템플릿 사용"),
            f"    {STAMP}",
        ])),
        page("\n".join([
            h1("근거와 계보"),
            evidence(fx, cont="근거 전량과 필드 대응표는 C(Evidence Dossier) 템플릿"),
            h2("계보와 체크섬"),
            lineage(fx),
            p("PDF · DOCX · PPTX 는 같은 보고서 모델에서 파생 — 데이터 버전, 기간, 필터, 모집단, "
              "커버리지, 서버 지표, 근거 상태, 일관성 체크섬이 형식과 무관하게 동일", muted=True),
            f"    {STAMP}",
        ])),
    ]


def spec_b(fx):
    """B — 분석 대시보드. 가로 지면 · 두 단. 결론이 아니라 수치 검토가 목적이다."""
    m = fx["metrics"]
    return [
        page("\n".join([
            h1("분석 범위와 필터 계약"),
            scope_band(fx, full=True),
            metrics([{"id": x["id"], "label": x["label"],
                      "value": f'{x["value"]:,}' if isinstance(x["value"], int) else x["value"],
                      "unit": x.get("unit"), "note": x.get("note"), "state": x.get("state")} for x in m]
                    + [{"id": "lab_total", "label": "시험기관 수", "value": "12", "unit": "개", "note": "기간 내 1건 이상"},
                       {"id": "product_total", "label": "제품군", "value": "4", "unit": "종", "note": "무선 모듈 하위 분류"}]),
            cols(count_semantics([
                    {"k": "전체 모집단", "d": "필터 통과 전체", "v": "1,284"},
                    {"k": "반환 행", "d": "이 보고서가 받은 행", "v": "1,284"},
                    {"k": "고유 인증", "d": "인증 식별자 기준 중복 제거", "v": "1,284"},
                    {"k": "고유 엔터티", "d": "엔터티 해소 후 제조사", "v": "12"}]),
                 identity_panel("대상 제조사 12개사", "법인명 변경 2건 · 영문 표기 상이 5건",
                                "3건", "1건", "사업자 식별자 우선 · 실패 시 정규화 상호 + 주소 대조")),
            f"    {STAMP}",
        ]), land=True),
        page("\n".join([
            h1("기간 추이와 순위"),
            cols(line([{"l": pt["label"], "v": pt["value"], "d": pt["value"]}
                       for pt in fx["charts"][0]["series"][0]["points"]],
                      fx["charts"][0]["partialFromIndex"], 220, "trend_monthly", "월별 인증 건수"),
                 rank([{"n": pt["label"], "v": pt["value"], "d": f'{pt["value"]:,}',
                        "subject": pt.get("emphasis") == "subject"}
                       for pt in fx["charts"][1]["series"][0]["points"]],
                      "lab_rank", "시험기관별 처리 건수 · 모집단 1,284건")),
            narr("server_fact", ["마감 7개월 1,214건 · 부분 1개월 70건",
                                 "상위 3개 기관 958건 — 모집단의 74.6%"]),
            warn("이 수치를 읽을 때", fx["quality"]["warnings"]),
            f"    {STAMP}",
        ]), land=True),
        page("\n".join([
            h1("코호트 비교와 구성"),
            cols(cohort([{"n": "무선 모듈", "a": 612, "da": "612", "b": 498, "db": "498"},
                         {"n": "차량 전장", "a": 341, "da": "341", "b": 287, "db": "287"},
                         {"n": "가전", "a": 218, "da": "218", "b": 196, "db": "196"},
                         {"n": "산업 기기", "a": 113, "da": "113", "b": 132, "db": "132"}],
                        "2026 상반기", "2025 상반기",
                        "제품군별 인증 건수 · 같은 축 · 같은 단위 · 모집단 정의 동일"),
                 heatmap(["WLAN", "BLE", "UWB", "기타"],
                         [{"n": "무선 모듈", "v": [286, 214, 62, 50]},
                          {"n": "차량 전장", "v": [98, 142, 71, 30]},
                          {"n": "가전", "v": [121, 74, None, 23]},
                          {"n": "산업 기기", "v": [46, 38, 12, 17]}],
                         "제품군 x 기술 교차 · 칸 값은 인증 건수",
                         "— 표시는 해당 조합 0건")),
            warn("비가산 주의", [
                "다중 분류 인증이 있어 행·열 합계가 모집단(1,284)과 일치하지 않음",
                "코호트 비교는 모집단 정의가 같을 때만 성립 — 다르면 비교 가능 여부를 먼저 표시"]),
            f"    {STAMP}",
        ]), land=True),
        page("\n".join([
            h1("품질 상태와 근거"),
            # 근거 표는 열이 다섯이라 반 폭에 넣으면 출처가 여러 줄로 접혀 지면을 넘긴다.
            # 가로 지면에서는 표를 온 폭으로 두고 요약만 두 단으로 나눈다.
            cols(quality([{"k": s["label"], "v": f'{s["value"]:,}' if isinstance(s["value"], int) else s["value"]}
                          for s in fx["quality"]["summary"]]),
                 coverage_indicator(4, 4, "근거 전량 반환 · bounded 상태 아님")),
            evidence(fx, cont="전량 목록은 C 템플릿"),
            f"    {STAMP}",
        ]), land=True),
        page("\n".join([
            h1("제한사항과 계보"),
            cols(warn("이 보고서로 말할 수 없는 것", fx["quality"]["limitations"], limit=True),
                 lineage(fx)),
            p("PDF · DOCX · PPTX 는 같은 보고서 모델에서 파생 — 데이터 버전, 기간, 필터, 모집단, "
              "커버리지, 서버 지표, 근거 상태, 일관성 체크섬이 형식과 무관하게 동일", muted=True),
            f"    {STAMP}",
        ]), land=True),
    ]


def spec_c(fx):
    """C — 증거 도시에. 재현성이 목적이라 문서 통제와 필드 대응이 앞에 온다."""
    return [
        page(cover(SPECS_META["c"], fx), dark=True, pad="display:flex;flex-direction:column"),
        page("\n".join([
            h1("문서 통제"),
            table(["항목", "내용"],
                  [["보고서 번호", '<span class="bd-key">DEMO-FCC-2026-0001-C</span>'],
                   ["템플릿", "fcc-kc-c-evidence-dossier · v0.1.0"],
                   ["작성 근거", "Blue Report FCC/KC Insight 서버 산출 보고서 모델"],
                   ["검토 상태", '<span class="bd-chip">초안</span>'],
                   ["보존 기간", "산출일로부터 5년"],
                   ["재현 방법", "같은 데이터 버전·필터·기간으로 재실행 시 동일 체크섬"]],
                  widths=["26%", None]),
            h2("모집단 · 레코드 단위 · 필터"),
            scope_band(fx),
            count_semantics([
                {"k": "전체 모집단", "d": "필터 통과 전체", "v": "1,284"},
                {"k": "반환 행", "d": "이 보고서가 받은 행", "v": "1,284"},
                {"k": "고유 인증", "d": "인증 식별자 기준 중복 제거", "v": "1,284"},
                {"k": "고유 엔터티", "d": "엔터티 해소 후 제조사", "v": "12"},
                {"k": "미해소", "d": "상호 표기만 확인 · 위 12에 미포함", "v": "3"}]),
            f"    {STAMP}",
        ])),
        page("\n".join([
            h1("서버 수치와 원본 필드 대응"),
            p("표시된 모든 수치는 서버 산출값 — 이 문서가 다시 계산한 값 없음"),
            table(["표시 항목", "보고서 모델 필드", "원본 필드", "집계 방법"],
                  [["기간 내 인증 건수", "metrics.cert_total", "certification_id", "고유 개수"],
                   ["제조사 수", "metrics.entity_total", "applicant_name(정규화)", "해소 후 고유 개수"],
                   ["1위 시험기관 비중", "metrics.lab_share_top", "test_lab_id", "최상위 기관 건수 ÷ 모집단"],
                   ["전년 동기 대비", "metrics.yoy_delta", "grant_date", "동일 기간 폭 비교"],
                   ["월별 추이", "charts.trend_monthly", "grant_date", "월 단위 집계"],
                   ["시험기관 순위", "charts.lab_rank", "test_lab_id", "건수 내림차순"]],
                  widths=["24%", "24%", "22%", None]),
            h2("엔터티 해소"),
            identity_panel("대상 제조사 12개사", "법인명 변경 2건 · 영문 표기 상이 5건",
                           "3건", "1건", "사업자 식별자 우선 · 실패 시 정규화 상호 + 주소 대조"),
            f"    {STAMP}",
        ])),
        page("\n".join([
            h1("품질 예외와 제한사항"),
            narr("server_fact", ["예외 4종 · 모두 수치에 영향 있음 — 아래 표에 영향 범위 표시"]),
            quality([{"k": s["label"], "v": f'{s["value"]:,}' if isinstance(s["value"], int) else s["value"]}
                     for s in fx["quality"]["summary"]]),
            table(["예외", "건수", "처리", "영향"],
                  [["미해소 엔터티", "3", "제조사 수에서 제외", "제조사 수 · 순위"],
                   ["모호 엔터티", "1", "수기 확인 대기", "제조사 수"],
                   ["부분 기간", "1개월", "점선·음영 표기", "월 추이 마지막 점"],
                   ["다중 분류", "해당", "비가산 표기", "교차 분석 합계"]],
                  widths=["30%", "14%", "26%", None]),
            warn("이 수치를 읽을 때", fx["quality"]["warnings"]),
            warn("이 보고서로 말할 수 없는 것", fx["quality"]["limitations"], limit=True),
            f"    {STAMP}",
        ])),
        page("\n".join([
            h1("근거 목록"),
            coverage_indicator(4, 4, "근거 전량 반환 · bounded 상태 아님"),
            evidence(fx, cont="긴 목록은 쪽이 갈릴 때마다 머리행을 다시 찍음"),
            h2("공개 연락처"),
            table(["엔터티", "구분", "값", "출처", "확인일"],
                  [[c["entity"], {"website": "누리집", "email": "메일", "phone": "전화",
                                  "address": "주소"}[c["channel"]], c["value"], c["source"], c["verifiedAt"]]
                   for c in fx["publicContacts"]],
                  widths=["20%", "12%", None, "26%", "14%"]),
            p("공개 출처에서 확인된 것만 게재 · 추정 연락처 미작성 · 비공개 개인정보 미수록", muted=True),
            f"    {STAMP}",
        ])),
        page("\n".join([
            h1("계보와 검토"),
            lineage(fx),
            p("같은 데이터 버전·필터·기간으로 재실행 시 위 체크섬이 동일 — 값이 다르면 입력이 바뀐 것", muted=True),
            h2("검토·승인"),
            '    <div class="bd-sign">',
            '      <div><div class="bd-sign-k">작성</div><div class="bd-sign-v"></div></div>',
            '      <div><div class="bd-sign-k">검토</div><div class="bd-sign-v"></div></div>',
            '      <div><div class="bd-sign-k">승인</div><div class="bd-sign-v"></div></div>',
            "    </div>",
            f"    {STAMP}",
        ])),
    ]


def head_page(fx, title, ms, note_origin=None, note_paras=(), extra=None):
    """특수 템플릿 1쪽 — 범위 계약과 서버 지표. 어느 분석이든 여기서 시작한다."""
    parts = [h1(title), scope_band(fx, full=True), metrics(ms, cols=len(ms) if len(ms) < 4 else None)]
    if note_origin:
        parts.append(narr(note_origin, list(note_paras)))
    if extra:
        parts.append(extra)
    parts.append(f"    {STAMP}")
    return page("\n".join(parts))


def core_page(title, blocks):
    return page("\n".join([h1(title)] + list(blocks) + [f"    {STAMP}"]))


def spec_trend(fx):
    return [
        head_page(fx, "인증 추이 — 무엇을 어떤 자로 셌는가",
                  [{"id": "cert_total", "label": "기간 내 인증", "value": "1,284", "unit": "건"},
                   {"id": "month_avg", "label": "마감 월 평균", "value": "173.4", "unit": "건", "note": "1~7월 7개월"},
                   {"id": "partial", "label": "부분 기간", "value": "1", "unit": "개월", "note": "8월 1~15일", "state": "warn"}],
                  "server_fact", ["마감 7개월 1,214건 · 부분 1개월 70건",
                                  "월 최대 209건(7월) · 월 최소 138건(2월)"]),
        core_page("월별 추이", [
            line([{"l": pt["label"], "v": pt["value"], "d": pt["value"]}
                  for pt in fx["charts"][0]["series"][0]["points"]],
                 fx["charts"][0]["partialFromIndex"], 220, "trend_monthly", "월별 인증 건수"),
            warn("부분 기간 취급", [
                "8월은 15일까지 — 마감월과 같은 자로 비교 불가",
                "전년 동기 비교는 같은 기간 폭(1월 1일~8월 15일)으로만 성립",
                "추세 변화는 인증 상태 변화가 아님 — 공개 시점의 변화일 수 있음"]),
            table(["구간", "건수", "일평균", "비고"],
                  [["2026년 1~7월 (마감)", "1,214", "5.7", "비교 기준"],
                   ["2026년 8월 1~15일 (부분)", "70", "4.7", "마감월과 직접 비교 불가"],
                   ["2025년 1월~8월 15일", "1,085", "4.8", "전년 동기 · 같은 기간 폭"]],
                  widths=["36%", "16%", "16%", None])]),
        *tail_pages(fx, None, ["부분 기간을 마감 기간처럼 환산한 값 미제공"]),
    ]


def spec_cohort(fx):
    return [
        head_page(fx, "코호트 비교 — 비교 가능 여부부터",
                  [{"id": "coh_n", "label": "비교 코호트", "value": "2", "unit": "개"},
                   {"id": "coh_pop", "label": "모집단 정의", "value": "동일", "note": "필터·레코드 단위 일치"},
                   {"id": "coh_period", "label": "기간 폭", "value": "동일", "note": "1월 1일~8월 15일"}],
                  "server_fact", ["두 코호트의 모집단 정의·기간 폭 일치 — 비교 성립",
                                  "총량 차이 +199건 · 구성 차이는 제품군별로 상이"]),
        core_page("제품군별 비교", [
            cohort([{"n": "무선 모듈", "a": 612, "da": "612", "b": 498, "db": "498"},
                    {"n": "차량 전장", "a": 341, "da": "341", "b": 287, "db": "287"},
                    {"n": "가전", "a": 218, "da": "218", "b": 196, "db": "196"},
                    {"n": "산업 기기", "a": 113, "da": "113", "b": 132, "db": "132"}],
                   "2026 상반기", "2025 상반기", "같은 축 · 같은 단위 · 모집단 정의 동일"),
            table(["제품군", "2026", "2025", "총량 차이", "구성비 차이"],
                  [["무선 모듈", "612", "498", "+114", "47.7% → 47.4%"],
                   ["차량 전장", "341", "287", "+54", "27.5% → 26.4%"],
                   ["가전", "218", "196", "+22", "18.8% → 16.9%"],
                   ["산업 기기", "113", "132", "−19", "12.6% → 8.8%"]],
                  widths=["26%", "14%", "14%", "16%", None]),
            warn("총량과 구성비를 섞지 않음", [
                "산업 기기는 총량 감소 · 구성비도 감소 — 두 값이 같은 방향",
                "가전은 총량 증가 · 구성비 감소 — 전체가 더 빨리 늘어난 결과",
                "모집단이 다른 코호트는 총량 비교 불가 — 구성비만 비교 가능"])]),
        *tail_pages(fx, None, ["코호트 간 인과 관계 미제공 — 관측된 차이만 표시"]),
    ]


def spec_mfr360(fx):
    return [
        head_page(fx, "제조사 360 — 엔터티 해소부터",
                  [{"id": "m_cert", "label": "인증 건수", "value": "241", "unit": "건"},
                   {"id": "m_lab", "label": "사용 시험기관", "value": "4", "unit": "개"},
                   {"id": "m_prod", "label": "제품군", "value": "3", "unit": "종"}],
                  extra=identity_panel("주식회사 매우긴법인명테스트용제조사",
                                       "구 상호 1건 · 영문 표기 2건", "0건", "0건",
                                       "사업자 식별자 일치")),
        core_page("포트폴리오와 시험기관 구성", [
            rank([{"n": "WLAN 모듈", "v": 128, "d": "128", "subject": True},
                  {"n": "BLE 모듈", "v": 71, "d": "71"},
                  {"n": "UWB 모듈", "v": 42, "d": "42"}],
                 "mfr_product", "제품군별 인증 건수 · 서버가 정한 순서"),
            narr("ai_interpretation", ["시험기관 A 편중은 일정 위험과 연결 가능 — 처리 기간이 데이터에 없어 확정 불가"]),
            rank([{"n": "시험기관 A", "v": 121, "d": "121", "subject": True},
                  {"n": "시험기관 C", "v": 62, "d": "62"},
                  {"n": "시험기관 B", "v": 41, "d": "41"},
                  {"n": "시험기관 E", "v": 17, "d": "17"}],
                 "mfr_lab", "사용 시험기관 구성 · 같은 모집단(241건)"),
            warn("이 지면이 말하지 않는 것", [
                "관측된 인증 기록 — 시장점유율·매출·수주 아님",
                "미공개 인증은 모집단에 없음",
                "시험기관 선택의 까닭은 데이터 밖"], limit=True)]),
        *tail_pages(fx, None, ["엔터티 단일 대상 보고서 — 동종 비교는 일괄 비교 템플릿 사용"]),
    ]


def spec_lab360(fx):
    return [
        head_page(fx, "시험기관 360 — 처리 기록",
                  [{"id": "l_cert", "label": "처리 건수", "value": "529", "unit": "건"},
                   {"id": "l_share", "label": "모집단 내 비중", "value": "41.2", "unit": "%", "state": "warn"},
                   {"id": "l_mfr", "label": "거래 제조사", "value": "9", "unit": "개사"}],
                  "server_fact", ["기간 내 529건 처리 · 모집단 1,284건의 41.2%",
                                  "거래 제조사 9개사 · 상위 3개사가 318건(60.1%)"]),
        core_page("제조사·제품 구성과 변화", [
            rank([{"n": "제조사 가", "v": 142, "d": "142", "subject": True},
                  {"n": "제조사 나", "v": 98, "d": "98"},
                  {"n": "제조사 다", "v": 78, "d": "78"},
                  {"n": "그 외 6개사", "v": 211, "d": "211"}],
                 "lab_mfr", "제조사 구성 · 모집단 529건"),
            table(["구분", "건수", "비고"],
                  [["신규 유입 제조사", "2", "직전 반기 거래 없음"],
                   ["이탈 제조사", "1", "이번 반기 거래 없음"],
                   ["재진입 제조사", "1", "2024 하반기 이후 재거래"]],
                  widths=["36%", "16%", None]),
            warn("순위를 읽을 때", [
                "순위의 모집단은 필터를 통과한 1,284건 — 전체 시장 아님",
                "처리 건수는 처리 능력·품질과 다른 값",
                "기간 밖 처리분은 미포함"], limit=True)]),
        *tail_pages(fx, None, ["처리 기간·대기열은 공개 데이터에 없음"]),
    ]


def spec_flow(fx):
    return [
        head_page(fx, "시험기관 이동과 재진입",
                  [{"id": "f_move", "label": "이동 흐름", "value": "37", "unit": "건", "note": "제조사 기준 전이"},
                   {"id": "f_uniq", "label": "고유 제조사", "value": "21", "unit": "개사", "note": "흐름 총합과 다른 값"},
                   {"id": "f_re", "label": "재진입", "value": "4", "unit": "건"}],
                  "server_fact", ["흐름 총합 37건 · 고유 제조사 21개사 — 한 제조사가 여러 번 이동 가능",
                                  "재진입 4건은 이탈 후 같은 기관으로 되돌아온 경우"]),
        core_page("이동 흐름과 전이 행렬", [
            flow([{"n": "이전 기관", "d": "직전 반기 주 사용 기관", "to": "이동 37건"},
                  {"n": "이후 기관", "d": "이번 반기 주 사용 기관", "to": "재진입 4건"},
                  {"n": "복귀", "d": "이전 기관으로 되돌아옴", "to": ""}]),
            matrix(["A", "B", "C", "D"],
                   [{"n": "A", "v": [0, 6, 4, 2]},
                    {"n": "B", "v": [5, 0, 3, 1]},
                    {"n": "C", "v": [4, 2, 0, 3]},
                    {"n": "D", "v": [3, 1, 3, 0]}],
                   "제조사 전이 건수 · 행 = 이전 기관 · 열 = 이후 기관",
                   "대각선은 제자리(이동 없음)라 0으로 표기 · 흐름 총합 37건 ≠ 고유 제조사 21개사"),
            warn("흐름을 읽을 때", [
                "관측된 순서 — 인과 관계 아님",
                "이동의 까닭(가격·일정·품질)은 데이터 밖",
                "기간 경계에서 잘린 이동은 미집계"], limit=True)]),
        *tail_pages(fx, None, ["흐름 총합과 고유 엔터티 수를 합산하지 않음"]),
    ]


def spec_taxonomy(fx):
    return [
        head_page(fx, "제품군 x 기술 교차 분석",
                  [{"id": "t_cells", "label": "교차 조합", "value": "16", "unit": "칸", "note": "제품군 4 x 기술 4"},
                   {"id": "t_filled", "label": "값이 있는 칸", "value": "15", "unit": "칸"},
                   {"id": "t_multi", "label": "다중 분류", "value": "해당", "note": "합계 비가산", "state": "warn"}]),
        core_page("교차 매트릭스", [
            heatmap(["WLAN", "BLE", "UWB", "기타"],
                    [{"n": "무선 모듈", "v": [286, 214, 62, 50]},
                     {"n": "차량 전장", "v": [98, 142, 71, 30]},
                     {"n": "가전", "v": [121, 74, None, 23]},
                     {"n": "산업 기기", "v": [46, 38, 12, 17]}],
                    "칸 값은 인증 건수 · 색은 값의 크기(단조 램프)",
                    "— 표시는 해당 조합 0건"),
            narr("server_fact", ["값이 있는 칸 15 · 0건 칸 1 · 다중 분류 119건"]),
            warn("합계가 맞지 않는 까닭", [
                "다중 분류 인증이 있어 행·열 합계가 모집단(1,284)을 넘음",
                "한 인증이 두 기술로 분류되면 두 칸에 각각 계상",
                "미분류 건은 「기타」가 아니라 별도 — 아래 표 참조"]),
            table(["구분", "건수", "처리"],
                  [["단일 분류", "1,142", "해당 칸에 1회 계상"],
                   ["다중 분류", "119", "분류마다 계상 · 합계 비가산"],
                   ["미분류", "23", "교차표에서 제외 · 모집단에는 포함"]],
                  widths=["30%", "18%", None])]),
        *tail_pages(fx, None, ["교차표 합계와 모집단은 일치하지 않음 — 비가산 구조"]),
    ]


def spec_quality(fx):
    return [
        head_page(fx, "데이터 품질과 집계 의미",
                  [{"id": "q_pop", "label": "전체 모집단", "value": "1,284", "unit": "건"},
                   {"id": "q_rows", "label": "반환 행", "value": "1,284", "unit": "행"},
                   {"id": "q_unres", "label": "미해소 엔터티", "value": "3", "unit": "건", "state": "warn"}]),
        core_page("숫자가 다른 까닭", [
            narr("server_fact", ["같은 모집단에서 나온 여섯 가지 셈 — 정의가 다르면 값도 다름"]),
            count_semantics([
                {"k": "전체 모집단", "d": "필터를 통과한 인증 건 전체", "v": "1,284"},
                {"k": "반환 행", "d": "보고서가 받은 행 — 페이지 분할 전", "v": "1,284"},
                {"k": "고유 인증", "d": "인증 식별자 기준 중복 제거", "v": "1,284"},
                {"k": "고유 제조사", "d": "엔터티 해소 후", "v": "12"},
                {"k": "상호 기준 제조사", "d": "해소 전 문자열 기준 — 별칭이 따로 세어짐", "v": "19"},
                {"k": "미해소", "d": "식별자·주소 대조 실패 · 위 12에 미포함", "v": "3"}]),
            table(["품질 항목", "건수", "영향", "처리"],
                  [["결측 공개일", "0", "없음", "해당 없음"],
                   ["중복 인증 식별자", "0", "없음", "해당 없음"],
                   ["미해소 엔터티", "3", "제조사 수 · 순위", "제조사 수에서 제외"],
                   ["모호 엔터티", "1", "제조사 수", "수기 확인 대기"],
                   ["부분 기간", "1개월", "월 추이 마지막 점", "점선·음영 표기"]],
                  widths=["30%", "14%", "22%", None]),
            warn("경고를 줄이지 않음", [
                "품질 경고는 각주가 아니라 본문 — 수치와 같은 지면에 표시",
                "미해소 3건이 해소되면 제조사 수와 순위가 바뀔 수 있음"])]),
        *tail_pages(fx, None),
    ]


def spec_version(fx):
    return [
        head_page(fx, "데이터 버전 간 변경",
                  [{"id": "v_base", "label": "기준 버전", "value": "2026.07.31", "note": "직전 스냅샷"},
                   {"id": "v_cmp", "label": "비교 버전", "value": "2026.08.15", "note": "이번 스냅샷"},
                   {"id": "v_delta", "label": "변경 합계", "value": "62", "unit": "건"}]),
        core_page("무엇이 달라졌는가", [
            narr("server_fact", ["두 스냅샷 차이 62건 — 신규 48 · 변경 9 · 제외 3 · 미확정 2"]),
            delta_cards([
                {"kind": "new", "k": "신규", "v": "48", "n": "이번 스냅샷에 처음 나타난 인증"},
                {"kind": "chg", "k": "변경", "v": "9", "n": "기존 건의 필드 값 변경"},
                {"kind": "gone", "k": "제외", "v": "3", "n": "이번 스냅샷에 없음"},
                {"kind": "open", "k": "미확정", "v": "2", "n": "판정 대기"}]),
            warn("「제외」를 취소로 읽지 않음", [
                "데이터셋에서 사라진 것과 인증이 취소된 것은 다른 사건",
                "공개 지연·정정·재분류로도 사라질 수 있음",
                "취소 여부는 공식 고시로만 확인 가능"]),
            table(["구분", "인증 식별자", "엔터티", "달라진 것"],
                  [["신규", "2AXXX-WM100-2026", "제조사 가", "신규 공개"],
                   ["변경", "MSIP-CRM-XYZ-WM200", "제조사 나", "시험기관 코드 정정"],
                   ["제외", "R-C-ZZZ-WLAN-2026-0091", "제조사 라", "스냅샷에 없음 · 까닭 미확인"],
                   ["미확정", "2BYYY-BLE55-2026-REV2", "주식회사 매우긴법인명테스트용제조사", "판정 대기"]],
                  widths=["14%", "30%", "26%", None])]),
        *tail_pages(fx, None, ["변경의 까닭은 공개 데이터에 없음 — 관측된 차이만 표시"]),
    ]


def spec_telematics(fx):
    return [
        head_page(fx, "텔레매틱스 특수 분석",
                  [{"id": "tl_excl", "label": "상호배타 분류", "value": "4", "unit": "종"},
                   {"id": "tl_agg", "label": "집계형 그룹", "value": "6", "unit": "종"},
                   {"id": "tl_rank", "label": "독립 순위", "value": "3", "unit": "목록"}],
                  "server_fact", ["세 체계는 서로 다른 분류 축 — 합산 불가",
                                  "상호배타 4분류만 모집단을 남김없이 나눔"]),
        core_page("세 체계를 갈라 놓기", [
            tele_panel("excl", "상호배타 4분류", "합이 모집단과 일치",
                       table(["분류", "건수", "구성비"],
                             [["차량 내 통신", "196", "38.4%"], ["차량 대 외부", "142", "27.8%"],
                              ["위치 측위", "108", "21.1%"], ["기타", "64", "12.5%"]],
                             widths=["44%", "20%", None])),
            tele_panel("agg", "집계형 6그룹", "겹침 허용 · 합산 금지",
                       table(["그룹", "건수", "겹침"],
                             [["V2X", "121", "위치 측위와 겹침"], ["OBD 연동", "88", "차량 내 통신과 겹침"],
                              ["e-Call", "54", "차량 대 외부와 겹침"], ["원격 진단", "77", "복수 겹침"],
                              ["요금 정산", "31", "겹침 없음"], ["차량 공유", "43", "복수 겹침"]],
                             widths=["36%", "18%", None])),
            tele_panel("rank", "독립 순위 3목록", "서로 다른 기준 · 교차 합산 금지",
                       table(["목록", "1위", "2위", "3위"],
                             [["인증 건수", "제조사 가", "제조사 나", "제조사 다"],
                              ["기술 다양성", "제조사 라", "제조사 가", "제조사 마"],
                              ["시험기관 분산", "제조사 나", "제조사 마", "제조사 가"]],
                             widths=["26%", "24%", "24%", None])),
            ]),
        *tail_pages(fx, None, [
            "집계형 6그룹은 겹침이 있어 합이 모집단을 넘음 — 합산 금지",
            "독립 순위는 각각 다른 기준 — 순위끼리 더하거나 평균 내지 않음",
            "상호배타 분류만 구성비 계산 가능",
            "세 분류 체계 간 변환·합산 미제공"]),
    ]


def spec_batch(fx):
    ITEMS = [
        {"n": "제조사 가", "v": 142, "d": "142"}, {"n": "제조사 나", "v": 98, "d": "98"},
        {"n": "제조사 다", "v": 78, "d": "78"}, {"n": "제조사 라", "v": 71, "d": "71"},
        {"n": "제조사 마", "v": 64, "d": "64"}, {"n": "제조사 바", "v": 58, "d": "58"},
        {"n": "주식회사 매우긴법인명테스트용제조사", "v": 53, "d": "53"},
        {"n": "제조사 아", "v": 47, "d": "47"}, {"n": "제조사 자", "v": 41, "d": "41"},
        {"n": "제조사 차", "v": 38, "d": "38"}, {"n": "제조사 카", "v": 33, "d": "33"},
        {"n": "제조사 타", "v": 29, "d": "29"}, {"n": "제조사 파", "v": 24, "d": "24"},
        {"n": "제조사 하", "v": 21, "d": "21"}, {"n": "제조사 거", "v": 18, "d": "18"},
        {"n": "제조사 너", "v": 14, "d": "14"}, {"n": "제조사 더", "v": 11, "d": "11"},
        {"n": "제조사 러", "v": 9, "d": "9"}, {"n": "미해소 A", "v": 6, "d": "6", "alert": True},
        {"n": "미해소 B", "v": 4, "d": "4", "alert": True}]
    return [
        head_page(fx, "일괄 엔터티 비교 — 20개사",
                  [{"id": "b_n", "label": "비교 엔터티", "value": "20", "unit": "개사", "note": "상한"},
                   {"id": "b_sum", "label": "합계", "value": "859", "unit": "건"},
                   {"id": "b_unres", "label": "미해소 포함", "value": "2", "unit": "개", "state": "warn"}]),
        core_page("같은 축 · 같은 단위", [
            narr("server_fact", ["20개사 합계 859건 · 최대 142건 · 최소 4건"]),
            small_multiples(ITEMS, "건"),
            p("모든 칸이 같은 축(최댓값 142건 기준) · 같은 단위(건) — 칸마다 축이 다르면 비교가 아니라 착시", muted=True),
            warn("긴 이름과 미해소 처리", [
                "긴 법인명은 잘라 표시 · 전체 이름은 근거 목록에 그대로 수록",
                "미해소 2개사는 테두리로 구분 — 해소되면 값이 합쳐질 수 있음",
                "쪽이 갈리면 열 제목과 엔터티 식별 정보를 다시 표시"])]),
        *tail_pages(fx, None, ["20개 상한 — 초과분은 별도 보고서로 분리"]),
    ]


def spec_evidence(fx):
    return [
        head_page(fx, "정확한 근거와 공개 연락처",
                  [{"id": "e_ret", "label": "반환 근거", "value": "4", "unit": "건"},
                   {"id": "e_tot", "label": "전체 근거", "value": "4", "unit": "건"},
                   {"id": "e_ct", "label": "확인된 연락처", "value": "1", "unit": "건"}],
                  extra=coverage_indicator(4, 4, "근거 전량 반환 · bounded 상태 아님")),
        core_page("근거 목록과 연락처", [
            narr("server_fact", ["근거 4건 전량 반환 · 공개 연락처 1건 확인"]),
            evidence(fx, cont="쪽이 갈리면 머리행을 다시 표시"),
            h2("공개 연락처"),
            table(["엔터티", "구분", "값", "출처", "확인일"],
                  [[c["entity"], {"website": "누리집", "email": "메일", "phone": "전화",
                                  "address": "주소"}[c["channel"]], c["value"], c["source"], c["verifiedAt"]]
                   for c in fx["publicContacts"]],
                  widths=["20%", "12%", None, "26%", "14%"]),
            empty("연락처가 없는 엔터티",
                  "공개 출처에서 확인되지 않은 엔터티는 빈칸으로 남김 · 추정 연락처 미작성"),
            ]),
        *tail_pages(fx, None, [
            "연락처는 공개 출처에서 확인된 것만 게재 · 출처와 확인일 병기",
            "비공개 개인정보 미수록",
            "확인일 이후 변경 가능 — 사용 전 재확인 필요",
            "bounded 상태에서는 반환 근거가 전체의 일부 — 커버리지 표시 확인"]),
    ]


# ------------------------------------------------------------------ 목록과 실행

SPECS_META = {
    "a": {"id": "fcc-kc-a-executive-editorial", "file": "tpl-a-executive.html",
          "name": "A — Executive Editorial", "title": "무선 모듈 인증 동향과 시험기관 편중",
          "subtitle": "2026년 상반기 FCC/KC 공개 인증 데이터 분석 · 하반기 시험 물량 배분 결정용",
          "docNo": "DEMO-FCC-2026-0001", "audience": "경영진 · 영업 책임자",
          "purpose": "결론 · 위험 · 권고 · 다음 행동", "coverEyebrow": "경영진 보고 · 결정 요청",
          "build": spec_a},
    "b": {"id": "fcc-kc-b-analytical-dashboard", "file": "tpl-b-dashboard.html",
          "name": "B — Analytical Dashboard", "title": "인증 지표 대시보드",
          "subtitle": "2026년 상반기 FCC/KC 공개 인증 데이터 · 수치 비교와 추이 검토용",
          "docNo": "DEMO-FCC-2026-0002", "audience": "분석가 · 영업 운영 · 프로젝트 실무",
          "purpose": "수치 비교 · 추이 · 분류 · 순위 검토", "coverEyebrow": "분석 대시보드",
          "land": True, "build": spec_b},
    "c": {"id": "fcc-kc-c-evidence-dossier", "file": "tpl-c-dossier.html",
          "name": "C — Evidence Dossier", "title": "인증 분석 근거 도시에",
          "subtitle": "재현성 · 근거 제출 · 감사 대응용 · 2026년 상반기 FCC/KC 공개 인증 데이터",
          "docNo": "DEMO-FCC-2026-0001-C", "audience": "품질 · 심사 · 감사 · 증거 검토",
          "purpose": "재현성 · 근거 제출 · 예외 확인", "coverEyebrow": "증거 도시에 · 재현 가능",
          "build": spec_c},
}

SPECIALS = [
    ("certification-trend", "1. Certification Trend Report", "인증 추이 분석",
     "부분 기간을 가려 표시한 월별 추이", spec_trend),
    ("cohort-comparison", "2. Cohort Comparison Report", "코호트 비교 분석",
     "같은 기준으로 견줄 수 있는지부터 판정", spec_cohort),
    ("manufacturer-360", "3. Manufacturer/Applicant 360 Report", "제조사 360 분석",
     "엔터티 해소 · 포트폴리오 · 사용 시험기관", spec_mfr360),
    ("test-lab-360", "4. Test Lab 360 Report", "시험기관 360 분석",
     "처리 기록 · 제조사 구성 · 유입과 이탈", spec_lab360),
    ("lab-flow-reentry", "5. Lab Flow & Re-entry Report", "시험기관 이동과 재진입",
     "전이 행렬과 흐름 · 총합과 고유 수의 구분", spec_flow),
    ("product-technology-taxonomy", "6. Product × Technology Taxonomy Report", "제품군 x 기술 교차 분석",
     "교차 히트맵 · 비가산 구조 표시", spec_taxonomy),
    ("data-quality-count-semantics", "7. Data Quality & Count Semantics Report", "데이터 품질과 집계 의미",
     "숫자가 다른 까닭을 대조표로", spec_quality),
    ("data-version-change-digest", "8. Data Version Change Digest", "데이터 버전 간 변경",
     "신규 · 변경 · 제외 · 미확정 분리", spec_version),
    ("telematics-special", "9. Telematics Special Analysis Report", "텔레매틱스 특수 분석",
     "상호배타 4분류 · 집계형 6그룹 · 독립 순위 3목록", spec_telematics),
    ("batch-entity-review", "10. Batch Entity Review Report", "일괄 엔터티 비교",
     "최대 20개사 · 같은 축 작은 배수", spec_batch),
    ("exact-evidence-contacts", "11. Exact Evidence & Public Contacts Report", "정확한 근거와 공개 연락처",
     "근거 커버리지와 출처 확인 연락처", spec_evidence),
]

for _i, (_slug, _name, _title, _sub, _fn) in enumerate(SPECIALS, start=1):
    SPECS_META[_slug] = {
        "id": f"fcc-kc-s-{_slug}", "file": f"special/tpl-s{_i:02d}-{_slug}.html",
        "name": _name, "title": _title, "subtitle": _sub + " · DESIGN FIXTURE 기준",
        "docNo": f"DEMO-FCC-2026-S{_i:02d}", "audience": "분석 담당 · 실무 검토",
        "purpose": _title, "coverEyebrow": "특수 분석", "build": _fn,
    }


def build_all():
    fx = json.load(open(FIXTURE, encoding="utf-8"))
    out = {}
    for key, spec in SPECS_META.items():
        pages = spec["build"](fx)
        out[os.path.join(OUT, spec["file"])] = doc(spec, pages)
    return out


def main():
    ap = argparse.ArgumentParser(description="FCC/KC 템플릿 조립")
    ap.add_argument("--check", action="store_true", help="파일과 다른지만 본다")
    a = ap.parse_args()

    made = build_all()
    if a.check:
        bad = []
        for path, html in made.items():
            cur = open(path, encoding="utf-8").read() if os.path.isfile(path) else None
            if cur != html:
                bad.append(os.path.relpath(path, SKILL) + (" — 파일 없음" if cur is None else " — 내용 다름"))
        if bad:
            print(f"  실패  FCC/KC 템플릿이 스크립트 산출물과 다르다 — {len(bad)}건")
            for b in bad:
                print(f"    · {b}")
            print("\n  python3 scripts/build_fcc_templates.py 로 다시 만든다.")
            return 1
        print(f"  통과  FCC/KC 템플릿 {len(made)}종 — 스크립트 산출물과 일치")
        return 0

    for path, html in made.items():
        os.makedirs(os.path.dirname(path), exist_ok=True)
        open(path, "w", encoding="utf-8").write(html)
    print(f"템플릿 {len(made)}종 생성")
    for path in sorted(made):
        print("  " + os.path.relpath(path, SKILL))
    return 0


if __name__ == "__main__":
    sys.exit(main())
