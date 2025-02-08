from langchain_openai import ChatOpenAI
from pydantic import SecretStr


class GclModel(ChatOpenAI):
    def __init__(self, verbose: bool = True):
        super().__init__(openai_api_base='https://dashscope.aliyuncs.com/compatible-mode/v1',
                         openai_api_key=SecretStr('sk-b6a3758602c34c739cea457fba04349e'),
                         model_name='qwen-plus', verbose=verbose)
