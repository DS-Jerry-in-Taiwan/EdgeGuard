"""
EdgeGuard Phase 3 - ResourceMonitor Agent
職責：即時監控 GPU/VRAM/溫度，預測 OOM 風險，對接 nvidia-smi/Prometheus
"""

import subprocess
import time
from typing import Dict, Any, Optional

def get_nvidia_smi() -> Optional[Dict[str, Any]]:
    try:
        result = subprocess.run(
            ["nvidia-smi", "--query-gpu=memory.free,memory.total,utilization.gpu,temperature.gpu", "--format=csv,noheader,nounits"],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True, text=True
        )
        free, total, util, temp = [float(x) for x in result.stdout.strip().split(",")]
        return {
            "vram_free_gb": round(free / 1024, 2),
            "vram_total_gb": round(total / 1024, 2),
            "gpu_util": util / 100,
            "temp_c": temp
        }
    except Exception as e:
        return None

def risk_level_from_vram(vram_free_gb: float) -> str:
    if vram_free_gb < 2:
        return "critical"
    elif vram_free_gb < 5:
        return "high"
    elif vram_free_gb < 8:
        return "medium"
    else:
        return "safe"

def resource_monitor_agent(model_request: Dict[str, Any]) -> Dict[str, Any]:
    gpu_status = get_nvidia_smi()
    if not gpu_status:
        return {
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "gpu_status": {},
            "risk_level": "unknown",
            "oom_probability": 1.0,
            "recommendation": "nvidia-smi 無法取得資料"
        }
    vram_free = gpu_status["vram_free_gb"]
    risk_level = risk_level_from_vram(vram_free)
    # OOM 概率簡化推估
    if risk_level == "critical":
        oom_prob = 0.99
        rec = "立即阻擋，請釋放資源"
    elif risk_level == "high":
        oom_prob = 0.85
        rec = "強烈建議量化"
    elif risk_level == "medium":
        oom_prob = 0.5
        rec = "建議 INT4 量化"
    else:
        oom_prob = 0.1
        rec = "FP16 可行"
    return {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "gpu_status": gpu_status,
        "risk_level": risk_level,
        "oom_probability": oom_prob,
        "recommendation": rec
    }

# 單元測試
if __name__ == "__main__":
    print(resource_monitor_agent({"hf_path": "Qwen/Qwen2.5-7B", "batch_size": 1}))
