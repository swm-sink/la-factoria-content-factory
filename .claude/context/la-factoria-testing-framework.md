# La Factoria Educational Content Testing Framework

## TDD Testing Patterns for Educational Content Generation

### Pytest Configuration for La Factoria
```python
# conftest.py - La Factoria testing configuration
import pytest
import asyncio
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from src.main import app
from src.database import get_async_session
from src.models import Base
import uuid

# Test database configuration
TEST_DATABASE_URL = "postgresql+asyncpg://test:test@localhost:5432/la_factoria_test"

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
async def test_engine():
    """Create test database engine."""
    engine = create_async_engine(TEST_DATABASE_URL, echo=True)
    
    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    # Cleanup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    await engine.dispose()

@pytest.fixture
async def async_session(test_engine):
    """Create test database session."""
    TestSessionFactory = async_sessionmaker(
        bind=test_engine,
        class_=AsyncSession,
        expire_on_commit=False
    )
    
    async with TestSessionFactory() as session:
        yield session

@pytest.fixture
def client(async_session):
    """Create test client with database session override."""
    def override_get_async_session():
        return async_session
    
    app.dependency_overrides[get_async_session] = override_get_async_session
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()

@pytest.fixture
def auth_headers():
    """Provide authentication headers for testing."""
    return {"Authorization": "Bearer test-api-key"}

@pytest.fixture
def sample_learning_objectives():
    """Sample learning objectives for testing."""
    return [
        {
            "cognitive_level": "understand",
            "subject_area": "Mathematics",
            "specific_skill": "Solve linear equations",
            "measurable_outcome": "Student can solve 8/10 linear equations correctly",
            "difficulty_level": 5
        }
    ]

@pytest.fixture
def sample_cognitive_load():
    """Sample cognitive load metrics for testing."""
    return {
        "intrinsic_load": 0.6,
        "extraneous_load": 0.3,
        "germane_load": 0.7,
        "total_cognitive_load": 0.53
    }
```

### Educational Content Generation Tests
```python
# tests/test_educational_content_generation.py
import pytest
from fastapi import status
from src.models.educational import LaFactoriaContentType

class TestEducationalContentGeneration:
    """Test educational content generation for all 8 content types"""
    
    @pytest.mark.asyncio
    async def test_master_outline_generation(
        self, client, auth_headers, sample_learning_objectives, sample_cognitive_load
    ):
        """Test master content outline generation"""
        request_data = {
            "content_type": "master_content_outline",
            "topic": "Introduction to Algebra",
            "age_group": "high_school",
            "learning_objectives": sample_learning_objectives,
            "cognitive_load_target": sample_cognitive_load
        }
        
        response = client.post(
            "/api/content/generate/master_content_outline",
            json=request_data,
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        content = response.json()
        
        # Validate response structure
        assert "id" in content
        assert "content_type" in content
        assert content["content_type"] == "master_content_outline"
        assert "generated_content" in content
        
        # Validate generated content structure (from prompt template)
        generated = content["generated_content"]
        assert "title" in generated
        assert "overview" in generated
        assert "learning_objectives" in generated
        assert "sections" in generated
        assert isinstance(generated["sections"], list)
        assert len(generated["sections"]) > 0
        
        # Validate educational quality
        assert "quality_score" in content
        assert content["quality_score"] >= 0.7  # Minimum quality threshold
    
    @pytest.mark.asyncio
    async def test_podcast_script_generation(
        self, client, auth_headers, sample_learning_objectives, sample_cognitive_load
    ):
        """Test podcast script generation with educational engagement"""
        request_data = {
            "content_type": "podcast_script",
            "topic": "Climate Change Science",
            "age_group": "college",
            "learning_objectives": sample_learning_objectives,
            "cognitive_load_target": sample_cognitive_load
        }
        
        response = client.post(
            "/api/content/generate/podcast_script",
            json=request_data,
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        content = response.json()
        
        # Validate podcast-specific structure
        generated = content["generated_content"]
        assert "title" in generated
        assert "introduction" in generated
        assert "main_content" in generated
        assert "conclusion" in generated
        assert "speaker_notes" in generated
        assert "estimated_duration_minutes" in generated
        
        # Validate educational engagement elements
        assert len(generated["introduction"]) >= 100  # Engaging introduction
        assert len(generated["main_content"]) >= 800  # Substantial content
        assert generated["estimated_duration_minutes"] > 0
    
    @pytest.mark.asyncio
    async def test_study_guide_generation(
        self, client, auth_headers, sample_learning_objectives, sample_cognitive_load
    ):
        """Test study guide generation with learning science principles"""
        request_data = {
            "content_type": "study_guide",
            "topic": "World War II History",
            "age_group": "high_school",
            "learning_objectives": sample_learning_objectives,
            "cognitive_load_target": sample_cognitive_load,
            "additional_requirements": "Include timeline and key figures"
        }
        
        response = client.post(
            "/api/content/generate/study_guide",
            json=request_data,
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        content = response.json()
        
        # Validate study guide structure
        generated = content["generated_content"]
        assert "title" in generated
        assert "introduction" in generated
        assert "key_concepts" in generated
        assert "study_sections" in generated
        assert "summary" in generated
        assert "review_questions" in generated
        
        # Validate educational effectiveness
        assert isinstance(generated["key_concepts"], list)
        assert len(generated["key_concepts"]) >= 3
        assert isinstance(generated["study_sections"], list)
        assert len(generated["study_sections"]) >= 2
    
    @pytest.mark.asyncio
    async def test_flashcards_generation(
        self, client, auth_headers, sample_learning_objectives, sample_cognitive_load
    ):
        """Test flashcards generation with memory techniques"""
        request_data = {
            "content_type": "flashcards",
            "topic": "Spanish Vocabulary - Food",
            "age_group": "middle_school",
            "learning_objectives": sample_learning_objectives,
            "cognitive_load_target": sample_cognitive_load
        }
        
        response = client.post(
            "/api/content/generate/flashcards",
            json=request_data,
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        content = response.json()
        
        # Validate flashcards structure
        generated = content["generated_content"]
        assert "title" in generated
        assert "description" in generated
        assert "flashcards" in generated
        
        # Validate flashcard content
        flashcards = generated["flashcards"]
        assert isinstance(flashcards, list)
        assert len(flashcards) >= 10  # Minimum viable set
        
        for card in flashcards:
            assert "front" in card
            assert "back" in card
            assert len(card["front"]) >= 3
            assert len(card["back"]) >= 5
    
    @pytest.mark.parametrize("content_type", [
        "one_pager_summary",
        "detailed_reading_material", 
        "faq_collection",
        "reading_guide_questions"
    ])
    @pytest.mark.asyncio
    async def test_all_content_types_generation(
        self, client, auth_headers, sample_learning_objectives, 
        sample_cognitive_load, content_type
    ):
        """Test generation for all remaining content types"""
        request_data = {
            "content_type": content_type,
            "topic": "Photosynthesis in Plants",
            "age_group": "high_school",
            "learning_objectives": sample_learning_objectives,
            "cognitive_load_target": sample_cognitive_load
        }
        
        response = client.post(
            f"/api/content/generate/{content_type}",
            json=request_data,
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        content = response.json()
        
        # Basic validation for all content types
        assert "id" in content
        assert content["content_type"] == content_type
        assert "generated_content" in content
        assert "quality_score" in content
        assert content["quality_score"] >= 0.7
```

### Educational Quality Assessment Tests
```python
# tests/test_educational_quality.py
import pytest
from src.services.educational_quality import EducationalQualityAssessor
from src.models.educational import CognitiveLoadMetrics, LearningObjective

class TestEducationalQuality:
    """Test educational content quality assessment"""
    
    @pytest.fixture
    def quality_assessor(self):
        return EducationalQualityAssessor()
    
    @pytest.mark.asyncio
    async def test_cognitive_load_assessment(self, quality_assessor):
        """Test cognitive load calculation"""
        content = {
            "title": "Complex Mathematical Concepts",
            "content": "This is a detailed explanation of calculus derivatives..."
        }
        
        cognitive_load = await quality_assessor.assess_cognitive_load(
            content, age_group="high_school"
        )
        
        assert isinstance(cognitive_load, CognitiveLoadMetrics)
        assert 0 <= cognitive_load.intrinsic_load <= 1
        assert 0 <= cognitive_load.extraneous_load <= 1
        assert 0 <= cognitive_load.germane_load <= 1
        assert cognitive_load.total_cognitive_load > 0
    
    @pytest.mark.asyncio
    async def test_learning_objective_alignment(self, quality_assessor):
        """Test learning objective alignment assessment"""
        learning_objectives = [
            LearningObjective(
                cognitive_level="understand",
                subject_area="Mathematics",
                specific_skill="Solve equations",
                measurable_outcome="80% accuracy",
                difficulty_level=5
            )
        ]
        
        content = {
            "title": "Solving Linear Equations",
            "content": "Learn to solve equations step by step..."
        }
        
        alignment_score = await quality_assessor.assess_objective_alignment(
            content, learning_objectives
        )
        
        assert 0 <= alignment_score <= 1
        assert alignment_score > 0.5  # Should have reasonable alignment
    
    @pytest.mark.asyncio
    async def test_age_appropriateness(self, quality_assessor):
        """Test age-appropriate language assessment"""
        content_elementary = {
            "content": "Animals need food to grow big and strong."
        }
        
        content_college = {
            "content": "The metabolic processes in organisms require complex biochemical reactions."
        }
        
        score_elementary = await quality_assessor.assess_age_appropriateness(
            content_elementary, "elementary"
        )
        score_college = await quality_assessor.assess_age_appropriateness(
            content_college, "college"
        )
        
        assert score_elementary > 0.8  # Should be appropriate
        assert score_college > 0.8     # Should be appropriate
        
        # Cross-check: elementary content with college level
        cross_score = await quality_assessor.assess_age_appropriateness(
            content_elementary, "college"
        )
        assert cross_score < score_elementary  # Should be less appropriate
    
    @pytest.mark.asyncio
    async def test_engagement_elements(self, quality_assessor):
        """Test engagement element detection"""
        engaging_content = {
            "content": "Imagine you're a detective solving a mystery! What clues can you find?"
        }
        
        boring_content = {
            "content": "This is a list of facts about the topic."
        }
        
        engaging_score = await quality_assessor.assess_engagement(engaging_content)
        boring_score = await quality_assessor.assess_engagement(boring_content)
        
        assert engaging_score > boring_score
        assert engaging_score > 0.6
```

### Prompt Template Integration Tests
```python
# tests/test_prompt_integration.py
import pytest
from src.services.content_generation import EducationalContentService
from pathlib import Path

class TestPromptTemplateIntegration:
    """Test integration with actual prompt templates from la-factoria/prompts/"""
    
    @pytest.fixture
    def content_service(self):
        return EducationalContentService()
    
    def test_prompt_template_loading(self, content_service):
        """Test that all 8 prompt templates load correctly"""
        expected_templates = [
            "master_content_outline",
            "podcast_script", 
            "study_guide",
            "one_pager_summary",
            "detailed_reading_material",
            "faq_collection",
            "flashcards",
            "reading_guide_questions"
        ]
        
        for template_name in expected_templates:
            prompt = content_service.get_prompt_template(template_name)
            assert prompt is not None
            assert len(prompt) > 100  # Should have substantial content
            assert "You are an expert" in prompt  # Standard opening
    
    def test_prompt_variable_replacement(self, content_service):
        """Test prompt template variable replacement"""
        template = content_service.get_prompt_template("study_guide")
        
        variables = {
            "topic": "Test Topic",
            "age_group": "high_school",
            "learning_objectives": ["Objective 1", "Objective 2"]
        }
        
        compiled_prompt = content_service.compile_prompt(template, variables)
        
        assert "Test Topic" in compiled_prompt
        assert "high_school" in compiled_prompt
        assert "Objective 1" in compiled_prompt
    
    @pytest.mark.asyncio
    async def test_langfuse_integration(self, content_service):
        """Test Langfuse prompt management integration"""
        # This test requires Langfuse setup
        if not content_service.langfuse_enabled:
            pytest.skip("Langfuse not configured")
        
        prompt_name = "study_guide"
        langfuse_prompt = await content_service.get_langfuse_prompt(prompt_name)
        
        assert langfuse_prompt is not None
        assert "prompt" in langfuse_prompt
        assert "variables" in langfuse_prompt
```

### Performance and Load Tests
```python
# tests/test_performance.py
import pytest
import asyncio
import time
from concurrent.futures import ThreadPoolExecutor

class TestPerformance:
    """Test performance characteristics of educational content generation"""
    
    @pytest.mark.asyncio
    async def test_generation_time_limits(self, client, auth_headers):
        """Test that content generation completes within time limits"""
        request_data = {
            "content_type": "study_guide",
            "topic": "Performance Test Topic",
            "age_group": "high_school"
        }
        
        start_time = time.time()
        
        response = client.post(
            "/api/content/generate/study_guide",
            json=request_data,
            headers=auth_headers
        )
        
        end_time = time.time()
        generation_time = end_time - start_time
        
        assert response.status_code == 200
        assert generation_time < 180  # 3 minutes max
        
        # Check if generation time is recorded
        content = response.json()
        assert "generation_duration_ms" in content["metadata"]
    
    @pytest.mark.asyncio
    async def test_concurrent_generation(self, client, auth_headers):
        """Test concurrent content generation handling"""
        async def generate_content(content_type, topic_suffix):
            request_data = {
                "content_type": content_type,
                "topic": f"Concurrent Test {topic_suffix}",
                "age_group": "high_school"
            }
            
            response = client.post(
                f"/api/content/generate/{content_type}",
                json=request_data,
                headers=auth_headers
            )
            return response.status_code
        
        # Generate 5 pieces of content concurrently
        tasks = [
            generate_content("flashcards", i) 
            for i in range(5)
        ]
        
        results = await asyncio.gather(*tasks)
        
        # All should succeed
        assert all(status == 200 for status in results)
    
    @pytest.mark.asyncio
    async def test_memory_usage_stability(self, client, auth_headers):
        """Test that memory usage remains stable during generation"""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss
        
        # Generate 10 pieces of content
        for i in range(10):
            request_data = {
                "content_type": "one_pager_summary",
                "topic": f"Memory Test {i}",
                "age_group": "general"
            }
            
            response = client.post(
                "/api/content/generate/one_pager_summary",
                json=request_data,
                headers=auth_headers
            )
            assert response.status_code == 200
        
        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory
        
        # Memory increase should be reasonable (less than 100MB)
        assert memory_increase < 100 * 1024 * 1024
```

### Test Data Factories
```python
# tests/factories.py
import factory
from factory import SubFactory
from src.models.educational import EducationalContent, User, LearningObjective

class UserFactory(factory.Factory):
    class Meta:
        model = User
    
    username = factory.Sequence(lambda n: f"testuser{n}")
    email = factory.LazyAttribute(lambda obj: f"{obj.username}@example.com")
    is_active = True
    learning_preferences = factory.Dict({
        "preferred_learning_style": "visual",
        "difficulty_preference": "medium"
    })

class LearningObjectiveFactory(factory.Factory):
    class Meta:
        model = LearningObjective
    
    cognitive_level = factory.Iterator([
        "remember", "understand", "apply", "analyze", "evaluate", "create"
    ])
    subject_area = factory.Iterator([
        "Mathematics", "Science", "History", "Literature", "Art"
    ])
    specific_skill = factory.Faker("sentence", nb_words=4)
    measurable_outcome = factory.Faker("sentence", nb_words=6)
    difficulty_level = factory.Faker("random_int", min=1, max=10)

class EducationalContentFactory(factory.Factory):
    class Meta:
        model = EducationalContent
    
    user = SubFactory(UserFactory)
    content_type = factory.Iterator([
        "master_content_outline", "podcast_script", "study_guide",
        "one_pager_summary", "detailed_reading_material", "faq_collection",
        "flashcards", "reading_guide_questions"
    ])
    topic = factory.Faker("sentence", nb_words=5)
    age_group = factory.Iterator(["elementary", "middle_school", "high_school", "college"])
    learning_objectives = factory.Dict({
        "objectives": factory.List([
            factory.SubFactory(LearningObjectiveFactory) for _ in range(3)
        ])
    })
    cognitive_load_metrics = factory.Dict({
        "intrinsic_load": factory.Faker("pyfloat", min_value=0, max_value=1),
        "extraneous_load": factory.Faker("pyfloat", min_value=0, max_value=1),
        "germane_load": factory.Faker("pyfloat", min_value=0, max_value=1)
    })
    generated_content = factory.Dict({
        "title": factory.Faker("sentence", nb_words=4),
        "content": factory.Faker("text", max_nb_chars=2000)
    })
    quality_score = factory.Faker("pyfloat", min_value=0.5, max_value=1.0)
```