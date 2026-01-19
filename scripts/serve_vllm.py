import os
import subprocess
import yaml

def load_config(config_path="vllm.env", yaml_path="config.yaml"):
    # 讀取 .env 格式
    env = {}
    if os.path.exists(config_path):
        with open(config_path) as f:
            for line in f:
                if line.strip() and not line.startswith("#"):
                    k, v = line.strip().split("=", 1)
                    env[k] = v
    # 可選：讀取 YAML 進階參數
    if os.path.exists(yaml_path):
        with open(yaml_path) as f:
            yml = yaml.safe_load(f)
            if isinstance(yml, dict):
                env.update({k.upper(): str(v) for k, v in yml.items()})
    return env

def main():
    env = load_config()
    # 組合啟動指令
    cmd = [
        "python3", "-m", "vllm.entrypoints.openai.api_server",
        "--model", env.get("VLLM_MODEL", "/models/quantized"),
        "--dtype", env.get("VLLM_DTYPE", "float16"),
        "--quantization", env.get("VLLM_QUANTIZATION", "awq"),
        "--max-model-len", env.get("VLLM_MAX_MODEL_LEN", "1024"),
        "--gpu-memory-utilization", env.get("VLLM_GPU_MEMORY_UTILIZATION", "0.6"),
        "--max-num-seqs", env.get("VLLM_MAX_NUM_SEQS", "64"),
        "--host", env.get("VLLM_HOST", "0.0.0.0"),
        "--port", env.get("VLLM_PORT", "8000"),
    ]
    print("Launching vLLM API server with:", " ".join(cmd))
    subprocess.run(cmd)

if __name__ == "__main__":
    main()