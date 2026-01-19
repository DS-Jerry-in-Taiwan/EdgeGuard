import argparse
import requests
import json
import os
from datetime import datetime

SLACK_WEBHOOK_URL = os.environ.get("SLACK_WEBHOOK_URL", "https://hooks.slack.com/services/your/webhook/url")

def send_slack_notification(level, message, metrics=None, log=None):
    color = {
        "critical": "#ff0000",
        "warning": "#ffae42",
        "info": "#36a64f"
    }.get(level, "#cccccc")
    text = f"*[{level.upper()}]* {message}"
    if metrics:
        text += "\n" + "\n".join([f"{k}: {v}" for k, v in metrics.items()])
    if log and os.path.exists(log):
        with open(log, "r") as f:
            log_tail = "".join(f.readlines()[-10:])
        text += f"\n```{log_tail}```"
    payload = {
        "attachments": [
            {
                "fallback": text,
                "color": color,
                "pretext": f"EdgeGuard Production Alert ({datetime.now().isoformat(timespec='seconds')})",
                "text": text
            }
        ]
    }
    resp = requests.post(SLACK_WEBHOOK_URL, data=json.dumps(payload), headers={"Content-Type": "application/json"})
    if resp.status_code != 200:
        raise Exception(f"Slack notification failed: {resp.text}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--level", required=True, choices=["critical", "warning", "info"])
    parser.add_argument("--message", required=True)
    parser.add_argument("--metrics", type=str, help="JSON string of metrics")
    parser.add_argument("--log", type=str, help="Log file path")
    args = parser.parse_args()
    metrics = json.loads(args.metrics) if args.metrics else None
    send_slack_notification(args.level, args.message, metrics, args.log)