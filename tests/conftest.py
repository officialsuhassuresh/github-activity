import pytest
import os

@pytest.fixture(autouse=True)
def clean_environment():
    """Clean environment variables before each test."""
    original_environ = dict(os.environ)
    yield
    os.environ.clear()
    os.environ.update(original_environ) 