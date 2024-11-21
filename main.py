import sys
import os

from dotenv import load_dotenv, find_dotenv
from langchain_openai import ChatOpenAI

# 从当前文件夹或父文件夹中加载.env文件的配置（成为全局可访问的静态变量）。
load_dotenv(find_dotenv())

# Add the project root dynamically to sys.path
current_file = os.path.abspath(__file__)
project_root = os.path.abspath(os.path.join(current_file, "../../../.."))  # Adjust to project root
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from typing import Annotated, Sequence
from typing_extensions import TypedDict
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages

from langchain_core.messages import HumanMessage, AIMessage
from utilities.create_retriever_from_md_files import create_retriever_from_md_files, find_md_files
from utilities.create_retriever_from_urls import create_retriever_from_urls, load_urls
from utilities.image_saver import save_graph_image
from find_tools import find_tools
from create_graph_with_tools import create_graph_with_tools
from langgraph.checkpoint.memory import MemorySaver


def main():

    # Create tools for the chatbot
    tools = find_tools()
    print("\nCount of tools created: ", len(tools))

    # Create the chatbot model
    llm = ChatOpenAI(model="gpt-4o-mini")
    llm_with_tools = llm.bind_tools(tools)

    # Define the structure of the chatbot's state
    class State(TypedDict):
        messages: Annotated[list, add_messages]

    # Define the chatbot function
    def chatbot(state: State):
        return {"messages": [llm_with_tools.invoke(state["messages"])]}

    # Create the graph with memory
    memory = MemorySaver()
    graph = create_graph_with_tools(tools, chatbot, State, memory)

    # Optional: Visualize the graph structure
    save_graph_image(graph, os.path.basename(__file__))

    # Function to handle conversation updates with thread_id for memory
    def stream_graph_updates(user_input: str, thread_id: str):

        # Stream events and print responses
        events = graph.stream(
            {"messages": [("user", user_input)]}, config, stream_mode="values"
        )
        for event in events:
            message = event["messages"][-1]
            if (isinstance(message, AIMessage) and message.content):
                message.pretty_print()

    # Initial prompt for the chatbot. This can be customized as needed.
    initial_prompt = """
            请优先使用所提供的工具回答用户的问题。
            每当调用了一个工具，请在回答后以如下的格式加以说明：
            “回答这个问题我用到了工具：【工具的名字】”。

            现在，请先说“我发现了以下的工具：”，然后用带序号的列表，列出你所有可用的工具，包括工具名称和工具描述。
            并在之后说“我可以使用这些工具辅助回答您的问题。”
            """

    # Chatbot loop with memory enabled using thread_id
    while True:
        print("==================================== Users can input 'quit' to quit.")
        thread_id = input("Enter a thread ID for this session: ")
        
        config = {"configurable": {"thread_id": thread_id}}
        if (len(graph.get_state(config).values) == 0): # If the graph state is empty, initialize the chatbot
            stream_graph_updates(initial_prompt, thread_id)

        user_input = input("User: ")
        if user_input.lower() == "quit":
            print("Goodbye!")
            break


        stream_graph_updates(user_input, thread_id)


if __name__ == "__main__":
    main()
