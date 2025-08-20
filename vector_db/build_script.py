from pathlib import Path
from llama_index.core import (
    SimpleDirectoryReader,
    VectorStoreIndex,
    StorageContext,
    Settings,
)
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.core.retrievers import VectorIndexRetriever
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.llms.ollama import Ollama
import chromadb
from chromadb.config import Settings as ChromaSettings
import pathspec


# --- Configuration ---
PROJECT_DIR = Path("/home/brian/repos").resolve()
CHROMA_DIR = Path("/home/brian/chroma_storage").resolve()
COLLECTION_NAME = "my_codebase"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
OLLAMA_MODEL = "codellama:instruct"
IGNORE_FILE = Path('.') / 'vector-db' / ".llamaignore"


class IndexBuilder:
    """
    Builds a Chroma-backed vector index from source files using LlamaIndex.
    """

    def __init__(self, project_dir, chroma_dir, collection_name, model_name, ignore_file):
        """
        Initialize the IndexBuilder.

        :param project_dir: Path to the root directory containing source files.
        :param chroma_dir: Directory where ChromaDB will persist its storage.
        :param collection_name: Name of the vector collection in Chroma.
        :param model_name: Name of the HuggingFace embedding model to use.
        :param ignore_file: Path to a .llamaignore or .gitignore-style file.
        """
        self.project_dir = Path(project_dir).resolve()
        self.chroma_dir = Path(chroma_dir).resolve()
        self.collection_name = collection_name
        self.model_name = model_name
        self.ignore_file = Path(ignore_file).resolve()
        self.index = None

    def load_ignore_spec(self):
        """
        Load ignore patterns from the .llamaignore file using gitwildmatch syntax.

        :returns: A compiled PathSpec object for matching excluded files.
        """
        if self.ignore_file.exists():
            with open(self.ignore_file) as f:
                return pathspec.PathSpec.from_lines("gitwildmatch", f)
        return pathspec.PathSpec([])

    def get_valid_files(self, spec):
        """
        Recursively collect valid file paths from the project directory.

        :param spec: A PathSpec object used to exclude ignored files.
        :returns: A list of file paths as strings.
        """
        all_files = self.project_dir.rglob("*")
        return [
            str(f.resolve()) for f in all_files
            if f.is_file() and not spec.match_file(str(f.relative_to(self.project_dir)))
        ]

    def load_documents(self, files):
        """
        Load documents from the given list of file paths.

        :param files: List of full file paths.
        :returns: List of Document objects.
        """
        return SimpleDirectoryReader(input_files=files).load_data()

    def setup_embeddings(self):
        """
        Set up the global embedding model using the HuggingFace embedding backend.
        """
        Settings.embed_model = HuggingFaceEmbedding(model_name=self.model_name)

    def setup_vector_store(self):
        """
        Initialize and return a persistent Chroma vector store.

        :returns: An instance of ChromaVectorStore.
        """
        client = chromadb.PersistentClient(path=str(self.chroma_dir))
        collection = client.get_or_create_collection(self.collection_name)
        return ChromaVectorStore(chroma_collection=collection)

    def build_index(self, documents, vector_store):
        """
        Build the VectorStoreIndex from the given documents and vector store.

        :param documents: A list of LlamaIndex Document objects.
        :param vector_store: A ChromaVectorStore instance.
        :returns: A VectorStoreIndex instance.
        """
        storage_context = StorageContext.from_defaults(vector_store=vector_store)
        return VectorStoreIndex.from_documents(documents, storage_context=storage_context)
    
    def build(self):
        """
        Execute the full indexing pipeline:
        - Load ignore patterns
        - Collect valid files
        - Load documents
        - Set up embedding model
        - Set up vector store
        - Build and return the index

        :returns: A VectorStoreIndex instance.
        """
        spec = self.load_ignore_spec()
        files = self.get_valid_files(spec)
        documents = self.load_documents(files)
        self.setup_embeddings()
        vector_store = self.setup_vector_store()
        self.index = self.build_index(documents, vector_store)
        vector_store.persist(str(self.chroma_dir))
        print("✅ Index built successfully.")
        return self.index
    
    def interact(self):
        """
        Interactively interact with the index:
        """

        # Set embedding model to local HuggingFace model
        Settings.embed_model = HuggingFaceEmbedding(model_name=self.model_name)

        # Reconnect to persisted Chroma collection
        client = chromadb.PersistentClient(path=str(self.chroma_dir))
        collection = client.get_or_create_collection(self.collection_name)
        vector_store = ChromaVectorStore(chroma_collection=collection)

        # Load index from storage context
        storage_context = StorageContext.from_defaults(vector_store=vector_store)
        index = VectorStoreIndex.from_vector_store(vector_store, storage_context=storage_context)

        # Start query engine
        print("\n💬 Ready for questions. Type 'exit' to quit.")
        llm = Ollama(model=OLLAMA_MODEL, request_timeout=60)
        retriever = VectorIndexRetriever(index=index, similarity_top_k=5)
        query_engine = RetrieverQueryEngine.from_args(retriever=retriever, llm=llm)

        while True:
            query = input("\n🧠 Ask a question: ")
            if query.strip().lower() in {"exit", "quit"}:
                break
            response = query_engine.query(query)
            print("\n📝 Answer:\n", response)
    

if __name__ == "__main__":
    builder = IndexBuilder(
        project_dir="/home/brian/repos/streamlit-stock-gui",
        chroma_dir="/home/brian/chroma_storage",
        collection_name="my_codebase",
        model_name="all-MiniLM-L6-v2",
        ignore_file="./vector-db/.llamaignore",
    )
    builder.build()

