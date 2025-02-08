## 1.1 Simple Graph

## 定义 state ##############################################################
## The State schema serves as the input schema for all Nodes and Edges in the graph
from typing_extensions import TypedDict


## 定义了一个名为 State 的类型
## 这个类型继承了 TypedDict，声明 State 的实例是一个字典
## 字典中必须包含一个键名为 graph_state，其值的类型必须是 str（TypeDict 的核心作用）
class State(TypedDict):
    graph_state: str  ## 对于 graph_state 这个键，其值必须是 str 类型


## 这里的 State 并不是一个普通的类，它本质上是一个字典模板，实例化后仍然是一个普通的字典
## 作为类型检查工具（再比如 mypy），会确保字典的键和值符合定义
## 没有普通类的方法或动态行为，只是数据结构


## 定义了 3 个节点（函数） ######################################################
## 每个节点都接受一个 State 类型的参数，返回一个 State 类型的结果
def node_1(state):
    print("---Node 1---")
    print(f"state['graph_state'] = {state['graph_state']}")
    return {"graph_state": state['graph_state'] + " I am"}


def node_2(state):
    print("---Node 2---")
    print(f"state['graph_state'] = {state['graph_state']}")
    return {"graph_state": state['graph_state'] + " happy!"}


def node_3(state):
    print("---Node 3---")
    print(f"state['graph_state'] = {state['graph_state']}")
    return {"graph_state": state['graph_state'] + " sad!"}


## 定义了 2 条边 ##############################################################
# 每条边都接受一个 State 类型的参数，返回一个 State 类型的结果
import random
## Literal 的字面意思是“字面值”。这是因为它允许你指定一个变量、参数或函数返回值的类型
## 为某些具体的值（字面值），而不是一个通用的类型
from typing import Literal


## Literal["node_2", "node_3"] 限定了函数 decide_mood 的返回值，只能是 "node_2" 或 "node_3"
def decide_mood(state) -> Literal["node_2", "node_3"]:
    # Often, we will use state to decide on the next node to visit
    user_input = state['graph_state']

    # Here, let's just do a 50 / 50 split between nodes 2, 3
    if random.random() < 0.5:
        # 50% of the time, we return Node 2
        return "node_2"

    # 50% of the time, we return Node 3
    return "node_3"


## 定义了一个简单的图 ############################################################
from IPython.display import Image, display
from langgraph.graph import StateGraph, START, END

# Build graph
builder = StateGraph(State)
builder.add_node("node_1", node_1)
builder.add_node("node_2", node_2)
builder.add_node("node_3", node_3)

# Logic
builder.add_edge(START, "node_1")
builder.add_conditional_edges("node_1", decide_mood)
builder.add_edge("node_2", END)
builder.add_edge("node_3", END)

# Add
graph = builder.compile()

# View
display(Image(graph.get_graph().draw_mermaid_png()))

## 运行图 ############################################################
graph.invoke({"graph_state": "Hi, this is Lance."})

## 案例结束 ###########################################################