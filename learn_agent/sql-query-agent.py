from langchain_core.messages import HumanMessage
from langgraph.constants import START
from langgraph.graph import StateGraph, MessagesState
from langgraph.prebuilt import ToolNode, tools_condition
from pymysql import connect

from model.model import GclModel


def assistant(state: MessagesState):
    message = llm_with_tools.invoke(state["messages"])
    return {"messages": [message]}


def execute_sql_query(sql):
    """
    执行SQL查询语句并返回结果
    :return: 查询结果
    """
    config = {
        "host": '10.171.149.97',
        "port": 5002,
        "user": 'rds_erp_mdm',
        "password": 'fvCH8zXh3cdTjf',
        "database": 'finerp_mdm'
    }

    with connect(**config) as conn:
        with conn.cursor() as cursor:
            cursor.execute(sql)
            return cursor.fetchall()


tools = [execute_sql_query]
llm = GclModel()
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
graph.get_graph().draw_png("./png/sql-query-agent.png")

# 调用 Agent
messages = graph.invoke(
    {"messages": [
        HumanMessage(content="查询mdm_customer_info的前10条数据，根据ID倒序，只需要id、customer_id、customer_name、status字段")]},
    debug=True)

# 打印结果
for m in messages['messages']:
    m.pretty_print()
