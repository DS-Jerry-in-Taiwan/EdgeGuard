"""
EdgeGuard Phase 3 - Resource Management Workflow
職責：串接 ResourceMonitor → QuantOptimizer → PerfValidator，實現資源感知決策鏈
"""

from typing import Dict, Any

class ResourceMgmtWorkflow:
    def __init__(self):
        self.state = {
            "model_request": None,
            "gpu_status": None,
            "quant_plan": None,
            "perf_results": None,
            "deploy_decision": None
        }

    def run(self, model_request: Dict[str, Any]) -> Dict[str, Any]:
        from src.agents.resource_monitor import resource_monitor_agent
        from src.agents.quant_optimizer import quant_optimizer_agent
        from src.agents.perf_validator import perf_validator_agent

        self.state["model_request"] = model_request
        # 兼容測試 mock patch，直接傳遞 gpu_status 給 quant_optimizer
        gpu_status = resource_monitor_agent(model_request)
        if "vram_free_gb" not in gpu_status and "gpu_status" in gpu_status:
            # 測試 patch 傳回的已是 gpu_status 結構
            gpu_status = gpu_status["gpu_status"]
        self.state["gpu_status"] = gpu_status
        self.state["quant_plan"] = quant_optimizer_agent(model_request, self.state["gpu_status"])
        self.state["perf_results"] = perf_validator_agent(self.state["quant_plan"], model_request)
        self.state["deploy_decision"] = {
            "approved": self.state["perf_results"]["deploy_approved"],
            "report": self.state["perf_results"]["report_path"]
        }
        return self.state

# 單元測試
if __name__ == "__main__":
    workflow = ResourceMgmtWorkflow()
    result = workflow.run({"hf_path": "Qwen/Qwen2.5-7B", "batch_size": 1, "model_size_gb": 7.2})
    print(result)
