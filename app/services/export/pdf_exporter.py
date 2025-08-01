"""
PDF exporter for content export functionality.
"""

import io
from typing import List, Optional

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    ListFlowable,
    ListItem,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)
from reportlab.platypus.tableofcontents import TableOfContents

from app.models.pydantic.content import GeneratedContent
from app.services.export.base import BaseExporter, ExportFormat, ExportOptions


class PDFExporter(BaseExporter):
    """Exporter for PDF format."""

    def __init__(self):
        """Initialize the PDF exporter."""
        super().__init__(ExportFormat.PDF)
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()

    def _setup_custom_styles(self):
        """Set up custom PDF styles."""
        # Title style
        self.styles.add(
            ParagraphStyle(
                name="CustomTitle",
                parent=self.styles["Heading1"],
                fontSize=24,
                textColor=colors.HexColor("#1a1a1a"),
                spaceAfter=30,
                alignment=1,  # Center alignment
            )
        )

        # Section heading style
        self.styles.add(
            ParagraphStyle(
                name="SectionHeading",
                parent=self.styles["Heading2"],
                fontSize=18,
                textColor=colors.HexColor("#2c3e50"),
                spaceAfter=12,
                spaceBefore=20,
            )
        )

        # Subsection heading style
        self.styles.add(
            ParagraphStyle(
                name="SubsectionHeading",
                parent=self.styles["Heading3"],
                fontSize=14,
                textColor=colors.HexColor("#34495e"),
                spaceAfter=10,
                spaceBefore=15,
            )
        )

        # Custom body text
        self.styles.add(
            ParagraphStyle(name="CustomBody", parent=self.styles["BodyText"], fontSize=11, leading=16, spaceAfter=12)
        )

    async def export_single(self, content: GeneratedContent, options: Optional[ExportOptions] = None) -> bytes:
        """
        Export a single content item as PDF.

        Args:
            content: The content to export
            options: Export options

        Returns:
            PDF bytes
        """
        # Create PDF in memory
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=72)

        # Build content
        story = []

        # Title
        story.append(Paragraph(content.content_outline.title, self.styles["CustomTitle"]))
        story.append(Spacer(1, 0.2 * inch))

        # Overview
        story.append(Paragraph("Overview", self.styles["SectionHeading"]))
        story.append(Paragraph(content.content_outline.overview, self.styles["CustomBody"]))
        story.append(Spacer(1, 0.2 * inch))

        # Learning Objectives
        story.append(Paragraph("Learning Objectives", self.styles["SectionHeading"]))
        objectives_list = ListFlowable(
            [
                ListItem(Paragraph(obj, self.styles["CustomBody"]))
                for obj in content.content_outline.learning_objectives
            ],
            bulletType="bullet",
        )
        story.append(objectives_list)
        story.append(Spacer(1, 0.2 * inch))

        # Metadata
        if content.content_outline.target_audience or content.content_outline.difficulty_level:
            metadata_data = []
            if content.content_outline.target_audience:
                metadata_data.append(["Target Audience:", content.content_outline.target_audience])
            if content.content_outline.difficulty_level:
                metadata_data.append(["Difficulty Level:", content.content_outline.difficulty_level])
            if content.content_outline.estimated_total_duration:
                metadata_data.append(
                    ["Estimated Duration:", f"{content.content_outline.estimated_total_duration} minutes"]
                )

            metadata_table = Table(metadata_data, colWidths=[2 * inch, 4 * inch])
            metadata_table.setStyle(
                TableStyle(
                    [
                        ("FONT", (0, 0), (0, -1), "Helvetica-Bold", 10),
                        ("FONT", (1, 0), (1, -1), "Helvetica", 10),
                        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                        ("VALIGN", (0, 0), (-1, -1), "TOP"),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                    ]
                )
            )
            story.append(metadata_table)
            story.append(Spacer(1, 0.3 * inch))

        # Content Sections
        story.append(Paragraph("Content Sections", self.styles["SectionHeading"]))
        for section in content.content_outline.sections:
            story.append(
                Paragraph(f"Section {section.section_number}: {section.title}", self.styles["SubsectionHeading"])
            )
            story.append(Paragraph(section.description, self.styles["CustomBody"]))

            if section.key_points:
                story.append(Paragraph("Key Points:", self.styles["Normal"]))
                key_points_list = ListFlowable(
                    [ListItem(Paragraph(point, self.styles["Normal"])) for point in section.key_points],
                    bulletType="bullet",
                )
                story.append(key_points_list)

            if section.estimated_duration_minutes:
                story.append(
                    Paragraph(f"<i>Duration: {section.estimated_duration_minutes} minutes</i>", self.styles["Normal"])
                )
            story.append(Spacer(1, 0.2 * inch))

        # Add other content types if present
        if content.study_guide:
            story.append(PageBreak())
            story.append(Paragraph("Study Guide", self.styles["SectionHeading"]))
            story.append(Paragraph(content.study_guide.overview, self.styles["CustomBody"]))

            story.append(Paragraph("Key Concepts", self.styles["SubsectionHeading"]))
            concepts_list = ListFlowable(
                [ListItem(Paragraph(concept, self.styles["Normal"])) for concept in content.study_guide.key_concepts],
                bulletType="bullet",
            )
            story.append(concepts_list)
            story.append(Spacer(1, 0.2 * inch))

            story.append(Paragraph("Detailed Content", self.styles["SubsectionHeading"]))
            story.append(Paragraph(content.study_guide.detailed_content, self.styles["CustomBody"]))
            story.append(Spacer(1, 0.2 * inch))

            story.append(Paragraph("Summary", self.styles["SubsectionHeading"]))
            story.append(Paragraph(content.study_guide.summary, self.styles["CustomBody"]))

        # FAQs
        if content.faqs:
            story.append(PageBreak())
            story.append(Paragraph(content.faqs.title, self.styles["SectionHeading"]))

            for idx, item in enumerate(content.faqs.items):
                story.append(Paragraph(f"Q{idx + 1}: {item.question}", self.styles["SubsectionHeading"]))
                story.append(Paragraph(f"A: {item.answer}", self.styles["CustomBody"]))
                if item.category:
                    story.append(Paragraph(f"<i>Category: {item.category}</i>", self.styles["Normal"]))
                story.append(Spacer(1, 0.1 * inch))

        # Build PDF
        doc.build(story)

        # Get PDF bytes
        buffer.seek(0)
        return buffer.read()

    async def export_batch(self, contents: List[GeneratedContent], options: Optional[ExportOptions] = None) -> bytes:
        """
        Export multiple content items as PDF.

        Args:
            contents: List of contents to export
            options: Export options

        Returns:
            PDF bytes
        """
        # Create PDF in memory
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=72)

        # Build content
        story = []

        # Title page
        story.append(Spacer(1, 2 * inch))
        story.append(Paragraph("Content Export Collection", self.styles["CustomTitle"]))
        story.append(Spacer(1, 0.5 * inch))
        story.append(Paragraph(f"Total Items: {len(contents)}", self.styles["Normal"]))
        story.append(PageBreak())

        # Add each content item
        for idx, content in enumerate(contents):
            if idx > 0:
                story.append(PageBreak())

            # Export single content to story elements
            single_pdf = await self.export_single(content, options)

            # For batch, we'll add content directly to story instead
            # Add content number
            story.append(Paragraph(f"Content Item {idx + 1} of {len(contents)}", self.styles["Normal"]))
            story.append(Spacer(1, 0.2 * inch))

            # Add the content (simplified version for batch)
            story.append(Paragraph(content.content_outline.title, self.styles["CustomTitle"]))
            story.append(Spacer(1, 0.2 * inch))
            story.append(Paragraph(content.content_outline.overview, self.styles["CustomBody"]))
            # ... (add more content as needed)

        # Build PDF
        doc.build(story)

        # Get PDF bytes
        buffer.seek(0)
        return buffer.read()

    def get_content_type(self) -> str:
        """Get MIME content type for PDF."""
        return "application/pdf"

    def get_file_extension(self) -> str:
        """Get file extension for PDF."""
        return "pdf"
