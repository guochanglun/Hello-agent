## 定义多个工具，让大模型进行调用

from langchain_openai import ChatOpenAI
from pydantic import SecretStr


def multiply(a: int, b: int) -> int:
    """Multiply a and b.

    Args:
        a: first int
        b: second int
    """
    print(f"call multiply {a}, {b}")
    return a * b


# This will be a tool
def add(a: int, b: int) -> int:
    """Adds a and b.

    Args:
        a: first int
        b: second int
    """
    print(f"call add {a}, {b}")
    return a + b


def divide(a: int, b: int) -> float:
    """Divide a and b.

    Args:
        a: first int
        b: second int
    """
    print(f"call divide {a}, {b}")
    return a / b


tools = [add, multiply, divide]
llm = ChatOpenAI(openai_api_base='https://api.deepseek.com',
                 openai_api_key=SecretStr('sk-84f2ed3716b948e4a6e20dfc2540b7ad'),
                 model_name='deepseek-chat', verbose=True)

# 在此 ipynb 文件中，我们将`并行工具调用`设置为 False，因为数学通常是按顺序完成的。这次我们有三个可以处理数学的工具。
# OpenAI 模型默认使用并行工具调用以提高效率，请参阅相关文档。
# 尝试调试一下，看看模型在处理数学方程时的行为如何！

## 绑定工具到 llm 对象
llm_with_tools = llm.bind_tools(tools, parallel_tool_calls=False)

## 让我们创建我们的 LLM 和提示词模板，并通过一个期望的整体代理行为提示，来进行初始化。 ########################
from langgraph.graph import MessagesState
from langchain_core.messages import SystemMessage, HumanMessage

# System message
sys_msg = SystemMessage(content="你是一个数学天才，可以帮我解决复杂的数学计算问题。解决问题并给出解题思路和步骤。")


# Node
def assistant(state: MessagesState):
    message = llm_with_tools.invoke([sys_msg] + state["messages"])
    # print([sys_msg] + state["messages"])
    # print(json_dump(message))
    return {"messages": [message]}


## 创建图 ############################################################
from langgraph.graph import START, StateGraph
from langgraph.prebuilt import tools_condition
from langgraph.prebuilt import ToolNode

# Graph
builder = StateGraph(MessagesState)

# Define nodes: these do the work
builder.add_node("assistant", assistant)  ## 大模型助手节点，决定是否需要调用工具
builder.add_node("tools", ToolNode(tools))  ## 工具节点，运行函数工具

# Define edges: these determine how the control flow moves
builder.add_edge(START, "assistant")  # 普通边
builder.add_conditional_edges(  # 条件边
    "assistant",
    # If the latest message (result) from assistant is a tool call -> tools_condition routes to tools
    # If the latest message (result) from assistant is a not a tool call -> tools_condition routes to END
    tools_condition,
)
builder.add_edge("tools", "assistant")  # 这里加了一条返回的边，形成闭环。
react_graph = builder.compile()

## 显示图的架构
# image = Image(react_graph.get_graph(xray=True).draw_mermaid_png())
# with open('output_image.png', 'wb') as f:
#     f.write(image.data)

# 运行图 ############################################################
# 运行图
messages = [HumanMessage(content="3加4，把结果乘以2，再把结果除以5，最终结果是多少？")]
messages = react_graph.invoke({"messages": messages})

## 打印全部结果
for m in messages['messages']:
    m.pretty_print()
