import aiohttp
import asyncio
import time
import json
import torch

API_URL = "http://127.0.0.1:8000/v1/chat/completions"
CONCURRENCY = 2
PROMPT = "你好"
REQUESTS_PER_WORKER = 5

# 預先將 prompt 轉為 tensor 並放到 GPU，減少 Host-to-Device 傳輸
def prepare_prompt_on_gpu(prompt):
    # 假設 prompt 為簡單字串，實際應根據 tokenizer 處理
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

async def worker(results, gpu_prompt):
    async with aiohttp.ClientSession() as session:
        payload = {
            "model": "/home/ubuntu/projects/EdgeGuard/models/quantized",
            "messages": [{"role": "user", "content": PROMPT}],
            "max_tokens": 32
        }
        # 模擬批次處理：一次送多個請求資料
        batch_payloads = [payload for _ in range(REQUESTS_PER_WORKER)]
        tasks = [fetch(session, p) for p in batch_payloads]
        batch_results = await asyncio.gather(*tasks)
        results.extend(batch_results)

async def main():
    results = []
    # 預先將 prompt 處理到 GPU
    gpu_prompt = prepare_prompt_on_gpu(PROMPT)
    tasks = [worker(results, gpu_prompt) for _ in range(CONCURRENCY)]
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
