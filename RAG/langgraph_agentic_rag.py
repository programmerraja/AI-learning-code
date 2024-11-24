from pydoc import doc
from typing import Annotated, Literal, TypedDict
from attr import has
from click import prompt
from pydantic import BaseModel

from langchain_core.messages import HumanMessage
from langchain_ollama import ChatOllama, OllamaEmbeddings
from langchain_openai import (
    ChatOpenAI,
    OpenAIEmbeddings,
    AzureChatOpenAI,
    AzureOpenAIEmbeddings,
)
from langchain_chroma import Chroma
from langchain_community.document_loaders import WebBaseLoader

from langchain_core.tools import tool
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph, MessagesState
from langgraph.prebuilt import ToolNode


def get_website_content(website_link):
    loader = WebBaseLoader(website_link)
    docs = loader.load()
    return docs


def web_search(website_link):
    "get content from the website"
    return get_website_content(website_link)


@tool
def retriever(query):
    "will return relavant document from the vector store"
    print("RETERVIER CALLING")
    res = vectorstore.similarity_search(query, k=3)
    return {"context": [c.page_content for c in res].join(" ")}


def ask_human(question):
    # print(question)
    # /input("ask question")
    return {"messages": "summarize"}


class AskHuman(BaseModel):
    """Ask the human a question"""

    question: str


tools = [AskHuman, retriever]

tool_node = ToolNode(tools)

model = AzureChatOpenAI(
    azure_deployment="gpt-4o-mini-2", openai_api_version="2024-08-01-preview"
)
# ChatOllama(
#     model="llama3.1", base_url=""
# ).bind_tools(tools)

embeddings = AzureOpenAIEmbeddings(
    azure_deployment="text-embedding-ada-002",
    openai_api_version="2023-05-15",
    api_key="",
)
# OllamaEmbeddings(
#     model="nomic-embed-text", base_url=""
# )


def should_continue(state: MessagesState) -> Literal["tools", END]:
    # print("should_continue", state)
    messages = state["messages"]
    last_message = messages[-1]
    if hasattr(last_message, "tool_calls"):
        return "tools"
    if hasattr(last_message, "context"):
        return "call_model"
    return END


def call_model(state: MessagesState):
    # print("state", state)
    messages = state["messages"]
    last_message = messages[-1]
    if hasattr(last_message, "context"):
        response = model.invoke(
            f"Answer the question using follwing context\n {last_message.context}"
        )
        print("Response", response)
        return {"messages": [response]}
    # prompt = "You are AI assistant you are answer the user question"
    response = model.invoke(messages)
    # print("Response", response)
    return {"messages": [response]}


def Graph_wrapper(website_link):
    docs = get_website_content(website_link)

    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)

    global vectorstore
    vectorstore = Chroma.from_documents(
        documents=splitter.split_documents(docs), embedding=embeddings
    )
    print("creating graph")

    workflow = StateGraph(MessagesState)

    workflow.add_node("agent", call_model)
    workflow.add_node("tools", tool_node)
    workflow.add_node("ask_human", ask_human)

    # Set the entrypoint as `agent`
    # This means that this node is the first one called
    workflow.add_edge(START, "agent")
    workflow.add_edge("ask_human", "agent")
    workflow.add_edge("agent", "ask_human")

    workflow.add_conditional_edges(
        "agent",
        should_continue,
    )

    workflow.add_edge("tools", "agent")

    checkpointer = MemorySaver()

    app = workflow.compile(checkpointer=checkpointer)

    print("compiled")

    # vectorstore.similarity_search("hai", k=3)
    # # Retrieve and generate using the relevant snippets of the blog.
    # retriever = vectorstore.as_retriever()

    config = {"configurable": {"thread_id": 42}}
    final_state = app.invoke(
        {"messages": [HumanMessage(content="summarize the content form vector db")]},
        config=config,
    )
    print(final_state["messages"][-1].content)


def main():
    # print("Enter the website link to rag with it:  ")
    website_link = (
        "https://docs.llamaindex.ai/en/stable/module_guides/models/"  # input()
    )
    Graph_wrapper(website_link)


main()

#
