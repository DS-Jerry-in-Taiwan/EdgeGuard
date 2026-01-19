# EdgeGuard - 邊緣 AI 服務自動化驗證與效能監控平台

## 專案簡介

EdgeGuard 是一套針對邊緣 AI 服務可靠性與效能的自動化驗證平台，具備兩大核心功能：

1. **自動化測試部署**：支援 GPU 推論環境、模型部署、效能基線檢查與多版本壓測，強調可重現、可擴展、易於 CI/CD 整合。
2. **效能評估與監控**：聚焦於服務層監控、深度推論 profiling 及自訂義業務指標，協助用戶即時掌握服務狀態與效能瓶頸。

本平台同時提供 RTX 3080 GPU 的生產級 vLLM 部署解決方案，支援自動化部署、量化模型、健康檢查、回滾機制與即時效能監控。

---

## 主要功能與分層監控架構

EdgeGuard 以「由高階到細節」的分層設計，將自動化部署、監控、回滾、效能分析整合於單一平台：

### 1. 全域監控與異常自動化
- **Prometheus + Grafana**：統一收集 vLLM 服務的 GPU VRAM、TTFT、TPS、GPU 溫度等指標，並可視化於 Grafana。
- **Alertmanager 告警整合**：當 VRAM > 98%、TTFT > 800ms、TPS < 20 或 GPU 過熱時，自動發送 Slack 通知並可觸發自動回滾。
- **/metrics 端點**：vLLM 服務自帶 /metrics，Prometheus 以 15 秒頻率抓取，支援多服務多版本監控。
- **日誌與追蹤**：所有異常事件與回滾操作皆記錄於 /logs，便於審查與效能優化。

### 2. 自動化測試部署與回滾
- **GitHub Actions + self-hosted runner**：自動化部署（可結合健康檢查與 scripts/rollback.sh 實現自動回滾）
- **docker-compose.prod.yml**：一鍵啟動生產環境
- **健康檢查腳本**：scripts/health_check.py 提供自動化健康檢查，可集成至 CI/CD 或監控流程
- **回滾腳本**：scripts/rollback.sh 同時還原 config.yaml 與 models/quantized 目錄，確保部署異常時一鍵恢復穩定狀態
- **詳細回滾與 artifacts 一致性說明**：請參見 [docs/rollback_protocol.md](docs/rollback_protocol.md)

### 3. 服務層監控與瓶頸分析
- **Prometheus/Grafana 監控模板與自動化部署**
- **瓶頸分析**：監控數據可用於分析推理延遲、資源瓶頸（如 OOM、GPU 飽和）、服務重啟等異常，協助快速定位與優化
- **Slack/Alertmanager 整合**：異常自動告警與回滾

### 4. 深度推論效能分析（Profiling）
- **NVIDIA Nsight Systems (nsys) 整合**：可於容器內啟動 nsys，對推論流程進行 GPU kernel trace、memory timeline、CUDA kernel、PCIe 傳輸等細節 profiling
- **Profiling 報告**：nsys 產生 .qdrep/.nsys-rep 檔案，支援離線分析，或透過 nsys-exporter 將部分指標轉為 Prometheus 格式
- **應用場景**：適用於定位單次推論瓶頸、GPU 資源利用率、kernel 排程與記憶體傳輸等底層效能問題，補足 API 層監控無法涵蓋的細節

### 5. 自訂義效能與業務指標
- **自訂指標類型**：可於 API server 內用 prometheus_client 定義如 RAG 準度、召回率、BLEU/ROUGE、推論成功率、延遲分布等 Gauge/Counter/Histogram
- **多模型/多版本/A/B 測試指標收集**，Prometheus/Grafana 可視化

---

## 快速啟動

1. 安裝 NVIDIA 驅動與 Container Toolkit
2. `docker-compose -f docker-compose.prod.yml up --build`
3. 訪問 http://localhost:8000/health 及 /metrics
4. 監控與告警自動啟動，異常自動通知

---

## 參考

- [docs/rollback_protocol.md](docs/rollback_protocol.md)
- [docs/agent_context/phase4/05_validation_checklist.md](docs/agent_context/phase4/05_validation_checklist.md)
- [monitoring/prometheus.prod.yml](monitoring/prometheus.prod.yml)
- [monitoring/alertmanager.yml](monitoring/alertmanager.yml)- 健康檢查腳本（scripts/health_check.py）：提供自動化健康檢查腳本，方便集成至 CI/CD 或監控流程
