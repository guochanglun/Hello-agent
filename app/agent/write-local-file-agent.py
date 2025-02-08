import os

from langchain_core.messages import HumanMessage
from langgraph.constants import START
from langgraph.graph import StateGraph, MessagesState
from langgraph.prebuilt import ToolNode, tools_condition

from model.model import MyModel


# assistant节点，Agent的大脑，调用大模型接口
def assistant(state: MessagesState):
    message = llm_with_tools.invoke(state["messages"])
    return {"messages": [message]}


# 工具一：当前目录
def cur_dir():
    """
    查询当前目录所在的绝对路径
    :return: 当前目录所在的文件路径
    """
    return os.path.abspath(os.getcwd())


# 工具二：写入文件
def write_file(path, content):
    """
    写入文件
    :param path: 文件路径（包括文件名）
    :param content: 文件内容
    :return: None
    """
    with open(path, 'w', encoding='utf-8') as file:
        file.write(content)


# 构造 LLM Model
tools = [cur_dir, write_file]
llm = MyModel()
llm_with_tools = llm.bind_tools(tools)

# 构造 Graph
builder = StateGraph(MessagesState)
builder.add_node("assistant", assistant)
builder.add_node("tools", ToolNode(tools))
builder.add_edge(START, "assistant")
builder.add_conditional_edges("assistant", tools_condition)
builder.add_edge("tools", "assistant")
graph = builder.compile()

# Graph 可视化
# graph.get_graph().draw_png("write-local-file.png")

# 调用 Agent
messages = graph.invoke(
    {"messages": [HumanMessage(content="写一段生日祝福，100字以内，并写入当前目录的生日祝福.txt文件中。")]})

# 打印结果
for m in messages['messages']:
    m.pretty_print()
