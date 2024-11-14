from langchain_text_splitters import NLTKTextSplitter
from langchain.text_splitter import MarkdownTextSplitter

# import nltk

# nltk.download("punkt_tab")

text = """## Multi-Agent Orchestrator Flexible and powerful framework for managing multiple AI agents and handling complex conversations

## RAG

RAG stands for **Retrieval Augmented Generation**, which is a technique to **enhance Large Language Models (LLMs) by connecting them to external knowledge bases or datasets.** This approach is crucial when LLMs need to answer questions about specific products, services, or domains they haven't been trained on. A practical example is building a chatbot for a website that needs to provide information about the site's specific products and services.
### **How RAG Works**

The basic version of RAG, called **Naive RAG**, involves several steps:

- **Knowledge Base Preparation:** Dividing the data into smaller chunks, embedding them (converting into numerical representations), and storing them in a vector database.
- **Query Processing:** When a user submits a query, it's embedded and compared to the embedded chunks in the database using semantic matching (a technique to determine the similarity of meaning between pieces of text) to find the most relevant information.
- **Contextualized Response:** The retrieved context is then sent to the LLM along with the original query, allowing the LLM to generate a response informed by the relevant knowledge.
### **RAG Optimization Techniques**

Optimizing a RAG system can be complex, involving several techniques that can be broadly categorized into four buckets:

- **Pre-Retrieval Optimization**: Focusing on improving the quality and retrievability of data before the retrieval process.
- **Retrieval Optimization**: Enhancing the actual retrieval process to find the most relevant context.
- **Post-Retrieval Optimization**: Further refining the retrieved information to ensure its relevance and conciseness.
- **Generation Optimization**: Optimizing how the LLM uses the retrieved context to generate the best possible answer.

### **Specific Examples of RAG Optimization Techniques**

The sources highlight a few specific examples of RAG optimization techniques.

**1. Pre-Retrieval Optimization**

- **Improving Information Density:** Unstructured data often has low information density, meaning the relevant facts are scattered within large volumes of text. This can lead to many chunks being sent to the LLM, increasing costs and the likelihood of errors. One solution is to use an LLM to pre-process and summarize the data into a more factual and concise format. A case study using GPT-4 to summarize financial services web pages showed a **4x reduction in token count**, leading to improved accuracy.
	- GRAPH based RAG
   
- **Query Transformation:** User queries are often poorly worded or overly complex. Query transformation involves rewriting or breaking down queries to improve their clarity and effectiveness for retrieval. LLMs can be used for this task. For example, an LLM can rewrite a query with typos or grammatical errors or break down a complex query into multiple sub-queries. Another example involves handling conversational context by identifying the core query from a series of user interactions, ensuring the retrieval focuses on the current topic and avoids retrieving irrelevant past information.


**2. Retrieval Optimization**

- **Ensemble/Fusion Retriever:** This technique combines traditional keyword search (lexical search) with semantic search (vector search) to improve retrieval effectiveness, especially for domain-specific data where embedding models might not perform well. Two retrievers, one for each search type, run in parallel, and their results are combined using a technique like reciprocal rank fusion to produce a consolidated ranking of relevant chunks. Experiments by Microsoft have shown significant improvement in retrieving high-quality chunks using hybrid retrieval methods.

**3. Post-Retrieval Optimization**

- **Cross-Encoder Reranking:** This technique addresses the limitations of bi-encoder-based semantic search, where a single vector representation for a document might lose crucial context. Reranking involves using a cross-encoder, which processes both the query and the retrieved chunks together to determine their similarity more accurately, effectively reordering the retrieved chunks to prioritize the most relevant ones. This is particularly useful for pushing highly relevant chunks initially ranked lower due to the limitations of bi-encoders to the top of the results list. Due to its computational cost, cross-encoder reranking is typically used as a second stage after an initial retrieval method.
### Chunking Methods

- **Naive chunking**: A simple method that divides text based on a fixed number of characters, often using the `CharacterTextSplitter` in Langchain. It is fast and efficient but may not be the most intelligent approach as it does not account for document structure.

- **Sentence splitting**: This method uses natural language processing (NLP) frameworks like NLTK or SpaCy to split text into sentence-sized chunks. It is more accurate than naive chunking and can handle edge cases.

- **Recursive character text splitting**: This method, implemented using the `RecursiveCharacterTextSplitter` in Langchain, combines character-based splitting with consideration for document structure. It recursively splits chunks based on paragraphs, sentences, and characters, maximizing the information contained within each chunk while adhering to the specified chunk size.

- **Structural chunkers**: Langchain provides structural chunkers for HTML and Markdown documents that split text based on the document's schema, such as headers and subsections. This method is particularly useful for structured documents and allows for the addition of metadata to each chunk, indicating its source and location within the document.

- Semantic Chunking: This strategy uses embedding models to analyze the meaning of sentences and group together sentences that are semantically similar. It results in chunks that are more likely to represent coherent concepts, but it requires more computational resources than other methods. check out the nice article to visulize the chunking [here](https://towardsdatascience.com/a-visual-exploration-of-semantic-text-chunking-6bb46f728e30)

### **Evaluating Chunking Strategies**

Recall is a crucial metric for evaluating the effectiveness of a chunking strategy. It measures the proportion of relevant chunks retrieved in response to a query.

A high recall rate indicates that the chunking strategy is effectively capturing and representing the information in a way that allows for accurate retrieval.

Example:

Imagine a document has been chunked, and a query results in three relevant chunks. The retriever returns five chunks, but only two of those are the relevant ones. In this case:
- Relevant elements = 3
- Retrieved elements that are also relevant = 2
- Therefore, Recall = (2/3) * 100% = 66%
### Retrevial types

Rank GPT
- instead of just querying in vector and sending to LLM after querying ask LLM can you rank the doc that fetched from vecotr db based relvant to the query and again send to LLM with re ranked doc

Multi query retrieval 
- Send the user query to LLM and ask can you suggest revelant query to this query get that and use that query to get from db

Contextual compression
- Ask the LLM can you give relavant part that required for the doc by asking this we reducing the context then again send to LLM

Hypothetical document embedding
- ask LLM to suggest Hypothetical document for query and use that to fetch from DB

### Retrevial Algorithm

- Cosine Similarity and Euclidean Distance
- Graph-Based RAG
- Exact Nearest Neighbor (k-NN) Search
- **Hierarchical Navigable Small Worlds (HNSW)**: A popular ANN algorithm that constructs a graph-like structure for fast similarity searches. It's highly scalable and suited to high-dimensional data.
- **Product Quantization (PQ)**: Used to reduce storage requirements and speed up searches by dividing vectors into smaller, quantized components.
- **Locality-Sensitive Hashing (LSH)**: This algorithm hashes input vectors so that similar vectors map to the same hash, allowing fast lookup based on hash values rather than full comparison
- **BM25 (Best Matching 25)** Unlike vector-based search, which relies on embeddings, BM25 is a term-based algorithm that ranks documents based on the presence and frequency of query terms in the documents.

### RAG Evaluation

RAG Triad of metrics
- Context Relevance -> is retervied context relvant to the query?
- Answer Relevance -> is the response relvant to the query?
- Groundedness -> is response supported by the context?

Framework for eval `trulens_eval`
### RAG Fusion

How it works

1. **Multi-Query Generation:** RAG-Fusion generates multiple versions of the user's original query. As we've discussed above, this is different to single query generation, which traditional RAG does. This allows the system to explore different interpretations and perspectives, which significantly broadens the search's scope and improvs the relevance of the retrieved information. 
	- Use AI to generate the multiple version of the user query 
	
2. **Reciprocal Rank Fusion (RRF):** In this technique, we combine and re-rank search results based on relevance. By merging scores from various retrieval strategies, RAG-Fusion ensures that documents consistently appearing in top positions are prioritized, which makes the response more accurate.

3. **Improved Contextual Relevance:** Because we consider multiple interpretations of the user's query and re-ranking results, RAG-Fusion generates responses that are more closely aligned with user intent, which makes the answers more accurate and contextually relevant.

**Resources**
- [ Not RAG, but RAG Fusion?](https://pub.towardsai.net/not-rag-but-rag-fusion-understanding-next-gen-info-retrieval-477788da02e2)
- https://github.com/Raudaschl/rag-fusion 

###  CRAG

Corrective Retrieval Augmented Generation.The strategy we followed for this let’s say for each topic, we consult the book and identify relevant sections. Before forming an opinion, categorize the gathered information into three groups: `**Correct**`, `**Incorrect**`, and `**Ambiguous**`. Process each type of information separately. Then, based on this processed information, compile and summarize it mentally

**How it works**
- **Retrieval Evaluator:** A lightweight model assesses the relevance of retrieved documents to the input query, assigning a confidence score to each document. This evaluator is fine-tuned on datasets with relevance signals, allowing it to distinguish relevant documents from irrelevant ones, even if they share surface-level similarities with the query.
- **Action Trigger:** Based on the confidence scores, CRAG triggers one of three actions:
    - **Correct:** If at least one document has a high confidence score, CRAG assumes the retrieval is correct and refines the retrieved documents to extract the most relevant knowledge strips.
        - **Example:** If the query is "What is Henry Feilden's occupation?" and a retrieved document mentions Henry Feilden's political affiliation, CRAG would identify this as relevant and refine the document to focus on the information about his occupation.
    - **Incorrect:** If all documents have low confidence scores, CRAG assumes the retrieval is incorrect and resorts to web search for additional knowledge sources.
        - **Example:** If the query is "Who was the screenwriter for Death of a Batman?" and the retrieved documents do not contain the correct information, CRAG would initiate a web search using keywords like "Death of a Batman, screenwriter, Wikipedia" to find more reliable sources.
    - **Ambiguous:** If the confidence scores are neither high nor low, CRAG combines both refined retrieved knowledge and web search results.
- **Knowledge Refinement:** For relevant documents, CRAG employs a decompose-then-recompose approach:
    - It breaks documents into smaller knowledge strips, filters out irrelevant strips based on their relevance scores, and then recomposes the remaining relevant strips into a concise knowledge representation.
- **Web Search:** When the initial retrieval fails, CRAG utilizes web search to find complementary information.
    - It rewrites the input query into keyword-based search queries and prioritizes results from authoritative sources like Wikipedia to mitigate the risk of biases and unreliable information from the open web.
    - The retrieved web content is then refined using the same knowledge refinement method.

Check out implementation from langchain [here](https://langchain-ai.github.io/langgraph/tutorials/rag/langgraph_crag/#use-the-graph)
### Contextual Retrieval

Contextual Retrieval is a technique that enhances the accuracy of retrieving relevant information from a knowledge base, especially when used in Retrieval-Augmented Generation (RAG) systems. It addresses the limitations of traditional RAG, which often disregards context, by adding relevant context to the individual chunks of information before they are embedded and indexed. This process significantly improves the system's ability to locate the most pertinent information.

- This technique applies the BM25 ranking function, which relies on lexical matching for finding specific terms or phrases, to the contextualized chunks.
- Contextual Retrieval leverages AI models like Claude to generate the contextual text for each chunk
- It required more window context model and space


## Retrieval Interleaved Generation (RIG)

A technique devloped by google that enhances the factual accuracy of large language models (LLMs) by integrating structured external data into their responses.Unlike standard LLMs that rely solely on their internal knowledge, RIG dynamically retrieves data from a trusted repository like Data Commons.This allows [RIG](https://research.google/blog/grounding-ai-in-reality-with-a-little-help-from-data-commons/) to provide more accurate and reliable information by leveraging real-time data.

**How it works**

1. **Identifying the Need for External Data**: The LLM recognizes when a query requires external information beyond its internal knowledge, distinguishing between general knowledge and specific data-driven facts.
  
2. **Generating a Natural Language Query**: Once external data is needed, the model generates a natural language query, designed to interact with a data repository like Data Commons, for example, "What was the unemployment rate in California in 2020?"

3. **Fetching and Integrating Data**: The model sends the query to Data Commons through an API, retrieves relevant data from diverse datasets, and seamlessly incorporates it into its response.

4. **Providing a Verified Answer**: The LLM uses the retrieved data to give a reliable, data-backed answer, reducing the risk of hallucinations and improving the trustworthiness of its output.

### Late Chunking

- Let say we have doc as `Berin is captial of germany it is more then 3M population` if we chunk as `Berin is captial of germany` and `it is more then 3M population` in second chunk we loose the context to avoid that 
- We first applies the transformer layer of the embedding model to _the entire text_ or as much of it as possible. This generates a sequence of vector representations for each token that encompasses textual information from the entire text. Subsequently, mean pooling is applied to each chunk of this sequence of token vectors, yielding embeddings for each chunk that consider the entire text's contex
- It required large context window model 

`The process of converting a sequence of embeddings into a sentence embedding is called pooling`

Mean pooling in Natural Language Processing (NLP) is a technique used to create a fixed-size vector representation from a variable-length input sequence, such as a sentence or document. It works by averaging the vectors of all tokens (words or subwords) in the sequence

1. **Tokenization**: The input text is split into tokens (words, subwords, or characters).
2. **Embedding**: Each token is mapped to a corresponding vector using an embedding layer (e.g., pre-trained embeddings like Word2Vec, GloVe, or BERT embeddings).
3. **Mean Pooling**: The vectors of all the tokens in the sequence are averaged to produce a single vector. This can be done by summing the vectors and then dividing by the total number of tokens.

### Astute RAG

To solve the potential conflicts arise between the LLMs’ internal knowledge and external sources. let say what is captial of india? for this LLM answer will be new delhi but we added the context using RAG that has `new york` so there will be conflict to resolve this they introduced this method

**How it works**
- First Astute RAG prompts the LLM with the question and asks it to generate a passage based on its internal knowledge
- Astute RAG combines the generated passage with the retrieved ones using RAG, marking their sources.
- It might go through a few iterations, prompting the LLM to further refine the information by sending both context and asking for good one

**Prompt for first step**

```
Generate a document that provides accurate and relevant information to answer the given question. If the information is unclear or uncertain, explicitly state ’I don’t know’ to avoid any hallucinations. Question: {question} Document
```


Prompt for Iterative Knowledge Consolidation: 

```
Consolidate information from both your own memorized documents and externally retrieved documents in response to the given question. * For documents that provide consistent information, cluster them together and summarize the key details into a single, concise document. * For documents with conflicting information, separate them into distinct documents, ensuring each captures the unique perspective or data. * Exclude any information irrelevant to the query. For each new document created, clearly indicate: Whether the source was from memory or an external retrieval. 
The original document numbers for transparency. 
Initial Context: {context} 
Last Context: {context} 
Question: {question} 
New Context

```

Final prompt

```
Task: Answer a given question using the consolidated information from both your own

memorized documents and externally retrieved documents.

Step 1: Consolidate information

* For documents that provide consistent information, cluster them together and summarize the key details into a single, concise document.
* For documents with conflicting information, separate them into distinct documents, ensuring each captures the unique perspective or data.
* Exclude any information irrelevant to the query.For each new document created, clearly indicate:
* Whether the source was from memory or an external retrieval.
* The original document numbers for transparency.

Step 2: Propose Answers and Assign Confidence For each group of documents, propose a possible answer and assign a confidence score based on the credibility and agreement of the information.

Step 3: Select the Final Answer

After evaluating all groups, select the most accurate and well-supported answer.

Highlight your exact answer within <ANSWER> your answer </ANSWER>.

Initial Context: {context_init}

[Consolidated Context: {context}] # optional

Question: {question}

Answer:
```

`Note: This method only work  if LLM has some knoweledge about the question`
### Resources

**Frameworks and Toolkits for RAG (Retrieval-Augmented Generation)**:
1. **[Pinecone Canopy](https://github.dev/pinecone-io/canopy)**: A framework built by Pinecone for developing vector-based applications.
2. **[FlashRAG](https://github.com/ruc-nlpir/flashrag)**: A Python toolkit for efficient RAG research, designed to support retrieval-augmented generation use cases.
3. **[RAGFlow](https://ragflow.io/)**: An open-source RAG engine focusing on deep document understanding for more advanced RAG applications.

**Courses and Learning Resources**:
1. **[Introduction to RAG by Ben](https://parlance-labs.com/education/rag/ben.html)**: Educational material to help understand the fundamentals and implementation of Retrieval-Augmented Generation (RAG).
2. **[LLM Twin Course](https://github.com/decodingml/llm-twin-course)**: A course focused on using twin architectures for RAG-based research and projects.

 **Research Repositories and Articles**:
1. **[RAG Techniques](https://github.com/NirDiamant/RAG_Techniques)**: A GitHub repository that compiles techniques, methods, and best practices for working with RAG systems.
2. **[Beyond the Basics of RAG](https://github.com/ruc-nlpir/flashrag)**: Advanced topics and concepts for pushing the limits of RAG technology.
3.  [Microsoft AutoGen](https://microsoft.github.io/autogen/)**: A toolkit provided by Microsoft to automate the process of generating language models and leveraging RAG workflows.

---
## Generative Representational Instruction Tuning


## Micro Agent

The idea of a micro agent is to
1. Create a definitive test case that can give clear feedback if the code works as intended or not, and
2. Iterate on code until all test cases pass

https://github.com/BuilderIO/micro-agent 


## Crew AI

Alternative to auto gen



- Shorterm memory
- long term memory
- enitiy memory

Tools
-  Agent Level: The Agent can use the Tool(s) on any Task it performs.
- Task Level: The Agent will only use the Tool(s) when performing that specific Task.

**Note**: Task Tools override the Agent Tools.

## Nerve
 Red team with AI
**[Nerve](https://github.com/evilsocket/nerve) is a tool that creates stateful agents with any LLM — without writing a single line of code.** Agents created with Nerve are capable of both planning and enacting step-by-step whatever actions are required to complete a user-defined task.



## Agent with no code

- [dify](https://github.com/langgenius/dify) 
- https://mindpal.space/



Agent flow
- graph based 
- event based



Unstructured Data for LLM
- https://unstructured.io/ 



https://github.com/WooooDyy/LLM-Agent-Paper-List
"""

text_splitter = NLTKTextSplitter(chunk_size=2000, chunk_overlap=20)
markdownSplitter = MarkdownTextSplitter(chunk_size=2000, chunk_overlap=20)
texts = text_splitter.split_text(text)

# for i in markdownSplitter.create_documents([text]):
#     print(i.page_content)
print(markdownSplitter.create_documents([text])[0].page_content)
print("====================")
print(texts[0])
