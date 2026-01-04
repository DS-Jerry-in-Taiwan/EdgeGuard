# 基於官方 CUDA + Python 映像（需支援 GPU）
FROM nvidia/cuda:12.1.1-cudnn8-runtime-ubuntu22.04

# 基本環境
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && \
    apt-get install -y python3 python3-pip git curl && \
    rm -rf /var/lib/apt/lists/*

# 建立工作目錄
WORKDIR /app

# 複製 minimal requirements
COPY minimal-requirements.txt ./requirements.txt

# 安裝 Python 依賴（分開安裝便於 debug）
RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt
RUN pip3 install --pre vllm
RUN pip3 install transformers prometheus_client

# 複製啟動腳本（如有自訂）
# COPY scripts/start_vllm.sh ./

# 預設模型目錄（由 docker-compose 掛載）
VOLUME ["/models"]

# 預設啟動命令（可根據實際 API server 調整）
CMD ["python3", "-m", "vllm.entrypoints.openai.api_server", \
     "--model", "/models/quantized", \
     "--dtype", "float16", \
     "--quantization", "awq", \
     "--max-model-len", "4096", \
     "--gpu-memory-utilization", "0.7", \
     "--host", "0.0.0.0", \
     "--port", "8000"]
