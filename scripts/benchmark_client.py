import aiohttp
import asyncio
import time
import json
import torch
import os

API_URL = os.environ.get("BENCHMARK_API_URL", "http://127.0.0.1:8000/v1/chat/completions")
CONCURRENCY = int(os.environ.get("BENCHMARK_CONCURRENCY", 1))
PROMPT = "你好"
REQUESTS_PER_WORKER = int(os.environ.get("BENCHMARK_REQUESTS_PER_WORKER", 10))
WARMUP = int(os.environ.get("BENCHMARK_WARMUP", 2))
BATCH_SIZE = int(os.environ.get("BENCHMARK_BATCH_SIZE", 3))

def prepare_prompt_on_gpu(prompt):
    arr = [ord(c) for c in prompt]
    tensor = torch.tensor(arr, dtype=torch.int32).cuda()
    return tensor

async def fetch(session, payload, worker_id, req_id):
    start = time.time()
    # 記錄傳送資料大小
    input_size = len(json.dumps(payload).encode())
    async with session.post(API_URL, json=payload) as resp:
        result = await resp.json()
        end = time.time()
        ttft = end - start
        output = result.get("choices", [{}])[0].get("message", {}).get("content", "")
        return {
            "ttft": ttft,
            "output": output,
            "status": resp.status,
            "input_size": input_size,
            "worker_id": worker_id,
            "req_id": req_id
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
                await fetch(session, payload, worker_id, "warmup")
            except Exception:
                pass
        # 分批送入，減少單次傳輸量
        for batch in range((REQUESTS_PER_WORKER + BATCH_SIZE - 1) // BATCH_SIZE):
            batch_payloads = [payload for _ in range(min(BATCH_SIZE, REQUESTS_PER_WORKER - batch * BATCH_SIZE))]
            tasks = [fetch(session, p, worker_id, batch * BATCH_SIZE + i) for i, p in enumerate(batch_payloads)]
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
    max_input = max(r["input_size"] for r in results)
    max_ttft = max(r["ttft"] for r in results)
    report = {
        "total_requests": len(results),
        "avg_ttft": avg_ttft,
        "max_ttft": max_ttft,
        "tps": tps,
        "max_input_size": max_input,
        "results": results,
        "duration": end - start
    }
    with open("benchmark_results.json", "w") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    print(f"Benchmark completed: {len(results)} requests, avg TTFT={avg_ttft:.3f}s, max TTFT={max_ttft:.3f}s, TPS={tps:.2f}, max input={max_input} bytes")
    for idx, r in enumerate(results):
        print(f"Worker {r['worker_id']} Req {r['req_id']}: TTFT={r['ttft']:.3f}s, Status={r['status']}, Input={r['input_size']} bytes, Output={r['output'][:40]}")

if __name__ == "__main__":
    asyncio.run(main())
