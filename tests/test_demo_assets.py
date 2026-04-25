from __future__ import annotations

from importlib.resources import files
import unittest


class DemoAssetsTests(unittest.TestCase):
    def test_index_html_contains_expected_demo_sections(self) -> None:
        html = files("maie.demo").joinpath("web", "index.html").read_text(encoding="utf-8")
        self.assertIn("Multi-Agent Intelligence Engine", html)
        self.assertIn("risk-form", html)
        self.assertIn("supplier-name", html)
        self.assertIn("signals-list", html)
        self.assertIn("add-signal", html)
        self.assertIn("submit-workflow", html)
        self.assertIn("Backend Results", html)
        self.assertIn("Compliance", html)
        self.assertIn("signal-template", html)
        self.assertNotIn("Audit Trail", html)
        self.assertNotIn("workflow route", html)
        self.assertNotIn("routing-path", html)

    def test_styles_include_custom_theme_variables(self) -> None:
        css = files("maie.demo").joinpath("web", "styles.css").read_text(encoding="utf-8")
        self.assertIn("--accent", css)
        self.assertIn(".workspace", css)
        self.assertIn(".signal-card", css)
        self.assertIn(".metrics-grid", css)
        self.assertIn(".primary-button", css)
        self.assertIn("@media", css)


if __name__ == "__main__":
    unittest.main()
