#!/bin/bash
# 啟動 vLLM 並用 nsys profile，收集完整 GPU 運算資訊

nsys profile --trace=cuda,cudnn,osrt \
  -o ../vllm_profile_report \
  --force-overwrite=true  \
  -- \
  python -m vllm.entrypoints.openai.api_server \
    --model /home/ubuntu/projects/EdgeGuard/models/quantized \
    --dtype float16 \
    --quantization awq \
    --max-model-len 4096 \
    --gpu-memory-utilization 0.7 \
    --host 127.0.0.1 \
    --port 8000