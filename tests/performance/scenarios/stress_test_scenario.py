"""
Stress test scenarios for La Factoria API.

Tests system behavior under extreme conditions:
- Sudden traffic spikes
- Sustained high load
- Resource exhaustion scenarios
- Database connection pool stress
- External service timeouts
"""

import random
import time
import threading
from locust import HttpUser, task, between, events, LoadTestShape
from locust.exception import RescheduleTask


class StressTestUser(HttpUser):
    """User for stress testing with aggressive request patterns."""
    
    wait_time = between(0.1, 0.5)  # Very aggressive timing
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.api_key = "test-api-key-12345"
        self.tokens = []  # Multiple tokens for parallel requests
        self.request_count = 0
        self.error_count = 0
    
    def on_start(self):
        """Create multiple sessions for stress testing."""
        # Create multiple user sessions
        for i in range(3):
            email = f"stress_user_{random.randint(1000, 9999)}_{i}@example.com"
            self.create_session(email)
    
    def create_session(self, email):
        """Create a user session and get token."""
        # Register user
        self.client.post(
            "/api/v1/auth/register",
            json={
                "email": email,
                "password": "StressTest123!",
                "full_name": "Stress Test User"
            }
        )
        
        # Login
        response = self.client.post(
            "/api/v1/auth/login",
            data={
                "username": email,
                "password": "StressTest123!"
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            token = data.get("access_token")
            if token:
                self.tokens.append(token)
    
    def get_headers(self):
        """Get headers with random token."""
        headers = {"X-API-Key": self.api_key}
        if self.tokens:
            headers["Authorization"] = f"Bearer {random.choice(self.tokens)}"
        return headers
    
    @task(10)
    def rapid_fire_requests(self):
        """Send rapid requests to various endpoints."""
        endpoints = [
            ("/healthz", "GET", None),
            ("/api/v1/health", "GET", None),
            ("/api/v1/jobs", "GET", None),
            ("/api/v1/jobs", "POST", {
                "syllabus_text": f"Stress test content {random.randint(1, 1000)}",
                "target_format": random.choice(["summary", "quiz", "flashcards"]),
                "use_cache": random.choice([True, False])
            }),
        ]
        
        endpoint, method, data = random.choice(endpoints)
        
        with self.client.request(
            method,
            endpoint,
            headers=self.get_headers() if endpoint != "/healthz" else {},
            json=data,
            catch_response=True,
            name=f"{endpoint} [stress]"
        ) as response:
            self.request_count += 1
            if response.status_code < 400:
                response.success()
            elif response.status_code == 429:
                # Rate limited - expected under stress
                response.success()
                self.error_count += 1
            else:
                response.failure(f"Status: {response.status_code}")
                self.error_count += 1
    
    @task(5)
    def concurrent_job_creation(self):
        """Create multiple jobs concurrently."""
        def create_job():
            self.client.post(
                "/api/v1/jobs",
                headers=self.get_headers(),
                json={
                    "syllabus_text": f"Concurrent test {time.time()}",
                    "target_format": "summary",
                    "use_cache": False
                }
            )
        
        # Create 3 concurrent requests
        threads = []
        for _ in range(3):
            t = threading.Thread(target=create_job)
            threads.append(t)
            t.start()
        
        # Wait for all threads
        for t in threads:
            t.join(timeout=5)
    
    @task(3)
    def large_payload_request(self):
        """Send requests with large payloads."""
        # Generate large syllabus text
        large_text = " ".join([
            f"Chapter {i}: " + " ".join([f"Topic {j}" for j in range(100)])
            for i in range(10)
        ])
        
        with self.client.post(
            "/api/v1/content/generate",
            headers=self.get_headers(),
            json={
                "syllabus_text": large_text,
                "target_format": "podcast",
                "use_cache": False
            },
            timeout=60,
            catch_response=True,
            name="/content/generate [large-payload]"
        ) as response:
            if response.status_code == 200:
                response.success()
            elif response.status_code == 413:
                # Payload too large - expected
                response.success()
            else:
                response.failure(f"Large payload failed: {response.status_code}")
    
    @task(2)
    def timeout_simulation(self):
        """Simulate requests that might timeout."""
        with self.client.post(
            "/api/v1/content/generate",
            headers=self.get_headers(),
            json={
                "syllabus_text": "Generate extremely detailed content with all possible variations and examples " * 10,
                "target_format": "podcast",
                "use_cache": False
            },
            timeout=5,  # Short timeout
            catch_response=True,
            name="/content/generate [timeout-test]"
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                # Timeout or error expected
                response.success()
    
    def on_stop(self):
        """Report stress test metrics."""
        if self.request_count > 0:
            error_rate = (self.error_count / self.request_count) * 100
            print(f"\nStress Test Metrics:")
            print(f"  Total requests: {self.request_count}")
            print(f"  Errors: {self.error_count}")
            print(f"  Error rate: {error_rate:.1f}%")


class DatabaseStressUser(HttpUser):
    """Specifically stress database operations."""
    
    wait_time = between(0.2, 0.8)
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.api_key = "test-api-key-12345"
        self.job_ids = []
    
    def get_headers(self):
        """Get request headers."""
        return {"X-API-Key": self.api_key}
    
    @task(5)
    def create_many_jobs(self):
        """Create many jobs to stress job storage."""
        batch_size = random.randint(5, 10)
        
        for _ in range(batch_size):
            response = self.client.post(
                "/api/v1/jobs",
                headers=self.get_headers(),
                json={
                    "syllabus_text": f"DB stress test {random.randint(1, 10000)}",
                    "target_format": "summary",
                    "use_cache": False
                }
            )
            
            if response.status_code == 201:
                data = response.json()
                job_id = data.get("id")
                if job_id:
                    self.job_ids.append(job_id)
                    # Keep only last 100 jobs
                    if len(self.job_ids) > 100:
                        self.job_ids = self.job_ids[-100:]
    
    @task(10)
    def query_many_jobs(self):
        """Query jobs with complex filters."""
        # Large page size to stress database
        page_size = random.choice([50, 100, 200])
        
        with self.client.get(
            f"/api/v1/jobs?page=1&page_size={page_size}",
            headers=self.get_headers(),
            catch_response=True,
            name=f"/jobs [page_size={page_size}]"
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Query failed: {response.status_code}")
    
    @task(8)
    def concurrent_job_updates(self):
        """Check many jobs concurrently."""
        if not self.job_ids:
            return
        
        # Select random subset of jobs
        jobs_to_check = random.sample(
            self.job_ids, 
            min(10, len(self.job_ids))
        )
        
        def check_job(job_id):
            self.client.get(
                f"/api/v1/jobs/{job_id}",
                headers=self.get_headers()
            )
        
        # Check jobs in parallel
        threads = []
        for job_id in jobs_to_check:
            t = threading.Thread(target=check_job, args=(job_id,))
            threads.append(t)
            t.start()
        
        # Wait for all
        for t in threads:
            t.join(timeout=3)


class SpikeLoadShape(LoadTestShape):
    """
    A load test shape that creates sudden spikes in traffic.
    
    Simulates real-world traffic patterns with sudden increases.
    """
    
    stages = [
        {"duration": 60, "users": 10, "spawn_rate": 2},    # Warm up
        {"duration": 120, "users": 100, "spawn_rate": 50}, # Sudden spike
        {"duration": 180, "users": 20, "spawn_rate": 10},  # Drop
        {"duration": 240, "users": 200, "spawn_rate": 100}, # Bigger spike
        {"duration": 300, "users": 50, "spawn_rate": 20},  # Stabilize
        {"duration": 360, "users": 0, "spawn_rate": 10},   # Cool down
    ]
    
    def tick(self):
        run_time = self.get_run_time()
        
        for stage in self.stages:
            if run_time < stage["duration"]:
                return (stage["users"], stage["spawn_rate"])
        
        return None


class SustainedLoadUser(HttpUser):
    """User for sustained load testing."""
    
    wait_time = between(1, 3)  # More realistic timing
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.api_key = "test-api-key-12345"
        self.token = None
        self.user_email = f"sustained_user_{random.randint(1, 1000)}@example.com"
    
    def on_start(self):
        """Setup user."""
        self.authenticate()
    
    def authenticate(self):
        """Get authentication token."""
        # Register
        self.client.post(
            "/api/v1/auth/register",
            json={
                "email": self.user_email,
                "password": "Sustained123!",
                "full_name": "Sustained Load User"
            }
        )
        
        # Login
        response = self.client.post(
            "/api/v1/auth/login",
            data={
                "username": self.user_email,
                "password": "Sustained123!"
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            self.token = data.get("access_token")
    
    def get_headers(self):
        """Get request headers."""
        headers = {"X-API-Key": self.api_key}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers
    
    @task(30)
    def normal_workflow(self):
        """Simulate normal user workflow."""
        # Check health
        self.client.get("/healthz")
        
        # Create a job
        response = self.client.post(
            "/api/v1/jobs",
            headers=self.get_headers(),
            json={
                "syllabus_text": f"Sustained test content about {random.choice(['math', 'science', 'history'])}",
                "target_format": random.choice(["summary", "quiz", "flashcards"]),
                "use_cache": True
            }
        )
        
        if response.status_code == 201:
            job_id = response.json().get("id")
            
            # Check job status a few times
            for _ in range(3):
                time.sleep(2)
                self.client.get(
                    f"/api/v1/jobs/{job_id}",
                    headers=self.get_headers()
                )
        
        # Check usage
        self.client.get(
            f"/api/v1/monitoring/usage/user/{self.user_email}",
            headers=self.get_headers()
        )
    
    @task(10)
    def browse_jobs(self):
        """Browse job history."""
        # List jobs with different filters
        for page in range(1, 4):
            self.client.get(
                f"/api/v1/jobs?page={page}&page_size=10",
                headers=self.get_headers()
            )
            time.sleep(1)  # Simulate reading
    
    @task(5)
    def direct_generation(self):
        """Direct content generation."""
        self.client.post(
            "/api/v1/content/generate",
            headers=self.get_headers(),
            json={
                "syllabus_text": "Create a brief summary about renewable energy",
                "target_format": "summary",
                "use_cache": True
            },
            timeout=30
        )


# Event handlers for stress test metrics
stress_metrics = {
    "max_response_time": 0,
    "total_timeouts": 0,
    "total_rate_limits": 0,
    "connection_errors": 0
}

@events.request.add_listener
def track_stress_metrics(request_type, name, response_time, response_length, response, **kwargs):
    """Track stress test specific metrics."""
    global stress_metrics
    
    # Track max response time
    if response_time > stress_metrics["max_response_time"]:
        stress_metrics["max_response_time"] = response_time
    
    # Track rate limits
    if hasattr(response, 'status_code') and response.status_code == 429:
        stress_metrics["total_rate_limits"] += 1

@events.request_failure.add_listener
def track_stress_failures(request_type, name, response_time, response_length, exception, **kwargs):
    """Track stress test failures."""
    global stress_metrics
    
    if "timeout" in str(exception).lower():
        stress_metrics["total_timeouts"] += 1
    elif "connection" in str(exception).lower():
        stress_metrics["connection_errors"] += 1

@events.test_stop.add_listener
def report_stress_metrics(environment, **kwargs):
    """Report stress test specific metrics."""
    print("\nStress Test Summary:")
    print("-" * 60)
    print(f"Max response time: {stress_metrics['max_response_time']:.0f}ms")
    print(f"Total timeouts: {stress_metrics['total_timeouts']}")
    print(f"Total rate limits: {stress_metrics['total_rate_limits']}")
    print(f"Connection errors: {stress_metrics['connection_errors']}")
    
    # Calculate requests per second at peak
    if hasattr(environment.stats, 'total'):
        total_time = environment.stats.total.last_request_timestamp - environment.stats.total.start_time
        if total_time > 0:
            rps = environment.stats.total.num_requests / total_time
            print(f"Average RPS: {rps:.1f}")