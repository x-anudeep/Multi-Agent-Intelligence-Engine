from __future__ import annotations

import unittest

from maie.tools.registry import ToolDefinition, ToolRegistry


class ToolRegistryTests(unittest.TestCase):
    def test_register_and_invoke_tool(self) -> None:
        registry = ToolRegistry()
        registry.register(
            ToolDefinition(
                name="web_search",
                description="Searches intelligence sources.",
                required_args=("query",),
                handler=lambda query: {"query": query, "matches": 3},
            )
        )

        result = registry.invoke("web_search", query="supplier bankruptcy")

        self.assertEqual(result["matches"], 3)

    def test_invoke_raises_when_required_args_are_missing(self) -> None:
        registry = ToolRegistry()
        registry.register(
            ToolDefinition(
                name="news_lookup",
                description="Fetches news.",
                required_args=("ticker",),
                handler=lambda ticker: ticker,
            )
        )

        with self.assertRaises(ValueError):
            registry.invoke("news_lookup")


if __name__ == "__main__":
    unittest.main()

