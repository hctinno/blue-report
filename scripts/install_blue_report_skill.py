#!/usr/bin/env python3
"""블루 리포트 스킬을 사용자 범위로 설치한다.

`.claude/skills/blue-report`는 이 저장소 안에서만 로드된다. 다른 프로젝트에서도 쓰려면
사용자 홈의 `~/.claude/skills/blue-report`로 복사해야 한다. 이 스크립트가 그 복사를
멱등하게 수행하고, 덮어쓰기 전에 기존 설치본을 백업한다.

    python3 scripts/install_blue_report_skill.py --check     # 상태만 확인, 변경 없음
    python3 scripts/install_blue_report_skill.py --dry-run   # 무엇이 바뀔지만 출력
    python3 scripts/install_blue_report_skill.py             # 설치 또는 갱신
    python3 scripts/install_blue_report_skill.py --target D:\\other\\.claude\\skills\\blue-report

설치 뒤 실행 중인 Claude Code는 새 스킬을 즉시 읽지 않는다. 세션을 새로 시작한다.
"""
import argparse
import filecmp
import hashlib
import os
import shutil
import sys
from datetime import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SOURCE = os.path.join(ROOT, ".claude", "skills", "blue-report")

# 재생성 가능한 산출물과 빌드 의존성은 설치본에 넣지 않는다.
#   node_modules — `cd pptx && npm install` 로 각자 받는다. 수백 개 파일이고
#                  Node 버전이 다르면 오히려 깨진다.
#   shots        — 점검 스크립트가 만드는 스크린샷
EXCLUDE_DIRS = {"__pycache__", "shots", "node_modules"}
EXCLUDE_FILES = {".gitignore"}


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def walk(base):
    """설치 대상 파일을 base 기준 상대 경로로 돌려준다."""
    out = []
    for dirpath, dirnames, filenames in os.walk(base):
        dirnames[:] = [d for d in dirnames if d not in EXCLUDE_DIRS]
        for fn in filenames:
            if fn in EXCLUDE_FILES:
                continue
            full = os.path.join(dirpath, fn)
            out.append(os.path.relpath(full, base))
    return sorted(out)


def default_target():
    return os.path.join(os.path.expanduser("~"), ".claude", "skills", "blue-report")


def diff(source, target):
    """(추가, 변경, 잔여) 목록을 낸다. 잔여 = 대상에만 있는 파일."""
    src_files = walk(source)
    tgt_files = walk(target) if os.path.isdir(target) else []
    add, change = [], []
    for rel in src_files:
        t = os.path.join(target, rel)
        if not os.path.exists(t):
            add.append(rel)
        elif sha256(os.path.join(source, rel)) != sha256(t):
            change.append(rel)
    extra = [r for r in tgt_files if r not in src_files]
    return add, change, extra


def main():
    ap = argparse.ArgumentParser(description="블루 리포트 스킬 사용자 범위 설치")
    ap.add_argument("--target", help=f"설치 경로 (기본 {default_target()})")
    ap.add_argument("--check", action="store_true", help="상태만 확인하고 종료. 변경하지 않는다")
    ap.add_argument("--dry-run", action="store_true", help="바뀔 내용만 출력하고 변경하지 않는다")
    a = ap.parse_args()

    if not os.path.isdir(SOURCE):
        sys.exit(f"오류: 원본이 없다 — {SOURCE}")

    target = os.path.abspath(a.target or default_target())
    add, change, extra = diff(SOURCE, target)

    print(f"원본: {SOURCE}")
    print(f"대상: {target}\n")

    if a.check:
        if not os.path.isdir(target):
            print("[미설치] 대상 경로가 없다.")
            print(f"설치: python3 {os.path.relpath(__file__, ROOT)}")
            sys.exit(1)
        if not add and not change:
            print(f"[일치] 파일 {len(walk(SOURCE))}개가 원본과 같다.")
            if extra:
                print(f"  참고: 대상에만 있는 파일 {len(extra)}개 — {', '.join(extra[:5])}")
            sys.exit(0)
        print(f"[불일치] 추가 필요 {len(add)}개 · 갱신 필요 {len(change)}개")
        for r in add:
            print(f"  추가  {r}")
        for r in change:
            print(f"  갱신  {r}")
        sys.exit(1)

    if not add and not change:
        print(f"[변경 없음] 파일 {len(walk(SOURCE))}개가 이미 최신이다.")
        return

    print(f"추가 {len(add)}개 · 갱신 {len(change)}개")
    for r in add:
        print(f"  추가  {r}")
    for r in change:
        print(f"  갱신  {r}")

    if a.dry_run:
        print("\n[dry-run] 아무것도 쓰지 않았다.")
        return

    # 기존 설치본이 있으면 통째로 백업한다. 덮어쓰기 전 복구 지점을 남긴다.
    if os.path.isdir(target) and (change or extra):
        stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        backup = f"{target}.backup-{stamp}"
        shutil.copytree(target, backup)
        print(f"\n백업: {backup}")

    for rel in add + change:
        src = os.path.join(SOURCE, rel)
        dst = os.path.join(target, rel)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copy2(src, dst)

    ok = all(filecmp.cmp(os.path.join(SOURCE, r), os.path.join(target, r), shallow=False)
             for r in walk(SOURCE))
    print(f"\n설치 완료: 파일 {len(walk(SOURCE))}개 · 내용 일치 {'예' if ok else '아니오'}")
    if not ok:
        sys.exit("오류: 복사 후 내용이 다르다. 대상 경로 권한을 확인한다.")
    print("실행 중인 Claude Code는 새 스킬을 즉시 읽지 않는다. 세션을 새로 시작한다.")


if __name__ == "__main__":
    main()
