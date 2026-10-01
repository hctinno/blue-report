#!/usr/bin/env python3
"""회사 정보와 로고를 덱 템플릿에 한 번에 적용한다.

덱의 자리표시자(회사명·워드마크·이메일·전화·저작권·로고 자리)는 8군데에 흩어져 있다.
손으로 고치면 빠뜨리기 쉬우므로 brand.json 한 곳에서 읽어 일괄 적용한다.

항상 원본 템플릿에서 새로 만들기 때문에 몇 번을 실행해도 결과가 같다.
로고는 data URI로 박으므로 완성된 덱 파일 하나만 들고 다니면 된다.

    python3 apply_brand.py --brand brand.json                  # dist/deck-branded.html
    python3 apply_brand.py --brand brand.json -o 우리덱.html
    python3 apply_brand.py --brand brand.json --single-file    # CSS까지 인라인한 한 장짜리
"""
import argparse
import base64
import json
import mimetypes
import os
import re
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
ROOT = os.path.dirname(HERE)
ASSETS = os.path.join(ROOT, "assets")

# 용도별 덱. 이름으로 고르거나 --deck 에 파일 경로를 직접 준다.
DECKS = {
    "catalog":  "deck-template.html",         # 레이아웃 19종 카탈로그
    "internal": "deck-internal-report.html",  # 사내 보고 (월간)
    "weekly":   "deck-weekly-report.html",    # 조직 주간보고
    "ax":       "deck-ax-weekly.html",        # AX 조직 주간보고 (1장 + 부록)
    "team":     "deck-team-weekly.html",      # 팀 단위 압축 주간보고 (2장 · 가로)
    "sales":    "deck-sales-proposal.html",   # 외부 제안·영업
    "project":  "deck-project-report.html",   # 프로젝트 착수·완료
    "training": "deck-training.html",         # 교육·기술 설명
    "exec":     "deck-exec-report.html",      # 경영진 보고 (결론 먼저 · 6장)
    "allhands": "deck-allhands.html",         # 전직원 보고 (타운홀)
    "strategy": "deck-strategy-report.html",  # 전략 보고 (논증형 결정 요청 · 16장)
    "report":   "deck-report.html",           # 고밀도 보고 (본문 14 + 부록 5 · 도해 중심)
}

# A4 문서. 덱과 달리 가로 슬라이드가 아니라 794x1123 세로 지면이다.
DOCS = {
    "minutes": "doc-minutes.html",           # 회의록
    "policy":  "doc-policy.html",            # 사규·규정 (조·항·호 · 개정 이력 · 결재란)
    "manual":  "doc-manual.html",            # 매뉴얼·가이드 (목차 · 절차 단계 · 캡처)
    "notice":  "doc-notice.html",            # 공지 (1쪽 완결)
}

# 웹 보드. 슬라이드도 A4 도 아닌 제3의 계통이다 — 지면 크기가 없고 화면 폭에
# 따라 흐른다. 글자 하한 12.5px, 판정은 check_board.py 가 한다.
# 읽는 물건이 아니라 상태를 바꾸는 화면이라 PPTX·PDF 대상이 아니다.
# 이름은 덱·문서와 겹치면 안 된다 — resolve() 가 덱을 먼저 보므로 겹친 이름은
# 보드에 영영 닿지 않는다. exec·team 이 실제로 덱에 있어 그렇게 묻혔다.
# 아래 NAMES 검사가 같은 실수를 다시 못 하게 막는다.
BOARDS = {
    "board":     "board-task.html",    # 과제 실행보드 — 레일 · KPI · 표 · 메모 (가장 작은 견본)
    "manage":    "board-manage.html",  # 관리보드 — 절 12 · 표 8 대시보드형. 전사 여러 축을 한 화면에
    "execboard": "board-exec.html",    # 실행보드 — 항목마다 상태 알약과 메모. 매일 움직이는 목록
    "teamboard": "board-team.html",    # 팀보드 — 칸반 4열. 주간 회의에서 화면을 같이 보며 좁힐 때
    "gapcheck":  "board-gap.html",     # 점검보드 — 공백 부모 + 대응 자식. 빠진 칸을 찾을 때
}

# 라이브 덱 — 고정 지면이 없는 발표 계통. 한 장이 100dvh 이고 치수가 전부 rem 이다.
# 덱(1920x1080)과 목적은 같지만 규격이 달라 검사기도 check_live.py 로 따로 있다.
LIVE = {
    # 새 보고서는 standard 에서 시작한다. 레이아웃 어휘가 한 파일에 모여 있고
    # 머리띠·꼬리띠·로고·워터마크가 전부 달려 있다.
    "standard": "live-standard.html",  # 기준 덱 — 새 보고서의 출발점
    "live": "live-brief.html",         # 라이브 브리핑 — 짧은 브리핑용 (견본)
}

# 네 표의 이름이 겹치면 뒤에 오는 쪽이 통째로 묻힌다. 불러오는 순간 걸리게 둔다.
_dup = ([k for k in DOCS if k in DECKS]
        + [k for k in BOARDS if k in DECKS or k in DOCS]
        + [k for k in LIVE if k in DECKS or k in DOCS or k in BOARDS])
assert not _dup, f"덱·문서·보드 이름 충돌: {_dup}"

LOGO_TYPES = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
              ".svg": "image/svg+xml", ".webp": "image/webp"}
LOGO_WARN_BYTES = 400 * 1024

HANGUL = re.compile(r"[가-힣]")

# 슬라이드 우측 상단 마크. 그룹1=배경 밝기, 그룹2=자리표시자 주석(다시 찾기 쉽게 남긴다).
MARK = re.compile(r'<div class="br-mark" data-on="(dark|light)">(<!--.*?-->)?.*?</div>', re.S)
# 다크면 가운데 배경 워터마크. 마크와 자리표시자 구조가 같지만 크기·색 처리가 달라 따로 잡는다.
WATERMARK = re.compile(r'<div class="br-watermark" data-on="(dark|light)">(<!--.*?-->)?.*?</div>', re.S)


def resolve(name):
    """덱·문서·보드 이름 또는 파일 경로를 실제 경로로 바꾼다.

    이름 세 벌을 한곳에서 푼다. 다른 스크립트도 이것을 불러 쓰므로
    새 덱·문서·보드가 생겨도 고칠 곳은 위 표 세 개뿐이다."""
    if name in DECKS:
        return os.path.join(ASSETS, DECKS[name])
    if name in DOCS:
        return os.path.join(ASSETS, DOCS[name])
    if name in BOARDS:
        return os.path.join(ASSETS, BOARDS[name])
    if name in LIVE:
        return os.path.join(ASSETS, LIVE[name])
    return os.path.abspath(name)


def load_brand(path):
    with open(path, encoding="utf-8") as f:
        b = json.load(f)
    missing = [k for k in ("company", "copyrightYear") if not b.get(k)]
    if missing:
        sys.exit(f"오류: brand.json에 필수 항목이 없다 — {', '.join(missing)}")
    b.setdefault("wordmark", b["company"])
    b.setdefault("email", "")
    b.setdefault("website", "")
    b.setdefault("phone", "")
    b.setdefault("logoOnLight", "")
    b.setdefault("watermark", "")          # 다크면 배경 워터마크. 비우면 logo 를 키워 쓴다
    b.setdefault("watermarkOnLight", "")   # 밝은 지면 배경 워터마크. 비우면 logoOnLight
    b.setdefault("logoHeight", 40)
    return b


def logo_data_uri(brand, brand_path, key="logo"):
    """로고를 data URI로 만든다. 해당 항목이 비어 있으면 None."""
    rel = brand.get(key)
    if not rel:
        return None
    path = rel if os.path.isabs(rel) else os.path.join(os.path.dirname(os.path.abspath(brand_path)), rel)
    if not os.path.isfile(path):
        sys.exit(f"오류: 로고 파일이 없다 — {path}")
    ext = os.path.splitext(path)[1].lower()
    mime = LOGO_TYPES.get(ext) or mimetypes.guess_type(path)[0]
    if not mime or not mime.startswith("image/"):
        sys.exit(f"오류: 지원하지 않는 로고 형식 — {ext}. PNG·JPG·SVG·WEBP를 쓴다.")
    size = os.path.getsize(path)
    if size > LOGO_WARN_BYTES:
        print(f"주의: 로고가 {size/1024:.0f}KB다. 덱 파일이 그만큼 커진다. "
              f"200KB 이하로 줄이길 권한다.", file=sys.stderr)
    with open(path, "rb") as f:
        data = base64.b64encode(f.read()).decode("ascii")
    print(f"로고[{key}]: {path} ({mime}, {size/1024:.1f}KB) → data URI")
    return f"data:{mime};base64,{data}"


def logo_uris(brand, brand_path):
    """브랜드가 쓰는 이미지 네 벌을 한 번에 data URI 로 만든다.

    이 딕셔너리를 두 곳에서 따로 만들다 사고가 났다. build_single_file.py 가
    watermark 키를 빠뜨려, 아티팩트에서만 워터마크가 전체 로고로 되돌아갔다.
    호출부가 늘어도 키가 갈라지지 않게 여기 한 곳에서만 만든다."""
    return {
        "dark":  logo_data_uri(brand, brand_path, "logo"),
        "light": logo_data_uri(brand, brand_path, "logoOnLight"),
        "watermark":        logo_data_uri(brand, brand_path, "watermark"),
        "watermarkOnLight": logo_data_uri(brand, brand_path, "watermarkOnLight"),
    }


def wordmark_html(brand, font_size):
    """로고가 없을 때 쓰는 워드마크. 한글이면 자간을 줄인다.

    폰트는 한글이든 라틴이든 같다 — 프리텐다드 한 벌이 둘 다 담는다.
    갈라야 하는 것은 자간이다. 라틴 대문자 워드마크는 .2em 으로 벌려야
    마크처럼 보이지만, 한글에 같은 값을 주면 글자가 흩어져 낱자로 읽힌다.

    색은 넣지 않는다. .br-mark[data-on] 규칙이 배경에 맞춰 정한다."""
    text = brand["wordmark"]
    if HANGUL.search(text):
        style = f"font:700 {font_size}px/1 var(--br-font-kr);letter-spacing:.02em"
    else:
        style = (f"font:600 {font_size}px/1 var(--br-font-label);"
                 f"letter-spacing:var(--br-ls-mark)")
    return f'<span class="br-wordmark" style="{style}">{text}</span>'


def logo_html(uri, height):
    return (f'<img class="br-logo" src="{uri}" alt="회사 로고" '
            f'style="height:{height}px;width:auto">')


def apply(html, brand, uris, title_override=None):
    """자리표시자를 실제 값으로 바꾼다. 바꾼 건수를 함께 돌려준다."""
    n = 0

    def sub(pattern, repl, count=0):
        nonlocal n, html
        html, k = re.subn(pattern, lambda m: repl, html, count=count)
        n += k
        return k

    # 우측 상단 브랜드 마크 — 모든 슬라이드에 같은 자리로 들어간다.
    # data-on 이 배경 밝기를 알려주므로 슬라이드마다 로고 변형을 바꿔 넣는다.
    h = brand["logoHeight"]

    def one_mark(m):
        on = m.group(1)
        u = uris["dark"] if on == "dark" else uris["light"]
        inner = logo_html(u, h) if u else wordmark_html(brand, 28)
        # 그룹2(자리표시자 주석)는 선택이라 없으면 None 이다. 그대로 f-string 에
        # 넣으면 슬라이드에 'None' 이 찍힌다 — 워터마크 쪽과 같이 빈 문자열로 접는다.
        return f'<div class="br-mark" data-on="{on}">{m.group(2) or ""}{inner}</div>'

    def one_watermark(m):
        # 마크와 같이 배경 밝기에 따라 잉크를 고른다. 다크면은 흰색 녹아웃,
        # 밝은 지면은 원색이다. brand.json 에 심볼만 잘라 낸 판을 주면 그것을 먼저
        # 쓰고, 없으면 마크용 로고를 그대로 키워 쓴다.
        on = m.group(1)
        if on == "dark":
            u = uris.get("watermark") or uris["dark"]
        else:
            u = uris.get("watermarkOnLight") or uris["light"]
        inner = f'<img src="{u}" alt="">' if u else wordmark_html(brand, 128)
        return f'<div class="br-watermark" data-on="{on}">{m.group(2) or ""}{inner}</div>'

    html, n_wm = WATERMARK.subn(one_watermark, html)
    n += n_wm

    html, n_mark = MARK.subn(one_mark, html)
    n += n_mark
    if not n_mark:
        sys.exit("오류: br-mark 자리를 하나도 찾지 못했다. 템플릿이 수정된 것 같다.\n"
                 "        슬라이드는 슬라이드마다, A4 문서는 쪽 머리말마다 하나씩 있어야 한다.")

    contact = brand["email"] or brand["website"]
    if contact:
        sub(re.escape("contact@company.co.kr"), contact)
        if not brand["email"]:
            # 이메일 미확정 — 홈페이지 주소를 쓰므로 라벨도 WEB으로 바꾼다.
            sub(r'<span style="letter-spacing:\.1em">EMAIL</span>',
                '<span style="letter-spacing:.1em">WEB</span>', 1)
    else:
        # 연락처 없음 — 표지의 연락처 줄과 마무리의 EMAIL 행을 통째로 없앤다.
        sub(r'\n\s*<div class="br-num"[^>]*>contact@company\.co\.kr</div>', "", 1)
        sub(r'\n\s*<div style="display:flex;gap:24px;justify-content:flex-end;'
            r'margin-top:20px;[^"]*">\s*\n\s*<span[^>]*>EMAIL</span>'
            r'<span[^>]*>contact@company\.co\.kr</span>\s*\n\s*</div>', "", 1)

    if brand["phone"]:
        sub(re.escape("02-0000-0000"), brand["phone"])
    else:
        # 전화 없음 — PHONE 행을 통째로 없앤다.
        sub(r'\n\s*<div style="display:flex;gap:24px;justify-content:flex-end;'
            r'margin-top:14px;[^"]*">\s*\n\s*<span[^>]*>PHONE</span>'
            r'<span[^>]*>02-0000-0000</span>\s*\n\s*</div>', "", 1)
    sub(re.escape("© 2026 COMPANY NAME · All rights reserved"),
        f'© {brand["copyrightYear"]} {brand["company"]} · All rights reserved')

    # 슬라이드 푸터의 문서명. 쪽번호는 뷰어가 자동으로 매기므로 여기서 건드리지 않는다.
    if brand.get("docTitle"):
        sub(r'data-deck-title="[^"]*"', f'data-deck-title="{brand["docTitle"]}"', 1)

    # A4 문서의 data-doc-title 은 브랜드가 아니라 그 문서 자체의 제목이다
    # (회의록이면 회의 이름). brand.json 의 docTitle 로 덮으면 문서가 이름을 잃는다.
    # --title 로 명시했을 때만 바꾼다.
    if title_override:
        sub(r'data-doc-title="[^"]*"', f'data-doc-title="{title_override}"', 1)

    # A4 문서 꼬리말의 회사명. 슬라이드에는 없는 자리다.
    sub(r'<span class="bd-company">COMPANY NAME</span>',
        f'<span class="bd-company">{brand["company"]}</span>')

    # 자리표시자 주석은 일부러 남긴다. 나중에 로고를 바꿀 때 위치를 다시 찾기 쉽다.
    # 남은 자리표시자를 셀 때는 그 주석을 빼고 본문만 본다.
    body_only = re.sub(r"<!--.*?-->", "", html, flags=re.S)
    left = re.findall(r"COMPANY NAME|company\.co\.kr|02-0000-0000", body_only)
    return html, n, left


HEAD = re.compile(r"<head\b.*?</head>", re.S)
SHEET = re.compile(r'<link[^>]+rel="stylesheet"[^>]+href="([^"]+)"')


def copy_assets(html, out):
    """단일 파일이 아닐 때, HTML 이 부르는 CSS 와 폰트를 결과물 옆에 같이 둔다.

    이걸 안 하면 결과물이 조용히 망가진다. `<link href="blue-report.css">` 는
    결과물 기준 상대 경로라 decks-out/ 에는 그 파일이 없다 — 브라우저는 404 를
    삼키고 스타일 없는 문서를 그린다. 글자는 Times New Roman 이 되고 지면도
    띠도 사라지는데, 파일은 멀쩡히 만들어져 있어 만든 사람이 알아채지 못한다.
    실제로 그렇게 나간 덱을 보고 「로고도 폰트도 안 들어갔다」는 말을 들었다.

    경고 한 줄로는 부족했다. 경고는 스크롤 위로 사라지고 파일만 남는다.

    폰트는 CSS 기준 상대 경로(fonts/...)라 CSS 와 같은 자리에 둔다."""
    head = HEAD.search(html)
    if not head:
        return []
    src_dir = os.path.join(ROOT, "assets")
    out_dir = os.path.dirname(os.path.abspath(out)) or "."
    done = []
    for href in SHEET.findall(head.group(0)):
        if "//" in href or href.startswith("data:"):
            continue                      # 바깥에서 받아 오는 것은 건드리지 않는다
        src = os.path.join(src_dir, href)
        dst = os.path.join(out_dir, href)
        if not os.path.isfile(src) or os.path.abspath(src) == os.path.abspath(dst):
            continue
        os.makedirs(os.path.dirname(os.path.abspath(dst)), exist_ok=True)
        shutil.copy2(src, dst)
        done.append(href)
    if done:
        fsrc, fdst = os.path.join(src_dir, "fonts"), os.path.join(out_dir, "fonts")
        if os.path.isdir(fsrc) and os.path.abspath(fsrc) != os.path.abspath(fdst):
            shutil.copytree(fsrc, fdst, dirs_exist_ok=True)
            done.append("fonts/")
    return done


def main():
    ap = argparse.ArgumentParser(description="회사 정보·로고를 덱에 적용")
    ap.add_argument("--brand", required=True, help="brand.json 경로")
    ap.add_argument("-o", "--out", help="출력 HTML (기본 dist/deck-branded.html)")
    ap.add_argument("--single-file", action="store_true",
                    help="CSS까지 인라인해 파일 하나로 만든다")
    ap.add_argument("--title", help="이 덱의 문서명 (푸터에 들어간다). brand.json의 docTitle보다 우선한다")
    ap.add_argument("--deck", default="catalog",
                    help="덱 이름(" + " · ".join(DECKS) + ") · A4 문서 이름("
                         + " · ".join(DOCS) + ") · 웹 보드 이름("
                         + " · ".join(BOARDS) + ") · 라이브 덱 이름("
                         + " · ".join(LIVE) + ") · 또는 HTML 파일 경로")
    a = ap.parse_args()

    brand = load_brand(a.brand)
    if a.title:
        brand["docTitle"] = a.title
    # 다크면용(흰색 녹아웃)과 밝은면용(원색) 두 벌을 읽는다.
    uris = logo_uris(brand, a.brand)
    if uris["dark"] and not uris["light"]:
        print("주의: logoOnLight 가 없다. 흰색 로고를 밝은 지면에 얹으면 보이지 않으므로 "
              "밝은 슬라이드는 워드마크 텍스트로 둔다. brand.json 에 원색 로고 경로를 넣어라.",
              file=sys.stderr)
    if uris["light"] and not uris["dark"]:
        print("주의: logo(다크면용 흰색 녹아웃)가 없다. 표지·다크 슬라이드는 "
              "워드마크 텍스트로 둔다.", file=sys.stderr)

    deck_path = resolve(a.deck)
    if not os.path.isfile(deck_path):
        sys.exit(f"오류: 덱·문서를 찾지 못했다 — {deck_path}\n"
                 f"덱 이름: {' · '.join(DECKS)}\n"
                 f"문서 이름: {' · '.join(DOCS)}\n"
                 f"보드 이름: {' · '.join(BOARDS)}\n"
                 f"라이브 이름: {' · '.join(LIVE)}")
    is_doc = os.path.basename(deck_path).startswith("doc-")
    print(f"{'문서' if is_doc else '덱'}: {os.path.basename(deck_path)}")

    html = open(deck_path, encoding="utf-8").read()
    html, n, left = apply(html, brand, uris, a.title)

    if a.single_file:
        from build_single_file import inline_assets
        html = inline_assets(html)

    out = a.out or os.path.join(ROOT, "dist", f"deck-{a.deck}-branded.html")
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"\n적용 {n}건")
    print(f"  회사명   {brand['company']}")
    print(f"  마크     다크면 {'로고' if uris['dark'] else '워드마크 ' + brand['wordmark']}"
          f" · 밝은면 {'로고' if uris['light'] else '워드마크 ' + brand['wordmark']}"
          + (" (쪽 머리말 · 높이 20px 로 blue-doc.css 가 맞춘다)" if is_doc
             else f" (높이 {brand['logoHeight']}px, 우측 상단)"))
    if brand["email"]:
        print(f"  연락처   {brand['email']}")
    elif brand["website"]:
        print(f"  연락처   {brand['website']} (이메일 미확정 — WEB으로 표기)")
    else:
        print("  연락처   없음 — 연락처 줄 삭제")
    print(f"  전화     {brand['phone'] or '없음 — PHONE 행 삭제'}")
    print(f"  저작권   © {brand['copyrightYear']} {brand['company']}")
    if is_doc:
        # A4 문서의 제목은 문서 자체의 내용이다. --title 로 덮었을 때만 알린다.
        print(f"  문서명   {a.title}" if a.title else "  문서명   문서에 적힌 것 유지 (브랜드가 건드리지 않는다)")
    else:
        print(f"  문서명   {brand.get('docTitle') or '(미지정 — 템플릿 기본값 유지)'}")
    print(f"\n생성: {out}")
    if left:
        print(f"\n주의: 본문에 남은 자리표시자 {len(left)}건 — {', '.join(sorted(set(left)))}")
    if not a.single_file:
        copied = copy_assets(html, out)
        if copied:
            print(f"함께 복사: {' · '.join(copied)}")
        print("파일 하나로 만들려면 --single-file 을 준다.")


if __name__ == "__main__":
    main()
