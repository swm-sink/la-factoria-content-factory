"""
Prompt templates for multi-step content generation.
These prompts are designed to work with the MultiStepContentGenerationService.
"""

class MultiStepPrompts:
    """Prompt templates for multi-step content generation."""
    
    @staticmethod
    def get_topic_decomposition_prompt(syllabus_text: str) -> str:
        """Generate prompt for decomposing syllabus into topics."""
        return f"""
        Using the standards in @.cursor/rules/project.mdc, analyze the following syllabus text and decompose it into major topics and subtopics.
        For each topic, identify key concepts, learning objectives, and potential content formats.
        
        Syllabus Text:
        {syllabus_text}
        
        Output a JSON object with the following structure:
        {{
            "topics": [
                {{
                    "title": "Topic Title",
                    "subtopics": [
                        {{
                            "title": "Subtopic Title",
                            "key_concepts": ["concept1", "concept2"],
                            "learning_objectives": ["objective1", "objective2"],
                            "suggested_formats": ["podcast", "guide", "one_pager"]
                        }}
                    ],
                    "estimated_duration": 10,  # in minutes
                    "complexity": "beginner|intermediate|advanced"
                }}
            ],
            "total_topics": 0,
            "estimated_total_duration": 0
        }}
        
        Ensure the decomposition is logical, comprehensive, and suitable for creating engaging educational content.
        """

    @staticmethod
    def get_section_outline_prompt(
        topic: dict,
        target_format: str,
        target_duration: float = None,
        target_pages: int = None
    ) -> str:
        """Generate prompt for creating a detailed outline for a section."""
        duration_str = f"approximately {target_duration} minutes" if target_duration else "appropriate length"
        pages_str = f"approximately {target_pages} pages" if target_pages else "appropriate length"
        
        return f"""
        Create a detailed outline for a {target_format} on the following topic:
        
        Topic: {topic['title']}
        Key Concepts: {', '.join(topic['subtopics'][0]['key_concepts'])}
        Learning Objectives: {', '.join(topic['subtopics'][0]['learning_objectives'])}
        Target Length: {duration_str if target_format == 'podcast' else pages_str}
        
        Output a JSON object with the following structure:
        {{
            "title": "Section Title",
            "sections": [
                {{
                    "title": "Section Title",
                    "subsections": [
                        {{
                            "title": "Subsection Title",
                            "key_points": ["point1", "point2"],
                            "estimated_duration": 5,  # in minutes
                            "notes": "Additional context or requirements"
                        }}
                    ]
                }}
            ],
            "introduction": {{
                "hook": "Engaging opening",
                "overview": "Brief topic overview",
                "objectives": ["objective1", "objective2"]
            }},
            "conclusion": {{
                "summary": "Key takeaways",
                "next_steps": "Suggested follow-up topics or activities"
            }}
        }}
        
        Ensure the outline is engaging, well-structured, and suitable for the target format.
        """

    @staticmethod
    def get_section_content_prompt(
        topic: dict,
        outline: dict,
        target_format: str
    ) -> str:
        """Generate prompt for creating detailed content for a section."""
        format_specific_instructions = {
            'podcast': """
                - Write in a conversational, engaging tone
                - Include speaker notes and timing cues
                - Add suggested sound effects or music transitions
                - Include potential Q&A or discussion points
            """,
            'guide': """
                - Write in a clear, instructional tone
                - Include examples and practical applications
                - Add study questions and exercises
                - Include references to additional resources
            """,
            'one_pager': """
                - Write in a concise, informative tone
                - Focus on key takeaways and main points
                - Use bullet points and short paragraphs
                - Include a brief summary and next steps
            """
        }
        
        return f"""
        Using the following outline, generate detailed content for a {target_format}:
        
        Topic: {topic['title']}
        Outline: {outline}
        
        {format_specific_instructions.get(target_format, '')}
        
        Output a JSON object with the following structure:
        {{
            "title": "Content Title",
            "text": "The full content text...",
            "metadata": {{
                "word_count": 0,
                "estimated_duration": 0,
                "format": "{target_format}",
                "sections": [
                    {{
                        "title": "Section Title",
                        "content": "Section content...",
                        "word_count": 0,
                        "estimated_duration": 0
                    }}
                ]
            }}
        }}
        
        Ensure the content is engaging, accurate, and follows the format-specific requirements.
        """

    @staticmethod
    def get_content_assembly_prompt(
        sections: list,
        target_format: str
    ) -> str:
        """Generate prompt for assembling and enhancing final content."""
        sections_text = "\n".join([
            f"Section {i+1}: {s.title}\n{s.content}\n"
            for i, s in enumerate(sections)
        ])
        
        return f"""
        Assemble and enhance the following sections into a cohesive {target_format}:
        
        {sections_text}
        
        Output a JSON object with the following structure:
        {{
            "title": "Final Content Title",
            "content": "The assembled and enhanced content...",
            "metadata": {{
                "total_sections": 0,
                "total_word_count": 0,
                "total_duration": 0,
                "format": "{target_format}",
                "enhancements": [
                    {{
                        "type": "transition|introduction|conclusion",
                        "content": "Enhanced content...",
                        "purpose": "Purpose of the enhancement"
                    }}
                ]
            }}
        }}
        
        Ensure the final content:
        1. Flows smoothly between sections
        2. Has a strong introduction and conclusion
        3. Maintains consistent tone and style
        4. Includes appropriate transitions
        5. Meets all format-specific requirements
        """ 