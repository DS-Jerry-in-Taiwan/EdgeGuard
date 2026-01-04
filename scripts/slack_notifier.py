import sys
import json
import requests
import logging

LOG_PATH = "./logs/slack_notifier.log"
WEBHOOK_URL = "https://hooks.slack.com/services/your/webhook/url"

def send_slack(level, message, metrics=None):
    color = {"critical": "#ff0000", "warning": "#ffae42", "info": "#36a64f"}.get(level, "#cccccc")
    payload = {
        "attachments": [
            {
                "color": color,
                "title": f"EdgeGuard Alert [{level.upper()}]",
                "text": message,
                "fields": [{"title": k, "value": str(v), "short": True} for k, v in (metrics or {}).items()]
            }
        ]
    }
    try:
        resp = requests.post(WEBHOOK_URL, data=json.dumps(payload), headers={"Content-Type": "application/json"}, timeout=5)
        resp.raise_for_status()
        logging.info(f"Slack notification sent: {level} - {message}")
        return True
    except Exception as e:
        logging.error(f"Slack notification failed: {str(e)}")
        return False

if __name__ == "__main__":
    import argparse
    logging.basicConfig(filename=LOG_PATH, level=logging.INFO, format="%(asctime)s %(message)s")
    parser = argparse.ArgumentParser()
    parser.add_argument("--level", required=True, choices=["critical", "warning", "info"])
    parser.add_argument("--message", required=True)
    parser.add_argument("--metrics", type=str, default=None)
    args = parser.parse_args()
    metrics = json.loads(args.metrics) if args.metrics else None
    success = send_slack(args.level, args.message, metrics)
    sys.exit(0 if success else 1)
