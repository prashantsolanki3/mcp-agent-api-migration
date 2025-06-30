
# Modular vector store manager import
from agents.components.vectorstore_manager import VectorStoreManager

def ingest_files_to_vectorstore(root_dir: str, persist_directory: str = "./vectorstore", cache_file: str = "./vectorstore/.ingest_cache.json"):
    """
    Ingest files from the given root_dir into the vector store using the modular VectorStoreManager.
    """
    vsm = VectorStoreManager(persist_directory=persist_directory, cache_file=cache_file)
    return vsm.ingest_files(root_dir)
