## 定义并绑定工具 multiply 函数
from langchain_openai import ChatOpenAI
from pydantic import SecretStr


def multiply(a: int, b: int) -> int:
    """Multiply a and b.

    Args:
        a: first int
        b: second int
    """
    return a * b

llm = ChatOpenAI(openai_api_base='https://api.deepseek.com',
                 openai_api_key=SecretStr('sk-84f2ed3716b948e4a6e20dfc2540b7ad'),
                 model_name='deepseek-chat', verbose=True)
llm_with_tools = llm.bind_tools([multiply])


## 创建图
from IPython.display import Image, display
from langgraph.graph import StateGraph, START, END

## MessagesState is defined with a single messages key
## which is a list of AnyMessage objects and uses the add_messages reducer.
from langgraph.graph import MessagesState
from langgraph.prebuilt import ToolNode
from langgraph.prebuilt import tools_condition

# Node
def tool_calling_llm(state: MessagesState):
    return {"messages": [llm_with_tools.invoke(state["messages"])]}

# Build graph
builder = StateGraph(MessagesState)
builder.add_node("tool_calling_llm", tool_calling_llm) ## 工具调用节点
builder.add_node("tools", ToolNode([multiply])) # 工具节点
builder.add_edge(START, "tool_calling_llm") # 开始节点 --> 工具调用节点
builder.add_conditional_edges( # 工具调用节点 -条件边-> 工具节点
    "tool_calling_llm",
    # If the latest message (result) from assistant is a tool call -> tools_condition routes to tools
    # If the latest message (result) from assistant is a not a tool call -> tools_condition routes to END
    tools_condition,
)
builder.add_edge("tools", END)
graph = builder.compile()

# View
# display(Image(graph.get_graph().draw_mermaid_png()))


## 运行图 ############################################################
from langchain_core.messages import HumanMessage
messages = [HumanMessage(content="你好")]
messages = graph.invoke({"messages": messages})
for m in messages['messages']:
    m.pretty_print()

## 提出一个乘法相关的题目 ################################################
print()
print("*回答问题：What is 2 multiply by 3?")
messages = [HumanMessage(content="What is 2 multiply by 3?.")]
messages = graph.invoke({"messages": messages})
for m in messages['messages']:
    m.pretty_print()