from typing import Optional, Any

from langchain_core.callbacks import CallbackManagerForLLMRun
from langchain_core.language_models import LLM
from langchain_core.outputs import ChatResult


class DeepSeekLLM(LLM):

    @property
    def _llm_type(self) -> str:
        return "deepseek"

    def _call(
            self,
            messages: str,
            stop: Optional[list[str]] = None,
            run_manager: Optional[CallbackManagerForLLMRun] = None,
            **kwargs: Any,
    ) -> ChatResult:
        import requests
        api_url = "https://api.deepseek.com/v1/chat/completions"  # 替换为实际API地址
        headers = {
            "Authorization": "Bearer <Your Secret>",
            "Content-Type": "application/json"
        }
        data = {
            "messages": [
                {"role": "user", "content": messages}
            ],
            "model": "deepseek-chat",
            "stream": False
        }
        response = requests.post(api_url, headers=headers, json=data)
        return response.text.choices[0].message.content
