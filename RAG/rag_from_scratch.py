import chromadb
import os
from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction

import google.generativeai as genai


genai.configure(api_key=os.getenv("GOOGLE_GEMENI_API_KEY"))

google_genai = genai.GenerativeModel("gemini-1.5-flash-001")
# response = model.generate_content("The opposite of hot is")

embedding_function = genai.embed_content(
    model="models/embedding-001", google_api_key=os.getenv("GOOGLE_GEMENI_API_KEY")
)


chroma_client = chromadb.Client()
vector_store = chroma_client.get_or_create_collection(
    name="Washington", embedding_function=embedding_function
)


class RAG:
    def retrieve(self, query: str) -> list:
        results = vector_store.query(query_texts=query, n_results=4)
        return [doc for sublist in results["documents"] for doc in sublist]

    def generate_completion(self, query: str, context_str: list) -> str:
        if len(context_str) == 0:
            return "Sorry, I couldn't find an answer to your question."

        completion = (
            google_genai.chat.completions.create(
                model="gpt-3.5-turbo",
                temperature=0,
                messages=[
                    {
                        "role": "user",
                        "content": f"We have provided context information below. \n"
                        f"---------------------\n"
                        f"{context_str}"
                        f"\n---------------------\n"
                        f"First, say hello and that you're happy to help. \n"
                        f"\n---------------------\n"
                        f"Then, given this information, please answer the question: {query}",
                    }
                ],
            )
            .choices[0]
            .message.content
        )
        if completion:
            return completion
        else:
            return "Did not find an answer."

    def query(self, query: str) -> str:
        context_str = self.retrieve(query=query)
        completion = self.generate_completion(query=query, context_str=context_str)
        return completion


rag = RAG()
