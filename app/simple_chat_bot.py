import uuid

from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import START, MessagesState, StateGraph
from pydantic import SecretStr

# Define a new graph
workflow = StateGraph(state_schema=MessagesState)

# Define a chat model
model = ChatOpenAI(openai_api_base='https://api.deepseek.com',
                   openai_api_key=SecretStr('sk-33c5aa8706fa43ad8d0bb0ad51a43a1e'),
                   model_name='deepseek-chat', verbose=True)


# Define the function that calls the model
def call_model(state: MessagesState):
    response = model.invoke(state["messages"])
    # We return a list, because this will get added to the existing list
    return {"messages": response}


# Define the two nodes we will cycle between
workflow.add_edge(START, "model")
workflow.add_node("model", call_model)

# Adding memory is straight forward in langgraph!
memory = MemorySaver()

app = workflow.compile(
    checkpointer=memory
)

thread_id = uuid.uuid4()
config = {"configurable": {"thread_id": thread_id}}

while True:
    input_str = input("")
    input_message = HumanMessage(content=input_str)
    for event in app.stream({"messages": [input_message]}, config, stream_mode="values"):
        event["messages"][-1].pretty_print()
