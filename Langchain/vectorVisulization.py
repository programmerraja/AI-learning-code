from langchain_openai import AzureChatOpenAI
from langchain_openai import AzureOpenAIEmbeddings
import json
import pandas as pd

from utils import umap_plot

import os

os.environ["OPENAI_API_VERSION"] = "2023-05-15"
os.environ["AZURE_OPENAI_ENDPOINT"] = ""
os.environ["AZURE_OPENAI_API_KEY"] = ""
os.environ["PINECONE_API_KEY"] = ""

llm = AzureChatOpenAI(
    deployment_name="",
)
embedding = AzureOpenAIEmbeddings(model="embeddings")


cpu_metrics_embedings = []
cpu_metrics = []


with open("./embedding.json") as file:
    cpu_metrics_embedings = json.load(file)

# print(len(cpu_metrics_embedings))

metrics_frame = pd.DataFrame({"text": cpu_metrics})

chart = umap_plot(metrics_frame, cpu_metrics_embedings)
# chart.interactive()
