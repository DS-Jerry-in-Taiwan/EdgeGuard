# EdgeGuard 生產環境回滾流程文檔

## 目標
確保部署失敗或異常時，能一鍵還原所有關鍵 artifacts（設定、模型、依賴），保障服務穩定性與一致性。

---

## 回滾觸發時機
- 部署後健康檢查失敗（連續3次/60秒內）
- Prometheus/Alertmanager 發出 Critical 告警
- 人工運維指令（如 Slack 指令）

---

## 回滾步驟

1. **停止服務**
   - 執行 `docker-compose -f docker-compose.prod.yml down`
   - 確保所有容器已停止

2. **還原設定與模型 artifacts**
   - 還原 `config.yaml`：`cp config.yaml.bak config.yaml`
   - 還原模型目錄：`rm -rf models/quantized && cp -r models/quantized.bak models/quantized`
   - 可擴充：還原其他依賴檔案（如 tokenizer、weights、環境變數等）

3. **重啟服務**
   - 執行 `docker-compose -f docker-compose.prod.yml up -d`
   - 等待服務啟動完成

4. **健康檢查驗證**
   - 執行 `python3 scripts/health_check.py`
   - 若健康檢查失敗，記錄日誌並通知運維

5. **發送 Slack 通知**
   - 執行 `python3 scripts/slack_notifier.py --level critical --message "Rollback completed" --log /logs/rollback.log`

6. **日誌與審計**
   - 所有操作記錄於 `/logs/rollback.log`
   - 建議同步更新 docs/agent_context/phase4/06_delivery_record.md

---

## 備份建議

- 每次部署前自動備份 `config.yaml` 與 `models/quantized/` 至 `.bak` 目錄
- 可用 git commit hash 或 timestamp 管理多版本備份
- 定期清理過舊備份，避免磁碟空間不足

---

## 注意事項

- 回滾僅保證 artifacts 完整還原，資料庫/外部資源需另行備份
- 若模型 artifacts 結構有變動，需同步調整回滾腳本
- 回滾後務必執行健康檢查，確保服務可用

---

## 參考腳本

見 `scripts/rollback.sh`，可根據實際需求擴充 artifacts 還原範圍。

---

**狀態**：⏳ 持續優化中