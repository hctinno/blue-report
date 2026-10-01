#!/usr/bin/env python3
"""덱 HTML을 발표용 PDF로 내보낸다.

슬라이드 1장이 1페이지가 되고, 크기는 1920x1080px = 20in x 11.25in(96dpi)다.
텍스트는 이미지가 아니라 실제 글자로 남아 복사와 검색이 된다.

    python3 to_pdf.py deck.html                  # deck.pdf
    python3 to_pdf.py deck.html -o 보고서.pdf
    python3 to_pdf.py deck.html --notes          # 발표자 노트를 별도 페이지로 덧붙인다

Chromium이 필요하다. 이 환경에서는 Playwright가 설치한 것을 쓴다.
"""
import argparse
import os
import signal
import sys

# head 등으로 파이프가 닫혀도 역추적을 뱉지 않고 조용히 끝낸다
try:
    signal.signal(signal.SIGPIPE, signal.SIG_DFL)
except (AttributeError, ValueError):
    pass

def export(deck, out, with_notes=False, wait_ms=2500):
    # 없으면 여기서 알아서 받는다.
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from ensure_deps import need_browser
    chrome = need_browser()
    from playwright.sync_api import sync_playwright

    url = "file://" + os.path.abspath(deck) + "?all=1"
    with sync_playwright() as p:
        br = p.chromium.launch(executable_path=chrome)
        pg = br.new_page(viewport={"width": 1920, "height": 1080})
        pg.goto(url)
        pg.wait_for_timeout(wait_ms)          # 웹폰트 로드 대기

        info = pg.evaluate("""() => ({
            slides: document.querySelectorAll('.br-frame').length,
            title: (document.getElementById('stage')||{}).dataset?.deckTitle || '',
            notes: Array.from(document.querySelectorAll('.br-frame')).map(
                (f,i) => ({n:i+1, label:f.dataset.label||'', text:f.dataset.notes||''}))
        })""")

        if with_notes:
            _append_notes_page(pg, info)

        pg.pdf(path=out, width="20in", height="11.25in",
               print_background=True, prefer_css_page_size=True)
        br.close()

    size = os.path.getsize(out) / 1024
    print(f"슬라이드 {info['slides']}장 → {out}  ({size:,.0f}KB)")
    if info["title"]:
        print(f"문서명: {info['title']}")
    if with_notes:
        print("발표자 노트 페이지 1장 추가")
    return info


def _append_notes_page(pg, info):
    """발표자 노트를 모아 마지막에 한 페이지로 붙인다. 인쇄해서 손에 들기 위한 용도."""
    rows = "".join(
        f"<tr><td class='n'>{x['n']:02d}</td><td class='l'>{x['label']}</td>"
        f"<td class='t'>{x['text'] or '—'}</td></tr>"
        for x in info["notes"]
    )
    pg.evaluate("""(rows) => {
        const d = document.createElement('div');
        d.className = 'br-frame';
        d.style.cssText = 'background:#fff;padding:96px;box-sizing:border-box;'
            + 'width:1920px;height:1080px;font-family:var(--br-font-kr);';
        d.innerHTML = '<h2 style="font:900 54px/1.2 var(--br-font-kr);margin:0 0 40px;'
            + 'color:var(--br-text)">발표자 노트</h2>'
            + '<table style="width:100%;border-collapse:collapse;font:400 22px/1.5 '
            + 'var(--br-font-kr);color:var(--br-text-2)">' + rows + '</table>';
        d.querySelectorAll('td').forEach(td => {
            td.style.padding = '14px 16px';
            td.style.borderBottom = '1px solid #dbe3ec';
            td.style.verticalAlign = 'top';
        });
        d.querySelectorAll('td.n').forEach(td => {
            td.style.width = '70px'; td.style.fontWeight = '700'; td.style.color = '#0b2a6b';
        });
        d.querySelectorAll('td.l').forEach(td => {
            td.style.width = '260px'; td.style.fontWeight = '700'; td.style.color = '#10151c';
        });
        document.getElementById('stage').appendChild(d);
    }""", rows)


def main():
    ap = argparse.ArgumentParser(description="덱 HTML → 발표용 PDF")
    ap.add_argument("deck", help="덱 HTML 파일")
    ap.add_argument("-o", "--out", help="출력 PDF (기본: 입력과 같은 이름의 .pdf)")
    ap.add_argument("--notes", action="store_true", help="발표자 노트를 마지막 페이지로 덧붙인다")
    ap.add_argument("--wait", type=int, default=2500, help="폰트 로드 대기 ms (기본 2500)")
    a = ap.parse_args()
    out = a.out or os.path.splitext(a.deck)[0] + ".pdf"
    export(a.deck, out, a.notes, a.wait)


if __name__ == "__main__":
    main()
