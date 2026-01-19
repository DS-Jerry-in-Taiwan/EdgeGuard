import os
import yaml

def main():
    # 讀取模型路徑與量化參數
    with open("config.yaml", "r") as f:
        config = yaml.safe_load(f)
    model_path = config.get("model_path", "models/qwen2.5-7b")
    output_dir = config.get("output_dir", "models/quantized/")
    quant_dtype = config.get("quant_dtype", "int4")
    quant_method = config.get("quant_method", "awq")

    os.makedirs(output_dir, exist_ok=True)

    # AutoAWQ 量化指令
    # 需先安裝 autoawq: pip install autoawq
    # 產出標準 AWQ 格式，vLLM 直接支援
    print(f"Quantizing {model_path} to {quant_dtype} ({quant_method}) using AutoAWQ ...")
    
    from awq import AutoAWQForCausalLM
    from transformers import AutoTokenizer
    
    # 載入模型與 tokenizer
    model = AutoAWQForCausalLM.from_pretrained(
            model_path,
            trust_remote_code=True
        )
    tokenizer = AutoTokenizer.from_pretrained(
        model_path,
        trust_remote_code=True
    )
    
    # 進行量化（新版 awq API，顯式傳入 tokenizer 以避免 NoneType 問題）
    model.quantize(
        quant_config={
            "quant_method": "awq",
            "zero_point": True,
            "q_group_size": 64,
            "w_bit": 4,
            "version": "gemm"
        },
        tokenizer=tokenizer
    )
    
    # 儲存量化後的模型
    model.save_quantized(output_dir)
    tokenizer.save_pretrained(output_dir)
    
    print(f"Quantized model saved to {output_dir}")

if __name__ == "__main__":
    main()
