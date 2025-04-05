import os
import qdrant_client as client
from llama_index.vector_stores.qdrant import QdrantVectorStore
from llama_index.core import VectorStoreIndex, StorageContext, Document
from llama_index.core.node_parser import SemanticSplitterNodeParser
from qdrant_client.http.models import Filter, FieldCondition, MatchValue
from llama_index.llms.azure_openai import AzureOpenAI
from llama_index.embeddings.azure_openai import AzureOpenAIEmbedding

from code_to_summary import getSummary

llm = AzureOpenAI(
    deployment_name="gpt-4o-mini", api_key=os.getenv("AZURE_OPENAI_API_KEY")
)

embed_model = AzureOpenAIEmbedding(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"), deployment_name="text-embedding-3-large"
)
qdrant_client = client.QdrantClient(
    url=os.getenv("QDRANT_URI"),
    api_key=os.getenv("QDRANT_API_KEY"),
    port=None,
)


def build_kg(data, col_name, reIndex, key):
    document_with_meta = []
    splitter = SemanticSplitterNodeParser(embed_model=embed_model)

    for doc in data:

        if reIndex:
            doc["summary"] = getSummary(doc["code"], doc["component"])
            result = qdrant_client.query_points(
                collection_name=col_name,
                query_filter=Filter(
                    must=[
                        FieldCondition(
                            key=key,
                            match=MatchValue(value=doc["component"]),
                        ),
                    ]
                ),
                limit=1,
            )
            doc["parent"] = result.points[0].payload["parent"]
            qdrant_client.delete(
                collection_name=col_name,
                points_selector=Filter(
                    must=[
                        FieldCondition(
                            key=key,
                            match=MatchValue(value=doc["component"]),
                        ),
                    ]
                ),
                wait=True,
            )
        document = Document(
            text=doc["summary"],
            metadata={
                "component": doc["component"],
                "parent": doc["parent"],
                "filePath": doc["filePath"],
            },
        )

        document_with_meta.append(document)

    nodes = splitter.get_nodes_from_documents(document_with_meta, show_progress=True)
    vector_store = QdrantVectorStore(client=qdrant_client, collection_name=col_name)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    VectorStoreIndex(nodes, storage_context=storage_context, embed_model=embed_model)
    print(f"done indexing documents for {col_name}")


