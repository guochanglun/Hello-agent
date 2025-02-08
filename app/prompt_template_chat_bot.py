from langchain_core.prompts import ChatPromptTemplate

from model.deep_seek_llm import DeepSeekLLM

if __name__ == '__main__':
    # 系统prompt
    system_template = "你是个资深的心理咨询师，帮助我解决心理问题"

    template = ChatPromptTemplate.from_messages([("system", system_template), ("user", "{text}")])
    prompt = template.invoke({"text": "你好，我最近工作好累啊"})

    llm = DeepSeekLLM()
    response = llm.invoke(prompt)
    print(response)
