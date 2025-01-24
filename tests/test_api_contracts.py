from __future__ import annotations

import unittest

from maie.api.contracts import RiskWorkflowRequest


class RiskWorkflowRequestTests(unittest.TestCase):
    def test_request_validates_and_converts_signal_payload(self) -> None:
        request = RiskWorkflowRequest.model_validate(
            {
                "supplier_name": "Apex Components",
                "signals": [
                    {
                        "source": "news",
                        "headline": "Port congestion",
                        "summary": "Shipping timelines are slipping.",
                        "severity": 4,
                        "region": "North America",
                    }
                ],
            }
        )

        signal = request.signals[0].to_domain(request.supplier_name)

        self.assertEqual(signal.supplier_name, "Apex Components")
        self.assertEqual(signal.source.value, "news")


if __name__ == "__main__":
    unittest.main()

