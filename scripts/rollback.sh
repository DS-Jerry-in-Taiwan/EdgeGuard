#!/bin/bash
# EdgeGuard Production Rollback Script

LOG_PATH="./logs/rollback.log"
CONFIG_BAK="config.yaml.bak"
CONFIG_CUR="config.yaml"

echo "$(date) [INFO] Starting rollback..." >> $LOG_PATH

docker-compose -f docker-compose.prod.yml down >> $LOG_PATH 2>&1

if [ -f "$CONFIG_BAK" ]; then
  cp "$CONFIG_BAK" "$CONFIG_CUR"
  echo "$(date) [INFO] Restored config.yaml from backup." >> $LOG_PATH
else
  echo "$(date) [ERROR] Backup config.yaml.bak not found!" >> $LOG_PATH
fi

docker-compose -f docker-compose.prod.yml up -d >> $LOG_PATH 2>&1

sleep 10
python3 scripts/health_check.py >> $LOG_PATH 2>&1

python3 scripts/slack_notifier.py --level critical --message "Rollback completed. Service restored to previous stable version." >> $LOG_PATH 2>&1

echo "$(date) [INFO] Rollback finished." >> $LOG_PATH
