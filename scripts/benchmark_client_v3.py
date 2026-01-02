import aiohttp
import asyncio
import time
import json
import torch
import os

API_URL = os.environ.get("BENCHMARK_API_URL", "http://127.0.0.1:8000/v1/chat/completions")
CONCURRENCY = int(os.environ.get("BENCHMARK_CONCURRENCY", 8))
PROMPT = "你好"
REQUESTS_PER_WORKER = int(os.environ.get("BENCHMARK_REQUESTS_PER_WORKER", 10))
WARMUP = int(os.environ.get("BENCHMARK_WARMUP", 2))

def prepare_prompt_on_gpu(prompt):
    arr = [ord(c) for c in prompt]
    tensor = torch.tensor(arr, dtype=torch.int32).cuda()
    return tensor

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

async def worker(results, gpu_prompt, worker_id):
    async with aiohttp.ClientSession() as session:
        payload = {
            "model": "/home/ubuntu/projects/EdgeGuard/models/quantized",
            "messages": [{"role": "user", "content": PROMPT}],
            "max_tokens": 32
        }
        # WARMUP: 預先送幾個請求，避免首請求慢
        for _ in range(WARMUP):
            try:
                await fetch(session, payload)
            except Exception:
                pass
        # 批次並發請求
        batch_payloads = [payload for _ in range(REQUESTS_PER_WORKER)]
        tasks = [fetch(session, p) for p in batch_payloads]
        batch_results = await asyncio.gather(*tasks)
        results.extend(batch_results)

async def main():
    results = []
    gpu_prompt = prepare_prompt_on_gpu(PROMPT)
    tasks = [worker(results, gpu_prompt, i) for i in range(CONCURRENCY)]
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
