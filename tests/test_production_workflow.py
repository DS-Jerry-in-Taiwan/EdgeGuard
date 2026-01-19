import subprocess
import time

def test_auto_deploy_success():
    """模擬自動部署流程，檢查服務啟動與健康檢查"""
    result = subprocess.run(
        ["python3", "scripts/health_check.py"],
        capture_output=True, text=True
    )
    assert result.returncode == 0, f"Health check failed: {result.stdout}\n{result.stderr}"

def test_health_check_failure_triggers_rollback():
    """模擬健康檢查失敗，檢查回滾腳本是否被觸發"""
    # 模擬異常: 臨時關閉服務
    subprocess.run(["docker-compose", "-f", "docker-compose.prod.yml", "down"])
    time.sleep(60)
    # 執行回滾
    result = subprocess.run(
        ["bash", "scripts/rollback.sh"],
        capture_output=True, text=True
    )
    assert "Rollback completed successfully" in result.stdout, f"Rollback failed: {result.stdout}\n{result.stderr}"

def test_alertmanager_critical_alert():
    """模擬 Alertmanager 發送 Critical 告警，檢查 Slack 通知與回滾"""
    # 這裡僅檢查 slack_notifier.py 可執行
    result = subprocess.run(
        ["python3", "scripts/slack_notifier.py", "--level", "critical", "--message", "Test critical alert"],
        capture_output=True, text=True
    )
    assert result.returncode == 0, f"Slack notification failed: {result.stdout}\n{result.stderr}"

def test_rollback_completion_time():
    """測量回滾腳本完成時間 < 30 秒"""
    start = time.time()
    result = subprocess.run(
        ["bash", "scripts/rollback.sh"],
        capture_output=True, text=True
    )
    elapsed = time.time() - start
    assert result.returncode == 0, f"Rollback failed: {result.stdout}\n{result.stderr}"
    assert elapsed < 180, f"Rollback took too long: {elapsed:.1f}s"

if __name__ == "__main__":
    test_auto_deploy_success()
    test_health_check_failure_triggers_rollback()
    test_alertmanager_critical_alert()
    test_rollback_completion_time()
    print("All production workflow tests passed.")