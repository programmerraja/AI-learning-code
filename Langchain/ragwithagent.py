from langchain_ollama import ChatOllama
from langchain_ollama import OllamaEmbeddings
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain.tools.retriever import create_retriever_tool
from langchain import hub

from langchain_community.document_loaders import WebBaseLoader
from langchain_community.vectorstores import FAISS

# from langchain_openai import OpenAIEmbeddings
from langchain_openai import ChatOpenAI
from langchain_text_splitters import RecursiveCharacterTextSplitter


# llm = ChatOpenAI(model="gpt-3.5-turbo-0125", temperature=0,api_key=)
llm = ChatOllama(model="gemma")

# llm.invoke("hai")

loader = WebBaseLoader("https://docs.smith.langchain.com/overview")

docs = loader.load()

documents = RecursiveCharacterTextSplitter(
    chunk_size=1000, chunk_overlap=200
).split_documents(docs)

vector = FAISS.from_documents(documents, OllamaEmbeddings(model="nomic-embed-text"))

retriever = vector.as_retriever()

retriever_tool = create_retriever_tool(
    retriever,
    "langsmith_search",
    "Search for information about LangSmith. For any questions about LangSmith, you must use this tool!",
)

tools = [retriever_tool]

prompt = hub.pull("hwchase17/openai-functions-agent")

agent = create_tool_calling_agent(llm, tools, prompt)

agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

agent_executor.invoke({"input": "hi!"})
