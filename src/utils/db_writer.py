import sqlite3
import threading
import queue
import time
import os
from datetime import datetime

class DBWriter:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, db_path=None):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(DBWriter, cls).__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self, db_path=None):
        if self._initialized:
            return
            
        self.db_path = db_path or os.path.join("data", "leads.db")
        self.write_queue = queue.Queue()
        self.running = True
        self.thread = threading.Thread(target=self._process_queue, daemon=True, name="DBWriterThread")
        self.thread.start()
        self._initialized = True
        print(f"[DBWriter] Started background writer for {self.db_path}")

    def _get_connection(self):
        conn = sqlite3.connect(self.db_path, timeout=60, check_same_thread=False)
        # try:
        #     conn.execute("PRAGMA journal_mode=WAL;")
        #     conn.execute("PRAGMA synchronous=NORMAL;")
        # except Exception as e:
        #     print(f"[DBWriter] Warning: Failed to set WAL mode: {e}")
        return conn

    def _process_queue(self):
        """
        Consumer loop that processes write requests sequentially.
        Opens/Closes connection per task to avoid holding locks (Docker/WAL safety).
        """
        while self.running:
            try:
                # Block for up to 1s waiting for a task
                task = self.write_queue.get(timeout=1.0)
            except queue.Empty:
                continue

            query, params, future = task
            conn = None
            
            try:
                conn = self._get_connection()
                cursor = conn.cursor()
                
                # Distinguish between single execute and executemany
                is_batch = False
                if isinstance(params, list) and len(params) > 0 and isinstance(params[0], (list, tuple)):
                    is_batch = True
                
                if is_batch:
                    cursor.executemany(query, params)
                else:
                    cursor.execute(query, params)
                    
                conn.commit()
                
                if future:
                    if not is_batch and query.strip().upper().startswith("INSERT"):
                        future.set_result(cursor.lastrowid)
                    else:
                        future.set_result(True)
                        
            except Exception as e:
                print(f"❌ [DBWriter] Error executing query: {query[:50]}... -> {e}")
                if future:
                    future.set_exception(e)
            finally:
                if conn:
                    try:
                        conn.close()
                    except: pass
                self.write_queue.task_done()
        
        print("[DBWriter] Stopped.")

    def execute_write(self, query, params=(), wait=True):
        """
        Submits a write query to the queue.
        If wait=True, blocks until completion and returns result (e.g. lastrowid).
        If wait=False, fires and forgets (returns None).
        """
        if not self.running:
            raise RuntimeError("DBWriter is stopped.")

        future = Future() if wait else None
        self.write_queue.put((query, params, future))
        
        if wait:
            return future.result()
        return None

    def execute_many_write(self, query, params_list, wait=True):
        """
        Submits a batch write (executemany) to the queue.
        params_list: A list of tuples/lists.
        """
        if not self.running:
            raise RuntimeError("DBWriter is stopped.")

        future = Future() if wait else None
        self.write_queue.put((query, params_list, future))
        
        if wait:
            return future.result()
        return None

    def stop(self):
        self.running = False
        if self.thread.is_alive():
            self.thread.join(timeout=2)

class Future:
    """Simple Future implementation for strict synchronous waiting."""
    def __init__(self):
        self._result = None
        self._exception = None
        self._event = threading.Event()

    def set_result(self, result):
        self._result = result
        self._event.set()

    def set_exception(self, exception):
        self._exception = exception
        self._event.set()

    def result(self, timeout=None):
        self._event.wait(timeout)
        if self._exception:
            raise self._exception
        return self._result

# Global accessor
_db_writer = None

def get_db_writer():
    global _db_writer
    if _db_writer is None:
        _db_writer = DBWriter()
    return _db_writer
