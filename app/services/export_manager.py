"""
Export manager service to coordinate content export operations.
"""

import io
import logging
import os
import tempfile
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple
from uuid import uuid4

from app.models.export import ExportFormat, ExportJob, ExportStatus
from app.models.pydantic.content import ContentResponse, GeneratedContent
from app.services.export import BaseExporter, CSVExporter, DOCXExporter, JSONExporter, PDFExporter, TXTExporter
from app.services.export_monitor import export_monitor
from app.services.job.firestore_client import (
    batch_get_documents,
    create_or_update_job_in_firestore,
    get_job_from_firestore,
    query_documents,
)

logger = logging.getLogger(__name__)


class ExportManager:
    """Manager for coordinating content export operations."""

    def __init__(self):
        """Initialize the export manager."""
        self.exporters: Dict[ExportFormat, BaseExporter] = {
            ExportFormat.JSON: JSONExporter(),
            ExportFormat.CSV: CSVExporter(),
            ExportFormat.PDF: PDFExporter(),
            ExportFormat.DOCX: DOCXExporter(),
            ExportFormat.TXT: TXTExporter(),
        }
        self.temp_storage_path = os.environ.get("EXPORT_TEMP_PATH", "/tmp/exports")
        self._ensure_temp_storage()

    def _ensure_temp_storage(self):
        """Ensure temporary storage directory exists."""
        os.makedirs(self.temp_storage_path, exist_ok=True)

    async def process_export_job(
        self,
        job_id: str,
        user_id: str,
        content_ids: List[str],
        format: ExportFormat,
        options: Optional[Dict[str, Any]] = None,
    ):
        """
        Process an export job asynchronously.

        Args:
            job_id: Export job ID
            user_id: User ID requesting the export
            content_ids: List of content IDs to export
            format: Export format
            options: Export options
        """
        logger.info(f"Processing export job {job_id} for user {user_id}")
        start_time = datetime.utcnow()

        # Record export request in monitoring
        await export_monitor.record_export_request(format, len(content_ids))

        try:
            # Update job status to processing
            await self._update_job_status(job_id, ExportStatus.PROCESSING, progress=10.0)

            # Fetch content from database
            contents = await self._fetch_contents(user_id, content_ids)

            if not contents:
                raise ValueError("No content found for export")

            # Update progress
            await self._update_job_status(job_id, ExportStatus.PROCESSING, progress=30.0)

            # Get the appropriate exporter
            exporter = self.exporters.get(format)
            if not exporter:
                raise ValueError(f"Unsupported export format: {format}")

            # Export content
            if len(contents) == 1:
                export_bytes = await exporter.export_single(contents[0], options)
            else:
                export_bytes = await exporter.export_batch(contents, options)

            # Update progress
            await self._update_job_status(job_id, ExportStatus.PROCESSING, progress=70.0)

            # Save export file
            file_path = await self._save_export_file(job_id, user_id, export_bytes, exporter.get_file_extension())

            # Generate download URL (in production, this would be a signed URL)
            download_url = f"/api/export/jobs/{job_id}/download"
            expires_at = datetime.utcnow() + timedelta(hours=24)

            # Update job as completed
            completed_at = datetime.utcnow()
            await self._update_job_status(
                job_id,
                ExportStatus.COMPLETED,
                progress=100.0,
                file_size=len(export_bytes),
                download_url=download_url,
                expires_at=expires_at,
                completed_at=completed_at,
            )

            # Record completion in monitoring
            duration = (completed_at - start_time).total_seconds()
            await export_monitor.record_export_completion(
                format=format,
                duration_seconds=duration,
                file_size_bytes=len(export_bytes),
                status=ExportStatus.COMPLETED,
            )

            logger.info(f"Export job {job_id} completed successfully")

        except Exception as e:
            logger.error(f"Error processing export job {job_id}: {str(e)}")

            # Record error in monitoring
            await export_monitor.record_export_error(format=format, error_type=type(e).__name__, error_message=str(e))

            await self._update_job_status(job_id, ExportStatus.FAILED, error_message=str(e))

    async def _fetch_contents(self, user_id: str, content_ids: List[str]) -> List[GeneratedContent]:
        """
        Fetch content items from the database.

        Args:
            user_id: User ID
            content_ids: List of content IDs

        Returns:
            List of GeneratedContent objects
        """
        # Batch fetch content documents
        content_docs = await batch_get_documents(content_ids, "content")

        contents = []
        for content_id, doc_data in content_docs.items():
            if doc_data and doc_data.get("user_id") == user_id:
                # Parse content response
                content_response = ContentResponse(**doc_data)
                contents.append(content_response.content)

        return contents

    async def _save_export_file(self, job_id: str, user_id: str, content: bytes, extension: str) -> str:
        """
        Save export file to temporary storage.

        Args:
            job_id: Export job ID
            user_id: User ID
            content: File content bytes
            extension: File extension

        Returns:
            File path
        """
        # Create user directory
        user_dir = os.path.join(self.temp_storage_path, user_id)
        os.makedirs(user_dir, exist_ok=True)

        # Save file
        filename = f"export_{job_id}.{extension}"
        file_path = os.path.join(user_dir, filename)

        with open(file_path, "wb") as f:
            f.write(content)

        return file_path

    async def get_export_file(self, job_id: str, user_id: str) -> Tuple[io.BytesIO, str, str]:
        """
        Get export file for download.

        Args:
            job_id: Export job ID
            user_id: User ID

        Returns:
            Tuple of (file content, content type, filename)
        """
        # Get job details
        job_data = await get_job_from_firestore("export_jobs", job_id)
        if not job_data:
            raise FileNotFoundError("Export job not found")

        export_job = ExportJob(**job_data)

        # Get exporter for content type
        exporter = self.exporters.get(export_job.format)
        if not exporter:
            raise ValueError(f"Unknown export format: {export_job.format}")

        # Find file
        filename = f"export_{job_id}.{exporter.get_file_extension()}"
        file_path = os.path.join(self.temp_storage_path, user_id, filename)

        if not os.path.exists(file_path):
            raise FileNotFoundError("Export file not found")

        # Read file
        with open(file_path, "rb") as f:
            content = io.BytesIO(f.read())

        content.seek(0)
        return content, exporter.get_content_type(), filename

    async def _update_job_status(
        self,
        job_id: str,
        status: ExportStatus,
        progress: Optional[float] = None,
        file_size: Optional[int] = None,
        download_url: Optional[str] = None,
        expires_at: Optional[datetime] = None,
        error_message: Optional[str] = None,
        completed_at: Optional[datetime] = None,
    ):
        """Update export job status in database."""
        update_data = {"status": status.value, "updated_at": datetime.utcnow()}

        if progress is not None:
            update_data["progress"] = progress
        if file_size is not None:
            update_data["file_size"] = file_size
        if download_url is not None:
            update_data["download_url"] = download_url
        if expires_at is not None:
            update_data["expires_at"] = expires_at
        if error_message is not None:
            update_data["error_message"] = error_message
        if completed_at is not None:
            update_data["completed_at"] = completed_at

        await create_or_update_job_in_firestore("export_jobs", job_id, update_data)

    async def query_content_ids(self, user_id: str, filters: Dict[str, Any], max_items: int = 1000) -> List[str]:
        """
        Query content IDs based on filters.

        Args:
            user_id: User ID
            filters: Filter criteria
            max_items: Maximum number of items

        Returns:
            List of content IDs
        """
        # Build query filters
        query_filters = {"user_id": user_id}

        # Add date filters
        if "date_from" in filters:
            query_filters["created_at__gte"] = filters["date_from"]
        if "date_to" in filters:
            query_filters["created_at__lte"] = filters["date_to"]

        # Add content type filters
        if "content_types" in filters:
            query_filters["content_type__in"] = filters["content_types"]

        # Query content collection
        results = await query_documents(
            collection="content", filters=query_filters, limit=max_items, order_by="created_at", order_direction="desc"
        )

        # Extract content IDs
        return [doc["id"] for doc in results]

    async def cancel_export_job(self, job_id: str, user_id: str):
        """
        Cancel an export job.

        Args:
            job_id: Export job ID
            user_id: User ID
        """
        # Update job status to cancelled
        await self._update_job_status(job_id, ExportStatus.FAILED, error_message="Export cancelled by user")

        # Clean up any temporary files
        try:
            user_dir = os.path.join(self.temp_storage_path, user_id)
            for extension in ["json", "csv", "pdf", "docx", "txt"]:
                file_path = os.path.join(user_dir, f"export_{job_id}.{extension}")
                if os.path.exists(file_path):
                    os.remove(file_path)
        except Exception as e:
            logger.error(f"Error cleaning up export files: {str(e)}")

    async def cleanup_expired_exports(self, days_to_keep: int = 7):
        """
        Clean up expired export files.

        Args:
            days_to_keep: Number of days to keep export files
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days_to_keep)

        # Walk through temp storage directory
        for user_id in os.listdir(self.temp_storage_path):
            user_dir = os.path.join(self.temp_storage_path, user_id)
            if not os.path.isdir(user_dir):
                continue

            for filename in os.listdir(user_dir):
                file_path = os.path.join(user_dir, filename)

                # Check file modification time
                if os.path.getmtime(file_path) < cutoff_date.timestamp():
                    try:
                        os.remove(file_path)
                        logger.info(f"Removed expired export file: {file_path}")
                    except Exception as e:
                        logger.error(f"Error removing export file {file_path}: {str(e)}")
