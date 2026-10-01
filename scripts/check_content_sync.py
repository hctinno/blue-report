#!/usr/bin/env python3
"""HTML 덱과 PPTX 내용이 갈라졌는지 본다.

같은 내용이 `assets/deck-*.html` 과 `pptx/content.js` 두 곳에 따로 있다.
HTML 이 기준이고 PPTX 는 그 내용을 데이터로 옮긴 것이라, 한쪽만 고치면
같은 덱인데 형식에 따라 내용이 달라진다. 사람 눈으로는 잘 보이지 않는다.

두 곳을 합치지 않는 이유 — HTML 덱은 손으로 고치는 것이 이 시스템의 사용법이다
(`assets/deck-*.html` 을 복사해 내용만 바꾼다). HTML 을 생성물로 만들면 그 사용법이
사라진다. 그래서 원본을 둘로 두고, 갈라짐을 사람이 아니라 이 스크립트가 잡는다.

    python3 scripts/check_content_sync.py
    python3 scripts/check_content_sync.py --deck internal

대조 항목
  슬라이드 수 · 문서명 · 제목 · 리드 · 발표자 노트 · 세로 막대(이름·값)
  · 도넛(범례 이름·값) · 표(머리글·행)

레이아웃·문체·색은 대상이 아니다. 그쪽은 check_deck.py 가 본다.
종료 코드는 어긋난 곳이 있으면 1 이다.
"""
import argparse
import html as htmllib
import json
import os
import re
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILL = os.path.join(ROOT, ".claude", "skills", "blue-report")
ASSETS = os.path.join(SKILL, "assets")
CONTENT_JS = os.path.join(SKILL, "pptx", "content.js")

# content.js 의 덱 키 → HTML 덱 파일. deck-template.html 은 카탈로그라 PPTX 판이 없다.
DECKS = {
    "internal": "deck-internal-report.html",
    "weekly": "deck-weekly-report.html",
    # AX 덱은 본문 1장 + 부록 구조라 HTML 과 PPTX 의 슬라이드 구성이 다르다.
    # HTML 1장(대시보드)을 PPTX 는 표 1장으로 옮긴다. 그래서 이 대조에서 뺀다.
    # team 덱의 2쪽(부록)도 같은 이유로 뺀다 — HTML 은 표 + 특이사항 목록을 나란히
    # 두 상자로 나누는데, PPTX 는 슬라이드 종류를 늘리지 않으려고 특이사항을 표
    # 아래 강조 행으로 붙인다(ax 덱의 "결정 요청"과 같은 방법). DOM 모양이 달라
    # 표 개수·열 비교가 애초에 성립하지 않는다.
    "exec": "deck-exec-report.html",
    "allhands": "deck-allhands.html",
    "sales": "deck-sales-proposal.html",
    "project": "deck-project-report.html",
    "training": "deck-training.html",
}


# ------------------------------------------------------------------ 공통 도구

# 분모(.br-bar-of)는 값이 아니라 견주는 대상이다. "174 / 180" 에서 막대가 말하는
# 값은 174 뿐이므로, 대조 전에 통째로 걷어낸다. 단위(.br-sup)는 그대로 둔다 —
# 양쪽에 단위가 있으면 그때는 같아야 한다는 기존 규칙이 있다.
OF_RE = re.compile(r'<span class="br-bar-of">.*?</span>', re.S)


def text(fragment):
    """태그를 벗기고 공백을 하나로 줄인다."""
    s = re.sub(r"<[^>]+>", "", OF_RE.sub("", fragment))
    return re.sub(r"\s+", " ", htmllib.unescape(s)).strip()


def flat(node):
    """content.js 의 lede/title 조각([문자열, {k: 강조}])을 문자열로 편다."""
    if node is None:
        return ""
    if isinstance(node, str):
        return node
    if isinstance(node, dict):
        return str(node.get("k", node.get("t", "")))
    if isinstance(node, list):
        return "".join(flat(x) for x in node)
    return str(node)


def norm(s):
    return re.sub(r"\s+", " ", str(s)).strip()


def num(s):
    """'36.0%' · '174' → 비교 가능한 숫자. 숫자가 아니면 None."""
    m = re.search(r"-?\d+(?:\.\d+)?", str(s))
    return float(m.group()) if m else None


# '36.0%' · '312h' — 숫자 뒤에 붙는 단위. HTML 은 지면에 찍고 PPTX 는 생성기가 붙이므로
# 한쪽에만 있는 것이 정상이다. 양쪽 다 있으면 그때는 같아야 한다.
UNIT_RE = re.compile(r"^\s*(-?[\d,]+(?:\.\d+)?)\s*([^\d\s]*)\s*$")


def same_value(a, b):
    """숫자는 값으로, 그 밖은 문자열로 견준다.

    36 과 36.0 을 다르다고 하지 않고, '36%' 와 36 도 다르다고 하지 않는다.
    후자는 단위를 PPTX 생성기가 붙이기 때문이다(`labelFormat` · `sup`).
    '2026.08.01 ~ 08.31' 처럼 숫자로 떨어지지 않는 것은 문자열로 견준다."""
    ma, mb = UNIT_RE.match(norm(a)), UNIT_RE.match(norm(b))
    if ma and mb:
        if abs(float(ma.group(1).replace(",", "")) - float(mb.group(1).replace(",", ""))) >= 1e-9:
            return False
        ua, ub = ma.group(2), mb.group(2)
        return not (ua and ub) or ua == ub
    return norm(a) == norm(b)


# ---------------------------------------------------------------- HTML 쪽 추출

def split_frames(html):
    """`.br-frame` 단위로 슬라이드를 자른다."""
    starts = [m.start() for m in re.finditer(r'<div class="br-frame"', html)]
    if not starts:
        return []
    ends = starts[1:] + [len(html)]
    return [html[a:b] for a, b in zip(starts, ends)]


def lines(fragment):
    """줄바꿈을 공백으로 살려 두고 태그를 벗긴다.

    리드는 <br> 로 두 줄을 적는다. 그냥 태그만 벗기면 앞줄 끝과 뒷줄 머리가
    붙어 "…지연 2지연 2건은…" 이 되어 대조가 헛돈다."""
    return text(re.sub(r"<br\s*/?>", " ", fragment))


def html_facts(frame):
    """한 슬라이드에서 대조 가능한 사실만 뽑는다."""
    f = {}

    m = re.search(r'data-notes="([^"]*)"', frame)
    f["notes"] = norm(htmllib.unescape(m.group(1))) if m else ""

    # 제목 — 한 지면에서 가장 많이 읽히는 한 줄이다. 여기가 갈라지면 같은 보고인데
    # 형식에 따라 주장이 달라진다. v1.24.0 에서 실제로 그렇게 갈라졌고, 그때는
    # 이 대조가 없어 검사가 통과했다. 표지·마무리는 br-title 을 쓰지 않아 빠진다.
    m = re.search(r'<h2\b[^>]*\bclass="[^"]*\bbr-title\b[^"]*"[^>]*>(.*?)</h2>', frame, re.S)
    if m:
        f["title"] = lines(m.group(1))

    led = re.findall(r'<p\b[^>]*\bclass="[^"]*\bbr-lede\b[^"]*"[^>]*>(.*?)</p>', frame, re.S)
    if led:
        f["lede"] = norm(" ".join(lines(x) for x in led))

    # 막대 — 세로(.br-col-*)와 가로(.br-bar-name/.br-bar-val) 두 배치를 모두 읽는다.
    # class 뒤에 style 같은 속성이 붙어도 걸리게 한다. 예전 정규식은 class 속성이
    # 태그의 마지막일 때만 맞아서 막대를 통째로 놓쳤고, 그래서 "HTML 없음" 이 떴다.
    def cls(name):
        return re.findall(rf'<div\b[^>]*\bclass="[^"]*\b{name}\b[^"]*"[^>]*>(.*?)</div>', frame, re.S)

    vals = [text(x) for x in cls("br-col-val")]
    names = [text(x) for x in cls("br-col-name")]
    if not (vals and names):
        names = [text(x) for x in cls("br-bar-name")]
        vals = [text(x) for x in cls("br-bar-val")]
    if vals and names:
        f["bar"] = {"names": names, "values": vals}

    # 도넛 — 범례가 이름과 값을 함께 들고 있다
    leg = re.findall(
        r'<div class="br-legend-name">(.*?)</div>\s*<div class="br-legend-val">(.*?)</div>',
        frame, re.S)
    if leg:
        f["donut"] = {"names": [text(a) for a, _ in leg], "values": [text(b) for _, b in leg]}

    # 표
    if "<table" in frame:
        head = [text(x) for x in re.findall(r"<th[^>]*>(.*?)</th>", frame, re.S)]
        rows = []
        for tr in re.findall(r"<tr>(.*?)</tr>", frame, re.S):
            cells = re.findall(r"<td([^>]*)>(.*?)</td>", tr, re.S)
            if not cells:
                continue
            # colspan 은 빈 칸으로 편다. content.js 는 칸을 하나씩 들고 있다.
            row = []
            for attrs, body in cells:
                span = re.search(r'colspan="(\d+)"', attrs)
                row.append(text(body))
                row.extend([""] * (int(span.group(1)) - 1 if span else 0))
            rows.append(row)
        f["table"] = {"head": head, "rows": rows}

    return f


def read_html(fname):
    path = os.path.join(ASSETS, fname)
    src = open(path, encoding="utf-8").read()
    m = re.search(r'data-deck-title="([^"]*)"', src)
    return {
        "docTitle": norm(htmllib.unescape(m.group(1))) if m else "",
        "slides": [html_facts(fr) for fr in split_frames(src)],
    }


# ------------------------------------------------------------ content.js 쪽

def read_content_js():
    """node 로 실제 모듈을 읽는다. 정규식으로 JS 를 파싱하지 않는다."""
    script = (
        "const c = require(%s);\n"
        "const out = {};\n"
        "for (const [k, v] of Object.entries(c)) if (v && v.slides) out[k] = v;\n"
        "process.stdout.write(JSON.stringify(out));\n"
    ) % json.dumps(CONTENT_JS)
    with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False, encoding="utf-8") as fh:
        fh.write(script)
        tmp = fh.name
    try:
        r = subprocess.run(["node", tmp], capture_output=True, text=True)
        if r.returncode != 0:
            raise RuntimeError(f"content.js 를 읽지 못했다 — {r.stderr.strip()[:300]}")
        return json.loads(r.stdout)
    finally:
        os.unlink(tmp)


def js_facts(slide):
    f = {"notes": norm(slide.get("notes", ""))}

    if slide.get("title"):
        f["title"] = norm(flat(slide.get("title")) + " " + flat(slide.get("titleBold", "")))
    if slide.get("lede"):
        f["lede"] = norm(" ".join(flat(l) for l in slide["lede"]))

    if slide.get("type") == "compare":
        # 좌우 두 카드에 가로 막대가 하나씩. HTML 도 좌 → 우 순서로 적혀 있다.
        # 예전에는 HTML 쪽 가로 막대를 못 읽어 이 슬라이드가 통째로 대조 밖이었다.
        bars = list(slide.get("left", {}).get("bars", [])) + list(slide.get("right", {}).get("bars", []))
        if bars:
            f["bar"] = {"names": [norm(b.get("name", "")) for b in bars],
                        "values": [norm(str(b.get("val", ""))) for b in bars]}
    if slide.get("type") == "progress":
        # 공유 트랙형. 트랙이 계획, 채움이 실적이므로 막대 하나에 값이 둘이다.
        # HTML 은 "174" 와 "/ 180" 을 나눠 적으므로 값은 실적만 견준다.
        bars = slide.get("bars", [])
        if bars:
            f["bar"] = {"names": [norm(b.get("name", "")) for b in bars],
                        "values": [norm(str(b.get("val", ""))) for b in bars]}
    if slide.get("type") == "bar":
        f["bar"] = {"names": [norm(x) for x in slide.get("categories", [])],
                    "values": [norm(v) for v in slide.get("values", [])]}

    if slide.get("type") == "donut":
        seg = slide.get("segments", [])
        f["donut"] = {"names": [norm(s.get("name", "")) for s in seg],
                      "values": [norm(s.get("value", "")) for s in seg]}

    if slide.get("type") == "table":
        f["table"] = {
            "head": [norm(flat(h.get("t", h))) for h in slide.get("head", [])],
            "rows": [[norm(flat(c.get("t", c) if isinstance(c, dict) else c)) for c in row]
                     for row in slide.get("rows", [])],
        }
    return f


# -------------------------------------------------------------------- 대조

def compare_deck(key, hd, cd, problems):
    where = f"{key}"

    if not same_value(hd["docTitle"], cd.get("docTitle", "")):
        problems.append(f"{where} 문서명 — HTML「{hd['docTitle']}」 · PPTX「{cd.get('docTitle','')}」")

    hs, cs = hd["slides"], cd.get("slides", [])
    if len(hs) != len(cs):
        problems.append(f"{where} 슬라이드 수 — HTML {len(hs)}장 · PPTX {len(cs)}장")

    for i, (h, c_raw) in enumerate(zip(hs, cs), start=1):
        c = js_facts(c_raw)
        at = f"{where} {i}장"

        if h["notes"] != c["notes"]:
            problems.append(f"{at} 발표자 노트\n      HTML: {h['notes'][:80]}\n      PPTX: {c['notes'][:80]}")

        # 제목·리드는 한쪽에만 있는 것이 정상이다 — 표지처럼 배치가 다른 장이 있다.
        # 양쪽에 다 있을 때만 견준다.
        for kind, label in (("title", "제목"), ("lede", "리드")):
            if kind in h and kind in c and norm(h[kind]) != norm(c[kind]):
                problems.append(f"{at} {label}\n      HTML: {h[kind]}\n      PPTX: {c[kind]}")

        # 형식 한계로 배치가 다른 슬라이드는 마크만 뺀다. 문서명·장수·노트는 계속 본다.
        # 덱을 통째로 빼는 것(ax)보다 잃는 범위가 작다.
        if c_raw.get("syncSkip"):
            continue

        for kind, label in (("bar", "막대"), ("donut", "도넛")):
            if kind in h and kind in c:
                for field, fl in (("names", "이름"), ("values", "값")):
                    a, b = h[kind][field], c[kind][field]
                    if len(a) != len(b):
                        problems.append(f"{at} {label} {fl} 개수 — HTML {len(a)} · PPTX {len(b)}")
                    elif not all(same_value(x, y) for x, y in zip(a, b)):
                        problems.append(f"{at} {label} {fl}\n      HTML: {a}\n      PPTX: {b}")
            elif (kind in h) != (kind in c):
                problems.append(f"{at} {label} — 한쪽에만 있다 "
                                f"(HTML {'있음' if kind in h else '없음'} · "
                                f"PPTX {'있음' if kind in c else '없음'})")

        if "table" in h and "table" in c:
            if [norm(x) for x in h["table"]["head"]] != c["table"]["head"]:
                problems.append(f"{at} 표 머리글\n      HTML: {h['table']['head']}\n      PPTX: {c['table']['head']}")
            hr, cr = h["table"]["rows"], c["table"]["rows"]
            if len(hr) != len(cr):
                problems.append(f"{at} 표 행 수 — HTML {len(hr)} · PPTX {len(cr)}")
            else:
                for r, (a, b) in enumerate(zip(hr, cr), start=1):
                    if len(a) != len(b) or not all(same_value(x, y) for x, y in zip(a, b)):
                        problems.append(f"{at} 표 {r}행\n      HTML: {a}\n      PPTX: {b}")


def main():
    ap = argparse.ArgumentParser(description="HTML 덱과 PPTX 내용 동기화 점검")
    ap.add_argument("--deck", choices=sorted(DECKS), help="한 종만 본다")
    a = ap.parse_args()

    try:
        content = read_content_js()
    except Exception as e:
        print(f"  실패  {e}")
        return 1

    targets = {a.deck: DECKS[a.deck]} if a.deck else DECKS
    problems, checked = [], 0

    for key, fname in targets.items():
        if key not in content:
            problems.append(f"{key} — content.js 에 없다")
            continue
        compare_deck(key, read_html(fname), content[key], problems)
        checked += 1

    if problems:
        print(f"  실패  HTML 덱과 PPTX 내용이 갈라졌다 — {len(problems)}건")
        for p in problems:
            print(f"    · {p}")
        print("\n  HTML 이 기준이다. pptx/content.js 를 HTML 에 맞춘다.")
        return 1

    print(f"  통과  내용 동기화 — 덱 {checked}종의 노트·막대·도넛·표가 HTML 과 일치")
    return 0


if __name__ == "__main__":
    sys.exit(main())
