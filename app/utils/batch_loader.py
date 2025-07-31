"""
Batch loading utilities for efficient database operations.

This module provides utilities for batching database operations to avoid N+1 query problems.
"""

import asyncio
import logging
from typing import Any, Dict, List, Optional, Set, Tuple

logger = logging.getLogger(__name__)


class BatchLoader:
    """Batches multiple database operations for efficient execution."""

    def __init__(self, batch_size: int = 100, delay_ms: int = 10):
        """
        Initialize batch loader.
        
        Args:
            batch_size: Maximum number of operations to batch together
            delay_ms: Delay in milliseconds before executing batch
        """
        self.batch_size = batch_size
        self.delay_ms = delay_ms
        self._pending_loads: Dict[str, List[Tuple[str, asyncio.Future]]] = {}
        self._batch_task: Optional[asyncio.Task] = None

    async def load(self, collection: str, doc_id: str) -> Optional[Dict[str, Any]]:
        """
        Load a document, batching with other requests.
        
        Args:
            collection: Collection name
            doc_id: Document ID
            
        Returns:
            Document data if found
        """
        if collection not in self._pending_loads:
            self._pending_loads[collection] = []
            
        future = asyncio.Future()
        self._pending_loads[collection].append((doc_id, future))
        
        # Schedule batch execution
        if not self._batch_task or self._batch_task.done():
            self._batch_task = asyncio.create_task(self._execute_batch())
            
        return await future

    async def _execute_batch(self):
        """Execute pending batch operations."""
        # Small delay to allow more operations to batch
        await asyncio.sleep(self.delay_ms / 1000.0)
        
        # Import here to avoid circular imports
        from app.services.job.firestore_client import get_firestore_client
        
        client = get_firestore_client()
        
        for collection, loads in self._pending_loads.items():
            if not loads:
                continue
                
            # Extract unique document IDs
            doc_ids = list(set(doc_id for doc_id, _ in loads))
            
            # Batch fetch documents
            try:
                # Firestore supports batching up to 500 documents
                for i in range(0, len(doc_ids), 500):
                    batch_ids = doc_ids[i:i + 500]
                    docs = await self._batch_get_documents(client, collection, batch_ids)
                    
                    # Resolve futures
                    doc_map = {doc['id']: doc for doc in docs if doc}
                    for doc_id, future in loads:
                        if not future.done():
                            future.set_result(doc_map.get(doc_id))
                            
            except Exception as e:
                logger.error(f"Batch load failed for collection {collection}: {e}")
                # Reject all pending futures
                for _, future in loads:
                    if not future.done():
                        future.set_exception(e)
                        
        # Clear pending loads
        self._pending_loads.clear()

    async def _batch_get_documents(
        self, client: Any, collection: str, doc_ids: List[str]
    ) -> List[Dict[str, Any]]:
        """Batch get multiple documents from Firestore."""
        results = []
        
        # Use Firestore's batch get capability
        collection_ref = client.collection(collection)
        
        # Get all documents in parallel
        tasks = [collection_ref.document(doc_id).get() for doc_id in doc_ids]
        docs = await asyncio.gather(*tasks, return_exceptions=True)
        
        for doc_id, doc in zip(doc_ids, docs):
            if isinstance(doc, Exception):
                logger.error(f"Failed to get document {doc_id}: {doc}")
                results.append(None)
            elif doc.exists:
                data = doc.to_dict()
                data['id'] = doc_id
                results.append(data)
            else:
                results.append(None)
                
        return results


class BatchUpdater:
    """Batches multiple update operations for efficient execution."""
    
    def __init__(self, batch_size: int = 500):
        """
        Initialize batch updater.
        
        Args:
            batch_size: Maximum number of operations per batch
        """
        self.batch_size = batch_size
        self._updates: Dict[str, List[Tuple[str, Dict[str, Any]]]] = {}
        
    def add_update(self, collection: str, doc_id: str, updates: Dict[str, Any]):
        """
        Add an update operation to the batch.
        
        Args:
            collection: Collection name
            doc_id: Document ID
            updates: Fields to update
        """
        if collection not in self._updates:
            self._updates[collection] = []
            
        self._updates[collection].append((doc_id, updates))
        
    async def execute(self):
        """Execute all pending updates."""
        # Import here to avoid circular imports
        from app.services.job.firestore_client import get_firestore_client
        
        client = get_firestore_client()
        
        for collection, updates in self._updates.items():
            if not updates:
                continue
                
            # Process in batches (Firestore limit is 500 per batch)
            for i in range(0, len(updates), self.batch_size):
                batch = client.batch()
                batch_updates = updates[i:i + self.batch_size]
                
                for doc_id, update_data in batch_updates:
                    doc_ref = client.collection(collection).document(doc_id)
                    batch.update(doc_ref, update_data)
                    
                try:
                    await batch.commit()
                    logger.info(f"Batch updated {len(batch_updates)} documents in {collection}")
                except Exception as e:
                    logger.error(f"Batch update failed for {collection}: {e}")
                    raise
                    
        # Clear updates after execution
        self._updates.clear()


class BatchCreator:
    """Batches multiple create operations for efficient execution."""
    
    def __init__(self, batch_size: int = 500):
        """
        Initialize batch creator.
        
        Args:
            batch_size: Maximum number of operations per batch
        """
        self.batch_size = batch_size
        self._creates: Dict[str, List[Tuple[str, Dict[str, Any]]]] = {}
        
    def add_create(self, collection: str, doc_id: str, data: Dict[str, Any]):
        """
        Add a create operation to the batch.
        
        Args:
            collection: Collection name
            doc_id: Document ID (or None for auto-generated)
            data: Document data
        """
        if collection not in self._creates:
            self._creates[collection] = []
            
        self._creates[collection].append((doc_id, data))
        
    async def execute(self) -> Dict[str, List[str]]:
        """
        Execute all pending creates.
        
        Returns:
            Dictionary mapping collection to list of created document IDs
        """
        # Import here to avoid circular imports
        from app.services.job.firestore_client import get_firestore_client
        
        client = get_firestore_client()
        created_ids = {}
        
        for collection, creates in self._creates.items():
            if not creates:
                continue
                
            created_ids[collection] = []
            
            # Process in batches
            for i in range(0, len(creates), self.batch_size):
                batch = client.batch()
                batch_creates = creates[i:i + self.batch_size]
                
                for doc_id, data in batch_creates:
                    if doc_id:
                        doc_ref = client.collection(collection).document(doc_id)
                    else:
                        doc_ref = client.collection(collection).document()
                        doc_id = doc_ref.id
                        
                    batch.set(doc_ref, data)
                    created_ids[collection].append(doc_id)
                    
                try:
                    await batch.commit()
                    logger.info(f"Batch created {len(batch_creates)} documents in {collection}")
                except Exception as e:
                    logger.error(f"Batch create failed for {collection}: {e}")
                    raise
                    
        # Clear creates after execution
        self._creates.clear()
        return created_ids


# Global instances for reuse
_batch_loader: Optional[BatchLoader] = None
_batch_updater: Optional[BatchUpdater] = None
_batch_creator: Optional[BatchCreator] = None


def get_batch_loader() -> BatchLoader:
    """Get or create global batch loader instance."""
    global _batch_loader
    if _batch_loader is None:
        _batch_loader = BatchLoader()
    return _batch_loader


def get_batch_updater() -> BatchUpdater:
    """Get or create global batch updater instance."""
    global _batch_updater
    if _batch_updater is None:
        _batch_updater = BatchUpdater()
    return _batch_updater


def get_batch_creator() -> BatchCreator:
    """Get or create global batch creator instance."""
    global _batch_creator
    if _batch_creator is None:
        _batch_creator = BatchCreator()
    return _batch_creator