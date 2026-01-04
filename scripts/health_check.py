import time
import requests
import logging

LOG_PATH = "./logs/health_check.log"
HEALTH_URL = "http://localhost:8000/health"
MAX_ATTEMPTS = 6
FAIL_THRESHOLD = 3
LATENCY_LIMIT_MS = 100

logging.basicConfig(filename=LOG_PATH, level=logging.INFO, format="%(asctime)s %(message)s")

def check_health():
    fail_count = 0
    latencies = []
    for attempt in range(1, MAX_ATTEMPTS + 1):
        start = time.time()
        try:
            resp = requests.get(HEALTH_URL, timeout=2)
            latency = int((time.time() - start) * 1000)
            latencies.append(latency)
            if resp.status_code == 200 and latency < LATENCY_LIMIT_MS:
                logging.info(f"Attempt {attempt}: OK, Latency: {latency}ms")
            else:
                fail_count += 1
                logging.warning(f"Attempt {attempt}: FAIL, Status: {resp.status_code}, Latency: {latency}ms")
        except Exception as e:
            fail_count += 1
            logging.error(f"Attempt {attempt}: ERROR, {str(e)}")
        time.sleep(10)
        if fail_count >= FAIL_THRESHOLD:
            logging.error("Health check failed 3 times, returning FAIL")
            return 1
    avg_latency = sum(latencies) // len(latencies) if latencies else -1
    logging.info(f"Health check completed, avg latency: {avg_latency}ms, fail count: {fail_count}")
    return 0

if __name__ == "__main__":
    exit(check_health())
