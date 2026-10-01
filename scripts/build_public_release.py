#!/usr/bin/env python3
"""비공개 저장소의 현재 HEAD 에서 공개본 트리를 만든다.

    python3 scripts/build_public_release.py                    # 빌드하고 검증만
    python3 scripts/build_public_release.py --out /tmp/pub     # 자리 지정
    python3 scripts/build_public_release.py --commit           # 단일 커밋까지
    python3 scripts/build_public_release.py --commit --push    # 공개 저장소로 push

왜 필요한가
----------
공개본은 비공개본에서 **템플릿·스크립트·문서만** 뽑아 낸 것이다. 실명·조직명·
사내 계획·구 계정 핸들을 걷어내고, 파일 이름에 박힌 사내 제품명을 바꾸고,
공개용 문서 세 벌을 덮어쓴다. 손으로 하면 열댓 단계다 — 한 번은 해냈지만
판올림마다 되풀이하면 어느 회차에서 반드시 하나를 빠뜨린다.

빠뜨렸을 때 대가가 크다. 공개 push 는 되돌릴 수 없다 — 포크·캐시·코드검색
색인이 몇 분 안에 잡는다. 그래서 이 스크립트는 **유출 검사에서 하나라도
걸리면 커밋도 push 도 하지 않고 죽는다.**

무엇을 하는가
------------
    1. 현재 HEAD 를 빈 폴더로 뽑는다 (작업 트리의 미커밋 변경은 들어가지 않는다)
    2. EXCLUDE 경로를 지운다
    3. RENAME 경로의 이름을 바꾼다
    4. COPY_DIRS 를 복사해 넣고 OVERLAY 파일을 덮어쓴다
    5. 치환표 다섯 벌을 적용한다 (사내 고유어 · 브랜드 · 계정 · 브랜치 · 이력 문장)
    6. README 꼬리의 「이력」절을 라이선스 절로 바꾼다
    7. 공개본 판번호를 plugin.json 에 박고 마켓플레이스 소유자를 바꾼다
    8. dist/ 세 벌을 다시 만든다
    9. verify_repo.py 를 돌린다
   10. 유출 검사 — DENY 가 0, EXPECT 가 1 이상이어야 한다

규칙은 전부 `public/config.py` 에 있다. 이 파일은 순서만 안다.
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "public"))
import config as C  # noqa: E402

TEXT_EXT = (".md", ".html", ".css", ".js", ".py", ".json", ".yml", ".yaml", ".txt")
SKIP_DIRS = {".git", "node_modules", "__pycache__"}

# dist/ 는 치환 대상에서 뺀다. 로고가 base64 로 박혀 있어 'HCT' 같은 짧은
# 문자열이 그림 데이터 한가운데에서도 걸린다 — 실제로 'HCTyVEpv' 가 있다.
# 8단계에서 assets/ 로부터 다시 만들므로 손댈 이유도 없다.
# brand/hct/ 도 뺀다. 여기 값은 실제 브랜드 설정이라 바꿀 것이 없고, 잘못 건드리면
# brand.json 이 없는 로고 파일을 가리켜 빌드가 죽는다 — 실제로 한 번 죽였다.
NO_SUBST = ("/dist/", "/brand/hct/")


class Step:
    """단계마다 한 줄씩 남긴다. 어디서 틀어졌는지 로그만 보고 알 수 있어야 한다."""

    def __init__(self):
        self.n = 0

    def __call__(self, title, detail=""):
        self.n += 1
        print(f"  {self.n:2}. {title:<34} {detail}")


step = Step()


def run(cmd, cwd=None, check=True):
    r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    if check and r.returncode != 0:
        print(r.stdout)
        print(r.stderr, file=sys.stderr)
        raise SystemExit(f"실패: {' '.join(cmd)}")
    return r


def walk_text(root):
    """치환 대상 텍스트 파일만 돌려준다.

    overlay 파일은 뺀다. 손으로 쓴 공개용 문서라 이미 공개본 기준으로 쓰여
    있고, 치환표를 한 번 더 먹이면 멀쩡한 문장이 망가진다 — 실제로 CLAUDE.md 의
    「brand/hct 가 기본이고」가 「brand/sample 가 기본이고」로 뒤집혔다."""
    overlay = {"/" + n for n in C.OVERLAY}
    for base, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for fn in files:
            if not fn.endswith(TEXT_EXT):
                continue
            p = os.path.join(base, fn)
            rel = "/" + os.path.relpath(p, root).replace(os.sep, "/")
            if rel in overlay or any(s in rel for s in NO_SUBST):
                continue
            yield p


def substitute(root, table, label, regex=False):
    """표 하나를 트리 전체에 적용하고 교체 건수를 돌려준다.

    regex=True 면 표의 왼쪽을 정규식으로 본다. 단어 경계가 필요한 규칙 때문이다 —
    단순 치환은 다른 낱말 한가운데 우연히 들어간 자리까지 바꾼다."""
    pairs = [(re.compile(a), b) for a, b in table] if regex else table
    total = 0
    fired = [0] * len(pairs)
    for p in walk_text(root):
        try:
            s = open(p, encoding="utf-8").read()
        except (UnicodeDecodeError, IsADirectoryError):
            continue
        out, hits = s, 0
        for i, (a, b) in enumerate(pairs):
            if regex:
                out, n = a.subn(b, out)
            else:
                n = out.count(a)
                if n:
                    out = out.replace(a, b)
            hits += n
            fired[i] += n
        if hits:
            open(p, "w", encoding="utf-8", newline="\n").write(out)
            total += hits
    idle = [i for i, n in enumerate(fired) if n == 0 and not covered(table, i)]
    step(f"치환 — {label}", f"{total}건" + (f" · 미적용 {len(idle)}줄" if idle else ""))
    for i in idle:
        warn_idle(label, table[i][0])
    return total


def covered(table, i):
    """앞선 더 긴 규칙이 이미 먹어 치운 자리인지 본다.

    치환표는 긴 문자열부터 적는다. 그래서 짧은 갈무리 규칙은 앞 규칙이 다 먹으면
    한 번도 안 걸린다 — 「BLUE」는 「DEMO-FCC」가, 「운영 담당」는
    「운영 담당 · 총괄」가 먼저 가져간다. 이것은 빗나간 것이 아니라 제 일을
    한 것이므로 경고하지 않는다. 앞에 자기를 품은 규칙이 하나도 없는데 0건이면
    그때가 진짜 빗나간 것이다."""
    pat = table[i][0]
    return any(pat in table[j][0] for j in range(i))


def warn_idle(label, pattern):
    """한 번도 안 걸린 규칙을 이름까지 불러 준다.

    치환 규칙은 원문이 한 글자만 바뀌어도 조용히 빗나간다. 실제로 이력 문장
    하나가 그렇게 빗나가 계정 복구 이력이 공개본에 실릴 뻔했다. DENY 가 결과를
    보고 막아 주지만, DENY 에 없는 문장(이를테면 안내문 다듬기)은 막아 줄 것이
    없다 — README 구조 목록의 공백이 3칸 어긋나 두 판 동안 조용히 빗나갔다.

    빌드를 세우지는 않는다. 규칙을 지우기 전에 한동안 남겨 두는 일이 있고,
    그때마다 공개본 판올림이 막히면 곤란하다."""
    head = pattern.splitlines()[0] if pattern else pattern
    if len(head) > 58:
        head = head[:58] + "…"
    print(f"      ! {label} 규칙 미적용 — {head}")


# ---------------------------------------------------------------- 단계

def export_head(out):
    """작업 트리가 아니라 HEAD 를 뽑는다.

    작업 트리를 복사하면 아직 커밋하지 않은 실험이 공개본에 섞인다. 공개하는
    것은 언제나 커밋된 상태여야 한다."""
    if os.path.exists(out):
        shutil.rmtree(out)
    os.makedirs(out)
    tar = subprocess.run(["git", "archive", "HEAD"], cwd=ROOT,
                         capture_output=True, check=True)
    subprocess.run(["tar", "-x", "-C", out], input=tar.stdout, check=True)
    head = run(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT).stdout.strip()
    n = sum(len(f) for _, _, f in os.walk(out))
    step("HEAD 추출", f"{head} · {n}파일")


def drop_excluded(out):
    # 빌드 부산물. dist 재생성이 만들어 내므로 추출 단계가 아니라 여기서도,
    # 커밋 직전에도 한 번 더 지운다.
    for base, dirs, _ in os.walk(out):
        for d in list(dirs):
            if d == "__pycache__":
                shutil.rmtree(os.path.join(base, d), ignore_errors=True)
                dirs.remove(d)
    gone = []
    for rel in C.EXCLUDE:
        p = os.path.join(out, rel)
        if os.path.isdir(p):
            shutil.rmtree(p)
            gone.append(rel)
        elif os.path.isfile(p):
            os.remove(p)
            gone.append(rel)
    step("제외", ", ".join(gone) if gone else "없음")


def apply_renames(out):
    done = 0
    for src, dst in C.RENAME:
        s, d = os.path.join(out, src), os.path.join(out, dst)
        if os.path.exists(s):
            os.makedirs(os.path.dirname(d), exist_ok=True)
            shutil.move(s, d)
            done += 1
    step("이름 변경", f"{done}/{len(C.RENAME)}건")


def apply_overlay(out):
    for src_rel, dst_rel in C.COPY_DIRS:
        src = os.path.join(ROOT, src_rel)
        dst = os.path.join(out, dst_rel)
        if not os.path.isdir(src):
            raise SystemExit(f"오류: {src_rel} 이 없다. 공개본 브랜드 자산이 빠졌다.")
        shutil.rmtree(dst, ignore_errors=True)
        shutil.copytree(src, dst)
    for name in C.OVERLAY:
        src = os.path.join(ROOT, "public", "overlay", name)
        if not os.path.isfile(src):
            raise SystemExit(f"오류: public/overlay/{name} 이 없다.")
        shutil.copy2(src, os.path.join(out, name))
    step("덮어쓰기", f"폴더 {len(C.COPY_DIRS)} · 파일 {len(C.OVERLAY)}")


def patch_readme(out):
    p = os.path.join(out, "README.md")
    s = open(p, encoding="utf-8").read()
    if C.README_CUT not in s:
        step("README 꼬리", "「이력」절 없음 — 건너뜀")
        return
    s = s[:s.index(C.README_CUT)].rstrip() + C.README_TAIL
    # 자르는 자리 바로 앞이 구분선이면 라이선스 절의 구분선과 겹친다
    s = s.replace("---\n\n---\n\n## 라이선스", "---\n\n## 라이선스")
    open(p, "w", encoding="utf-8", newline="\n").write(s)
    step("README 꼬리", "「이력」절 → 라이선스 절")


def stamp_version(out):
    """공개본은 비공개본과 다른 판번호를 쓴다.

    비공개본이 1.41.0 일 때 공개본이 1.1.0 인 것은 어긋난 것이 아니다 —
    공개본은 자기 배포 이력을 따로 센다. 대신 VERSION 과 CHANGELOG 가
    어긋나면 받는 사람이 자기 판을 확인할 곳이 없어지므로 여기서 막는다."""
    ver = open(os.path.join(ROOT, "public", "VERSION"), encoding="utf-8").read().strip()
    chg = open(os.path.join(out, "CHANGELOG.md"), encoding="utf-8").read()
    if f"## {ver}" not in chg:
        raise SystemExit(
            f"오류: public/VERSION 은 {ver} 인데 public/overlay/CHANGELOG.md 에\n"
            f"      '## {ver}' 항목이 없다. 판올림 기록을 먼저 적는다.")

    p = os.path.join(out, ".claude", "skills", "blue-report", ".claude-plugin", "plugin.json")
    d = json.load(open(p, encoding="utf-8"))
    d["version"] = ver
    json.dump(d, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    open(p, "a", encoding="utf-8").write("\n")

    m = os.path.join(out, ".claude-plugin", "marketplace.json")
    j = json.load(open(m, encoding="utf-8"))
    j["owner"]["name"] = C.MARKETPLACE_OWNER
    json.dump(j, open(m, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    open(m, "a", encoding="utf-8").write("\n")
    step("판번호·소유자", f"v{ver} · {C.MARKETPLACE_OWNER}")
    return ver


def rebuild_dist(out):
    """dist/ 는 assets/ 에서 다시 만든다.

    추출된 dist/ 에는 치환 전 문자열이 그대로 박혀 있다 — 치환 대상에서
    뺐기 때문이다. 다시 만들지 않으면 그것이 공개본에 실려 나간다."""
    # pptx 의존성은 비공개 트리 것을 빌려 쓴다. node_modules 는 커밋 대상이 아니다.
    nm_src = os.path.join(ROOT, ".claude/skills/blue-report/pptx/node_modules")
    nm_dst = os.path.join(out, ".claude/skills/blue-report/pptx/node_modules")
    linked = False
    if os.path.isdir(nm_src) and not os.path.exists(nm_dst):
        os.symlink(nm_src, nm_dst)
        linked = True

    b = os.path.join(out, ".claude/skills/blue-report/scripts/build_single_file.py")
    brand = "brand/hct/brand.json"
    for args in ([], ["--artifact", "--brand", brand],
                 ["--artifact", "--brand", brand, "--deck", "minutes"]):
        run([sys.executable, b] + args, cwd=out)
    if linked:
        os.remove(nm_dst)
    step("dist 재생성", "3벌")


def verify(out):
    nm_src = os.path.join(ROOT, ".claude/skills/blue-report/pptx/node_modules")
    nm_dst = os.path.join(out, ".claude/skills/blue-report/pptx/node_modules")
    linked = False
    if os.path.isdir(nm_src) and not os.path.exists(nm_dst):
        os.symlink(nm_src, nm_dst)
        linked = True
    r = run([sys.executable, os.path.join(out, "scripts", "verify_repo.py")],
            cwd=out, check=False)
    if linked:
        os.remove(nm_dst)
    tail = [l for l in r.stdout.splitlines() if l.startswith("통과 ")]
    line = tail[-1] if tail else "결과 줄 없음"
    if r.returncode != 0:
        print(r.stdout[-4000:])
        raise SystemExit(f"저장소 점검 실패 — {line}")
    step("저장소 점검", line)


def leak_scan(out):
    """공개 직전 마지막 관문. 여기서 걸리면 커밋도 push 도 하지 않는다.

    트리와 파일 경로 둘 다 본다. 파일 이름에만 남는 경우가 실제로 있었다 —
    내용은 치환됐는데 docs/BLUE_... 라는 경로가 남아 있었다."""
    found = []
    for pat in C.DENY:
        hits = 0
        for base, dirs, files in os.walk(out):
            dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
            for fn in files:
                p = os.path.join(base, fn)
                rel = os.path.relpath(p, out)
                if pat in rel:
                    hits += 1
                if not fn.endswith(TEXT_EXT):
                    continue
                try:
                    hits += open(p, encoding="utf-8").read().count(pat)
                except (UnicodeDecodeError, IsADirectoryError):
                    pass
        if hits:
            found.append((pat, hits))

    # EXPECT 는 walk_text 를 쓰지 않는다. 그 함수는 치환 제외 목록(NO_SUBST)을
    # 그대로 걸러 내는데, 회사명과 로고가 사는 곳이 바로 그 brand/hct 와 dist 다.
    # 걸러 버리면 브랜드가 멀쩡히 있어도 「없음」으로 잡힌다 — 실제로 잡혔다.
    missing = []
    for pat in C.EXPECT:
        hits = 0
        for base, dirs, files in os.walk(out):
            dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
            for fn in files:
                if fn.endswith(TEXT_EXT):
                    try:
                        hits += open(os.path.join(base, fn),
                                     encoding="utf-8").read().count(pat)
                    except (UnicodeDecodeError, IsADirectoryError):
                        pass
                if pat in fn:
                    hits += 1
        if not hits:
            missing.append(pat)

    if found or missing:
        print()
        for pat, n in found:
            print(f"      남음  {pat}  {n}건")
        for pat in missing:
            print(f"      없음  {pat}  — 브랜드가 빠졌다")
        raise SystemExit("유출 검사 실패 — 커밋하지 않는다")
    step("유출 검사", f"금지 {len(C.DENY)}패턴 0건 · 필수 {len(C.EXPECT)}패턴 확인")


def commit(out, ver, message=None):
    for base, dirs, _ in os.walk(out):
        for d in list(dirs):
            if d == "__pycache__":
                shutil.rmtree(os.path.join(base, d), ignore_errors=True)
                dirs.remove(d)
    if not os.path.isdir(os.path.join(out, ".git")):
        run(["git", "init", "-q", "-b", "main"], cwd=out, check=False)
        run(["git", "symbolic-ref", "HEAD", "refs/heads/main"], cwd=out, check=False)
    run(["git", "config", "user.name", "hctinno"], cwd=out)
    run(["git", "config", "user.email",
         "206163851+hctinno@users.noreply.github.com"], cwd=out)
    run(["git", "add", "-A"], cwd=out)
    if not run(["git", "status", "--porcelain"], cwd=out).stdout.strip():
        step("커밋", "변경 없음 — 건너뜀")
        return None
    msg = message or f"블루 리포트 공개본 v{ver}"
    run(["git", "-c", "commit.gpgsign=false", "commit", "-q", "-m", msg], cwd=out)
    sha = run(["git", "rev-parse", "--short", "HEAD"], cwd=out).stdout.strip()
    step("커밋", f"{sha}  {msg}")
    return sha


def push(out, remote):
    r = run(["git", "remote"], cwd=out)
    if "origin" in r.stdout.split():
        run(["git", "remote", "set-url", "origin", remote], cwd=out)
    else:
        run(["git", "remote", "add", "origin", remote], cwd=out)
    # 얕은 클론이 아니므로 그냥 밀면 된다. 공개본은 이 스크립트가 유일한 작성자다.
    r = run(["git", "push", "origin", "main", "--force"], cwd=out, check=False)
    out_txt = (r.stdout + r.stderr).strip().splitlines()
    step("push", out_txt[-1] if out_txt else "")
    if r.returncode != 0:
        raise SystemExit("push 실패")


# ---------------------------------------------------------------- 진입점

def main():
    ap = argparse.ArgumentParser(description="공개본 트리를 만든다")
    ap.add_argument("--out", help="만들 자리 (기본: 임시 폴더)")
    ap.add_argument("--commit", action="store_true", help="단일 커밋까지 만든다")
    ap.add_argument("--push", action="store_true",
                    help="공개 저장소로 push 한다 (--commit 필요)")
    ap.add_argument("--remote", default="https://github.com/hctinno/blue-report.git")
    ap.add_argument("--message", help="커밋 메시지")
    ap.add_argument("--skip-verify", action="store_true",
                    help="저장소 점검을 건너뛴다 (빠른 확인용 · push 와 함께 쓰지 않는다)")
    a = ap.parse_args()

    if a.push and not a.commit:
        raise SystemExit("--push 는 --commit 과 함께 준다")
    if a.push and a.skip_verify:
        raise SystemExit("--push 와 --skip-verify 를 함께 주지 않는다")

    out = a.out or os.path.join(tempfile.gettempdir(), "blue-report-public")
    out = os.path.abspath(out)
    print(f"\n공개본 빌드 → {out}\n")

    export_head(out)
    drop_excluded(out)
    apply_renames(out)
    apply_overlay(out)
    substitute(out, C.INTERNAL, "사내 고유어")
    substitute(out, C.BRANDING, "브랜드 문자열")
    substitute(out, C.WORD, "단어 경계 규칙", regex=True)
    substitute(out, C.ACCOUNT, "구 계정 핸들")
    substitute(out, C.BRANCH, "기본 브랜치")
    substitute(out, C.HISTORY, "저장소 이력 문장")
    patch_readme(out)
    ver = stamp_version(out)
    rebuild_dist(out)
    if a.skip_verify:
        step("저장소 점검", "건너뜀 (--skip-verify)")
    else:
        verify(out)
    leak_scan(out)

    sha = None
    if a.commit:
        sha = commit(out, ver, a.message)
    if a.push:
        push(out, a.remote)

    print(f"\n완료 — {out}")
    if not a.commit:
        print("  커밋까지 하려면 --commit, 공개 저장소로 올리려면 --commit --push")
    elif not a.push and sha:
        print(f"  올리려면: git -C {out} push origin main --force")
    print()


if __name__ == "__main__":
    main()
