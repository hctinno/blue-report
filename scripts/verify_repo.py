#!/usr/bin/env python3
"""저장소 전체 점검 — CI 와 로컬이 같은 명령을 쓴다.

    python3 scripts/verify_repo.py             # 전부 점검
    python3 scripts/verify_repo.py --shots out # 슬라이드별 PNG 도 남긴다
    python3 scripts/verify_repo.py --only decks

검사 항목
  docs      A4 문서 4종을 check_doc.py 9항목으로 판정한다.
  decks     덱을 apply_brand.py 로 만들고 check_deck.py 17항목으로 판정한다.
            목록은 apply_brand.py 의 DECKS 가 정한다 — 여기 세지 않는다.
            `실패` 가 하나라도 있으면 저장소 점검이 실패한다.
            `주의` 는 허용한다 — 도넛을 쓰지 않은 덱에서 나오는 정상 결과다.
  boards    웹 보드 5종을 check_board.py 11항목으로 판정한다.
  live      라이브 덱을 check_live.py 22항목으로 판정한다. 고정 지면이 없고
            치수가 rem 이라 px 하한이 아니라 rem 하한으로 본다.
            견본만이 아니라 apply_brand.py 산출물(단일 파일 · 연결형)도 본다.
  pptx      build.js 가 돌고 .pptx 4종이 나오는가.
  dist      dist/ 의 두 파일이 소스에서 재생성한 것과 같은가.
            assets/ 를 고치고 dist/ 를 다시 만들지 않으면 여기서 걸린다.
  encoding  한국어가 UTF-8 로 저장됐고 깨짐 패턴이 없는가.
  plugin    마켓플레이스·플러그인 매니페스트가 성립하는가.
            여기가 깨지면 다른 PC 에서 `plugin install` 이 실패한다.
  sync      HTML 덱과 pptx/content.js 의 내용이 갈라지지 않았는가.
            같은 내용이 두 곳에 있어 한쪽만 고치기 쉽다.
  version   스킬 폴더를 고쳤으면 plugin.json 의 version 을 올렸는가.
            플러그인은 main 을 통째로 받아 가므로 버전이 그대로면
            받는 쪽이 자기 판을 구분하지 못한다.

종료 코드는 실패가 하나라도 있으면 1, 아니면 0 이다.
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unicodedata
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILL = os.path.join(ROOT, ".claude", "skills", "blue-report")
SCRIPTS = os.path.join(SKILL, "scripts")
ASSETS = os.path.join(SKILL, "assets")
BRAND = os.path.join(ROOT, "brand", "hct", "brand.json")

# 덱 목록을 여기 또 적지 않는다. apply_brand.py 가 한 곳에서 정하고
# build_single_file.py 도 거기서 읽는다. 목록이 두 곳에 있으면 덱을 늘릴 때
# 한쪽이 남아 검사가 엉뚱한 개수를 기대한다 — 실제로 그렇게 한 번 걸렸다.
sys.path.insert(0, SCRIPTS)
from apply_brand import DECKS as _DECK_FILES  # noqa: E402
DECKS = list(_DECK_FILES)
from apply_brand import BOARDS as _BOARD_FILES  # noqa: E402
BOARDS = list(_BOARD_FILES.values())
from apply_brand import LIVE as _LIVE_FILES  # noqa: E402

# PPTX 는 카탈로그를 뺀 용도별 덱만 나온다. 카탈로그는 발표물이 아니라 레이아웃 견본첩이다.
EXPECTED_PPTX = len(DECKS) - 1

# A4 문서. 슬라이드가 아니라 지면이 794x1123 이고 검사기가 다르다.
DOCS = ["doc-minutes.html", "doc-policy.html", "doc-manual.html", "doc-notice.html"]

# dist/ 의 두 파일은 빌드 명령이 서로 다르다. 아래가 그 정본이다.
DIST_BUILDS = [
    ("blue-report-deck.html", []),
    ("blue-report-artifact.html", ["--artifact", "--brand", BRAND]),
    # A4 문서도 Artifact 발행 경로를 탄다. 덱과 뷰어·CSS 가 달라 따로 굳혀 둔다.
    ("blue-report-doc-artifact.html", ["--artifact", "--brand", BRAND, "--deck", "minutes"]),
]

# 인코딩이 깨졌을 때 나오는 대표 글자. 스크립트 자신이 걸리지 않도록 코드포인트로 적는다.
MOJIBAKE = ["濡", "湲", "遺", "媛", "李", "???"]
# 이 패턴을 규칙 문장으로 인용하는 문서. 검사에서 제외한다.
# 깨짐 패턴 목록 자체를 본문에 적은 파일들. 규칙을 설명하려면 그 문자를 써야 한다.
MOJIBAKE_EXEMPT = {"CLAUDE.md", "AGENTS.md",
                   os.path.join("scripts", "verify_repo.py"),
                   os.path.join("public", "overlay", "CLAUDE.md")}
SCAN_EXT = {".md", ".html", ".js", ".py", ".json", ".css", ".yml", ".yaml"}

RESULT_RE = re.compile(r"결과: 통과 (\d+) · 주의 (\d+) · 실패 (\d+)")


class Log:
    def __init__(self):
        self.rows, self.failed = [], False

    def ok(self, name, detail=""):
        self.rows.append(("통과", name, detail))

    def warn(self, name, detail=""):
        self.rows.append(("주의", name, detail))

    def fail(self, name, detail=""):
        self.rows.append(("실패", name, detail))
        self.failed = True

    @staticmethod
    def _w(s):
        """한글은 터미널에서 두 칸을 먹는다. 그 폭으로 센다."""
        return sum(2 if unicodedata.east_asian_width(c) in "WF" else 1 for c in s)

    def render(self):
        print("\n" + "=" * 62)
        print("저장소 점검 결과")
        print("=" * 62)
        w = max((self._w(n) for _, n, _ in self.rows), default=0)
        for mark, name, detail in self.rows:
            pad = " " * (w - self._w(name))
            print(f"  {mark}  {name}{pad}  {detail}")
        n_ok = sum(1 for m, _, _ in self.rows if m == "통과")
        n_wa = sum(1 for m, _, _ in self.rows if m == "주의")
        n_fa = sum(1 for m, _, _ in self.rows if m == "실패")
        print(f"\n통과 {n_ok} · 주의 {n_wa} · 실패 {n_fa}")
        if self.failed:
            print("\n실패가 있다. 완료가 아니다.")
        return 1 if self.failed else 0


def run(cmd, cwd=None):
    return subprocess.run(cmd, cwd=cwd or ROOT, capture_output=True, text=True)


# ---------------------------------------------------------------------- 덱

def check_decks(log, out_dir, shots_dir):
    for name in DECKS:
        deck = os.path.join(out_dir, f"{name}.html")
        r = run([sys.executable, os.path.join(SCRIPTS, "apply_brand.py"),
                 "--brand", BRAND, "--deck", name, "--single-file", "-o", deck])
        if r.returncode != 0 or not os.path.exists(deck):
            log.fail(f"덱 {name}", "apply_brand.py 실패 — " + (r.stderr.strip().splitlines() or [""])[-1])
            continue

        cmd = [sys.executable, os.path.join(SCRIPTS, "check_deck.py"), deck]
        if shots_dir:
            cmd += ["--shots", os.path.join(shots_dir, name)]
        r = run(cmd)
        print(r.stdout, end="")
        if r.stderr.strip():
            print(r.stderr, end="", file=sys.stderr)

        m = RESULT_RE.search(r.stdout)
        if not m:
            log.fail(f"덱 {name}", "check_deck.py 가 결과 줄을 내지 않았다")
            continue
        ok, warn, fail = (int(x) for x in m.groups())
        detail = f"통과 {ok} · 주의 {warn} · 실패 {fail}"
        if fail or r.returncode != 0:
            log.fail(f"덱 {name}", detail)
        elif warn:
            log.warn(f"덱 {name}", detail)
        else:
            log.ok(f"덱 {name}", detail)


# ------------------------------------------------------------------ A4 문서

def check_docs(log):
    """문서는 브랜드 적용 대상이 아니다. assets 의 원본을 그대로 본다.

    blue-doc.css 가 blue-report.css 의 토큰을 전제하므로 같은 폴더에서 열어야
    한다. assets/ 안에 둘 다 있어 경로를 옮기지 않는다."""
    assets = os.path.join(SKILL, "assets")
    for name in DOCS:
        path = os.path.join(assets, name)
        if not os.path.exists(path):
            log.fail(f"문서 {name}", "파일이 없다")
            continue
        r = run([sys.executable, os.path.join(SCRIPTS, "check_doc.py"), path])
        print(r.stdout, end="")
        if r.stderr.strip():
            print(r.stderr, end="", file=sys.stderr)
        m = RESULT_RE.search(r.stdout)
        if not m:
            log.fail(f"문서 {name}", "check_doc.py 가 결과 줄을 내지 않았다")
            continue
        ok, warn, fail = (int(x) for x in m.groups())
        detail = f"통과 {ok} · 주의 {warn} · 실패 {fail}"
        if fail or r.returncode != 0:
            log.fail(f"문서 {name}", detail)
        elif warn:
            log.warn(f"문서 {name}", detail)
        else:
            log.ok(f"문서 {name}", detail)


# ---------------------------------------------------------------------- 웹 보드

def check_boards(log):
    """보드는 슬라이드도 A4 도 아니다. check_board.py 가 따로 판정한다.

    문서와 같이 브랜드 적용 대상이 아니라 assets 원본을 그대로 본다 —
    blue-web.css 가 blue-report.css 의 색 토큰을 전제하므로 같은 폴더에서
    열어야 한다."""
    assets = os.path.join(SKILL, "assets")
    for name in BOARDS:
        path = os.path.join(assets, name)
        if not os.path.exists(path):
            log.fail(f"보드 {name}", "파일이 없다")
            continue
        r = run([sys.executable, os.path.join(SCRIPTS, "check_board.py"), path])
        print(r.stdout, end="")
        if r.stderr.strip():
            print(r.stderr, end="", file=sys.stderr)
        m = RESULT_RE.search(r.stdout)
        if not m:
            log.fail(f"보드 {name}", "check_board.py 가 결과 줄을 내지 않았다")
            continue
        ok, warn, fail = (int(x) for x in m.groups())
        detail = f"통과 {ok} · 주의 {warn} · 실패 {fail}"
        if fail or r.returncode != 0:
            log.fail(f"보드 {name}", detail)
        elif warn:
            log.warn(f"보드 {name}", detail)
        else:
            log.ok(f"보드 {name}", detail)


# ---------------------------------------------------------------------- PPTX

# ---------------------------------------------------------------------- 라이브 덱

def check_live(log, out_dir):
    """라이브 덱은 슬라이드도 보드도 아니다. check_live.py 가 따로 판정한다.

    두 번 본다. 견본(assets 원본)은 로고 자리가 자리표시자인 것이 맞고, 사람이
    실제로 받는 것은 apply_brand.py 를 거친 산출물이다. 견본만 보면 산출물에서만
    나는 결함을 놓친다 — `--single-file` 이 CSS 를 문서 안으로 넣자 CSS 주석의
    사용 예가 진짜 근거 JSON 보다 앞에 놓여 검사기가 오판한 일이 그랬다.

    산출물은 두 갈래다. `--single-file`(권장)은 덱마다, CSS·`fonts/` 를 옆에
    복사하는 연결형은 기준 덱 하나만 본다 — 복사 경로는 덱과 무관하게 같다."""
    targets = []
    for name, f in _LIVE_FILES.items():
        targets.append((f"라이브 {f}", os.path.join(ASSETS, f), None))
        targets.append((f"라이브 산출물 {name}",
                        os.path.join(out_dir, "live", f"{name}.html"), ["--single-file"]))
    targets.append(("라이브 연결형 standard",
                    os.path.join(out_dir, "live-linked", "standard.html"), []))

    for label, path, brand in targets:
        if brand is not None:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            deck = os.path.splitext(os.path.basename(path))[0]
            r = run([sys.executable, os.path.join(SCRIPTS, "apply_brand.py"),
                     "--brand", BRAND, "--deck", deck, "-o", path] + brand)
            if r.returncode != 0 or not os.path.exists(path):
                log.fail(label, "apply_brand.py 실패 — " + (r.stderr.strip().splitlines() or [""])[-1])
                continue
        elif not os.path.exists(path):
            log.fail(label, "파일이 없다")
            continue
        r = run([sys.executable, os.path.join(SCRIPTS, "check_live.py"), path])
        print(r.stdout, end="")
        if r.stderr.strip():
            print(r.stderr, end="", file=sys.stderr)
        m = RESULT_RE.search(r.stdout)
        if not m:
            log.fail(label, "check_live.py 가 결과 줄을 내지 않았다")
            continue
        ok, warn, fail = (int(x) for x in m.groups())
        detail = f"통과 {ok} · 주의 {warn} · 실패 {fail}"
        if fail or r.returncode != 0:
            log.fail(label, detail)
        elif warn:
            log.warn(label, detail)
        else:
            log.ok(label, detail)


def check_pptx(log, out_dir):
    if not shutil.which("node"):
        log.fail("PPTX 생성", "node 가 없다")
        return
    r = run(["node", os.path.join(SKILL, "pptx", "build.js"),
             "--brand", BRAND, "--out", out_dir])
    made = sorted(f for f in os.listdir(out_dir) if f.endswith(".pptx"))
    if r.returncode != 0:
        log.fail("PPTX 생성", (r.stderr.strip().splitlines() or ["build.js 실패"])[-1])
        return
    if len(made) != EXPECTED_PPTX:
        log.fail("PPTX 생성", f"{EXPECTED_PPTX}종이 나와야 하는데 {len(made)}종")
        return
    log.ok("PPTX 생성", f"{len(made)}종 — " + ", ".join(made))
    check_pptx_integrity(log, out_dir, made)


def check_pptx_integrity(log, out_dir, made):
    """생긴 파일이 실제로 열리는가. 파일 개수만 세면 깨진 것도 통과한다.

    .pptx 는 zip 이다. 표준 라이브러리로 열어 압축 무결성과 필수 부품,
    슬라이드 수를 본다. 슬라이드 수는 content.js 가 선언한 값과 견준다."""
    try:
        expect = expected_slide_counts()
    except Exception as e:
        log.warn("PPTX 무결성", f"기대 슬라이드 수를 읽지 못했다 — {e}")
        expect = {}

    bad = []
    for name in made:
        path = os.path.join(out_dir, name)
        try:
            with zipfile.ZipFile(path) as z:
                if z.testzip() is not None:
                    bad.append(f"{name} (압축 손상)")
                    continue
                names = z.namelist()
                if "[Content_Types].xml" not in names:
                    bad.append(f"{name} ([Content_Types].xml 없음)")
                    continue
                n = len([x for x in names
                         if x.startswith("ppt/slides/slide") and x.endswith(".xml")])
                want = expect.get(name)
                if n == 0:
                    bad.append(f"{name} (슬라이드 0장)")
                elif want is not None and n != want:
                    bad.append(f"{name} (슬라이드 {n}장 · content.js 는 {want}장)")
        except Exception as e:
            bad.append(f"{name} (열지 못함 — {e})")

    if bad:
        log.fail("PPTX 무결성", "; ".join(bad))
    else:
        total = sum(expect.get(n, 0) for n in made)
        log.ok("PPTX 무결성", f"{len(made)}종 모두 정상 · 슬라이드 합계 {total}장")

    check_pptx_slides(log, out_dir, made)


# 슬라이드 본문에 절대 나오면 안 되는 글자. 값이 아니라 자바스크립트가 흘린 흔적이다.
# progressSlide 가 footer(slide, {docTitle, page, dark}) 를 L.footer(sl, brand, page) 로
# 잘못 불러 쪽번호 자리에 undefined 가 찍혀 있었다. 인자 모양이 어긋나도 build.js 는
# 아무 소리 없이 성공하므로, 결과물 글자를 직접 봐야 잡힌다.
JS_LEAK = ("undefined", "NaN", "[object Object]")


def check_pptx_slides(log, out_dir, made):
    """만든 슬라이드의 글자와 그림을 실제로 들여다본다.

    두 가지를 본다.
      1. 자바스크립트가 흘린 글자(undefined 따위)가 지면에 찍히지 않았는가
      2. 브랜드 그림이 장마다 정확히 제 개수인가
         — 표지는 마크 1개, 나머지는 마크 + 배경 워터마크 2개.
         build.js 가 모든 장에 마크를 그리므로 생성기가 또 그리면 2번 겹친다.
         같은 자리에 같은 그림이라 열어 봐도 티가 잘 나지 않는다. 세는 편이 확실하다."""
    try:
        types = expected_slide_types()
    except Exception as e:
        log.warn("PPTX 지면", f"슬라이드 종류를 읽지 못했다 — {e}")
        return

    leaks, pics = [], []
    for name in made:
        want_types = types.get(name)
        if want_types is None:
            continue
        try:
            with zipfile.ZipFile(os.path.join(out_dir, name)) as z:
                slides = sorted(
                    (n for n in z.namelist()
                     if re.fullmatch(r"ppt/slides/slide\d+\.xml", n)),
                    key=lambda n: int(re.search(r"(\d+)\.xml$", n).group(1)))
                for i, member in enumerate(slides):
                    xml = z.read(member).decode("utf-8")
                    text = "".join(re.findall(r"<a:t>([^<]*)</a:t>", xml))
                    for word in JS_LEAK:
                        if word in text:
                            leaks.append(f"{name} {i+1}장: '{word}'")
                    n_pic = len(re.findall(r"<p:pic>", xml))
                    want = 1 if (i < len(want_types) and want_types[i] == "cover") else 2
                    if n_pic != want:
                        pics.append(f"{name} {i+1}장: 그림 {n_pic}개 (기대 {want}개)")
        except Exception as e:
            leaks.append(f"{name} (열지 못함 — {e})")

    for bad, ok_msg, fail_msg, hint in (
        (leaks, "PPTX 지면 글자 — undefined·NaN 이 찍힌 곳 없음",
         "PPTX 지면에 자바스크립트가 흘린 글자",
         "→ 그 슬라이드 생성기의 인자 모양을 layouts.js 의 선언과 맞춘다"),
        (pics, "PPTX 브랜드 그림 — 표지 마크 1 · 나머지 마크+워터마크 2",
         "PPTX 브랜드 그림 개수 이탈",
         "→ 생성기가 L.mark 를 부르지 않는다. build.js 가 모든 장에 그린다"),
    ):
        if bad:
            log.fail(fail_msg, "; ".join(bad[:6]))
            print(f"    · {hint}")
        else:
            log.ok(ok_msg.split(" — ")[0], ok_msg.split(" — ", 1)[1])


def _content_query(expr):
    script = (
        "const c = require(%s);\n"
        "const o = {};\n"
        "for (const v of Object.values(c)) if (v && v.slides) o[v.file] = %s;\n"
        "process.stdout.write(JSON.stringify(o));\n"
    ) % (json.dumps(os.path.join(SKILL, "pptx", "content.js")), expr)
    r = subprocess.run(["node", "-e", script], capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(r.stderr.strip()[:200])
    return json.loads(r.stdout)


def expected_slide_counts():
    """content.js 가 선언한 덱별 파일명과 슬라이드 수."""
    return _content_query("v.slides.length")


def expected_slide_types():
    """content.js 가 선언한 덱별 슬라이드 종류. 표지만 워터마크가 없다."""
    return _content_query("v.slides.map(s => s.type)")


# ---------------------------------------------------------------------- dist

def check_dist(log):
    """dist/ 가 소스에서 재생성한 것과 같은지 본다. 원본은 건드리지 않는다."""
    dist = os.path.join(SKILL, "dist")
    backup = {}
    try:
        for fname, _ in DIST_BUILDS:
            p = os.path.join(dist, fname)
            backup[fname] = open(p, "rb").read() if os.path.exists(p) else None

        for fname, extra in DIST_BUILDS:
            r = run([sys.executable, os.path.join(SCRIPTS, "build_single_file.py")] + extra)
            p = os.path.join(dist, fname)
            if r.returncode != 0 or not os.path.exists(p):
                log.fail(f"dist/{fname}", "재생성 실패 — " + (r.stderr.strip().splitlines() or [""])[-1])
                continue
            if open(p, "rb").read() == backup[fname]:
                log.ok(f"dist/{fname}", "소스와 일치")
            else:
                cmd = "python3 .claude/skills/blue-report/scripts/build_single_file.py " + " ".join(
                    "brand/hct/brand.json" if x == BRAND else x for x in extra)
                log.fail(f"dist/{fname}", f"소스와 다르다 — 다시 만들어 커밋한다: {cmd}")
    finally:
        for fname, data in backup.items():
            if data is not None:
                open(os.path.join(dist, fname), "wb").write(data)


# ------------------------------------------------------------------ 인코딩

def check_encoding(log):
    r = run(["git", "ls-files"])
    if r.returncode != 0:
        log.warn("한국어 인코딩", "git ls-files 실패 — 건너뜀")
        return
    bad = []
    for rel in r.stdout.splitlines():
        if os.path.splitext(rel)[1] not in SCAN_EXT:
            continue
        if rel in MOJIBAKE_EXEMPT or rel.replace("/", os.sep) in MOJIBAKE_EXEMPT:
            continue
        p = os.path.join(ROOT, rel)
        try:
            text = open(p, encoding="utf-8").read()
        except UnicodeDecodeError:
            bad.append(f"{rel} (UTF-8 아님)")
            continue
        hits = [m for m in MOJIBAKE if m in text]
        if hits:
            bad.append(f"{rel} ({' '.join(hits)})")
    if bad:
        log.fail("한국어 인코딩", "깨짐 의심 — " + "; ".join(bad[:5]))
    else:
        log.ok("한국어 인코딩", "UTF-8 · 깨짐 패턴 없음")


# ------------------------------------------------------------------ 계열색

def check_palette(log):
    """계열색 6종이 지면에서 갈리는지 본다.

    부서·제품처럼 순서가 없는 항목을 색으로 가르는 자리라, 두 색이 닿았을 때
    구별되지 않으면 그래프가 거짓말을 한다. 정상 시각만으로는 모자라서
    적록색각 이상(남성 8%)까지 모의해서 본다. 판정은 palette.py --cat 이 한다."""
    script = os.path.join(SKILL, "scripts", "palette.py")
    r = run([sys.executable, script, "--cat"])
    print(r.stdout, end="")
    if r.returncode == 0:
        worst = [l for l in r.stdout.splitlines() if "판정:" in l]
        detail = " · ".join(w.split("판정:")[-1].strip() for w in worst)
        log.ok("계열색", detail or "밝은면·다크면 6종 통과")
    else:
        bad = [l.strip() for l in r.stdout.splitlines() if "실패 —" in l]
        log.fail("계열색", bad[0].replace("실패 — ", "") if bad else "인접쌍이 갈리지 않는다")


# --------------------------------------------------------------- FCC/KC 템플릿

# 지시서 12장이 요구하는 판정 중 A4 공통 규칙(크기·대비·글자·머리말)은 check_doc.py
# 가 이미 본다. 여기서는 FCC/KC 템플릿에만 있는 규칙을 본다 — 중복 구현하지 않는다.
FCC_DIR = os.path.join(SKILL, "assets", "fcc-kc")


def fcc_templates():
    out = []
    for root, _, files in os.walk(os.path.join(FCC_DIR, "templates")):
        for f in sorted(files):
            if f.endswith(".html"):
                out.append(os.path.join(root, f))
    return sorted(out)


def check_fcc(log):
    """FCC/KC 템플릿 14종을 A4 규칙 + 제품 규칙으로 본다.

    제품 규칙은 지시서 12장에서 왔다. 요약하면 「이 지면이 무엇을 센 것인지,
    누가 말한 것인지, 시안인지」를 지면 스스로 밝히는가다."""
    files = fcc_templates()
    if not files:
        log.fail("FCC/KC 템플릿", "assets/fcc-kc/templates 가 비어 있다")
        return

    # 1) 재생성 대조 — 조립 스크립트 산출물과 저장소 파일이 같은가
    r = run([sys.executable, os.path.join(SCRIPTS, "build_fcc_templates.py"), "--check"])
    print(r.stdout, end="")
    if r.returncode == 0:
        log.ok("FCC/KC 재생성 대조", f"템플릿 {len(files)}종 — 스크립트 산출물과 일치")
    else:
        log.fail("FCC/KC 재생성 대조", "스크립트를 다시 돌려야 한다")

    # 2) A4 공통 9항목
    bad = []
    for f in files:
        rr = run([sys.executable, os.path.join(SCRIPTS, "check_doc.py"), f])
        tail = [l for l in rr.stdout.splitlines() if l.startswith("결과:")]
        if rr.returncode != 0:
            bad.append(f"{os.path.basename(f)} — {tail[0] if tail else '실패'}")
    if bad:
        log.fail("FCC/KC A4 규칙", f"{len(bad)}종 실패")
        for b in bad[:8]:
            print(f"    · {b}")
    else:
        log.ok("FCC/KC A4 규칙", f"{len(files)}종 모두 check_doc 9항목 통과")

    # 3) 제품 규칙 — 지면이 스스로 밝혀야 하는 것들
    import re as _re
    need = {
        "DESIGN FIXTURE 표시": lambda h, n: h.count("fk-fixture") >= n,
        "데이터 버전": lambda h, n: 'data-field="scope.sourceDataVersion"' in h,
        "분석 기간": lambda h, n: 'data-field="scope.appliedPeriod"' in h,
        "모집단 정의": lambda h, n: 'data-field="scope.populationDefinition"' in h,
        "레코드 단위": lambda h, n: 'data-field="scope.recordGrain"' in h,
        "커버리지 상태": lambda h, n: "fk-cov" in h,
        "서술 출처 구분": lambda h, n: "data-narrative-origin" in h or "fk-tele" in h,
        "근거·계보": lambda h, n: "fk-lineage" in h and "fk-evi" in h,
        "제품 서명": lambda h, n: "Blue Report" in h,
        "템플릿 식별자": lambda h, n: 'data-template-id="' in h,
    }
    miss = []
    for f in files:
        h = open(f, encoding="utf-8").read()
        # 꼬리말의 class="bd-pageno" 가 'class="bd-page' 를 접두로 갖는다.
        # 그냥 세면 쪽수가 두 배로 잡혀 도장 개수 판정이 헛돈다.
        pages = h.count('<section class="bd-page')
        for k, fn in need.items():
            if not fn(h, pages):
                miss.append(f"{os.path.basename(f)} — {k} 없음")
    if miss:
        log.fail("FCC/KC 제품 규칙", f"{len(miss)}건 누락")
        for m in miss[:10]:
            print(f"    · {m}")
    else:
        log.ok("FCC/KC 제품 규칙",
               f"{len(files)}종 모두 시안 표시·범위 계약·서술 출처·근거 계보를 지면에 밝힌다")

    # 4) fixture 가 계약(schema)을 지키는가. 스키마를 두고 검사하지 않으면 장식이 된다.
    #    ensure_deps 는 자동 설치가 막힌 환경(CI)에서 sys.exit 로 멈춘다. 그대로 두면
    #    점검 결과 요약이 아예 찍히지 않아 무엇이 문제인지 로그에서 보이지 않는다.
    #    여기서 받아 실패 한 줄로 바꾸고 나머지 검사는 계속 돌린다.
    sys.path.insert(0, SCRIPTS)
    try:
        from ensure_deps import need_jsonschema
        need_jsonschema()
        import jsonschema
    except SystemExit as e:
        log.fail("FCC/KC fixture 계약", "jsonschema 가 없다 — "
                 f"{sys.executable} -m pip install jsonschema")
        print(f"    · {str(e).splitlines()[0]}")
        jsonschema = None
    if jsonschema is None:
        return
    schema = json.load(open(os.path.join(FCC_DIR, "schemas", "report-model.schema.json"),
                            encoding="utf-8"))
    fxdir = os.path.join(FCC_DIR, "fixtures")
    fxs = sorted(f for f in os.listdir(fxdir) if f.endswith(".json"))
    fx_bad = []
    for f in fxs:
        try:
            jsonschema.validate(json.load(open(os.path.join(fxdir, f), encoding="utf-8")), schema)
        except jsonschema.ValidationError as e:
            fx_bad.append(f"{f} — {e.message[:90]}")
    if fx_bad:
        log.fail("FCC/KC fixture 계약", f"{len(fx_bad)}건 위반")
        for x in fx_bad[:8]:
            print(f"    · {x}")
    else:
        log.ok("FCC/KC fixture 계약", f"{len(fxs)}종 모두 schema 통과")

    # 5) 비밀값·로컬 경로·개인정보 패턴이 섞이지 않았는가
    LEAK = [(_re.compile(r"[A-Za-z]:\\\\"), "윈도 절대경로"),
            (_re.compile(r"/home/[a-z]+/"), "로컬 절대경로"),
            (_re.compile(r"(?i)(api[_-]?key|secret|password|token)\s*[:=]"), "비밀값 표기"),
            (_re.compile(r"\b\d{6}-\d{7}\b"), "주민등록번호 꼴"),
            (_re.compile(r"\b01[016-9]-?\d{3,4}-?\d{4}\b"), "휴대전화 번호")]
    leaks = []
    for f in files + [os.path.join(FCC_DIR, "fixtures", x) for x in
                      os.listdir(os.path.join(FCC_DIR, "fixtures"))]:
        h = open(f, encoding="utf-8").read()
        for rx, what in LEAK:
            if rx.search(h):
                leaks.append(f"{os.path.basename(f)} — {what}")
    if leaks:
        log.fail("FCC/KC 안전", f"{len(leaks)}건")
        for x in leaks[:8]:
            print(f"    · {x}")
    else:
        log.ok("FCC/KC 안전", "비밀값·로컬 경로·개인정보 패턴 없음")


# ------------------------------------------------------------------ 뷰어 축척

# 실제로 쓰이는 화면들. 16:9 정배수만 보면 이 검사가 하는 일이 없다 —
# 결함은 1920x1080 보다 작은 창에서만 났다.
VIEWPORTS = [
    ("FHD 16:9", 1920, 1080), ("노트북 16:9", 1366, 768), ("QHD 16:9", 2560, 1440),
    ("16:10", 1920, 1200), ("맥북 16:10", 1440, 900), ("울트라와이드 21:9", 3440, 1440),
    ("빔프로젝터 4:3", 1024, 768), ("5:4", 1280, 1024),
]

FIT_PROBE = """() => {
  const f = document.querySelector('.br-frame.is-active');
  if (!f) return { err: '활성 슬라이드가 없다' };
  const b = f.getBoundingClientRect();
  const hud = document.getElementById('hud');
  const h = hud ? hud.getBoundingClientRect() : null;
  const foot = f.querySelector('.br-footer');
  const fb = foot ? foot.getBoundingClientRect() : null;
  return {
    l: b.left, t: b.top, r: b.right, b: b.bottom, w: b.width, h: b.height,
    vw: innerWidth, vh: innerHeight,
    hudTop: h ? h.top : Infinity,
    footBottom: fb ? fb.bottom : null,
  };
}"""


def check_viewer(log):
    """창 크기가 달라져도 지면 전체가 화면 안에 들어오는가.

    덱 뷰어는 1920x1080 지면을 창에 맞춰 줄여 보여 준다. 그런데 브라우저는 컨테이너
    보다 큰 항목을 가운데가 아니라 시작 모서리에 붙이므로, 가운데 기준으로 줄이면
    지면이 오른쪽·아래로 밀린다. 1366x768 노트북에서 오른쪽 277px 가 화면 밖으로
    나가 있었고 16항목 검사는 전부 통과했다 — 검사기가 1920x1080 에서만 그렸기
    때문이다. 그래서 여러 해상도로 직접 띄워 본다.

    HUD 띠도 함께 본다. 지면이 띠 뒤로 들어가면 꼬리말(문서명·쪽번호)이 가려진다."""
    sys.path.insert(0, SCRIPTS)
    from ensure_deps import need_browser
    chrome = need_browser()
    from playwright.sync_api import sync_playwright

    deck = os.path.join(ASSETS, "deck-internal-report.html")
    url = "file://" + os.path.abspath(deck)
    bad = []
    with sync_playwright() as pw:
        br = pw.chromium.launch(executable_path=chrome)
        for name, w, h in VIEWPORTS:
            pg = br.new_page(viewport={"width": w, "height": h}, reduced_motion="reduce")
            pg.goto(url)
            pg.wait_for_timeout(700)
            pg.keyboard.press("ArrowRight")      # 꼬리말이 있는 장으로 넘긴다
            pg.keyboard.press("ArrowRight")
            pg.wait_for_timeout(400)
            r = pg.evaluate(FIT_PROBE)
            pg.close()
            if r.get("err"):
                bad.append(f"{name} {w}x{h} — {r['err']}")
                continue
            if (r["l"] < -1 or r["t"] < -1 or r["r"] > r["vw"] + 1 or r["b"] > r["vh"] + 1):
                bad.append(f"{name} {w}x{h} — 지면이 화면 밖으로 나간다 "
                           f"({r['l']:.0f},{r['t']:.0f}~{r['r']:.0f},{r['b']:.0f})")
            elif r["footBottom"] and r["footBottom"] > r["hudTop"] + 1:
                bad.append(f"{name} {w}x{h} — 꼬리말이 HUD 띠에 "
                           f"{r['footBottom'] - r['hudTop']:.0f}px 가린다")
        br.close()

    if bad:
        log.fail("뷰어 축척", f"{len(bad)}개 해상도에서 지면이 다 보이지 않는다")
        for t in bad:
            print(f"    · {t}")
    else:
        log.ok("뷰어 축척", f"해상도 {len(VIEWPORTS)}종 모두 지면 전체가 화면 안에 들어온다")

    check_present(log)


def check_present(log):
    """덱 9종이 전부 전체화면 발표 모드로 들어가고, 그 상태로 슬라이드를 넘기는가.

    HTML 덱은 발표에 쓴다. 발표 모드가 없으면 화면만 커지고 이전·다음·노트 버튼이
    그대로 남아 발표 자료가 아니라 편집 화면이 된다. 실제로 뷰어에 전체화면 코드가
    아예 없었고, 축척 검사 8종은 전부 통과했다 — 창 크기만 봤기 때문이다.

    네 가지를 본다. 하나라도 어기면 그 덱으로는 발표를 못 한다.
      1. F 키로 발표 모드에 들어가는가
      2. 그때 HUD 와 노트 띠가 완전히 사라지는가
      3. 지면이 세로 스크롤이 아니라 한 장으로 화면을 채우는가
      4. 그 상태로 좌우 키가 슬라이드를 넘기는가

    콘솔 예외도 함께 본다. 덱 2종에 #notes-text 가 빠져 있어 슬라이드를 넘길 때마다
    show() 가 던지고 있었고, 그래서 목록에서 발표로 넘어가는 길이 조용히 막혀 있었다.
    화면은 멀쩡해 보이므로 예외를 보지 않으면 잡히지 않는다."""
    sys.path.insert(0, SCRIPTS)
    from ensure_deps import need_browser
    chrome = need_browser()
    from playwright.sync_api import sync_playwright

    decks = sorted(f for f in os.listdir(ASSETS)
                   if f.startswith("deck-") and f.endswith(".html"))
    bad = []
    with sync_playwright() as pw:
        br = pw.chromium.launch(executable_path=chrome)
        for name in decks:
            errs = []
            pg = br.new_page(viewport={"width": 1440, "height": 900}, reduced_motion="reduce")
            pg.on("pageerror", lambda e, box=errs: box.append(str(e).splitlines()[0]))
            pg.goto("file://" + os.path.abspath(os.path.join(ASSETS, name)))
            pg.wait_for_timeout(700)
            # 목록(세로 나열)에서 시작해도 발표로 들어가야 한다. 사용자가 실제로
            # 겪은 순서다 — 전체 보기를 전체화면으로 알고 누른 뒤 발표하려 했다.
            pg.click("#all")
            pg.wait_for_timeout(250)
            pg.keyboard.press("f")
            pg.wait_for_timeout(400)
            st = pg.evaluate("""() => {
              const hud = document.getElementById('hud');
              const nt = document.getElementById('notes');
              const f = document.querySelector('.br-frame.is-active');
              const r = f ? f.getBoundingClientRect() : null;
              return {
                present: document.body.classList.contains('present'),
                all: document.body.classList.contains('all-mode--live'),
                hud: getComputedStyle(hud).display,
                notes: nt ? getComputedStyle(nt).display : 'none',
                scroll: document.documentElement.scrollHeight,
                win: innerHeight,
                w: r ? Math.round(r.width) : 0, h: r ? Math.round(r.height) : 0,
                vw: innerWidth, vh: innerHeight,
                pos: (document.getElementById('pos') || {}).textContent || '',
              };
            }""")
            pg.keyboard.press("ArrowRight")
            pg.wait_for_timeout(250)
            pos2 = pg.evaluate("() => (document.getElementById('pos')||{}).textContent || ''")
            pg.close()

            if not st["present"]:
                bad.append(f"{name} — F 키로 발표 모드에 들어가지 않는다")
                continue
            if st["all"]:
                bad.append(f"{name} — 발표 모드인데 목록(세로 나열)이 켜져 있다")
            if st["hud"] != "none" or st["notes"] != "none":
                bad.append(f"{name} — 발표 중에 HUD·노트가 보인다 "
                           f"(hud={st['hud']} notes={st['notes']})")
            # 세로 스크롤이 생기면 한 장짜리 지면이 아니다.
            if st["scroll"] > st["win"] + 2:
                bad.append(f"{name} — 발표 중에 세로 스크롤이 생긴다 "
                           f"({st['scroll']}px > {st['win']}px)")
            # 가로·세로 중 빡빡한 쪽에 맞추므로 한 변은 화면에 닿아야 한다.
            if not (abs(st["w"] - st["vw"]) <= 2 or abs(st["h"] - st["vh"]) <= 2):
                bad.append(f"{name} — 지면이 화면을 채우지 않는다 "
                           f"({st['w']}x{st['h']} · 화면 {st['vw']}x{st['vh']})")
            if st["pos"] and pos2 == st["pos"]:
                bad.append(f"{name} — 발표 중에 좌우 키가 넘기지 않는다 ({st['pos']})")
            if errs:
                bad.append(f"{name} — 콘솔 예외: {errs[0]}")
        br.close()

    if bad:
        log.fail("뷰어 발표 모드", f"덱 {len(decks)}종 중 {len(bad)}건 이상")
        for t in bad[:10]:
            print(f"    · {t}")
    else:
        log.ok("뷰어 발표 모드", f"덱 {len(decks)}종 모두 전체화면·한 장씩·버튼 없음")


# ------------------------------------------------------- HTML · PPTX 내용 동기화

def check_sync(log):
    """같은 내용이 assets/deck-*.html 과 pptx/content.js 두 곳에 있다.

    합치지 않기로 했다. HTML 을 손으로 고치는 것이 이 시스템의 사용법이고,
    HTML 을 생성물로 만들면 그 사용법이 사라진다. 대신 갈라짐을 기계가 잡는다.
    자세한 내용은 scripts/check_content_sync.py 머리말에 있다."""
    script = os.path.join(ROOT, "scripts", "check_content_sync.py")
    r = run([sys.executable, script])
    print(r.stdout, end="")
    if r.stderr.strip():
        print(r.stderr, end="", file=sys.stderr)
    first = (r.stdout.strip().splitlines() or [""])[0]
    detail = first.split("  ", 2)[-1].strip() if first else ""
    # 하위 스크립트가 자기 이름을 앞에 붙여 나온다. 표에서 두 번 찍지 않게 뗀다.
    for prefix in ("내용 동기화 — ", "내용 동기화 "):
        if detail.startswith(prefix):
            detail = detail[len(prefix):]
            break
    if r.returncode == 0:
        log.ok("내용 동기화", detail or "HTML 과 PPTX 일치")
    else:
        log.fail("내용 동기화", detail or "HTML 덱과 pptx/content.js 가 갈라졌다")


# ------------------------------------------------------------------ 배포

def check_plugin(log):
    """`plugin install` 이 성립하는 최소 조건을 본다."""
    mp = os.path.join(ROOT, ".claude-plugin", "marketplace.json")
    try:
        data = json.load(open(mp, encoding="utf-8"))
    except Exception as e:
        log.fail("마켓플레이스 매니페스트", f"{mp} 를 읽지 못했다 — {e}")
        return

    plugins = data.get("plugins") or []
    if not data.get("name") or not plugins:
        log.fail("마켓플레이스 매니페스트", "name 또는 plugins 가 비어 있다")
        return
    log.ok("마켓플레이스 매니페스트", f"{data['name']} · 플러그인 {len(plugins)}개")

    for entry in plugins:
        pname = entry.get("name", "(이름 없음)")
        src = entry.get("source", "")
        pdir = os.path.normpath(os.path.join(ROOT, src))
        if not os.path.isdir(pdir):
            log.fail(f"플러그인 {pname}", f"source 경로가 없다 — {src}")
            continue

        manifest = os.path.join(pdir, ".claude-plugin", "plugin.json")
        if not os.path.exists(manifest):
            log.fail(f"플러그인 {pname}", "plugin.json 이 없다")
            continue
        try:
            pj = json.load(open(manifest, encoding="utf-8"))
        except Exception as e:
            log.fail(f"플러그인 {pname}", f"plugin.json 이 깨졌다 — {e}")
            continue
        if pj.get("name") != pname:
            log.fail(f"플러그인 {pname}",
                     f"이름이 어긋난다 — marketplace {pname} · plugin.json {pj.get('name')}")
            continue

        skill = os.path.join(pdir, "SKILL.md")
        if not os.path.exists(skill):
            log.fail(f"플러그인 {pname}", "SKILL.md 가 없다")
            continue
        head = open(skill, encoding="utf-8").read(2048)
        if not head.startswith("---") or "\nname:" not in head:
            log.fail(f"플러그인 {pname}", "SKILL.md 머리말에 name 이 없다")
            continue

        log.ok(f"플러그인 {pname}", f"v{pj.get('version', '?')} · {src}")

    # 저장소 설정이 가리키는 마켓플레이스 이름이 실제와 같은가
    st = os.path.join(ROOT, ".claude", "settings.json")
    if os.path.exists(st):
        try:
            known = json.load(open(st, encoding="utf-8")).get("extraKnownMarketplaces", {})
        except Exception as e:
            log.fail("settings.json", f"읽지 못했다 — {e}")
            return
        if known and data.get("name") not in known:
            log.fail("settings.json",
                     f"등록된 이름 {list(known)} 이 marketplace.json 의 {data['name']} 와 다르다")
        else:
            log.ok("settings.json", "마켓플레이스 이름 일치")


# ------------------------------------------------------------------ 버전 올림

def _base_candidates():
    """기준 브랜치 후보를 우선순위대로 돌려준다.

    이름을 main 으로 못 박지 않는다. 저장소를 포크하거나 계정 사이로 옮기면
    기본 브랜치 이름이 달라진다. origin/HEAD 가 가리키는 기본 브랜치를 먼저
    보고, 없으면 이름으로 찾는다."""
    head = run(["git", "symbolic-ref", "--short", "refs/remotes/origin/HEAD"])
    if head.returncode == 0 and head.stdout.strip():
        yield head.stdout.strip()
    for name in ("origin/main", "main", "origin/main", "main"):
        yield name


def check_version(log):
    """스킬 폴더가 바뀌었는데 version 이 그대로면 실패.

    기준 브랜치를 찾지 못하는 환경(얕은 클론, 기본 브랜치가 없는 저장소)에서는
    실패가 아니라 주의로 넘긴다. 없는 것을 근거로 실패시키지 않는다."""
    # 이름만 맞는 브랜치를 잡으면 안 된다. 뿌리가 다른 동명 브랜치는 merge-base 가
    # 없어 검사가 통째로 건너뛰어진다 — 갈라진 지점이 실제로 나오는 후보를 고른다.
    base = ref = None
    for cand in _base_candidates():
        if run(["git", "rev-parse", "--verify", "--quiet", cand]).returncode != 0:
            continue
        # 갈라진 지점 기준으로 본다. 아직 커밋하지 않은 것도 포함하려고 작업 트리와 견준다.
        mb = run(["git", "merge-base", cand, "HEAD"])
        if mb.returncode == 0 and mb.stdout.strip():
            base, ref = cand, mb.stdout.strip()
            break
    if ref is None:
        log.warn("버전 올림", "기준 브랜치와의 갈라진 지점을 찾지 못해 건너뜀 "
                             "(얕은 클론이면 checkout 의 fetch-depth 를 0 으로 둔다)")
        return

    rel = os.path.relpath(SKILL, ROOT).replace(os.sep, "/")
    r = run(["git", "diff", "--name-only", ref, "--", rel])
    if r.returncode != 0:
        log.warn("버전 올림", "git diff 실패 — 건너뜀")
        return
    changed = [x for x in r.stdout.splitlines() if x.strip()]
    if not changed:
        log.ok("버전 올림", f"{rel} 변경 없음 · 기준 {base}")
        return

    manifest = f"{rel}/.claude-plugin/plugin.json"
    try:
        now = json.load(open(os.path.join(ROOT, manifest), encoding="utf-8")).get("version")
    except Exception as e:
        log.fail("버전 올림", f"plugin.json 을 읽지 못했다 — {e}")
        return
    r2 = run(["git", "show", f"{ref}:{manifest}"])
    if r2.returncode != 0:
        log.warn("버전 올림", "갈라진 지점에 plugin.json 이 없어 건너뜀")
        return
    try:
        before = json.loads(r2.stdout).get("version")
    except Exception as e:
        log.warn("버전 올림", f"갈라진 지점의 plugin.json 을 읽지 못했다 — {e}")
        return

    if now == before:
        log.fail("버전 올림",
                 f"스킬 파일 {len(changed)}개가 바뀌었는데 version 이 {now} 그대로 — "
                 f"{manifest} 와 CHANGELOG.md 를 올린다")
    else:
        log.ok("버전 올림", f"{before} → {now} · 스킬 파일 {len(changed)}개 변경 · 기준 {base}")


# ------------------------------------------------------------------------ main

def main():
    ap = argparse.ArgumentParser(description="블루 리포트 저장소 점검")
    ap.add_argument("--shots", metavar="폴더", help="슬라이드별 PNG 를 남길 폴더")
    ap.add_argument("--only", choices=["decks", "docs", "boards", "live", "fcc", "viewer", "pptx", "dist", "encoding", "plugin", "sync", "version", "palette"],
                    action="append", help="일부만 돌린다. 여러 번 줄 수 있다")
    ap.add_argument("--keep", metavar="폴더", help="만든 덱·PPTX 를 여기에 남긴다")
    a = ap.parse_args()

    only = set(a.only or ["decks", "docs", "boards", "live", "fcc", "viewer", "pptx", "dist", "encoding", "plugin", "sync", "version", "palette"])
    log = Log()

    if a.shots:
        os.makedirs(a.shots, exist_ok=True)

    tmp = a.keep or tempfile.mkdtemp(prefix="blue-report-verify-")
    os.makedirs(tmp, exist_ok=True)
    try:
        if "palette" in only:
            print("── 계열색 ──")
            check_palette(log)
        if "decks" in only:
            print("\n── 덱 ──")
            check_decks(log, tmp, a.shots)
        if "docs" in only:
            print("\n── A4 문서 ──")
            check_docs(log)
        if "boards" in only:
            print("\n── 웹 보드 ──")
            check_boards(log)
        if "live" in only:
            print("\n── 라이브 덱 ──")
            check_live(log, tmp)
        if "fcc" in only:
            print("\n── Blue Report FCC/KC 템플릿 ──")
            check_fcc(log)
        if "viewer" in only:
            print("\n── 뷰어 축척 ──")
            check_viewer(log)
        if "pptx" in only:
            print("\n── PPTX ──")
            check_pptx(log, tmp)
        if "dist" in only:
            print("\n── dist 재생성 대조 ──")
            check_dist(log)
        if "encoding" in only:
            print("\n── 한국어 인코딩 ──")
            check_encoding(log)
        if "plugin" in only:
            print("\n── 배포 매니페스트 ──")
            check_plugin(log)
        if "sync" in only:
            print("\n── HTML · PPTX 내용 동기화 ──")
            check_sync(log)
        if "version" in only:
            print("\n── 버전 올림 ──")
            check_version(log)
    finally:
        if not a.keep:
            shutil.rmtree(tmp, ignore_errors=True)

    return log.render()


if __name__ == "__main__":
    sys.exit(main())
