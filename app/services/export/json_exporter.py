"""
JSON exporter for content export functionality.
"""

import json
from typing import List, Optional

from app.models.pydantic.content import GeneratedContent
from app.services.export.base import BaseExporter, ExportFormat, ExportOptions


class JSONExporter(BaseExporter):
    """Exporter for JSON format."""

    def __init__(self):
        """Initialize the JSON exporter."""
        super().__init__(ExportFormat.JSON)

    async def export_single(self, content: GeneratedContent, options: Optional[ExportOptions] = None) -> bytes:
        """
        Export a single content item as JSON.

        Args:
            content: The content to export
            options: Export options

        Returns:
            JSON bytes
        """
        data = self._prepare_content_data(content, options)

        # Convert to JSON with proper formatting
        json_str = json.dumps(data, indent=2, ensure_ascii=False, default=str)
        return json_str.encode("utf-8")

    async def export_batch(self, contents: List[GeneratedContent], options: Optional[ExportOptions] = None) -> bytes:
        """
        Export multiple content items as JSON array.

        Args:
            contents: List of contents to export
            options: Export options

        Returns:
            JSON bytes
        """
        data_list = [self._prepare_content_data(content, options) for content in contents]

        # Wrap in a container with metadata
        export_data = {
            "export_info": {
                "total_items": len(contents),
                "format": self.format_type.value,
                "exported_at": data_list[0]["export_metadata"]["exported_at"] if data_list else None,
            },
            "contents": data_list,
        }

        json_str = json.dumps(export_data, indent=2, ensure_ascii=False, default=str)
        return json_str.encode("utf-8")

    def get_content_type(self) -> str:
        """Get MIME content type for JSON."""
        return "application/json"

    def get_file_extension(self) -> str:
        """Get file extension for JSON."""
        return "json"
