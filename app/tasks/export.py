"""
Export-related background tasks.
"""

import logging
from typing import Any, Dict, List, Optional

from app.models.export import ExportFormat
from app.services.export_manager import ExportManager

logger = logging.getLogger(__name__)

# Initialize export manager
export_manager = ExportManager()


async def process_export_task(
    job_id: str, user_id: str, content_ids: List[str], format: str, options: Optional[Dict[str, Any]] = None
):
    """
    Process an export job as a background task.

    This function is called by FastAPI's BackgroundTasks or
    can be adapted for use with Celery or other task queues.

    Args:
        job_id: Export job ID
        user_id: User ID requesting the export
        content_ids: List of content IDs to export
        format: Export format as string
        options: Export options
    """
    try:
        logger.info(f"Starting export task {job_id} for user {user_id}")

        # Convert format string to enum
        export_format = ExportFormat(format)

        # Process the export
        await export_manager.process_export_job(
            job_id=job_id, user_id=user_id, content_ids=content_ids, format=export_format, options=options
        )

        logger.info(f"Export task {job_id} completed successfully")

    except Exception as e:
        logger.error(f"Error in export task {job_id}: {str(e)}", exc_info=True)
        raise


async def cleanup_expired_exports_task(days_to_keep: int = 7):
    """
    Clean up expired export files.

    This task should be run periodically (e.g., daily) to remove
    old export files and free up storage space.

    Args:
        days_to_keep: Number of days to keep export files
    """
    try:
        logger.info(f"Starting cleanup of exports older than {days_to_keep} days")

        await export_manager.cleanup_expired_exports(days_to_keep=days_to_keep)

        logger.info("Export cleanup completed successfully")

    except Exception as e:
        logger.error(f"Error in export cleanup task: {str(e)}", exc_info=True)
        raise
