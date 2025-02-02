from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

from maie.api.contracts import RiskWorkflowRequest, WorkflowExecutionResponse
from maie.core.config import Settings


EMAIL_PATTERN = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
PHONE_PATTERN = re.compile(r"\b(?:\+?1[-.\s]?)?(?:\(?\d{3}\)?[-.\s]?)\d{3}[-.\s]?\d{4}\b")
SSN_PATTERN = re.compile(r"\b\d{3}-\d{2}-\d{4}\b")


@dataclass(slots=True)
class GovernanceFinding:
    rule_id: str
    severity: str
    message: str


@dataclass(slots=True)
class GovernanceReview:
    approved: bool
    findings: list[GovernanceFinding]


class GovernancePolicy:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def review_request(self, request: RiskWorkflowRequest) -> GovernanceReview:
        if not self.settings.enable_governance:
            return GovernanceReview(approved=True, findings=[])

        findings: list[GovernanceFinding] = []
        if not request.signals:
            findings.append(
                GovernanceFinding(
                    rule_id="request.signals_required",
                    severity="high",
                    message="At least one signal is required for enterprise risk assessment.",
                )
            )

        if request.max_steps > 12:
            findings.append(
                GovernanceFinding(
                    rule_id="request.max_steps_review",
                    severity="medium",
                    message="High step counts should be reviewed for cost and latency impact.",
                )
            )

        for signal in request.signals:
            if self._contains_sensitive_data(signal.summary) or self._contains_sensitive_data(
                signal.headline
            ):
                findings.append(
                    GovernanceFinding(
                        rule_id="request.pii_detected",
                        severity="medium",
                        message="Potential sensitive data detected in request content; response will be sanitized.",
                    )
                )
                break

        approved = not any(finding.severity == "high" for finding in findings)
        return GovernanceReview(approved=approved, findings=findings)

    def sanitize_execution_response(
        self,
        response: WorkflowExecutionResponse,
    ) -> WorkflowExecutionResponse:
        if not self.settings.enable_governance:
            return response

        sanitized_state = self._sanitize_value(response.state_snapshot)
        sanitized_report = self._sanitize_text(response.report_preview)
        sanitized_audit_trail = [
            self._sanitize_text(entry) for entry in response.audit_trail
        ]
        sanitized_findings = [
            self._sanitize_text(entry) for entry in response.governance_findings
        ]
        sanitized_hits = [self._sanitize_text(hit) for hit in response.knowledge_hits]
        return response.model_copy(
            update={
                "report_preview": sanitized_report,
                "audit_trail": sanitized_audit_trail,
                "governance_findings": sanitized_findings,
                "knowledge_hits": sanitized_hits,
                "state_snapshot": sanitized_state,
            }
        )

    def _sanitize_value(self, value: Any) -> Any:
        if isinstance(value, str):
            return self._sanitize_text(value)
        if isinstance(value, list):
            return [self._sanitize_value(item) for item in value]
        if isinstance(value, dict):
            return {key: self._sanitize_value(item) for key, item in value.items()}
        return value

    def _sanitize_text(self, text: str | None) -> str | None:
        if text is None:
            return None
        sanitized = EMAIL_PATTERN.sub("[redacted-email]", text)
        sanitized = PHONE_PATTERN.sub("[redacted-phone]", sanitized)
        sanitized = SSN_PATTERN.sub("[redacted-ssn]", sanitized)
        return sanitized

    def _contains_sensitive_data(self, text: str) -> bool:
        return bool(
            EMAIL_PATTERN.search(text)
            or PHONE_PATTERN.search(text)
            or SSN_PATTERN.search(text)
        )

