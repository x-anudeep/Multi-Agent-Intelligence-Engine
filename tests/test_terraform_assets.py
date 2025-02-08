from __future__ import annotations

from pathlib import Path
import unittest


class TerraformAssetsTests(unittest.TestCase):
    def test_terraform_defines_cluster_and_registry(self) -> None:
        main_tf = Path("infra/terraform/main.tf").read_text(encoding="utf-8")
        self.assertIn("google_container_cluster", main_tf)
        self.assertIn("google_artifact_registry_repository", main_tf)
        self.assertIn("workload_identity_config", main_tf)

    def test_terraform_outputs_include_cluster_endpoint(self) -> None:
        outputs_tf = Path("infra/terraform/outputs.tf").read_text(encoding="utf-8")
        self.assertIn("gke_cluster_endpoint", outputs_tf)
        self.assertIn("artifact_registry_repository_url", outputs_tf)


if __name__ == "__main__":
    unittest.main()
