"""手工验证已配置 LLM 服务的连接。"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from llm.qwen_client import QwenClient

# 测试 DeepSeek API 连接
client = QwenClient()
response = client.chat(
    system_prompt="你是一个助手，请用中文回答。",
    user_prompt="请用一句话说明什么是路径规划。",
    temperature=0.3,
)
print(f"LLM 响应: {response}")
print("\n✅ DeepSeek API 连接成功!")
