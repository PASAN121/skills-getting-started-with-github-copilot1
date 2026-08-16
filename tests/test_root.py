"""
Tests for the root endpoint (GET /).
"""

import pytest


def test_root_redirect(client):
    """Test that GET / redirects to /static/index.html"""
    # Arrange
    endpoint = "/"
    expected_status = 307
    expected_location = "/static/index.html"
    
    # Act
    response = client.get(endpoint, follow_redirects=False)
    
    # Assert
    assert response.status_code == expected_status
    assert response.headers["location"] == expected_location


def test_root_redirect_with_follow(client):
    """Test that GET / eventually serves the index page when following redirects"""
    # Arrange
    endpoint = "/"
    expected_status = 200
    
    # Act
    response = client.get(endpoint, follow_redirects=True)
    
    # Assert
    assert response.status_code == expected_status
