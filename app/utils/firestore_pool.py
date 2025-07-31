"""
Firestore connection pooling implementation.

Provides a managed connection pool for Firestore with health monitoring
and automatic recovery.
"""

import asyncio
import logging
import os
from typing import Any, Dict, List, Optional

from google.cloud.firestore import AsyncClient
from google.cloud.exceptions import GoogleCloudError

from app.core.config.connection_config import get_pool_config
from app.core.config.settings import get_settings
from app.core.connection_pool import ConnectionPoolBase, PooledConnectionContext


class FirestorePool(ConnectionPoolBase):
    """Firestore-specific connection pool implementation."""
    
    def __init__(self, **kwargs):
        """Initialize Firestore pool with settings."""
        settings = get_settings()
        config = get_pool_config("firestore")
        
        # Override with any provided kwargs
        pool_config = {
            "name": kwargs.get("name", "firestore_pool"),
            "min_size": kwargs.get("min_size", config.min_size),
            "max_size": kwargs.get("max_size", config.max_size),
            "max_idle_time": kwargs.get("max_idle_time", config.max_idle_time),
            "health_check_interval": kwargs.get("health_check_interval", config.health_check_interval),
        }
        
        super().__init__(**pool_config)
        
        # Firestore-specific configuration
        self.project_id = settings.gcp_project_id
        self.emulator_host = os.getenv("FIRESTORE_EMULATOR_HOST")
        
        # Track collections for health checks
        self._test_collection = "__health_check__"
    
    async def _create_connection(self) -> AsyncClient:
        """Create a new Firestore connection."""
        try:
            # Create client
            client = AsyncClient(project=self.project_id if self.project_id else None)
            
            # Test connection with a simple operation
            # Note: Firestore doesn't have a direct "ping" equivalent
            # We'll use a lightweight collection existence check
            test_ref = client.collection(self._test_collection)
            await test_ref.limit(1).get()  # Minimal query
            
            self.logger.debug("Created new Firestore connection")
            return client
            
        except GoogleCloudError as e:
            self.logger.error(f"Failed to create Firestore connection: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error creating Firestore connection: {e}")
            raise
    
    async def _is_connection_healthy(self, connection: AsyncClient) -> bool:
        """Check if Firestore connection is healthy."""
        try:
            # Perform a minimal read operation
            test_ref = connection.collection(self._test_collection)
            await test_ref.limit(1).get()
            return True
        except GoogleCloudError:
            return False
        except Exception as e:
            self.logger.warning(f"Health check failed with unexpected error: {e}")
            return False
    
    async def _close_connection(self, connection: AsyncClient) -> None:
        """Close a Firestore connection."""
        try:
            # Firestore AsyncClient doesn't have an explicit close method
            # The underlying gRPC connections are managed automatically
            # We'll just delete the reference
            del connection
        except Exception as e:
            self.logger.error(f"Error closing Firestore connection: {e}")
    
    async def get_document(
        self, 
        collection: str, 
        document_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get a document from Firestore.
        
        Args:
            collection: Collection name
            document_id: Document ID
            
        Returns:
            Document data or None if not found
        """
        async with PooledConnectionContext(self) as client:
            doc_ref = client.collection(collection).document(document_id)
            doc = await doc_ref.get()
            return doc.to_dict() if doc.exists else None
    
    async def set_document(
        self, 
        collection: str, 
        document_id: str, 
        data: Dict[str, Any],
        merge: bool = True
    ) -> None:
        """
        Set a document in Firestore.
        
        Args:
            collection: Collection name
            document_id: Document ID
            data: Document data
            merge: Whether to merge with existing data
        """
        async with PooledConnectionContext(self) as client:
            doc_ref = client.collection(collection).document(document_id)
            await doc_ref.set(data, merge=merge)
    
    async def update_document(
        self, 
        collection: str, 
        document_id: str, 
        updates: Dict[str, Any]
    ) -> None:
        """
        Update specific fields in a document.
        
        Args:
            collection: Collection name
            document_id: Document ID
            updates: Fields to update
        """
        async with PooledConnectionContext(self) as client:
            doc_ref = client.collection(collection).document(document_id)
            await doc_ref.update(updates)
    
    async def delete_document(
        self, 
        collection: str, 
        document_id: str
    ) -> None:
        """
        Delete a document from Firestore.
        
        Args:
            collection: Collection name
            document_id: Document ID
        """
        async with PooledConnectionContext(self) as client:
            doc_ref = client.collection(collection).document(document_id)
            await doc_ref.delete()
    
    async def query_documents(
        self,
        collection: str,
        filters: Optional[List[tuple]] = None,
        order_by: Optional[str] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Query documents from Firestore.
        
        Args:
            collection: Collection name
            filters: List of (field, op, value) tuples
            order_by: Field to order by
            limit: Maximum documents to return
            offset: Number of documents to skip
            
        Returns:
            List of documents
        """
        async with PooledConnectionContext(self) as client:
            query = client.collection(collection)
            
            # Apply filters
            if filters:
                for field, op, value in filters:
                    query = query.where(field, op, value)
            
            # Apply ordering
            if order_by:
                query = query.order_by(order_by)
            
            # Apply pagination
            if offset:
                query = query.offset(offset)
            if limit:
                query = query.limit(limit)
            
            # Execute query
            docs = await query.get()
            
            results = []
            for doc in docs:
                data = doc.to_dict()
                data["id"] = doc.id
                results.append(data)
            
            return results
    
    async def batch_get_documents(
        self,
        collection: str,
        document_ids: List[str]
    ) -> Dict[str, Optional[Dict[str, Any]]]:
        """
        Batch get multiple documents.
        
        Args:
            collection: Collection name
            document_ids: List of document IDs
            
        Returns:
            Dictionary mapping document ID to data
        """
        async with PooledConnectionContext(self) as client:
            # Get all documents in parallel
            tasks = []
            for doc_id in document_ids:
                doc_ref = client.collection(collection).document(doc_id)
                tasks.append(doc_ref.get())
            
            docs = await asyncio.gather(*tasks, return_exceptions=True)
            
            results = {}
            for doc_id, doc in zip(document_ids, docs):
                if isinstance(doc, Exception):
                    self.logger.error(f"Failed to get document {doc_id}: {doc}")
                    results[doc_id] = None
                elif doc.exists:
                    results[doc_id] = doc.to_dict()
                else:
                    results[doc_id] = None
            
            return results
    
    async def batch_write(
        self,
        operations: List[Dict[str, Any]]
    ) -> None:
        """
        Perform batch write operations.
        
        Args:
            operations: List of operations, each containing:
                - type: "set", "update", or "delete"
                - collection: Collection name
                - document_id: Document ID
                - data: Data for set/update operations
                - merge: For set operations (optional)
        """
        async with PooledConnectionContext(self) as client:
            # Process in batches of 500 (Firestore limit)
            batch_size = 500
            
            for i in range(0, len(operations), batch_size):
                batch = client.batch()
                batch_ops = operations[i:i + batch_size]
                
                for op in batch_ops:
                    doc_ref = client.collection(op["collection"]).document(op["document_id"])
                    
                    if op["type"] == "set":
                        batch.set(doc_ref, op["data"], merge=op.get("merge", True))
                    elif op["type"] == "update":
                        batch.update(doc_ref, op["data"])
                    elif op["type"] == "delete":
                        batch.delete(doc_ref)
                
                # Commit the batch
                await batch.commit()


# Global pool instance
_firestore_pool: Optional[FirestorePool] = None


async def get_firestore_pool() -> FirestorePool:
    """
    Get or create the global Firestore pool.
    
    Returns:
        Firestore connection pool
    """
    global _firestore_pool
    
    if _firestore_pool is None:
        _firestore_pool = FirestorePool(name="global_firestore_pool")
        await _firestore_pool.initialize()
        logging.info("Global Firestore pool initialized")
    
    return _firestore_pool


async def close_firestore_pool() -> None:
    """Close the global Firestore pool."""
    global _firestore_pool
    
    if _firestore_pool:
        await _firestore_pool.close()
        _firestore_pool = None
        logging.info("Global Firestore pool closed")


# Convenience functions that maintain backward compatibility
async def get_document_from_firestore(
    document_id: str,
    collection_name: str = "jobs"
) -> Optional[Dict[str, Any]]:
    """Get a document from Firestore (backward compatible)."""
    pool = await get_firestore_pool()
    return await pool.get_document(collection_name, document_id)


async def create_or_update_document_in_firestore(
    document_id: str,
    data: Dict[str, Any],
    collection_name: str = "jobs"
) -> None:
    """Create or update a document in Firestore (backward compatible)."""
    pool = await get_firestore_pool()
    await pool.set_document(collection_name, document_id, data, merge=True)


async def update_document_field_in_firestore(
    document_id: str,
    field_path: str,
    value: Any,
    collection_name: str = "jobs"
) -> None:
    """Update a specific field in a document (backward compatible)."""
    pool = await get_firestore_pool()
    await pool.update_document(collection_name, document_id, {field_path: value})


# Health check function
async def check_firestore_health() -> dict:
    """
    Check Firestore pool health.
    
    Returns:
        Health status dictionary
    """
    try:
        pool = await get_firestore_pool()
        
        # Get pool stats
        stats = pool.get_stats()
        
        # Try a simple operation
        test_doc = await pool.get_document("__health_check__", "test")
        
        return {
            "status": "healthy",
            "pool_stats": stats,
            "test_successful": True,
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
        }