from __future__ import annotations

from importlib.resources import files
import unittest


class DemoAssetsTests(unittest.TestCase):
    def test_index_html_contains_expected_demo_sections(self) -> None:
        html = files("maie.demo").joinpath("web", "index.html").read_text(encoding="utf-8")
        self.assertIn("Control Room", html)
        self.assertIn("scenario-list", html)
        self.assertIn("request-editor", html)
        self.assertIn("Operational Overview", html)

    def test_styles_include_custom_theme_variables(self) -> None:
        css = files("maie.demo").joinpath("web", "styles.css").read_text(encoding="utf-8")
        self.assertIn("--accent", css)
        self.assertIn("radial-gradient", css)
        self.assertIn("@keyframes rise", css)


if __name__ == "__main__":
    unittest.main()
