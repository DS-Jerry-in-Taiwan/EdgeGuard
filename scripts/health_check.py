import time
import requests
import logging
import sys
from datetime import datetime

LOG_PATH = "logs/health_check.log"
HEALTH_URL = "http://localhost:8000/health"
MAX_LATENCY_MS = 100
MAX_FAILS = 3
CHECK_DURATION = 60  # seconds

import os

def setup_logger():
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
    logging.basicConfig(
        filename=LOG_PATH,
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s"
    )

def main():
    setup_logger()
    import sys
    # 啟動等待與 retry 機制
    for retry in range(3):
        if retry > 0:
            print(f"Health check retry {retry}/3: waiting 30s before next attempt...")
            time.sleep(30)
        try:
            # 嘗試連線一次 /health
            resp = requests.get(HEALTH_URL, timeout=2)
            if resp.status_code == 200:
                print("Initial health check passed, start monitoring...")
                break
        except Exception as e:
            print(f"Initial health check failed: {e}")
        if retry == 2:
            print("Service not ready after 3 attempts, aborting health check.")
            sys.exit(1)
    start = time.time()
    fails = 0
    latencies = []
    attempts = 0

    while time.time() - start < CHECK_DURATION:
        attempts += 1
        try:
            t0 = time.time()
            resp = requests.get(HEALTH_URL, timeout=2)
            latency = int((time.time() - t0) * 1000)
            latencies.append(latency)
            if resp.status_code == 200 and latency < MAX_LATENCY_MS:
                logging.info(f"Health OK, latency={latency}ms")
                print(f"Status: OK, Latency: {latency}ms")
                fails = 0
            else:
                fails += 1
                logging.warning(f"Health FAIL, latency={latency}ms, status={resp.status_code}")
                print(f"Status: FAIL, Latency: {latency}ms, Status: {resp.status_code}")
        except Exception as e:
            fails += 1
            logging.error(f"Health EXCEPTION: {e}")
            print(f"Status: FAIL, Exception: {e}")

        if fails >= MAX_FAILS:
            logging.error("Health check failed 3 times, returning FAIL")
            print("FAIL")
            sys.exit(1)
        time.sleep(1)

    avg_latency = sum(latencies) / len(latencies) if latencies else 0
    logging.info(f"Health check completed, attempts={attempts}, avg_latency={avg_latency:.1f}ms")
    print(f"Health check completed, attempts={attempts}, avg_latency={avg_latency:.1f}ms")
    sys.exit(0)

if __name__ == "__main__":
    main()