#!/bin/bash
# 初始化 EdgeGuard 專案環境

set -e

# Python venv
python3 -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -r requirements.txt

# 建立模型目錄
mkdir -p models/quantized
mkdir -p models/configs

# 建立 config.yaml example（如不存在才建立）
if [ ! -f config.yaml ]; then
  cat > config.yaml <<EOF
model_path: models/qwen2.5-7b
output_dir: models/quantized
quant_dtype: int4
quant_method: awq

performance_gate:
  max_vram_gb: 9.5
  max_ttft_s: 0.5
  min_tps: 40
EOF
  echo "已建立 config.yaml 範例，請依需求修改"
fi

# 下載模型檔（以 Qwen2.5-7B 為例，可依需求更換）
if [ ! -f models/quantized/pytorch_model.bin ]; then
  echo "下載 Qwen2.5-7B 量化模型（請依實際需求修改下載來源）"
  wget -O models/quantized/pytorch_model.bin "https://huggingface.co/Qwen/Qwen2.5-7B/resolve/main/pytorch_model.bin" || echo "請手動下載模型檔"
fi

# 建立模型配置範例
cat > models/configs/qwen2.5-7b.yaml.example <<EOF
# Qwen2.5-7B 模型配置範例
model:
  name: Qwen2.5-7B
  path: ./models/quantized/pytorch_model.bin
  dtype: float16
  quant_method: awq
  max_length: 4096
  tokenizer: QwenTokenizer
EOF

echo "專案初始化完成，請依 README 啟動服務與壓測"
