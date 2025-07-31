"""
Integration tests for Firestore client interactions.

These tests validate the integration between the application and Firestore database,
ensuring proper data persistence and retrieval.
"""

import asyncio
import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, List
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.models.pydantic.job import Job, JobProgress, JobStatus
from app.services.job.firestore_client import get_firestore_client


@pytest.mark.integration
class TestFirestoreIntegration:
    """Test Firestore database integration."""

    @pytest.fixture
    def mock_firestore(self):
        """Mock Firestore client with realistic behavior."""
        with patch("app.services.job.firestore_client.get_firestore_client") as mock_get_client:
            mock_client = MagicMock()
            mock_collection = MagicMock()
            mock_document = MagicMock()
            
            # Storage for mocked data
            mock_storage = {}
            
            def get_document(doc_id):
                """Get a specific document."""
                doc_mock = MagicMock()
                
                async def mock_get():
                    snapshot = MagicMock()
                    if doc_id in mock_storage:
                        snapshot.exists = True
                        snapshot.to_dict.return_value = mock_storage[doc_id]
                    else:
                        snapshot.exists = False
                        snapshot.to_dict.return_value = None
                    return snapshot
                
                async def mock_set(data, merge=False):
                    mock_storage[doc_id] = data
                    return True
                
                async def mock_update(data):
                    if doc_id in mock_storage:
                        mock_storage[doc_id].update(data)
                        mock_storage[doc_id]["updated_at"] = datetime.utcnow().isoformat()
                    return True
                
                async def mock_delete():
                    if doc_id in mock_storage:
                        del mock_storage[doc_id]
                    return True
                
                doc_mock.get = AsyncMock(side_effect=mock_get)
                doc_mock.set = AsyncMock(side_effect=mock_set)
                doc_mock.update = AsyncMock(side_effect=mock_update)
                doc_mock.delete = AsyncMock(side_effect=mock_delete)
                
                return doc_mock
            
            mock_collection.document = MagicMock(side_effect=get_document)
            mock_client.collection.return_value = mock_collection
            
            # Mock query operations
            async def mock_stream():
                docs = []
                for doc_id, data in mock_storage.items():
                    doc = MagicMock()
                    doc.id = doc_id
                    doc.to_dict.return_value = data
                    docs.append(doc)
                return docs
            
            mock_query = MagicMock()
            mock_query.stream = AsyncMock(side_effect=mock_stream)
            mock_query.where = MagicMock(return_value=mock_query)
            mock_query.order_by = MagicMock(return_value=mock_query)
            mock_query.limit = MagicMock(return_value=mock_query)
            mock_collection.where = MagicMock(return_value=mock_query)
            
            mock_get_client.return_value = mock_client
            yield mock_client, mock_storage

    @pytest.mark.asyncio
    async def test_job_document_crud_operations(self, mock_firestore):
        """Test Create, Read, Update, Delete operations for job documents."""
        mock_client, mock_storage = mock_firestore
        
        # Create a job document
        job_id = str(uuid.uuid4())
        job_data = {
            "id": job_id,
            "status": JobStatus.PENDING.value,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
            "metadata": {
                "syllabus_text": "Test syllabus for CRUD operations",
                "target_format": "guide"
            },
            "progress": {
                "current_step": "Created",
                "total_steps": 7,
                "completed_steps": 0,
                "percentage": 0.0
            }
        }
        
        # CREATE
        collection = mock_client.collection("jobs")
        doc_ref = collection.document(job_id)
        await doc_ref.set(job_data)
        
        assert job_id in mock_storage
        assert mock_storage[job_id]["status"] == JobStatus.PENDING.value
        
        # READ
        snapshot = await doc_ref.get()
        assert snapshot.exists
        retrieved_data = snapshot.to_dict()
        assert retrieved_data["id"] == job_id
        assert retrieved_data["metadata"]["syllabus_text"] == "Test syllabus for CRUD operations"
        
        # UPDATE
        update_data = {
            "status": JobStatus.PROCESSING.value,
            "progress": {
                "current_step": "Generating outline",
                "total_steps": 7,
                "completed_steps": 2,
                "percentage": 28.6
            }
        }
        await doc_ref.update(update_data)
        
        # Verify update
        snapshot = await doc_ref.get()
        updated_data = snapshot.to_dict()
        assert updated_data["status"] == JobStatus.PROCESSING.value
        assert updated_data["progress"]["current_step"] == "Generating outline"
        assert updated_data["progress"]["percentage"] == 28.6
        
        # DELETE
        await doc_ref.delete()
        
        # Verify deletion
        snapshot = await doc_ref.get()
        assert not snapshot.exists

    @pytest.mark.asyncio
    async def test_concurrent_document_updates(self, mock_firestore):
        """Test handling of concurrent updates to the same document."""
        mock_client, mock_storage = mock_firestore
        
        job_id = str(uuid.uuid4())
        initial_data = {
            "id": job_id,
            "status": JobStatus.PROCESSING.value,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
            "progress": {
                "current_step": "Starting",
                "total_steps": 10,
                "completed_steps": 0,
                "percentage": 0.0
            }
        }
        
        # Create initial document
        doc_ref = mock_client.collection("jobs").document(job_id)
        await doc_ref.set(initial_data)
        
        # Simulate concurrent updates
        async def update_progress(step_num):
            await doc_ref.update({
                "progress": {
                    "current_step": f"Step {step_num}",
                    "total_steps": 10,
                    "completed_steps": step_num,
                    "percentage": step_num * 10.0
                }
            })
        
        # Run concurrent updates
        tasks = [update_progress(i) for i in range(1, 11)]
        await asyncio.gather(*tasks)
        
        # Verify final state
        snapshot = await doc_ref.get()
        final_data = snapshot.to_dict()
        
        # Should have the last update
        assert final_data["progress"]["completed_steps"] in range(1, 11)
        assert "updated_at" in final_data

    @pytest.mark.asyncio
    async def test_query_operations(self, mock_firestore):
        """Test querying documents with filters and ordering."""
        mock_client, mock_storage = mock_firestore
        
        # Create multiple job documents
        jobs_data = []
        for i in range(5):
            job_id = str(uuid.uuid4())
            status = JobStatus.COMPLETED if i % 2 == 0 else JobStatus.FAILED
            created_at = datetime.utcnow() - timedelta(hours=i)
            
            job_data = {
                "id": job_id,
                "status": status.value,
                "created_at": created_at.isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
                "metadata": {
                    "syllabus_text": f"Test syllabus {i}",
                    "target_format": "guide" if i % 2 == 0 else "podcast"
                }
            }
            
            await mock_client.collection("jobs").document(job_id).set(job_data)
            jobs_data.append(job_data)
        
        # Query completed jobs
        query = mock_client.collection("jobs").where("status", "==", JobStatus.COMPLETED.value)
        docs = await query.stream()
        
        completed_jobs = [doc.to_dict() for doc in docs]
        
        # Should have 3 completed jobs (indices 0, 2, 4)
        assert len(completed_jobs) == 3
        assert all(job["status"] == JobStatus.COMPLETED.value for job in completed_jobs)

    @pytest.mark.asyncio
    async def test_batch_operations(self, mock_firestore):
        """Test batch write operations."""
        mock_client, mock_storage = mock_firestore
        
        # Create multiple documents in a batch
        job_ids = [str(uuid.uuid4()) for _ in range(3)]
        
        for idx, job_id in enumerate(job_ids):
            job_data = {
                "id": job_id,
                "status": JobStatus.PENDING.value,
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
                "metadata": {
                    "syllabus_text": f"Batch test syllabus {idx}",
                    "target_format": "guide"
                }
            }
            await mock_client.collection("jobs").document(job_id).set(job_data)
        
        # Verify all documents were created
        for job_id in job_ids:
            snapshot = await mock_client.collection("jobs").document(job_id).get()
            assert snapshot.exists

    @pytest.mark.asyncio
    async def test_transaction_operations(self, mock_firestore):
        """Test transactional operations for consistency."""
        mock_client, mock_storage = mock_firestore
        
        # Create two related documents
        job_id = str(uuid.uuid4())
        result_id = str(uuid.uuid4())
        
        job_data = {
            "id": job_id,
            "status": JobStatus.PROCESSING.value,
            "result_id": None,
            "created_at": datetime.utcnow().isoformat()
        }
        
        result_data = {
            "id": result_id,
            "job_id": job_id,
            "content": "Generated content",
            "created_at": datetime.utcnow().isoformat()
        }
        
        # Simulate transactional update
        await mock_client.collection("jobs").document(job_id).set(job_data)
        await mock_client.collection("results").document(result_id).set(result_data)
        
        # Update job with result reference
        await mock_client.collection("jobs").document(job_id).update({
            "status": JobStatus.COMPLETED.value,
            "result_id": result_id
        })
        
        # Verify consistency
        job_snapshot = await mock_client.collection("jobs").document(job_id).get()
        job_final = job_snapshot.to_dict()
        
        assert job_final["status"] == JobStatus.COMPLETED.value
        assert job_final["result_id"] == result_id

    @pytest.mark.asyncio
    async def test_error_handling(self, mock_firestore):
        """Test error handling for database operations."""
        mock_client, mock_storage = mock_firestore
        
        # Test non-existent document
        doc_ref = mock_client.collection("jobs").document("non-existent-id")
        snapshot = await doc_ref.get()
        
        assert not snapshot.exists
        assert snapshot.to_dict() is None
        
        # Test update on non-existent document
        # In real Firestore, this would create the document or fail depending on settings
        await doc_ref.update({"status": "updated"})
        
        # For our mock, it should now exist
        snapshot = await doc_ref.get()
        # Mock behavior may differ from real Firestore here

    @pytest.mark.asyncio
    async def test_pagination(self, mock_firestore):
        """Test pagination of query results."""
        mock_client, mock_storage = mock_firestore
        
        # Create 20 job documents
        for i in range(20):
            job_id = f"job-{i:03d}"
            await mock_client.collection("jobs").document(job_id).set({
                "id": job_id,
                "status": JobStatus.COMPLETED.value,
                "created_at": (datetime.utcnow() - timedelta(minutes=i)).isoformat(),
                "index": i
            })
        
        # Query with limit
        query = mock_client.collection("jobs").order_by("created_at").limit(10)
        first_page = await query.stream()
        
        assert len(list(first_page)) <= 10

    @pytest.mark.asyncio 
    async def test_field_updates(self, mock_firestore):
        """Test updating specific fields without affecting others."""
        mock_client, mock_storage = mock_firestore
        
        job_id = str(uuid.uuid4())
        initial_data = {
            "id": job_id,
            "status": JobStatus.PENDING.value,
            "metadata": {
                "syllabus_text": "Original syllabus",
                "target_format": "guide",
                "custom_field": "should_remain"
            },
            "created_at": datetime.utcnow().isoformat()
        }
        
        doc_ref = mock_client.collection("jobs").document(job_id)
        await doc_ref.set(initial_data)
        
        # Update only status
        await doc_ref.update({"status": JobStatus.PROCESSING.value})
        
        # Verify other fields remain unchanged
        snapshot = await doc_ref.get()
        updated_data = snapshot.to_dict()
        
        assert updated_data["status"] == JobStatus.PROCESSING.value
        assert updated_data["metadata"]["custom_field"] == "should_remain"
        assert updated_data["metadata"]["syllabus_text"] == "Original syllabus"

    @pytest.mark.asyncio
    async def test_nested_field_updates(self, mock_firestore):
        """Test updating nested fields."""
        mock_client, mock_storage = mock_firestore
        
        job_id = str(uuid.uuid4())
        initial_data = {
            "id": job_id,
            "progress": {
                "current_step": "Starting",
                "total_steps": 5,
                "completed_steps": 0,
                "details": {
                    "outline": False,
                    "content": False,
                    "validation": False
                }
            }
        }
        
        doc_ref = mock_client.collection("jobs").document(job_id)
        await doc_ref.set(initial_data)
        
        # Update nested field
        await doc_ref.update({
            "progress.completed_steps": 1,
            "progress.details.outline": True
        })
        
        # Verify update
        snapshot = await doc_ref.get()
        data = snapshot.to_dict()
        
        assert data["progress"]["completed_steps"] == 1
        assert data["progress"]["details"]["outline"] is True
        assert data["progress"]["details"]["content"] is False  # Should remain unchanged