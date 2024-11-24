from pydoc import doc
from llama_index.core import VectorStoreIndex
from llama_index.core.response_synthesizers import CompactAndRefine, SimpleSummarize
from llama_index.core.postprocessor.llm_rerank import LLMRerank
from llama_index.readers.web import SimpleWebPageReader
from llama_index.core.workflow import (
    Context,
    Workflow,
    StartEvent,
    StopEvent,
    step,
)

from llama_index.llms.openai import OpenAI

# from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.llms.ollama import Ollama
from llama_index.embeddings.ollama import OllamaEmbedding

from llama_index.core.workflow import Event
from llama_index.core.schema import NodeWithScore
from llama_index.core.settings import Settings

from llama_index.core.node_parser import SentenceSplitter

node_parser = SentenceSplitter(chunk_size=1024, chunk_overlap=20)

Settings.llm = Ollama(
    model="llama3.1",
)
Settings.embed_model = OllamaEmbedding(
    model_name="nomic-embed-text",
)


class RetrieverEvent(Event):
    """Result of running retrieval"""

    nodes: list[NodeWithScore]


class RerankEvent(Event):
    """Result of running reranking on retrieved nodes"""

    nodes: list[NodeWithScore]


class RAGWorkflow(Workflow):
    @step
    async def ingest(self, ctx: Context, ev: StartEvent) -> StopEvent | None:
        """Entry point to ingest a document, triggered by a StartEvent with `dirname`."""

        website_link = ev.get("website_link")
        if not website_link:
            return None
        documents = SimpleWebPageReader(html_to_text=True).load_data([website_link])

        # for doc in documents:
        #     print(doc.get_content())

        # return

        print("INDEX STARTED", len(documents))

        index = VectorStoreIndex.from_documents(
            documents=documents, show_progress=True, transformations=[node_parser]
        )
        index.as_query_engine()
        print("INDEX COMPELETED")
        return StopEvent(result=index)

    @step
    async def retrieve(self, ctx: Context, ev: StartEvent) -> RetrieverEvent | None:
        "Entry point for RAG, triggered by a StartEvent with `query`."
        query = ev.get("query")
        index = ev.get("index")

        if not query:
            return None

        print(f"Query the database with: {query}")

        # store the query in the global context
        await ctx.set("query", query)

        # get the index from the global context
        if index is None:
            print("Index is empty, load some documents before querying!")
            return None

        retriever = index.as_retriever(similarity_top_k=1)
        nodes = await retriever.aretrieve(query)
        print(f"Retrieved {len(nodes)} nodes.")
        return RetrieverEvent(nodes=nodes)

    # @step
    # async def rerank(self, ctx: Context, ev: RetrieverEvent) -> RerankEvent:
    #     # Rerank the nodes
    #     # ranker = LLMRerank(
    #     #     choice_batch_size=5,
    #     #     top_n=3,
    #     # )
    #     # print(await ctx.get("query", default=None), flush=True)
    #     # new_nodes = ranker.postprocess_nodes(
    #     #     ev.nodes, query_str=await ctx.get("query", default=None)
    #     # )
    #     # new_nodes = retriever.retrieve("Who is Paul Graham?")
    #     # print(f"Reranked nodes to {len(new_nodes)}")
    #     return RerankEvent(nodes=new_nodes)

    @step
    async def synthesize(self, ctx: Context, ev: RetrieverEvent) -> StopEvent:
        """Return a streaming response using reranked nodes."""
        summarizer = CompactAndRefine(verbose=True)
        query = await ctx.get("query", default=None)
        # print("query", query, ev.nodes)
        response = summarizer.synthesize(query, nodes=ev.nodes)
        print("RESPONE", response.content)
        return StopEvent(result=response)


async def main():
    w = RAGWorkflow()
    # Ingest the documents
    index = await w.run(
        website_link="https://aws.amazon.com/what-is/cross-origin-resource-sharing/"
    )

    # Run a query
    await w.run(query="what is cors?", index=index)
    # print(str(result.sysnct))
    # async for chunk in result.async_response_gen():
    #     print(chunk, end="", flush=True)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())


# from llama_index.core.schema import TextNode

# node1 = TextNode(
#     text="Hai hellow how are you my name is boopathi",
# )
# node2 = TextNode(
#     text="Hai hellow how are you.",
# )
# nodes = [node1, node2]
# index = VectorStoreIndex(
#     nodes,
# )
# print(
#     index.as_query_engine(
#         response_synthesizer=CompactAndRefine(verbose=True),
#     ).query("what is here name?")
# )
