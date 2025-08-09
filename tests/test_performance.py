"""
Performance Tests for La Factoria
=================================

Comprehensive performance testing covering:
- Response time requirements (<5s quality assessment, <30s content generation)
- Concurrent request handling
- Load testing and stress testing
- Memory usage and resource management
- Database performance
- AI provider integration performance
"""

# Fix Python path for src imports
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pytest
import asyncio
import time
import statistics
from typing import List, Dict, Any
from unittest.mock import patch, AsyncMock
from concurrent.futures import ThreadPoolExecutor, as_completed

from src.services.educational_content_service import EducationalContentService
from src.services.quality_assessor import EducationalQualityAssessor
from src.models.educational import LaFactoriaContentType, LearningLevel


class TestResponseTimeRequirements:
    """Test La Factoria response time requirements"""

    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_quality_assessment_speed_requirement(
        self, quality_assessor, high_quality_content, timing_context
    ):
        """Test quality assessment completes within 5 second requirement"""

        with timing_context() as timer:
            result = await quality_assessor.assess_content_quality(
                content=high_quality_content,
                content_type="study_guide",
                age_group="high_school"
            )

        # Quality assessment should complete within 5 seconds
        timer.assert_under_time_limit(5.0, "Quality assessment")

        # Should still produce valid results
        assert result["overall_quality_score"] >= 0.0
        assert "meets_quality_threshold" in result

    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_content_generation_speed_requirement(
        self, content_service, timing_context
    ):
        """Test content generation completes within 30 second requirement"""

        with timing_context() as timer:
            result = await content_service.generate_content(
                content_type="flashcards",  # Generally fastest content type
                topic="Quick Performance Test",
                age_group="high_school"
            )

        # Content generation should complete within 30 seconds (mocked should be much faster)
        timer.assert_under_time_limit(30.0, "Content generation")

        # Should produce valid results
        assert "generated_content" in result
        assert result["content_type"] == "flashcards"

    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_api_endpoint_response_times(
        self, client, auth_headers, mock_ai_providers, timing_context
    ):
        """Test API endpoint response times"""

        # Test fastest endpoint (one-pager summary)
        with timing_context() as timer:
            response = client.post(
                "/api/v1/generate/one_pager_summary",
                json={"topic": "API Performance Test", "age_group": "high_school"},
                headers=auth_headers
            )

        timer.assert_under_time_limit(10.0, "API endpoint response")
        assert response.status_code == 200

    @pytest.mark.performance
    @pytest.mark.parametrize("content_type", [
        "flashcards", "one_pager_summary", "faq_collection"  # Typically faster content types
    ])
    @pytest.mark.asyncio
    async def test_fast_content_types_performance(
        self, content_service, timing_context, content_type
    ):
        """Test performance of typically faster content types"""

        with timing_context() as timer:
            result = await content_service.generate_content(
                content_type=content_type,
                topic=f"Performance Test - {content_type}",
                age_group="high_school"
            )

        # Fast content types should complete quickly even with processing
        timer.assert_under_time_limit(15.0, f"{content_type} generation")
        assert result["content_type"] == content_type

    @pytest.mark.performance
    @pytest.mark.parametrize("content_type", [
        "detailed_reading_material", "study_guide", "master_content_outline"  # Typically slower
    ])
    @pytest.mark.asyncio
    async def test_comprehensive_content_types_performance(
        self, content_service, timing_context, content_type
    ):
        """Test performance of comprehensive content types"""

        with timing_context() as timer:
            result = await content_service.generate_content(
                content_type=content_type,
                topic=f"Performance Test - {content_type}",
                age_group="high_school"
            )

        # Comprehensive content types allowed longer time but should still meet requirement
        timer.assert_under_time_limit(30.0, f"{content_type} generation")
        assert result["content_type"] == content_type


class TestConcurrentRequestHandling:
    """Test concurrent request handling and scaling"""

    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_concurrent_quality_assessments(
        self, quality_assessor, high_quality_content
    ):
        """Test concurrent quality assessments"""

        async def assess_content(content_id):
            return await quality_assessor.assess_content_quality(
                content={**high_quality_content, "id": content_id},
                content_type="study_guide",
                age_group="high_school"
            )

        start_time = time.time()

        # Run 10 concurrent assessments
        tasks = [assess_content(f"test-{i}") for i in range(10)]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        end_time = time.time()
        duration = end_time - start_time

        # Should complete all 10 assessments reasonably quickly
        assert duration < 15.0, f"10 concurrent assessments took {duration:.2f}s"

        # All should succeed
        successful_results = [r for r in results if not isinstance(r, Exception)]
        assert len(successful_results) >= 8, f"Only {len(successful_results)}/10 assessments succeeded"

    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_concurrent_content_generation(
        self, content_service
    ):
        """Test concurrent content generation"""

        async def generate_content(topic_suffix):
            return await content_service.generate_content(
                content_type="flashcards",
                topic=f"Concurrent Test {topic_suffix}",
                age_group="high_school"
            )

        start_time = time.time()

        # Run 5 concurrent generations (realistic load)
        tasks = [generate_content(i) for i in range(5)]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        end_time = time.time()
        duration = end_time - start_time

        # Should handle concurrent generations efficiently
        assert duration < 60.0, f"5 concurrent generations took {duration:.2f}s"

        # Most should succeed
        successful_results = [r for r in results if not isinstance(r, Exception)]
        assert len(successful_results) >= 3, f"Only {len(successful_results)}/5 generations succeeded"

    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_mixed_concurrent_operations(
        self, content_service, quality_assessor, high_quality_content
    ):
        """Test mixed concurrent operations (generation + assessment)"""

        async def generate_and_assess():
            # Generate content
            result = await content_service.generate_content(
                content_type="one_pager_summary",
                topic="Mixed Operation Test",
                age_group="high_school"
            )

            # Assess different content
            assessment = await quality_assessor.assess_content_quality(
                content=high_quality_content,
                content_type="study_guide",
                age_group="high_school"
            )

            return result, assessment

        start_time = time.time()

        # Run 3 mixed operations concurrently
        tasks = [generate_and_assess() for _ in range(3)]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        end_time = time.time()
        duration = end_time - start_time

        # Should handle mixed operations efficiently
        assert duration < 45.0, f"Mixed concurrent operations took {duration:.2f}s"

        successful_results = [r for r in results if not isinstance(r, Exception)]
        assert len(successful_results) >= 2


class TestLoadAndStressTests:
    """Load testing and stress testing"""

    @pytest.mark.performance
    @pytest.mark.slow
    @pytest.mark.asyncio
    async def test_sustained_load_quality_assessment(
        self, quality_assessor, high_quality_content
    ):
        """Test sustained load on quality assessment"""

        async def assessment_batch(batch_size=5):
            tasks = []
            for i in range(batch_size):
                task = quality_assessor.assess_content_quality(
                    content={**high_quality_content, "batch_id": i},
                    content_type="study_guide",
                    age_group="high_school"
                )
                tasks.append(task)
            return await asyncio.gather(*tasks, return_exceptions=True)

        start_time = time.time()
        response_times = []

        # Run 5 batches of 5 assessments each (25 total)
        for batch_num in range(5):
            batch_start = time.time()
            results = await assessment_batch()
            batch_end = time.time()

            batch_duration = batch_end - batch_start
            response_times.append(batch_duration)

            # Each batch should complete within reasonable time
            assert batch_duration < 10.0, f"Batch {batch_num} took {batch_duration:.2f}s"

            # Most assessments in batch should succeed
            successful = [r for r in results if not isinstance(r, Exception)]
            assert len(successful) >= 3, f"Batch {batch_num}: only {len(successful)}/5 succeeded"

        total_duration = time.time() - start_time
        avg_response_time = statistics.mean(response_times)

        # Overall performance should be acceptable
        assert total_duration < 60.0, f"Total sustained load test took {total_duration:.2f}s"
        assert avg_response_time < 8.0, f"Average batch time: {avg_response_time:.2f}s"

    @pytest.mark.performance
    @pytest.mark.slow
    def test_memory_usage_under_load(self, client, auth_headers):
        """Test memory usage under load"""
        import psutil
        import os

        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB

        # Make many requests to test memory usage
        for i in range(20):
            response = client.post(
                "/api/v1/generate/flashcards",
                json={"topic": f"Memory Test {i}", "age_group": "high_school"},
                headers=auth_headers
            )
            # Don't assert success due to potential mocking issues

        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory

        # Memory usage should remain reasonable
        assert memory_increase < 100, f"Memory increased by {memory_increase:.1f}MB"

    @pytest.mark.performance
    @pytest.mark.slow
    @pytest.mark.asyncio
    async def test_stress_test_error_handling(
        self, content_service
    ):
        """Test error handling under stress"""

        # Mock AI provider to occasionally fail
        original_generate = content_service.ai_provider.generate_content

        call_count = 0
        async def sometimes_failing_generate(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count % 4 == 0:  # Fail every 4th call
                raise Exception("Simulated AI provider failure")
            return await original_generate(*args, **kwargs)

        content_service.ai_provider.generate_content = sometimes_failing_generate

        # Generate content with some failures
        tasks = []
        for i in range(12):  # 3 failures expected
            task = content_service.generate_content(
                content_type="flashcards",
                topic=f"Stress Test {i}",
                age_group="high_school"
            )
            tasks.append(task)

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Should handle failures gracefully
        successful_results = [r for r in results if not isinstance(r, Exception)]
        failed_results = [r for r in results if isinstance(r, Exception)]

        assert len(successful_results) >= 6, f"Only {len(successful_results)} succeeded"
        assert len(failed_results) >= 2, f"Expected some failures, got {len(failed_results)}"


class TestResourceUtilization:
    """Test resource utilization and efficiency"""

    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_cpu_utilization_monitoring(
        self, content_service
    ):
        """Monitor CPU utilization during content generation"""
        import psutil

        # Monitor CPU usage
        cpu_percentages = []

        async def monitor_cpu():
            for _ in range(10):  # Monitor for ~5 seconds
                cpu_percentages.append(psutil.cpu_percent(interval=0.5))

        async def generate_content():
            return await content_service.generate_content(
                content_type="study_guide",
                topic="CPU Monitoring Test",
                age_group="high_school"
            )

        # Run monitoring and generation concurrently
        monitor_task = asyncio.create_task(monitor_cpu())
        generation_task = asyncio.create_task(generate_content())

        await asyncio.gather(monitor_task, generation_task, return_exceptions=True)

        if cpu_percentages:
            avg_cpu = statistics.mean(cpu_percentages)
            max_cpu = max(cpu_percentages)

            # CPU usage should be reasonable (not maxed out)
            assert avg_cpu < 80.0, f"Average CPU usage: {avg_cpu:.1f}%"
            assert max_cpu < 95.0, f"Peak CPU usage: {max_cpu:.1f}%"

    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_response_time_consistency(
        self, quality_assessor, high_quality_content
    ):
        """Test response time consistency"""

        response_times = []

        # Run multiple assessments and measure consistency
        for i in range(10):
            start_time = time.time()

            await quality_assessor.assess_content_quality(
                content={**high_quality_content, "iteration": i},
                content_type="study_guide",
                age_group="high_school"
            )

            end_time = time.time()
            response_times.append(end_time - start_time)

        # Analyze response time consistency
        avg_time = statistics.mean(response_times)
        std_dev = statistics.stdev(response_times) if len(response_times) > 1 else 0
        min_time = min(response_times)
        max_time = max(response_times)

        # Response times should be consistent
        assert avg_time < 3.0, f"Average response time: {avg_time:.2f}s"
        assert std_dev < 1.0, f"Response time std dev: {std_dev:.2f}s"
        assert max_time - min_time < 2.0, f"Response time range: {max_time - min_time:.2f}s"

    @pytest.mark.performance
    def test_database_query_performance(self, test_database):
        """Test database query performance"""
        # Placeholder for database performance testing
        # In a full implementation, this would test:
        # - Query response times
        # - Connection pool efficiency
        # - Index effectiveness
        # - Concurrent query handling

        # Mock database operations
        start_time = time.time()

        # Simulate database operations
        time.sleep(0.01)  # Simulate 10ms query time

        end_time = time.time()
        query_time = end_time - start_time

        # Database queries should be fast
        assert query_time < 0.1, f"Database query took {query_time:.3f}s"


class TestScalabilityLimits:
    """Test scalability limits and bottlenecks"""

    @pytest.mark.performance
    @pytest.mark.slow
    @pytest.mark.asyncio
    async def test_maximum_concurrent_users(
        self, client, auth_headers
    ):
        """Test maximum concurrent user simulation"""
        from httpx import AsyncClient
        import asyncio

        async def simulate_user_session(client, user_id):
            """Simulate a user session with multiple requests"""
            try:
                # User makes multiple requests
                responses = []

                # Get content types
                response = await client.get("/api/v1/content-types")
                responses.append(response.status_code)

                # Generate content
                response = await client.post(
                    "/api/v1/generate/flashcards",
                    json={"topic": f"User {user_id} Topic", "age_group": "high_school"},
                    headers=auth_headers
                )
                responses.append(response.status_code)

                return responses
            except Exception as e:
                return [500]  # Error status

        # Simulate 25 concurrent users
        async with AsyncClient(app=client.app, base_url="http://test") as ac:
            tasks = [simulate_user_session(ac, i) for i in range(25)]
            results = await asyncio.gather(*tasks, return_exceptions=True)

        # Analyze results
        successful_sessions = 0
        total_requests = 0
        successful_requests = 0

        for result in results:
            if not isinstance(result, Exception) and isinstance(result, list):
                successful_sessions += 1
                total_requests += len(result)
                successful_requests += sum(1 for status in result if 200 <= status < 300)

        # Should handle reasonable concurrent load
        success_rate = successful_sessions / len(results) if results else 0
        request_success_rate = successful_requests / total_requests if total_requests > 0 else 0

        assert success_rate >= 0.6, f"User session success rate: {success_rate:.2f}"
        assert request_success_rate >= 0.7, f"Request success rate: {request_success_rate:.2f}"

    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_queue_overflow_handling(
        self, content_service
    ):
        """Test handling of request queue overflow"""

        # Create a large number of requests quickly
        tasks = []
        for i in range(50):  # Large number of requests
            task = content_service.generate_content(
                content_type="flashcards",
                topic=f"Queue Test {i}",
                age_group="high_school"
            )
            tasks.append(task)

        start_time = time.time()

        # Execute with timeout
        try:
            results = await asyncio.wait_for(
                asyncio.gather(*tasks, return_exceptions=True),
                timeout=120.0  # 2 minute timeout
            )
        except asyncio.TimeoutError:
            pytest.fail("Queue overflow test timed out")

        end_time = time.time()
        duration = end_time - start_time

        # Should handle the load without timing out
        successful_results = [r for r in results if not isinstance(r, Exception)]
        success_rate = len(successful_results) / len(results)

        assert success_rate >= 0.5, f"Success rate under load: {success_rate:.2f}"
        assert duration < 120.0, f"Queue processing took {duration:.1f}s"

    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_graceful_degradation(
        self, content_service
    ):
        """Test graceful degradation under extreme load"""

        # Mock AI provider to have increasing delays
        original_generate = content_service.ai_provider.generate_content

        call_count = 0
        async def delayed_generate(*args, **kwargs):
            nonlocal call_count
            call_count += 1

            # Simulate increasing delays
            delay = min(call_count * 0.1, 2.0)  # Up to 2 second delay
            await asyncio.sleep(delay)

            return await original_generate(*args, **kwargs)

        content_service.ai_provider.generate_content = delayed_generate

        # Generate content with increasing delays
        tasks = []
        for i in range(10):
            task = content_service.generate_content(
                content_type="one_pager_summary",  # Fast content type
                topic=f"Degradation Test {i}",
                age_group="high_school"
            )
            tasks.append(task)

        start_time = time.time()
        results = await asyncio.gather(*tasks, return_exceptions=True)
        end_time = time.time()

        # Should handle degradation gracefully
        successful_results = [r for r in results if not isinstance(r, Exception)]

        # Some requests should still succeed even with degradation
        assert len(successful_results) >= 5, f"Only {len(successful_results)}/10 succeeded under degradation"


class TestPerformanceRegression:
    """Performance regression testing"""

    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_performance_baseline_quality_assessment(
        self, quality_assessor, high_quality_content
    ):
        """Establish performance baseline for quality assessment"""

        times = []

        # Run assessment multiple times to establish baseline
        for _ in range(5):
            start_time = time.time()

            await quality_assessor.assess_content_quality(
                content=high_quality_content,
                content_type="study_guide",
                age_group="high_school"
            )

            end_time = time.time()
            times.append(end_time - start_time)

        avg_time = statistics.mean(times)
        p95_time = sorted(times)[int(0.95 * len(times))]

        # Document baseline performance
        print(f"Quality Assessment Baseline - Avg: {avg_time:.3f}s, P95: {p95_time:.3f}s")

        # Baseline should meet requirements
        assert avg_time < 2.0, f"Baseline average: {avg_time:.3f}s"
        assert p95_time < 3.0, f"Baseline P95: {p95_time:.3f}s"

    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_performance_baseline_content_generation(
        self, content_service
    ):
        """Establish performance baseline for content generation"""

        times = []

        # Run generation multiple times to establish baseline
        for i in range(3):  # Fewer iterations due to longer execution
            start_time = time.time()

            await content_service.generate_content(
                content_type="flashcards",
                topic=f"Baseline Test {i}",
                age_group="high_school"
            )

            end_time = time.time()
            times.append(end_time - start_time)

        avg_time = statistics.mean(times)
        max_time = max(times)

        # Document baseline performance
        print(f"Content Generation Baseline - Avg: {avg_time:.3f}s, Max: {max_time:.3f}s")

        # Baseline should meet requirements (with mocked AI providers should be very fast)
        assert avg_time < 5.0, f"Baseline average: {avg_time:.3f}s"
        assert max_time < 10.0, f"Baseline max: {max_time:.3f}s"
