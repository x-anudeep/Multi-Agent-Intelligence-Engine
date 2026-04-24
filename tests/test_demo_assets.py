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
        self.assertIn("metric-snapshots", html)
        self.assertIn("Runtime Profile", html)
        self.assertIn("Compliance Review", html)
        self.assertIn("Problem Intake", html)
        self.assertIn("generate-request", html)
        self.assertIn("composer-send-button", html)
        self.assertIn("composer-add", html)

    def test_styles_include_custom_theme_variables(self) -> None:
        css = files("maie.demo").joinpath("web", "styles.css").read_text(encoding="utf-8")
        self.assertIn("--accent", css)
        self.assertIn("radial-gradient", css)
        self.assertIn("@keyframes rise", css)
        self.assertIn(".runtime-profile", css)
        self.assertIn(".composer-shell", css)
        self.assertIn(".composer-send-button", css)


if __name__ == "__main__":
    unittest.main()
