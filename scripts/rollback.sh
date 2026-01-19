#!/bin/bash
# EdgeGuard Production Rollback Script

LOG_PATH="logs/rollback.log"
CONFIG_PATH="./config.yaml"
BACKUP_PATH="./config.yaml.bak"

mkdir -p logs
echo "[`date '+%Y-%m-%d %H:%M:%S'`] Rollback initiated" | tee -a $LOG_PATH

# Step 1: Stop current services
docker-compose -f docker-compose.prod.yml down >> $LOG_PATH 2>&1

# Step 2: Restore previous stable config and model artifacts
if [ -f "$BACKUP_PATH" ]; then
    cp "$BACKUP_PATH" "$CONFIG_PATH"
    echo "[`date '+%Y-%m-%d %H:%M:%S'`] Config restored from backup" | tee -a $LOG_PATH
else
    echo "[`date '+%Y-%m-%d %H:%M:%S'`] No backup config found, aborting rollback" | tee -a $LOG_PATH
    exit 1
fi

if [ -d "./models/quantized.bak" ]; then
    rm -rf ./models/quantized
    cp -r ./models/quantized.bak ./models/quantized
    echo "[`date '+%Y-%m-%d %H:%M:%S'`] Model artifacts restored from backup" | tee -a $LOG_PATH
else
    echo "[`date '+%Y-%m-%d %H:%M:%S'`] No model backup found, aborting rollback" | tee -a $LOG_PATH
    exit 1
fi

# Step 3: Restart services
docker-compose -f docker-compose.prod.yml up -d >> $LOG_PATH 2>&1
echo "[`date '+%Y-%m-%d %H:%M:%S'`] Services restarted" | tee -a $LOG_PATH
sleep 30

# Step 4: Health check
python3 scripts/health_check.py >> $LOG_PATH 2>&1
if [ $? -eq 0 ]; then
    echo "[`date '+%Y-%m-%d %H:%M:%S'`] Rollback completed successfully" | tee -a $LOG_PATH
else
    echo "[`date '+%Y-%m-%d %H:%M:%S'`] Rollback failed health check" | tee -a $LOG_PATH
    exit 2
fi

# Step 5: Slack notification (optional, if slack_notifier.py exists)
if [ -f "scripts/slack_notifier.py" ]; then
    python3 scripts/slack_notifier.py --level critical --message "Rollback completed" --log $LOG_PATH
fi