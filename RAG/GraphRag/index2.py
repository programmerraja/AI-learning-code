from llama_index.core import SimpleDirectoryReader
from llama_index.core import KnowledgeGraphIndex
from llama_index.core import Settings
from llama_index.core.graph_stores import SimpleGraphStore
from llama_index.core import StorageContext
# from pyvis.network import Network

# from langchain_openai import AzureChatOpenAI
from langchain_openai import AzureOpenAIEmbeddings
from langchain_openai import OpenAIEmbeddings


import logging
import sys
import os

#
logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))

os.environ["OPENAI_API_VERSION"] = "2023-05-15"
os.environ["AZURE_OPENAI_ENDPOINT"] = ""
os.environ["AZURE_OPENAI_API_KEY"] = ""
os.environ["PINECONE_API_KEY"] = ""

os.environ["OPENAI_API_KEY"] = ""

# llm = AzureChatOpenAI(
#     deployment_name="Klenty_turbo_16K",
# )
# embedding = AzureOpenAIEmbeddings(model="embeddings")
embeddings = OpenAIEmbeddings(model="text-embedding-3-large")
documents = SimpleDirectoryReader("./data").load_data()


# setup the service context (global setting of LLM)
# Settings.llm = llm
Settings.chunk_size = 512

# setup the storage context
graph_store = SimpleGraphStore()
storage_context = StorageContext.from_defaults(graph_store=graph_store)

# Construct the Knowlege Graph Undex
index = KnowledgeGraphIndex.from_documents(
    documents=documents,
    max_triplets_per_chunk=3,
    storage_context=storage_context,
    embed_model=embeddings,
    include_embeddings=True,
    llm=None,
)
query = "What is the max cpu usage time?"

query_engine = index.as_query_engine(
    include_text=True,
    response_mode="tree_summarize",
    embedding_mode="hybrid",
    similarity_top_k=5,
)
#
message_template = f"""<|system|>Please check if the following pieces of context has any mention of the  keywords provided in the Question.If not then don't know the answer, just say that you don't know.Stop there.Please donot try to make up an answer.</s>
<|user|>
Question: {query}
Helpful Answer:
</s>"""
#
response = query_engine.query(message_template)
#
print(response.response.split("<|assistant|>")[-1].strip())
