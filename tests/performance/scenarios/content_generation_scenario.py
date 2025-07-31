"""
Content generation-focused load test scenario.

Tests content generation endpoints under various load conditions including:
- Different content types and sizes
- Cache hit/miss patterns
- Concurrent generation requests
- Long-running generation tasks
"""

import random
import time
from locust import HttpUser, task, between, events
from locust.exception import RescheduleTask


class ContentGenerationUser(HttpUser):
    """Simulates users generating various types of content."""
    
    wait_time = between(2, 5)
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.api_key = "test-api-key-12345"
        self.auth_token = None
        self.active_jobs = []
        self.completed_jobs = []
        
        # Content generation templates
        self.syllabi = [
            {
                "topic": "Introduction to Machine Learning",
                "content": "This course covers the fundamentals of machine learning including supervised learning, unsupervised learning, neural networks, and deep learning. Students will learn about classification, regression, clustering, and dimensionality reduction.",
                "size": "medium"
            },
            {
                "topic": "Quantum Physics Basics",
                "content": "An introduction to quantum mechanics covering wave-particle duality, Heisenberg uncertainty principle, Schrödinger equation, quantum entanglement, and applications in modern technology.",
                "size": "medium"
            },
            {
                "topic": "World War II History",
                "content": "Comprehensive study of World War II including causes, major battles, political leaders, Holocaust, Pacific theater, European theater, and post-war consequences. Analysis of primary sources and historical documents.",
                "size": "large"
            },
            {
                "topic": "Python Programming",
                "content": "Learn Python from basics: variables, data types, control flow, functions, OOP, file handling, error handling, modules, and popular libraries like NumPy, Pandas, and Matplotlib.",
                "size": "medium"
            },
            {
                "topic": "Basic Algebra",
                "content": "Simple algebra concepts: equations, variables, and basic operations.",
                "size": "small"
            }
        ]
    
    def on_start(self):
        """Setup user authentication."""
        self.authenticate()
    
    def authenticate(self):
        """Authenticate and get token."""
        email = f"content_user_{random.randint(1, 100)}@example.com"
        
        # Try login first
        with self.client.post(
            "/api/v1/auth/login",
            data={
                "username": email,
                "password": "ContentTest123!"
            },
            catch_response=True
        ) as response:
            if response.status_code == 200:
                data = response.json()
                self.auth_token = data.get("access_token")
                response.success()
            else:
                # Register new user
                self.client.post(
                    "/api/v1/auth/register",
                    json={
                        "email": email,
                        "password": "ContentTest123!",
                        "full_name": f"Content Test User"
                    }
                )
                raise RescheduleTask()
    
    def get_headers(self):
        """Get request headers."""
        headers = {"X-API-Key": self.api_key}
        if self.auth_token:
            headers["Authorization"] = f"Bearer {self.auth_token}"
        return headers
    
    @task(5)
    def create_content_job(self):
        """Create an asynchronous content generation job."""
        syllabus = random.choice(self.syllabi)
        content_types = ["podcast", "summary", "flashcards", "quiz"]
        
        # Vary cache usage based on content
        use_cache = random.random() > 0.3  # 70% cache usage
        
        with self.client.post(
            "/api/v1/jobs",
            headers=self.get_headers(),
            json={
                "syllabus_text": syllabus["content"],
                "target_format": random.choice(content_types),
                "use_cache": use_cache
            },
            catch_response=True,
            name=f"/jobs [create-{syllabus['size']}]"
        ) as response:
            if response.status_code == 201:
                response.success()
                data = response.json()
                job_id = data.get("id")
                if job_id:
                    self.active_jobs.append({
                        "id": job_id,
                        "created_at": time.time(),
                        "size": syllabus["size"]
                    })
                    # Keep only last 20 active jobs
                    if len(self.active_jobs) > 20:
                        self.active_jobs = self.active_jobs[-20:]
            else:
                response.failure(f"Job creation failed: {response.status_code}")
    
    @task(8)
    def check_job_progress(self):
        """Check progress of active jobs."""
        if not self.active_jobs:
            return
        
        job = random.choice(self.active_jobs)
        
        with self.client.get(
            f"/api/v1/jobs/{job['id']}",
            headers=self.get_headers(),
            catch_response=True,
            name=f"/jobs/{{id}} [check-{job['size']}]"
        ) as response:
            if response.status_code == 200:
                response.success()
                data = response.json()
                status = data.get("status")
                
                if status in ["completed", "failed"]:
                    # Move to completed
                    self.active_jobs.remove(job)
                    self.completed_jobs.append({
                        **job,
                        "completed_at": time.time(),
                        "duration": time.time() - job["created_at"],
                        "status": status
                    })
                    
                    # Keep only last 50 completed jobs
                    if len(self.completed_jobs) > 50:
                        self.completed_jobs = self.completed_jobs[-50:]
            elif response.status_code == 404:
                # Job not found, remove from active
                self.active_jobs.remove(job)
                response.success()
            else:
                response.failure(f"Job check failed: {response.status_code}")
    
    @task(2)
    def direct_content_generation_small(self):
        """Generate small content directly (synchronous)."""
        with self.client.post(
            "/api/v1/content/generate",
            headers=self.get_headers(),
            json={
                "syllabus_text": "Quick summary: Explain photosynthesis in simple terms.",
                "target_format": "summary",
                "use_cache": True
            },
            timeout=15,
            catch_response=True,
            name="/content/generate [small]"
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Direct generation failed: {response.status_code}")
    
    @task(1)
    def direct_content_generation_large(self):
        """Generate large content directly (synchronous)."""
        large_syllabus = random.choice([s for s in self.syllabi if s["size"] == "large"])
        
        with self.client.post(
            "/api/v1/content/generate",
            headers=self.get_headers(),
            json={
                "syllabus_text": large_syllabus["content"],
                "target_format": "podcast",
                "use_cache": False  # Force regeneration
            },
            timeout=60,  # Longer timeout for large content
            catch_response=True,
            name="/content/generate [large]"
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Large generation failed: {response.status_code}")
    
    @task(3)
    def list_jobs_with_filters(self):
        """List jobs with various filters."""
        filters = [
            {"status": "pending"},
            {"status": "processing"},
            {"status": "completed"},
            {"page": random.randint(1, 5), "page_size": 20},
            {}  # No filters
        ]
        
        filter_params = random.choice(filters)
        query_string = "&".join([f"{k}={v}" for k, v in filter_params.items()])
        
        with self.client.get(
            f"/api/v1/jobs?{query_string}",
            headers=self.get_headers(),
            catch_response=True,
            name="/jobs [filtered]"
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Job listing failed: {response.status_code}")
    
    def on_stop(self):
        """Report content generation statistics."""
        if self.completed_jobs:
            total_jobs = len(self.completed_jobs)
            successful_jobs = len([j for j in self.completed_jobs if j["status"] == "completed"])
            avg_duration = sum(j["duration"] for j in self.completed_jobs) / total_jobs
            
            print(f"\nContent Generation Stats:")
            print(f"  Total jobs: {total_jobs}")
            print(f"  Successful: {successful_jobs} ({(successful_jobs/total_jobs)*100:.1f}%)")
            print(f"  Average duration: {avg_duration:.1f}s")
            
            # Duration by size
            for size in ["small", "medium", "large"]:
                size_jobs = [j for j in self.completed_jobs if j["size"] == size]
                if size_jobs:
                    avg_size_duration = sum(j["duration"] for j in size_jobs) / len(size_jobs)
                    print(f"  Average {size} duration: {avg_size_duration:.1f}s")


class CacheTestUser(HttpUser):
    """Tests cache behavior under load."""
    
    wait_time = between(1, 2)
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.api_key = "test-api-key-12345"
        self.popular_content = [
            "Introduction to Python programming basics",
            "Overview of World War II major events",
            "Fundamentals of quantum mechanics",
            "Basic algebra and equations",
            "Machine learning introduction"
        ]
    
    def get_headers(self):
        """Get request headers."""
        return {"X-API-Key": self.api_key}
    
    @task(10)
    def request_popular_content(self):
        """Request popular content (should hit cache)."""
        content = random.choice(self.popular_content)
        
        with self.client.post(
            "/api/v1/content/generate",
            headers=self.get_headers(),
            json={
                "syllabus_text": content,
                "target_format": "summary",
                "use_cache": True
            },
            catch_response=True,
            name="/content/generate [cache-hit]"
        ) as response:
            if response.status_code == 200:
                response.success()
                # Check if it was a cache hit (should be faster)
                if response.elapsed.total_seconds() < 0.5:
                    print(f"Cache hit for: {content[:30]}...")
            else:
                response.failure(f"Cache request failed: {response.status_code}")
    
    @task(2)
    def request_unique_content(self):
        """Request unique content (should miss cache)."""
        unique_id = random.randint(10000, 99999)
        content = f"Unique content {unique_id}: Explain the concept of {unique_id} in detail."
        
        with self.client.post(
            "/api/v1/content/generate",
            headers=self.get_headers(),
            json={
                "syllabus_text": content,
                "target_format": "summary",
                "use_cache": True
            },
            catch_response=True,
            name="/content/generate [cache-miss]"
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Unique content failed: {response.status_code}")
    
    @task(1)
    def force_cache_bypass(self):
        """Force cache bypass for popular content."""
        content = random.choice(self.popular_content)
        
        with self.client.post(
            "/api/v1/content/generate",
            headers=self.get_headers(),
            json={
                "syllabus_text": content,
                "target_format": "summary",
                "use_cache": False  # Force bypass
            },
            catch_response=True,
            name="/content/generate [no-cache]"
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"No-cache request failed: {response.status_code}")


# Event handlers for content generation metrics
generation_times = {}

@events.request.add_listener
def track_generation_time(request_type, name, response_time, response_length, response, **kwargs):
    """Track content generation times."""
    if "/content/generate" in name or "/jobs" in name:
        if name not in generation_times:
            generation_times[name] = []
        generation_times[name].append(response_time)

@events.test_stop.add_listener
def report_generation_metrics(environment, **kwargs):
    """Report content generation metrics."""
    if generation_times:
        print("\nContent Generation Performance:")
        print("-" * 60)
        for endpoint, times in generation_times.items():
            if times:
                avg_time = sum(times) / len(times)
                min_time = min(times)
                max_time = max(times)
                print(f"\n{endpoint}:")
                print(f"  Requests: {len(times)}")
                print(f"  Avg time: {avg_time:.0f}ms")
                print(f"  Min time: {min_time:.0f}ms")
                print(f"  Max time: {max_time:.0f}ms")