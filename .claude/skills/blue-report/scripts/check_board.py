#!/usr/bin/env python3
"""블루 리포트 웹 보드 점검기 — 슬라이드도 A4 도 아닌 화면용이다.

    python3 check_board.py 실행보드.html
    python3 check_board.py 실행보드.html --shots out/

check_deck.py 를 그대로 쓸 수 없다. 저쪽은 1920x1080 고정 지면과 24px 하한을
본다. 보드는 지면 크기가 없고 하한이 12.5px 다. 판정이 겹치는 것(문체·raw hex·
마크 대비)은 check_deck.py 에서 불러 쓴다 — 같은 낱말을 두 스크립트가 다르게
판정하는 일이 없도록 한 곳에만 둔다.

검사 항목 (11)
  정적 — HTML 원문만 본다. Playwright 없이도 돈다.
    1. 문체 — 존댓말·평서형 종결 없이 명사형인가 (check_deck.py 규칙 재사용)
    2. 색 — 토큰 밖 raw hex 를 본문에 직접 쓰지 않았는가
    3. 리터럴 px font-size 가 없는가 — 크기는 --bw-fs-* 로만 말한다
       사내 보드 두 벌의 글자 하한 위반 9건이 전부 리터럴이었다. 이 규칙 하나로 걸린다
    4. blue-report.css 와 blue-web.css 를 함께 불렀는가
    5. 가로 스크롤과 고정 머리행을 같이 쓰지 않았는가
       overflow-x:auto 는 그 상자를 스크롤포트로 만들어 sticky 머리행이 화면이
       아니라 그 상자에 붙는다. 상자는 세로로 안 움직이므로 머리행이 죽는다
  렌더 — 실제 브라우저 레이아웃. Playwright 가 필요하다.
    6. 12.5px 미만 글자가 없는가
    7. 데이터 마크가 실제 뒷배경 대비 2:1 이상인가 (채움 마크만 — 테두리 칩은 제외)
    8. sticky 요소의 조상에 overflow:hidden 이 없는가
       있으면 붙지 않는다. 육안으로는 스크롤해 봐야 알고, 대개 아무도 안 해 본다
    9. 1440px·400px 두 폭에서 문서가 가로로 넘치지 않는가
   10. 상태를 색으로만 말하지 않는가 — 상태 알약에 글자가 함께 있는가
   11. 문체 — **그려진 뒤의** 본문까지 개조식인가
       보드 넷 중 셋이 내용을 JS 데이터로 들고 그린다. 원문만 보는 1번은 그 글자를
       한 자도 못 본다 — <script> 안은 규칙상 걷어내기 때문이다. 렌더 뒤 DOM 을
       한 번 더 읽어 실제로 화면에 뜬 글자를 판정한다

종료 코드는 실패가 하나라도 있으면 1, 아니면 0 이다. 주의는 0 을 유지한다.
"""
import argparse
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from palette import contrast, MIN_DATA_CONTRAST  # noqa: E402
from ensure_deps import need_browser  # noqa: E402
from check_deck import (  # noqa: E402
    Report, style_violations, ALLOWED_HEX, _blank, _rgb_to_hex,
    check_brand, check_style_applied, sentinels, STYLE_PROBE,
)

MIN_FS = 12.5          # 웹 보드 글자 하한. 슬라이드 24px · A4 10.5pt 와 다르다
WIDTHS = [1440, 400]   # 데스크톱과 가장 좁은 실사용 폭


# ---------------------------------------------------------------- 정적 검사

def check_links(html, rep):
    """두 CSS 를 함께 불렀는가. blue-web.css 는 색을 선언하지 않는다."""
    has_base = re.search(r'href="[^"]*blue-report\.css"', html) or "--br-page:" in html
    has_web = re.search(r'href="[^"]*blue-web\.css"', html) or "--bw-fs-body:" in html
    if has_base and has_web:
        rep.o("CSS — blue-report.css 와 blue-web.css 를 함께 부른다")
    elif not has_web:
        rep.f("blue-web.css 를 부르지 않았다 — 웹 크기 토큰이 없다")
    else:
        rep.f("blue-report.css 를 부르지 않았다 — blue-web.css 는 색을 선언하지 않는다")


def check_literal_fs(html, rep):
    """리터럴 px font-size 금지. 크기는 --bw-fs-* 로만 말한다.

    사내 보드 두 벌에서 12.5px 하한을 깬 9건이 **전부** 리터럴이었다. 토큰을
    쓴 자리는 하나도 안 걸렸다. 그러니 리터럴을 막는 것이 하한을 지키는 가장
    싼 방법이다. 규격 CSS 자체는 대상이 아니므로 <style> 안은 보지 않는다."""
    body = _blank(html, r"<style[^>]*>.*?</style>")
    body = _blank(body, r"<script[^>]*>.*?</script>")
    bad = []
    for m in re.finditer(r"font-size\s*:\s*([\d.]+)px", body):
        bad.append(m.group(0))
    for m in re.finditer(r"font\s*:\s*[^;\"']*?\b([\d.]+)px", body):
        bad.append(m.group(0)[:40])
    if bad:
        rep.f(f"리터럴 px 글자 크기 {len(bad)}건 — --bw-fs-* 로 바꾼다")
        for b in bad[:8]:
            print(f"        {b}")
    else:
        rep.o("글자 크기 — 리터럴 px 없이 토큰만 쓴다")


def check_scroll_sticky_mix(html, rep):
    """가로 스크롤 상자 안에서 머리행을 고정하려 하지 않았는가.

    CSS 규칙상 overflow-x:auto 는 overflow-y 를 auto 로 계산시켜 그 상자가
    스크롤포트가 된다. 안쪽 sticky 는 화면이 아니라 그 상자에 붙고, 상자는
    세로로 스크롤하지 않으므로 머리행이 영영 따라오지 않는다. 사내 보드에서
    실제로 그렇게 죽어 있었다 — 150px 스크롤에 th 가 그대로 따라 올라갔다.

    blue-web.css 는 .bw-scroll .bw-table th { position:static } 으로 이미
    풀어 둔다. 여기서는 그 클래스를 지우고 직접 sticky 를 준 경우를 잡는다."""
    bad = []
    for m in re.finditer(r'<[^>]*class="[^"]*bw-scroll[^"]*"[^>]*>', html):
        tail = html[m.end():m.end() + 4000]
        if re.search(r"position\s*:\s*sticky", tail.split("</table>")[0]):
            bad.append(m.group(0)[:60])
    if bad:
        rep.f(f".bw-scroll 안에서 sticky 를 직접 준 곳 {len(bad)}건 — 둘은 같이 못 쓴다")
        for b in bad[:5]:
            print(f"        {b}…")
    else:
        rep.o("표 — 가로 스크롤과 고정 머리행을 섞지 않는다")


def check_raw_hex(html, rep):
    """본문의 토큰 밖 raw hex. 규격 CSS 사본 구간은 제외한다."""
    body = _blank(html, r"<style[^>]*>.*?</style>")
    found = {}
    for m in re.finditer(r"#[0-9a-fA-F]{3,6}\b", body):
        h = m.group(0).lower()
        if h not in ALLOWED_HEX:
            found[h] = found.get(h, 0) + 1
    if found:
        rep.f("토큰 밖 raw hex: " + ", ".join(f"{k}×{v}" for k, v in found.items()))
    else:
        rep.o("색 — 토큰 밖 raw hex 없음")


# ---------------------------------------------------------------- 렌더 검사

PROBE = r"""() => {
  const out = { small: [], marks: [], sticky: [], statusNoText: [] };

  // 12.5px 미만 글자. 자기 자신이 직접 가진 텍스트만 본다.
  document.querySelectorAll('body *').forEach(el => {
    const txt = Array.from(el.childNodes)
      .filter(n => n.nodeType === 3 && n.textContent.trim())
      .map(n => n.textContent.trim()).join(' ');
    if (!txt) return;
    const fs = parseFloat(getComputedStyle(el).fontSize);
    if (fs < 12.5 - 0.01) out.small.push({ fs: Math.round(fs * 10) / 10, txt: txt.slice(0, 32) });
  });

  // 데이터 마크. 채움으로 뜻을 나르는 것만 본다 — 테두리와 글자를 가진 칩은
  // 채움 대비가 낮아도 읽힌다. 규격이 일부러 그렇게 설계한 것이라 넣으면 오탐이다.
  const backdrop = el => {
    for (let p = el.parentElement; p; p = p.parentElement) {
      const c = getComputedStyle(p).backgroundColor;
      if (c && c !== 'transparent' && !/rgba\(.*,\s*0\)$/.test(c)) return c;
    }
    return getComputedStyle(document.body).backgroundColor;
  };
  // .bw-stage-s 는 채움이 있어도 글자를 언제나 함께 지므로 뺀다. .bw-wk 는 값이
  // 배정된 칸(data-s)만 마크이고, 비어 있는 칸은 채널이라 지면 대비가 낮아도 된다.
  const MARKS = '.bw-bar,.bw-dot,.bw-meter>span,.bw-wk[data-s],.bw-tl-bar,.bw-tl-dot,'
              + '.br-bar-h,.br-bar-v,circle';
  document.querySelectorAll(MARKS).forEach(el => {
    const cs = getComputedStyle(el);
    const c = el.tagName === 'circle' ? cs.stroke : cs.backgroundColor;
    if (!c || c === 'none' || c === 'rgba(0, 0, 0, 0)') return;
    out.marks.push({ c, bg: backdrop(el) });
  });

  // sticky 가 실제로 붙는가. 조상에 overflow:hidden 이 있으면 붙지 않는다.
  document.querySelectorAll('*').forEach(el => {
    if (getComputedStyle(el).position !== 'sticky') return;
    for (let p = el.parentElement; p && p !== document.documentElement; p = p.parentElement) {
      const o = getComputedStyle(p);
      if (o.overflow === 'hidden' || o.overflowY === 'hidden') {
        out.sticky.push({
          cls: (el.className || '').toString().slice(0, 30),
          by: (p.className || '').toString().slice(0, 30) || p.tagName.toLowerCase(),
        });
        break;
      }
    }
  });

  // 상태를 색으로만 말하지 않는가. 알약에 글자가 함께 있어야 한다.
  document.querySelectorAll('.bw-s,.bw-dd').forEach(el => {
    if (!el.textContent.trim()) {
      out.statusNoText.push((el.className || '').toString().slice(0, 30));
    }
  });

  return out;
}"""


def check_render(path, rep, shots=None, seen_style=()):
    need = None
    chrome = need_browser()
    if not chrome:
        rep.w("렌더 검사 생략 — 브라우저를 찾지 못했다")
        return
    from playwright.sync_api import sync_playwright

    url = "file://" + os.path.abspath(path)
    overflow, small, marks, sticky, no_text, drawn = [], [], [], [], [], ""
    with sync_playwright() as pw:
        br = pw.chromium.launch(executable_path=chrome)
        for w in WIDTHS:
            pg = br.new_page(viewport={"width": w, "height": 900}, reduced_motion="reduce")
            errs = []
            pg.on("pageerror", lambda e, box=errs: box.append(str(e).splitlines()[0]))
            pg.goto(url)
            pg.wait_for_timeout(1200)
            if need is None:
                need = sentinels(open(path, encoding="utf-8").read())
                check_style_applied(
                    pg.evaluate(STYLE_PROBE, [t for _, t in need]), need, rep)

            wide = pg.evaluate("() => ({ sw: document.documentElement.scrollWidth,"
                               " cw: document.documentElement.clientWidth })")
            if wide["sw"] > wide["cw"] + 1:
                overflow.append(f"{w}px 에서 문서가 {wide['sw'] - wide['cw']}px 가로로 넘친다")
            if errs:
                rep.f(f"{w}px — 콘솔 예외 {len(errs)}건: {errs[0]}")

            if w == WIDTHS[0]:                    # 상세 검사는 넓은 폭에서 한 번만
                d = pg.evaluate(PROBE)
                small, marks, sticky, no_text = (d["small"], d["marks"],
                                                 d["sticky"], d["statusNoText"])
                drawn = pg.evaluate("() => document.body.innerHTML")
                if shots:
                    os.makedirs(shots, exist_ok=True)
                    pg.screenshot(path=os.path.join(shots, "board.png"), full_page=True)
                    print(f"\n  전체 화면 저장: {shots}")
            pg.close()
        br.close()

    if overflow:
        rep.f(f"가로 넘침 {len(overflow)}건")
        for t in overflow:
            print(f"        {t}")
    else:
        rep.o(f"가로 넘침 — {WIDTHS[0]}px·{WIDTHS[1]}px 두 폭 모두 없음")

    if small:
        rep.f(f"{MIN_FS}px 미만 글자 {len(small)}건")
        for t in small[:8]:
            print(f"        {t['fs']}px — “{t['txt']}”")
    else:
        rep.o(f"글자 크기 — {MIN_FS}px 미만 없음")

    bad = []
    for m in marks:
        hexc, bgh = _rgb_to_hex(m["c"]), _rgb_to_hex(m["bg"])
        if not hexc or not bgh:
            continue
        cr = contrast(hexc, bgh)
        if cr < MIN_DATA_CONTRAST:
            bad.append(f"{hexc} vs {bgh} = {cr:.2f}:1")
    if bad:
        rep.f(f"데이터 마크 대비 2:1 미달 {len(bad)}건")
        for t in bad[:8]:
            print(f"        {t}")
    elif marks:
        rep.o(f"데이터 마크 — 채움 마크 {len(marks)}개 모두 뒷배경 대비 2:1 이상")
    else:
        rep.w("채움 데이터 마크 없음 — 막대를 쓰면 검산 대상이 생긴다")

    if sticky:
        rep.f(f"붙지 않는 sticky {len(sticky)}건 — 조상의 overflow:hidden 이 막는다")
        for t in sticky[:5]:
            print(f"        .{t['cls']} ← {t['by']}")
    else:
        rep.o("sticky — 조상에 overflow:hidden 없음")

    if no_text:
        rep.f(f"글자 없는 상태 알약 {len(no_text)}건 — 색만으로 상태를 말하지 않는다")
    else:
        rep.o("상태 — 색과 함께 글자가 온다")

    # JS 로 그린 내용은 원문 검사(1번)가 못 본다. 그려진 DOM 을 한 번 더 판정한다.
    # 행 번호는 원문과 DOM 이 다르므로 떼고 견준다 — 안 그러면 같은 문장을 두 번 센다.
    def _key(b):
        return b.split("행 ", 1)[-1]
    seen = {_key(b) for b in seen_style}
    late = [b for b in style_violations(drawn) if _key(b) not in seen]
    if late:
        rep.f(f"문체 위반 {len(late)}건 — JS 로 그린 본문 (개조식·명사형 아님)")
        for b in late[:8]:
            print(f"        {b}")
    else:
        rep.o("문체 — 그려진 본문까지 금지 어미 없음")


def main():
    ap = argparse.ArgumentParser(description="블루 리포트 웹 보드 점검기")
    ap.add_argument("path")
    ap.add_argument("--shots", help="전체 화면 PNG 를 저장할 폴더")
    a = ap.parse_args()

    if not os.path.isfile(a.path):
        raise SystemExit(f"파일이 없다: {a.path}")
    html = open(a.path, encoding="utf-8").read()
    print(f"점검 대상: {a.path}\n")

    rep = Report()
    bad = style_violations(html)
    if bad:
        rep.f(f"문체 위반 {len(bad)}건 (개조식·명사형 아님)")
        for b in bad[:8]:
            print(f"        {b}")
    else:
        rep.o("문체 — 금지 어미 없음")
    check_raw_hex(html, rep)
    check_literal_fs(html, rep)
    check_links(html, rep)
    check_scroll_sticky_mix(html, rep)
    check_brand(html, rep, a.path)
    check_render(a.path, rep, a.shots, seen_style=bad)

    sys.exit(rep.render())


if __name__ == "__main__":
    main()
