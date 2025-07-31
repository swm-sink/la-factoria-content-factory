"""
Authentication-focused load test scenario.

Tests authentication endpoints under various load conditions including:
- User registration storms
- Login attempts
- Token validation
- Failed authentication attempts
"""

import random
import time
from locust import HttpUser, task, between, events
from locust.exception import RescheduleTask


class AuthenticationStormUser(HttpUser):
    """Simulates authentication storms (e.g., many users logging in at once)."""
    
    wait_time = between(0.5, 2)  # Faster requests for storm simulation
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.successful_logins = 0
        self.failed_logins = 0
    
    @task(3)
    def register_new_user(self):
        """Attempt to register a new user."""
        user_num = random.randint(10000, 99999)
        email = f"storm_user_{user_num}_{int(time.time())}@example.com"
        
        with self.client.post(
            "/api/v1/auth/register",
            json={
                "email": email,
                "password": "StormTest123!",
                "full_name": f"Storm User {user_num}"
            },
            catch_response=True,
            name="/auth/register [storm]"
        ) as response:
            if response.status_code == 201:
                response.success()
                # Immediately try to login
                self.login_user(email, "StormTest123!")
            elif response.status_code == 400:
                # User might already exist
                response.success()
            else:
                response.failure(f"Registration failed: {response.status_code}")
    
    @task(5)
    def login_existing_user(self):
        """Login with existing test users."""
        user_num = random.randint(1, 100)
        email = f"existing_user_{user_num}@example.com"
        
        self.login_user(email, "TestPass123!")
    
    @task(2)
    def login_with_wrong_password(self):
        """Simulate failed login attempts."""
        user_num = random.randint(1, 100)
        email = f"existing_user_{user_num}@example.com"
        
        with self.client.post(
            "/api/v1/auth/login",
            data={
                "username": email,
                "password": "WrongPassword123!"
            },
            catch_response=True,
            name="/auth/login [failed]"
        ) as response:
            if response.status_code == 401:
                response.success()  # Expected failure
                self.failed_logins += 1
            else:
                response.failure(f"Expected 401, got {response.status_code}")
    
    def login_user(self, email: str, password: str):
        """Helper method to login a user."""
        with self.client.post(
            "/api/v1/auth/login",
            data={
                "username": email,
                "password": password
            },
            catch_response=True,
            name="/auth/login [storm]"
        ) as response:
            if response.status_code == 200:
                response.success()
                self.successful_logins += 1
                
                # Use the token for a few authenticated requests
                data = response.json()
                token = data.get("access_token")
                if token:
                    self.make_authenticated_request(token)
            else:
                response.failure(f"Login failed: {response.status_code}")
                self.failed_logins += 1
    
    def make_authenticated_request(self, token: str):
        """Make an authenticated request to test token validation."""
        headers = {
            "Authorization": f"Bearer {token}",
            "X-API-Key": "test-api-key-12345"
        }
        
        # Random authenticated endpoint
        endpoint = random.choice([
            "/api/v1/jobs",
            "/api/v1/monitoring/usage/user/me",
        ])
        
        with self.client.get(
            endpoint,
            headers=headers,
            catch_response=True,
            name=f"{endpoint} [authenticated]"
        ) as response:
            if response.status_code in [200, 404]:
                response.success()
            else:
                response.failure(f"Authenticated request failed: {response.status_code}")
    
    def on_stop(self):
        """Report authentication statistics."""
        total_attempts = self.successful_logins + self.failed_logins
        if total_attempts > 0:
            success_rate = (self.successful_logins / total_attempts) * 100
            print(f"User auth stats - Success: {self.successful_logins}, "
                  f"Failed: {self.failed_logins}, Success Rate: {success_rate:.1f}%")


class TokenExpirationUser(HttpUser):
    """Tests behavior with expired tokens."""
    
    wait_time = between(1, 3)
    
    def on_start(self):
        """Get initial token."""
        self.token = None
        self.token_age = 0
        self.get_new_token()
    
    def get_new_token(self):
        """Get a fresh token."""
        with self.client.post(
            "/api/v1/auth/login",
            data={
                "username": "token_test@example.com",
                "password": "TokenTest123!"
            },
            catch_response=True
        ) as response:
            if response.status_code == 200:
                data = response.json()
                self.token = data.get("access_token")
                self.token_age = time.time()
                response.success()
            else:
                # Register if doesn't exist
                self.client.post(
                    "/api/v1/auth/register",
                    json={
                        "email": "token_test@example.com",
                        "password": "TokenTest123!",
                        "full_name": "Token Test User"
                    }
                )
                raise RescheduleTask()
    
    @task
    def use_potentially_expired_token(self):
        """Use token that might be expired."""
        if not self.token:
            self.get_new_token()
            return
        
        # Check token age (assume 30 minute expiry)
        token_age_minutes = (time.time() - self.token_age) / 60
        
        headers = {
            "Authorization": f"Bearer {self.token}",
            "X-API-Key": "test-api-key-12345"
        }
        
        with self.client.get(
            "/api/v1/jobs",
            headers=headers,
            catch_response=True,
            name="/api/v1/jobs [token-test]"
        ) as response:
            if response.status_code == 200:
                response.success()
            elif response.status_code == 401:
                # Token expired, get new one
                response.success()  # Expected behavior
                self.get_new_token()
            else:
                response.failure(f"Unexpected response: {response.status_code}")


class BruteForceSimulator(HttpUser):
    """Simulates brute force attack patterns for testing rate limiting."""
    
    wait_time = between(0.1, 0.5)  # Very fast requests
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.target_email = f"target_{random.randint(1, 10)}@example.com"
    
    @task
    def brute_force_login(self):
        """Rapid login attempts with different passwords."""
        passwords = [
            "password123",
            "admin123",
            "12345678",
            "qwerty123",
            f"random{random.randint(1000, 9999)}"
        ]
        
        with self.client.post(
            "/api/v1/auth/login",
            data={
                "username": self.target_email,
                "password": random.choice(passwords)
            },
            catch_response=True,
            name="/auth/login [brute-force]"
        ) as response:
            if response.status_code == 429:
                # Rate limited - this is what we want to see
                response.success()
            elif response.status_code == 401:
                # Failed auth - normal
                response.success()
            else:
                response.failure(f"Unexpected response: {response.status_code}")


# Event handlers for authentication-specific metrics
@events.request.add_listener
def on_request(request_type, name, response_time, response_length, response, **kwargs):
    """Track authentication-specific metrics."""
    if "/auth/" in name:
        if response.status_code == 401:
            # Track failed authentications
            events.request_failure.fire(
                request_type=request_type,
                name=name + " [AUTH_FAILED]",
                response_time=response_time,
                response_length=response_length,
                exception="Authentication failed"
            )
        elif response.status_code == 429:
            # Track rate limiting
            events.request_failure.fire(
                request_type=request_type,
                name=name + " [RATE_LIMITED]",
                response_time=response_time,
                response_length=response_length,
                exception="Rate limited"
            )