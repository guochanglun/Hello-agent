from langchain_openai import ChatOpenAI
from pydantic import SecretStr


class MyModel(ChatOpenAI):
    def __init__(self, verbose: bool = True):
        super().__init__(openai_api_base='https://dashscope.aliyuncs.com/compatible-mode/v1',
                         openai_api_key=SecretStr('<Your-Secret>'),
                         model_name='qwen-plus', verbose=verbose)
