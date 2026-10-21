"""Observable packaging and rendering checks for the shared skill workflow."""
import copy
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock
import sys
import zipfile

ROOT = Path(__file__).resolve().parent.parent


def module(path, name):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    loaded = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(loaded)
    return loaded


installer = module("scripts/install_codex_skill.py", "codex_installer")
previews = module(".claude/skills/blue-report/scripts/style_previews.py", "style_previews")
dependencies = module(".claude/skills/blue-report/scripts/ensure_deps.py", "workflow_dependencies")
pptx = module(".claude/skills/blue-report/scripts/check_pptx.py", "pptx_check")


class InstallTests(unittest.TestCase):
    def test_portable_bundle_contains_tools_brand_and_no_repository_dependencies(self):
        with tempfile.TemporaryDirectory() as temporary:
            out = Path(temporary) / "codex-skill.zip"
            installer.bundle(out)
            with zipfile.ZipFile(out) as archive:
                self.assertIsNone(archive.testzip())
                names = archive.namelist()
                for file in ("SKILL.md", "agents/openai.yaml", "scripts/check_pptx.py",
                             "references/quality-and-delivery.md", "references/page-style-selection.md",
                             "brand/hct/brand.json"):
                    self.assertIn("blue-report/" + file, names)
                self.assertFalse(any("/.claude-plugin/" in p or "/node_modules/" in p for p in names))
                moved = Path(temporary) / "unrelated-project"
                archive.extractall(moved)
            portable = module(moved / "blue-report/scripts/style_previews.py", "portable_previews")
            result = portable.render_previews(portable.EXAMPLE, Path(temporary) / "rendered")
            self.assertEqual(len(result["styles"]), 3)
            with self.assertRaises(FileExistsError):
                installer.bundle(out)

    def test_native_skill_is_self_contained(self):
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / "skills/blue-report"
            installer.install(target)
            self.assertTrue((target / "brand/hct/brand.json").is_file())
            self.assertTrue((target / "scripts/style_previews.py").is_file())
            self.assertTrue((target / "references/visual-style-selection.md").is_file())
            self.assertTrue((target / "references/page-style-selection.md").is_file())
            self.assertFalse((target / ".claude-plugin").exists())
            brand = json.loads((target / "brand/hct/brand.json").read_text(encoding="utf-8"))
            for key in ("logo", "logoOnLight", "watermark", "watermarkOnLight"):
                self.assertTrue((target / "brand/hct" / brand[key]).is_file())

    def test_existing_install_requires_update_and_retains_original(self):
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / "skills/blue-report"
            installer.install(target)
            (target / "personal-note.txt").write_text("keep me", encoding="utf-8")
            with self.assertRaises(FileExistsError):
                installer.install(target)
            self.assertEqual((target / "personal-note.txt").read_text(encoding="utf-8"), "keep me")
            result = installer.install(target, update=True)
            backup = Path(result["backup"])
            self.assertFalse(backup.is_relative_to(target.parent))
            self.assertEqual((backup / "personal-note.txt").read_text(encoding="utf-8"), "keep me")
            self.assertEqual((target / "personal-note.txt").read_text(encoding="utf-8"), "keep me")
            self.assertTrue((target / "SKILL.md").is_file())

    def test_update_does_not_move_open_directory_or_keep_plugin_namespace(self):
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / "skills/blue-report"
            installer.install(target)
            manifest = target / ".claude-plugin/plugin.json"
            manifest.parent.mkdir()
            manifest.write_text('{"name": "old-plugin"}', encoding="utf-8")
            (target / "SKILL.md").write_text("old installation", encoding="utf-8")
            with mock.patch.object(Path, "rename", side_effect=PermissionError("open directory")):
                result = installer.install(target, update=True)
            self.assertFalse(manifest.exists())
            self.assertTrue((Path(result["backup"]) / ".claude-plugin/plugin.json").is_file())
            self.assertEqual((Path(result["backup"]) / "SKILL.md").read_text(encoding="utf-8"), "old installation")
            self.assertIn("name: blue-report", (target / "SKILL.md").read_text(encoding="utf-8"))


class RuntimeTests(unittest.TestCase):
    def test_html_readiness_does_not_require_node_or_install_anything(self):
        with mock.patch.object(sys, "argv", ["ensure_deps.py", "--for", "html", "--check"]), \
                mock.patch.object(dependencies.shutil, "which", return_value=None), \
                mock.patch.object(dependencies, "_pip", side_effect=AssertionError("check installed a package")):
            with self.assertRaises(SystemExit) as stopped:
                dependencies.main()
        self.assertEqual(stopped.exception.code, 0)

    def test_pptx_checker_catches_missing_slide_and_does_not_claim_visual_review(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "missing-slide.pptx"
            with zipfile.ZipFile(path, "w") as archive:
                archive.writestr("[Content_Types].xml", "<Types/>")
                archive.writestr("_rels/.rels", "<Relationships><Relationship Target='ppt/presentation.xml'/></Relationships>")
                archive.writestr("ppt/presentation.xml", f'<p:presentation xmlns:p="{pptx.P}" xmlns:r="{pptx.R}"><p:sldIdLst><p:sldId r:id="rId1"/></p:sldIdLst></p:presentation>')
                archive.writestr("ppt/_rels/presentation.xml.rels", "<Relationships><Relationship Id='rId1' Target='slides/slide1.xml'/></Relationships>")
            result = pptx.inspect(path)
            self.assertEqual(result["slides"], 1)
            self.assertTrue(result["failures"])
            self.assertEqual(result["visual_review"], "not performed")
            path.write_bytes(b"broken pptx")
            self.assertTrue(pptx.inspect(path)["failures"])


class PreviewTests(unittest.TestCase):
    def test_same_content_and_safe_text_in_all_directions(self):
        data = copy.deepcopy(previews.EXAMPLE)
        data["title"] = '<script>alert("x")</script>'
        data["points"][0]["label"] = "A & B"
        rendered = [previews.make_html(data, style[0]) for style in previews.STYLES]
        self.assertEqual(len(set(rendered)), 3)
        for page in rendered:
            self.assertNotIn('<script>alert("x")</script>', page)
            self.assertIn("&lt;script&gt;", page)
            self.assertIn("A &amp; B", page)
            self.assertIn(data["message"], page)

    def test_invalid_brief_does_not_silently_drop_content(self):
        data = copy.deepcopy(previews.EXAMPLE)
        data["points"] *= 2
        with self.assertRaises(ValueError):
            previews.validate_content(data)
        data = copy.deepcopy(previews.EXAMPLE)
        data["recommended_style"] = "missing"
        with self.assertRaises(ValueError):
            previews.validate_content(data)

    def test_real_pngs_and_unselected_manifest(self):
        from PIL import Image
        with tempfile.TemporaryDirectory() as temporary:
            out = Path(temporary)
            manifest = previews.render_previews(previews.EXAMPLE, out)
            self.assertIsNone(manifest["selected_style"])
            images = []
            for style in manifest["styles"]:
                for key in ("cover", "body"):
                    with Image.open(out / style[key]) as image:
                        self.assertEqual(image.size, (1600, 900))
                        images.append(image.tobytes())
            self.assertEqual(len(set(images)), 6)
            self.assertTrue((out / "comparison.png").is_file())
            with self.assertRaises(FileExistsError):
                previews.render_previews(previews.EXAMPLE, out)


if __name__ == "__main__":
    unittest.main()
