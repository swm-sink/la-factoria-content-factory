# Export Feature Documentation

## Overview

The export feature allows users to download their generated content in various formats including JSON, CSV, PDF, DOCX, and plain text. The system supports both single and batch exports with asynchronous processing for optimal performance.

## Supported Export Formats

1. **JSON** - Structured data format with full metadata
2. **CSV** - Tabular format for spreadsheet analysis
3. **PDF** - Formatted documents for printing/sharing
4. **DOCX** - Editable Word documents
5. **TXT** - Plain text for simple consumption

## API Endpoints

### Create Export Job
```
POST /api/export/
```
Creates an asynchronous export job for specified content items.

**Request Body:**
```json
{
  "content_ids": ["content-1", "content-2"],
  "format": "pdf",
  "include_metadata": true,
  "include_quality_metrics": true
}
```

### Get Export Job Status
```
GET /api/export/jobs/{job_id}
```
Returns the current status and progress of an export job.

### Download Export
```
GET /api/export/jobs/{job_id}/download
```
Downloads the exported file once the job is completed.

### List Export Jobs
```
GET /api/export/jobs?page=1&page_size=20&status=completed
```
Lists export jobs for the current user with pagination and filtering.

### Bulk Export
```
POST /api/export/bulk
```
Creates an export job based on filter criteria rather than explicit content IDs.

**Request Body:**
```json
{
  "format": "json",
  "filters": {
    "date_from": "2024-01-01",
    "date_to": "2024-12-31",
    "content_types": ["study_guide", "flashcards"]
  },
  "max_items": 100
}
```

### Cancel Export Job
```
DELETE /api/export/jobs/{job_id}
```
Cancels a pending or processing export job.

### Get Export Formats
```
GET /api/export/formats
```
Returns list of supported export formats with descriptions.

## Features

### Asynchronous Processing
- Export jobs are processed in the background
- Real-time progress tracking
- Non-blocking API responses

### Batch Export
- Export multiple content items in a single file
- Support for up to 100 items per export
- Filtered exports based on date ranges and content types

### Security
- User authentication required
- Users can only export their own content
- Secure download URLs with 24-hour expiration

### Monitoring
- Prometheus metrics for export operations
- Export duration tracking
- File size monitoring
- Error rate tracking

### File Management
- Temporary file storage with automatic cleanup
- Configurable retention period (default: 7 days)
- Efficient disk space usage

## Export Content Structure

Each export includes:
- Content outline with sections and learning objectives
- Study guides (if available)
- FAQs (if available)
- Flashcards (if available)
- Reading guide questions (if available)
- Metadata and quality metrics (optional)

## Error Handling

The system handles various error scenarios:
- Content not found
- Invalid export format
- User permission errors
- File generation failures
- Storage space issues

All errors are logged and tracked in monitoring metrics.

## Configuration

Environment variables:
- `EXPORT_TEMP_PATH` - Directory for temporary export files (default: `/tmp/exports`)

## Usage Examples

### Export Single Content as PDF
```python
response = requests.post(
    "/api/export/",
    json={
        "content_ids": ["content-123"],
        "format": "pdf",
        "include_metadata": True
    },
    headers={"Authorization": f"Bearer {token}"}
)
job_id = response.json()["job_id"]

# Check status
status = requests.get(f"/api/export/jobs/{job_id}")

# Download when ready
if status.json()["status"] == "completed":
    download = requests.get(f"/api/export/jobs/{job_id}/download")
    with open("export.pdf", "wb") as f:
        f.write(download.content)
```

### Bulk Export with Filters
```python
response = requests.post(
    "/api/export/bulk",
    json={
        "format": "csv",
        "filters": {
            "date_from": "2024-01-01",
            "content_types": ["study_guide"]
        },
        "max_items": 50
    },
    headers={"Authorization": f"Bearer {token}"}
)
```

## Testing

Run the validation script to verify functionality:
```bash
python scripts/validate_export_feature.py
```

Run unit tests:
```bash
pytest tests/services/export/
```