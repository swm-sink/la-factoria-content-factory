"""
Tests for individual exporter implementations.
"""

import json
from io import BytesIO

import pytest

from app.models.pydantic.content import (
    ContentOutline,
    FAQCollection,
    FAQItem,
    FlashcardCollection,
    FlashcardItem,
    GeneratedContent,
    OutlineSection,
    StudyGuide,
)
from app.services.export import CSVExporter, DOCXExporter, ExportOptions, JSONExporter, PDFExporter, TXTExporter


@pytest.fixture
def sample_content():
    """Create sample content for testing."""
    return GeneratedContent(
        content_outline=ContentOutline(
            title="Test Content Title",
            overview="This is a test overview of the content.",
            learning_objectives=[
                "Understand basic concepts",
                "Apply knowledge practically",
                "Evaluate different approaches",
            ],
            sections=[
                OutlineSection(
                    section_number=1,
                    title="Introduction",
                    description="This section introduces the main concepts.",
                    key_points=["Key point 1", "Key point 2"],
                    estimated_duration_minutes=15.0,
                ),
                OutlineSection(
                    section_number=2,
                    title="Main Content",
                    description="This section covers the core material.",
                    key_points=["Core concept 1", "Core concept 2", "Core concept 3"],
                    estimated_duration_minutes=30.0,
                ),
            ],
            estimated_total_duration=45.0,
            target_audience="University students",
            difficulty_level="intermediate",
        ),
        study_guide=StudyGuide(
            title="Test Content Title",
            overview="Study guide overview",
            key_concepts=["Concept 1", "Concept 2", "Concept 3", "Concept 4", "Concept 5"],
            detailed_content="This is the detailed content of the study guide.",
            summary="This is a summary of the key points.",
            recommended_reading=["Book 1", "Article 2"],
        ),
        faqs=FAQCollection(
            title="Frequently Asked Questions",
            items=[
                FAQItem(
                    question="What is the main concept?",
                    answer="The main concept is about understanding the fundamentals.",
                    category="General",
                ),
                FAQItem(
                    question="How do I apply this knowledge?",
                    answer="You can apply this knowledge through practical exercises.",
                    category="Application",
                ),
                FAQItem(
                    question="What are the prerequisites?",
                    answer="Basic understanding of the subject is required.",
                    category="Prerequisites",
                ),
                FAQItem(
                    question="How long does it take to complete?",
                    answer="Approximately 45 minutes for the full content.",
                    category="Time",
                ),
                FAQItem(
                    question="Where can I find more resources?",
                    answer="Check the recommended reading section for additional resources.",
                    category="Resources",
                ),
            ],
        ),
        flashcards=FlashcardCollection(
            title="Study Flashcards",
            items=[
                FlashcardItem(term="Term 1", definition="Definition of term 1", category="Basic", difficulty="easy"),
                FlashcardItem(term="Term 2", definition="Definition of term 2", category="Advanced", difficulty="hard"),
            ]
            + [
                FlashcardItem(
                    term=f"Term {i}", definition=f"Definition of term {i}", category="Intermediate", difficulty="medium"
                )
                for i in range(3, 11)  # Create 10 total flashcards
            ],
        ),
    )


class TestJSONExporter:
    """Test JSON exporter functionality."""

    @pytest.mark.asyncio
    async def test_export_single(self, sample_content):
        """Test exporting a single content item as JSON."""
        exporter = JSONExporter()

        # Export content
        result = await exporter.export_single(sample_content)

        # Verify result is bytes
        assert isinstance(result, bytes)

        # Parse JSON
        data = json.loads(result.decode("utf-8"))

        # Verify structure
        assert data["title"] == "Test Content Title"
        assert data["overview"] == "This is a test overview of the content."
        assert len(data["learning_objectives"]) == 3
        assert len(data["sections"]) == 2
        assert data["sections"][0]["title"] == "Introduction"

        # Verify optional content is included
        assert "study_guide" in data
        assert "faqs" in data
        assert "flashcards" in data

        # Verify export metadata
        assert "export_metadata" in data
        assert data["export_metadata"]["format"] == "json"

    @pytest.mark.asyncio
    async def test_export_batch(self, sample_content):
        """Test exporting multiple content items as JSON."""
        exporter = JSONExporter()

        # Export multiple contents
        contents = [sample_content, sample_content]
        result = await exporter.export_batch(contents)

        # Parse JSON
        data = json.loads(result.decode("utf-8"))

        # Verify structure
        assert "export_info" in data
        assert data["export_info"]["total_items"] == 2
        assert data["export_info"]["format"] == "json"

        assert "contents" in data
        assert len(data["contents"]) == 2

    def test_content_type(self):
        """Test correct MIME type for JSON."""
        exporter = JSONExporter()
        assert exporter.get_content_type() == "application/json"

    def test_file_extension(self):
        """Test correct file extension for JSON."""
        exporter = JSONExporter()
        assert exporter.get_file_extension() == "json"


class TestCSVExporter:
    """Test CSV exporter functionality."""

    @pytest.mark.asyncio
    async def test_export_single(self, sample_content):
        """Test exporting a single content item as CSV."""
        exporter = CSVExporter()

        # Export content
        result = await exporter.export_single(sample_content)

        # Verify result is bytes
        assert isinstance(result, bytes)

        # Parse CSV
        csv_text = result.decode("utf-8")
        lines = csv_text.strip().split("\n")

        # Verify header is present
        assert len(lines) > 1
        header = lines[0]
        assert "content_type" in header
        assert "title" in header
        assert "item_type" in header

        # Verify some content rows
        content_rows = lines[1:]
        assert len(content_rows) > 0

        # Check for different item types
        item_types = set()
        for row in content_rows:
            if "learning_objective" in row:
                item_types.add("learning_objective")
            elif "section" in row:
                item_types.add("section")
            elif "faq" in row:
                item_types.add("faq")
            elif "flashcard" in row:
                item_types.add("flashcard")

        assert "learning_objective" in item_types
        assert "section" in item_types
        assert "faq" in item_types
        assert "flashcard" in item_types

    @pytest.mark.asyncio
    async def test_export_batch(self, sample_content):
        """Test exporting multiple content items as CSV."""
        exporter = CSVExporter()

        # Export multiple contents
        contents = [sample_content, sample_content]
        result = await exporter.export_batch(contents)

        # Parse CSV
        csv_text = result.decode("utf-8")
        lines = csv_text.strip().split("\n")

        # Verify content_index column is added
        header = lines[0]
        assert "content_index" in header

    def test_content_type(self):
        """Test correct MIME type for CSV."""
        exporter = CSVExporter()
        assert exporter.get_content_type() == "text/csv"

    def test_file_extension(self):
        """Test correct file extension for CSV."""
        exporter = CSVExporter()
        assert exporter.get_file_extension() == "csv"


class TestTXTExporter:
    """Test TXT exporter functionality."""

    @pytest.mark.asyncio
    async def test_export_single(self, sample_content):
        """Test exporting a single content item as plain text."""
        exporter = TXTExporter()

        # Export content
        result = await exporter.export_single(sample_content)

        # Verify result is bytes
        assert isinstance(result, bytes)

        # Parse text
        text = result.decode("utf-8")

        # Verify content structure
        assert "# Test Content Title" in text
        assert "## Overview" in text
        assert "## Learning Objectives" in text
        assert "## Content Sections" in text

        # Verify sections
        assert "### Section 1: Introduction" in text
        assert "### Section 2: Main Content" in text

        # Verify other content types
        assert "## Study Guide" in text
        assert "## Frequently Asked Questions" in text
        assert "## Study Flashcards" in text

    @pytest.mark.asyncio
    async def test_export_batch(self, sample_content):
        """Test exporting multiple content items as plain text."""
        exporter = TXTExporter()

        # Export multiple contents
        contents = [sample_content, sample_content]
        result = await exporter.export_batch(contents)

        # Parse text
        text = result.decode("utf-8")

        # Verify separator between contents
        assert "=" * 80 in text

        # Verify both contents are present
        assert text.count("# Test Content Title") == 2

    def test_content_type(self):
        """Test correct MIME type for TXT."""
        exporter = TXTExporter()
        assert exporter.get_content_type() == "text/plain"

    def test_file_extension(self):
        """Test correct file extension for TXT."""
        exporter = TXTExporter()
        assert exporter.get_file_extension() == "txt"


class TestPDFExporter:
    """Test PDF exporter functionality."""

    @pytest.mark.asyncio
    async def test_export_single(self, sample_content):
        """Test exporting a single content item as PDF."""
        exporter = PDFExporter()

        # Export content
        result = await exporter.export_single(sample_content)

        # Verify result is bytes
        assert isinstance(result, bytes)

        # Verify PDF header
        assert result.startswith(b"%PDF")

    @pytest.mark.asyncio
    async def test_export_batch(self, sample_content):
        """Test exporting multiple content items as PDF."""
        exporter = PDFExporter()

        # Export multiple contents
        contents = [sample_content, sample_content]
        result = await exporter.export_batch(contents)

        # Verify result is bytes
        assert isinstance(result, bytes)

        # Verify PDF header
        assert result.startswith(b"%PDF")

    def test_content_type(self):
        """Test correct MIME type for PDF."""
        exporter = PDFExporter()
        assert exporter.get_content_type() == "application/pdf"

    def test_file_extension(self):
        """Test correct file extension for PDF."""
        exporter = PDFExporter()
        assert exporter.get_file_extension() == "pdf"


class TestDOCXExporter:
    """Test DOCX exporter functionality."""

    @pytest.mark.asyncio
    async def test_export_single(self, sample_content):
        """Test exporting a single content item as DOCX."""
        exporter = DOCXExporter()

        # Export content
        result = await exporter.export_single(sample_content)

        # Verify result is bytes
        assert isinstance(result, bytes)

        # DOCX files are actually ZIP archives
        # Verify ZIP header (PK)
        assert result.startswith(b"PK")

    @pytest.mark.asyncio
    async def test_export_batch(self, sample_content):
        """Test exporting multiple content items as DOCX."""
        exporter = DOCXExporter()

        # Export multiple contents
        contents = [sample_content, sample_content]
        result = await exporter.export_batch(contents)

        # Verify result is bytes
        assert isinstance(result, bytes)

        # Verify ZIP header
        assert result.startswith(b"PK")

    def test_content_type(self):
        """Test correct MIME type for DOCX."""
        exporter = DOCXExporter()
        expected = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        assert exporter.get_content_type() == expected

    def test_file_extension(self):
        """Test correct file extension for DOCX."""
        exporter = DOCXExporter()
        assert exporter.get_file_extension() == "docx"
