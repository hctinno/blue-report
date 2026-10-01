#!/usr/bin/env python3
"""블루 리포트 A4 문서 점검기 — 슬라이드가 아니라 문서용이다.

    python3 check_doc.py 회의록.html
    python3 check_doc.py 회의록.html --shots out/

검사 항목 (9)
  정적 — HTML 원문만 본다. Playwright 없이도 돈다.
    1. 문체 — 존댓말·평서형 종결 없이 명사형인가 (check_deck.py 규칙 재사용)
    2. 색 — 토큰 밖 raw hex 를 문서에 직접 쓰지 않았는가
    3. 쪽마다 머리말·꼬리말이 있는가
    4. 쪽번호를 손으로 적지 않았는가 (뷰어가 채운다)
    5. 쪽마다 브랜드 마크(.br-mark)가 있고 꼬리말에 회사명 자리가 있는가
  렌더 — 실제 브라우저 레이아웃. Playwright 가 필요하다.
    6. 지면이 정확히 794x1123 인가 (A4 210x297mm @96dpi)
    7. 본문이 머리말·꼬리말을 침범하지 않는가
       .bd-page 가 overflow:hidden 이라 scrollHeight 로는 잡히지 않는다.
       자손까지 포함한 실제 차지 범위로 형제 간 겹침을 본다.
    8. 10.5pt(14px) 미만 본문이 없는가 — 표 보조·각주(.bd-fs-small)는 예외
    9. 본문 글자가 지면 대비 4.5:1 이상인가 (인쇄물 기준)

종료 코드는 실패가 하나라도 있으면 1, 아니면 0 이다. 주의는 0 을 유지한다.
"""
import argparse
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from palette import contrast  # noqa: E402
from ensure_deps import need_browser  # noqa: E402
from check_deck import (  # noqa: E402
    Report, style_violations, ALLOWED_HEX, _blank, _rgb_to_hex,
    check_brand, check_style_applied, sentinels, STYLE_PROBE,
)

PAGE_W, PAGE_H = 794, 1123        # A4 세로 210x297mm @96dpi
# A4 가로. 분석 대시보드처럼 표·차트를 나란히 놓아야 하는 문서가 쓴다.
# 세로/가로를 지면 클래스(.bd-page--land)로 가른다 — 렌더된 크기로 짐작하지 않는다.
# 짐작하면 "가로가 아니라 그냥 넘친 세로 지면"을 통과시킨다.
PAGE_W_LAND, PAGE_H_LAND = 1123, 794
MIN_BODY_PX = 14        # 10.5pt @96dpi
MIN_TEXT_CONTRAST = 4.5  # 인쇄물 본문


def check_style(html, rep):
    """슬라이드와 같은 문체 규칙. 판정은 check_deck.style_violations 하나만 쓴다.

    예전에는 같은 순회를 여기에 한 벌 더 두고 정규식만 가져다 썼다. 그러면 규칙에
    예외가 붙을 때 한쪽만 따라가고, 같은 낱말을 덱과 문서가 다르게 판정한다.
    """
    bad = style_violations(html)
    if bad:
        rep.f(f"문체 위반 {len(bad)}건 (개조식·명사형 아님)")
        for b in bad[:8]:
            print(f"        {b}")
    else:
        rep.o("문체 — 존댓말·평서형 종결 없음")


def check_hex(html, rep):
    body = _blank(html, r"<style[^>]*>.*?</style>")
    body = _blank(body, r"<!--.*?-->")
    found = {}
    for m in re.finditer(r"#[0-9a-fA-F]{3,8}\b", body):
        h = m.group().lower()
        if h[:7] not in ALLOWED_HEX and h not in ALLOWED_HEX:
            found[h] = found.get(h, 0) + 1
    if found:
        rep.w("토큰 밖 raw hex: " + ", ".join(f"{k}×{v}" for k, v in found.items()))
    else:
        rep.o("색 — 토큰 밖 raw hex 없음")


def check_frame(html, rep):
    """쪽마다 머리말·꼬리말이 있고 쪽번호를 손으로 적지 않았는가."""
    pages = re.findall(r'<section[^>]*class="[^"]*bd-page[^"]*"[^>]*>(.*?)</section>', html, re.S)
    if not pages:
        rep.f("`.bd-page` 를 찾지 못했다 — A4 문서가 아니다")
        return
    miss = [f"{i+1}쪽" for i, p in enumerate(pages)
            if "bd-head" not in p or "bd-foot" not in p]
    if miss:
        rep.f(f"머리말·꼬리말 누락 {len(miss)}쪽 — " + ", ".join(miss[:6]))
    else:
        rep.o(f"머리말·꼬리말 — {len(pages)}쪽 모두 있다")

    # 브랜드 마크 — 슬라이드와 같은 .br-mark 자리표시자를 쪽 머리말에 둔다.
    no_mark = [f"{i+1}쪽" for i, p in enumerate(pages) if "br-mark" not in p]
    no_co = [f"{i+1}쪽" for i, p in enumerate(pages) if "bd-company" not in p]
    if no_mark:
        rep.f(f"브랜드 마크 없는 쪽 {len(no_mark)} — " + ", ".join(no_mark[:6]))
    elif no_co:
        rep.f(f"꼬리말에 회사명 자리 없는 쪽 {len(no_co)} — " + ", ".join(no_co[:6]))
    else:
        rep.o(f"브랜드 — {len(pages)}쪽 모두 마크와 회사명 자리가 있다")

    hand = []
    for i, p in enumerate(pages):
        m = re.search(r'<div class="bd-foot"[^>]*>(.+?)</div>', p, re.S)
        if m and re.search(r"\d\s*/\s*\d", m.group(1)):
            hand.append(f"{i+1}쪽")
    if hand:
        rep.f("쪽번호를 손으로 적었다 — 뷰어가 채운다: " + ", ".join(hand))
    else:
        rep.o("쪽번호 — 뷰어가 자동으로 채운다")


def check_render(path, rep, shots=None):
    chrome = need_browser()
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        br = p.chromium.launch(executable_path=chrome)
        pg = br.new_page(viewport={"width": 1000, "height": 1300})
        pg.goto("file://" + os.path.abspath(path))
        pg.wait_for_timeout(1800)
        need = sentinels(open(path, encoding="utf-8").read())
        check_style_applied(pg.evaluate(STYLE_PROBE, [t for _, t in need]),
                            need, rep)

        data = pg.evaluate(r"""() => {
          const band = el => {
            let r = el.getBoundingClientRect(), t = r.top, b = r.bottom;
            el.querySelectorAll('*').forEach(d => {
              const cs = getComputedStyle(d);
              if (cs.display === 'none' || cs.visibility === 'hidden' || cs.position === 'absolute') return;
              const dr = d.getBoundingClientRect();
              if (!dr.height && !dr.width) return;
              if (dr.top < t) t = dr.top;
              if (dr.bottom > b) b = dr.bottom;
            });
            return { top: t, bottom: b };
          };
          return [...document.querySelectorAll('.bd-page')].map((pgel, i) => {
            const kids = [...pgel.children].map(e => ({
              cls: (e.className || e.tagName).toString().slice(0, 24), ...band(e) }));
            const collide = [];
            for (let a = 0; a < kids.length - 1; a++)
              for (let b = a + 1; b < kids.length; b++) {
                const ov = Math.round(Math.min(kids[a].bottom, kids[b].bottom)
                                    - Math.max(kids[a].top, kids[b].top));
                if (ov > 2) collide.push({ a: kids[a].cls, b: kids[b].cls, ov });
              }
            const small = [];
            pgel.querySelectorAll('*').forEach(el => {
              const t = [...el.childNodes].filter(n => n.nodeType === 3 && n.textContent.trim())
                          .map(n => n.textContent.trim()).join(' ');
              if (!t) return;
              // 보조 요소는 예외. 자신뿐 아니라 조상에 붙은 클래스도 본다
              // (머리말·꼬리말 안의 span 은 클래스가 없다).
              if (el.closest('.bd-foot,.bd-head,.bd-chip,.bd-sign,.bd-table .num')) return;
              const fs = parseFloat(getComputedStyle(el).fontSize);
              if (fs < 14) small.push({ fs: Math.round(fs * 10) / 10, txt: t.slice(0, 30) });
            });
            const body = pgel.querySelector('.bd-body');
            const cs = getComputedStyle(pgel);
            return { i, w: pgel.scrollWidth, h: pgel.clientHeight,
                     land: pgel.classList.contains('bd-page--land'),
                     bg: cs.backgroundColor,
                     fg: body ? getComputedStyle(body).color : cs.color,
                     collide, small };
          });
        }""")

        size_bad, collide_all, small_all, contrast_bad = [], [], [], []
        for s in data:
            here = f"{s['i']+1}쪽"
            w, h = (PAGE_W_LAND, PAGE_H_LAND) if s.get("land") else (PAGE_W, PAGE_H)
            if s["w"] != w or s["h"] != h:
                size_bad.append(f"{here}: {s['w']}x{s['h']} (기대 {w}x{h} · "
                                f"{'가로' if s.get('land') else '세로'})")
            for c in s["collide"]:
                collide_all.append(f"{here}: {c['a']} 와 {c['b']} 가 세로로 {c['ov']}px 겹침")
            for t in s["small"]:
                small_all.append(f"{here}: {t['fs']}px — “{t['txt']}”")
            fg, bg = _rgb_to_hex(s["fg"]), _rgb_to_hex(s["bg"])
            if fg and bg:
                cr = contrast(fg, bg)
                if cr < MIN_TEXT_CONTRAST:
                    contrast_bad.append(f"{here}: {fg} vs {bg} = {cr:.2f}:1")

        for bad, ok_msg, fail_msg, hint in (
            (size_bad, ("지면 크기 — %d쪽 모두 규격대로 (세로 %dx%d · 가로 %dx%d)"
                        % (len(data), PAGE_W, PAGE_H, PAGE_W_LAND, PAGE_H_LAND)),
             "지면 크기 이탈", None),
            (collide_all, "본문 영역 — 머리말·꼬리말과 겹치지 않는다",
             "본문이 머리말·꼬리말을 침범", "→ 내용을 다음 쪽으로 넘기거나 여백을 줄인다"),
            (small_all, f"글자 크기 — {MIN_BODY_PX}px(10.5pt) 미만 본문 없음",
             f"{MIN_BODY_PX}px 미만 본문", None),
            (contrast_bad, f"본문 대비 — 지면 대비 {MIN_TEXT_CONTRAST}:1 이상",
             f"본문 대비 {MIN_TEXT_CONTRAST}:1 미달", None),
        ):
            if bad:
                rep.f(f"{fail_msg} {len(bad)}건")
                for x in bad[:8]:
                    print(f"        {x}")
                if hint:
                    print(f"        {hint}")
            else:
                rep.o(ok_msg)

        if shots:
            os.makedirs(shots, exist_ok=True)
            for i, el in enumerate(pg.query_selector_all(".bd-page"), 1):
                el.screenshot(path=os.path.join(shots, f"{i:02d}.png"))
            print(f"\n  스크린샷 {len(data)}쪽 저장: {shots}")
        br.close()


def main():
    ap = argparse.ArgumentParser(description="블루 리포트 A4 문서 점검")
    ap.add_argument("doc", help="점검할 HTML 파일")
    ap.add_argument("--shots", help="쪽별 PNG를 저장할 폴더")
    a = ap.parse_args()

    html = open(a.doc, encoding="utf-8").read()
    print(f"점검 대상: {a.doc}\n")
    rep = Report()
    check_style(html, rep)
    check_hex(html, rep)
    check_frame(html, rep)
    check_brand(html, rep, a.doc)
    check_render(a.doc, rep, a.shots)
    return rep.render()


if __name__ == "__main__":
    sys.exit(main())
