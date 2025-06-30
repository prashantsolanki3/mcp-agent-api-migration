import os
import json
import hashlib
from typing import List
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_community.document_loaders import TextLoader, PDFPlumberLoader, Docx2txtLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

SUPPORTED_EXTENSIONS = ['.py', '.md', '.txt', '.json', '.docx', '.pdf']

class VectorStoreManager:
    def __init__(self, persist_directory: str = "./vectorstore", cache_file: str = "./vectorstore/.ingest_cache.json"):
        self.persist_directory = persist_directory
        self.cache_file = cache_file

    def get_all_files_with_extensions(self, root_dir: str, extensions: List[str]) -> List[str]:
        matched_files = []
        for dirpath, _, filenames in os.walk(root_dir):
            for filename in filenames:
                if any(filename.endswith(ext) for ext in extensions):
                    matched_files.append(os.path.join(dirpath, filename))
        return matched_files

    def _get_file_hash(self, file_path):
        hasher = hashlib.sha256()
        with open(file_path, 'rb') as f:
            while True:
                chunk = f.read(8192)
                if not chunk:
                    break
                hasher.update(chunk)
        return hasher.hexdigest()

    def ingest_files(self, root_dir: str):
        files = self.get_all_files_with_extensions(root_dir, SUPPORTED_EXTENSIONS)
        # Load cache of file hashes
        if os.path.exists(self.cache_file):
            with open(self.cache_file, 'r') as f:
                file_cache = json.load(f)
        else:
            file_cache = {}

        changed_files = []
        new_cache = {}
        for file_path in files:
            try:
                file_hash = self._get_file_hash(file_path)
                new_cache[file_path] = file_hash
                if file_path not in file_cache or file_cache[file_path] != file_hash:
                    changed_files.append(file_path)
            except Exception as e:
                print(f"Failed to hash {file_path}: {e}")

        if not changed_files:
            print("No new or changed files to ingest.")
            return None

        documents = []
        for file_path in changed_files:
            try:
                ext = os.path.splitext(file_path)[1].lower()
                if ext in ['.py', '.md', '.txt', '.json']:
                    loader = TextLoader(file_path, encoding="utf-8")
                elif ext == '.pdf':
                    loader = PDFPlumberLoader(file_path)
                elif ext == '.docx':
                    loader = Docx2txtLoader(file_path)
                else:
                    print(f"Unsupported file type: {file_path}")
                    continue
                docs = loader.load()
                documents.extend(docs)
            except Exception as e:
                print(f"Failed to load {file_path}: {e}")
        if not documents:
            print("No documents loaded.")
            return None
        splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        docs = splitter.split_documents(documents)
        embeddings = OpenAIEmbeddings()
        vectordb = Chroma.from_documents(docs, embeddings, persist_directory=self.persist_directory)
        print(f"Ingested {len(docs)} chunks into vector store at {self.persist_directory}")
        # Save updated cache
        with open(self.cache_file, 'w') as f:
            json.dump(new_cache, f, indent=2)
        return vectordb

    def get_vectorstore(self):
        return Chroma(persist_directory=self.persist_directory, embedding_function=None)

    def get_relevant_docs(self, query: str, k: int = 5) -> str:
        try:
            vectordb = self.get_vectorstore()
            docs = vectordb.similarity_search(query, k=k)
            return '\n\n'.join([doc.page_content for doc in docs])
        except Exception as e:
            return f"[Vectorstore error: {e}]"