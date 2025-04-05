import fs from "fs";
import {
  Document,
  VectorStoreIndex,
  Settings,
  SentenceSplitter,
} from "llamaindex";

import { QdrantVectorStore } from "@llamaindex/qdrant";

import { OpenAI, OpenAIEmbedding } from "@llamaindex/openai";

// import { SemanticSplitterNodeParser } from "@llamaindex/node-parser";

process.env.OPENAI_API_KEY = "";

// process.env.AZURE_OPENAI_KEY = "";
// process.env.AZURE_OPENAI_ENDPOINT = "";
// process.env.AZURE_OPENAI_DEPLOYMENT = "";

Settings.llm = new OpenAI({
  model: "gpt-4o-mini",
});

Settings.embedModel = new OpenAIEmbedding({
  model: "text-embedding-3-large",
});

async function indexData() {
  const essay = fs.readFileSync("./test.txt", "utf-8");

  const document = new Document({ text: essay, id_: "./test.txt" });

  const qdrantVectorStore = new QdrantVectorStore({
    url: "http://localhost:6333",
    collectionName: "call-agent",
  });

  const index = await VectorStoreIndex.fromDocuments([document], {
    vectorStores: { TEXT: qdrantVectorStore },
  });
}

async function query() {
  const qdrantVectorStore = new QdrantVectorStore({
    url: "http://localhost:6333",
    collectionName: "call-agent2",
  });

  const index = await VectorStoreIndex.fromVectorStore(qdrantVectorStore);

  const queryEngine = index.asQueryEngine();

  const { message, sourceNodes } = await queryEngine.query({
    query: "claim in progress",
  });
  console.log(message);

  if (sourceNodes) {
    sourceNodes.forEach((source, index) => {
      console.log(source);
    });
  }
}

query();
