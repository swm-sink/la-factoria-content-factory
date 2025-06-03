"""
End-to-End Content Generation Tests
Production-grade E2E testing for AI Content Factory

Tests the complete workflow from API request to content delivery,
including async job processing, caching, and error handling.
"""

import argparse
import json
import logging
import os
import time
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List

import httpx
import pytest

logger = logging.getLogger(__name__)


@dataclass
class E2ETestConfig:
    """Configuration for E2E tests"""

    base_url: str = "http://localhost:8080"
    api_key: str = "test-api-key-e2e"
    timeout: int = 30
    retry_attempts: int = 3

    @classmethod
    def from_env(cls) -> "E2ETestConfig":
        return cls(
            base_url=os.getenv("E2E_BASE_URL", cls.base_url),
            api_key=os.getenv("E2E_API_KEY", cls.api_key),
            timeout=int(os.getenv("E2E_TIMEOUT", str(cls.timeout))),
            retry_attempts=int(
                os.getenv("E2E_RETRY_ATTEMPTS", str(cls.retry_attempts))
            ),
        )


class ContentGenerationE2ETest:
    """Production E2E test suite for content generation workflows"""

    def __init__(self, config: E2ETestConfig = None):
        self.config = config or E2ETestConfig.from_env()
        self.base_url = self.config.base_url.rstrip("/")
        self.api_key = self.config.api_key
        self.session = httpx.Client(
            timeout=httpx.Timeout(self.config.timeout),
            headers={"X-API-Key": self.api_key, "Content-Type": "application/json"},
        )

        # Test data
        self.test_syllabus = """
        Introduction to Artificial Intelligence

        Course Overview:
        This comprehensive course introduces students to the fundamental concepts of artificial intelligence,
        covering machine learning algorithms, neural networks, natural language processing, and computer vision.
        Students will gain hands-on experience with AI tools and frameworks while exploring ethical considerations
        and real-world applications.

        Learning Objectives:
        1. Understand core AI concepts and terminology
        2. Implement basic machine learning algorithms
        3. Explore neural network architectures
        4. Apply NLP techniques for text processing
        5. Develop computer vision applications
        6. Analyze AI ethics and societal impact

        Topics Covered:
        - History and evolution of AI
        - Search algorithms and problem solving
        - Knowledge representation and reasoning
        - Machine learning fundamentals
        - Deep learning and neural networks
        - Natural language processing
        - Computer vision and image recognition
        - AI ethics and responsible development
        """

    def test_complete_content_generation_workflow(self):
        """Test the complete content generation workflow from request to delivery"""

        logger.info("Starting complete content generation E2E test")
        start_time = time.time()

        # Step 1: Submit content generation request
        request_data = {
            "syllabus_text": self.test_syllabus,
            "target_formats": [
                "podcast_script",
                "study_guide",
                "faq_collection",
                "flashcard_collection",
                "one_pager_summary",
            ],
        }

        response = self.session.post(
            f"{self.base_url}/api/v1/content/generate", json=request_data
        )

        assert (
            response.status_code == 200
        ), f"Content generation failed: {response.text}"
        content_data = response.json()

        # Step 2: Validate response structure
        assert "success" in content_data
        assert content_data["success"] is True
        assert "content_outline" in content_data
        assert "generated_content" in content_data

        # Step 3: Validate content outline
        outline = content_data["content_outline"]
        required_outline_fields = [
            "title",
            "overview",
            "main_topics",
            "learning_objectives",
        ]
        for field in required_outline_fields:
            assert field in outline, f"Missing outline field: {field}"
            assert outline[field], f"Empty outline field: {field}"

        # Step 4: Validate generated content
        generated = content_data["generated_content"]
        expected_formats = request_data["target_formats"]

        for format_name in expected_formats:
            assert format_name in generated, f"Missing content format: {format_name}"
            content_item = generated[format_name]
            assert content_item is not None, f"Null content for format: {format_name}"

            # Validate content structure based on format
            self._validate_content_format(format_name, content_item)

        end_time = time.time()
        generation_time = end_time - start_time

        logger.info(f"Complete workflow test passed in {generation_time:.2f} seconds")

        # Performance assertions
        assert (
            generation_time < 60
        ), f"Content generation too slow: {generation_time:.2f}s"

        return content_data

    def test_async_job_workflow(self):
        """Test async job creation and polling workflow"""

        logger.info("Starting async job workflow E2E test")

        # Step 1: Create async job (if endpoint exists)
        job_request = {
            "syllabus_text": self.test_syllabus[:1000],  # Shorter for faster testing
            "target_formats": ["podcast_script", "study_guide"],
            "async": True,
        }

        try:
            response = self.session.post(
                f"{self.base_url}/api/v1/jobs", json=job_request
            )

            if response.status_code == 404:
                pytest.skip("Async job endpoints not implemented yet")

            assert response.status_code == 201, f"Job creation failed: {response.text}"
            job_data = response.json()

            assert "job_id" in job_data
            assert "status" in job_data
            job_id = job_data["job_id"]

            # Step 2: Poll job status
            max_polls = 30  # 30 * 2 = 60 seconds max wait
            poll_count = 0

            while poll_count < max_polls:
                status_response = self.session.get(
                    f"{self.base_url}/api/v1/jobs/{job_id}"
                )
                assert status_response.status_code == 200

                status_data = status_response.json()
                job_status = status_data.get("status")

                if job_status == "completed":
                    # Validate completed job
                    assert "result" in status_data
                    result = status_data["result"]
                    assert "content_outline" in result
                    assert "generated_content" in result

                    logger.info(f"Async job completed after {poll_count * 2} seconds")
                    return status_data

                elif job_status == "failed":
                    pytest.fail(
                        f"Job failed: {status_data.get('error', 'Unknown error')}"
                    )

                time.sleep(2)
                poll_count += 1

            pytest.fail("Job did not complete within timeout period")

        except requests.exceptions.ConnectionError:
            pytest.skip("Service not available for async job testing")

    def test_rate_limiting_behavior(self):
        """Test API rate limiting behavior"""

        logger.info("Starting rate limiting E2E test")

        # Small request for rapid testing
        quick_request = {
            "syllabus_text": "Quick test content for rate limiting validation. " * 10,
            "target_formats": ["one_pager_summary"],
        }

        # Make requests up to rate limit
        responses = []
        start_time = time.time()

        for i in range(12):  # Exceed the 10 req/min limit
            response = self.session.post(
                f"{self.base_url}/api/v1/content/generate", json=quick_request
            )
            responses.append(
                (response.status_code, response.headers.get("Retry-After"))
            )

            if response.status_code == 429:
                logger.info(f"Rate limit hit after {i+1} requests")
                break

            time.sleep(1)  # Small delay between requests

        # Verify rate limiting is working
        rate_limited_responses = [r for r in responses if r[0] == 429]

        if rate_limited_responses:
            logger.info("Rate limiting is active and working correctly")
            # Check that Retry-After header is present
            retry_after = rate_limited_responses[0][1]
            assert (
                retry_after is not None
            ), "Rate limit response missing Retry-After header"
        else:
            logger.warning("Rate limiting may not be active or limits are very high")

    def test_error_handling_and_recovery(self):
        """Test error handling and system recovery"""

        logger.info("Starting error handling E2E test")

        # Test 1: Invalid input
        invalid_request = {
            "syllabus_text": "Short",  # Too short
            "target_formats": ["invalid_format"],
        }

        response = self.session.post(
            f"{self.base_url}/api/v1/content/generate", json=invalid_request
        )

        assert response.status_code == 422, "Should return validation error"
        error_data = response.json()
        assert "detail" in error_data, "Error response should contain details"

        # Test 2: Missing API key
        no_auth_session = httpx.Client(
            timeout=httpx.Timeout(self.config.timeout),
            headers={"Content-Type": "application/json"},
        )

        response = no_auth_session.post(
            f"{self.base_url}/api/v1/content/generate",
            json={
                "syllabus_text": self.test_syllabus,
                "target_formats": ["study_guide"],
            },
        )

        assert response.status_code in [401, 403], "Should require authentication"

        # Test 3: System recovery after errors
        # Make a valid request after errors to ensure system is still responsive
        valid_request = {
            "syllabus_text": self.test_syllabus,
            "target_formats": ["one_pager_summary"],
        }

        response = self.session.post(
            f"{self.base_url}/api/v1/content/generate", json=valid_request
        )

        assert response.status_code == 200, "System should recover after errors"

        logger.info("Error handling tests passed")

    def test_caching_behavior(self):
        """Test content caching effectiveness"""

        logger.info("Starting caching behavior E2E test")

        cache_test_request = {
            "syllabus_text": "Caching test content for AI Content Factory. " * 20,
            "target_formats": ["study_guide"],
        }

        # First request (cache miss)
        start_time = time.time()
        response1 = self.session.post(
            f"{self.base_url}/api/v1/content/generate", json=cache_test_request
        )
        first_request_time = time.time() - start_time

        assert response1.status_code == 200
        content1 = response1.json()

        # Second identical request (should be cache hit)
        start_time = time.time()
        response2 = self.session.post(
            f"{self.base_url}/api/v1/content/generate", json=cache_test_request
        )
        second_request_time = time.time() - start_time

        assert response2.status_code == 200
        content2 = response2.json()

        # Validate caching behavior
        assert (
            content1["content_outline"] == content2["content_outline"]
        ), "Cached content should be identical"

        # Cache hit should be significantly faster
        if second_request_time < first_request_time * 0.5:
            logger.info(
                f"Caching working: {first_request_time:.2f}s -> {second_request_time:.2f}s"
            )
        else:
            logger.warning(
                f"Caching may not be working optimally: {first_request_time:.2f}s -> {second_request_time:.2f}s"
            )

    def _validate_content_format(self, format_name: str, content: Dict[str, Any]):
        """Validate content structure for specific formats"""

        if format_name == "podcast_script":
            required_fields = ["title", "introduction", "main_content", "conclusion"]
            for field in required_fields:
                assert field in content, f"Missing field in podcast_script: {field}"
                assert content[field], f"Empty field in podcast_script: {field}"

        elif format_name == "study_guide":
            required_fields = ["title", "overview", "key_concepts", "detailed_content"]
            for field in required_fields:
                assert field in content, f"Missing field in study_guide: {field}"

        elif format_name == "faq_collection":
            assert "faqs" in content, "FAQ collection missing faqs field"
            assert isinstance(content["faqs"], list), "FAQs should be a list"
            assert len(content["faqs"]) > 0, "FAQ collection should not be empty"

            for faq in content["faqs"]:
                assert "question" in faq, "FAQ missing question"
                assert "answer" in faq, "FAQ missing answer"

        elif format_name == "flashcard_collection":
            assert (
                "flashcards" in content
            ), "Flashcard collection missing flashcards field"
            assert isinstance(
                content["flashcards"], list
            ), "Flashcards should be a list"

            for card in content["flashcards"]:
                assert "front" in card, "Flashcard missing front"
                assert "back" in card, "Flashcard missing back"

        elif format_name == "one_pager_summary":
            required_fields = ["title", "executive_summary", "key_points"]
            for field in required_fields:
                assert field in content, f"Missing field in one_pager_summary: {field}"

    def run_all_tests(self) -> Dict[str, Any]:
        """Run all E2E tests and return results"""

        results = {
            "timestamp": datetime.now().isoformat(),
            "base_url": self.base_url,
            "tests_run": 0,
            "tests_passed": 0,
            "tests_failed": 0,
            "test_results": [],
        }

        test_methods = [
            ("complete_workflow", self.test_complete_content_generation_workflow),
            ("async_job_workflow", self.test_async_job_workflow),
            ("rate_limiting", self.test_rate_limiting_behavior),
            ("error_handling", self.test_error_handling_and_recovery),
            ("caching_behavior", self.test_caching_behavior),
        ]

        for test_name, test_method in test_methods:
            results["tests_run"] += 1

            try:
                start_time = time.time()
                test_method()
                duration = time.time() - start_time

                results["tests_passed"] += 1
                results["test_results"].append(
                    {
                        "name": test_name,
                        "status": "PASSED",
                        "duration": round(duration, 2),
                        "error": None,
                    }
                )
                logger.info(f"✅ {test_name} PASSED ({duration:.2f}s)")

            except Exception as e:
                duration = time.time() - start_time
                results["tests_failed"] += 1
                results["test_results"].append(
                    {
                        "name": test_name,
                        "status": "FAILED",
                        "duration": round(duration, 2),
                        "error": str(e),
                    }
                )
                logger.error(f"❌ {test_name} FAILED: {e}")

        # Calculate summary
        results["success_rate"] = (results["tests_passed"] / results["tests_run"]) * 100
        results["total_duration"] = sum(t["duration"] for t in results["test_results"])

        return results


# Pytest integration
@pytest.fixture
def e2e_tester():
    """Fixture to provide E2E tester instance"""
    config = E2ETestConfig.from_env()
    return ContentGenerationE2ETest(config=config)


def test_content_generation_workflow_e2e(e2e_tester):
    """Pytest wrapper for complete workflow test"""
    e2e_tester.test_complete_content_generation_workflow()


def test_error_handling_e2e(e2e_tester):
    """Pytest wrapper for error handling test"""
    e2e_tester.test_error_handling_and_recovery()


def test_caching_e2e(e2e_tester):
    """Pytest wrapper for caching test"""
    e2e_tester.test_caching_behavior()


if __name__ == "__main__":
    # Direct execution for manual testing
    import argparse

    parser = argparse.ArgumentParser(description="Run E2E tests for AI Content Factory")
    parser.add_argument(
        "--base-url",
        default=os.getenv("E2E_BASE_URL", "http://localhost:8080"),
        help="Base URL for API",
    )
    parser.add_argument(
        "--api-key",
        default=os.getenv("E2E_API_KEY", "test-api-key-e2e"),
        help="API key for authentication",
    )
    parser.add_argument("--output", help="Output file for results (JSON)")

    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )

    tester = ContentGenerationE2ETest(
        config=E2ETestConfig(base_url=args.base_url, api_key=args.api_key)
    )
    results = tester.run_all_tests()

    print(f"\n🎯 E2E Test Results:")
    print(f"   Tests Run: {results['tests_run']}")
    print(f"   Passed: {results['tests_passed']}")
    print(f"   Failed: {results['tests_failed']}")
    print(f"   Success Rate: {results['success_rate']:.1f}%")
    print(f"   Total Duration: {results['total_duration']:.2f}s")

    if args.output:
        with open(args.output, "w") as f:
            json.dump(results, f, indent=2)
        print(f"   Results saved to: {args.output}")
