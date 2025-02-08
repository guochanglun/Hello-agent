from langchain_core.messages import SystemMessage, HumanMessage
from langchain_openai import ChatOpenAI
from langgraph.constants import START
from langgraph.graph import StateGraph, END, MessagesState
from langgraph.prebuilt import ToolNode, tools_condition
from pydantic import SecretStr

from slow_sql_risk_tool import extract_sql_from_file, detect_sql_anti_pattern, explain_sql_execution_plan, \
    evaluate_table_size, save_to_file

# 定义模型
llm = ChatOpenAI(openai_api_base='https://api.deepseek.com',
                 openai_api_key=SecretStr('sk-84f2ed3716b948e4a6e20dfc2540b7ad'),
                 model_name='deepseek-chat', verbose=True)

# 定义工具
# tools = [extract_sql_from_file, detect_sql_anti_pattern, explain_sql_execution_plan, evaluate_table_size]
tools = [extract_sql_from_file, detect_sql_anti_pattern, save_to_file]

# 绑定工具
llm_with_tools = llm.bind_tools(tools, parallel_tool_calls=False)

# 定义助手
sys_msg = SystemMessage("""
你是一个经验丰富Java开发工程师，对SQL优化存在丰富经验，可以帮我从不同维度去判断一个SQL是否存在慢查询风险。超过 3S 的mysql 查询被认为是慢查询。
把最终结果写入markdown文件中，格式为表格，包含SQL语句、风险概率、风险描述、优化建议列。
""")

def assistant(state: MessagesState):
    message = llm_with_tools.invoke([sys_msg] + state["messages"])
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

messages = [HumanMessage(content="分析这个文件中的SQL存在慢查询风险的概率，/Users/guochanglun/erp-mdm/erp-mdm-dao/src/main/resources/base/sql-mapper/BpmMapper.xml")]
messages = react_graph.invoke({"messages": messages})

## 打印全部结果
for m in messages['messages']:
    m.pretty_print()
