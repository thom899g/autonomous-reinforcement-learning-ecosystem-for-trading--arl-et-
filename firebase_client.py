"""
Firebase Client for ARL-ET
Centralized state management with automatic retry and error handling
"""
import firebase_admin
from firebase_admin import credentials, firestore
from google.cloud.firestore_v1 import Client as FirestoreClient
from google.cloud.firestore_v1.base_query import FieldFilter
import logging
from typing import Dict, Any, List, Optional, Union
import time
from datetime import datetime
import threading
from config import config

class FirebaseClient:
    """Firebase Firestore client with automatic reconnection"""
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        """Singleton pattern for Firebase client"""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialize()
        return cls._instance
    
    def _initialize(self) -> None:
        """Initialize Firebase connection"""
        try:
            if not firebase_admin._apps:
                cred = credentials.Certificate(config.firebase.credentials_path)
                firebase_admin.initialize_app(cred, {
                    'projectId': config.firebase.project_id
                })
            
            self.db: FirestoreClient = firestore.client()
            self.collection_prefix = config.firebase.collection_prefix
            logging.info(f"Firebase initialized for project: {config.firebase.project_id}")
            
        except Exception as e:
            logging.error(f"Failed to initialize Firebase: {e}")
            raise ConnectionError(f"Firebase initialization failed: {e}")
    
    def _get_collection(self, collection_name: str) -> str:
        """Get fully qualified collection name with prefix"""
        return f"{self.collection_prefix}{collection_name}"
    
    def write_state(self, 
                    collection: str, 
                    document_id: str, 
                    data: Dict[str, Any],
                    merge: bool = True) -> bool:
        """
        Write data to Firestore with retry logic
        Returns: Success status
        """
        max_retries = 3
        for attempt in range(max_retries):
            try:
                doc_ref = self.db.collection(
                    self._get_collection(collection)
                ).document(document_id)
                
                if merge:
                    doc_ref.set(data, merge=True)
                else:
                    doc_ref.set(data)
                
                logging.debug(f"Successfully wrote to {collection}/{document_id}")
                return True
                
            except Exception as e:
                logging.warning(f"Firestore write attempt {attempt + 1} failed: {e}")
                if attempt == max_retries - 1:
                    logging.error(f"Failed to write to Firestore after {max_retries} attempts")
                    return False
                time.sleep(2 ** attempt)  # Exponential backoff
    
    def read_state(self,