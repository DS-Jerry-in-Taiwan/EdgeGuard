import aiohttp
import asyncio
import time
import json

API_URL = "http://127.0.0.1:8000/v1/chat/completions"
CONCURRENCY = 2
PROMPT = "你好"
REQUESTS_PER_WORKER = 5

async def fetch(session, payload):
    start = time.time()
    async with session.post(API_URL, json=payload) as resp:
        result = await resp.json()
        end = time.time()
        ttft = end - start
        output = result.get("choices", [{}])[0].get("message", {}).get("content", "")
        return {
            "ttft": ttft,
            "output": output,
            "status": resp.status
        }

async def worker(results):
    async with aiohttp.ClientSession() as session:
        payload = {
            "model": "/home/ubuntu/projects/EdgeGuard/models/quantized",
            "messages": [{"role": "user", "content": PROMPT}],
            "max_tokens": 32
        }
        for _ in range(REQUESTS_PER_WORKER):
            res = await fetch(session, payload)
            results.append(res)

async def main():
    results = []
    tasks = [worker(results) for _ in range(CONCURRENCY)]
    start = time.time()
    await asyncio.gather(*tasks)
    end = time.time()
    tps = sum(len(r["output"]) for r in results) / (end - start)
    avg_ttft = sum(r["ttft"] for r in results) / len(results)
    report = {
        "total_requests": len(results),
        "avg_ttft": avg_ttft,
        "tps": tps,
        "results": results,
        "duration": end - start
    }
    with open("benchmark_results.json", "w") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    print(f"Benchmark completed: {len(results)} requests, avg TTFT={avg_ttft:.3f}s, TPS={tps:.2f}")
    for idx, r in enumerate(results):
        print(f"Request {idx+1}: TTFT={r['ttft']:.3f}s, Status={r['status']}, Output={r['output'][:40]}")

if __name__ == "__main__":
    asyncio.run(main())
