import logging
import os
import time
from typing import Any, Dict, List, Optional

import requests
from dotenv import load_dotenv

load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
if not GITHUB_TOKEN:
    raise EnvironmentError(
        "GITHUB_TOKEN not set. Please add it to your .env file or environment variables."
    )

GITHUB_API_URL = "https://api.github.com"

logger = logging.getLogger(__name__)


def _make_github_request_with_retry(
    method: str, url: str, data: dict = None, max_retries: int = 3
):
    """Make a GitHub API request with retry logic and exponential backoff."""
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json",
    }

    for attempt in range(max_retries):
        try:
            if method.upper() == "POST":
                response = requests.post(url, json=data, headers=headers, timeout=30)
            elif method.upper() == "PATCH":
                response = requests.patch(url, json=data, headers=headers, timeout=30)
            else:
                response = requests.get(url, headers=headers, timeout=30)

            response.raise_for_status()
            return response.json()

        except (
            requests.exceptions.ConnectTimeout,
            requests.exceptions.ReadTimeout,
        ) as e:
            print(
                f"  ⏳ Network timeout on attempt {attempt + 1}/{max_retries}. Retrying in {2 ** attempt} seconds..."
            )
            if attempt < max_retries - 1:
                time.sleep(2**attempt)  # Exponential backoff: 1s, 2s, 4s
            else:
                raise e
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:  # Rate limit
                print("  🚦 Rate limited. Waiting 60 seconds...")
                time.sleep(60)
                if attempt < max_retries - 1:
                    continue
            raise e

    raise Exception(f"Failed after {max_retries} attempts")


def create_github_issue(
    title: str,
    body: str,
    token: str,
    repo: str,
    owner: str,
    labels: Optional[List[str]] = None,
) -> Optional[Dict[str, Any]]:
    """
    Create a GitHub issue.

    Args:
        title: Issue title
        body: Issue body
        token: GitHub token
        repo: Repository name
        owner: Repository owner
        labels: Optional list of labels

    Returns:
        Created issue data or None if failed
    """
    url = f"https://api.github.com/repos/{owner}/{repo}/issues"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json",
    }
    data = {"title": title, "body": body, "labels": labels or []}

    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:  # Rate limit
                print("  🚦 Rate limited. Waiting 60 seconds...")
                time.sleep(60)
                if attempt < max_retries - 1:
                    continue
            logger.error(f"Failed to create GitHub issue: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Error creating GitHub issue: {str(e)}")
            return None


def close_github_issue(repo: str, issue_number: int) -> dict:
    """Close a GitHub Issue by issue number.

    Args:
        repo (str): The repository in 'owner/repo' format.
        issue_number (int): The issue number to close.

    Returns:
        dict: The updated issue's JSON data.
    """
    url = f"{GITHUB_API_URL}/repos/{repo}/issues/{issue_number}"
    data = {"state": "closed"}

    result = _make_github_request_with_retry("PATCH", url, data)

    # Small delay between requests
    time.sleep(0.3)

    return result


def add_comment_to_issue(repo: str, issue_number: int, comment: str) -> dict:
    """Add a comment to a GitHub Issue.

    Args:
        repo (str): The repository in 'owner/repo' format.
        issue_number (int): The issue number to comment on.
        comment (str): The comment text.

    Returns:
        dict: The created comment's JSON data.
    """
    url = f"{GITHUB_API_URL}/repos/{repo}/issues/{issue_number}/comments"
    data = {"body": comment}

    result = _make_github_request_with_retry("POST", url, data)

    # Small delay between requests
    time.sleep(0.3)

    return result
