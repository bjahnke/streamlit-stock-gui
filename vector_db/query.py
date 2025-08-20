from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.llms.ollama import Ollama
from llama_index.core.retrievers import VectorIndexRetriever

# Load persisted index
index = VectorStoreIndex.from_vector_store(vector_store)

# Connect to local Ollama model (e.g., llama3 or codellama)
llm = Ollama(model="llama3")  # or "codellama:latest"

retriever = VectorIndexRetriever(index=index, similarity_top_k=5)
query_engine = RetrieverQueryEngine(retriever=retriever, llm=llm)

# Ask a question
response = query_engine.query("How does the data loader work?")
print(response)
