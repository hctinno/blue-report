#!/usr/bin/env python3
"""Codex 등 전역 지침 파일에 이 저장소를 가리키는 문단을 심는다.

    python3 scripts/install_codex_pointer.py --check     # 상태만 확인, 변경 없음
    python3 scripts/install_codex_pointer.py --dry-run   # 무엇이 바뀔지만 출력
    python3 scripts/install_codex_pointer.py             # 설치 또는 갱신
    python3 scripts/install_codex_pointer.py --target ~/.config/other-agent/AGENTS.md
    python3 scripts/install_codex_pointer.py --remove     # 심은 블록만 걷어낸다

왜 필요한가
-----------
Codex 는 `.claude/skills/` 를 인식하지 못하고, 어느 에이전트도 사용자의 GitHub 계정을
훑어 스킬을 찾아 오지 않는다. 이 저장소를 열었을 때만 `AGENTS.md` 가 읽힌다. 다른
프로젝트에서 "회사 양식으로 보고서" 라고 하면 템플릿은 시야에 없다.

그 구멍을 메우는 것이 전역 지침이다. "회사 양식 요청을 받으면 이 저장소를 받아라"
한 문단을 심어 두면 그때부터 에이전트가 스스로 가지러 온다.

**심는 것은 경로뿐이고 규격은 넣지 않는다.** 색값이나 덱 목록을 지침에 복사하면 그
순간부터 저장소와 갈라진다. 경로만 있으면 저장소가 바뀌어도 지침은 손댈 필요가 없다.

표식 블록 안만 관리한다. 사람이 직접 쓴 나머지 내용은 건드리지 않는다. 배경과 다른
경로는 `docs/AGENT_WIRING.md` 에 있다.

전역 지침 파일의 위치는 도구마다 다르고 바뀐다. 기본값이 네 도구와 맞는지 그 도구의
현재 문서에서 확인한다. 다르면 `--target` 으로 지정한다.
"""
import argparse
import os
import shutil
import sys
from datetime import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

START = "<!-- HCT-BLUE-REPORT:START -->"
END = "<!-- HCT-BLUE-REPORT:END -->"

# 저장소 주소와 기본 브랜치.
REPO = "https://github.com/hctinno/blue-report.git"
BRANCH = "main"

BLOCK = f"""{START}
## 사내 보고서·발표 자료 — 회사 공용 템플릿

사내 보고서·발표자료·덱·슬라이드·회의록·공지·매뉴얼·보드·대시보드·현황판을 회사 양식이나
템플릿으로 만들라는 요청을 받으면, 새 스타일을 만들지 말고 먼저 아래를 받는다.

    git clone -b {BRANCH} {REPO}

이미 받아 둔 것이 있으면 `git pull` 로 갱신한다. 그다음 그 저장소의
`docs/CODEX_DECK_PROMPT.md` 를 전부 읽고 그대로 수행한다. 그 문서에 슬라이드 덱 12종,
A4 문서 4종, 웹 보드 5종의 목록과 각각의 `--deck` 이름, 금지 사항, 검사 절차가 있다.

덱과 A4 문서와 웹 보드는 지면 크기도 글자 하한도 검사기도 서로 다르다. 바꿔 쓸 수 없으므로
용도가 분명하지 않으면 먼저 묻는다.

산출물은 그 저장소의 `decks-out/` 에 넣는다. 완료라고 말하기 전에 그 저장소의 검사
스크립트를 돌리고 결과를 함께 제시한다. 실패가 0 이 아니면 완료가 아니다.
{END}"""


def default_target():
    """Codex 홈의 전역 지침 파일. CODEX_HOME 이 있으면 그것을 따른다."""
    home = os.environ.get("CODEX_HOME") or os.path.join(os.path.expanduser("~"), ".codex")
    return os.path.join(home, "AGENTS.md")


def split(text):
    """(앞, 블록, 뒤). 블록이 없으면 가운데가 빈 문자열이다."""
    i = text.find(START)
    if i < 0:
        return text, "", ""
    j = text.find(END, i)
    if j < 0:
        # 시작만 있고 끝이 없다. 사람이 잘라 먹었거나 편집이 꼬인 것이다.
        # 짐작으로 나머지를 다 먹지 않고 멈춘다.
        sys.exit(f"오류: {START} 는 있는데 {END} 가 없다. 대상 파일을 손으로 고친 뒤 다시 실행한다.")
    return text[:i], text[i:j + len(END)], text[j + len(END):]


def compose(before, after):
    """블록을 끼운 전체 본문. 앞뒤에 빈 줄 하나씩만 둔다."""
    head = before.rstrip("\n")
    tail = after.lstrip("\n")
    parts = ([head, ""] if head else []) + [BLOCK] + (["", tail] if tail else [""])
    return "\n".join(parts).rstrip("\n") + "\n"


def main():
    ap = argparse.ArgumentParser(description="전역 지침에 블루 리포트 저장소 지시문을 심는다")
    ap.add_argument("--target", help=f"지침 파일 경로 (기본 {default_target()})")
    ap.add_argument("--check", action="store_true", help="상태만 확인하고 종료. 변경하지 않는다")
    ap.add_argument("--dry-run", action="store_true", help="바뀔 내용만 출력하고 변경하지 않는다")
    ap.add_argument("--remove", action="store_true", help="심어 둔 블록만 걷어낸다")
    a = ap.parse_args()

    target = os.path.abspath(os.path.expanduser(a.target or default_target()))
    exists = os.path.isfile(target)
    current = ""
    if exists:
        with open(target, encoding="utf-8") as f:
            current = f.read()

    before, block, after = split(current)
    print(f"대상: {target}")
    print(f"상태: {'파일 없음' if not exists else ('블록 있음' if block else '블록 없음')}\n")

    if a.remove:
        if not block:
            print("[변경 없음] 걷어낼 블록이 없다.")
            return
        # 앞뒤를 그냥 이으면 블록이 갈라 놓았던 두 문단이 붙는다. 제목 둘이
        # 맞닿으면 마크다운이 달라지므로 양쪽이 다 있을 때만 빈 줄을 남긴다.
        head, tail = before.strip("\n"), after.strip("\n")
        new = "\n\n".join(p for p in (head, tail) if p)
        new = new + "\n" if new else ""
        if a.dry_run:
            print("[dry-run] 블록을 걷어낼 예정. 아무것도 쓰지 않았다.")
            return
        backup(target)
        write(target, new)
        print("블록을 걷어냈다. 나머지 내용은 그대로다.")
        return

    new = compose(before, after)

    if a.check:
        if block == BLOCK:
            print("[최신] 심어 둔 블록이 현재 판과 같다.")
            sys.exit(0)
        print("[불일치] 블록이 없거나 낡았다.")
        print(f"설치: python3 {os.path.relpath(__file__, ROOT)}")
        sys.exit(1)

    if block == BLOCK:
        print("[변경 없음] 이미 최신이다.")
        return

    print("갱신" if block else "추가", f"— 블록 {len(BLOCK.splitlines())}줄")
    if a.dry_run:
        print("\n" + BLOCK)
        print("\n[dry-run] 아무것도 쓰지 않았다.")
        return

    if exists:
        backup(target)
    write(target, new)

    with open(target, encoding="utf-8") as f:
        _, got, _ = split(f.read())
    if got != BLOCK:
        sys.exit("오류: 쓴 뒤 내용이 다르다. 대상 경로 권한을 확인한다.")
    print(f"\n설치 완료: {target}")
    print("실행 중인 세션은 새 지침을 즉시 읽지 않는다. 세션을 새로 시작한다.")


def backup(path):
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    dst = f"{path}.backup-{stamp}"
    shutil.copy2(path, dst)
    print(f"백업: {dst}")


def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)


if __name__ == "__main__":
    main()
