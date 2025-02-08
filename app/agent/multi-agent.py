from langchain_core.messages import SystemMessage, HumanMessage
from langgraph.constants import END, START
from langgraph.graph import StateGraph, MessagesState
from langgraph.types import Command

from model.model import MyModel

teacher_sys_msg = SystemMessage(content="""
    你是一名五年级的语文教师，可以指导学生修改作文，对学生作为给出修改建议，并给出评分，如果学生按照你的建议修改了，评分要对应的提高。
    
    输出结果为JSON，格式如下：
    {
        "score": [作文评分，正整数],
        "content": [作文评价]
    }
""")

student_sys_msg = SystemMessage(
    content="你的作文水平很差，会有语句不通顺、错别字等的问题，在老师的建议下不断完善作文，你水平太差了，不能一次根据老师的建议把作文改好")

# model
student_llm = MyModel()
teacher_llm = MyModel()
teacher_llm = teacher_llm.bind(response_format={"type": "json_object"})


class State(MessagesState):
    score: int


def teacher(state: State):
    """
    优秀的语文老师
    """
    result = teacher_llm.with_structured_output(State, method='json_mode').invoke([teacher_sys_msg] + state["messages"])

    suggest = result["content"]
    score = result["score"]
    return Command(
        update={
            "messages": [
                HumanMessage(content=f"分数：{score}\n建议：{suggest}", name="teacher")
            ],
            "score": score
        }
    )


def student(state: State):
    """
    有点笨的学生
    """
    result = student_llm.invoke([student_sys_msg] + state["messages"])
    return Command(
        update={
            "messages": [
                HumanMessage(content=result.content, name="student")
            ]
        }
    )


def route(state: State):
    score = state["score"]
    if score is None:
        return False
    return score >= 95


# graph
builder = StateGraph(State)
builder.add_node("teacher", teacher)
builder.add_node("student", student)
builder.add_edge(START, "teacher")
builder.add_conditional_edges("teacher", route, {True: END, False: "student"})
builder.add_edge("student", "teacher")

graph = builder.compile()
# graph.get_graph().draw_png("./png/multi-agent.png")

# 调用 Agent，给学生出作文题目，以秋天为题，写一篇200字左右的小作文
messages = graph.invoke(
    {"messages": [
        SystemMessage(content="给学生出作文题目，以秋天为题，写一篇200字左右的小作文")]},
    debug=True)

# 打印结果
for m in messages['messages']:
    m.pretty_print()
