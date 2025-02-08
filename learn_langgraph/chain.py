from langchain_core.messages import HumanMessage
# for m in messages:
#     m.pretty_print()
#
# ## 调用 OpenAI 的模型，用来构建 agent
from langchain_openai import ChatOpenAI
from pydantic import SecretStr

## 虚构一些人类用户和大模型 AI 的聊天记录
# messages = [AIMessage(content=f"你在找北京的美食吗?", name="Model")]
# messages.append(HumanMessage(content=f"是的.", name="Lance"))
# messages.append(AIMessage(content=f"好的，你想了解什么呢？", name="Model"))
# messages.append(HumanMessage(content=f"我想知道在北京最推荐的美食是什么", name="Lance"))
#
llm = ChatOpenAI(openai_api_base='https://api.deepseek.com',
                 openai_api_key=SecretStr('sk-84f2ed3716b948e4a6e20dfc2540b7ad'),
                 model_name='deepseek-chat', verbose=True)


# result = llm.invoke(messages)
# result.pretty_print()

## 定义一个工具函数
def multiply(a: int, b: int) -> int:
    """Multiply a and b.

    Args:
        a: first int
        b: second int
    """
    return a * b


## 绑定函数到 llm 对象
# llm_with_tools = llm
llm_with_tools = llm.bind_tools([multiply])

## 基于 messages 定义 state


##  AnyMessage 是用来表示消息的泛型类型。这是一种类型注解，表示 messages 列表中的元素可以是任何消息类型，
## 例如 HumanMessage, AIMessage, SystemMessage 或 ToolMessage 等
# class MessagesState(TypedDict):  # 之前我们定义的叫 State; LangGraph 其实自带有 MessageState，下面会正式介绍
#     messages: list[AnyMessage]


## MessagesState
from langgraph.graph import MessagesState

# class MessagesState(MessagesState):
#     # Add any keys needed beyond messages, which is pre-built
#     pass


## Initial state
# initial_messages = [AIMessage(content="你好，需要帮助吗?", name="Model"),
#                     HumanMessage(content="我想了解关于美团的一些信息", name="Lance")]

# # New message to add
# new_message = AIMessage(content="好的，我可以帮助你。你具体想了解哪些信息呢？", name="Model")

# Test
# from langgraph.graph.message import add_messages

# add_messages(initial_messages, new_message)

## 创建图  ############################################################
from langgraph.graph import StateGraph, START, END


# Node
def tool_calling_llm(state: MessagesState):
    return {"messages": [llm_with_tools.invoke(state["messages"])]}


# Build graph
builder = StateGraph(MessagesState)
builder.add_node("tool_calling_llm", tool_calling_llm)
builder.add_edge(START, "tool_calling_llm")
builder.add_edge("tool_calling_llm", END)
graph = builder.compile()

# View
# display(Image(graph.get_graph().draw_mermaid_png()))
#
# ## 运行图 ############################################################
messages = graph.invoke({"messages": HumanMessage(content="你好!")})
for m in messages['messages']:
    m.pretty_print()

messages = graph.invoke({"messages": HumanMessage(content="100乘100等于几？")})
for m in messages['messages']:
    m.pretty_print()

#
# ## 后面的 notebook，会介绍如何执行工具函数，并返回结果
# # END
