#!/usr/bin/env python3
"""블루 리포트 라이브 덱 점검기 — 고정 지면이 없는 발표 덱이다.

    python3 check_live.py live-brief.html
    python3 check_live.py live-brief.html --shots out/

check_deck.py 를 그대로 쓸 수 없다. 저쪽은 1920x1080 고정 지면과 24px 하한을
본다. 라이브 계통은 한 장이 100dvh 이고 치수가 전부 rem 이라 px 하한이라는
개념 자체가 없다 — 루트 글자 크기가 뷰포트를 따라 움직이기 때문이다.

판정이 겹치는 것(문체·raw hex·마크 대비)은 check_deck.py 에서 불러 쓴다.
같은 낱말을 두 스크립트가 다르게 판정하는 일이 없도록 한 곳에만 둔다.

검사 항목 (22)
  정적 — HTML 원문만 본다. Playwright 없이도 돈다.
    1. 문체 — 존댓말·평서형 종결 없이 명사형인가 (check_deck.py 규칙 재사용)
    2. 색 — 토큰 밖 raw hex 를 본문에 직접 쓰지 않았는가
    3. blue-report.css 와 blue-live.css 를 함께 불렀는가
    4. 리터럴 px 치수가 없는가 — 이 계통은 rem 으로만 말한다
       px 로 적으면 루트 글자 크기를 따라가지 않아 창이 작아질 때 그 값만 남는다.
       테두리 1px 와 미디어 질의 분기점은 예외다
    5. 장마다 data-notes 가 있는가 — 발표자 노트 없는 장은 대본 창이 빈다
    6~10. 지면 크롬 — 머리띠 · 꼬리띠 · 쪽번호 · 머리띠 브랜드 마크 · 워터마크가 장마다 있는가
   11. 마크 배경 짝 — data-on 이 마크가 앉는 면과 맞는가 (머리띠 마크는 지면과 반대)
   12. 브랜드 자리 — 산출물에 「COMPANY NAME」이 남지 않았는가 (assets/ 견본만 예외)
   13. 출처 칩 — .bl-ev 의 키가 #bl-evidence 근거에 있고 근거마다 제목·등급·출처가 있는가
  렌더 — 실제 브라우저 레이아웃. Playwright 가 필요하다.
   14. 스타일 — 계통 CSS 토큰이 렌더에서 살아 있는가
   15. 본문 폰트 — Pretendard FontFace 가 실제로 로드됐는가
   16. 지면 — 화면 좌우 끝까지 닿는가 (body 기본 여백 8px)
   17. 조작판 — 1600·760·400px 에서 꼬리띠 글자(문서명·쪽번호)를 덮지 않는가
   18. 절대 하한(0.78rem) 미만 글자가 없는가
   19. 본문 계열이 본문 하한(1.0rem) 이상인가 — 주석 계열만 그 아래를 허용한다
   20. 16:9 · 좁은 폭 · 휴대폰 폭 세 경우에서 가로로 넘치지 않는가
   21. 데이터 마크가 실제 뒷배경 대비 2:1 이상인가 (채움 마크만)
   22. 문체 — **그려진 뒤의** 본문까지 개조식인가

왜 rem 으로 판정하는가
  px 로 재면 창 크기에 따라 결과가 달라져 같은 파일이 통과했다 떨어졌다 한다.
  루트 글자 크기로 나눠 rem 으로 되돌린 뒤 판정하면 창과 무관하게 같은 답이다.

종료 코드는 실패가 하나라도 있으면 1, 아니면 0 이다.
"""
import argparse
import json
import os
import re
import sys
from html.parser import HTMLParser

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from palette import contrast, MIN_DATA_CONTRAST  # noqa: E402
from ensure_deps import need_browser  # noqa: E402
from check_deck import (  # noqa: E402
    Report, style_violations, ALLOWED_HEX, _blank, _rgb_to_hex,
    check_brand, check_style_applied, sentinels, STYLE_PROBE,
)

MIN_REM = 0.78     # 절대 하한. 무엇도 이보다 작게 쓰지 않는다
BODY_REM = 1.0     # 본문 하한. 주석 계열만 이 아래를 허용한다
# 주석·라벨 계열. 이 클래스를 단 요소는 BODY_REM 아래여도 된다.
NOTE_CLS = ("bl-note", "bl-src", "bl-chip", "bl-eyebrow", "bl-stat-t", "bl-rf",
            "bl-ord", "bl-code", "bl-pg", "bl-ev")
# 16:9 한 벌, 좁은 폭 한 벌, 휴대폰 폭 한 벌. 좁은 쪽 둘은 루트가 하한(10.5px)에
# 걸리는 구간이다 — 글자는 그대로고 가로 자리만 줄어 겹침·넘침이 여기서 난다.
VIEWS = [(1600, 900), (760, 900), (400, 800)]


# 지면이 화면 좌우 끝까지 닿는가. 브라우저 기본 body 여백(8px)이 살아 있으면
# 머리띠·꼬리띠가 끝에 닿지 않고 흰 틈이 테두리처럼 남는다 — 실제로 그랬다.
EDGE_PROBE = r"""() => {
  const s = document.querySelector('.bl-sl');
  if (!s) return {left: 0, right: 0, gap: 0};
  const r = s.getBoundingClientRect();
  const left = Math.round(r.left), right = Math.round(innerWidth - r.right);
  return {left, right, gap: Math.max(left, right)};
}"""


# 떠 있는 조작판이 꼬리띠 글자(문서명 · 쪽번호)를 덮는가. 조작판 단추를 넷에서
# 여덟로 늘리자 400px 에서 둘 다 덮었다 — 겹침은 넘침이 아니라 가로 넘침 검사가
# 못 잡는다. 글자의 실제 폭(Range)으로 잰다. 요소 상자는 띠 폭만큼 늘어날 수 있다.
HUD_PROBE = r"""() => {
  const hud = document.querySelector('.bl-hud'), s = document.querySelector('.bl-sl');
  if (!hud || !s || getComputedStyle(hud).display === 'none') return [];
  const a = hud.getBoundingClientRect(), hit = [];
  s.querySelectorAll('.bl-rf-name, .bl-pg').forEach(el => {
    const r = document.createRange(); r.selectNodeContents(el);
    const b = r.getBoundingClientRect();
    if (b.width && a.left < b.right && b.left < a.right && a.top < b.bottom && b.top < a.bottom)
      hit.push(el.classList.contains('bl-pg') ? '쪽번호' : '문서명');
  });
  return hit;
}"""


# ---------------------------------------------------------------- 정적 검사

def check_links(html, rep):
    """두 CSS 를 함께 불렀는가. blue-live.css 는 색을 선언하지 않는다."""
    has_base = re.search(r'href="[^"]*blue-report\.css"', html) or "--br-page:" in html
    has_live = re.search(r'href="[^"]*blue-live\.css"', html) or "--bl-fs-body:" in html
    if has_base and has_live:
        rep.o("CSS — blue-report.css 와 blue-live.css 를 함께 부른다")
    elif has_live:
        rep.f("blue-report.css 를 부르지 않았다 — 색 토큰이 전부 빈다")
    else:
        rep.f("blue-live.css 를 부르지 않았다 — 배율과 배치가 없다")


def check_raw_hex(html, rep):
    """본문에 토큰 밖 hex 를 직접 적지 않았는가. 규칙 문장과 CSS 는 뺀다."""
    body = _blank(html, r"<style[^>]*>.*?</style>")
    body = _blank(body, r"<!--.*?-->")
    found = {}
    for m in re.finditer(r"#[0-9a-fA-F]{3,8}\b", body):
        h = m.group().lower()
        if h not in ALLOWED_HEX:
            found[h] = found.get(h, 0) + 1
    if found:
        rep.w("토큰 밖 raw hex: " + ", ".join(f"{k}×{v}" for k, v in found.items()))
    else:
        rep.o("색 — 토큰 밖 raw hex 없음")


def check_literal_px(html, rep, path_hint=None):
    """라이브 계통 규칙에 리터럴 px 치수를 쓰지 않았는가.

    이 계통은 루트 글자 크기가 뷰포트를 따라 움직이고 안의 치수가 전부 rem 이다.
    px 를 하나 섞으면 그 값만 창 크기와 무관하게 고정돼, 작은 창에서 그 요소만
    상대적으로 커진다. 눈에 잘 안 띄고 실제로 깨지는 것은 좁은 화면이다.

    **라이브 규칙만 본다.** 한 파일로 묶으면 blue-report.css 가 통째로 인라인되는데
    거기 --br-fs-* 는 전부 px 다 — 그게 슬라이드 계통의 규격이라 정상이다. 선택자에
    bl- 가 들어간 규칙과 인라인 style= 만 세지 않으면 묶은 판에서만 129건이 뜬다.

    테두리 1px 는 실선 한 줄이라 배율을 따라갈 이유가 없다. 미디어 질의의
    분기점도 뷰포트 자체의 값이라 예외다."""
    css = "\n".join(re.findall(r"<style[^>]*>(.*?)</style>", html, re.S))
    # 원본 형태에서는 blue-live.css 가 외부 파일이라 <style> 이 비어 있다. 그대로
    # 두면 묶은 판에서만 검사가 돌고 원본은 무사통과한다 — 고치는 자리는 원본인데.
    # 링크를 따라가 디스크에서 읽어 함께 본다.
    for href in re.findall(r'<link[^>]+href="([^"]*blue-live\.css)"', html):
        side = os.path.join(os.path.dirname(os.path.abspath(path_hint or ".")), href)
        if os.path.isfile(side):
            css += "\n" + open(side, encoding="utf-8").read()
    css = re.sub(r"@media[^{]*\{", "{", css)          # 분기점은 뷰포트 값이라 뺀다

    def px_in(decls, where, out):
        for m in re.finditer(r"([a-z-]+)\s*:\s*([^;{}]*?-?[\d.]+px[^;{}]*)", decls):
            prop, val = m.group(1), m.group(2).strip()
            if "border" in prop or prop == "outline":
                if re.match(r"[\d.]*1px", val):
                    continue                            # 테두리 1px
            # 배율 엔진 자신은 px 로 적을 수밖에 없다. 루트 글자 크기를 rem 으로
            # 적으면 자기 자신을 참조해 순환한다.
            if prop == "font-size" and val.startswith("clamp("):
                continue
            # 흐림·그림자 반지름은 배치 치수가 아니다. 배율을 따라갈 이유가 없다.
            if prop in ("backdrop-filter", "filter", "box-shadow", "text-shadow"):
                continue
            out.append(f"{where} {prop}: {val[:44]}")

    bad = []
    # 선택자에 bl- 가 들어간 규칙만 본다 — 이 계통이 스스로 선언한 치수다.
    for m in re.finditer(r"([^{}]+)\{([^{}]*)\}", css):
        sel, decls = m.group(1), m.group(2)
        if "bl-" not in sel:
            continue
        px_in(decls, "<style>", bad)
    # 인라인 style= 은 **속성 하나씩** 본다. 여러 개를 이어 붙이면 앞 선언의 px 가
    # 뒤 선언과 한 덩어리로 잡혀 없는 위반이 생긴다 — 실제로 width:100% 가
    # 앞 태그의 height:40px 에 붙어 걸렸다.
    #
    # br-logo 는 예외다. 그 height 는 brand.json 의 logoHeight 를 apply_brand.py 가
    # 넣은 값이라 이 파일이 적은 치수가 아니다.
    for tag in re.findall(r"<[^>]*\sstyle=\"[^\"]*\"[^>]*>", html):
        if "br-logo" in tag:
            continue
        m = re.search(r'style="([^"]*)"', tag)
        if m:
            px_in(m.group(1), "style=", bad)

    if bad:
        rep.f(f"리터럴 px 치수 {len(bad)}건 — 이 계통은 rem 으로만 적는다")
        for b in bad[:6]:
            print(f"        {b}")
    else:
        rep.o("치수 — 리터럴 px 없이 rem 만 쓴다")


def _slices(html):
    """장 단위로 자른다. 정규식 하나로 장 안팎을 가릴 수 없어 시작 위치로 나눈다."""
    starts = [m for m in re.finditer(
        r"<section[^>]*\bclass=\"[^\"]*\bbl-sl\b[^\"]*\"[^>]*>", html)]
    out = []
    for k, m in enumerate(starts):
        end = starts[k + 1].start() if k + 1 < len(starts) else len(html)
        out.append((m.group(0), html[m.start():end]))
    return out


def check_chrome(html, rep):
    """지면 크롬이 장마다 붙어 있는가.

    이 검사가 이 계통의 핵심이다. 앞서 라이브 덱을 냈을 때 규격서에는 띠·로고·
    워터마크가 적혀 있었지만 강제하는 것이 없었다 — 그래서 다른 에이전트가 만든
    덱에 로고도 워터마크도 띠도 붙지 않았고, 「우리 양식으로 만들었다」면서
    회사 문서로 보이지 않는 결과가 나왔다. 규칙을 글로만 두면 지켜지지 않는다.

    브랜드 마크의 data-on 이 지면과 반대인 것도 여기서 잡는다. 마크가 앉는 곳은
    지면이 아니라 띠이고 띠 색은 지면과 반대이므로, 밝은 장의 머리띠 마크는
    data-on="dark" 다. 눈으로는 틀려도 알아채기 어렵다 — 로고가 배경에 묻힐 뿐
    사라지지는 않기 때문이다."""
    sl = _slices(html)
    if not sl:
        rep.f("bl-sl 장을 찾지 못했다")
        return

    miss_hd, miss_rf, miss_pg, miss_mark, miss_wm, wrong = [], [], [], [], [], []
    for n, (tag, body) in enumerate(sl, 1):
        dark = "bl-sl--dark" in tag
        if not re.search(r'class="[^"]*\bbl-hd\b', body):       miss_hd.append(n)
        if not re.search(r'class="[^"]*\bbl-rf\b', body):       miss_rf.append(n)
        if not re.search(r'class="[^"]*\bbl-pg\b', body):       miss_pg.append(n)

        # 머리띠 안의 마크 — 띠 구간만 잘라서 본다
        hd = re.search(r'<header[^>]*\bbl-hd\b.*?</header>', body, re.S)
        mark = re.search(r'<div class="br-mark" data-on="(dark|light)"', hd.group(0)) if hd else None
        if not mark:
            miss_mark.append(n)
        else:
            want = "light" if dark else "dark"     # 띠 색은 지면과 반대다
            if mark.group(1) != want:
                wrong.append(f"{n}장 머리띠 마크 data-on=\"{mark.group(1)}\" — "
                             f"{'어두운' if dark else '밝은'} 장이므로 \"{want}\"")

        wm = re.search(r'<div class="br-watermark" data-on="(dark|light)"', body)
        if not wm:
            miss_wm.append(n)
        else:
            want = "dark" if dark else "light"     # 워터마크는 지면 위에 앉는다
            if wm.group(1) != want:
                wrong.append(f"{n}장 워터마크 data-on=\"{wm.group(1)}\" — "
                             f"{'어두운' if dark else '밝은'} 장이므로 \"{want}\"")

    def verdict(label, missing, total=len(sl)):
        if missing:
            rep.f(f"{label} 없는 장 {len(missing)}건 / 전체 {total}장 — "
                  f"{', '.join(str(x) for x in missing[:8])}")
        else:
            rep.o(f"{label} — {total}장 모두 있다")

    verdict("머리띠 .bl-hd", miss_hd)
    verdict("꼬리띠 .bl-rf", miss_rf)
    verdict("쪽번호 .bl-pg", miss_pg)
    verdict("머리띠 브랜드 마크", miss_mark)
    verdict("워터마크", miss_wm)

    if wrong:
        rep.f(f"마크 배경 짝 어긋남 {len(wrong)}건 — 띠 색은 지면과 반대다")
        for w in wrong[:6]:
            print(f"        {w}")
    else:
        rep.o("마크 배경 짝 — 머리띠·워터마크 모두 앉는 면과 맞다")


EV_GRADES = {"A", "B", "C", "R"}   # 1차 공식 · 학술·전문 · 언론·2차 · 직접 조회·집계


class _Evidence(HTMLParser):
    """칩과 근거 JSON 을 브라우저가 읽는 대로 찾는다.

    정규식으로 원문을 훑으면 `--single-file` 산출물에서 틀린다. CSS·JS 가 문서
    안으로 들어오면서 CSS 주석의 사용 예(`<script id="bl-evidence">{…}`)가
    진짜 근거보다 앞에 놓이기 때문이다. 브라우저에게 `<style>`·`<script>` 속
    글자와 주석은 태그가 아니다 — HTMLParser 도 그렇게 읽는다."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.chips, self.json, self._in = [], None, False

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if "bl-ev" in (a.get("class") or "").split():
            self.chips.append(a.get("data-ev"))
        if tag == "script" and a.get("id") == "bl-evidence" and self.json is None:
            self._in, self.json = True, ""

    def handle_endtag(self, tag):
        if tag == "script":
            self._in = False

    def handle_data(self, data):
        if self._in:
            self.json += data


def check_evidence(html, rep):
    """출처 칩이 실제 근거를 가리키는가.

    칩(.bl-ev data-ev="E1")은 키만 들고 있고 내용은 문서 끝 #bl-evidence JSON
    한 벌에 있다. 키가 어긋나면 누른 사람에게 「근거 없음」이 뜬다 — 근거를
    보여 주려고 단 칩이 오히려 근거가 없다는 표시가 된다. 그래서 막는다.

    근거 항목마다 제목 · 등급 · 출처는 반드시 있어야 한다. 등급은 A·B·C·R
    네 가지다(JSON 의 grades 로 늘릴 수 있다). 칩이 하나도 없는 덱은 해당 없음."""
    p = _Evidence()
    p.feed(html)
    p.close()
    chips = p.chips
    if not chips:
        rep.o("출처 칩 — 없음 (해당 없음)")
        return
    if not all(chips):
        rep.f(f"출처 칩 {sum(1 for k in chips if not k)}개에 data-ev 키가 없다")
        return
    if p.json is None:
        rep.f(f"출처 칩 {len(chips)}개가 있는데 #bl-evidence 근거 JSON 이 없다")
        return
    try:
        data = json.loads(p.json)
    except ValueError as e:
        rep.f(f"근거 JSON 을 읽지 못했다 — {e}")
        return
    ev = data.get("ev", {})
    grades = EV_GRADES | set((data.get("grades") or {}).keys())
    missing = sorted(set(chips) - set(ev))
    bad = []
    for k, e in ev.items():
        lack = [f for f in ("title", "grade", "src") if not e.get(f)]
        if lack:
            bad.append(f"{k} — {'·'.join(lack)} 없음")
        elif e["grade"] not in grades:
            bad.append(f"{k} — 등급 {e['grade']} 은 정의되지 않음")
    if missing:
        rep.f(f"근거 없는 출처 칩 — {', '.join(missing)}")
    if bad:
        rep.f(f"근거 항목 불완전 {len(bad)}건")
        for b in bad[:6]:
            print(f"        {b}")
    if not missing and not bad:
        rep.o(f"출처 칩 — {len(chips)}개 모두 근거 {len(ev)}건에 이어짐 · 제목·등급·출처 완비")


def check_notes(html, rep):
    """장마다 발표자 노트가 있는가. 없으면 대본 창이 그 장에서 빈칸이 된다."""
    sl = re.findall(r"<section[^>]*class=\"[^\"]*\bbl-sl\b[^\"]*\"[^>]*>", html)
    miss = [s for s in sl if "data-notes" not in s]
    if not sl:
        rep.f("bl-sl 장을 찾지 못했다")
    elif miss:
        rep.f(f"발표자 노트 없는 장 {len(miss)}건 / 전체 {len(sl)}장")
    else:
        rep.o(f"발표자 노트 — {len(sl)}장 모두 있다")


# ---------------------------------------------------------------- 렌더 검사

def check_render(path, rep, shots=None, seen_style=()):
    chrome = need_browser()
    if not chrome:
        rep.w("렌더 검사 생략 — 브라우저를 찾지 못했다")
        return
    from playwright.sync_api import sync_playwright

    url = "file://" + os.path.abspath(path)
    overflow, tiny, body_small, marks, drawn = [], [], [], [], ""
    style, need = None, sentinels(open(path, encoding="utf-8").read())
    edge, hud_hits = None, []
    with sync_playwright() as pw:
        br = pw.chromium.launch(executable_path=chrome)
        for w, h in VIEWS:
            pg = br.new_page(viewport={"width": w, "height": h}, reduced_motion="reduce")
            pg.goto(url)
            pg.wait_for_timeout(1200)

            data = pg.evaluate(r"""(NOTE) => {
              const root = parseFloat(getComputedStyle(document.documentElement).fontSize);
              const out = {root, tiny: [], body: [], marks: [], over: 0, html: ''};
              out.over = Math.max(0, document.documentElement.scrollWidth
                                   - document.documentElement.clientWidth);
              out.html = document.body.innerText;

              // 글자 크기 — 직접 글자를 가진 요소만 본다. 부모까지 세면 같은
              // 문장을 여러 번 센다.
              document.querySelectorAll('.bl-sl *').forEach(el => {
                const txt = Array.from(el.childNodes)
                  .filter(n => n.nodeType === 3 && n.textContent.trim())
                  .map(n => n.textContent.trim()).join(' ');
                if (!txt) return;
                const cs = getComputedStyle(el);
                if (cs.display === 'none' || cs.visibility === 'hidden') return;
                const rem = parseFloat(cs.fontSize) / root;
                const isNote = NOTE.some(c => el.closest('.' + c));
                const rec = {rem: +rem.toFixed(3), cls: el.className || el.tagName,
                             txt: txt.slice(0, 40)};
                if (rem < 0.7795) out.tiny.push(rec);
                else if (!isNote && rem < 0.9995) out.body.push(rec);
              });

              // 채움 데이터 마크 — 실제로 깔린 배경과 견준다
              document.querySelectorAll('.bl-bar,.bl-stat-v').forEach(el => {
                const cs = getComputedStyle(el);
                const fill = el.classList.contains('bl-bar')
                  ? cs.backgroundColor : cs.color;
                if (!fill || fill === 'rgba(0, 0, 0, 0)') return;
                let p = el.parentElement, bg = null;
                while (p) {
                  const b = getComputedStyle(p).backgroundColor;
                  if (b && b !== 'rgba(0, 0, 0, 0)' && !/,\s*0\)$/.test(b)) { bg = b; break; }
                  p = p.parentElement;
                }
                out.marks.push({fill, bg: bg || 'rgb(255,255,255)',
                                cls: el.className});
              });
              return out;
            }""", list(NOTE_CLS))

            if w == VIEWS[0][0]:
                style = pg.evaluate(STYLE_PROBE, [t for _, t in need])
                edge = pg.evaluate(EDGE_PROBE)
            hud_hits += [f"{w}px {x}" for x in pg.evaluate(HUD_PROBE)]

            if data["over"] > 1:
                overflow.append(f"{w}px — {data['over']}px 넘침")
            tiny += [dict(r, view=w) for r in data["tiny"]]
            body_small += [dict(r, view=w) for r in data["body"]]
            if w == VIEWS[0][0]:
                marks = data["marks"]
                drawn = data["html"]
                if shots:
                    os.makedirs(shots, exist_ok=True)
                    pg.screenshot(path=os.path.join(shots, "live.png"), full_page=False)
            pg.close()
        br.close()

    if style is not None:
        check_style_applied(style, need, rep)

    if edge is not None:
        if edge["gap"] > 0:
            rep.f(f"지면이 화면 끝에 닿지 않는다 — 좌 {edge['left']}px · 우 {edge['right']}px 틈")
            print("        body 기본 여백(8px)이 살아 있으면 이렇게 된다. "
                  "blue-live.css 를 불렀는지 본다")
        else:
            rep.o("지면 — 화면 좌우 끝까지 닿는다")

    if hud_hits:
        rep.f("조작판이 꼬리띠 글자를 덮는다 — " + " · ".join(hud_hits))
    else:
        rep.o(f"조작판 — {'·'.join(str(w) for w, _ in VIEWS)}px 모두 꼬리띠 글자를 덮지 않는다")

    if tiny:
        rep.f(f"절대 하한 미만 {len(tiny)}건 — {MIN_REM}rem 보다 작다")
        for t in tiny[:6]:
            print(f"        {t['view']}px  {t['rem']}rem  .{t['cls']}  {t['txt']}")
    else:
        rep.o(f"글자 크기 — {MIN_REM}rem 미만 없음")

    if body_small:
        rep.f(f"본문 하한 미만 {len(body_small)}건 — {BODY_REM}rem 보다 작다")
        for t in body_small[:6]:
            print(f"        {t['view']}px  {t['rem']}rem  .{t['cls']}  {t['txt']}")
    else:
        rep.o(f"본문 글자 — {BODY_REM}rem 이상 (주석 계열 제외)")

    if overflow:
        rep.f("가로 넘침 — " + " · ".join(overflow))
    else:
        rep.o(f"가로 넘침 — {'·'.join(str(w) for w, _ in VIEWS)}px 모두 없음")

    weak = []
    for m in marks:
        try:
            c = contrast(_rgb_to_hex(m["fill"]), _rgb_to_hex(m["bg"]))
        except Exception:
            continue
        if c < MIN_DATA_CONTRAST:
            weak.append(f".{m['cls']} {c:.2f}:1")
    if weak:
        rep.f(f"데이터 마크 대비 미달 {len(weak)}건 — 뒷배경 대비 {MIN_DATA_CONTRAST}:1 미만")
        for w in weak[:5]:
            print(f"        {w}")
    elif marks:
        rep.o(f"데이터 마크 — {len(marks)}개 모두 뒷배경 대비 {MIN_DATA_CONTRAST}:1 이상")
    else:
        rep.w("채움 데이터 마크 없음 — 막대를 쓰면 검산 대상이 생긴다")

    # 원문 검사가 못 본 글자(JS 로 그린 것)를 한 번 더 본다.
    def _key(b):
        return b.split("행 ", 1)[-1]
    seen = {_key(b) for b in seen_style}
    late = [b for b in style_violations(drawn) if _key(b) not in seen]
    if late:
        rep.f(f"문체 위반 {len(late)}건 — 그려진 본문 (개조식·명사형 아님)")
        for b in late[:8]:
            print(f"        {b}")
    else:
        rep.o("문체 — 그려진 본문까지 금지 어미 없음")


def main():
    ap = argparse.ArgumentParser(description="블루 리포트 라이브 덱 점검기")
    ap.add_argument("path")
    ap.add_argument("--shots", help="화면 PNG 를 저장할 폴더")
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
    check_links(html, rep)
    check_literal_px(html, rep, a.path)
    check_notes(html, rep)
    check_chrome(html, rep)
    check_brand(html, rep, a.path)
    check_evidence(html, rep)
    check_render(a.path, rep, a.shots, seen_style=bad)

    sys.exit(rep.render())


if __name__ == "__main__":
    main()
