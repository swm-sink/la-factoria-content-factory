import uuid
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.core.config.settings import Settings
from app.models.pydantic.content import ContentRequest
from app.models.pydantic.job import (
    Job,
    JobError,
    JobErrorCode,
    JobProgress,
    JobStatus,
    JobUpdate,
)
from app.services.job_manager import JobManager, get_job_manager

# --- Fixtures ---


@pytest.fixture
def mock_job_settings():
    """Mock settings for job manager tests"""
    return Settings(
        gcp_project_id="test-project",
        gemini_model_name="models/gemini-2.5-flash-preview-05-20",
        api_key="test_key",
        elevenlabs_api_key="test_eleven_key",
        jwt_secret_key="test_jwt_secret_key_minimum_length_32",
        tasks_worker_service_url="https://test-worker.example.com",
        cors_origins=["http://localhost:3000"],
        gcp_location="us-central1",
    )


@pytest.fixture
def job_manager(mock_job_settings):
    with patch("app.services.job_manager.get_settings", return_value=mock_job_settings):
        # Mock the dependencies of JobManager: FirestoreClient and CloudTasksClient
        with patch(
            "app.services.job_manager.get_cloud_tasks_client"
        ) as mock_get_tasks_client:
            mock_tasks_client_instance = AsyncMock()
            mock_get_tasks_client.return_value = mock_tasks_client_instance

            # Firestore functions are imported directly, so they need to be patched directly
            # in the job_manager module's namespace.
            with patch(
                "app.services.job_manager.create_or_update_job_in_firestore",
                new_callable=AsyncMock,
            ) as mock_create_update_firestore, patch(
                "app.services.job_manager.get_job_from_firestore",
                new_callable=AsyncMock,
            ) as mock_get_firestore, patch(
                "app.services.job_manager.update_job_field_in_firestore",
                new_callable=AsyncMock,
            ) as mock_update_field_firestore, patch(
                "app.services.job_manager.query_jobs_by_status", new_callable=AsyncMock
            ) as mock_query_firestore, patch(
                "app.services.job_manager.count_jobs_by_status", new_callable=AsyncMock
            ) as mock_count_firestore, patch(
                "app.services.job_manager.get_all_job_statuses", new_callable=AsyncMock
            ) as mock_get_all_statuses_firestore:
                manager = JobManager()
                # Attach mocks for easy access in tests if needed, though direct patching is preferred
                manager._mock_create_update_firestore = mock_create_update_firestore
                manager._mock_get_firestore = mock_get_firestore
                manager._mock_update_field_firestore = mock_update_field_firestore
                manager._mock_query_firestore = mock_query_firestore
                manager._mock_count_firestore = mock_count_firestore
                manager._mock_get_all_statuses_firestore = (
                    mock_get_all_statuses_firestore
                )
                manager._mock_tasks_client = mock_tasks_client_instance
                yield manager


@pytest.fixture
def sample_content_request():
    return ContentRequest(
        syllabus_text="This is a test syllabus, long enough for validation."
    )


# --- Test Cases ---


@pytest.mark.asyncio
async def test_create_job_success(
    job_manager: JobManager, sample_content_request: ContentRequest
):
    job_manager._mock_tasks_client.enqueue_content_generation_job.return_value = True

    created_job = await job_manager.create_job(sample_content_request)

    assert isinstance(created_job, Job)
    assert (
        created_job.status == JobStatus.PENDING
    )  # Initial status before enqueue success update
    assert created_job.request_data == sample_content_request.model_dump()

    job_manager._mock_create_update_firestore.assert_called_once()
    job_manager._mock_tasks_client.enqueue_content_generation_job.assert_called_once_with(
        str(created_job.id)
    )
    # Check for status updates after enqueue
    assert (
        job_manager._mock_update_field_firestore.call_count >= 2
    )  # For progress.current_step and progress.percentage


@pytest.mark.asyncio
async def test_create_job_enqueue_failure(
    job_manager: JobManager, sample_content_request: ContentRequest
):
    job_manager._mock_tasks_client.enqueue_content_generation_job.return_value = (
        False  # Simulate enqueue failure
    )

    created_job = await job_manager.create_job(sample_content_request)

    assert created_job.status == JobStatus.FAILED
    assert created_job.error is not None
    assert created_job.error.message == "Failed to enqueue job for processing"

    job_manager._mock_create_update_firestore.assert_called_once()
    job_manager._mock_tasks_client.enqueue_content_generation_job.assert_called_once_with(
        str(created_job.id)
    )

    # Check that status was updated to FAILED in Firestore
    update_calls = job_manager._mock_update_field_firestore.call_args_list
    assert any(
        call_args[0][1] == "status" and call_args[0][2] == JobStatus.FAILED.value
        for call_args in update_calls
    )
    assert any(call_args[0][1] == "error" for call_args in update_calls)


@pytest.mark.asyncio
async def test_get_job_found(job_manager: JobManager):
    job_id = uuid.uuid4()
    mock_firestore_data = {
        "id": str(job_id),
        "status": "completed",
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat(),
        "request_data": {"syllabus_text": "test"},
    }
    job_manager._mock_get_firestore.return_value = mock_firestore_data

    job = await job_manager.get_job(job_id)

    assert job is not None
    assert job.id == job_id
    assert job.status == JobStatus.COMPLETED
    job_manager._mock_get_firestore.assert_called_once_with(
        str(job_id), job_manager._collection_name
    )


@pytest.mark.asyncio
async def test_get_job_not_found(job_manager: JobManager):
    job_id = uuid.uuid4()
    job_manager._mock_get_firestore.return_value = None

    job = await job_manager.get_job(job_id)

    assert job is None
    job_manager._mock_get_firestore.assert_called_once_with(
        str(job_id), job_manager._collection_name
    )


@pytest.mark.asyncio
async def test_list_jobs(job_manager: JobManager):
    mock_job_doc1 = {
        "id": str(uuid.uuid4()),
        "status": "pending",
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat(),
        "request_data": {},
    }
    mock_job_doc2 = {
        "id": str(uuid.uuid4()),
        "status": "completed",
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat(),
        "request_data": {},
    }
    job_manager._mock_query_firestore.return_value = [mock_job_doc1, mock_job_doc2]
    job_manager._mock_count_firestore.return_value = 2

    job_list = await job_manager.list_jobs(page=1, page_size=10)

    assert isinstance(job_list, JobList)
    assert len(job_list.jobs) == 2
    assert job_list.total == 2
    assert job_list.page == 1
    assert job_list.total_pages == 1
    job_manager._mock_query_firestore.assert_called_once_with(
        status=None, limit=10, offset=0, collection_name=job_manager._collection_name
    )
    job_manager._mock_count_firestore.assert_called_once_with(
        status=None, collection_name=job_manager._collection_name
    )


@pytest.mark.asyncio
async def test_update_job_success(job_manager: JobManager):
    job_id = uuid.uuid4()
    job_update_data = JobUpdate(
        status=JobStatus.PROCESSING,
        progress=JobProgress(
            current_step="Working", total_steps=3, completed_steps=1, percentage=33.3
        ),
    )

    # Simulate existing job and then the updated job data from Firestore
    mock_existing_job_data = {
        "id": str(job_id),
        "status": "pending",
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat(),
        "request_data": {},
    }
    mock_updated_job_data = {
        "id": str(job_id),
        "status": "processing",
        "created_at": mock_existing_job_data["created_at"],
        "updated_at": datetime.utcnow().isoformat(),  # Should be updated
        "progress": job_update_data.progress.model_dump(),
        "request_data": {},
    }
    job_manager._mock_get_firestore.side_effect = [
        mock_existing_job_data,
        mock_updated_job_data,
    ]

    updated_job = await job_manager.update_job(job_id, job_update_data)

    assert updated_job is not None
    assert updated_job.status == JobStatus.PROCESSING
    assert updated_job.progress.percentage == 33.3

    # Check that update_job_field_in_firestore was called for status, progress, and updated_at
    assert job_manager._mock_update_field_firestore.call_count >= 3
    # Example check for one of the calls
    job_manager._mock_update_field_firestore.assert_any_call(
        str(job_id), "status", "processing", job_manager._collection_name
    )


@pytest.mark.asyncio
async def test_delete_job_success(job_manager: JobManager):
    job_id = uuid.uuid4()
    mock_existing_job_data = {
        "id": str(job_id),
        "status": "completed",
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat(),
    }
    job_manager._mock_get_firestore.return_value = mock_existing_job_data

    result = await job_manager.delete_job(job_id)
    assert result is True

    # Check that status was updated to DELETED and deleted_at was set
    job_manager._mock_update_field_firestore.assert_any_call(
        str(job_id), "status", JobStatus.DELETED.value, job_manager._collection_name
    )
    job_manager._mock_update_field_firestore.assert_any_call(
        str(job_id),
        "deleted_at",
        pytest.approx(datetime.utcnow().isoformat(), abs=1),
        job_manager._collection_name,
    )


@pytest.mark.asyncio
async def test_get_job_statistics(job_manager: JobManager):
    mock_status_counts = {
        JobStatus.PENDING.value: 5,
        JobStatus.COMPLETED.value: 10,
        "other_custom_status": 1,  # Test handling of unexpected statuses
    }
    job_manager._mock_get_all_statuses_firestore.return_value = mock_status_counts

    stats = await job_manager.get_job_statistics()

    assert stats["total"] == 16
    assert stats["pending"] == 5
    assert stats["completed"] == 10
    assert stats["processing"] == 0  # Default if not in counts
    assert stats["other_other_custom_status"] == 1
    job_manager._mock_get_all_statuses_firestore.assert_called_once_with(
        job_manager._collection_name
    )


def test_firestore_to_job_model_conversion(job_manager: JobManager):
    job_id_str = str(uuid.uuid4())
    now_iso = datetime.utcnow().isoformat()
    firestore_data = {
        "id": job_id_str,
        "status": "failed",
        "created_at": now_iso,
        "updated_at": now_iso,
        "completed_at": now_iso,
        "error": {"code": "JOB_PROCESSING_ERROR", "message": "Failed hard"},
        "progress": {
            "current_step": "final",
            "total_steps": 1,
            "completed_steps": 1,
            "percentage": 100.0,
        },
        "request_data": {"syllabus_text": "test syllabus"},
        "metadata": {"user": "test_user"},
    }
    job_model = job_manager._firestore_to_job_model(firestore_data)

    assert isinstance(job_model, Job)
    assert job_model.id == UUID(job_id_str)
    assert job_model.status == JobStatus.FAILED
    assert isinstance(job_model.created_at, datetime)
    assert isinstance(job_model.error, JobError)
    assert job_model.error.code == JobErrorCode.JOB_PROCESSING_ERROR
    assert isinstance(job_model.progress, JobProgress)
    assert job_model.progress.percentage == 100.0


# Test get_job_manager singleton behavior (optional, depends on how critical it is)
def test_get_job_manager_singleton(mock_job_settings):
    with patch("app.services.job_manager.get_settings", return_value=mock_job_settings):
        with patch(
            "app.services.job_manager.get_cloud_tasks_client"
        ):  # Mock its dependency
            jm1 = asyncio.run(get_job_manager())
            jm2 = asyncio.run(get_job_manager())
            assert jm1 is jm2
