"""
EdgeGuard Phase 3 - Resource State Schema
職責：定義資源決策鏈的狀態結構
"""

from typing import TypedDict, Optional, Dict, Any

class ModelRequest(TypedDict):
    hf_path: str
    batch_size: int
    model_size_gb: float

class GpuStatus(TypedDict):
    vram_free_gb: float
    vram_total_gb: float
    gpu_util: float
    temp_c: float

class QuantPlan(TypedDict):
    selected_strategy: str
    config: Dict[str, Any]
    predicted_vram_gb: float
    vram_saving_pct: int
    quality_impact_pct: int
    execution_time_min: int

class PerfResults(TypedDict):
    vram_peak_gb: float
    ttft_ms: float
    tps: float

class DeployDecision(TypedDict):
    approved: bool
    report: str

class ResourceMgmtState(TypedDict):
    model_request: ModelRequest
    gpu_status: GpuStatus
    quant_plan: QuantPlan
    perf_results: PerfResults
    deploy_decision: DeployDecision
