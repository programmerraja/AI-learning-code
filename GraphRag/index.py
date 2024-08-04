import networkx as nx
import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer


class GraphRAG:
    def __init__(self, model_name_or_path, chunk_size=600, overlap_size=100):
        self.chunk_size = chunk_size
        self.overlap_size = overlap_size
        self.tokenizer = AutoTokenizer.from_pretrained(model_name_or_path)
        self.model = AutoModelForSequenceClassification.from_pretrained(
            model_name_or_path, num_labels=8
        )

    def split_documents_into_chunks(self, documents):
        chunks = []
        for doc in documents:
            for i in range(0, len(doc), self.chunk_size - self.overlap_size):
                chunk = doc[i : i + self.chunk_size]
                chunks.append(chunk)
        return chunks

    def extract_elements_from_chunks(self, chunks):
        elements = []
        for chunk in chunks:
            inputs = self.tokenizer(
                chunk, return_tensors="pt", max_length=512, truncation=True
            )
            outputs = self.model(**inputs)
            entities = torch.argmax(outputs.logits[:, :4], dim=1).cpu().numpy()
            relationships = torch.argmax(outputs.logits[:, 4:], dim=1).cpu().numpy()
            elements.extend(
                [
                    (chunk, entity, relationship)
                    for entity, relationship in zip(entities, relationships)
                ]
            )
        return elements

    def summarize_elements(self, elements):
        summaries = []
        for chunk, entity, relationship in elements:
            summary = f"{entity} {relationship} {chunk}"
            summaries.append(summary)
        return summaries

    def build_graph_from_summaries(self, summaries):
        graph = nx.Graph()
        for i, summary in enumerate(summaries):
            graph.add_node(i, summary=summary)
            for j, other_summary in enumerate(summaries):
                if i != j:
                    similarity = self.calculate_similarity(summary, other_summary)
                    if similarity > 0.5:
                        graph.add_edge(i, j, weight=similarity)
        return graph

    def calculate_similarity(self, summary1, summary2):
        print(summary1,summary2,"ss")
        
        inputs = self.tokenizer(
            summary1, summary2, return_tensors="pt", max_length=512, truncation=True
        )
        outputs = self.model(**inputs)
        logits1 = outputs.logits[:, 0]  # Get the logits for the first summary
        logits2 = outputs.logits[:, 1]  # Get the logits for the second summary
        print(logits1,logits2)
        # similarity = torch.cosine_similarity(logits1, logits2, dim=1)
        # return similarity.item()

    def detect_communities(self, graph):
        communities = []
        for community in nx.algorithms.community.asyn_lpa_communities(graph):
            communities.append(list(community))
        return communities

    def generate_summaries_from_communities(self, communities, graph):
        community_summaries = []
        for community in communities:
            community_summary = " ".join(
                [graph.nodes[node]["summary"] for node in community]
            )
            community_summaries.append(community_summary)
        return community_summaries

    def combine_summaries_into_global_answer(self, community_summaries, query):
        global_answer = " ".join(community_summaries)
        return global_answer

    def graph_rag_pipeline(self, documents, query):
        chunks = self.split_documents_into_chunks(documents)
        elements = self.extract_elements_from_chunks(chunks)
        summaries = self.summarize_elements(elements)
        graph = self.build_graph_from_summaries(summaries)
        communities = self.detect_communities(graph)
        community_summaries = self.generate_summaries_from_communities(
            communities, graph
        )
        final_answer = self.combine_summaries_into_global_answer(
            community_summaries, query
        )
        return final_answer


# Example usage
graph_rag = GraphRAG("bert-base-uncased")
documents = [
    "This is a sample document. It has multiple sentences.",
    "Another document with different content.",
]
query = "What is the main topic of the documents?"
answer = graph_rag.graph_rag_pipeline(documents, query)
print(answer)
