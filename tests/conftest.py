"""
Pytest configuration and shared fixtures for the test suite.
"""

import pytest
import copy
from fastapi.testclient import TestClient
from src.app import app, activities as original_activities


@pytest.fixture
def client(monkeypatch):
    """
    Fixture that provides a TestClient with isolated test data.
    Each test gets a fresh copy of activities to prevent state leakage.
    """
    # Create a deep copy of the original activities
    test_activities = copy.deepcopy(original_activities)
    
    # Monkeypatch the global activities dict in the app module
    monkeypatch.setattr("src.app.activities", test_activities)
    
    # Return the TestClient
    return TestClient(app)


@pytest.fixture
def sample_activities():
    """
    Fixture that provides a fresh copy of the original activities data.
    Useful for test assertions and setup.
    """
    return copy.deepcopy(original_activities)
