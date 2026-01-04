"""
EdgeGuard Phase 3 - GPU Profiler 工具
職責：封裝 nvidia-smi 與 Nsight CLI，提供 GPU/VRAM/溫度/利用率查詢
"""

import subprocess
from typing import Dict, Any, Optional

def query_nvidia_smi() -> Optional[Dict[str, Any]]:
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

def nsight_profile(model_path: str, batch_size: int = 1) -> Dict[str, Any]:
    # TODO: 實際調用 Nsight CLI，這裡僅回傳 stub
    return {
        "kernel_time_ms": 123.4,
        "mem_copy_time_ms": 45.6,
        "compute_util": 0.82
    }

# 單元測試
if __name__ == "__main__":
    print(query_nvidia_smi())
    print(nsight_profile("/models/qwen2.5-7b", 1))
