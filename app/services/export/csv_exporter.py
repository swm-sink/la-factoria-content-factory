"""
CSV exporter for content export functionality.
"""

import csv
import io
from typing import List, Optional

from app.models.pydantic.content import GeneratedContent
from app.services.export.base import BaseExporter, ExportFormat, ExportOptions


class CSVExporter(BaseExporter):
    """Exporter for CSV format."""

    def __init__(self):
        """Initialize the CSV exporter."""
        super().__init__(ExportFormat.CSV)

    async def export_single(self, content: GeneratedContent, options: Optional[ExportOptions] = None) -> bytes:
        """
        Export a single content item as CSV.

        Args:
            content: The content to export
            options: Export options

        Returns:
            CSV bytes
        """
        rows = self._flatten_content_for_csv(content)

        # Create CSV in memory
        output = io.StringIO()

        if rows:
            # Get all unique keys for headers
            all_keys = set()
            for row in rows:
                all_keys.update(row.keys())
            headers = sorted(all_keys)

            writer = csv.DictWriter(output, fieldnames=headers)
            writer.writeheader()
            writer.writerows(rows)

        # Convert to bytes
        csv_str = output.getvalue()
        return csv_str.encode("utf-8")

    async def export_batch(self, contents: List[GeneratedContent], options: Optional[ExportOptions] = None) -> bytes:
        """
        Export multiple content items as CSV.

        Args:
            contents: List of contents to export
            options: Export options

        Returns:
            CSV bytes
        """
        all_rows = []

        # Flatten all contents
        for idx, content in enumerate(contents):
            rows = self._flatten_content_for_csv(content)
            # Add content index to distinguish between different contents
            for row in rows:
                row["content_index"] = idx + 1
            all_rows.extend(rows)

        # Create CSV in memory
        output = io.StringIO()

        if all_rows:
            # Get all unique keys for headers
            all_keys = set()
            for row in all_rows:
                all_keys.update(row.keys())
            headers = sorted(all_keys)

            writer = csv.DictWriter(output, fieldnames=headers)
            writer.writeheader()
            writer.writerows(all_rows)

        # Convert to bytes
        csv_str = output.getvalue()
        return csv_str.encode("utf-8")

    def get_content_type(self) -> str:
        """Get MIME content type for CSV."""
        return "text/csv"

    def get_file_extension(self) -> str:
        """Get file extension for CSV."""
        return "csv"
