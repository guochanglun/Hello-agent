from langchain_core.messages import SystemMessage, HumanMessage
from langgraph.constants import START
from langgraph.graph import StateGraph, MessagesState
from langgraph.prebuilt import ToolNode, tools_condition
from mcp import StdioServerParameters
from mcpadapt.core import MCPAdapt
from mcpadapt.langchain_adapter import LangChainAdapter

from model.model import GclModel


# 定义assistant节点
def assistant(state: MessagesState):
    message = llm_with_tools.invoke([sys_msg] + state["messages"])
    return {"messages": [message]}


with MCPAdapt(
        StdioServerParameters(
            command='python',
            args=['mysql_mcp_server.py'],
            env=None
        ),
        LangChainAdapter()
) as tools:
    # 定义模型
    llm = GclModel()

    # 绑定工具到 llm 对象
    llm_with_tools = llm.bind_tools(tools, parallel_tool_calls=False)

    # 系统消息
    sys_msg = SystemMessage(content="你是一个经验丰富的数据分析师，可以熟练使用SQL语法，并懂得如何高效的查询数据。")

    # graph
    builder = StateGraph(MessagesState)

    # 增加节点
    builder.add_node("assistant", assistant)
    builder.add_node("tools", ToolNode(tools))

    # 增加边
    builder.add_edge(START, "assistant")
    builder.add_conditional_edges("assistant", tools_condition)
    builder.add_edge("tools", "assistant")
    react_graph = builder.compile(debug=True)

    # prompt
    print("============== 开始执行 ==============")
    messages = [HumanMessage(content="查询mdm_material_info的前10条数据，根据ID倒序")]
    messages = react_graph.invoke({"messages": messages}, debug=True)

    # 打印结果
    for m in messages['messages']:
        m.pretty_print()
