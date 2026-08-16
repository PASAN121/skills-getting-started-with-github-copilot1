"""
Tests for the activities endpoint (GET /activities).
"""

import pytest


def test_get_activities_returns_all_activities(client, sample_activities):
    """Test that GET /activities returns all activities"""
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == len(sample_activities)


def test_get_activities_returns_correct_keys(client):
    """Test that each activity has all required fields"""
    # Arrange
    endpoint = "/activities"
    required_keys = ["description", "schedule", "max_participants", "participants"]
    
    # Act
    response = client.get(endpoint)
    data = response.json()
    
    # Assert
    for activity_name, activity_data in data.items():
        for key in required_keys:
            assert key in activity_data


def test_get_activities_participants_is_list(client):
    """Test that participants field is a list"""
    # Arrange
    endpoint = "/activities"
    
    # Act
    response = client.get(endpoint)
    data = response.json()
    
    # Assert
    for activity_name, activity_data in data.items():
        assert isinstance(activity_data["participants"], list)


def test_get_activities_contains_expected_activities(client):
    """Test that response contains expected activity names"""
    # Arrange
    endpoint = "/activities"
    expected_activities = [
        "Chess Club",
        "Programming Class",
        "Gym Class",
        "Basketball Team",
        "Track and Field",
        "Drama Club",
        "Art Studio",
        "Debate Team",
        "Science Club"
    ]
    
    # Act
    response = client.get(endpoint)
    data = response.json()
    
    # Assert
    for activity in expected_activities:
        assert activity in data


def test_get_activities_participants_have_emails(client):
    """Test that all participants are valid email strings"""
    # Arrange
    endpoint = "/activities"
    
    # Act
    response = client.get(endpoint)
    data = response.json()
    
    # Assert
    for activity_name, activity_data in data.items():
        for participant in activity_data["participants"]:
            assert isinstance(participant, str)
            assert "@" in participant


def test_get_activities_max_participants_is_positive_int(client):
    """Test that max_participants is a positive integer"""
    # Arrange
    endpoint = "/activities"
    
    # Act
    response = client.get(endpoint)
    data = response.json()
    
    # Assert
    for activity_name, activity_data in data.items():
        assert isinstance(activity_data["max_participants"], int)
        assert activity_data["max_participants"] > 0


def test_get_activities_participants_count_valid(client):
    """Test that participants count does not exceed max_participants"""
    # Arrange
    endpoint = "/activities"
    
    # Act
    response = client.get(endpoint)
    data = response.json()
    
    # Assert
    for activity_name, activity_data in data.items():
        assert len(activity_data["participants"]) <= activity_data["max_participants"]
