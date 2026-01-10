import os
from pathlib import Path
try:
    from safe_store import SafeStore, LogLevel
except ImportError:
    print("[RAGService] safe_store module missing. Using fallback stub.")
    from enum import Enum
    import logging
    
    # Configure logger (fallback)
    logger = logging.getLogger("SafeStoreFallback")

    class LogLevel(Enum):
        INFO = "INFO"
        DEBUG = "DEBUG"
        ERROR = "ERROR"
        WARNING = "WARNING"

    class SafeStore:
        def __init__(self, db_path=None, log_level=LogLevel.INFO):
            self.db_path = db_path
            self.log_level = log_level
            # logger.info(f"Initialized SafeStore (Fallback) at {db_path}")

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_val, exc_tb):
            pass

        def add_document(self, file_path, vectorizer_name="st:all-MiniLM-L6-v2", metadata=None):
            return True

        def query(self, query_text, vectorizer_name="st:all-MiniLM-L6-v2", top_k=5):
            return []

class RAGService:
    def __init__(self, db_path=None, log_level=LogLevel.INFO):
        self.db_path = db_path or os.path.join('data', 'rag_store.db')
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self.store = None
        self.log_level = log_level

    def _get_store(self):
        """Lazy loads the SafeStore to prevent import-time hangs."""
        if self.store is None:
            self.store = SafeStore(db_path=self.db_path, log_level=self.log_level)
        return self.store

    def add_document(self, file_path, metadata=None):
        """Adds a document to the RAG store."""
        try:
            store = self._get_store()
            with store:
                store.add_document(
                    file_path=file_path,
                    vectorizer_name="st:all-MiniLM-L6-v2",
                    metadata=metadata
                )
            return True
        except Exception as e:
            print(f"[RAGService] Error adding document: {e}")
            return False

    def query(self, query_text, top_k=5):
        """Queries the RAG store for relevant chunks."""
        try:
            store = self._get_store()
            with store:
                results = store.query(
                    query_text=query_text,
                    vectorizer_name="st:all-MiniLM-L6-v2",
                    top_k=top_k
                )
            return results
        except Exception as e:
            print(f"[RAGService] Error querying store: {e}")
            return []

    def get_context(self, query_text, top_k=3):
        """Returns a string context from the query results."""
        results = self.query(query_text, top_k=top_k)
        if not results:
            return ""
        
        context_parts = []
        for res in results:
            context_parts.append(f"Source: {res['file_path']}\nContent: {res['chunk_text']}")
        
        return "\n\n---\n\n".join(context_parts)

rag_service = RAGService()
