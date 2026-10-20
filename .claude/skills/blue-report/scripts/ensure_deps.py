#!/usr/bin/env python3
"""필요한 것을 스스로 갖춘다.

사용자가 미리 설치할 것을 요구하지 않는다. 스크립트가 실행될 때 없는 것만 골라
직접 받아 온다. 이미 있으면 아무것도 하지 않고 아무 말도 하지 않는다.

    from ensure_deps import need_pillow, need_fonttools, need_browser, need_node_modules
    need_pillow()          # 로고 변환
    need_fonttools()       # 폰트 서브셋
    need_browser()         # 렌더 점검 · PDF
    need_node_modules(d)   # PPTX

자동 설치를 원하지 않으면 환경변수 BLUE_REPORT_NO_INSTALL=1 을 준다.
그때는 설치하지 않고 실행할 명령을 알려준 뒤 멈춘다.

    python3 ensure_deps.py --check    # 무엇이 있고 없는지만 본다
    python3 ensure_deps.py --all      # 전부 미리 갖춘다
"""
import importlib
import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SKILL = os.path.dirname(HERE)
PPTX_DIR = os.path.join(SKILL, "pptx")

# Playwright 가 설치한 것 외에 시스템에 있을 수 있는 브라우저
BROWSER_HINTS = [
    "/opt/pw-browsers/chromium-*/chrome-linux/chrome",
    "/usr/bin/chromium", "/usr/bin/chromium-browser", "/usr/bin/google-chrome",
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
]


def _no_install():
    return os.environ.get("BLUE_REPORT_NO_INSTALL", "").strip() not in ("", "0")


def _say(msg):
    print(f"[준비] {msg}", file=sys.stderr)


def _run(cmd, what):
    _say(f"{what} — {' '.join(cmd)}")
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        tail = (r.stderr or r.stdout or "").strip().splitlines()[-3:]
        sys.exit(f"[준비 실패] {what}\n  " + "\n  ".join(tail) +
                 f"\n  직접 실행: {' '.join(cmd)}")
    return r


def _pip(pkg, what):
    if _no_install():
        sys.exit(f"[준비 필요] {what}\n  실행: {sys.executable} -m pip install {pkg}\n"
                 f"  (BLUE_REPORT_NO_INSTALL 이 켜져 있어 자동 설치하지 않았다)")
    _run([sys.executable, "-m", "pip", "install", "--quiet", pkg], f"{what} 설치")


def need_python(module, pkg, what):
    """import 이름과 pip 이름이 다를 수 있어 둘 다 받는다."""
    try:
        importlib.import_module(module)
        return
    except ImportError:
        pass
    _pip(pkg, what)
    importlib.invalidate_caches()
    try:
        importlib.import_module(module)
    except ImportError:
        sys.exit(f"[준비 실패] {pkg} 를 설치했는데도 import 되지 않는다. "
                 f"파이썬 환경을 확인한다: {sys.executable}")


def need_pillow():
    need_python("PIL", "Pillow", "이미지 처리(Pillow)")


def need_jsonschema():
    """fixture 계약 검증. 스키마를 두고 검사하지 않으면 장식이 된다."""
    need_python("jsonschema", "jsonschema", "fixture 계약 검증(jsonschema)")


def need_fonttools():
    """폰트 서브셋. brotli 는 woff2 로 저장할 때 fontTools 가 부른다."""
    need_python("fontTools", "fonttools", "폰트 서브셋(fontTools)")
    need_python("brotli", "brotli", "woff2 압축(brotli)")


def find_browser():
    """쓸 수 있는 Chromium 실행 파일을 찾는다. 없으면 None."""
    import glob
    for pat in BROWSER_HINTS:
        for p in sorted(glob.glob(pat), reverse=True):
            if os.path.exists(p):
                return p
    for name in ("chromium", "chromium-browser", "google-chrome", "chrome"):
        p = shutil.which(name)
        if p:
            return p
    # Playwright 가 자기 경로에 받아 둔 것
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as pw:
            p = pw.chromium.executable_path
            if p and os.path.exists(p):
                return p
    except Exception:
        pass
    return None


def need_browser():
    """렌더 점검과 PDF 내보내기에 필요한 Chromium 을 갖춘다. 경로를 돌려준다."""
    need_python("playwright", "playwright", "브라우저 제어(Playwright)")
    p = find_browser()
    if p:
        return p
    if _no_install():
        sys.exit("[준비 필요] Chromium 이 없다.\n"
                 f"  실행: {sys.executable} -m playwright install chromium")
    _say("Chromium 내려받는 중 — 처음 한 번만, 150MB 정도 걸린다")
    _run([sys.executable, "-m", "playwright", "install", "chromium"], "Chromium 설치")
    p = find_browser()
    if not p:
        sys.exit("[준비 실패] Chromium 을 받았는데도 찾지 못했다.")
    return p


def need_node_modules(directory=PPTX_DIR):
    """PPTX 생성에 필요한 npm 패키지를 갖춘다."""
    if os.path.isdir(os.path.join(directory, "node_modules", "pptxgenjs")):
        return
    if not shutil.which("npm"):
        sys.exit("[준비 필요] npm 이 없다. Node.js 를 설치한다 — https://nodejs.org")
    if _no_install():
        sys.exit(f"[준비 필요] PPTX 생성기 의존성이 없다.\n  실행: cd {directory} && npm install")
    _run(["npm", "install", "--silent", "--prefix", directory], "PPTX 생성기 의존성 설치")
    if not os.path.isdir(os.path.join(directory, "node_modules", "pptxgenjs")):
        sys.exit(f"[준비 실패] npm install 후에도 pptxgenjs 가 없다: {directory}")


STATUS = [
    ("Pillow (로고 변환)", lambda: importlib.util.find_spec("PIL") is not None),
    ("fontTools (폰트 서브셋)", lambda: importlib.util.find_spec("fontTools") is not None),
    ("Playwright (렌더 점검 · PDF)", lambda: importlib.util.find_spec("playwright") is not None),
    ("Chromium (렌더 점검 · PDF)", lambda: find_browser() is not None),
    ("pptxgenjs (PPTX)", lambda: os.path.isdir(os.path.join(PPTX_DIR, "node_modules", "pptxgenjs"))),
]


def main():
    import importlib.util  # noqa: F401  (STATUS 에서 쓴다)
    args = sys.argv[1:]
    if "--all" in args:
        need_pillow(); need_fonttools(); need_browser(); need_node_modules()
        print("전부 준비됨")
        return
    print("의존성 상태")
    missing = 0
    for name, ok in STATUS:
        try:
            good = ok()
        except Exception:
            good = False
        missing += (not good)
        print(f"  {'있음' if good else '없음'}  {name}")
    if missing:
        print(f"\n{missing}개가 없다. 스크립트를 실행하면 필요한 것만 알아서 받는다.")
        print("미리 다 받으려면: python3 ensure_deps.py --all")
    sys.exit(1 if missing else 0)


if __name__ == "__main__":
    import importlib.util
    main()
