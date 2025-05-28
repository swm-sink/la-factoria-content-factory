"""
Content generation prompts for various educational content formats.
Version 1.0 - Supports multiple content types with enhanced features.
"""

from typing import Dict, Any

class ContentGenerationPrompts:
    """Prompt templates for generating various types of educational content."""
    
    @staticmethod
    def get_main_prompt(syllabus_text: str) -> str:
        """Generate the main comprehensive prompt for content generation."""
        return f"""
        Using the standards in @.cursor/rules/project.mdc, generate comprehensive educational content based on the following syllabus text.
        
        Syllabus Text:
        {syllabus_text}
        
        Generate content in ALL of the following formats and return as a single JSON object:
        
        {{
            "content_outline": "A structured outline with main topics and subtopics",
            "podcast_script": "An engaging 15-20 minute podcast script with speaker notes",
            "study_guide": "A comprehensive study guide with key concepts and questions",
            "one_pager_summary": "A concise one-page summary of key points",
            "detailed_reading": "Detailed reading material expanding on the syllabus",
            "faqs": "Frequently asked questions and answers about the topic",
            "flashcards": "Key terms and definitions in flashcard format",
            "reading_guide_questions": "Critical thinking questions for deeper understanding",
            "interactive_exercises": "Hands-on exercises and activities",
            "case_studies": "Real-world case studies related to the topic",
            "assessment_rubric": "Evaluation criteria for understanding the material"
        }}
        
        Ensure all content is:
        1. Educationally sound and age-appropriate
        2. Engaging and well-structured
        3. Factually accurate based on the syllabus
        4. Properly formatted for the intended use
        5. Includes quality metrics and metadata
        """

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
                            "suggested_formats": ["podcast", "guide", "one_pager", "interactive", "case_study"]
                        }}
                    ],
                    "estimated_duration": 10,
                    "complexity": "beginner|intermediate|advanced",
                    "prerequisites": ["prerequisite1", "prerequisite2"]
                }}
            ],
            "total_topics": 0,
            "estimated_total_duration": 0,
            "recommended_sequence": ["topic1", "topic2", "topic3"]
        }}
        
        Ensure the decomposition is logical, comprehensive, and suitable for creating engaging educational content.
        """

    @staticmethod
    def get_interactive_exercises_prompt(syllabus_text: str) -> str:
        """Generate interactive exercises and activities."""
        return f"""
        Create interactive exercises and hands-on activities based on the following syllabus:
        
        {syllabus_text}
        
        Generate exercises that include:
        1. Problem-solving scenarios
        2. Group discussion prompts
        3. Practical applications
        4. Simulation exercises
        5. Creative projects
        
        Format as JSON:
        {{
            "exercises": [
                {{
                    "title": "Exercise Title",
                    "type": "problem_solving|discussion|application|simulation|project",
                    "description": "Detailed description",
                    "instructions": ["step1", "step2", "step3"],
                    "materials_needed": ["material1", "material2"],
                    "estimated_time": "30 minutes",
                    "learning_objectives": ["objective1", "objective2"],
                    "assessment_criteria": ["criteria1", "criteria2"]
                }}
            ]
        }}
        """

    @staticmethod
    def get_case_studies_prompt(syllabus_text: str) -> str:
        """Generate real-world case studies."""
        return f"""
        Create compelling real-world case studies based on the following syllabus:
        
        {syllabus_text}
        
        Generate case studies that:
        1. Illustrate key concepts in practice
        2. Present realistic scenarios
        3. Include decision points and analysis
        4. Connect theory to application
        5. Encourage critical thinking
        
        Format as JSON:
        {{
            "case_studies": [
                {{
                    "title": "Case Study Title",
                    "scenario": "Detailed scenario description",
                    "background": "Context and background information",
                    "key_players": ["person1", "person2"],
                    "challenges": ["challenge1", "challenge2"],
                    "discussion_questions": ["question1", "question2"],
                    "learning_outcomes": ["outcome1", "outcome2"],
                    "additional_resources": ["resource1", "resource2"]
                }}
            ]
        }}
        """

    @staticmethod
    def get_assessment_rubric_prompt(syllabus_text: str) -> str:
        """Generate assessment rubrics for evaluating understanding."""
        return f"""
        Create comprehensive assessment rubrics based on the following syllabus:
        
        {syllabus_text}
        
        Generate rubrics that:
        1. Define clear performance levels
        2. Include specific criteria
        3. Provide measurable outcomes
        4. Support different learning styles
        5. Enable fair and consistent evaluation
        
        Format as JSON:
        {{
            "rubrics": [
                {{
                    "assessment_type": "quiz|project|presentation|discussion|practical",
                    "criteria": [
                        {{
                            "criterion": "Criterion name",
                            "weight": 25,
                            "levels": {{
                                "excellent": "Detailed description of excellent performance",
                                "good": "Detailed description of good performance",
                                "satisfactory": "Detailed description of satisfactory performance",
                                "needs_improvement": "Detailed description of performance needing improvement"
                            }}
                        }}
                    ],
                    "total_points": 100,
                    "grading_scale": {{
                        "A": "90-100",
                        "B": "80-89",
                        "C": "70-79",
                        "D": "60-69",
                        "F": "Below 60"
                    }}
                }}
            ]
        }}
        """

    @staticmethod
    def get_multimedia_content_prompt(syllabus_text: str) -> str:
        """Generate multimedia content suggestions."""
        return f"""
        Create multimedia content suggestions based on the following syllabus:
        
        {syllabus_text}
        
        Generate suggestions for:
        1. Video content ideas
        2. Infographic concepts
        3. Interactive presentations
        4. Audio content
        5. Visual aids and diagrams
        
        Format as JSON:
        {{
            "multimedia_suggestions": [
                {{
                    "type": "video|infographic|presentation|audio|visual_aid",
                    "title": "Content Title",
                    "description": "Detailed description",
                    "key_elements": ["element1", "element2"],
                    "target_audience": "audience description",
                    "estimated_duration": "duration",
                    "production_notes": "Notes for creation",
                    "learning_objectives": ["objective1", "objective2"]
                }}
            ]
        }}
        """

    @staticmethod
    def get_accessibility_enhanced_prompt(syllabus_text: str) -> str:
        """Generate accessibility-enhanced content."""
        return f"""
        Create accessibility-enhanced educational content based on the following syllabus:
        
        {syllabus_text}
        
        Generate content that:
        1. Supports different learning styles (visual, auditory, kinesthetic)
        2. Includes alternative text descriptions
        3. Provides multiple format options
        4. Considers cognitive accessibility
        5. Supports assistive technologies
        
        Format as JSON:
        {{
            "accessible_content": {{
                "visual_learners": {{
                    "diagrams": ["diagram1", "diagram2"],
                    "charts": ["chart1", "chart2"],
                    "color_coding": "Color coding scheme",
                    "visual_summaries": ["summary1", "summary2"]
                }},
                "auditory_learners": {{
                    "audio_descriptions": ["description1", "description2"],
                    "verbal_explanations": ["explanation1", "explanation2"],
                    "discussion_prompts": ["prompt1", "prompt2"]
                }},
                "kinesthetic_learners": {{
                    "hands_on_activities": ["activity1", "activity2"],
                    "movement_exercises": ["exercise1", "exercise2"],
                    "tactile_materials": ["material1", "material2"]
                }},
                "cognitive_support": {{
                    "simplified_language": "Simplified version of key concepts",
                    "step_by_step_guides": ["guide1", "guide2"],
                    "memory_aids": ["aid1", "aid2"],
                    "progress_tracking": "Progress tracking suggestions"
                }}
            }}
        }}
        """

    @staticmethod
    def get_content_outline_prompt(syllabus_text: str) -> str:
        """Generate a structured content outline."""
        return f"""
        Create a comprehensive content outline based on the following syllabus:
        
        {syllabus_text}
        
        The outline should include:
        1. Main topics and subtopics
        2. Key learning objectives
        3. Estimated time for each section
        4. Prerequisites and dependencies
        5. Assessment opportunities
        
        Format as a clear, hierarchical structure.
        """

    @staticmethod
    def get_podcast_script_prompt(syllabus_text: str) -> str:
        """Generate an engaging podcast script."""
        return f"""
        Create an engaging 15-20 minute podcast script based on the following syllabus:
        
        {syllabus_text}
        
        The script should include:
        1. Engaging introduction with hook
        2. Clear structure with transitions
        3. Conversational tone
        4. Speaker notes and timing cues
        5. Interactive elements (questions, pauses)
        6. Strong conclusion with key takeaways
        
        Include [SPEAKER NOTES] and [TIMING: X minutes] throughout.
        """

    @staticmethod
    def get_study_guide_prompt(syllabus_text: str) -> str:
        """Generate a comprehensive study guide."""
        return f"""
        Create a comprehensive study guide based on the following syllabus:
        
        {syllabus_text}
        
        The study guide should include:
        1. Key concepts and definitions
        2. Important facts and figures
        3. Study questions and practice problems
        4. Summary sections
        5. Additional resources for further learning
        6. Self-assessment checklist
        
        Organize in a clear, student-friendly format.
        """

    @staticmethod
    def get_one_pager_summary_prompt(syllabus_text: str) -> str:
        """Generate a concise one-page summary."""
        return f"""
        Create a concise one-page summary based on the following syllabus:
        
        {syllabus_text}
        
        The summary should:
        1. Capture the most important points
        2. Use bullet points and clear formatting
        3. Be scannable and easy to reference
        4. Include key takeaways
        5. Fit on a single page when printed
        
        Aim for 400-600 words maximum.
        """

    @staticmethod
    def get_detailed_reading_prompt(syllabus_text: str) -> str:
        """Generate detailed reading material."""
        return f"""
        Create detailed reading material based on the following syllabus:
        
        {syllabus_text}
        
        The reading should:
        1. Expand on the syllabus topics in depth
        2. Include examples and case studies
        3. Provide context and background
        4. Connect concepts to real-world applications
        5. Include references and further reading suggestions
        
        Write in an engaging, educational style suitable for the target audience.
        """

    @staticmethod
    def get_faqs_prompt(syllabus_text: str) -> str:
        """Generate frequently asked questions."""
        return f"""
        Create a comprehensive FAQ section based on the following syllabus:
        
        {syllabus_text}
        
        Include:
        1. Common questions students might have
        2. Clear, concise answers
        3. Questions about practical applications
        4. Clarifications of complex concepts
        5. Questions about prerequisites and next steps
        
        Aim for 8-12 question-answer pairs.
        """

    @staticmethod
    def get_flashcards_prompt(syllabus_text: str) -> str:
        """Generate flashcards for key terms."""
        return f"""
        Create flashcards for key terms and concepts based on the following syllabus:
        
        {syllabus_text}
        
        Each flashcard should have:
        1. A clear term or concept on the front
        2. A concise definition or explanation on the back
        3. Context or example when helpful
        4. Proper formatting for study apps
        
        Generate 15-25 flashcards covering the most important concepts.
        """

    @staticmethod
    def get_reading_guide_questions_prompt(syllabus_text: str) -> str:
        """Generate critical thinking questions."""
        return f"""
        Create reading guide questions based on the following syllabus:
        
        {syllabus_text}
        
        Include:
        1. Comprehension questions
        2. Analysis questions
        3. Application questions
        4. Synthesis questions
        5. Evaluation questions
        
        Questions should encourage deep thinking and understanding of the material.
        Generate 10-15 questions of varying difficulty levels.
        """ 