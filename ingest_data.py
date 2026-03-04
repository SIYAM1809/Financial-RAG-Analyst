import os
from dotenv import load_dotenv
from llama_parse import LlamaParse
from llama_index.core import VectorStoreIndex, StorageContext, Settings
from llama_index.core.node_parser import MarkdownNodeParser
from llama_index.vector_stores.qdrant import QdrantVectorStore
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
import qdrant_client

# Load environment variables for local script execution
load_dotenv()

def ingest_documents():
    print("🚀 Starting Data Ingestion Pipeline...")

    # 1. Initialize LlamaParse (The "Table-Aware" Engine)
    # This is what proves your resume claim! It converts PDF tables to clean Markdown.
    llama_parse_api_key = os.getenv("LLAMA_CLOUD_API_KEY")
    if not llama_parse_api_key:
        print("🚨 Error: Missing LLAMA_CLOUD_API_KEY")
        return

    parser = LlamaParse(
        api_key=llama_parse_api_key,
        result_type="markdown",  # Crucial: Forces table extraction
        verbose=True
    )

    # 2. Parse the PDF
    # (Assuming you have a folder named 'sec-edgar-filings' with a PDF inside)
    file_path = "sec-edgar-filings/sample_10k.pdf" 
    print(f"📄 Parsing document: {file_path}...")
    documents = parser.load_data(file_path)

    # 3. Use Markdown Chunking
    # This keeps table headers and rows together instead of slicing them randomly.
    node_parser = MarkdownNodeParser()
    nodes = node_parser.get_nodes_from_documents(documents)
    print(f"✂️ Split document into {len(nodes)} structural chunks.")

    # 4. Setup Embedding Model
    Settings.embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")

    # 5. Connect to Qdrant Vector DB
    client = qdrant_client.QdrantClient(
        url=os.getenv("QDRANT_URL"),
        api_key=os.getenv("QDRANT_API_KEY")
    )
    
    vector_store = QdrantVectorStore(client=client, collection_name="financial_filings")
    storage_context = StorageContext.from_defaults(vector_store=vector_store)

    # 6. Index and Upload
    print("☁️ Uploading vectors to Qdrant Cloud...")
    VectorStoreIndex(
        nodes, 
        storage_context=storage_context,
        show_progress=True
    )
    print("✅ Ingestion Complete!")

if __name__ == "__main__":
    ingest_documents()