#!/usr/bin/env python3
"""Render three branded design directions from the same representative content.

    python scripts/style_previews.py --content brief.json --out style-review

Creates two real PNGs per direction, an HTML comparison, comparison.png and a
manifest. No model, image-generation API or external presentation service is used.
"""
import argparse
import base64
import html
import json
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"
sys.path.insert(0, str(ROOT / "scripts"))
STYLES = (
    ("report", "01", "정돈된 보고형", "회의 보고 · 비교와 판단 근거", "밝은 지면 · 3구역 편집(번호 머리 · 구역별 근거) · 결론 띠"),
    ("explain", "02", "도식 중심 설명형", "교육 · 절차와 개념 설명", "노선 — 번호 역을 잇는 흐름 · 결과 역 강조 · 넉넉한 여백"),
    ("proposal", "03", "메시지 강조형", "제안 · 핵심 메시지 전달", "짙은 띠 지면 · 큰 메시지 · 쉐브론 단계 · 다음 행동 강조"),
)
EXAMPLE = {
    "title": "조사 결과를 실행으로 연결",
    "message": "자료의 핵심을 함께 이해하고 다음 행동을 결정",
    "points": [
        {"label": "핵심 메시지", "detail": "청중에게 전달할 결론 정리"},
        {"label": "판단 근거", "detail": "주장을 뒷받침하는 자료와 비교 기준"},
        {"label": "실행 제안", "detail": "회의 후 필요한 결정과 다음 행동"},
    ],
    "example": True,
}

# Scoped to preview content. The house chrome and tokens remain untouched.
# 세 방향 모두 회사 발표 덱의 디자인 언어(references/design-language.md)로 그린다 —
# 색은 --bl-pt-* 토큰, 01 = 3구역 편집 + 결론 띠, 02 = 노선, 03 = 짙은 띠 + 쉐브론.
CSS = """
.x-pv-k { color: var(--bl-pt-brand); font-size: 1.1rem; font-weight: 700; margin: 0; }
.x-pv-title { font-size: 4.4rem; line-height: 1.2; font-weight: 850; margin: 1rem 0; color: var(--bl-pt-ink); letter-spacing: -.02em; }
.x-pv-title em { font-style: normal; box-shadow: inset 0 -.38em 0 var(--bl-pt-hi); }
.x-pv-msg { font-size: 1.7rem; line-height: 1.6; margin: 0; color: var(--bl-pt-ink-3); }
.x-pv-cover { display: grid; grid-template-columns: 1.2fr .8fr; align-items: center; gap: 4rem; }
.x-pv-no { display: inline-grid; place-items: center; min-width: 2.4rem; padding: .1rem .45rem; border-radius: var(--bl-r-xs);
  background: var(--bl-pt-brand-2); color: var(--bl-pt-paper); font: 700 1.1rem/1.4 var(--bl-font-mono); }
.x-pv-list { display: grid; gap: 0; border-top: .2rem solid var(--bl-pt-ink); }
.x-pv-li { display: grid; grid-template-columns: auto 1fr; gap: .4rem 1rem; align-items: center; padding: 1.1rem 0; border-bottom: 1px solid var(--bl-pt-line); }
.x-pv-li b { font-size: 1.5rem; color: var(--bl-pt-ink); }
.x-pv-li p { grid-column: 2; margin: 0; font-size: 1.15rem; color: var(--bl-pt-ink-3); }
.x-pv-zones { display: grid; grid-template-columns: repeat(var(--n, 3), 1fr); border-top: .2rem solid var(--bl-pt-ink); }
.x-pv-zone { display: grid; gap: 1rem; align-content: start; padding: 1.6rem 2rem 1.6rem 0; }
.x-pv-zone + .x-pv-zone { padding-left: 2rem; border-left: 1px solid var(--bl-pt-line); }
.x-pv-zone h3 { display: flex; align-items: center; gap: .7rem; margin: 0; font-size: 1.8rem; color: var(--bl-pt-ink); }
.x-pv-zone p { margin: 0; font-size: 1.3rem; line-height: 1.6; color: var(--bl-pt-ink-3); }
.x-pv-band { margin-top: 2.2rem; padding: 1.2rem 2rem; border-radius: var(--bl-r-s); background: var(--bl-pt-tint);
  color: var(--bl-pt-brand-2); font-size: 1.6rem; font-weight: 800; text-align: center; }
.x-pv-band b { color: var(--bl-pt-orange-d); }
.x-pv-route { position: relative; display: grid; grid-template-columns: repeat(var(--n, 3), 1fr); margin-top: 2rem; }
.x-pv-route::before { content: ""; position: absolute; left: 0; right: 0; top: 1.6rem; height: .35rem; border-radius: var(--bl-r-pill); background: var(--bl-pt-brand-2); }
.x-pv-st { position: relative; display: grid; justify-items: center; gap: .8rem; text-align: center; padding: 0 1.2rem; }
.x-pv-dot { display: grid; place-items: center; width: 3.6rem; height: 3.6rem; border-radius: 50%; background: var(--bl-pt-paper);
  border: .35rem solid var(--bl-pt-brand-2); color: var(--bl-pt-brand-2); font: 800 1.3rem/1 var(--bl-font-mono); }
.x-pv-st:last-child .x-pv-dot { background: var(--bl-pt-orange); border-color: var(--bl-pt-orange); color: var(--bl-pt-paper); }
.x-pv-st b { font-size: 1.7rem; color: var(--bl-pt-ink); }
.x-pv-st:last-child b { color: var(--bl-pt-orange-d); }
.x-pv-st p { margin: 0; font-size: 1.25rem; line-height: 1.6; color: var(--bl-pt-ink-3); }
.x-pv-dark .x-pv-title { color: var(--br-on-dark); }
.x-pv-dark .x-pv-title em { box-shadow: none; color: var(--bl-pt-orange); }
.x-pv-dark .x-pv-msg { color: var(--br-on-dark-2); }
.x-pv-dark .x-pv-k { color: var(--br-accent-on-dark); }
.x-pv-chev { display: grid; grid-template-columns: repeat(var(--n, 3), 1fr); gap: .5rem; margin-top: 2rem; }
.x-pv-ch { padding: 1.4rem 2.6rem 1.4rem 2rem; background: var(--bl-pt-brand); color: var(--br-on-dark);
  clip-path: polygon(0 0, calc(100% - 1.4rem) 0, 100% 50%, calc(100% - 1.4rem) 100%, 0 100%, 1.4rem 50%); }
.x-pv-ch:first-child { clip-path: polygon(0 0, calc(100% - 1.4rem) 0, 100% 50%, calc(100% - 1.4rem) 100%, 0 100%); }
.x-pv-ch:last-child { background: var(--bl-pt-orange); }
.x-pv-ch b { display: block; font-size: 1.6rem; }
.x-pv-ch p { margin: .5rem 0 0; font-size: 1.15rem; line-height: 1.5; color: var(--br-on-dark); }
.x-pv-statement { font-size: 3.6rem; line-height: 1.35; font-weight: 850; margin: 0; color: var(--br-on-dark); }
.x-pv-statement em { font-style: normal; color: var(--bl-pt-orange); }
"""


def validate_content(data):
    if not isinstance(data, dict):
        raise ValueError("미리보기 내용은 JSON 객체여야 합니다.")
    for key in ("title", "message"):
        if not isinstance(data.get(key), str) or not data[key].strip():
            raise ValueError(f"{key}: 비어 있지 않은 문장이 필요합니다.")
    points = data.get("points")
    if not isinstance(points, list) or not 2 <= len(points) <= 3:
        raise ValueError("points: 같은 내용으로 비교할 대표 항목 2~3개가 필요합니다.")
    for point in points:
        if not isinstance(point, dict) or any(not isinstance(point.get(k), str) or not point[k].strip()
                                               for k in ("label", "detail")):
            raise ValueError("각 항목에는 label과 detail 문장이 필요합니다.")
    recommended = data.get("recommended_style")
    if recommended is not None and recommended not in {s[0] for s in STYLES}:
        raise ValueError("recommended_style: report, explain, proposal 중 하나입니다.")
    return data


def brand_path():
    candidates = (ROOT / "brand/hct/brand.json", ROOT.parents[2] / "brand/hct/brand.json")
    for path in candidates:
        if path.is_file():
            return path
    raise FileNotFoundError("HCT brand.json을 찾지 못했습니다. --brand로 지정하세요.")


def section(identifier, body, dark=False):
    tone = " bl-sl--dark" if dark else ""
    mark, watermark = ("light", "dark") if dark else ("dark", "light")
    return f'''<section class="bl-sl{tone}" id="{identifier}" data-notes="디자인 방향 비교용 장면이다.">
<header class="bl-hd"><span class="bl-code"><b>PREVIEW</b>디자인 선택</span><span class="bl-sp"></span>
<div class="br-mark" data-on="{mark}"><span class="br-wordmark">COMPANY NAME</span></div></header>
<div class="bl-bd bl-bd--center">{body}</div>
<footer class="bl-rf"><span class="bl-rf-name"></span><span class="bl-pg"></span></footer>
<div class="br-watermark" data-on="{watermark}"><span class="br-wordmark">COMPANY NAME</span></div>
</section>'''


def make_html(data, style):
    validate_content(data)
    if style not in {s[0] for s in STYLES}:
        raise ValueError("알 수 없는 디자인 방향")
    escape = html.escape
    title, message = escape(data["title"]), escape(data["message"])
    points = [(escape(p["label"]), escape(p["detail"])) for p in data["points"]]
    n = len(points)
    label = "스타일 비교용 예시 · 실제 업무 수치 미사용" if data.get("example") else "제공 자료를 활용한 디자인 비교"
    heads = "".join(f'<div class="x-pv-li"><span class="x-pv-no">{i:02}</span><b>{a}</b><p>{b}</p></div>'
                    for i, (a, b) in enumerate(points, 1))
    if style == "report":
        # 3구역 편집 + 결론 띠 — 굵은 윗선 · 번호 머리 · 구역별 근거
        cover = (f'<div class="x-pv-cover"><div><p class="x-pv-k">{label}</p><h1 class="x-pv-title">{title}</h1>'
                 f'<p class="x-pv-msg">{message}</p></div><div class="x-pv-list">{heads}</div></div>')
        zones = "".join(f'<div class="x-pv-zone"><h3><span class="x-pv-no">{i:02}</span>{a}</h3><p>{b}</p></div>'
                        for i, (a, b) in enumerate(points, 1))
        body = (f'<h2 class="bl-title">조사 내용 — <em>결론과 근거</em></h2><p class="bl-lede">{label}</p>'
                f'<div class="x-pv-zones" style="--n: {n}">{zones}</div><p class="x-pv-band">결론 → <b>{message}</b></p>')
        slides = section("preview-cover", cover) + section("preview-body", body)
    elif style == "explain":
        # 노선 — 번호 역을 잇는 굵은 선 · 마지막 역(결과)만 주황
        stations = "".join(f'<div class="x-pv-st"><span class="x-pv-dot">{i:02}</span><b>{a}</b><p>{b}</p></div>'
                           for i, (a, b) in enumerate(points, 1))
        cover = (f'<p class="x-pv-k">{label}</p><h1 class="x-pv-title">{title}</h1><p class="x-pv-msg">{message}</p>'
                 f'<div class="x-pv-route" style="--n: {n}">{stations}</div>')
        body = (f'<h2 class="bl-title">함께 이해할 내용 — <em>핵심 흐름</em></h2><p class="bl-lede">{message}</p>'
                f'<div class="x-pv-route" style="--n: {n}">{stations}</div>')
        slides = section("preview-cover", cover) + section("preview-body", body)
    else:
        # 짙은 띠 + 쉐브론 — 큰 메시지 · 마지막 단(다음 행동)만 주황
        chev = "".join(f'<div class="x-pv-ch"><b>{a}</b><p>{b}</p></div>' for a, b in points)
        cover = (f'<div class="x-pv-dark"><p class="x-pv-k">{label}</p><h1 class="x-pv-title">{title}</h1>'
                 f'<p class="x-pv-msg">{message}</p><div class="x-pv-chev" style="--n: {n}">{chev}</div></div>')
        body = (f'<h2 class="bl-title">전달할 메시지 — <em>다음 행동</em></h2><div class="x-pv-dark">'
                f'<p class="x-pv-statement">{message}</p><div class="x-pv-chev" style="--n: {n}">{chev}</div></div>')
        slides = section("preview-cover", cover, True) + section("preview-body", body, True)
    template = (ASSETS / "live-standard.html").read_text(encoding="utf-8")
    main = f'<main class="bl-deck" id="deck" data-deck-title="{title}" tabindex="0" aria-label="디자인 비교">{slides}</main>'
    result, count = re.subn(r'<main\b[^>]*>.*?</main>', lambda _: main, template, count=1, flags=re.S)
    if count != 1:
        raise ValueError("기준 덱의 main 구조가 변경됐습니다.")
    # The source deck's sample evidence is unrelated to this preview.
    result = re.sub(r'<script type="application/json" id="bl-evidence">.*?</script>', '', result, flags=re.S)
    result = re.sub(r'<title>.*?</title>', lambda _: f'<title>{title} · 디자인 비교</title>', result, count=1, flags=re.S)
    # 디자인 언어 토큰(--bl-pt-*)은 blue-pattern.css 에 있다 — 실제 덱과 같은 파일을 부른다.
    if 'blue-pattern.css' not in result:
        result = result.replace('</head>', '<link rel="stylesheet" href="blue-pattern.css">\n</head>', 1)
    return result.replace('</head>', '<style data-own>\n' + CSS + '\n</style>\n</head>', 1)


def make_gallery(data, items):
    css = (ASSETS / "blue-report.css").read_text(encoding="utf-8")
    font = ASSETS / "fonts/PretendardVariable.subset.woff2"
    uri = "data:font/woff2;base64," + base64.b64encode(font.read_bytes()).decode("ascii")
    css = css.replace("fonts/PretendardVariable.subset.woff2", uri)
    cards = []
    for item in items:
        badge = " · 추천" if data.get("recommended_style") == item["id"] else ""
        cards.append(f'''<article><h2>{item["number"]} {item["name"]}{badge}</h2><p>{item["description"]}</p>
<a href="{item["html"]}"><img src="{item["cover"]}" alt="{item["name"]} 표지"></a>
<a href="{item["html"]}"><img src="{item["body"]}" alt="{item["name"]} 본문"></a>
<p>{item["use_case"]}</p><a href="{item["html"]}">큰 화면으로 보기</a></article>''')
    title = html.escape(data["title"])
    return f'''<!doctype html><html lang="ko"><meta charset="utf-8"><title>디자인 방향 선택</title>
<meta name="viewport" content="width=device-width,initial-scale=1"><style>{css}
body{{margin:0;background:var(--br-page);color:var(--br-text);font-family:var(--br-font-kr)}}
main{{max-width:120rem;margin:auto;padding:2rem}}h1{{font-size:2rem;margin:0 0 .6rem}}
.intro{{color:var(--br-text-2);margin:0 0 1.6rem}}.choices{{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:1.2rem}}
article{{padding:1rem;background:var(--br-card);border-radius:.8rem}}h2{{font-size:1.35rem;margin:0}}
article p{{font-size:1rem;color:var(--br-text-2)}}img{{display:block;width:100%;height:auto;margin:.6rem 0}}
a{{color:var(--br-cobalt)}}@media(max-width:800px){{.choices{{grid-template-columns:1fr}}}}
</style><main><h1>같은 내용, 세 가지 디자인 방향</h1><p class="intro">{title} · 표지와 본문 실제 렌더링 · 선택할 번호를 채팅에서 전달</p>
<div class="choices">{''.join(cards)}</div><p class="intro">정지 이미지 비교용. 애니메이션과 출력 형식은 별도로 확인.</p></main></html>'''


def render_previews(data, out, brand=None):
    validate_content(data)
    out = Path(out).resolve()
    out.mkdir(parents=True, exist_ok=True)
    if (out / "styles.json").exists():
        raise FileExistsError("기존 선택 자료를 보존하려면 새 출력 폴더를 지정하세요.")
    items = []
    for style, number, name, use_case, description in STYLES:
        raw = out / (style + ".source.html")
        final = out / (style + ".html")
        raw.write_text(make_html(data, style), encoding="utf-8")
        command = [sys.executable, "-X", "utf8", str(ROOT / "scripts/apply_brand.py"), "--brand", str(brand or brand_path()),
                   "--deck", str(raw), "--title", data["title"], "--single-file", "-o", str(final)]
        result = subprocess.run(command, capture_output=True, text=True, encoding="utf-8", timeout=60)
        if result.returncode:
            raise RuntimeError((result.stderr or result.stdout or "브랜드 적용 실패").strip())
        items.append(dict(id=style, number=number, name=name, use_case=use_case, description=description,
                          html=final.name, cover=style + "-cover.png", body=style + "-body.png"))
    from ensure_deps import need_browser
    chrome = need_browser()
    from playwright.sync_api import sync_playwright
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(executable_path=chrome)
        try:
            for item in items:
                page = browser.new_page(viewport={"width": 1600, "height": 900}, reduced_motion="reduce")
                errors = []
                page.on("pageerror", lambda error: errors.append(str(error)))
                page.goto((out / item["html"]).as_uri())
                page.evaluate("document.fonts.ready")
                # Keep the working HTML's controls; hide only the floating overlay in PNGs.
                page.add_style_tag(content=".bl-hud { visibility: hidden !important; }")
                for kind in ("cover", "body"):
                    slide = page.locator("#preview-" + kind)
                    slide.scroll_into_view_if_needed()
                    overflow = slide.evaluate("""s => {const footer=s.querySelector('.bl-rf').getBoundingClientRect().top;
                      return [...s.querySelectorAll('.bl-bd *')].filter(e=>{
                        const r=e.getBoundingClientRect();return r.bottom>footer+2 || e.scrollWidth>e.clientWidth+2;
                      }).map(e=>e.className);} """)
                    if overflow:
                        raise ValueError(f"{item['id']} {kind}: 내용이 넘칩니다. 대표 문장을 줄이세요: {overflow[:3]}")
                    slide.screenshot(path=str(out / item[kind]), animations="disabled")
                if errors:
                    raise RuntimeError("발표 엔진 오류: " + errors[0])
                page.close()
            (out / "index.html").write_text(make_gallery(data, items), encoding="utf-8")
            gallery = browser.new_page(viewport={"width": 1920, "height": 1080})
            gallery.goto((out / "index.html").as_uri())
            gallery.evaluate("document.fonts.ready")
            gallery.screenshot(path=str(out / "comparison.png"), full_page=True)
            gallery.close()
        finally:
            browser.close()
    manifest = {"title": data["title"], "preview_format": "html", "selected_style": None,
                "recommended_style": data.get("recommended_style"), "styles": items}
    (out / "styles.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return manifest


def main():
    parser = argparse.ArgumentParser(description="같은 내용으로 회사 디자인 3안을 실제 PNG로 비교")
    parser.add_argument("--content", type=Path, help="title, message, points가 있는 UTF-8 JSON. 생략 시 표시된 예시 사용")
    parser.add_argument("--brand", type=Path)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    data = json.loads(args.content.read_text(encoding="utf-8-sig")) if args.content else EXAMPLE
    manifest = render_previews(data, args.out, args.brand)
    print(json.dumps({"out": str(args.out.resolve()), "styles": len(manifest["styles"]), "rendered_pngs": 7}, ensure_ascii=False))


if __name__ == "__main__":
    main()
