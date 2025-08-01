"""
Text exporter for content export functionality.
"""

from typing import List, Optional

from app.models.pydantic.content import GeneratedContent
from app.services.export.base import BaseExporter, ExportFormat, ExportOptions


class TXTExporter(BaseExporter):
    """Exporter for plain text format."""
    
    def __init__(self):
        """Initialize the text exporter."""
        super().__init__(ExportFormat.TXT)
        
    async def export_single(
        self,
        content: GeneratedContent,
        options: Optional[ExportOptions] = None
    ) -> bytes:
        """
        Export a single content item as plain text.
        
        Args:
            content: The content to export
            options: Export options
            
        Returns:
            Text bytes
        """
        text_lines = []
        
        # Title and overview
        text_lines.append(f"# {content.content_outline.title}")
        text_lines.append("")
        text_lines.append("## Overview")
        text_lines.append(content.content_outline.overview)
        text_lines.append("")
        
        # Learning objectives
        text_lines.append("## Learning Objectives")
        for idx, objective in enumerate(content.content_outline.learning_objectives):
            text_lines.append(f"{idx + 1}. {objective}")
        text_lines.append("")
        
        # Target audience and difficulty
        if content.content_outline.target_audience:
            text_lines.append(f"**Target Audience:** {content.content_outline.target_audience}")
        if content.content_outline.difficulty_level:
            text_lines.append(f"**Difficulty Level:** {content.content_outline.difficulty_level}")
        if content.content_outline.estimated_total_duration:
            text_lines.append(f"**Estimated Duration:** {content.content_outline.estimated_total_duration} minutes")
        text_lines.append("")
        
        # Sections
        text_lines.append("## Content Sections")
        for section in content.content_outline.sections:
            text_lines.append(f"\n### Section {section.section_number}: {section.title}")
            text_lines.append(section.description)
            
            if section.key_points:
                text_lines.append("\n**Key Points:**")
                for point in section.key_points:
                    text_lines.append(f"- {point}")
                    
            if section.estimated_duration_minutes:
                text_lines.append(f"\n*Duration: {section.estimated_duration_minutes} minutes*")
                
        # Study Guide
        if content.study_guide:
            text_lines.append("\n\n## Study Guide")
            text_lines.append(f"\n### {content.study_guide.title}")
            text_lines.append(content.study_guide.overview)
            
            text_lines.append("\n### Key Concepts")
            for concept in content.study_guide.key_concepts:
                text_lines.append(f"- {concept}")
                
            text_lines.append("\n### Detailed Content")
            text_lines.append(content.study_guide.detailed_content)
            
            text_lines.append("\n### Summary")
            text_lines.append(content.study_guide.summary)
            
            if content.study_guide.recommended_reading:
                text_lines.append("\n### Recommended Reading")
                for reading in content.study_guide.recommended_reading:
                    text_lines.append(f"- {reading}")
                    
        # One-Pager Summary
        if content.one_pager_summary:
            text_lines.append("\n\n## One-Page Summary")
            text_lines.append(f"\n### {content.one_pager_summary.title}")
            text_lines.append(content.one_pager_summary.executive_summary)
            
            text_lines.append("\n### Key Takeaways")
            for takeaway in content.one_pager_summary.key_takeaways:
                text_lines.append(f"- {takeaway}")
                
            text_lines.append("\n### Main Content")
            text_lines.append(content.one_pager_summary.main_content)
            
        # Podcast Script
        if content.podcast_script:
            text_lines.append("\n\n## Podcast Script")
            text_lines.append(f"\n### {content.podcast_script.title}")
            
            text_lines.append("\n### Introduction")
            text_lines.append(content.podcast_script.introduction)
            
            text_lines.append("\n### Main Content")
            text_lines.append(content.podcast_script.main_content)
            
            text_lines.append("\n### Conclusion")
            text_lines.append(content.podcast_script.conclusion)
            
            if content.podcast_script.speaker_notes:
                text_lines.append("\n### Speaker Notes")
                for note in content.podcast_script.speaker_notes:
                    text_lines.append(f"- {note}")
                    
        # FAQs
        if content.faqs:
            text_lines.append(f"\n\n## {content.faqs.title}")
            for idx, item in enumerate(content.faqs.items):
                text_lines.append(f"\n### Q{idx + 1}: {item.question}")
                text_lines.append(f"**A:** {item.answer}")
                if item.category:
                    text_lines.append(f"*Category: {item.category}*")
                    
        # Flashcards
        if content.flashcards:
            text_lines.append(f"\n\n## {content.flashcards.title}")
            for idx, item in enumerate(content.flashcards.items):
                text_lines.append(f"\n### Card {idx + 1}")
                text_lines.append(f"**Term:** {item.term}")
                text_lines.append(f"**Definition:** {item.definition}")
                if item.category:
                    text_lines.append(f"*Category: {item.category}*")
                if item.difficulty:
                    text_lines.append(f"*Difficulty: {item.difficulty}*")
                    
        # Reading Guide Questions
        if content.reading_guide_questions:
            text_lines.append(f"\n\n## {content.reading_guide_questions.title}")
            for idx, question in enumerate(content.reading_guide_questions.questions):
                text_lines.append(f"{idx + 1}. {question}")
                
        # Join all lines
        text_content = "\n".join(text_lines)
        return text_content.encode('utf-8')
        
    async def export_batch(
        self,
        contents: List[GeneratedContent],
        options: Optional[ExportOptions] = None
    ) -> bytes:
        """
        Export multiple content items as plain text.
        
        Args:
            contents: List of contents to export
            options: Export options
            
        Returns:
            Text bytes
        """
        text_parts = []
        
        for idx, content in enumerate(contents):
            if idx > 0:
                text_parts.append("\n\n" + "="*80 + "\n\n")
            
            single_export = await self.export_single(content, options)
            text_parts.append(single_export.decode('utf-8'))
            
        combined_text = "".join(text_parts)
        return combined_text.encode('utf-8')
        
    def get_content_type(self) -> str:
        """Get MIME content type for text."""
        return "text/plain"
        
    def get_file_extension(self) -> str:
        """Get file extension for text."""
        return "txt"