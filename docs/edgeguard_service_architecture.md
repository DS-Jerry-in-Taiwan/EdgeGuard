# EdgeGuard 調整後服務架構與路徑說明

## 架構概覽

- 主服務容器（API/監控指標收集）：負責推理、API、暴露 /metrics，依賴最小化
- Quantize 子容器：專責模型量化/轉換，獨立依賴環境
- 監控容器（Prometheus）：獨立服務，負責指標抓取、存儲與分析
- 共享資料目錄：`models/output`，主服務與子容器間模型交換

## 目錄與路徑規劃

```
EdgeGuard/
├── docker-compose.yml
├── Dockerfile                # 主服務容器
├── Dockerfile.quantize       # 量化子容器
├── models/
│   ├── raw/                  # 原始模型
│   └── output/               # 量化/轉換後模型（共享 volume）
├── scripts/
│   └── quantize.py           # 量化腳本（僅在 quantize 容器執行）
├── src/
│   └── api_server.py         # 主服務 API
│   └── monitor.py            # 指標收集（暴露 /metrics）
├── monitoring/
│   └── prometheus.prod.yml   # Prometheus 配置（獨立容器）
└── docs/
    └── edgeguard_service_architecture.md # 架構與路徑說明
```

## 服務協作流程

1. 主服務啟動，監控 API/推理服務，掛載 `models/output` 目錄，暴露 /metrics
2. 量化需求時，啟動 quantize 子容器，執行 `scripts/quantize.py`，輸出至 `models/output`
3. 主服務監控 `models/output`，自動或手動 reload 新模型
4. Prometheus 監控容器獨立運行，定期抓取主服務 /metrics 指標

## 說明

- 主服務與量化子容器依賴分離，降低衝突
- 量化腳本僅在 quantize 容器執行，主服務不需特殊科學套件
- 監控服務（Prometheus）獨立運行，主服務僅負責暴露指標
- 所有模型交換均透過共享 volume 完成
