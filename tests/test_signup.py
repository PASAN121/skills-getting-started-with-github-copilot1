"""
Tests for the signup endpoint (POST /activities/{activity_name}/signup).
"""

import pytest


class TestSignupHappyPath:
    """Happy path tests for signup functionality"""
    
    def test_signup_adds_participant(self, client):
        """Test that a valid signup adds the participant to the activity"""
        # Arrange
        activity_name = "Chess Club"
        email = "newstudent@mergington.edu"
        expected_status = 200
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        data = response.json()
        
        # Assert
        assert response.status_code == expected_status
        assert "message" in data
        assert email in data["message"]
        assert activity_name in data["message"]
    
    def test_signup_increases_participant_count(self, client):
        """Test that signup increases the participant count in the activity"""
        # Arrange
        activity_name = "Chess Club"
        email = "newstudent@mergington.edu"
        response_initial = client.get("/activities")
        initial_count = len(response_initial.json()[activity_name]["participants"])
        expected_count_after = initial_count + 1
        
        # Act
        client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        response_updated = client.get("/activities")
        updated_count = len(response_updated.json()[activity_name]["participants"])
        
        # Assert
        assert updated_count == expected_count_after
    
    def test_signup_email_appears_in_participants(self, client):
        """Test that the signed-up email appears in the participants list"""
        # Arrange
        activity_name = "Chess Club"
        email = "newstudent@mergington.edu"
        
        # Act
        client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        response = client.get("/activities")
        participants = response.json()[activity_name]["participants"]
        
        # Assert
        assert email in participants
    
    def test_signup_decreases_available_spots(self, client):
        """Test that signup decreases the number of available spots"""
        # Arrange
        activity_name = "Chess Club"
        email = "newstudent@mergington.edu"
        response_initial = client.get("/activities")
        initial_activity = response_initial.json()[activity_name]
        initial_spots = initial_activity["max_participants"] - len(initial_activity["participants"])
        expected_spots_after = initial_spots - 1
        
        # Act
        client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        response_updated = client.get("/activities")
        updated_activity = response_updated.json()[activity_name]
        updated_spots = updated_activity["max_participants"] - len(updated_activity["participants"])
        
        # Assert
        assert updated_spots == expected_spots_after


class TestSignupErrorCases:
    """Error case tests for signup functionality"""
    
    def test_signup_nonexistent_activity_returns_404(self, client):
        """Test that signing up for non-existent activity returns 404"""
        # Arrange
        activity_name = "Nonexistent Club"
        email = "student@mergington.edu"
        expected_status = 404
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == expected_status
        assert "not found" in response.json()["detail"].lower()
    
    def test_signup_already_registered_returns_400(self, client):
        """Test that signing up for an activity twice returns 400"""
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # Existing participant
        expected_status = 400
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == expected_status
        assert "already signed up" in response.json()["detail"].lower()
    
    def test_signup_duplicate_attempt_fails(self, client):
        """Test that attempting to signup twice fails on second attempt"""
        # Arrange
        activity_name = "Art Studio"
        email = "testduplicate@mergington.edu"
        expected_success = 200
        expected_failure = 400
        
        # Act & Assert - First signup succeeds
        response1 = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        assert response1.status_code == expected_success
        
        # Act & Assert - Second signup fails
        response2 = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        assert response2.status_code == expected_failure


class TestSignupEdgeCases:
    """Edge case tests for signup functionality"""
    
    def test_signup_multiple_students_same_activity(self, client):
        """Test that multiple different students can sign up for the same activity"""
        # Arrange
        activity_name = "Drama Club"
        emails = [
            "student1@mergington.edu",
            "student2@mergington.edu",
            "student3@mergington.edu"
        ]
        expected_status = 200
        
        # Act - Sign up each student
        for email in emails:
            response = client.post(
                f"/activities/{activity_name}/signup",
                params={"email": email}
            )
            assert response.status_code == expected_status
        
        # Assert - Verify all are in the activity
        response = client.get("/activities")
        participants = response.json()[activity_name]["participants"]
        for email in emails:
            assert email in participants
    
    def test_signup_same_student_different_activities(self, client):
        """Test that the same student can sign up for multiple different activities"""
        # Arrange
        email = "versatile@mergington.edu"
        activities = ["Debate Team", "Science Club"]
        expected_status = 200
        
        # Act - Sign up student for each activity
        for activity_name in activities:
            response = client.post(
                f"/activities/{activity_name}/signup",
                params={"email": email}
            )
            assert response.status_code == expected_status
        
        # Assert - Verify student is in all activities
        response = client.get("/activities")
        data = response.json()
        for activity_name in activities:
            assert email in data[activity_name]["participants"]
    
    def test_signup_url_encoded_activity_name(self, client):
        """Test that activity names with spaces are properly handled"""
        # Arrange
        activity_name = "Basketball Team"
        email = "baller@mergington.edu"
        expected_status = 200
        
        # Act - Sign up with activity name containing spaces
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert - Verify signup worked
        assert response.status_code == expected_status
        response_final = client.get("/activities")
        assert email in response_final.json()[activity_name]["participants"]
