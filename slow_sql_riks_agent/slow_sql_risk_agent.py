from langchain_core.messages import SystemMessage, HumanMessage
from langgraph.constants import START
from langgraph.graph import StateGraph, MessagesState
from langgraph.prebuilt import ToolNode, tools_condition

from model.model import GclModel
from slow_sql_risk_tool import extract_sql_from_file, get_table_structure, save_to_file, get_table_indexes, \
    get_table_row_count, explain_sql_query

# 定义模型
llm = GclModel()

# 定义工具
tools = [extract_sql_from_file, save_to_file, get_table_structure, get_table_indexes, get_table_row_count,
         explain_sql_query]

# 绑定工具
llm_with_tools = llm.bind_tools(tools, parallel_tool_calls=False)

# 定义助手
sys_msg = SystemMessage("""
你是一个经验丰富Java开发工程师，对SQL优化存在丰富经验，可以帮我从不同维度去判断一个SQL是否存在慢查询风险。超过 3S 的mysql 查询被认为是慢查询。
把最终结果写入markdown文件中，格式为表格，包含SQL语句、风险概率、风险描述、优化建议列。
""")


def assistant(state: MessagesState):
    message = llm_with_tools.invoke(state["messages"])
    return {"messages": [message]}


# 初始化空状态
workflow_state = StateGraph(MessagesState)
workflow_state.add_node("assistant", assistant)
workflow_state.add_node("tools", ToolNode(tools))

workflow_state.add_edge(START, "assistant")
workflow_state.add_conditional_edges(
    "assistant",
    tools_condition,
)
workflow_state.add_edge("tools", "assistant")

react_graph = workflow_state.compile()

messages = [sys_msg, HumanMessage(
    content="分析这个文件中的SQL存在慢查询风险的概率，/Users/guochanglun/erp-mdm/erp-mdm-dao/src/main/resources/base/sql-mapper/BpmMapper.xml")]
messages = react_graph.invoke({"messages": messages}, debug=True)

## 打印全部结果
for m in messages['messages']:
    m.pretty_print()
