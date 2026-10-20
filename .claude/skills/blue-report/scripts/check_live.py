#!/usr/bin/env python3
"""블루 리포트 라이브 덱 점검기 — 고정 지면이 없는 발표 덱이다.

    python3 check_live.py live-standard.html
    python3 check_live.py live-standard.html --shots out/

check_deck.py 를 그대로 쓸 수 없다. 저쪽은 1920x1080 고정 지면과 24px 하한을
본다. 라이브 계통은 한 장이 100dvh 이고 치수가 전부 rem 이라 px 하한이라는
개념 자체가 없다 — 루트 글자 크기가 뷰포트를 따라 움직이기 때문이다.

판정이 겹치는 것(문체·raw hex·마크 대비)은 check_deck.py 에서 불러 쓴다.
같은 낱말을 두 스크립트가 다르게 판정하는 일이 없도록 한 곳에만 둔다.

검사 항목 (30)
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
   13. 출처 칩 — .bl-ev 의 키(쉼표로 여럿)가 #bl-evidence 근거에 있고 근거마다 제목·등급·출처가
       있는가. 캡처(imgs)·하이라이트 상자(hl)·원문(doc)이 가리키는 것도 실제로 있는가
  렌더 — 실제 브라우저 레이아웃. Playwright 가 필요하다.
   14. 스타일 — 계통 CSS 토큰이 렌더에서 살아 있는가
   15. 본문 폰트 — Pretendard FontFace 가 실제로 로드됐는가
   16. 지면 — 화면 좌우 끝까지 닿는가 (body 기본 여백 8px)
   17. 조작판 — 1600·760·400px 에서 장마다 꼬리띠 글자(문서명·쪽번호)를 덮지 않는가
   18. 절대 하한(0.78rem) 미만 글자가 없는가
   19. 본문 계열이 본문 하한(1.0rem) 이상인가 — 주석 계열만 그 아래를 허용한다
   20. 16:9 · 좁은 폭 · 휴대폰 폭 세 경우에서 가로로 넘치지 않는가
   21. 데이터 마크가 실제 뒷배경 대비 2:1 이상인가 (채움 마크만)
   22. 문체 — **그려진 뒤의** 본문까지 개조식인가
   23. 스크립트 — 뷰어 엔진이 떠 있고 부품이 예외 없이 시작하는가 (세 폭 모두)
       live-viewer.js 를 부르는 덱인데 window.blDeck 이 없으면 실패다. 연결형 산출물에서
       JS 를 옆에 복사하지 않으면 지면은 멀쩡히 그려지고 넘김·발표·근거가 전부 죽는다
  정적 — 블라인드 제작 시험(스킬 문서만 받은 에이전트)이 검사기 밖에서 찾은 결함들
   24. 단계 — 장마다 노트의 [클릭] 이 단계(data-f 값 가짓수)보다 적지 않은가.
       적으면 대본 창 배지가 단계와 어긋나 발표자가 지금 몇 번째인지 잃는다
   25. 클래스 — bl-·br- 클래스가 전부 CSS 나 뷰어에 있는가. 지어낸 클래스는 아무
       일도 하지 않는다 — 화면은 멀쩡해 보여 눈으로는 모른다
  렌더
   26. 보이지 않는 글자 — 글자색과 실제 뒷배경 대비가 1.25:1 미만인 글자가 없는가.
       카드형 수치 타일 안의 강조 칸이 흰 바탕 흰 글자로 사라진 일이 있었다
   27. 세로 넘침 — 16:9 화면에서 장마다 본문이 꼬리띠 위에서 끝나는가. 지면은 한 화면
       높이에 overflow:hidden 이라 넘친 줄은 잘려 사라진다. 900px 이하 읽기 폭(장이 내용만큼
       늘어난다)에서는 꼬리띠가 장 안에 있고 본문이 그 위에서 끝나는가
  정적 — 본문 맞춤 디자인 (1.47.0)
   28. 맞춤 CSS — 덱 안 <style> 로 본문을 새로 짜도 된다. 대신 고정 영역(머리띠 · 꼬리띠 ·
       쪽번호 · 로고 · 워터마크 · 진행선 · 제목 밴드 · 조작판)을 건드리지 않고, 장 id 나 자기
       클래스로 범위를 묶고, 색은 --br-* · --bl-* 토큰만, 치수는 rem 만, bl-·br- 이름은
       새로 짓지 않는가. 형태 · 움직임도 계통 눈금만 — 글꼴 var(--br-font-*), 모서리
       var(--bl-r-*) · 0 · 50%, 그림자 var(--bl-shadow*), 곡선 var(--bl-ease*) · linear,
       길이 0.15~1.2s(무한 반복 12s). 인라인 style= 도 형태 · 움직임을 본다 (1.48.0)
   29. 본문 표현 — 내용 장 중 글 · 표만 있는 장이 절반을 넘지 않는가 (주의만, 실패 아님)
   30. 움직임 절제 — 장마다 등장 계열 2종 · 반복 움직임 1종을 넘지 않는가 (주의만). DESIGN.md 「4」

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
            "bl-ord", "bl-code", "bl-pg", "bl-ev",
            # 라이브 부품(1.44.0) — 라벨 · 칩 · 축 · 칸 안 값처럼 본문이 아닌 글자만.
            # 본문을 담는 그릇(카드 · 행)은 넣지 않는다 — 넣으면 그 안 본문까지 하한이 풀린다.
            "bl-lbl", "bl-cap", "bl-mini", "bl-axis", "bl-dl", "bl-leg", "bl-num", "bl-pill",
            "bl-badge", "bl-delta", "bl-asof", "bl-pgref", "bl-stamp", "bl-conf", "bl-seg",
            "bl-fig-ab", "bl-replay", "bl-shot-open", "bl-route-st", "bl-sc-pick")
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
# 장마다 잰다 — 쪽번호 폭과 꼬리띠는 장마다 다를 수 있다. 조작판은 화면 아래에 붙어
# 있고 꼬리띠는 장 아래 끝에 있으니, 장의 아래 끝을 화면 아래 끝에 맞춘 자리로 옮겨
# 잰다(좁은 폭에서 화면보다 긴 장도 끝까지 내리면 그 자리에서 만난다).
HUD_PROBE = r"""() => {
  const hud = document.querySelector('.bl-hud');
  if (!hud || getComputedStyle(hud).display === 'none') return [];
  const a = hud.getBoundingClientRect(), hit = [];
  document.querySelectorAll('.bl-sl').forEach((s, i) => {
    const dy = innerHeight - s.getBoundingClientRect().bottom;
    s.querySelectorAll('.bl-rf-name, .bl-pg').forEach(el => {
      const r = document.createRange(); r.selectNodeContents(el);
      const b = r.getBoundingClientRect();
      // 말줄임으로 잘린 글자는 글자 폭(Range)이 상자 밖까지 잡힌다. 보이는 부분만 잰다
      let L = b.left, R = b.right;
      if (getComputedStyle(el).overflowX !== 'visible') {
        const e = el.getBoundingClientRect(); L = Math.max(L, e.left); R = Math.min(R, e.right);
      }
      const T = b.top + dy, B = b.bottom + dy;
      if (R - L > 0 && a.left < R && L < a.right && a.top < B && T < a.bottom)
        hit.push([el.classList.contains('bl-pg') ? '쪽번호' : '문서명', i + 1]);
    });
  });
  return hit;
}"""


# 글자색과 실제 뒷배경. 뒷배경은 위로 올라가며 처음 만나는 칠한 바탕이다. 도중에
# 그림 · 그라데이션 바탕을 만나면 판정하지 않는다(색 하나로 대비를 말할 수 없다).
# 1.25:1 미만이면 글자와 바탕이 사실상 같은 색이다 — 흐린 글자(고스트 번호처럼 일부러
# 옅게 깐 장식)를 잡는 검사가 아니라 사라진 글자를 잡는다.
INK_PROBE = r"""() => {
  const lum = c => { const v = c.map(x => { x /= 255; return x <= .03928 ? x / 12.92 : Math.pow((x + .055) / 1.055, 2.4); });
                     return .2126 * v[0] + .7152 * v[1] + .0722 * v[2]; };
  // color-mix() 로 만든 색은 color(srgb r g b / a) 로 나온다(0~1). 못 읽는 형식이면 판정하지 않는다
  const rgba = t => {
    let m = t.match(/rgba?\(([^)]+)\)/);
    if (m) { const p = m[1].split(/[,\s/]+/).filter(Boolean).map(Number); return [p[0], p[1], p[2], p.length > 3 ? p[3] : 1]; }
    m = t.match(/color\(srgb\s+([^)]+)\)/);
    if (m) { const p = m[1].split(/[\s/]+/).filter(Boolean).map(Number); return [p[0] * 255, p[1] * 255, p[2] * 255, p.length > 3 ? p[3] : 1]; }
    return null;
  };
  const out = [], INK_MIN = 1.25;
  document.querySelectorAll('.bl-sl *').forEach(el => {
    const txt = Array.from(el.childNodes).filter(n => n.nodeType === 3 && n.textContent.trim())
      .map(n => n.textContent.trim()).join(' ');
    if (!txt) return;
    const cs = getComputedStyle(el);
    if (cs.display === 'none' || cs.visibility !== 'visible' || parseFloat(cs.fontSize) < 2) return;
    if (el.closest('svg, .br-watermark')) return;   // 워터마크는 일부러 흐린 장식이다
    for (let p = el; p; p = p.parentElement) if (parseFloat(getComputedStyle(p).opacity) === 0) return;
    const fg = rgba(cs.color); if (!fg || fg[3] < .2) return;
    // 뒷배경은 글자가 실제로 그 위에 놓인 상자다. 막대 위로 띄운 값 라벨처럼 부모 상자
    // 밖에 놓인 글자는 부모 색이 아니라 그 바깥 바탕 위에 있다 — 가운데 점으로 가린다
    const er = el.getBoundingClientRect(), cx = er.left + er.width / 2, cy = er.top + er.height / 2;
    if (!er.width || !er.height) return;   // 조상이 숨긴 글자(고르지 않은 보기 · 탭)
    let bg = null;
    for (let p = el; p; p = p.parentElement) {
      const ps = getComputedStyle(p);
      const pr = p.getBoundingClientRect();
      const over = cx >= pr.left && cx <= pr.right && cy >= pr.top && cy <= pr.bottom;
      if (!over) continue;
      if (ps.backgroundImage && ps.backgroundImage !== 'none') return;
      const c = rgba(ps.backgroundColor);
      if (!c) return;
      if (c[3] >= .5) { bg = c; break; }
    }
    if (!bg) return;
    const a = lum(fg), b = lum(bg), r = (Math.max(a, b) + .05) / (Math.min(a, b) + .05);
    if (r < INK_MIN) {
      const s = el.closest('.bl-sl');
      out.push({sl: s && s.id || '', cls: (el.className && el.className.baseVal === undefined ? el.className : el.tagName) || el.tagName,
                txt: txt.slice(0, 30), r: +r.toFixed(2)});
    }
  });
  return out;
}"""

# 장마다 본문 요소가 머리띠 아래 · 꼬리띠 위 · 지면 안에 있는가. 세로 보기(펼침)라 단계가
# 전부 열린 최대 모습을 잰다. 고르지 않은 장면(.bl-scene)은 겹쳐 놓인 판이라 뺀다.
FIT_PROBE = r"""() => {
  const out = [];
  document.querySelectorAll('#deck > .bl-sl, main > .bl-sl').forEach((s, k) => {
    const r = s.getBoundingClientRect(), bd = s.querySelector('.bl-bd');
    const hd = s.querySelector('.bl-hd'), rf = s.querySelector('.bl-rf');
    if (!bd) return;
    const top = hd ? hd.getBoundingClientRect().bottom : r.top, bot = rf ? rf.getBoundingClientRect().top : r.bottom;
    let worst = 0, who = '';
    bd.querySelectorAll('*').forEach(el => {
      const cs = getComputedStyle(el);
      if (cs.display === 'none' || cs.visibility === 'hidden' || cs.position === 'fixed') return;
      if (el.closest('.bl-scene:not(.is-cur)')) return;
      const b = el.getBoundingClientRect();
      if (!b.width || !b.height) return;
      const o = Math.max(b.bottom - bot, top - b.top, b.right - r.right, r.left - b.left);
      if (o > worst) { worst = o; who = (el.className && el.className.baseVal === undefined ? el.className : el.tagName) || el.tagName; }
    });
    if (worst > 1.5) out.push({k: k + 1, sl: s.id || '', px: Math.round(worst), cls: String(who).slice(0, 40)});
  });
  return out;
}"""


# 좁은 폭(900px 이하)은 장이 내용만큼 늘어나는 읽기 폭이다. 그래도 꼬리띠는 장 안에 있어야
# 하고 본문은 꼬리띠 위에서 끝나야 한다 — 띠 높이가 장 높이의 % 라 장이 늘면 꼬리띠가
# 장 밖으로 밀려 다음 장에 가려진 일이 있었다. 가로는 보지 않는다(넓은 부품은 옆으로 스크롤한다).
NARROW_PROBE = r"""() => {
  const out = [];
  document.querySelectorAll('#deck > .bl-sl, main > .bl-sl').forEach((s, k) => {
    const R = s.getBoundingClientRect(), rf = s.querySelector('.bl-rf');
    if (!rf) return;
    const F = rf.getBoundingClientRect();
    let worst = F.bottom - R.bottom, who = 'bl-rf';
    s.querySelectorAll('.bl-bd *').forEach(el => {
      const cs = getComputedStyle(el);
      if (cs.display === 'none' || cs.visibility === 'hidden' || cs.position === 'fixed') return;
      if (el.closest('.bl-scene:not(.is-cur)')) return;
      const b = el.getBoundingClientRect();
      if (!b.width || !b.height) return;
      if (b.bottom - F.top > worst) { worst = b.bottom - F.top; who = (el.className && el.className.baseVal === undefined ? el.className : el.tagName) || el.tagName; }
    });
    if (worst > 1.5) out.push({k: k + 1, sl: s.id || '', px: Math.round(worst), cls: String(who).slice(0, 40)});
  });
  return out;
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
    css = "\n".join(b for b in re.findall(r"<style[^>]*>(.*?)</style>", html, re.S)
                    if any(sig in b for sig in _SYS_SIGS))       # 맞춤 블록은 28번이 본다
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
    # br-logo · br-wordmark 는 예외다. 로고 높이와 글자 로고 크기는 brand.json 을 읽어
    # apply_brand.py 가 넣은 값이라 이 파일이 적은 치수가 아니다. 글자 로고만 쓰는
    # 브랜드(로고 그림 없음)로 묶으면 장마다 실패가 났다.
    for tag in re.findall(r"<[^>]*\sstyle=\"[^\"]*\"[^>]*>", html):
        if "br-logo" in tag or "br-wordmark" in tag:
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


# ---------------------------------------------------------------- 본문 맞춤 CSS

# 계통 CSS 를 덱 안에 묶어 넣은 블록인지 — 토큰 정의가 있으면 계통 것이다.
_SYS_SIGS = ("--br-page:", "--bl-fs-body:")
# 어느 자리에 나와도 안 되는 고정 영역. 이 이름이 선택자에 있으면 고정 영역을 건드린다.
FIXED_ANY = ("bl-hd", "bl-rf", "bl-rf-name", "bl-pg", "bl-code", "br-mark", "br-watermark",
             "br-wordmark", "br-logo", "bl-hud", "bl-hud-sep", "bl-title",
             "#bl-prog", "#bl-jump", "#bl-notes", "#bl-help", "#bl-ev-panel", "#bl-inkbar",
             "#bl-blank", "bl-ink")
# 조상으로는 써도 되지만 대상(마지막 덩어리)이면 안 되는 것 — 지면 · 덱 자체다.
FIXED_SUBJECT = ("bl-sl", "bl-deck", "#deck")
_BARE_SUBJECT = re.compile(r"^(?:html|body|:root|main|section|header|footer|\*)$")
_COLOR_PROPS = re.compile(r"(?:^|-)(?:color|background|border|outline|fill|stroke|shadow|"
                          r"stop-color|flood-color|lighting-color|caret|accent|column-rule|"
                          r"text-decoration)")
_NAMED = ("white", "black", "red", "blue", "green", "gray", "grey", "orange", "yellow",
          "purple", "pink", "navy", "silver", "teal", "aqua", "cyan", "magenta", "lime",
          "maroon", "olive", "brown", "gold", "violet", "indigo", "crimson", "coral",
          "salmon", "beige", "ivory", "khaki", "tomato", "orchid", "skyblue", "steelblue",
          "royalblue", "lightgray", "darkgray", "whitesmoke", "gainsboro")
_RAW_COLOR = re.compile(r"#[0-9a-fA-F]{3,8}\b|\b(?:rgba?|hsla?|hwb|lab|lch|oklab|oklch|color)\(|"
                        r"\b(?:" + "|".join(_NAMED) + r")\b", re.I)
_SHADOW_OK = re.compile(r"rgba?\(\s*(?:0\s*,\s*0\s*,\s*0|255\s*,\s*255\s*,\s*255|0 0 0|255 255 255)"
                        r"\s*[,/][^)]*\)", re.I)


def own_css_blocks(html):
    """덱이 스스로 적은 <style> 블록. 계통 CSS 를 묶어 넣은 블록은 뺀다."""
    out = []
    for m in re.finditer(r"<style[^>]*>(.*?)</style>", html, re.S):
        body = m.group(1)
        if any(sig in body for sig in _SYS_SIGS):
            continue
        out.append(body)
    return out


def _rules(css):
    """(선택자, 선언) 목록. @media · @supports 는 벗기고 @keyframes 속은 따로 낸다."""
    css = re.sub(r"/\*.*?\*/", " ", css, flags=re.S)
    frames = []

    def take_frames(m):
        frames.append(m.group(0))
        return " "
    # @keyframes 이름 { from {…} to {…} } — 중괄호 두 겹을 통째로 떼어 낸다
    css = re.sub(r"@(?:-webkit-)?keyframes\s+[\w-]+\s*\{(?:[^{}]*\{[^{}]*\})*[^{}]*\}", take_frames, css)
    css = re.sub(r"@(?:media|supports|container|layer)[^{]*\{", "", css)
    rules = [(m.group(1).strip(), m.group(2)) for m in re.finditer(r"([^{}]+)\{([^{}]*)\}", css)]
    kf = []
    for f in frames:
        kf += [(m.group(1).strip(), m.group(2)) for m in re.finditer(r"([^{}]+)\{([^{}]*)\}",
                                                                       f.split("{", 1)[1])]
    return rules, kf, len(frames)


def _tokens(sel):
    return set("." + c for c in re.findall(r"\.([\w-]+)", sel)) | set(re.findall(r"#[\w-]+", sel))


def _decls(text):
    for d in text.split(";"):
        if ":" in d:
            k, v = d.split(":", 1)
            yield k.strip().lower(), v.strip()


def own_css_problems(css_list, known, slide_ids=()):
    """맞춤 CSS 를 판정해 (실패 목록, 주의 목록) 을 돌려준다.

    known 은 계통 클래스 이름, slide_ids 는 덱의 장 id(#…)다."""
    slide_ids = {"#" + i.lstrip("#") for i in slide_ids}
    bad, warn = [], []
    n_frames, has_reduce = 0, False
    for css in css_list:
        if "prefers-reduced-motion" in css or "html.bl-anim" in css:
            has_reduce = True
        if re.search(r"@font-face|@import", css):
            bad.append("@font-face · @import — 폰트 · 외부 CSS 를 덧붙이지 않는다")
        rules, kf, nf = _rules(css)
        n_frames += nf
        for sel_list, decls in rules:
            for sel in (x.strip() for x in sel_list.split(",")):
                if not sel:
                    continue
                toks = _tokens(sel)
                hit = [t for t in FIXED_ANY if ("." + t if not t.startswith("#") else t) in toks]
                if hit:
                    bad.append(f"고정 영역을 건드린다 — {sel[:60]}  ({' '.join(hit)})")
                    continue
                subject = re.split(r"\s*[>+~]\s*|\s+", sel.strip())[-1]
                bare = re.sub(r"::?[\w-]+(\([^)]*\))?", "", subject)
                stoks = _tokens(bare)
                frame = any(("." + t if not t.startswith("#") else t) in stoks for t in FIXED_SUBJECT)
                # 장 id 만으로 된 대상(#s9, #s9.in)은 그 장의 지면 자체다. 자기 변수(--x-*)만
                # 정의하는 것은 괜찮다 — 본문 안으로 값을 내려 주는 자리다.
                slide = stoks and all(t in slide_ids or t in (".in",) or t.startswith(".is-")
                                      for t in stoks) and any(t in slide_ids for t in stoks)
                only_vars = all(k.startswith("--") for k, _ in _decls(decls))
                if _BARE_SUBJECT.match(bare) or frame or (slide and not only_vars):
                    bad.append(f"지면 · 덱 전체를 대상으로 삼는다 — {sel[:60]}")
                    continue
                scoped = any(t.startswith("#") or not t[1:].startswith(("bl-", "br-")) for t in toks)
                if not scoped:
                    bad.append(f"범위가 없다 — 장 id(#…) 나 자기 클래스로 묶는다: {sel[:60]}")
                for c in re.findall(r"\.(b[lr]-[\w-]+)", sel):
                    if c not in known:
                        bad.append(f"bl-·br- 이름을 새로 지었다 — .{c} (자기 클래스는 다른 접두어)")
            for k, v in _decls(decls):
                if re.match(r"--b[lr]-", k):
                    bad.append(f"계통 토큰을 덮어쓴다 — {k}")
                _color_bad(k, v, sel_list, bad)
                _px_bad(k, v, sel_list, bad)
                _form_bad(k, v, sel_list, bad)
        for sel, decls in kf:
            for k, v in _decls(decls):
                _color_bad(k, v, "@keyframes " + sel, bad)
                _px_bad(k, v, "@keyframes " + sel, bad)
                _form_bad(k, v, "@keyframes " + sel, bad)
    if n_frames and not has_reduce:
        warn.append(f"맞춤 @keyframes {n_frames}개에 움직임 줄이기 분기가 없다 — "
                    "@media (prefers-reduced-motion: no-preference) 안에 두거나 html.bl-anim 에 묶는다")
    # 같은 위반이 여러 번 나오면 한 번만 보인다
    return list(dict.fromkeys(bad)), warn


# 형태 · 움직임 토큰 (1.48.0). 색만 토큰이면 장마다 모서리 · 그림자 · 속도가 제각각이라
# 한 덱이 여러 덱처럼 보인다. 계통 CSS 가 실제로 쓰는 눈금만 허용한다.
_FONT_OK = re.compile(r"^(?:var\(--(?:br-font-(?:kr|num|label)|bl-font-mono)\)|inherit)$")
_RADIUS_OK = re.compile(r"^(?:0|50%|var\(--bl-r-(?:xs|s|m|l|pill)\)|inherit)$")
_SHADOW_TOKEN = re.compile(r"^(?:none|var\(--bl-shadow(?:-up)?\)|inherit|"
                           r"inset 0 0 0 [\d.]+rem var\(--b[rl]-[\w-]+\))$")
_EASE_WORD = re.compile(r"\b(?:ease(?:-in|-out|-in-out)?|step-start|step-end)\b|cubic-bezier\(|steps\(")
DUR_MIN, DUR_MAX, LOOP_MAX = 0.15, 1.2, 12.0     # 초. 무한 반복(흐르는 점 · 도는 표식)만 길게


def _secs(t):
    return float(t[:-2]) / 1000 if t.endswith("ms") else float(t[:-1])


def _form_bad(k, v, where, bad):
    """글꼴 · 모서리 · 그림자 · 곡선 · 길이를 계통 눈금에 묶는다."""
    v = v.replace("!important", "").strip()
    w = where[:40]
    if k == "font-family" and not _FONT_OK.match(v):
        bad.append(f"글꼴을 직접 정했다 — {w} {{ {k}: {v[:40]} }} · var(--br-font-kr) 등 토큰만")
    elif k == "font" and v != "inherit" and not re.search(r"var\(--(?:br-font-|bl-font-)", v):
        bad.append(f"글꼴을 직접 정했다 — {w} {{ font: {v[:40]} }} · 글꼴 자리에 var(--br-font-*)")
    elif re.fullmatch(r"border(?:-[a-z]+)*-radius", k):
        parts = re.split(r"\s+(?![^()]*\))|\s*/\s*", v)
        if not all(_RADIUS_OK.match(x) for x in parts if x):
            bad.append(f"모서리를 직접 정했다 — {w} {{ {k}: {v[:40]} }} · var(--bl-r-xs|s|m|l|pill) · 0 · 50%")
    elif k == "box-shadow":
        if not all(_SHADOW_TOKEN.match(x.strip()) for x in re.split(r",(?![^()]*\))", v)):
            bad.append(f"그림자를 직접 정했다 — {w} {{ {k}: {v[:40]} }} · var(--bl-shadow) · var(--bl-shadow-up) · none")
    elif k == "text-shadow" and v not in ("none", "inherit"):
        bad.append(f"글자 그림자 — {w} {{ {k}: {v[:40]} }} · 쓰지 않는다")
    elif k in ("animation", "transition") or k.endswith(("-timing-function", "-duration")):
        if v in ("none", "inherit", "initial", "unset"):
            return
        for item in re.split(r",(?![^()]*\))", v):
            item = item.strip()
            ease_free = re.sub(r"var\([^()]*\)", " ", item)
            if _EASE_WORD.search(ease_free):
                bad.append(f"움직임 곡선을 직접 정했다 — {w} {{ {k}: {item[:40]} }} · var(--bl-ease|ease-out|ease-pop) · linear")
            elif k in ("animation", "transition") and "var(--bl-ease" not in item \
                    and not re.search(r"\blinear\b", item):
                bad.append(f"움직임 곡선이 없다(기본 ease 가 걸린다) — {w} {{ {k}: {item[:40]} }} · var(--bl-ease*) 를 적는다")
            if k.endswith("-timing-function"):
                continue
            times = re.findall(r"(?<![\w.-])(\d*\.?\d+m?s)\b", ease_free)
            if not times:
                continue
            d = _secs(times[0])                         # 첫 시간 값이 길이, 둘째는 지연
            top = LOOP_MAX if "infinite" in item else DUR_MAX
            if d and not (DUR_MIN <= d <= top):
                bad.append(f"움직임 길이 {times[0]} — {w} · {DUR_MIN}~{DUR_MAX}s"
                           + (f" (무한 반복은 {LOOP_MAX:g}s 까지)" if top == DUR_MAX else ""))


def _color_bad(k, v, where, bad):
    if not (_COLOR_PROPS.search(k) or k.startswith("--")):
        return
    val = re.sub(r"var\([^()]*(?:\([^()]*\)[^()]*)*\)", " ", v)   # 토큰 참조는 지운다
    val = re.sub(r"url\([^)]*\)", " ", val)
    if "shadow" in k or k in ("filter",):
        val = _SHADOW_OK.sub(" ", val)
    m = _RAW_COLOR.search(val)
    if m:
        bad.append(f"색을 직접 적었다 — {where[:40]} {{ {k}: {v[:40]} }} · --br-* 토큰을 쓴다")


def _px_bad(k, v, where, bad):
    if not re.search(r"-?[\d.]+px\b", v):
        return
    if ("border" in k or k == "outline") and re.match(r"[\d.]*1px", v):
        return
    if k in ("backdrop-filter", "filter", "box-shadow", "text-shadow"):
        return
    bad.append(f"px 치수 — {where[:40]} {{ {k}: {v[:40]} }} · rem 으로 적는다")


def check_own_css(html, rep, path):
    """본문 맞춤 CSS — 새로 짜도 되지만 고정 영역 · 색 · 치수 · 이름 · 형태 · 움직임 규칙 안에서.

    인라인 style= 도 형태 · 움직임 규칙(글꼴 · 모서리 · 그림자 · 곡선 · 길이)을 본다 —
    <style> 을 피해 속성에 적으면 같은 결과가 나기 때문이다."""
    own = own_css_blocks(html)
    inline_bad = []
    body = _blank(html, r"<style[^>]*>.*?</style>")
    body = _blank(body, r"<script[^>]*>.*?</script>")
    for tag in re.findall(r"<[^>]*\sstyle=\"[^\"]*\"[^>]*>", body):
        if "br-logo" in tag or "br-wordmark" in tag:
            continue                                   # apply_brand.py 가 넣는 로고 치수
        for k, v in _decls(re.search(r'style="([^"]*)"', tag).group(1)):
            _form_bad(k, v, "style=", inline_bad)
    if not own and not inline_bad:
        rep.o("맞춤 CSS — 없음 (계통 부품만 사용)")
        return
    known = _system_classes(html, path)
    ids = re.findall(r'<section[^>]*\bbl-sl\b[^>]*\bid="([^"]+)"|<section[^>]*\bid="([^"]+)"[^>]*\bbl-sl\b', html)
    bad, warn = own_css_problems(own, known, [a or b for a, b in ids]) if own else ([], [])
    bad = list(dict.fromkeys(bad + inline_bad))
    for w in warn:
        rep.w(w)
    if bad:
        rep.f(f"맞춤 CSS 위반 {len(bad)}건 — 본문은 새로 짜도 되지만 고정 영역 · 토큰 · rem · 형태 · 움직임 규칙은 지킨다")
        for b in bad[:10]:
            print(f"        {b}")
    else:
        n = sum(len(_rules(c)[0]) for c in own)
        rep.o(f"맞춤 CSS — 블록 {len(own)}개 · 규칙 {n}개, 고정 영역 · 색 · 치수 · 이름 · 형태 · 움직임 규칙 지킴")


def _system_classes(html, path):
    """계통 CSS(덱이 부르는 파일 + 묶어 넣은 블록)와 뷰어 JS 가 아는 bl-·br- 이름."""
    p = _Slides()
    p.feed(html)
    p.close()
    css = "\n".join(b for b in re.findall(r"<style[^>]*>(.*?)</style>", html, re.S)
                    if any(sig in b for sig in _SYS_SIGS))
    js = "\n".join(re.findall(r"<script(?![^>]*\btype=\"application/json\")(?![^>]*\btype=\"text/plain\")[^>]*>(.*?)</script>",
                              html, re.S))
    for kind, ref in p.links:
        text = _read_near(path, ref)
        if kind == "css":
            css += "\n" + text
        else:
            js += "\n" + text
    return set(re.findall(r"\.(b[lr]-[\w-]+)", css)) | set(re.findall(r"\b(b[lr]-[\w-]+)", js))


# 그림 · 도식 부품 — 이것이 하나라도 있으면 글 · 표만 있는 장이 아니다.
VISUAL_CLS = ("bl-tc", "bl-lc", "bl-hc", "bl-meter", "bl-lanes", "bl-span", "bl-dots", "bl-gantt",
              "bl-org", "bl-matrix", "bl-orgtree", "bl-svgbox", "bl-raci", "bl-road", "bl-kpis",
              "bl-donut-box", "bl-bar", "bl-stack", "bl-wf", "bl-sc", "bl-rack", "bl-checks",
              "bl-waffle", "bl-pickset", "bl-heat", "bl-mock", "bl-stair", "bl-chev", "bl-hero",
              "bl-vs", "bl-simq", "bl-decide", "bl-road2", "bl-pipe", "bl-flowbox", "bl-fl-zone",
              "bl-baton", "bl-ghost", "bl-tabset", "bl-scenebox", "bl-flow", "bl-stat",
              "bl-gauge", "bl-prog", "bl-focusset", "bl-agenda")
# 표현을 따질 장이 아닌 것 — 표지 · 간지 · 마무리 · 부록 · 질문
_FRAME_CLS = ("bl-sl--cover", "bl-sl--chapter", "bl-sl--apxdiv", "bl-fin", "bl-qa", "bl-chapter",
              "bl-apxdiv")


# 등장(한 번) · 반복(계속) 계열. 반복은 읽는 동안 눈을 끌어 장마다 한 종만 둔다.
LOOP_FAM = ("flow", "blink", "pulse", "ripple", "glow", "run", "spin")
ENTER_MAX, LOOP_KINDS_MAX = 2, 1


def check_motion(html, rep):
    """장마다 움직임 종류가 과하지 않은가 — 판정이 아니라 신호다 (DESIGN.md 「4」).

    부록 장(data-apx)은 뺀다. 카탈로그의 움직임 견본처럼 모아 보여 주는 자리다."""
    busy = []
    for k, (tag, body) in enumerate(_slices(html), 1):
        if "data-apx" in tag:
            continue
        fam = set(re.findall(r"\bbl-a--([a-z0-9]+)", body))
        enter = sorted(f for f in fam if f not in LOOP_FAM)
        loops = {f for f in fam if f in LOOP_FAM}
        if "<animateMotion" in body or "<animate " in body:
            loops.add("svg")
        for css in re.findall(r"<style[^>]*>(.*?)</style>", body, re.S):
            for m in re.finditer(r"animation(?:-name)?\s*:\s*([^;}]*infinite[^;}]*)", css):
                name = re.findall(r"\b(x[A-Z]\w*|[a-z][\w-]*[A-Z]\w*)\b", m.group(1))
                loops.add("own:" + (name[0] if name else "?"))
        if len(enter) > ENTER_MAX or len(loops) > LOOP_KINDS_MAX:
            m = re.search(r'id="([^"]+)"', tag)
            busy.append(f"{k:02d}" + (f"({m.group(1)})" if m else "")
                        + f" 등장 {len(enter)} · 반복 {len(loops)}")
    if busy:
        rep.w(f"움직임 과다 {len(busy)}장 — 장마다 등장 {ENTER_MAX}종 · 반복 {LOOP_KINDS_MAX}종까지: "
              + " · ".join(busy[:6]))
    else:
        rep.o(f"움직임 절제 — 장마다 등장 {ENTER_MAX}종 · 반복 {LOOP_KINDS_MAX}종 이내 (부록 제외)")


def check_visual(html, rep):
    """내용 장 중 글 · 표만 있는 장이 얼마나 되는가. 판정이 아니라 신호다.

    1.7.0 으로 만든 덱이 표 · 목록만으로 채워져 밋밋하게 나온 일이 있었다. 검사기가
    바닥(띠 · 폰트 · 대비)만 보니 그래도 실패 0 이었다. 여기서는 막지 않고 알린다 —
    표가 맞는 장도 있다."""
    own = "\n".join(own_css_blocks(html))
    own_cls = set(re.findall(r"\.((?!b[lr]-)[a-zA-Z][\w-]*)", own))
    content, plain = 0, []
    for k, (tag, body) in enumerate(_slices(html), 1):
        if any(c in tag for c in _FRAME_CLS) or "data-apx" in tag:
            continue
        bd = re.search(r'class="[^"]*\bbl-bd\b[^"]*"', body)
        if not bd or any(re.search(r'class="[^"]*\b' + c + r'\b', body) for c in _FRAME_CLS):
            continue
        body = body[bd.start():]
        content += 1
        cls = set(" ".join(re.findall(r'class="([^"]*)"', body)).split())
        has_media = bool(re.search(r"<(svg|canvas|video)\b", body)) or bool(
            re.search(r"<img\b(?![^>]*br-logo)", body.split("bl-rf")[0]))
        if has_media or cls & set(VISUAL_CLS) or cls & own_cls:
            continue
        m = re.search(r'id="([^"]+)"', tag)
        plain.append(f"{k:02d}" + (f"({m.group(1)})" if m else ""))
    if not content:
        rep.o("본문 표현 — 내용 장 없음 (해당 없음)")
    elif len(plain) * 2 > content:
        rep.w(f"본문 표현 — 내용 장 {content}장 중 {len(plain)}장이 글 · 표뿐: {' '.join(plain[:12])}. "
              "흐름 · 일정 · 비교 · 수치는 카탈로그 부품이나 맞춤 도식으로 그린다")
    else:
        rep.o(f"본문 표현 — 내용 장 {content}장 중 글 · 표뿐인 장 {len(plain)}장")


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
    칩 하나가 근거 여럿을 가리킬 수 있다(data-ev="E1,E2" — 패널에 탭으로 뜬다).

    근거 항목마다 제목 · 등급 · 출처는 반드시 있어야 한다. 등급은 A·B·C·R
    네 가지다(JSON 의 grades 로 늘릴 수 있다). 칩이 하나도 없는 덱은 해당 없음.

    캡처를 붙인 근거는 셋을 더 본다 — 캡처 id 가 img 표에 있는가, 하이라이트
    상자(hl)가 있는 캡처를 가리키고 값이 0~1 사각형인가, 원문(doc)이 문서 안
    <script id> 로 있는가. 하나라도 어긋나면 패널이 빈 뷰어나 빈 원문을 연다."""
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
    imgs = data.get("img") or {}
    rects = data.get("hl") or {}
    grades = EV_GRADES | set((data.get("grades") or data.get("gr") or {}).keys())
    keys = [k.strip() for c in chips for k in c.split(",") if k.strip()]
    missing = sorted(set(keys) - set(ev))
    bad = []
    for k, e in ev.items():
        lack = [f for f in ("title", "grade", "src") if not e.get(f)]
        if lack:
            bad.append(f"{k} — {'·'.join(lack)} 없음")
        elif e["grade"] not in grades:
            bad.append(f"{k} — 등급 {e['grade']} 은 정의되지 않음")
        for it in e.get("imgs") or []:
            iid = it[0] if isinstance(it, (list, tuple)) and it else None
            if not iid or iid not in imgs:
                bad.append(f"{k} — 캡처 {iid} 가 img 표에 없음")
        doc = e.get("doc")
        if doc and not re.search(r'<script[^>]*\sid="' + re.escape(doc) + r'"', html):
            bad.append(f"{k} — 원문 {doc} 의 <script id> 가 없음")
    for iid, rs in rects.items():
        if iid not in imgs:
            bad.append(f"하이라이트 상자 {iid} — 그런 캡처가 없음")
            continue
        for r in rs:
            ok = (isinstance(r, (list, tuple)) and len(r) == 4 and all(isinstance(v, (int, float)) for v in r)
                  and 0 <= r[0] <= 1 and 0 <= r[1] <= 1 and 0 < r[2] <= 1 and 0 < r[3] <= 1)
            if not ok:
                bad.append(f"하이라이트 상자 {iid} — 0~1 사각형 [x, y, w, h] 가 아님: {r}")
    if missing:
        rep.f(f"근거 없는 출처 칩 — {', '.join(missing)}")
    if bad:
        rep.f(f"근거 항목 불완전 {len(bad)}건")
        for b in bad[:6]:
            print(f"        {b}")
    if not missing and not bad:
        extra = f" · 캡처 {len(imgs)}장" if imgs else ""
        rep.o(f"출처 칩 — {len(chips)}개 모두 근거 {len(ev)}건에 이어짐 · 제목·등급·출처 완비{extra}")


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


class _Slides(HTMLParser):
    """장마다 id · 노트 · 단계 값, 그리고 문서 전체의 클래스를 모은다.

    정규식으로 원문을 훑으면 화면에 글자로 적힌 마크업 견본(&lt;i class=…&gt;)까지
    클래스로 센다. 브라우저처럼 태그만 읽는다 — script · style 속은 태그가 아니다."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.slides, self.classes, self.links = [], set(), []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        cls = (a.get("class") or "").split()
        self.classes.update(c for c in cls if c.startswith(("bl-", "br-")))
        if tag == "link" and "stylesheet" in (a.get("rel") or "") and a.get("href"):
            self.links.append(("css", a["href"]))
        if tag == "script" and a.get("src"):
            self.links.append(("js", a["src"]))
        if tag == "section" and "bl-sl" in cls:
            self.slides.append({"id": a.get("id") or "", "notes": a.get("data-notes") or "", "f": set()})
        elif self.slides and "data-f" in a:
            self.slides[-1]["f"].add((a.get("data-f") or "").strip())


def check_steps(html, rep):
    """노트의 [클릭] 이 단계 수보다 적은 장이 없는가.

    대본 창은 [클릭] 을 「클릭 n」 배지로 그리고 지금 단계와 맞춰 지난 것 · 다음 것을
    칠한다. 단계가 셋인데 [클릭] 이 없으면 발표자는 몇 번 눌러야 다음 장인지 모른다.
    [클릭] 이 단계보다 많은 것은 허용한다 — 발표 중 클릭으로 여는 겹쳐 보기(data-peek-seq)도
    [클릭] 으로 적는다."""
    p = _Slides()
    p.feed(html)
    p.close()
    bad, staged = [], 0
    for k, sl in enumerate(p.slides, 1):
        lv = len(sl["f"])
        if not lv:
            continue
        staged += 1
        n = len(re.findall(r"\[클릭\]", sl["notes"]))
        if n < lv:
            bad.append(f"{k:02d}장 {sl['id'] or ''} — 단계 {lv} · [클릭] {n}")
    if bad:
        rep.f(f"노트의 [클릭] 이 단계보다 적은 장 {len(bad)}개 — 대본 창 배지가 단계와 어긋난다")
        for b in bad[:8]:
            print(f"        {b}")
    elif staged:
        rep.o(f"단계 — 단계가 있는 {staged}장 모두 노트의 [클릭] 이 단계 수 이상")
    else:
        rep.o("단계 — 단계 전개 없음 (해당 없음)")


def _read_near(path, ref):
    """덱이 부르는 CSS · JS 를 덱 옆에서, 없으면 스킬 assets/ 에서 읽는다."""
    if "//" in ref or ref.startswith("data:"):
        return ""
    for base in (os.path.dirname(os.path.abspath(path)), os.path.join(os.path.dirname(HERE), "assets")):
        f = os.path.join(base, ref)
        if os.path.isfile(f):
            return open(f, encoding="utf-8").read()
    return ""


def check_classes(html, rep, path):
    """bl- · br- 클래스가 전부 정의돼 있는가.

    계통 CSS(덱이 부르는 것 + 묶어 넣은 블록)의 클래스 선택자와 뷰어 JS 가 쓰는 이름이
    「아는 클래스」다. 그 밖의 bl-·br- 이름은 지어낸 것이다 — 아무 모양도 동작도 붙지 않는다.
    덱 안 맞춤 CSS 에 적었다고 아는 이름이 되지 않는다. 자기 클래스는 다른 접두어로 짓는다."""
    p = _Slides()
    p.feed(html)
    p.close()
    known = _system_classes(html, path)
    unknown = sorted(c for c in p.classes if c not in known)
    if not known:
        rep.w("클래스 검사 생략 — 덱이 부르는 CSS 를 찾지 못했다")
    elif unknown:
        rep.f(f"정의 없는 클래스 {len(unknown)}개 — 계통 CSS · 뷰어 어디에도 없다: {' '.join(unknown[:12])}")
        print("        bl-·br- 는 계통 이름이다. 카탈로그 부품은 그 이름 그대로, 맞춤 도식은 다른 접두어로 짓는다")
    else:
        rep.o(f"클래스 — bl-·br- {len(p.classes)}개 모두 계통 CSS · 뷰어에 있다")


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
    edge, hud_hits, errors, dead = None, [], [], []
    ink, fit, narrow = [], [], []
    wants_engine = "live-viewer.js" in open(path, encoding="utf-8").read()
    with sync_playwright() as pw:
        br = pw.chromium.launch(executable_path=chrome)
        for w, h in VIEWS:
            pg = br.new_page(viewport={"width": w, "height": h}, reduced_motion="reduce")
            pg.on("pageerror", lambda e, w=w: errors.append(f"{w}px {str(e).splitlines()[0]}"))
            pg.goto(url)
            pg.wait_for_timeout(1200)

            data = pg.evaluate(r"""(NOTE) => {
              const root = parseFloat(getComputedStyle(document.documentElement).fontSize);
              const out = {root, tiny: [], body: [], marks: [], over: 0, html: ''};
              out.over = Math.max(0, document.documentElement.scrollWidth
                                   - document.documentElement.clientWidth);
              out.html = document.body.innerText;
              out.engine = !!(window.blDeck && window.blDeck.slides && window.blDeck.slides.length);

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
            by_what = {}
            for what, n in pg.evaluate(HUD_PROBE):
                by_what.setdefault(what, []).append(n)
            for what, ns in by_what.items():
                at = ",".join(map(str, ns[:6])) + ("…" if len(ns) > 6 else "")
                hud_hits.append(f"{w}px {what} {len(ns)}장({at})")

            if data["over"] > 1:
                overflow.append(f"{w}px — {data['over']}px 넘침")
            if wants_engine and not data["engine"]:
                dead.append(f"{w}px")
            tiny += [dict(r, view=w) for r in data["tiny"]]
            body_small += [dict(r, view=w) for r in data["body"]]
            if w != VIEWS[0][0]:
                narrow += [dict(r, view=w) for r in pg.evaluate(NARROW_PROBE)]
            if w == VIEWS[0][0]:
                marks = data["marks"]
                drawn = data["html"]
                ink = pg.evaluate(INK_PROBE)
                fit = pg.evaluate(FIT_PROBE)
                if shots:
                    # 장마다 한 장씩. 눈으로 볼 것(여백 · 균형 · 겹침)은 장 단위로 나온다
                    os.makedirs(shots, exist_ok=True)
                    ids = pg.evaluate("() => [...document.querySelectorAll('.bl-sl')].map(s => s.id || '')")
                    for k, sid in enumerate(ids):
                        pg.evaluate("(k) => { const s = document.querySelectorAll('.bl-sl')[k];"
                                    " if (window.blDeck) blDeck.go(k); else s.scrollIntoView(); }", k)
                        pg.wait_for_timeout(160)
                        name = f"{k + 1:02d}" + (f"-{sid}" if sid else "") + ".png"
                        pg.screenshot(path=os.path.join(shots, name), full_page=False)
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

    if ink:
        rep.f(f"보이지 않는 글자 {len(ink)}건 — 글자색과 뒷배경 대비 1.25:1 미만")
        for t in ink[:6]:
            print(f"        {t['sl']}  .{t['cls']}  {t['r']}:1  {t['txt']}")
    else:
        rep.o("보이지 않는 글자 — 글자색과 뒷배경이 같은 색인 글자 없음 (1.25:1 미만 0)")

    if fit or narrow:
        rep.f(f"세로 넘침 — 16:9 {len(fit)}장 · 좁은 폭 {len(narrow)}건 — 본문이 꼬리띠 밑으로 · 꼬리띠가 장 밖으로 나간다")
        for t in fit[:6]:
            print(f"        16:9   {t['k']:02d}장 {t['sl']}  {t['px']}px  .{t['cls']}")
        for t in narrow[:6]:
            print(f"        {t['view']}px  {t['k']:02d}장 {t['sl']}  {t['px']}px  .{t['cls']}")
    else:
        rep.o("세로 넘침 — 16:9 는 한 화면 안, 좁은 폭은 꼬리띠가 장 안에서 본문 아래")

    if errors:
        rep.f(f"스크립트 예외 {len(errors)}건 — 뷰어나 부품이 시작하다 멈췄다")
        for e in errors[:5]:
            print(f"        {e}")
    elif dead:
        rep.f(f"뷰어 엔진이 뜨지 않았다 ({' · '.join(dead)}) — live-viewer.js 를 찾지 못했다. "
              "연결형이면 JS 를 덱 옆에 두고, 아니면 --single-file 로 묶는다")
    else:
        rep.o("스크립트 — 세 폭 모두 엔진이 뜨고 예외 없이 시작한다")

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
    ap.add_argument("--shots", help="장마다 화면 PNG(1600x900)를 저장할 폴더")
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
    check_steps(html, rep)
    check_classes(html, rep, a.path)
    check_own_css(html, rep, a.path)
    check_visual(html, rep)
    check_motion(html, rep)
    check_render(a.path, rep, a.shots, seen_style=bad)

    sys.exit(rep.render())


if __name__ == "__main__":
    main()
