# Qwen API 客户端（优先使用 Qwen，保留 DeepSeek 作为开发期兼容回退）

import os
import requests
from config import (
    DEEPSEEK_API_BASE_URL,
    DEEPSEEK_MODEL_NAME,
    QWEN_API_BASE_URL,
    QWEN_MODEL_NAME,
)


class QwenClient:
    """本系统以 Qwen 大模型为智能体核心基础模型，对外统一称为 Qwen 多智能体系统"""

    def __init__(self):
        qwen_key = os.getenv("QWEN_API_KEY")
        if qwen_key:
            self.provider = "qwen"
            self.api_key = qwen_key
            self.base_url = QWEN_API_BASE_URL
            self.model = QWEN_MODEL_NAME
            return

        # 兼容开发初期配置：没有 Qwen key 时才回退 DeepSeek。
        deepseek_key = os.getenv("DEEPSEEK_API_KEY")
        if deepseek_key:
            self.provider = "deepseek_compat"
            self.api_key = deepseek_key
            self.base_url = DEEPSEEK_API_BASE_URL
            self.model = DEEPSEEK_MODEL_NAME
            return

        raise RuntimeError(
            "未设置 QWEN_API_KEY；如需使用开发期兼容回退，请设置 DEEPSEEK_API_KEY"
        )

    def chat(self, system_prompt: str, user_prompt: str, temperature: float = 0.3) -> str:
        url = f"{self.base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": temperature,
        }

        response = requests.post(url, json=payload, headers=headers, timeout=120)
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"]
