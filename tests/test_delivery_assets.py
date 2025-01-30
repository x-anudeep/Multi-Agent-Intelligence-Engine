from __future__ import annotations

from pathlib import Path
import unittest


class DeliveryAssetsTests(unittest.TestCase):
    def test_dockerfile_uses_api_entrypoint(self) -> None:
        dockerfile = Path("Dockerfile").read_text(encoding="utf-8")
        self.assertIn('CMD ["maie-api"]', dockerfile)
        self.assertIn("EXPOSE 8080", dockerfile)

    def test_compose_maps_service_port(self) -> None:
        compose = Path("docker-compose.yml").read_text(encoding="utf-8")
        self.assertIn('8080:8080', compose)
        self.assertIn("CHECKPOINT_DIR: /app/.maie/checkpoints", compose)

    def test_kubernetes_manifests_include_health_probe_and_service(self) -> None:
        deployment = Path("deploy/kubernetes/deployment.yaml").read_text(encoding="utf-8")
        service = Path("deploy/kubernetes/service.yaml").read_text(encoding="utf-8")
        hpa = Path("deploy/kubernetes/hpa.yaml").read_text(encoding="utf-8")
        self.assertIn("/health", deployment)
        self.assertIn("containerPort: 8080", deployment)
        self.assertIn("ClusterIP", service)
        self.assertIn("HorizontalPodAutoscaler", hpa)


if __name__ == "__main__":
    unittest.main()
