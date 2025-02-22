from __future__ import annotations

import tempfile
import unittest

from maie.api.app import create_app, fastapi_available
from maie.api.contracts import RiskWorkflowRequest
from maie.application.workflow_service import WorkflowApplicationService
from maie.core.config import Settings


class WorkflowApplicationServiceTests(unittest.IsolatedAsyncioTestCase):
    async def test_execute_risk_workflow_returns_api_friendly_response(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            settings = Settings(
                checkpoint_dir=temp_dir,
                enable_telemetry=False,
                use_mock_providers=True,
            )
            service = WorkflowApplicationService(settings)
            request = RiskWorkflowRequest.model_validate(
                {
                    "supplier_name": "Apex Components",
                    "signals": [
                        {
                            "source": "news",
                            "headline": "Port congestion",
                            "summary": "Logistics issues are affecting shipments.",
                            "severity": 4,
                            "region": "North America",
                        },
                        {
                            "source": "sec_filing",
                            "headline": "Liquidity warning",
                            "summary": "Debt covenant risk disclosed in latest filing.",
                            "severity": 5,
                            "region": "US",
                        },
                    ],
                }
            )

            response = await service.execute_risk_workflow(request)
            history = service.get_checkpoint_history(response.workflow_id)

        self.assertEqual(response.status, "complete")
        self.assertGreaterEqual(response.checkpoint_count, 5)
        self.assertGreaterEqual(response.snapshot_count, response.checkpoint_count)
        self.assertGreaterEqual(history.checkpoint_count, response.checkpoint_count)
        self.assertIn("finish", response.routing_targets)
        self.assertIn("compliance_review_agent", response.routing_targets)
        self.assertGreaterEqual(response.routing_branch_count, 4)
        self.assertGreaterEqual(response.average_event_duration_ms, 0)
        self.assertTrue(response.report_preview)

    def test_app_factory_behaves_consistently_with_fastapi_availability(self) -> None:
        if fastapi_available():
            app = create_app(settings=Settings())
            self.assertIsNotNone(app)
        else:
            with self.assertRaises(RuntimeError):
                create_app(settings=Settings())


if __name__ == "__main__":
    unittest.main()
