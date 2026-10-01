#!/usr/bin/env python3
"""블루 리포트를 Claude 계정 스킬로 올릴 zip 묶음을 만든다.

    python3 scripts/build_account_skill_bundle.py            # decks-out/ 에 만든다
    python3 scripts/build_account_skill_bundle.py --check    # 만들지 않고 내용만 본다
    python3 scripts/build_account_skill_bundle.py --out 경로

왜 따로 만드는가
----------------
스킬을 쓰는 길이 셋인데 셋이 서로 다른 것을 필요로 한다.

  1. 저장소 안에서       `.claude/skills/blue-report` 가 그대로 로드된다. 아무것도 안 한다.
  2. Claude Code 플러그인  마켓플레이스가 `main` 을 통째로 받아 간다. 이 묶음이 필요 없다.
  3. Claude 계정 스킬      claude.ai 에 zip 하나를 올린다. 그러면 그 계정의 모든 세션
                          (claude.ai 대화 · Claude Code · 원격 세션)에 동기화된다.

3번만 저장소 밖에서 홀로 돌아야 한다. 그래서 두 가지를 손본다.

  - 브랜드 자산을 안으로 넣는다. 저장소에서는 `brand/hct/` 가 루트에 있고 스킬이
    `../../../brand/hct/` 로 가리킨다. 홀로 설치되면 그 경로가 없다. 묶음 안에
    `brand/hct/` 를 복사해 넣고 INSTALL.md 에 바뀐 경로를 적는다.
  - 재생성 가능한 것을 뺀다. `node_modules` 는 `npm install` 로 각자 받고, `dist/` 는
    사람에게 건네는 단일 파일이라 스킬이 읽지 않는다. 둘을 빼면 12MB 가 2MB 아래로 준다.

만든 zip 은 저장소에 커밋하지 않는다. `decks-out/` 은 gitignore 돼 있다.
내용은 `.claude/skills/blue-report` 에서 그때그때 뜨므로 낡을 일이 없다.
"""
import argparse
import io
import json
import os
import sys
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILL = os.path.join(ROOT, ".claude", "skills", "blue-report")
BRAND = os.path.join(ROOT, "brand", "hct")
NAME = "blue-report"

# 받는 쪽에서 다시 만들 수 있는 것은 넣지 않는다. 용량이 아니라 낡음이 문제다 —
# 묶음 안에 굳은 산출물이 있으면 원본과 갈라져도 아무도 모른다.
SKIP_DIRS = {"__pycache__", "node_modules", "shots", "dist"}
SKIP_FILES = {".gitignore", ".DS_Store"}

INSTALL_MD = """# 설치본 안내

이 폴더는 `blue-report` 저장소의 `.claude/skills/blue-report` 를 계정 스킬로
올리려고 뜬 것이다. 저장소 판과 두 가지가 다르다.

## 1. 브랜드 자산이 안에 있다

저장소에서는 루트의 `brand/hct/` 를 `../../../brand/hct/` 로 가리킨다. 홀로 설치되면
그 경로가 없으므로 이 폴더 안에 복사해 넣었다. 명령에 쓸 경로가 바뀐다.

    저장소 판   --brand ../../../brand/hct/brand.json
    설치본      --brand brand/hct/brand.json

## 2. 재생성 가능한 것이 빠져 있다

| 뺀 것 | 다시 만드는 법 |
|---|---|
| `pptx/node_modules/` | `cd pptx && npm install` |
| `dist/` | `python3 scripts/build_single_file.py` |

PPTX 를 만들 일이 없으면 `npm install` 은 하지 않아도 된다. HTML 슬라이드와 A4 문서,
FCC/KC 보고서는 추가 설치 없이 그대로 만들어진다.

## 원본

<https://github.com/hctinno/blue-report>

규격서는 이 폴더의 `README.md` 다. 고칠 일이 생기면 이 설치본이 아니라 저장소를
고치고 묶음을 다시 뜬다 — 설치본을 고치면 다음 판올림에 덮인다.
"""


def walk(base):
    """묶음에 넣을 파일을 (실제 경로, zip 안 경로) 로 돌려준다."""
    for dirpath, dirnames, filenames in os.walk(base):
        dirnames[:] = sorted(d for d in dirnames if d not in SKIP_DIRS)
        for fn in sorted(filenames):
            if fn in SKIP_FILES:
                continue
            src = os.path.join(dirpath, fn)
            yield src, os.path.relpath(src, base).replace(os.sep, "/")


def version():
    p = os.path.join(SKILL, ".claude-plugin", "plugin.json")
    with io.open(p, encoding="utf-8") as f:
        return json.load(f)["version"]


def collect():
    """(zip 안 경로, 실제 경로) 목록. 스킬 본체 + 브랜드 자산 + 설치 안내."""
    items = [(f"{NAME}/{rel}", src) for src, rel in walk(SKILL)]
    if os.path.isdir(BRAND):
        items += [(f"{NAME}/brand/hct/{rel}", src) for src, rel in walk(BRAND)]
    return sorted(items)


def main():
    ap = argparse.ArgumentParser(description="계정 스킬 업로드용 zip 묶음")
    ap.add_argument("--out", default=os.path.join(ROOT, "decks-out"),
                    help="묶음을 놓을 폴더 (기본 decks-out/)")
    ap.add_argument("--check", action="store_true", help="만들지 않고 내용만 본다")
    a = ap.parse_args()

    if not os.path.isfile(os.path.join(SKILL, "SKILL.md")):
        print(f"SKILL.md 를 찾지 못했다: {SKILL}", file=sys.stderr)
        return 1

    items = collect()
    raw = sum(os.path.getsize(src) for _, src in items)
    ver = version()
    print(f"블루 리포트 v{ver} · 파일 {len(items)}개 · 원본 {raw/1024/1024:.1f}MB")
    if not os.path.isdir(BRAND):
        print("  주의: brand/hct/ 가 없다 — 설치본에서 브랜드 적용이 안 된다")

    if a.check:
        for arc, _ in items[:12]:
            print(f"  {arc}")
        if len(items) > 12:
            print(f"  … 그 밖 {len(items)-12}개")
        return 0

    os.makedirs(a.out, exist_ok=True)
    out = os.path.join(a.out, f"{NAME}-skill-v{ver}.zip")
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for arc, src in items:
            z.write(src, arc)
        z.writestr(f"{NAME}/INSTALL.md", INSTALL_MD)

    # 만든 것이 실제로 열리고 SKILL.md 가 제자리에 있는가. 크기만 보면 빈 zip 도 통과한다.
    with zipfile.ZipFile(out) as z:
        if z.testzip() is not None:
            print("만든 zip 이 손상됐다", file=sys.stderr)
            return 1
        names = z.namelist()
        for must in (f"{NAME}/SKILL.md", f"{NAME}/README.md", f"{NAME}/INSTALL.md"):
            if must not in names:
                print(f"묶음에 {must} 가 없다", file=sys.stderr)
                return 1

    kb = os.path.getsize(out) / 1024
    print(f"\n생성: {out}  ({kb:.0f}KB · 파일 {len(names)}개)")
    print("\nclaude.ai → Settings → Capabilities → Skills 에서 이 zip 을 올린다.")
    print("올린 뒤 그 계정의 모든 세션에 동기화된다 — Claude Code 는 세션을 새로 연다.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
