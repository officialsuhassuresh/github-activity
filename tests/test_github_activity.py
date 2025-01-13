import pytest
from unittest.mock import patch, MagicMock
import urllib.error
import json
import os
from github_activity.github_activity import (
    fetch_github_events,
    format_event,
    get_auth_headers,
    GitHubActivity
)

# Test Data
@pytest.fixture
def sample_push_event():
    return {
        'type': 'PushEvent',
        'repo': {'name': 'test/repo'},
        'created_at': '2024-03-20T12:00:00Z',
        'payload': {
            'commits': [{'sha': '123'}, {'sha': '456'}]
        }
    }

@pytest.fixture
def sample_issue_event():
    return {
        'type': 'IssuesEvent',
        'repo': {'name': 'test/repo'},
        'created_at': '2024-03-20T12:00:00Z',
        'payload': {
            'action': 'opened',
            'issue': {'number': 123}
        }
    }

# Authentication Tests
def test_get_auth_headers_with_valid_env_vars():
    with patch.dict(os.environ, {'USERNAME': 'test', 'GITHUB_TOKEN': 'token123'}):
        headers = get_auth_headers()
        assert 'Authorization' in headers
        assert headers['Accept'] == 'application/vnd.github.v3+json'

def test_get_auth_headers_with_missing_env_vars():
    with patch.dict(os.environ, {}, clear=True):
        with pytest.raises(ValueError) as exc_info:
            get_auth_headers()
        assert "Missing required environment variables" in str(exc_info.value)

# API Fetch Tests
def test_fetch_github_events_success():
    mock_response = MagicMock()
    mock_response.read.return_value = json.dumps([{'type': 'PushEvent'}]).encode()
    mock_response.__enter__.return_value = mock_response
    
    with patch('urllib.request.urlopen', return_value=mock_response):
        events = fetch_github_events('testuser')
        assert len(events) == 1
        assert events[0]['type'] == 'PushEvent'

def test_fetch_github_events_user_not_found():
    with patch('urllib.request.urlopen') as mock_urlopen:
        mock_urlopen.side_effect = urllib.error.HTTPError(
            'url', 404, 'Not Found', {}, None
        )
        with pytest.raises(ValueError) as exc_info:
            fetch_github_events('nonexistentuser')
        assert "not found" in str(exc_info.value)

def test_fetch_github_events_rate_limit():
    with patch('urllib.request.urlopen') as mock_urlopen:
        mock_urlopen.side_effect = urllib.error.HTTPError(
            'url', 403, 'Rate Limit', {}, None
        )
        with pytest.raises(ValueError) as exc_info:
            fetch_github_events('testuser')
        assert "rate limit" in str(exc_info.value).lower()

# Event Formatting Tests
def test_format_push_event(sample_push_event):
    result = format_event(sample_push_event)
    assert "Pushed 2 commit(s)" in result
    assert "test/repo" in result

def test_format_issue_event(sample_issue_event):
    result = format_event(sample_issue_event)
    assert "Opened issue #123" in result
    assert "test/repo" in result

def test_format_unsupported_event():
    event = {
        'type': 'UnsupportedEvent',
        'repo': {'name': 'test/repo'},
        'created_at': '2024-03-20T12:00:00Z'
    }
    assert format_event(event) is None

# Integration Tests
def test_github_activity_show_success():
    mock_events = [
        {
            'type': 'PushEvent',
            'repo': {'name': 'test/repo'},
            'created_at': '2024-03-20T12:00:00Z',
            'payload': {'commits': [{'sha': '123'}]}
        }
    ]
    
    with patch('github_activity.github_activity.fetch_github_events', return_value=mock_events):
        activity = GitHubActivity()
        activity.show('testuser')

def test_github_activity_show_no_events():
    with patch('github_activity.github_activity.fetch_github_events', return_value=[]):
        activity = GitHubActivity()
        activity.show('testuser') 