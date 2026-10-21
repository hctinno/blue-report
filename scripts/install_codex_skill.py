#!/usr/bin/env python3
"""Install the shared skill for native Codex discovery, including HCT assets.

    python scripts/install_codex_skill.py
    python scripts/install_codex_skill.py --update

Updates retain the previous installation outside the skill discovery directory.
The installer does not change global instructions, auth, or running sessions.
"""
import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import uuid
import zipfile

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / ".claude/skills/blue-report"
BRAND = ROOT / "brand/hct"
EXCLUDE = {".claude-plugin", "node_modules", "dist", "__pycache__", "shots", ".DS_Store"}


def default_target():
    custom_home = os.environ.get("CODEX_HOME")
    return Path(custom_home) / "skills/blue-report" if custom_home else Path.home() / ".agents/skills/blue-report"


def install(target, update=False):
    target = Path(target).expanduser().absolute()
    if target.name != "blue-report" or target.is_symlink():
        raise ValueError("설치 대상은 링크가 아닌 blue-report 폴더여야 합니다.")
    if target.exists() and (not target.is_dir() or not update):
        raise FileExistsError("기존 설치본을 보존했습니다. 갱신은 --update로 명시하세요.")
    required = ("SKILL.md", "DESIGN.md", "references/business-presentation-intake.md",
                "references/visual-style-selection.md", "scripts/style_previews.py")
    for relative in required:
        if not (SOURCE / relative).is_file():
            raise FileNotFoundError("원본 파일 누락: " + relative)
    if not (BRAND / "brand.json").is_file():
        raise FileNotFoundError("원본 HCT 브랜드 자산 누락")
    # Resolved destinations and backups stay within the explicitly chosen parent.
    parent = target.parent.resolve()
    target = parent / target.name
    if target == SOURCE.resolve() or target.is_relative_to(SOURCE.resolve()):
        raise ValueError("원본 스킬에 설치할 수 없습니다.")
    version = json.loads((SOURCE / ".claude-plugin/plugin.json").read_text(encoding="utf-8"))["version"]
    try:
        result = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "HEAD"], capture_output=True, text=True)
        commit = result.stdout.strip() if result.returncode == 0 else None
        status = subprocess.run(["git", "-C", str(ROOT), "status", "--porcelain"], capture_output=True, text=True)
        modified = bool(status.stdout.strip()) if status.returncode == 0 else None
    except FileNotFoundError:
        commit, modified = None, None
    with tempfile.TemporaryDirectory(prefix="blue-report-install-") as temporary:
        stage = Path(temporary).resolve() / "blue-report"
        shutil.copytree(SOURCE, stage, ignore=shutil.ignore_patterns(*EXCLUDE))
        shutil.copytree(BRAND, stage / "brand/hct")
        record = {"repository": "https://github.com/hctinno/blue-report", "commit": commit,
                  "upstream_version": version, "source_worktree_modified": modified,
                  "installed_at_utc": datetime.now(timezone.utc).isoformat()}
        (stage / "INSTALLATION.json").write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        parent.mkdir(parents=True, exist_ok=True)
        backup = None
        if target.exists():
            backup_parent = parent.parent / "skill-backups/blue-report"
            backup_parent.mkdir(parents=True, exist_ok=True)
            backup = backup_parent / (datetime.now().strftime("%Y%m%d-%H%M%S") + "-" + uuid.uuid4().hex[:8])
            if not target.resolve().is_relative_to(parent) or not backup.resolve().is_relative_to(backup_parent.resolve()):
                raise ValueError("설치·백업 경로가 지정 범위를 벗어났습니다.")
            # Windows editors may hold the directory open. Back up its contents
            # before updating files in place, keeping personal additions intact.
            shutil.copytree(target, backup)
        try:
            shutil.copytree(stage, target, dirs_exist_ok=update)
            plugin_manifest = target / ".claude-plugin/plugin.json"
            if plugin_manifest.is_file():
                # The complete previous installation is retained in backup.
                # Native Codex skills must not inherit Claude plugin namespacing.
                plugin_manifest.unlink()
        except Exception:
            # Preserve partial output and restore the previous installation.
            if target.exists():
                partial_parent = parent.parent / "skill-backups/blue-report"
                partial_parent.mkdir(parents=True, exist_ok=True)
                partial = partial_parent / ("partial-" + uuid.uuid4().hex[:8])
                shutil.copytree(target, partial)
            if backup is not None:
                shutil.copytree(backup, target, dirs_exist_ok=True)
            raise
    return {"installed": str(target), "version": version, "backup": str(backup) if backup else None}


def main():
    parser = argparse.ArgumentParser(description="블루 리포트를 Codex 개인 스킬로 설치")
    parser.add_argument("--target", type=Path)
    parser.add_argument("--update", action="store_true")
    parser.add_argument("--bundle", type=Path, help="다른 PC에 복사할 독립 Codex 스킬 ZIP 생성")
    args = parser.parse_args()
    if args.bundle:
        if args.target or args.update:
            parser.error("--bundle은 --target·--update와 함께 사용할 수 없습니다.")
        print(json.dumps(bundle(args.bundle), ensure_ascii=False))
        return
    print(json.dumps(install(args.target or default_target(), args.update), ensure_ascii=False))
    print("다음 요청부터 /skills에서 blue-report를 선택하거나 $blue-report로 호출하세요.")


def bundle(output):
    """Ship exactly the self-contained native installation, without npm caches."""
    output = Path(output).expanduser().resolve()
    if output.exists():
        raise FileExistsError("기존 배포 ZIP을 보존했습니다. 새 파일명을 지정하세요.")
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="blue-report-bundle-") as temporary:
        skill = Path(temporary) / "skills/blue-report"
        install(skill)
        with zipfile.ZipFile(output, "x", zipfile.ZIP_DEFLATED) as archive:
            for path in sorted(skill.rglob("*")):
                if path.is_file():
                    archive.write(path, str(Path("blue-report") / path.relative_to(skill)).replace("\\", "/"))
    return {"bundle": str(output), "bytes": output.stat().st_size}


if __name__ == "__main__":
    main()
