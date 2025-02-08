## 定义了 3 个工具函数
from langchain_openai import ChatOpenAI
from pydantic import SecretStr


def multiply(a: int, b: int) -> int:
    """Multiply a and b.

    Args:
        a: first int
        b: second int
    """
    return a * b


# This will be a tool
def add(a: int, b: int) -> int:
    """Adds a and b.

    Args:
        a: first int
        b: second int
    """
    return a + b


def divide(a: int, b: int) -> float:
    """Divide a and b.

    Args:
        a: first int
        b: second int
    """
    return a / b


tools = [add, multiply, divide]
llm = ChatOpenAI(openai_api_base='https://api.deepseek.com',
                 openai_api_key=SecretStr('sk-84f2ed3716b948e4a6e20dfc2540b7ad'),
                 model_name='deepseek-chat', verbose=True)
llm_with_tools = llm.bind_tools(tools)  # 绑定工具函数

## 定义了一个 assistant agent ############################################################
from langgraph.graph import MessagesState
from langchain_core.messages import HumanMessage, SystemMessage

# System message
sys_msg = SystemMessage(content="You are a helpful assistant tasked with performing arithmetic on a set of inputs.")


# Node
def assistant(state: MessagesState):  # state
    return {"messages": [llm_with_tools.invoke([sys_msg] + state["messages"])]}


## 创建图 ############################################################
## 创建一个图
from langgraph.graph import START, StateGraph
from langgraph.prebuilt import tools_condition, ToolNode
from IPython.display import Image, display

# Graph
builder = StateGraph(MessagesState)

# Define nodes: these do the work
builder.add_node("assistant", assistant)
builder.add_node("tools", ToolNode(tools))

# Define edges: these determine how the control flow moves
builder.add_edge(START, "assistant")
builder.add_conditional_edges(
    "assistant",
    # If the latest message (result) from assistant is a tool call -> tools_condition routes to tools
    # If the latest message (result) from assistant is a not a tool call -> tools_condition routes to END
    tools_condition,
)
builder.add_edge("tools", "assistant")  ## 从 tools 节点返回 assistant 节点，形成闭环
react_graph = builder.compile()

# Show
# display(Image(react_graph.get_graph(xray=True).draw_mermaid_png()))

## 运行图 wo Memory ############################################################
## 运行图
messages = [HumanMessage(content="Add 3 and 4.")]
messages = react_graph.invoke({"messages": messages})
print("Without Memory:")
for m in messages['messages']:
    m.pretty_print()

print()
print()

## 运行图 with Memory ############################################################
## 引入 检查点工具 MemorySaver
from langgraph.checkpoint.memory import MemorySaver

memory = MemorySaver()
react_graph_memory = builder.compile(checkpointer=memory)

## 指定一个 thread
config = {"configurable": {"thread_id": "1"}}

## 指定人类的问题输入
messages = [HumanMessage(content="Add 3 and 4.")]

## 运行图
print()
print("*With Memory")
messages = react_graph_memory.invoke({"messages": messages}, config)
for m in messages['messages']:
    m.pretty_print()

## With Memory  ###############################################################
## 通过 config 和 thread_id 指定了一个线程，这样就可以使用之前的对话历史
messages = [HumanMessage(content="Multiply that by 2.")]
messages = react_graph_memory.invoke({"messages": messages}, config)

print()
print("*With Memory +  Multiply that by 2")
for m in messages['messages']:
    m.pretty_print()

## END
