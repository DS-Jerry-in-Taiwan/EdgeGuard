import os
import yaml
from awq import AutoAWQForCausalLM

def main():
    # 讀取模型路徑與量化參數
    with open("config.yaml", "r") as f:
        config = yaml.safe_load(f)
    model_path = config.get("model_path", "models/qwen2.5-7b")
    output_dir = config.get("output_dir", "models/quantized/")
    quant_dtype = config.get("quant_dtype", "int4")
    w_bit = 4 if quant_dtype == "int4" else 8

    os.makedirs(output_dir, exist_ok=True)

    print(f"Loading model from {model_path} ...")
    model = AutoAWQForCausalLM.from_pretrained(model_path)

    from transformers import AutoTokenizer
    tokenizer = AutoTokenizer.from_pretrained(model_path)

    print(f"Quantizing to {quant_dtype} ...")
    quant_config = {
        "zero_point": True,
        "q_group_size": 128,
        "w_bit": w_bit,
        "version": "GEMM"
    }
    model.quantize(
        tokenizer=tokenizer,
        quant_config=quant_config
    )

    model.save_quantized(output_dir)
    print(f"Quantized model saved to {output_dir}")

if __name__ == "__main__":
    main()
