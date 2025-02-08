from langchain_core.caches import InMemoryCache
from langchain_core.globals import set_llm_cache

from model.deep_seek_llm import DeepSeekLLM

set_llm_cache(InMemoryCache())

if __name__ == '__main__':
    llm = DeepSeekLLM()
    while True:
        prompt = input("user: ")
        response = llm.invoke(prompt)
        print(f"AI: {response}")
