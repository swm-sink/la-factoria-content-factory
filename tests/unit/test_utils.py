import pytest

from app.utils.text_cleanup import (
    capitalize_sentences,
    clean_punctuation,
    correct_grammar_and_style,
    normalize_whitespace,
    remove_redundant_words,
)

# --- Tests for normalize_whitespace ---


def test_normalize_whitespace_leading_trailing():
    assert normalize_whitespace("  hello world  ") == "hello world"


def test_normalize_whitespace_multiple_newlines():
    assert normalize_whitespace("hello\n\n\nworld") == "hello\n\nworld"


def test_normalize_whitespace_space_after_newline_before_capital():
    # This rule might be too aggressive or specific, depends on desired outcome.
    # The current rule is `\n([A-Z])` -> `\n\n\1`
    assert (
        normalize_whitespace("Paragraph.\nAnother paragraph.")
        == "Paragraph.\n\nAnother paragraph."
    )
    assert normalize_whitespace("End.\nStart") == "End.\n\nStart"


def test_normalize_whitespace_no_change():
    text = "This is a normal sentence.\n\nThis is another."
    assert normalize_whitespace(text) == text


# --- Tests for remove_redundant_words ---


def test_remove_redundant_words_basic():
    assert (
        remove_redundant_words("the the a a is is that that and and")
        == "the a is that and"
    )
    assert remove_redundant_words("very very good") == "very good"


def test_remove_redundant_words_case_insensitive():
    assert remove_redundant_words("The the cat") == "The cat"
    assert remove_redundant_words("Is is fine?") == "Is fine?"


def test_remove_redundant_words_no_redundancy():
    text = "This sentence has no redundant words."
    assert remove_redundant_words(text) == text


# --- Tests for clean_punctuation ---


def test_clean_punctuation_ellipsis():
    assert clean_punctuation("Wait for it ..") == "Wait for it ..."
    assert clean_punctuation("Wait for it ....") == "Wait for it ..."


def test_clean_punctuation_quotes():
    # The current implementation `re.sub(r'"([^"]+)"', r'"\1"', text)` doesn't change to smart quotes.
    # It ensures quotes are standard double quotes if they surround content.
    # This test will reflect the actual behavior.
    assert clean_punctuation('"Hello"') == '"Hello"'
    # If smart quotes were intended, the regex and assertion would be different.


def test_clean_punctuation_apostrophes():
    # Current implementation `re.sub(r"'", "'", text)` does nothing.
    assert clean_punctuation("it's fine") == "it's fine"


# --- Tests for capitalize_sentences ---


def test_capitalize_sentences_basic():
    assert (
        capitalize_sentences("hello world. this is a test.")
        == "Hello world. This is a test."
    )
    assert (
        capitalize_sentences("first sentence! second sentence? third sentence.")
        == "First sentence! Second sentence? Third sentence."
    )


def test_capitalize_sentences_start_of_text():
    assert capitalize_sentences("this starts lower.") == "This starts lower."


def test_capitalize_sentences_after_newline():
    assert (
        capitalize_sentences("Sentence one.\n new sentence starts here.")
        == "Sentence one.\n New sentence starts here."
    )
    assert (
        capitalize_sentences("Sentence one.\n\n new sentence starts here.")
        == "Sentence one.\n\n New sentence starts here."
    )


# --- Tests for correct_grammar_and_style (orchestrator) ---


def test_correct_grammar_and_style_empty_and_none():
    assert correct_grammar_and_style("") == ""
    assert correct_grammar_and_style(None) == ""


def test_correct_grammar_and_style_no_changes():
    text = "This is a perfectly fine sentence."
    assert correct_grammar_and_style(text) == text


def test_correct_grammar_and_style_common_contractions():
    assert correct_grammar_and_style("it dont work.") == "It don't work."
    assert correct_grammar_and_style("theyre happy.") == "They're happy."
    assert (
        correct_grammar_and_style("its a cat.") == "It's a cat."
    )  # Assuming "its" followed by space and noun


def test_correct_grammar_and_style_common_misspellings():
    assert (
        correct_grammar_and_style("i recieve alot of mail.")
        == "I receive a lot of mail."
    )
    assert (
        correct_grammar_and_style("this is definately neccessary.")
        == "This is definitely necessary."
    )


def test_correct_grammar_and_style_double_spaces():
    assert (
        correct_grammar_and_style("Hello  world.  This  is  a test.")
        == "Hello world. This is a test."
    )


def test_correct_grammar_and_style_space_before_punctuation():
    assert (
        correct_grammar_and_style("Hello , world . How are you ?")
        == "Hello, world. How are you?"
    )


def test_correct_grammar_and_style_multiple_punctuation():
    assert (
        correct_grammar_and_style("Really!!? No way...") == "Really!? No way..."
    )  # Keeps one of !? and normalizes ...


def test_correct_grammar_and_style_space_after_punctuation_before_capital():
    # Example: "end.Next" -> "end. Next"
    assert (
        correct_grammar_and_style("This is the end.Next sentence.")
        == "This is the end. Next sentence."
    )


def test_correct_grammar_and_style_integration():
    original = "  its a test , dont you think alot of ppl recieve this ??  this is definately true . "
    # Note: "ppl" is not in COMMON_CORRECTIONS, so it remains.
    # The sentence capitalization after "true ." might depend on the exact sequence of operations.
    # The current `capitalize_sentences` might not re-capitalize if `COMMON_CORRECTIONS` for space after period runs last.
    # Let's test the output of the current implementation.
    # The `correct_grammar_and_style` applies `normalize_whitespace` and `remove_redundant_words` last.
    # Sentence capitalization happens before that.

    # After COMMON_CORRECTIONS: "  it's a test, don't you think a lot of ppl receive this??  this is definitely true. "
    # After sentence capitalization: "  It's a test, don't you think a lot of ppl receive this??  This is definitely true. "
    # After normalize_whitespace: "It's a test, don't you think a lot of ppl receive this?? This is definitely true."
    # After remove_redundant_words: (no change here)
    # The multiple punctuation `??` is handled by `COMMON_CORRECTIONS` `r"([.!?]){2,}" : r"\1"`
    # So `??` becomes `?`.
    # The space before punctuation ` ,` becomes `,`
    # The space after punctuation `true .` becomes `true.`
    # The `COMMON_CORRECTIONS` `r"([,.!?;:])([A-Z])": r"\1 \2"` ensures space after punctuation if followed by capital.

    # Let's trace:
    # 1. original = "  its a test , dont you think alot of ppl recieve this ??  this is definately true . "
    # 2. COMMON_CORRECTIONS:
    #    "  it's a test , don't you think a lot of ppl receive this ?  this is definitely true . " (multiple changes)
    #    "  it's a test, don't you think a lot of ppl receive this ?  this is definitely true. " (space before punct)
    #    "  it's a test, don't you think a lot of ppl receive this ? This is definitely true. " (space after punct if capital)
    # 3. SENTENCE_ENDINGS & PARAGRAPH_START:
    #    "  It's a test, don't you think a lot of ppl receive this ? This is definitely true. "
    # 4. normalize_whitespace:
    #    "It's a test, don't you think a lot of ppl receive this ? This is definitely true."
    # 5. remove_redundant_words: (no change)

    # So the expected should be:
    expected_after_corrections = "It's a test, don't you think a lot of ppl receive this? This is definitely true."
    assert correct_grammar_and_style(original) == expected_after_corrections


def test_its_vs_it_is_correction():
    # `r"\b(its)\b(?=\s+[a-z])": "it's"`
    assert correct_grammar_and_style("its a dog.") == "It's a dog."
    assert (
        correct_grammar_and_style("its a Very big dog.") == "It's a Very big dog."
    )  # Regex is case insensitive for pattern but not lookahead
    assert (
        correct_grammar_and_style("The dog wagged its tail.")
        == "The dog wagged its tail."
    )  # Should not change possessive 'its'


from app.models.pydantic.content import (  # For validate_ai_content_dict return type
    QualityMetrics,
)

# --- Tests for app.utils.content_validation ---
from app.utils.content_validation import (
    validate_ai_content_dict,  # This is a higher-level orchestrator
)
from app.utils.content_validation import (  # validate_and_parse_content_response, # This one is very high level, might be better for integration tests
    calculate_readability_score,
    check_content_structure,
    estimate_reading_time,
    extract_text_from_content,
    sanitize_content_dict,
    sanitize_html_content,
    validate_content_length_requirements,
)


def test_sanitize_html_content_basic():
    assert sanitize_html_content("<p>Hello</p>") == "<p>Hello</p>"
    assert sanitize_html_content("Hello & world") == "Hello & world"


def test_sanitize_html_content_dangerous_tags():
    assert sanitize_html_content("<script>alert('XSS')</script>Text") == "Text"
    assert sanitize_html_content("Text<iframe src='evil.com'></iframe>") == "Text"
    assert (
        sanitize_html_content("<img src='x' onerror='alert(1)'>") == "<img src='x' >"
    )  # onerror is removed
    assert (
        sanitize_html_content("Text with <object>data</object>") == "Text with data"
    )  # object tags are removed


def test_sanitize_html_content_empty_and_none():
    assert sanitize_html_content("") == ""
    # Assuming the function is robust to None, though type hints suggest str
    # assert sanitize_html_content(None) == "" # Current impl will raise AttributeError if None


def test_sanitize_content_dict_recursive():
    dirty_dict = {
        "title": "Title with <script>alert(1)</script>",
        "details": {
            "description": "A <p>paragraph</p> with <iframe src='x'></iframe>.",
            "notes": ["Note 1 <object></object>", "Safe note"],
        },
        "count": 10,
    }
    expected_dict = {
        "title": "Title with ",
        "details": {
            "description": "A <p>paragraph</p> with .",
            "notes": ["Note 1 ", "Safe note"],
        },
        "count": 10,
    }
    # Note: The exact output of sanitize_html_content for tags like <object> is just removing them.
    # For <p> it's escaping.
    # Adjusting expected based on current sanitize_html_content behavior:
    expected_dict_adjusted = {
        "title": "Title with ",  # script tag removed
        "details": {
            "description": "A <p>paragraph</p> with .",  # iframe removed
            "notes": ["Note 1 ", "Safe note"],  # object removed
        },
        "count": 10,
    }
    assert sanitize_content_dict(dirty_dict) == expected_dict_adjusted


def test_calculate_readability_score():
    # These are simple heuristics, so exact scores are illustrative
    assert calculate_readability_score("Short simple text.") > 0.5  # Should be decent
    assert (
        calculate_readability_score(
            "This is a very long and convoluted sentence with many polysyllabic words causing obfuscation."
        )
        < 0.5
    )
    assert calculate_readability_score("") == 0.0
    assert calculate_readability_score("Too short") == 0.0  # len < 10


def test_check_content_structure_podcast():
    score, issues = check_content_structure(
        "Intro... main part... conclusion here.", "podcast_script"
    )
    assert score > 0.8  # Should be good
    assert not issues

    score_bad, issues_bad = check_content_structure("Only main part.", "podcast_script")
    assert "Missing introduction section" in issues_bad
    assert "Missing conclusion section" in issues_bad
    assert score_bad < 0.5


def test_check_content_structure_study_guide():
    score, issues = check_content_structure(
        "Overview... key concepts... summary.", "study_guide"
    )
    assert score > 0.8
    assert not issues

    score_bad, issues_bad = check_content_structure(
        "Only detailed content.", "study_guide"
    )
    assert "Missing overview section" in issues_bad
    assert score_bad < 0.5


def test_validate_content_length_requirements():
    valid_content = {
        "content_outline": {"overview": "o" * 200},
        "podcast_script": {
            "introduction": "i" * 100,
            "main_content": "m" * 800,
            "conclusion": "c" * 100,
        },
    }
    compliant, violations = validate_content_length_requirements(valid_content)
    assert compliant is True
    assert not violations

    invalid_content = {
        "content_outline": {"overview": "short"},  # Fails
        "podcast_script": {
            "introduction": "i",
            "main_content": "m",
            "conclusion": "c",
        },  # Fails
    }
    compliant, violations = validate_content_length_requirements(invalid_content)
    assert compliant is False
    assert len(violations) == 2
    assert "content_outline is 5 characters, minimum is 200" in violations[0]
    assert "podcast_script is 3 characters, minimum is 1000" in violations[1]


def test_validate_ai_content_dict_valid():
    # This function is an orchestrator, so we test its overall behavior
    # It calls sanitize, length checks, readability, structure.
    # For a "valid" case, ensure these sub-functions would pass.
    valid_ai_dict = {
        "podcast_script": {
            "title": "Valid Podcast",
            "introduction": "This is a valid introduction that is long enough for the podcast script. "
            * 2,
            "main_content": (
                "This is the main content of the podcast script. It needs to be very long. "
                * 20
            )
            + "End of main.",
            "conclusion": "This is a valid conclusion for the podcast script, also long enough. "
            * 2,
        },
        "study_guide": {
            "title": "Valid Study Guide",
            "overview": "Valid overview for the study guide, ensuring sufficient length. "
            * 3,
            "detailed_content": (
                "Detailed content for the study guide, must be very long. " * 15
            )
            + "End of details.",
            "summary": "Valid summary for the study guide, long enough. " * 3,
        }
        # Add other content types if their specific checks are implemented in validate_ai_content_dict
    }
    is_valid, qm, sanitized_dict = validate_ai_content_dict(valid_ai_dict)
    assert is_valid is True
    assert isinstance(qm, QualityMetrics)
    assert qm.overall_score > 0.7  # Expecting a good score
    assert qm.content_length_compliance is True
    assert not qm.validation_errors


def test_validate_ai_content_dict_invalid_due_to_length():
    invalid_ai_dict = {
        "podcast_script": {
            "title": "Short Podcast",
            "introduction": "Too short.",
            "main_content": "Way too short.",
            "conclusion": "Short.",
        }
    }
    is_valid, qm, _ = validate_ai_content_dict(invalid_ai_dict)
    assert is_valid is False
    assert qm.content_length_compliance is False
    assert any("podcast_script is" in err for err in qm.validation_errors)


def test_extract_text_from_content():
    assert extract_text_from_content("Simple string") == "Simple string"
    assert (
        extract_text_from_content({"key1": "value1", "key2": "value2"})
        == "value1 value2"
    )
    assert (
        extract_text_from_content(["item1", "item2", {"sub": "sub_value"}])
        == "item1 item2 sub_value"
    )
    assert (
        extract_text_from_content({"a": "1", "b": ["2", {"c": "3"}], "d": 4})
        == "1 2 3 4"
    )


def test_estimate_reading_time():
    assert estimate_reading_time("word " * 200) == 1.0  # 200 words / 200 wpm
    assert estimate_reading_time("word " * 400, wpm=200) == 2.0
    assert estimate_reading_time("") == 0.0


# --- Tests for app.utils.github_issues ---
from unittest.mock import MagicMock, patch

from app.utils import github_issues  # Import the module to patch its internals


@patch("app.utils.github_issues._make_github_request_with_retry")
def test_create_github_issue(mock_request):
    mock_response_data = {"id": 1, "title": "Test Issue", "body": "Test body"}
    mock_request.return_value = mock_response_data

    repo = "owner/repo"
    title = "Test Issue"
    body = "Test body"
    labels = ["bug", "critical"]

    result = github_issues.create_github_issue(repo, title, body, labels)

    expected_url = f"{github_issues.GITHUB_API_URL}/repos/{repo}/issues"
    expected_data = {
        "title": title,
        "body": body,
        "labels": labels,
        "assignees": [],  # Default
    }
    mock_request.assert_called_once_with("POST", expected_url, expected_data)
    assert result == mock_response_data


@patch("app.utils.github_issues._make_github_request_with_retry")
def test_create_github_issue_with_milestone_and_assignees(mock_request):
    mock_response_data = {"id": 2, "title": "Issue with Milestone"}
    mock_request.return_value = mock_response_data

    repo = "owner/repo"
    title = "Issue with Milestone"
    assignees = ["user1"]
    milestone_num = 5

    result = github_issues.create_github_issue(
        repo, title, assignees=assignees, milestone=milestone_num
    )

    expected_url = f"{github_issues.GITHUB_API_URL}/repos/{repo}/issues"
    expected_data = {
        "title": title,
        "body": "",  # Default
        "labels": [],  # Default
        "assignees": assignees,
        "milestone": milestone_num,
    }
    mock_request.assert_called_once_with("POST", expected_url, expected_data)
    assert result == mock_response_data


@patch("app.utils.github_issues._make_github_request_with_retry")
def test_close_github_issue(mock_request):
    mock_response_data = {"id": 1, "state": "closed"}
    mock_request.return_value = mock_response_data

    repo = "owner/repo"
    issue_number = 42

    result = github_issues.close_github_issue(repo, issue_number)

    expected_url = f"{github_issues.GITHUB_API_URL}/repos/{repo}/issues/{issue_number}"
    expected_data = {"state": "closed"}
    mock_request.assert_called_once_with("PATCH", expected_url, expected_data)
    assert result == mock_response_data


@patch("app.utils.github_issues._make_github_request_with_retry")
def test_add_comment_to_issue(mock_request):
    mock_response_data = {"id": 123, "body": "Test comment"}
    mock_request.return_value = mock_response_data

    repo = "owner/repo"
    issue_number = 42
    comment_text = "Test comment"

    result = github_issues.add_comment_to_issue(repo, issue_number, comment_text)

    expected_url = (
        f"{github_issues.GITHUB_API_URL}/repos/{repo}/issues/{issue_number}/comments"
    )
    expected_data = {"body": comment_text}
    mock_request.assert_called_once_with("POST", expected_url, expected_data)
    assert result == mock_response_data


# Test for _make_github_request_with_retry (more complex due to retries and actual requests.Session)
# This would typically involve mocking requests.post, requests.patch, requests.get
@patch("app.utils.github_issues.requests.post")
@patch("app.utils.github_issues.time.sleep")  # To avoid actual sleep during tests
def test_make_github_request_post_success(mock_sleep, mock_post):
    mock_response = MagicMock()
    mock_response.json.return_value = {"success": True}
    mock_response.raise_for_status = MagicMock()  # Does nothing if status is OK
    mock_post.return_value = mock_response

    url = "http://fakegithub.com/api/endpoint"
    data = {"key": "value"}

    result = github_issues._make_github_request_with_retry(
        "POST", url, data=data, max_retries=1
    )

    mock_post.assert_called_once()
    assert result == {"success": True}
    mock_sleep.assert_not_called()


@patch("app.utils.github_issues.requests.get")
@patch("app.utils.github_issues.time.sleep")
def test_make_github_request_get_network_timeout_then_success(mock_sleep, mock_get):
    mock_success_response = MagicMock()
    mock_success_response.json.return_value = {"data": "content"}
    mock_success_response.raise_for_status = MagicMock()

    # Simulate timeout on first call, success on second
    mock_get.side_effect = [
        requests.exceptions.ConnectTimeout("Connection timed out"),
        mock_success_response,
    ]

    url = "http://fakegithub.com/api/endpoint"
    result = github_issues._make_github_request_with_retry("GET", url, max_retries=2)

    assert mock_get.call_count == 2
    mock_sleep.assert_called_once_with(1)  # 2**0
    assert result == {"data": "content"}


@patch("app.utils.github_issues.requests.patch")
@patch("app.utils.github_issues.time.sleep")
def test_make_github_request_patch_rate_limit_then_success(mock_sleep, mock_patch):
    mock_rate_limit_response = MagicMock()
    mock_rate_limit_response.status_code = 429
    mock_rate_limit_response.raise_for_status.side_effect = (
        requests.exceptions.HTTPError(response=mock_rate_limit_response)
    )

    mock_success_response = MagicMock()
    mock_success_response.json.return_value = {"updated": True}
    mock_success_response.raise_for_status = MagicMock()

    mock_patch.side_effect = [
        mock_rate_limit_response,  # This will trigger raise_for_status with HTTPError
        mock_success_response,
    ]

    url = "http://fakegithub.com/api/endpoint"
    data = {"field": "new_value"}
    result = github_issues._make_github_request_with_retry(
        "PATCH", url, data=data, max_retries=2
    )

    assert mock_patch.call_count == 2
    mock_sleep.assert_called_once_with(60)  # Rate limit sleep
    assert result == {"updated": True}


@patch("app.utils.github_issues.requests.post")
@patch("app.utils.github_issues.time.sleep")
def test_make_github_request_all_retries_fail(mock_sleep, mock_post):
    mock_post.side_effect = requests.exceptions.ConnectTimeout("Connection timed out")

    url = "http://fakegithub.com/api/endpoint"
    with pytest.raises(requests.exceptions.ConnectTimeout):
        github_issues._make_github_request_with_retry(
            "POST", url, data={}, max_retries=3
        )

    assert mock_post.call_count == 3
    assert (
        mock_sleep.call_count == 2
    )  # Sleeps for attempt 0 and 1, fails on 2 (3rd attempt)
