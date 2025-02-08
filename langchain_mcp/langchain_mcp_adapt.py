from langchain_core.messages import SystemMessage, HumanMessage
from langgraph.graph import MessagesState
from langgraph.graph import START, StateGraph
from langgraph.prebuilt import ToolNode
from langgraph.prebuilt import tools_condition
from mcp import StdioServerParameters
from mcpadapt.core import MCPAdapt
from mcpadapt.langchain_adapter import LangChainAdapter

from model.model import GclModel


# 定义assistant节点
def assistant(state: MessagesState):
    message = llm_with_tools.invoke([sys_msg] + state["messages"])
    return {"messages": [message]}


with MCPAdapt(
        # MCP 启动参数
        StdioServerParameters(
            command="npx",
            args=["-y", "@modelcontextprotocol/server-filesystem", "/Users/guochanglun/HelloAgent/langchain_mcp/"],
            env=None
        ),
        LangChainAdapter()
) as tools:
    # 定义模型
    llm = GclModel()

    # 绑定工具到 llm 对象
    llm_with_tools = llm.bind_tools(tools, parallel_tool_calls=False)

    # 系统消息
    sys_msg = SystemMessage(content="你是一个智能助手，可以帮我完成一些操作。")

    # graph
    builder = StateGraph(MessagesState)

    # 增加节点
    builder.add_node("assistant", assistant)
    builder.add_node("tools", ToolNode(tools))

    # 增加边
    builder.add_edge(START, "assistant")
    builder.add_conditional_edges("assistant", tools_condition)
    builder.add_edge("tools", "assistant")
    react_graph = builder.compile()

    # 会依此执行，创建文件夹 - 写入文件
    messages = [HumanMessage(content="先创建一个文件夹 test，然后创建文件 a.txt 并写入内容：'你真棒！'，最后查询文件列表")]
    messages = react_graph.invoke({"messages": messages})

    # 打印结果
    for m in messages['messages']:
        m.pretty_print()
