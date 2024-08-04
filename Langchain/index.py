from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains import LLMChain
from langchain.chains import SimpleSequentialChain
from langchain_text_splitters import CharacterTextSplitter
from langchain_core.messages import HumanMessage
from langchain_chroma import Chroma

from langchain_openai import AzureChatOpenAI

from langchain_community.document_loaders import TextLoader

import os

os.environ["OPENAI_API_VERSION"] = "2023-05-15"
os.environ["AZURE_OPENAI_ENDPOINT"] = ""
os.environ["AZURE_OPENAI_API_KEY"] = ""

loader = TextLoader("./index.md")

text_splitter = CharacterTextSplitter(
    separator="\n",
    chunk_size=500,
    chunk_overlap=200,
    length_function=len,
    is_separator_regex=False,
)

# llm = ChatOpenAI(api_key="",base_url="")
llm = AzureChatOpenAI(
    deployment_name="model_name",
)
message = HumanMessage(
    content="Translate this sentence from English to French. I love programming."
)
print(llm.invoke([message]))


# text = str()
# print(text)
# a = text_splitter.split_text(text)

# print(len(a))

text = loader.load()

docs = text_splitter.split_documents(text)


# db = chroma(persist_directory="./chroma_db",)
# db = Chroma.from_documents(docs, OpenAIEmbeddings(),persist_directory="./chroma_db")
# db = Chroma(persist_directory="./chroma_db",embedding_function=OpenAIEmbeddings(api_key="",base_url=""))
# db.get()
# # query it
# query = "what is docker"
# docs = db.similarity_search(query)

# print(docs[0].page_content)


# prompt = ChatPromptTemplate.from_messages([
#     ("system", "You are a world class technical documentation writer."),
#     ("user", "{input}")
# ])


# # print(llm.invoke("hello").content)
# chain =prompt | llm

# print(chain.invoke(input="hai").content)


# first_prompt = ChatPromptTemplate.from_template(
#     "What is the best name to describe a company that makes {product}?"
# )
# chain_one = LLMChain(llm=llm, prompt=first_prompt)


# second_prompt = ChatPromptTemplate.from_template(
#     "Write a 20 words description for the following company:{company_name}"
# )
# chain_two = LLMChain(llm=llm, prompt=second_prompt)

# overall_simple_chain = SimpleSequentialChain(chains=[chain_one, chain_two],
#                                              verbose=True
#                                             )
# overall_simple_chain.invoke("gaming laptop")
