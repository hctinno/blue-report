#!/usr/bin/env python3
"""덱 템플릿을 단일 HTML 파일로 묶는다.

CSS를 인라인해 첨부 파일 없이 어디서나 열리는 한 장짜리 덱을 만든다.
--artifact 를 주면 <html>/<head>/<body> 껍데기를 벗겨 Artifact 발행용으로 낸다.

    python3 build_single_file.py                       # dist/blue-report-deck.html
    python3 build_single_file.py --artifact            # dist/blue-report-artifact.html
    python3 build_single_file.py --artifact --deck ax -o /tmp/ax-artifact.html

--brand 경로는 어디서 실행하느냐에 따라 다르다. 두 자리를 헷갈리면 파일을 못 찾는다.

    저장소 스킬 폴더에서   --brand ../../../brand/hct/brand.json
    저장소 루트에서        --brand brand/hct/brand.json
    계정 스킬 설치본에서   --brand brand/hct/brand.json   (묶음 안에 brand/ 가 들어 있다)

--deck 은 덱 이름과 A4 문서 이름(minutes)을 받는다. 생략하면 카탈로그다.

**웹 보드는 받지 않는다.** 보드에는 뷰어가 없어서 이 스크립트가 기대하는 것
(뷰어 JS 의 제목 표식, 뷰어 CSS 의 html,body 배경)이 둘 다 없다. 보드를 한 파일로
묶으려면 apply_brand.py 를 쓴다.

    python3 apply_brand.py --brand brand/hct/brand.json --deck manage --single-file -o 보드.html
"""
import argparse
import base64
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
ASSETS = os.path.join(ROOT, "assets")
DIST = os.path.join(ROOT, "dist")

# 덱·문서 이름. apply_brand.py 와 같은 것을 쓴다. 한곳에서만 고치도록 거기서 읽어 온다.
sys.path.insert(0, HERE)
from apply_brand import DECKS, DOCS, BOARDS, resolve  # noqa: E402

DECK = os.path.join(ASSETS, DECKS["catalog"])

# 로컬 자원 참조. 이름을 목록으로 박아 두지 않는다 — 덱은 deck-viewer,
# A4 문서는 doc-viewer 를 쓰므로 목록으로 두면 종류가 늘 때마다 여기를 고쳐야 한다.
LOCAL_CSS_RE = re.compile(r'<link rel="stylesheet" href="([^":/]+\.css)">')
LOCAL_JS_RE = re.compile(r'<script src="([^":/]+\.js)"></script>')

# @font-face 의 url(...). 인라인한 CSS 안에 남으면 상대 경로라 단일 파일에서 깨진다.
FONT_URL_RE = re.compile(r"url\(\s*['\"]?(fonts/[^'\")]+\.woff2)['\"]?\s*\)")

# 뷰어 CSS 가 지면 바깥 바탕을 정한다. 덱은 #111, A4 문서는 회색이다.
BODY_BG_RE = re.compile(r'html\s*,\s*body\s*\{[^}]*?background:\s*([^;}]+)')


def inline_fonts(css, assets_dir):
    """@font-face 의 woff2 를 data URI 로 바꾼다.

    단일 파일은 어디로든 옮겨 다니므로 상대 경로가 남으면 글자가 시스템
    폰트로 떨어진다. Artifact 는 더 엄해서, 폰트를 fonts.gstatic.com 에서만
    받는다 — 저장소가 들고 있는 파일이든 CDN 이든 링크로는 절대 못 들어간다.
    본문에 심는 것이 유일한 길이다.

    woff2 는 이미 압축돼 있어 base64 로 약 1.37배가 된다. 425KB → 582KB."""
    def one(m):
        path = os.path.join(assets_dir, m.group(1))
        if not os.path.isfile(path):
            raise SystemExit(f"폰트를 찾지 못했다: {path}\n"
                             f"  만들려면: python3 scripts/make_font_subset.py")
        b64 = base64.b64encode(open(path, "rb").read()).decode("ascii")
        return f"url(data:font/woff2;base64,{b64})"

    return FONT_URL_RE.sub(one, css)


def inline_assets(html, assets_dir=None):
    """<link>·<script src>로 걸린 로컬 자원을 본문에 인라인한다.

    폰트도 함께 심는다 — 바깥에서 받아 오는 글자는 이제 없다."""
    d = assets_dir or ASSETS

    def one(m, wrap, is_css=False):
        path = os.path.join(d, m.group(1))
        if not os.path.isfile(path):
            return m.group(0)
        text = open(path, encoding="utf-8").read()
        if is_css:
            text = inline_fonts(text, d)
        return wrap[0] + text + wrap[1]

    html = LOCAL_CSS_RE.sub(lambda m: one(m, ("<style>\n", "\n</style>"), True), html)
    html = LOCAL_JS_RE.sub(lambda m: one(m, ("<script>\n", "\n</script>")), html)
    return html


def build(artifact=False, brand_path=None, deck="catalog", out_path=None):
    deck_path = resolve(deck)
    if not os.path.exists(deck_path):
        raise SystemExit(f"덱·문서를 찾지 못했다: {deck}\n"
                         f"덱 이름: {' · '.join(DECKS)}\n"
                         f"문서 이름: {' · '.join(DOCS)}\n"
                         f"웹 보드({' · '.join(BOARDS)})는 apply_brand.py --single-file 로 묶는다")
    base = os.path.basename(deck_path)
    # 보드는 뷰어가 없다. 그대로 진행하면 아래 두 단정문이 알 수 없는 메시지로 터진다 —
    # 실제로 `--deck manage` 가 "뷰어 JS 인라인 실패 (data-deck-title 없음)" 로 죽었다.
    # 무엇을 쓰라는 것인지 여기서 먼저 말한다.
    if base.startswith("board-"):
        raise SystemExit(
            f"웹 보드는 이 스크립트가 묶지 않는다: {deck}\n"
            f"        보드에는 뷰어가 없어 제목 표식과 html,body 배경이 둘 다 없다.\n"
            f"        한 파일로 묶으려면 apply_brand.py 를 쓴다 —\n"
            f"        python3 apply_brand.py --brand <brand.json> --deck {deck} --single-file -o 보드.html")
    # 라이브 덱도 마찬가지다. 자기 뷰어(live-viewer.js)가 따로 있고 지면이 .br-frame 이
    # 아니라 .bl-sl 이라 여기서 기대하는 구조가 하나도 맞지 않는다.
    if base.startswith("live-"):
        raise SystemExit(
            f"라이브 덱은 이 스크립트가 묶지 않는다: {deck}\n"
            f"        라이브 계통은 지면이 .bl-sl 이고 뷰어가 live-viewer.js 로 따로 있다.\n"
            f"        한 파일로 묶으려면 apply_brand.py 를 쓴다 —\n"
            f"        python3 apply_brand.py --brand <brand.json> --deck {deck} --single-file -o 라이브.html")
    is_doc = base.startswith("doc-")
    html = open(deck_path, encoding="utf-8").read()
    if brand_path:
        # 순환 import를 피하려고 여기서 늦게 불러온다 (apply_brand 도 이 모듈을 쓴다).
        from apply_brand import load_brand, logo_uris, apply
        brand = load_brand(brand_path)
        uris = logo_uris(brand, brand_path)   # 키 목록은 apply_brand 가 한 곳에서 정한다
        html, n, left = apply(html, brand, uris)
        print(f"브랜드 적용 {n}건" + (f" · 남은 자리표시자 {len(left)}건" if left else ""))
    html = inline_assets(html)
    assert "--br-page" in html, "CSS 인라인 실패"
    marker = "data-doc-title" if is_doc else "data-deck-title"
    assert marker in html, f"뷰어 JS 인라인 실패 ({marker} 없음)"

    if not artifact:
        out = out_path or os.path.join(DIST, "blue-report-deck.html")
    else:
        # Artifact는 <!doctype>/<head>/<body>를 발행 시점에 씌운다. 본문만 남긴다.
        # 온전한 문서를 그대로 올리면 껍데기 안에 껍데기가 겹친다. 브라우저가
        # 관대해서 보이기는 하지만 <title>이 죽고 파서가 태그를 버린다.
        head = re.search(r"<head>(.*?)</head>", html, re.S).group(1)
        body = re.search(r"<body[^>]*>(.*?)</body>", html, re.S).group(1)

        # 남기는 것은 <title> 과 인라인된 <style> 뿐이다. 바깥으로 나가는 <link> 는
        # 하나도 없다 — 폰트까지 본문에 심었으므로 Artifact 가 무엇을 막든 상관없다.
        keep = []
        for tag in re.findall(r'<link[^>]+>|<title>.*?</title>|<style>.*?</style>', head, re.S):
            if tag.startswith("<title") or tag.startswith("<style"):
                keep.append(tag)
        # 지면 바깥 바탕은 뷰어 CSS 가 html,body 에 걸어 둔다. 껍데기를 벗기면서
        # 그 규칙이 바깥 body 에 닿도록 값을 그대로 옮겨 적는다. 덱과 문서가 다르므로
        # 색을 박지 않고 방금 인라인한 CSS 에서 읽는다.
        m = BODY_BG_RE.search(html)
        assert m, "뷰어 CSS 에서 html,body 배경을 찾지 못했다"
        keep.append(f"<style>\nbody {{ background:{m.group(1).strip()}; margin:0; }}\n</style>")
        html = "\n".join(keep) + "\n" + body
        default = "blue-report-doc-artifact.html" if is_doc else "blue-report-artifact.html"
        out = out_path or os.path.join(DIST, default)

    os.makedirs(os.path.dirname(os.path.abspath(out)) or ".", exist_ok=True)
    open(out, "w", encoding="utf-8").write(html)
    print(f"생성: {out}  ({len(html):,}자)")
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--artifact", action="store_true", help="Artifact 발행용 (껍데기 태그 제거)")
    ap.add_argument("--brand", help="brand.json 경로. 주면 회사 정보·로고까지 넣어 만든다")
    ap.add_argument("--deck", default="catalog",
                    help="덱 이름(" + " · ".join(DECKS) + ") · A4 문서 이름("
                         + " · ".join(DOCS) + ") · 또는 HTML 파일 경로")
    ap.add_argument("-o", "--out", help="출력 경로. 생략하면 dist/ 에 넣는다")
    a = ap.parse_args()
    build(a.artifact, a.brand, a.deck, a.out)
