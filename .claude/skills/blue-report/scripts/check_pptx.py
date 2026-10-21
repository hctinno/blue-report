#!/usr/bin/env python3
"""Self-contained OOXML integrity checks; layout and editing need a renderer.

    python scripts/check_pptx.py presentation.pptx
"""
import argparse
import json
from pathlib import Path
import posixpath
import re
from urllib.parse import unquote, urlsplit
import xml.etree.ElementTree as ET
import zipfile

P = "http://schemas.openxmlformats.org/presentationml/2006/main"
R = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
A = "http://schemas.openxmlformats.org/drawingml/2006/main"
LEAK = re.compile(r"\b(?:undefined|NaN)\b|\[object Object\]")


def inspect(path):
    result = {"file": str(Path(path).resolve()), "slides": 0, "failures": [],
              "scope": "zip/xml/relationships/slide text", "visual_review": "not performed"}
    failures = result["failures"]
    try:
        with zipfile.ZipFile(path) as archive:
            names = set(archive.namelist())
            corrupt = archive.testzip()
            if corrupt:
                failures.append("압축 손상: " + corrupt)
                return result
            required = {"[Content_Types].xml", "_rels/.rels", "ppt/presentation.xml",
                        "ppt/_rels/presentation.xml.rels"}
            missing = sorted(required - names)
            if missing:
                failures.append("필수 부품 누락: " + ", ".join(missing))
                return result
            parsed = {}
            for name in sorted(names):
                if name.endswith((".xml", ".rels")):
                    parsed[name] = ET.fromstring(archive.read(name))
            for name, root in parsed.items():
                if not name.endswith(".rels"):
                    continue
                base = posixpath.dirname(posixpath.dirname(name))
                for rel in root:
                    if rel.get("TargetMode") == "External":
                        continue
                    target = unquote(urlsplit(rel.get("Target", "")).path)
                    resolved = posixpath.normpath(target.lstrip("/") if target.startswith("/")
                                                 else posixpath.join(base, target))
                    if not target or resolved not in names:
                        failures.append(f"연결 부품 누락: {name} → {target}")
            rels = {r.get("Id"): r.get("Target", "")
                    for r in parsed["ppt/_rels/presentation.xml.rels"]}
            slide_ids = parsed["ppt/presentation.xml"].findall(f"./{{{P}}}sldIdLst/{{{P}}}sldId")
            result["slides"] = len(slide_ids)
            if not slide_ids:
                failures.append("발표 슬라이드 0장")
            for index, slide_id in enumerate(slide_ids, 1):
                target = rels.get(slide_id.get(f"{{{R}}}id"), "")
                resolved = posixpath.normpath(target.lstrip("/") if target.startswith("/")
                                             else posixpath.join("ppt", target))
                if resolved not in parsed or not resolved.startswith("ppt/slides/"):
                    failures.append(f"슬라이드 {index}: 연결 없음 또는 잘못된 대상")
                    continue
                for text in parsed[resolved].iter(f"{{{A}}}t"):
                    if LEAK.search(text.text or ""):
                        failures.append(f"슬라이드 {index}: 오류 텍스트 {text.text}")
    except (OSError, zipfile.BadZipFile, ET.ParseError, KeyError, RuntimeError) as error:
        failures.append("PPTX 검사 실패: " + str(error))
    return result


def main():
    parser = argparse.ArgumentParser(description="PPTX 파일 구조·연결·오류 텍스트 검사")
    parser.add_argument("path", type=Path)
    result = inspect(parser.parse_args().path)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 1 if result["failures"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
