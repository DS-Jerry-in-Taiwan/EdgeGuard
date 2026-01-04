"""
EdgeGuard Phase 3 - 端到端資源決策鏈測試
測試 ResourceMonitor → QuantOptimizer → PerfValidator 全流程
"""

import unittest
from src.workflows.resource_mgmt_workflow import ResourceMgmtWorkflow

class TestResourceMgmtWorkflow(unittest.TestCase):
    def setUp(self):
        self.workflow = ResourceMgmtWorkflow()

    def test_fp16_safe(self):
        # 充足 VRAM，應選 fp16，部署通過
        from unittest.mock import patch
        with patch("src.agents.resource_monitor.get_nvidia_smi", return_value={
            "vram_free_gb": 10.0, "vram_total_gb": 10.0, "gpu_util": 0.3, "temp_c": 60
        }):
            result = self.workflow.run({"hf_path": "Qwen/Qwen2.5-7B", "batch_size": 1, "model_size_gb": 7.2})
            self.assertEqual(result["quant_plan"]["selected_strategy"], "fp16")
            self.assertTrue(result["deploy_decision"]["approved"])

    def test_awq_int4_high(self):
        # 模擬 VRAM 6GB，應選 awq_int4
        from unittest.mock import patch
        with patch("src.agents.resource_monitor.get_nvidia_smi", return_value={
            "vram_free_gb": 6.0, "vram_total_gb": 10.0, "gpu_util": 0.3, "temp_c": 60
        }):
            result = self.workflow.run({"hf_path": "Qwen/Qwen2.5-7B", "batch_size": 1, "model_size_gb": 7.2})
            self.assertEqual(result["quant_plan"]["selected_strategy"], "awq_int4")
            self.assertTrue(result["deploy_decision"]["approved"])

    def test_q4_k_m_critical(self):
        # 模擬 VRAM 1.5GB，應選 q4_k_m，部署失敗
        from unittest.mock import patch
        with patch("src.agents.resource_monitor.get_nvidia_smi", return_value={
            "vram_free_gb": 1.5, "vram_total_gb": 10.0, "gpu_util": 0.3, "temp_c": 60
        }):
            result = self.workflow.run({"hf_path": "Qwen/Qwen2.5-7B", "batch_size": 1, "model_size_gb": 7.2})
            self.assertEqual(result["quant_plan"]["selected_strategy"], "q4_k_m")
            self.assertFalse(result["deploy_decision"]["approved"])

if __name__ == "__main__":
    unittest.main()
