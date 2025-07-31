"""
Main Locust load testing file for La Factoria API.

This module defines load test scenarios for key API endpoints including
health checks, authentication, content generation, and job management.
"""

import json
import os
import random
import time
from typing import Dict, Any

from locust import HttpUser, TaskSet, task, between, events
from locust.env import Environment
from locust.stats import stats_printer, stats_history
from locust.log import setup_logging

# Setup logging
setup_logging("INFO", None)


class LaFactoriaUser(HttpUser):
    """Simulates a typical La Factoria API user."""
    
    wait_time = between(1, 3)  # Wait 1-3 seconds between tasks
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.api_key = None
        self.auth_token = None
        self.user_id = None
        self.job_ids = []
    
    def on_start(self):
        """Called when a user starts. Performs authentication."""
        # Get API key from environment or use test key
        self.api_key = os.getenv("LA_FACTORIA_API_KEY", "test-api-key-12345")
        
        # Authenticate user
        self.login()
    
    def login(self):
        """Authenticate user and store token."""
        # Register a new test user
        user_num = random.randint(1000, 9999)
        email = f"loadtest_user_{user_num}@example.com"
        
        # Try to register first
        register_response = self.client.post(
            "/api/v1/auth/register",
            json={
                "email": email,
                "password": "LoadTest123!",
                "full_name": f"Load Test User {user_num}"
            },
            catch_response=True
        )
        
        # If registration fails (user exists), proceed to login
        if register_response.status_code != 201:
            register_response.failure("Registration failed (expected for existing users)")
        else:
            register_response.success()
        
        # Login
        with self.client.post(
            "/api/v1/auth/login",
            data={
                "username": email,
                "password": "LoadTest123!"
            },
            catch_response=True
        ) as response:
            if response.status_code == 200:
                data = response.json()
                self.auth_token = data.get("access_token")
                self.user_id = email  # Using email as user ID
                response.success()
            else:
                response.failure(f"Login failed: {response.text}")
    
    def get_headers(self, include_auth=True):
        """Get headers for API requests."""
        headers = {
            "X-API-Key": self.api_key,
            "Content-Type": "application/json"
        }
        if include_auth and self.auth_token:
            headers["Authorization"] = f"Bearer {self.auth_token}"
        return headers
    
    @task(10)
    def health_check(self):
        """Test health check endpoint (most frequent)."""
        with self.client.get(
            "/healthz",
            catch_response=True,
            name="/healthz"
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Health check failed: {response.status_code}")
    
    @task(5)
    def api_health_check(self):
        """Test API health check endpoint."""
        with self.client.get(
            "/api/v1/health",
            headers=self.get_headers(include_auth=False),
            catch_response=True,
            name="/api/v1/health"
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"API health check failed: {response.status_code}")
    
    @task(3)
    def create_job(self):
        """Create a content generation job."""
        content_types = ["podcast", "summary", "flashcards", "quiz"]
        
        with self.client.post(
            "/api/v1/jobs",
            headers=self.get_headers(),
            json={
                "syllabus_text": f"Load test content for {random.choice(content_types)}. "
                                 f"This is a test syllabus about {random.choice(['Mathematics', 'Science', 'History', 'Literature'])}. "
                                 f"Topic: {random.choice(['Algebra', 'Physics', 'World War II', 'Shakespeare'])}.",
                "target_format": random.choice(content_types),
                "use_cache": random.choice([True, False])
            },
            catch_response=True,
            name="/api/v1/jobs [POST]"
        ) as response:
            if response.status_code == 201:
                data = response.json()
                job_id = data.get("id")
                if job_id:
                    self.job_ids.append(job_id)
                    # Keep only last 10 job IDs
                    if len(self.job_ids) > 10:
                        self.job_ids = self.job_ids[-10:]
                response.success()
            else:
                response.failure(f"Job creation failed: {response.text}")
    
    @task(4)
    def check_job_status(self):
        """Check status of a random job."""
        if not self.job_ids:
            return  # Skip if no jobs created yet
        
        job_id = random.choice(self.job_ids)
        
        with self.client.get(
            f"/api/v1/jobs/{job_id}",
            headers=self.get_headers(),
            catch_response=True,
            name="/api/v1/jobs/{id} [GET]"
        ) as response:
            if response.status_code == 200:
                response.success()
            elif response.status_code == 404:
                # Job might have been cleaned up
                self.job_ids.remove(job_id)
                response.success()
            else:
                response.failure(f"Job status check failed: {response.status_code}")
    
    @task(2)
    def list_jobs(self):
        """List jobs with pagination."""
        page = random.randint(1, 3)
        page_size = random.choice([10, 20, 50])
        
        with self.client.get(
            f"/api/v1/jobs?page={page}&page_size={page_size}",
            headers=self.get_headers(),
            catch_response=True,
            name="/api/v1/jobs [GET]"
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Job listing failed: {response.status_code}")
    
    @task(1)
    def direct_content_generation(self):
        """Test direct content generation (synchronous)."""
        with self.client.post(
            "/api/v1/content/generate",
            headers=self.get_headers(),
            json={
                "syllabus_text": "Quick test: Generate a brief summary about quantum mechanics basics.",
                "target_format": "summary",
                "use_cache": True
            },
            catch_response=True,
            timeout=30,  # 30 second timeout for content generation
            name="/api/v1/content/generate"
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Content generation failed: {response.status_code}")
    
    @task(2)
    def check_usage(self):
        """Check user's usage statistics."""
        if not self.user_id:
            return
        
        with self.client.get(
            f"/api/v1/monitoring/usage/user/{self.user_id}",
            headers=self.get_headers(),
            catch_response=True,
            name="/api/v1/monitoring/usage/user/{id}"
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Usage check failed: {response.status_code}")


class AdminUser(HttpUser):
    """Simulates an admin user checking monitoring endpoints."""
    
    wait_time = between(5, 10)  # Admins check less frequently
    
    def on_start(self):
        """Admin authentication."""
        self.api_key = os.getenv("LA_FACTORIA_API_KEY", "test-api-key-12345")
        self.auth_token = None
        
        # Login as admin
        self.login_admin()
    
    def login_admin(self):
        """Login with admin credentials."""
        admin_email = os.getenv("ADMIN_EMAIL", "admin@lafactoria.ai")
        admin_password = os.getenv("ADMIN_PASSWORD", "AdminPass123!")
        
        with self.client.post(
            "/api/v1/auth/login",
            data={
                "username": admin_email,
                "password": admin_password
            },
            catch_response=True
        ) as response:
            if response.status_code == 200:
                data = response.json()
                self.auth_token = data.get("access_token")
                response.success()
            else:
                # If admin login fails, create a regular user
                self.client = LaFactoriaUser(self.environment)
                self.client.on_start()
    
    def get_headers(self):
        """Get headers for admin requests."""
        headers = {
            "X-API-Key": self.api_key,
            "Content-Type": "application/json"
        }
        if self.auth_token:
            headers["Authorization"] = f"Bearer {self.auth_token}"
        return headers
    
    @task
    def check_usage_summary(self):
        """Check overall usage summary."""
        with self.client.get(
            "/api/v1/monitoring/usage/summary",
            headers=self.get_headers(),
            catch_response=True,
            name="/api/v1/monitoring/usage/summary"
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Usage summary failed: {response.status_code}")


# Event handlers for reporting
@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    """Called when test starts."""
    print("Load test starting...")
    print(f"Target host: {environment.host}")
    print(f"Total users: {environment.parsed_options.num_users}")
    print(f"Spawn rate: {environment.parsed_options.spawn_rate}")


@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """Called when test stops."""
    print("\nLoad test completed!")
    print("\nTest Statistics Summary:")
    print("-" * 80)
    
    # Print summary statistics
    for name, entry in environment.stats.entries.items():
        print(f"\nEndpoint: {name}")
        print(f"  Total Requests: {entry.num_requests}")
        print(f"  Failure Rate: {entry.fail_ratio:.2%}")
        print(f"  Average Response Time: {entry.avg_response_time:.0f}ms")
        print(f"  Min Response Time: {entry.min_response_time:.0f}ms")
        print(f"  Max Response Time: {entry.max_response_time:.0f}ms")
        print(f"  Median Response Time: {entry.get_response_time_percentile(0.5):.0f}ms")
        print(f"  95th Percentile: {entry.get_response_time_percentile(0.95):.0f}ms")
        print(f"  99th Percentile: {entry.get_response_time_percentile(0.99):.0f}ms")


# Custom scenarios for specific load patterns
class QuickCheckUser(HttpUser):
    """User that only performs health checks - simulates monitoring systems."""
    
    wait_time = between(5, 10)
    
    @task
    def health_check_only(self):
        """Only check health endpoints."""
        self.client.get("/healthz")
        self.client.get("/api/v1/health", headers={"X-API-Key": "test-api-key-12345"})


class HeavyContentUser(LaFactoriaUser):
    """User that primarily generates content - simulates heavy API usage."""
    
    wait_time = between(2, 5)
    
    @task(1)
    def health_check(self):
        """Reduce health check frequency."""
        super().health_check()
    
    @task(10)
    def create_job(self):
        """Increase job creation frequency."""
        super().create_job()
    
    @task(8)
    def direct_content_generation(self):
        """Increase direct content generation."""
        super().direct_content_generation()