from langchain_text_splitters import CharacterTextSplitter
from langchain_core.messages import HumanMessage
from langchain_chroma import Chroma

# from langchain_pinecone import PineconeVectorStore
from langchain_openai import AzureChatOpenAI
from langchain_openai import AzureOpenAIEmbeddings
from langchain_community.vectorstores import Neo4jVector
from langchain_experimental.graph_transformers import LLMGraphTransformer
from langchain.docstore.document import Document

from langchain_community.document_loaders import TextLoader

import os
import json

from langchain_community.graphs import Neo4jGraph

os.environ["NEO4J_URI"] = ""
os.environ["NEO4J_USERNAME"] = ""
os.environ["NEO4J_PASSWORD"] = ""

graph = Neo4jGraph()


os.environ["OPENAI_API_VERSION"] = "2023-05-15"
os.environ["AZURE_OPENAI_ENDPOINT"] = ""
os.environ["AZURE_OPENAI_API_KEY"] = ""
os.environ["PINECONE_API_KEY"] = ""


llm = AzureChatOpenAI(
    deployment_name="",
)
embedding = AzureOpenAIEmbeddings(model="embeddings")

llm_transformer = LLMGraphTransformer(llm=llm)


loader = TextLoader("../formatedCpuUsage.json")

text_splitter = CharacterTextSplitter(
    separator="\n",
    chunk_size=500,
    chunk_overlap=0,
    length_function=len,
    is_separator_regex=False,
)

text = loader.load()

with open("../formatedCpuUsage.json") as fd:
    docs = []
    for word in json.load(fd):
        docs.append(Document(word))

# docs = text_splitter.split_documents(text)

# print(docs)

# graph_documents = llm_transformer.convert_to_graph_documents(docs)


# graph.add_graph_documents(graph_documents, baseEntityLabel=True, include_source=True)

vector_index = Neo4jVector.from_existing_graph(
    embedding,
    search_type="hybrid",
    node_label="Document",
    text_node_properties=["text"],
    embedding_node_property="embedding",
)
query = "When was the CPU core usage at its minimum?"

print([doc.page_content for doc in vector_index.similarity_search(query, 6)])

# docs = vector_index.similarity_search(query, 3)
# movie_plot_vector = Neo4jVector.from_existing_index(
#     embedding_provider,
#     graph=graph,
#     index_name="moviePlots",
#     embedding_node_property="plotEmbedding",
#     text_node_property="plot",
# )

# result = movie_plot_vector.similarity_search("A movie where aliens land and attack earth.")

# print(docs)

str = ""
for i in docs:
    str += i.page_content


print("DONE")

# print(str)
# print(
#     llm.invoke(
#         "help me answer my question my using below\n context: `\n"
#         + docs[0].page_content
#         + "`\n my question is "
#         + query
#     ).content
# )


# print(llm.invoke([message]))

#  docker run     --restart always     --publish=7474:7474 --publish=7687:7687     --env NEO4J_AUTH=neo4j/123456789  -e NEO4J_dbms_security_procedures_unrestricted=apoc.*   -e NEO4J_dbms_security_procedures_allowlist=apoc.coll.*,apoc.load.*,apoc.meta.*  -e NEO4JLABS_PLUGINS='["apoc"]'   neo4j:5.20.0
