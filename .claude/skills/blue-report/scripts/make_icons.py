#!/usr/bin/env python3
"""라이브 계통 아이콘 — Lucide 를 골라 blue-live.css 안에 CSS 마스크로 심는다.

    python3 scripts/make_icons.py           # 받아서 심는다 (npm 레지스트리 접속 필요)
    python3 scripts/make_icons.py --check   # 지금 CSS 가 목록과 맞는지만 본다 (오프라인)

## 왜 아이콘을 따로 두는가

사내 발표 덱은 장마다 24x24 선 아이콘을 수십 개 쓴다(카드 머리 · 아이콘 타일 ·
체크 목록 · 흐름도 마디). 견본에 아이콘이 없으면 에이전트마다 SVG 를 손으로 그려
넣고, 굵기·끝 모양·크기가 덱마다 갈라진다. 같은 모양을 한 벌로 고정한다.

## 왜 CSS 마스크인가

    <i class="bl-i bl-i--server" aria-hidden="true"></i>

- 색은 글자색(currentColor)을 따른다 — 토큰으로 칠하고 다크면에서 저절로 뒤집힌다
- 크기는 글자 크기(em)를 따른다 — 배율 엔진(rem)을 그대로 탄다
- 장을 복사할 때 따라올 스프라이트(<svg><symbol>)가 없다. 클래스 하나로 끝난다
- --single-file 산출물에 CSS 와 함께 들어간다. 외부 파일을 부르지 않는다

## 왜 Lucide 인가

사내 발표 덱의 아이콘이 24x24 · stroke 2 · round cap/join 계열이었다. Lucide 가 그
규격이고 ISC(일부 Feather 유래분은 MIT) 라이선스라 재배포 조건이 가볍다 — 저작권
고지를 사본에 함께 두는 것뿐이다. 고지는 CSS 블록 머리와 assets/LICENSE-Lucide.txt 에 둔다.

판을 고정한다(VERSION). 판이 바뀌면 같은 이름의 모양이 달라질 수 있어, 올릴 때는
여기 숫자를 바꾸고 화면을 눈으로 확인한다.
"""
import argparse
import io
import json
import os
import re
import sys
import tarfile
import urllib.parse
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
SKILL = os.path.dirname(HERE)
CSS = os.path.join(SKILL, "assets", "blue-live.css")
LICENSE_OUT = os.path.join(SKILL, "assets", "LICENSE-Lucide.txt")

PACKAGE = "lucide-static"
VERSION = "1.52.0"
START = "/* @icons:start — scripts/make_icons.py 가 쓴다. 손으로 고치지 않는다 */"
END = "/* @icons:end */"

# 보고서 지면에 실제로 나오는 것만 고른다. 갈래별로 묶어 둔다 — 카탈로그 덱의
# 아이콘 장이 이 순서로 보여 준다. 이름은 Lucide 이름 그대로다.
ICONS = {
    "사람·조직": ["user", "users", "user-check", "user-round", "user-cog", "building-2", "building",
                "briefcase", "landmark", "handshake", "graduation-cap", "hand", "store"],
    "문서": ["file-text", "files", "file-search", "file-check", "file-spreadsheet",
            "folder", "folder-open", "clipboard-check", "clipboard-list", "book-open",
            "notebook-pen", "pen-line", "stamp", "presentation", "receipt", "inbox", "ticket",
            "tag", "image", "video", "play"],
    "수치": ["chart-column", "chart-bar", "chart-line", "chart-area", "chart-spline",
            "chart-no-axes-combined", "trending-up", "trending-down", "activity",
            "gauge", "sigma", "coins", "wallet", "scale"],
    "기술": ["server", "database", "hard-drive", "cpu", "circuit-board", "cloud",
            "monitor", "laptop", "smartphone", "globe", "network", "cable",
            "radio-tower", "plug", "bot", "brain", "sparkles", "scan-search"],
    "보안": ["lock", "lock-open", "shield-check", "shield-alert", "key-round", "eye", "gavel"],
    "흐름": ["workflow", "git-branch", "git-merge", "waypoints", "route", "map",
            "repeat", "refresh-cw", "arrow-right", "arrow-up-right", "send",
            "upload", "download", "share-2", "link", "layers", "boxes", "blocks",
            "package", "layout-grid"],
    "판단": ["check", "circle-check", "x", "circle-x", "triangle-alert", "info",
            "circle-help", "lightbulb", "target", "flag", "badge-check", "award",
            "trophy", "list-checks", "list-todo", "search", "filter", "star", "circle-alert"],
    "도구·현장": ["settings", "cog", "wrench", "rocket", "zap", "factory",
                "flask-conical", "microscope", "thermometer", "mouse-pointer-click",
                "megaphone", "mail", "message-square", "messages-square", "phone", "headset", "bell",
                "map-pin"],
    "시간": ["clock", "calendar", "calendar-check", "timer", "hourglass"],
}


def names():
    out = []
    for group in ICONS.values():
        out += group
    dup = sorted({n for n in out if out.count(n) > 1})
    if dup:
        raise SystemExit(f"아이콘 이름 중복: {', '.join(dup)}")
    return out


def fetch():
    """npm 레지스트리에서 고정한 판의 묶음을 받아 아이콘 원본과 라이선스를 꺼낸다."""
    meta_url = f"https://registry.npmjs.org/{PACKAGE}/{VERSION}"
    with urllib.request.urlopen(meta_url, timeout=60) as r:
        meta = json.load(r)
    if meta.get("license") != "ISC":
        raise SystemExit(f"라이선스가 바뀌었다: {meta.get('license')}. 재배포 조건을 다시 확인한다.")
    with urllib.request.urlopen(meta["dist"]["tarball"], timeout=300) as r:
        blob = r.read()
    want = set(names())
    svgs, lic = {}, None
    with tarfile.open(fileobj=io.BytesIO(blob), mode="r:gz") as tar:
        for m in tar.getmembers():
            if m.name == "package/LICENSE":
                lic = tar.extractfile(m).read().decode("utf-8")
            mm = re.match(r"package/icons/([a-z0-9-]+)\.svg$", m.name)
            if mm and mm.group(1) in want:
                svgs[mm.group(1)] = tar.extractfile(m).read().decode("utf-8")
    missing = sorted(want - set(svgs))
    if missing:
        raise SystemExit(f"{PACKAGE} {VERSION} 에 없는 이름: {', '.join(missing)}")
    if not lic:
        raise SystemExit("LICENSE 를 찾지 못했다 — 재배포 조건이 없으면 싣지 않는다")
    return svgs, lic


def to_mask(svg):
    """원본 SVG 를 마스크용 data URI 로 줄인다.

    마스크는 알파만 본다. 색은 검정 하나로 두고, 크기 속성은 뺀다 — 크기는 CSS 가
    em 으로 준다. 굵기 2 · 둥근 끝은 그대로 둔다(사내 발표 덱과 같은 규격)."""
    body = re.sub(r"<!--.*?-->", "", svg, flags=re.S)
    inner = re.search(r"<svg[^>]*>(.*)</svg>", body, re.S).group(1)
    inner = re.sub(r"\s+", " ", inner).strip()
    inner = re.sub(r"\s*/>", "/>", inner).replace("> <", "><")
    out = ("<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' "
           "stroke='black' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'>"
           + inner.replace('"', "'") + "</svg>")
    return "data:image/svg+xml," + urllib.parse.quote(out, safe=" :/=',.-")


def block(svgs, lic):
    head = ("/* 아이콘 — Lucide " + VERSION + " (" + PACKAGE + ") 에서 " + str(len(svgs)) + "개.\n"
            "   쓰는 법   <i class=\"bl-i bl-i--server\" aria-hidden=\"true\"></i>\n"
            "   색은 글자색, 크기는 글자 크기를 따른다. 목록은 scripts/make_icons.py 의 ICONS.\n\n"
            "   저작권 고지 (사본마다 함께 둔다) ───────────────────────────────\n"
            + "\n".join("   " + ln if ln.strip() else "" for ln in lic.strip().splitlines())
            + "\n*/")
    rules = [f'.bl-i--{n} {{ --bl-i: url("{to_mask(svgs[n])}") }}' for n in names()]
    return START + "\n" + head + "\n" + "\n".join(rules) + "\n" + END


def check():
    """오프라인 점검 — 블록이 있고, 목록의 이름이 빠짐없이 들어 있고, 고지가 있는가."""
    css = open(CSS, encoding="utf-8").read()
    fails = []
    m = re.search(re.escape(START) + r"(.*?)" + re.escape(END), css, re.S)
    if not m:
        fails.append("blue-live.css 에 아이콘 블록 표식이 없다")
    else:
        have = set(re.findall(r"\.bl-i--([a-z0-9-]+)\s*\{", m.group(1)))
        miss = [n for n in names() if n not in have]
        extra = sorted(have - set(names()))
        if miss:
            fails.append(f"목록에 있는데 CSS 에 없는 아이콘 {len(miss)}개: {', '.join(miss[:8])}")
        if extra:
            fails.append(f"CSS 에만 있는 아이콘 {len(extra)}개: {', '.join(extra[:8])}")
        if "ISC License" not in m.group(1):
            fails.append("CSS 블록에 저작권 고지가 없다")
    if not os.path.isfile(LICENSE_OUT):
        fails.append("assets/LICENSE-Lucide.txt 가 없다")
    for f in fails:
        print(f"  실패 — {f}")
    if not fails:
        print(f"  아이콘 {len(names())}개 · Lucide {VERSION} · 고지 있음")
    return 1 if fails else 0


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true", help="지금 CSS 가 목록과 맞는지만 본다")
    a = ap.parse_args()
    if a.check:
        sys.exit(check())

    svgs, lic = fetch()
    css = open(CSS, encoding="utf-8").read()
    new = block(svgs, lic)
    pat = re.compile(re.escape(START) + r".*?" + re.escape(END), re.S)
    if not pat.search(css):
        raise SystemExit("blue-live.css 에 아이콘 블록 표식이 없다 — 표식 두 줄을 먼저 둔다")
    css = pat.sub(lambda _: new, css)
    open(CSS, "w", encoding="utf-8").write(css)
    open(LICENSE_OUT, "w", encoding="utf-8").write(lic.strip() + "\n")
    print(f"아이콘 {len(svgs)}개를 blue-live.css 에 심었다 · {os.path.relpath(LICENSE_OUT, SKILL)}")
    sys.exit(check())


if __name__ == "__main__":
    main()
