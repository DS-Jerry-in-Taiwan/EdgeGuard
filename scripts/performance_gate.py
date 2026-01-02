import json
import yaml

def load_config():
    with open("config.yaml", "r") as f:
        config = yaml.safe_load(f)
    # 預設閾值
    thresholds = config.get("performance_gate", {
        "max_vram_gb": 9.5,
        "max_ttft_s": 0.5,
        "min_tps": 40
    })
    return thresholds

def load_benchmark():
    with open("benchmark_results.json", "r") as f:
        data = json.load(f)
    return data

def load_vram():
    # 假設 benchmark_results.json 有 vram_peak 欄位，否則手動填入
    try:
        with open("benchmark_results.json", "r") as f:
            data = json.load(f)
        vram_peak = data.get("vram_peak", None)
        return vram_peak
    except Exception:
        return None

def main():
    thresholds = load_config()
    bench = load_benchmark()
    vram_peak = load_vram()
    avg_ttft = bench.get("avg_ttft", None)
    tps = bench.get("tps", None)

    # 判斷邏輯
    pass_flag = True
    reasons = []

    if avg_ttft is not None and avg_ttft > thresholds["max_ttft_s"]:
        pass_flag = False
        reasons.append(f"TTFT {avg_ttft:.3f}s > {thresholds['max_ttft_s']}s")
    if tps is not None and tps < thresholds["min_tps"]:
        pass_flag = False
        reasons.append(f"TPS {tps:.2f} < {thresholds['min_tps']}")
    if vram_peak is not None and vram_peak > thresholds["max_vram_gb"]:
        pass_flag = False
        reasons.append(f"VRAM {vram_peak:.2f}GB > {thresholds['max_vram_gb']}GB")

    result = {
        "PASS": pass_flag,
        "reasons": reasons,
        "avg_ttft": avg_ttft,
        "tps": tps,
        "vram_peak": vram_peak
    }
    with open("performance_gate_report.json", "w") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    if pass_flag:
        print("Performance Gate: PASS")
    else:
        print("Performance Gate: FAIL")
        for r in reasons:
            print("Reason:", r)

if __name__ == "__main__":
    main()
