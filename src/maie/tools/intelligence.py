from __future__ import annotations

from maie.domain.models import SignalSource, SupplierSignal
from maie.tools.registry import ToolDefinition, ToolRegistry


def build_default_tool_registry() -> ToolRegistry:
    registry = ToolRegistry()
    registry.register(
        ToolDefinition(
            name="news_search",
            description="Aggregates supplier-specific disruption headlines.",
            handler=_news_search,
            required_args=("supplier_name", "signals"),
        )
    )
    registry.register(
        ToolDefinition(
            name="sec_filings_lookup",
            description="Extracts material financial disclosures for the supplier.",
            handler=_sec_filings_lookup,
            required_args=("supplier_name", "signals"),
        )
    )
    registry.register(
        ToolDefinition(
            name="supplier_profile_lookup",
            description="Returns a risk-oriented supplier profile summary.",
            handler=_supplier_profile_lookup,
            required_args=("supplier_name", "signals"),
        )
    )
    registry.register(
        ToolDefinition(
            name="regional_exposure_map",
            description="Summarizes the geographies exposed by the current signal batch.",
            handler=_regional_exposure_map,
            required_args=("supplier_name", "signals"),
        )
    )
    return registry


def _news_search(supplier_name: str, signals: list[SupplierSignal]) -> dict[str, object]:
    news_signals = [signal for signal in signals if signal.source == SignalSource.NEWS]
    findings = [
        f"{signal.headline} ({signal.region}) severity={signal.severity}"
        for signal in news_signals
    ] or [f"No adverse news found for {supplier_name}; maintain baseline monitoring."]
    return {
        "tool_name": "news_search",
        "summary": f"{len(findings)} news findings collected for {supplier_name}.",
        "findings": findings,
    }


def _sec_filings_lookup(supplier_name: str, signals: list[SupplierSignal]) -> dict[str, object]:
    sec_signals = [signal for signal in signals if signal.source == SignalSource.SEC_FILING]
    findings = [
        f"{signal.headline}: {signal.summary}"
        for signal in sec_signals
    ] or [f"No SEC filing stress signals found for {supplier_name}."]
    return {
        "tool_name": "sec_filings_lookup",
        "summary": f"{len(sec_signals)} regulatory disclosures flagged for {supplier_name}.",
        "findings": findings,
    }


def _supplier_profile_lookup(supplier_name: str, signals: list[SupplierSignal]) -> dict[str, object]:
    max_severity = max((signal.severity for signal in signals), default=1)
    tier = "tier-1 strategic supplier" if max_severity >= 4 else "tier-2 monitored supplier"
    return {
        "tool_name": "supplier_profile_lookup",
        "summary": f"{supplier_name} classified as a {tier}.",
        "findings": [
            f"{supplier_name} has elevated monitoring due to current maximum signal severity of {max_severity}.",
        ],
    }


def _regional_exposure_map(supplier_name: str, signals: list[SupplierSignal]) -> dict[str, object]:
    regions = sorted({signal.region for signal in signals})
    if not regions:
        findings = [f"No regional exposures identified for {supplier_name}."]
    else:
        findings = [f"Current exposure regions: {', '.join(regions)}."]
    return {
        "tool_name": "regional_exposure_map",
        "summary": f"{supplier_name} has signal coverage across {len(regions)} regions.",
        "findings": findings,
    }

