#!/usr/bin/env python3
"""프리텐다드 가변 폰트를 잘라 assets/fonts/ 에 넣는다.

원본은 93MB 짜리 npm 패키지다. 그대로 저장소에 넣을 수 없고, 그렇다고 CDN 을
걸 수도 없다 — Artifact 로 발행하면 폰트를 fonts.gstatic.com 에서만 받을 수 있어
jsdelivr 링크는 조용히 차단된다. 그래서 필요한 글자만 잘라 저장소에 넣고,
발행할 때는 build_single_file.py 가 data URI 로 본문에 심는다.

## 왜 가변 폰트 한 벌인가

정적 폰트로 하면 굵기마다 한 벌씩 필요하다. 이 시스템은 300·400·500·600·700·900
여섯 굵기를 쓰므로 여섯 벌 = 965KB 다. 가변 폰트는 한 벌에 45~930 전 구간이
들어 있어 425KB 로 끝난다. 굵기를 하나 더 쓰기로 해도 파일이 늘지 않는다.

## 무슨 글자를 남기나

KS X 1001 완성형 한글 2,350자 + ASCII + 호환 자모 + 문서 기호.
한글 음절 전체(11,172자)를 넣으면 1,678KB 로 네 배가 된다. 사내 보고서에
쓰이는 한글은 KS X 1001 안에서 끝난다 — 옛한글이나 희귀 음절이 필요하면
--full 로 전체를 넣는다.

## 무슨 기능을 남기나

tnum(고정폭 숫자)을 반드시 남긴다. .br-num 이 font-variant-numeric:tabular-nums
를 쓰므로 이게 빠지면 표의 숫자 자리가 흔들린다. 처음에 --layout-features='' 로
잘랐다가 이걸 날려 먹었다. kern 도 남긴다.

    python3 scripts/make_font_subset.py              # 받아서 자른다
    python3 scripts/make_font_subset.py --check      # 지금 것이 규격에 맞는지만 본다
    python3 scripts/make_font_subset.py --full       # 한글 음절 전체
"""
import argparse
import io
import json
import os
import sys
import tarfile
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from ensure_deps import need_fonttools  # noqa: E402

SKILL = os.path.dirname(HERE)
FONT_DIR = os.path.join(SKILL, "assets", "fonts")
OUT = os.path.join(FONT_DIR, "PretendardVariable.subset.woff2")
LICENSE_OUT = os.path.join(FONT_DIR, "LICENSE-Pretendard.txt")

REGISTRY = "https://registry.npmjs.org/pretendard"
SRC_IN_TAR = "package/dist/web/variable/woff2/PretendardVariable.woff2"
LICENSE_IN_TAR = "package/dist/LICENSE.txt"

# 남길 조판 기능. tnum 이 빠지면 표의 숫자 자리가 흔들린다.
FEATURES = "ccmp,locl,kern,mark,mkmk,calt,liga,clig,tnum,case,frac"

# 기호 — 이 시스템이 실제로 지면에 찍는 것만. 눈에 보이지 않는 글자는 넣지 않는다.
SYMBOLS = {
    0x00A0, 0x00B0, 0x00B1, 0x00B7, 0x00D7, 0x00A3, 0x00A5,
    0x2013, 0x2014, 0x2018, 0x2019, 0x201C, 0x201D, 0x2022, 0x2026,
    0x2032, 0x2033, 0x203B, 0x20A9, 0x20AC,
    0x2190, 0x2192, 0x25A0, 0x25B2, 0x25BC, 0x25CF,
    0x2605, 0x2606, 0x2713,
}
# 프리텐다드에 U+2500(─ 괘선)은 없다. HTML 주석의 구분선에나 쓰는 글자라
# 지면에 나오지 않지만, --check 가 잡아 주지 않았으면 모르고 넘어갔을 것이다.
# 괘선이 필요하면 글자가 아니라 border 로 긋는다.


def ksx1001(cp):
    """KS X 1001 완성형 한글인가.

    파이썬의 euc-kr 코덱은 실제로는 CP949(UHC)라 11,172자를 전부 인코딩한다.
    그래서 인코딩 성공 여부로는 가릴 수 없고, 두 바이트가 KS X 1001 한글
    영역(0xB0A1~0xC8FE)에 들어오는지를 직접 본다.
    """
    try:
        b = chr(cp).encode("euc-kr")
    except UnicodeEncodeError:
        return False
    return len(b) == 2 and 0xB0 <= b[0] <= 0xC8 and 0xA1 <= b[1] <= 0xFE


def codepoints(full=False):
    cps = set(range(0x0020, 0x007F))          # ASCII
    cps |= set(range(0x3131, 0x3164))         # 호환 자모 (ㄱ ㄴ ㄷ …)
    cps |= SYMBOLS
    if full:
        cps |= set(range(0xAC00, 0xD7A4))     # 한글 음절 전체 11,172자
    else:
        cps |= {c for c in range(0xAC00, 0xD7A4) if ksx1001(c)}
    return cps


def fetch_source():
    """npm 레지스트리에서 가변 폰트 원본과 라이선스를 꺼낸다."""
    print("프리텐다드 내려받는 중 — 패키지가 69MB 라 조금 걸린다", file=sys.stderr)
    with urllib.request.urlopen(REGISTRY, timeout=60) as r:
        meta = json.load(r)
    version = meta["dist-tags"]["latest"]
    info = meta["versions"][version]
    if info.get("license") != "OFL-1.1":
        raise SystemExit(f"라이선스가 바뀌었다: {info.get('license')}. 재배포 조건을 다시 확인한다.")
    with urllib.request.urlopen(info["dist"]["tarball"], timeout=300) as r:
        blob = r.read()
    with tarfile.open(fileobj=io.BytesIO(blob), mode="r:gz") as tar:
        font = tar.extractfile(SRC_IN_TAR).read()
        lic = tar.extractfile(LICENSE_IN_TAR).read()
    print(f"프리텐다드 {version} · 원본 {len(font)/1024:.0f}KB", file=sys.stderr)
    return version, font, lic


def subset(src_bytes, cps):
    from fontTools import subset as ft
    from fontTools.ttLib import TTFont

    font = TTFont(io.BytesIO(src_bytes))
    opts = ft.Options()
    opts.layout_features = FEATURES.split(",")
    opts.flavor = "woff2"
    opts.desubroutinize = False
    sub = ft.Subsetter(options=opts)
    sub.populate(unicodes=cps)
    sub.subset(font)
    buf = io.BytesIO()
    font.flavor = "woff2"
    font.save(buf)
    return buf.getvalue()


def describe(path):
    """만들어진 폰트가 규격을 지키는지 본다. 크기만 보고 넘어가지 않는다."""
    from fontTools.ttLib import TTFont

    f = TTFont(path)
    gsub = sorted({r.FeatureTag for r in f["GSUB"].table.FeatureList.FeatureRecord}) if "GSUB" in f else []
    gpos = sorted({r.FeatureTag for r in f["GPOS"].table.FeatureList.FeatureRecord}) if "GPOS" in f else []
    axes = [(a.axisTag, a.minValue, a.maxValue) for a in f["fvar"].axes] if "fvar" in f else []
    cmap = set(f.getBestCmap())
    return {
        "kb": os.path.getsize(path) / 1024,
        "glyphs": len(f.getGlyphOrder()),
        "gsub": gsub, "gpos": gpos, "axes": axes, "cmap": cmap,
    }


def check(path, cps):
    """실패를 0/1 로 돌려준다. verify_repo.py 가 이걸 부른다."""
    if not os.path.isfile(path):
        print(f"실패 — 폰트가 없다: {path}")
        return 1
    d = describe(path)
    fails = []
    if "tnum" not in d["gsub"]:
        fails.append("tnum 이 없다 — .br-num 의 고정폭 숫자가 깨진다")
    if "kern" not in d["gpos"]:
        fails.append("kern 이 없다")
    if not any(a[0] == "wght" for a in d["axes"]):
        fails.append("가변 굵기 축(wght)이 없다 — 굵기마다 다른 파일이 필요해진다")
    else:
        lo, hi = next((a[1], a[2]) for a in d["axes"] if a[0] == "wght")
        if lo > 300 or hi < 900:
            fails.append(f"굵기 축이 {lo:.0f}~{hi:.0f} 라 300~900 을 못 덮는다")
    missing = cps - d["cmap"]
    if missing:
        sample = " ".join(f"U+{c:04X}" for c in sorted(missing)[:8])
        fails.append(f"글자 {len(missing)}자가 빠졌다: {sample}")
    if not os.path.isfile(LICENSE_OUT):
        fails.append("OFL 라이선스 원문이 없다 — 재배포 조건이다")

    axes = " ".join(f"{t} {lo:.0f}~{hi:.0f}" for t, lo, hi in d["axes"])
    print(f"  {d['kb']:.0f}KB · 글리프 {d['glyphs']} · {axes} · tnum·kern 유지")
    for f_ in fails:
        print(f"  실패 — {f_}")
    return 1 if fails else 0


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--full", action="store_true", help="한글 음절 11,172자 전체 (파일이 네 배가 된다)")
    ap.add_argument("--check", action="store_true", help="지금 있는 폰트가 규격에 맞는지만 본다")
    a = ap.parse_args()

    cps = codepoints(a.full)
    if a.check:
        need_fonttools()
        sys.exit(check(OUT, cps))

    need_fonttools()
    version, src, lic = fetch_source()
    os.makedirs(FONT_DIR, exist_ok=True)
    out = subset(src, cps)
    open(OUT, "wb").write(out)
    open(LICENSE_OUT, "wb").write(lic)

    hangul = len([c for c in cps if 0xAC00 <= c <= 0xD7A3])
    print(f"\n{os.path.relpath(OUT, SKILL)}")
    print(f"  프리텐다드 {version} · 한글 {hangul}자 · 총 {len(cps)} 코드포인트")
    sys.exit(check(OUT, cps))


if __name__ == "__main__":
    main()
