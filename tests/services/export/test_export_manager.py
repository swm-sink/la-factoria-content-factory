"""
Tests for export manager service.
"""

import os
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.models.export import ExportFormat, ExportJob, ExportStatus
from app.models.pydantic.content import ContentOutline, ContentResponse, GeneratedContent, OutlineSection
from app.services.export_manager import ExportManager


@pytest.fixture
def export_manager():
    """Create an export manager instance."""
    return ExportManager()


@pytest.fixture
def sample_content_response():
    """Create a sample content response."""
    return ContentResponse(
        job_id="test-job-123",
        content=GeneratedContent(
            content_outline=ContentOutline(
                title="Test Content",
                overview="Test overview",
                learning_objectives=["Objective 1", "Objective 2", "Objective 3"],
                sections=[
                    OutlineSection(
                        section_number=1,
                        title="Section 1",
                        description="Description 1",
                        key_points=["Point 1", "Point 2"],
                    )
                ],
            )
        ),
        metadata={"source_syllabus_length": 100, "generation_timestamp": datetime.utcnow()},
        status="completed",
        created_at=datetime.utcnow(),
    )


class TestExportManager:
    """Test export manager functionality."""

    @pytest.mark.asyncio
    async def test_process_export_job_success(self, export_manager, sample_content_response):
        """Test successful export job processing."""
        job_id = "export-123"
        user_id = "user-123"
        content_ids = ["content-1"]

        # Mock dependencies
        with patch("app.services.export_manager.batch_get_documents") as mock_batch_get:
            with patch("app.services.export_manager.create_or_update_job_in_firestore") as mock_update:
                # Set up mock return values
                mock_batch_get.return_value = {
                    "content-1": {"user_id": user_id, **sample_content_response.model_dump()}
                }

                # Process export job
                await export_manager.process_export_job(
                    job_id=job_id, user_id=user_id, content_ids=content_ids, format=ExportFormat.JSON, options={}
                )

                # Verify status updates were called
                assert mock_update.called

                # Check final status update
                final_call = mock_update.call_args_list[-1]
                assert final_call[0][0] == "export_jobs"
                assert final_call[0][1] == job_id
                assert final_call[0][2]["status"] == ExportStatus.COMPLETED.value
                assert final_call[0][2]["progress"] == 100.0
                assert "file_size" in final_call[0][2]
                assert "download_url" in final_call[0][2]

    @pytest.mark.asyncio
    async def test_process_export_job_no_content(self, export_manager):
        """Test export job with no content found."""
        job_id = "export-123"
        user_id = "user-123"
        content_ids = ["content-1"]

        # Mock dependencies
        with patch("app.services.export_manager.batch_get_documents") as mock_batch_get:
            with patch("app.services.export_manager.create_or_update_job_in_firestore") as mock_update:
                # Return empty content
                mock_batch_get.return_value = {"content-1": None}

                # Process export job
                await export_manager.process_export_job(
                    job_id=job_id, user_id=user_id, content_ids=content_ids, format=ExportFormat.JSON, options={}
                )

                # Verify failed status update
                final_call = mock_update.call_args_list[-1]
                assert final_call[0][2]["status"] == ExportStatus.FAILED.value
                assert "error_message" in final_call[0][2]

    @pytest.mark.asyncio
    async def test_process_export_job_wrong_user(self, export_manager, sample_content_response):
        """Test export job with content belonging to wrong user."""
        job_id = "export-123"
        user_id = "user-123"
        content_ids = ["content-1"]

        # Mock dependencies
        with patch("app.services.export_manager.batch_get_documents") as mock_batch_get:
            with patch("app.services.export_manager.create_or_update_job_in_firestore") as mock_update:
                # Return content for different user
                mock_batch_get.return_value = {
                    "content-1": {"user_id": "different-user", **sample_content_response.model_dump()}
                }

                # Process export job
                await export_manager.process_export_job(
                    job_id=job_id, user_id=user_id, content_ids=content_ids, format=ExportFormat.JSON, options={}
                )

                # Verify failed status update
                final_call = mock_update.call_args_list[-1]
                assert final_call[0][2]["status"] == ExportStatus.FAILED.value

    @pytest.mark.asyncio
    async def test_get_export_file_success(self, export_manager):
        """Test successful export file retrieval."""
        job_id = "export-123"
        user_id = "user-123"

        # Create test file
        os.makedirs(os.path.join(export_manager.temp_storage_path, user_id), exist_ok=True)
        test_file_path = os.path.join(export_manager.temp_storage_path, user_id, f"export_{job_id}.json")
        with open(test_file_path, "wb") as f:
            f.write(b'{"test": "data"}')

        # Mock get_job_from_firestore
        with patch("app.services.export_manager.get_job_from_firestore") as mock_get_job:
            mock_get_job.return_value = {"id": job_id, "format": "json", "status": "completed"}

            # Get export file
            content, content_type, filename = await export_manager.get_export_file(job_id=job_id, user_id=user_id)

            # Verify results
            assert content.read() == b'{"test": "data"}'
            assert content_type == "application/json"
            assert filename == f"export_{job_id}.json"

        # Clean up
        os.remove(test_file_path)

    @pytest.mark.asyncio
    async def test_get_export_file_not_found(self, export_manager):
        """Test export file not found."""
        job_id = "export-123"
        user_id = "user-123"

        # Mock get_job_from_firestore
        with patch("app.services.export_manager.get_job_from_firestore") as mock_get_job:
            mock_get_job.return_value = None

            # Should raise FileNotFoundError
            with pytest.raises(FileNotFoundError):
                await export_manager.get_export_file(job_id=job_id, user_id=user_id)

    @pytest.mark.asyncio
    async def test_query_content_ids(self, export_manager):
        """Test querying content IDs with filters."""
        user_id = "user-123"
        filters = {"date_from": "2024-01-01", "date_to": "2024-12-31", "content_types": ["study_guide", "flashcards"]}

        # Mock query_documents
        with patch("app.services.export_manager.query_documents") as mock_query:
            mock_query.return_value = [{"id": "content-1"}, {"id": "content-2"}, {"id": "content-3"}]

            # Query content IDs
            content_ids = await export_manager.query_content_ids(user_id=user_id, filters=filters, max_items=10)

            # Verify results
            assert content_ids == ["content-1", "content-2", "content-3"]

            # Verify query was called with correct filters
            mock_query.assert_called_once()
            call_args = mock_query.call_args[1]
            assert call_args["filters"]["user_id"] == user_id
            assert "created_at__gte" in call_args["filters"]
            assert "created_at__lte" in call_args["filters"]
            assert "content_type__in" in call_args["filters"]

    @pytest.mark.asyncio
    async def test_cancel_export_job(self, export_manager):
        """Test cancelling an export job."""
        job_id = "export-123"
        user_id = "user-123"

        # Create test file to clean up
        os.makedirs(os.path.join(export_manager.temp_storage_path, user_id), exist_ok=True)
        test_file_path = os.path.join(export_manager.temp_storage_path, user_id, f"export_{job_id}.json")
        with open(test_file_path, "wb") as f:
            f.write(b"test")

        # Mock update function
        with patch("app.services.export_manager.create_or_update_job_in_firestore") as mock_update:
            # Cancel job
            await export_manager.cancel_export_job(job_id=job_id, user_id=user_id)

            # Verify status update
            mock_update.assert_called_once()
            assert mock_update.call_args[0][2]["status"] == ExportStatus.FAILED.value
            assert "cancelled" in mock_update.call_args[0][2]["error_message"]

            # Verify file was cleaned up
            assert not os.path.exists(test_file_path)

    @pytest.mark.asyncio
    async def test_cleanup_expired_exports(self, export_manager):
        """Test cleanup of expired export files."""
        user_id = "user-123"

        # Create test files
        os.makedirs(os.path.join(export_manager.temp_storage_path, user_id), exist_ok=True)

        # Create old file (should be deleted)
        old_file = os.path.join(export_manager.temp_storage_path, user_id, "export_old.json")
        with open(old_file, "wb") as f:
            f.write(b"old")
        # Set modification time to 10 days ago
        old_time = (datetime.utcnow() - timedelta(days=10)).timestamp()
        os.utime(old_file, (old_time, old_time))

        # Create recent file (should be kept)
        recent_file = os.path.join(export_manager.temp_storage_path, user_id, "export_recent.json")
        with open(recent_file, "wb") as f:
            f.write(b"recent")

        # Run cleanup
        await export_manager.cleanup_expired_exports(days_to_keep=7)

        # Verify old file was deleted and recent file kept
        assert not os.path.exists(old_file)
        assert os.path.exists(recent_file)

        # Clean up
        os.remove(recent_file)

    def test_ensure_temp_storage(self, export_manager):
        """Test temporary storage directory creation."""
        # Directory should exist after initialization
        assert os.path.exists(export_manager.temp_storage_path)

    @pytest.mark.asyncio
    async def test_update_job_status(self, export_manager):
        """Test job status update functionality."""
        job_id = "export-123"

        with patch("app.services.export_manager.create_or_update_job_in_firestore") as mock_update:
            # Update with all parameters
            await export_manager._update_job_status(
                job_id=job_id,
                status=ExportStatus.COMPLETED,
                progress=100.0,
                file_size=1024,
                download_url="/download/123",
                expires_at=datetime.utcnow() + timedelta(hours=24),
                error_message=None,
                completed_at=datetime.utcnow(),
            )

            # Verify update was called
            mock_update.assert_called_once()
            call_args = mock_update.call_args[0]
            update_data = call_args[2]

            assert call_args[0] == "export_jobs"
            assert call_args[1] == job_id
            assert update_data["status"] == ExportStatus.COMPLETED.value
            assert update_data["progress"] == 100.0
            assert update_data["file_size"] == 1024
            assert update_data["download_url"] == "/download/123"
            assert "expires_at" in update_data
            assert "completed_at" in update_data
