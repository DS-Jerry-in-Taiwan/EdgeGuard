#!/bin/bash
# 啟動 Python 虛擬環境，執行 benchmark 與效能檢查

# 切換到專案目錄
cd /home/ubuntu/projects/EdgeGuard

# 啟用虛擬環境
source .venv/bin/activate

# 執行 benchmark 與效能檢查
python scripts/benchmark_client.py && python scripts/performance_gate.py