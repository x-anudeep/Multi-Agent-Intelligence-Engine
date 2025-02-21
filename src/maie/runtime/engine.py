from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from maie.agents.base import BaseAgent
from maie.agents.specialists import (
    ComplianceReviewAgent,
    HumanReviewAgent,
    ReportGenerationAgent,
    ResearchAgent,
    RiskScoringAgent,
)
from maie.checkpoints.store import (
    CheckpointRecord,
    JsonFileCheckpointStore,
    PostgresCheckpointStore,
    SQLiteCheckpointStore,
    build_checkpoint_store,
)
from maie.core.config import Settings
from maie.domain.models import AgentTarget, RoutingDecision, SupplierSignal, WorkflowStatus
from maie.graph.state import WorkflowState, build_initial_state
from maie.knowledge.retriever import LocalKnowledgeRetriever, build_default_knowledge_retriever
from maie.observability.telemetry import WorkflowTelemetry
from maie.providers.registry import ProviderRegistry, build_default_provider_registry
from maie.routing.policy import PolicyRouter
from maie.tools.intelligence import build_default_tool_registry
from maie.tools.registry import ToolRegistry
from maie.runtime.state_store import (
    RuntimeStateStore,
    SnapshotRecord,
    build_runtime_state_store,
)


class CheckpointStore(Protocol):
    def save(self, workflow_id: str, label: str, state: WorkflowState) -> CheckpointRecord:
        ...

    def load(self, workflow_id: str) -> list[CheckpointRecord]:
        ...


@dataclass(slots=True)
class WorkflowRunArtifacts:
    state: WorkflowState
    telemetry: WorkflowTelemetry
    checkpoint_records: list[CheckpointRecord]
    snapshot_records: list[SnapshotRecord]
    checkpoint_location: str | None


class WorkflowEngine:
    def __init__(
        self,
        *,
        router: PolicyRouter,
        agents: dict[AgentTarget, BaseAgent],
        checkpoint_store: CheckpointStore,
        state_store: RuntimeStateStore,
        telemetry: WorkflowTelemetry,
    ) -> None:
        self.router = router
        self.agents = agents
        self.checkpoint_store = checkpoint_store
        self.state_store = state_store
        self.telemetry = telemetry

    async def run(
        self,
        supplier_name: str,
        signals: list[SupplierSignal],
        *,
        sector: str = "financial-services",
        jurisdiction: str = "US",
        max_steps: int = 8,
    ) -> WorkflowRunArtifacts:
        state = build_initial_state(
            supplier_name=supplier_name,
            signals=signals,
            sector=sector,
            jurisdiction=jurisdiction,
        )
        checkpoint_records: list[CheckpointRecord] = []
        snapshot_records: list[SnapshotRecord] = []
        checkpoint_records.append(self._save_checkpoint(state, "initialized"))
        snapshot_records.append(self._save_snapshot(state, "initialized"))
        self.telemetry.record(
            state["workflow_id"],
            "workflow_initialized",
            supplier_name=supplier_name,
            signal_count=len(signals),
        )

        for step_index in range(max_steps):
            with self.telemetry.time_block(
                state["workflow_id"],
                "routing_decision",
                step=step_index + 1,
            ):
                decision = self.router.route(state)
            self._record_decision(state, decision)
            checkpoint_records.append(
                self._save_checkpoint(state, f"decision_{step_index + 1}_{decision.target_agent.value}")
            )
            snapshot_records.append(
                self._save_snapshot(state, f"decision_{step_index + 1}_{decision.target_agent.value}")
            )

            if decision.target_agent is AgentTarget.FINISH:
                state["status"] = WorkflowStatus.COMPLETE.value
                self.telemetry.record(
                    state["workflow_id"],
                    "workflow_completed",
                    step=step_index + 1,
                    final_status=state["status"],
                )
                checkpoint_records.append(self._save_checkpoint(state, "completed"))
                snapshot_records.append(self._save_snapshot(state, "completed"))
                return WorkflowRunArtifacts(
                    state=state,
                    telemetry=self.telemetry,
                    checkpoint_records=checkpoint_records,
                    snapshot_records=snapshot_records,
                    checkpoint_location=self._checkpoint_location(state["workflow_id"]),
                )

            with self.telemetry.time_block(
                state["workflow_id"],
                "agent_completed",
                step=step_index + 1,
                agent_name=decision.target_agent.value,
            ):
                result = await self.agents[decision.target_agent].run(state)
            state.update(result.state_updates)
            self.telemetry.record(
                state["workflow_id"],
                "agent_audit",
                step=step_index + 1,
                agent_name=result.agent_name.value,
                audit_log=result.audit_log,
            )
            checkpoint_records.append(
                self._save_checkpoint(state, f"post_{step_index + 1}_{result.agent_name.value}")
            )
            snapshot_records.append(
                self._save_snapshot(state, f"post_{step_index + 1}_{result.agent_name.value}")
            )

        raise RuntimeError("Workflow exceeded the maximum number of steps.")

    def _record_decision(self, state: WorkflowState, decision: RoutingDecision) -> None:
        history = [*state.get("routing_history", []), decision]
        state["last_decision"] = decision
        state["routing_history"] = history
        state["routing_branch_count"] = len(
            {item.reason for item in history}
        )

    def _save_checkpoint(self, state: WorkflowState, label: str) -> CheckpointRecord:
        labels = [*state.get("checkpoint_labels", []), label]
        state["checkpoint_labels"] = labels
        return self.checkpoint_store.save(state["workflow_id"], label, state)

    def _save_snapshot(self, state: WorkflowState, label: str) -> SnapshotRecord:
        labels = [*state.get("snapshot_labels", []), label]
        state["snapshot_labels"] = labels
        record = self.state_store.save_snapshot(state["workflow_id"], label, state)
        state["snapshot_count"] = len(self.state_store.load_snapshots(state["workflow_id"]))
        return record

    def _checkpoint_location(self, workflow_id: str) -> str | None:
        if isinstance(
            self.checkpoint_store,
            (JsonFileCheckpointStore, SQLiteCheckpointStore, PostgresCheckpointStore),
        ):
            return str(self.checkpoint_store.get_path(workflow_id))
        return None

    def load_checkpoints(self, workflow_id: str) -> list[CheckpointRecord]:
        return self.checkpoint_store.load(workflow_id)

    def load_snapshots(self, workflow_id: str) -> list[SnapshotRecord]:
        return self.state_store.load_snapshots(workflow_id)


def build_default_agents(
    provider_registry: ProviderRegistry,
    tool_registry: ToolRegistry,
    knowledge_retriever: LocalKnowledgeRetriever | None,
) -> dict[AgentTarget, BaseAgent]:
    return {
        AgentTarget.RESEARCH: ResearchAgent(
            provider_registry=provider_registry,
            tool_registry=tool_registry,
            knowledge_retriever=knowledge_retriever,
        ),
        AgentTarget.RISK_SCORING: RiskScoringAgent(
            provider_registry=provider_registry,
            tool_registry=tool_registry,
            knowledge_retriever=knowledge_retriever,
        ),
        AgentTarget.COMPLIANCE_REVIEW: ComplianceReviewAgent(
            provider_registry=provider_registry,
            tool_registry=tool_registry,
            knowledge_retriever=knowledge_retriever,
        ),
        AgentTarget.REPORT: ReportGenerationAgent(
            provider_registry=provider_registry,
            tool_registry=tool_registry,
            knowledge_retriever=knowledge_retriever,
        ),
        AgentTarget.HUMAN_REVIEW: HumanReviewAgent(
            provider_registry=provider_registry,
            tool_registry=tool_registry,
            knowledge_retriever=knowledge_retriever,
        ),
    }


def build_default_engine(settings: Settings) -> WorkflowEngine:
    provider_registry = build_default_provider_registry(settings)
    tool_registry = build_default_tool_registry()
    knowledge_retriever = build_default_knowledge_retriever(settings)
    checkpoint_store = build_checkpoint_store(
        settings.checkpoint_backend,
        checkpoint_dir=settings.checkpoint_dir,
        postgres_url=settings.postgres_url,
    )
    state_store = build_runtime_state_store(settings.state_backend, settings.redis_url)
    telemetry = WorkflowTelemetry(enable_logging=settings.enable_telemetry)
    return WorkflowEngine(
        router=PolicyRouter(),
        agents=build_default_agents(provider_registry, tool_registry, knowledge_retriever),
        checkpoint_store=checkpoint_store,
        state_store=state_store,
        telemetry=telemetry,
    )
