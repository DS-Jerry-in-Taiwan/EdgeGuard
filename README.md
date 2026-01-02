# EdgeGuard

EdgeGuard 是一套針對邊緣 AI 服務可靠性與效能的自動化驗證平台，支援 GPU 推論環境、模型部署、效能基線檢查與多版本壓測。專案設計強調可重現、可擴展、易於 CI/CD 整合。

## 專案特色

- 支援多版本 benchmark 壓測腳本（含 batch/concurrency 參數 sweep）
- 自動化效能門檻檢查（performance_gate.py）
- 完整 .gitignore，避免模型與中間檔污染 git
- 支援多種模型與推論引擎切換
- 可擴展的 agent context 文件結構

## 使用流程

1. **初始化專案**
   ```bash
   bash scripts/init_project.sh
   ```

2. **模型量化（必要步驟）**
   ```bash
   # 以 config.yaml 設定為例，將原始模型量化到 models/quantized/
   python scripts/quantize.py --config config.yaml
   ```

3. **啟動 vLLM 或其他推論服務**

4. **執行 benchmark 壓測**
   ```bash
   # 以預設參數壓測
   python scripts/benchmark_client.py

   # Sweep 參數範例
   BENCHMARK_BATCH_SIZE=2 BENCHMARK_CONCURRENCY=4 python scripts/benchmark_client.py
   ```

5. **效能門檻檢查**
   ```bash
   python scripts/performance_gate.py
   ```

6. **自動化一鍵驗證**
   ```bash
   bash scripts/run_benchmark_and_gate.sh
   ```

## 初始化腳本

建立 `scripts/init_project.sh`：

```bash
#!/bin/bash
# 初始化 EdgeGuard 專案環境

python3 -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -r requirements.txt

echo "專案初始化完成，請依 README 啟動服務與壓測"
```

> 請依需求補充 requirements.txt 內容（如 aiohttp, torch, pyyaml 等）

---

## 模型配置說明

- `models/quantized/config.json`：由 HuggingFace/transformers 或量化腳本自動產生，供框架與推論引擎讀取，屬於標準模型格式。
- `models/configs/*.yaml`：為自訂推論服務、多模型部署或跨框架自動化管理時的擴充配置，方便記錄額外推論參數（如 dtype、tokenizer、max_length、量化方式等）。
  - 若僅用 transformers/vLLM，config.json 已足夠。
  - 若需自動化部署、多模型切換或自訂參數，建議保留 yaml 配置。

兩者可並存，依實際需求選用。

## 目錄結構

```
EdgeGuard/
├── scripts/
│   ├── benchmark_client.py
│   ├── benchmark_client_v1.py
│   ├── benchmark_client_v2.py
│   ├── benchmark_client_v3.py
│   ├── benchmark_client_v4.py
│   ├── performance_gate.py
│   ├── run_benchmark_and_gate.sh
│   ├── run_vllm_nsys.sh
│   └── init_project.sh
├── config.yaml
├── .gitignore
├── README.md
└── ...
```

## 注意事項

- 請勿將 models/ 及 docs/agent_context/ 相關檔案加入 git
- 大型檔案與中間結果已自動排除於 .gitignore
- 如需推送到 GitHub，請先確認無大檔案殘留於 git 歷史

---
