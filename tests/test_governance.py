from __future__ import annotations

import tempfile
import unittest

from maie.api.contracts import RiskWorkflowRequest
from maie.application.workflow_service import WorkflowApplicationService
from maie.core.config import Settings
from maie.governance.policies import GovernancePolicy


class GovernancePolicyTests(unittest.IsolatedAsyncioTestCase):
    async def test_governance_sanitizes_sensitive_content_in_response(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            settings = Settings(
                checkpoint_dir=temp_dir,
                enable_telemetry=False,
                enable_governance=True,
            )
            service = WorkflowApplicationService(settings)
            request = RiskWorkflowRequest.model_validate(
                {
                    "supplier_name": "Apex Components",
                    "signals": [
                        {
                            "source": "news",
                            "headline": "Escalate to analyst at jane.doe@example.com",
                            "summary": "Call 602-555-0199 after supplier disruption review.",
                            "severity": 4,
                            "region": "North America",
                        }
                    ],
                }
            )

            response = await service.execute_risk_workflow(request)

        self.assertIn("[redacted-email]", response.state_snapshot["signal_batch"][0]["headline"])
        self.assertIn("[redacted-phone]", response.state_snapshot["signal_batch"][0]["summary"])
        self.assertFalse(any("example.com" in item for item in response.governance_findings))

    def test_governance_detects_potential_sensitive_data(self) -> None:
        policy = GovernancePolicy(Settings(enable_governance=True))
        request = RiskWorkflowRequest.model_validate(
            {
                "supplier_name": "Apex Components",
                "signals": [
                    {
                        "source": "news",
                        "headline": "Contact jane.doe@example.com",
                        "summary": "Monitor disruption impact.",
                        "severity": 3,
                        "region": "US",
                    }
                ],
            }
        )

        review = policy.review_request(request)

        self.assertTrue(review.approved)
        self.assertTrue(review.findings)


if __name__ == "__main__":
    unittest.main()

