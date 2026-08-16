"""
Tests for the remove participant endpoint (DELETE /activities/{activity_name}/participants/{email}).
"""

import pytest


class TestRemoveParticipantHappyPath:
    """Happy path tests for remove participant functionality"""
    
    def test_remove_participant_removes_from_activity(self, client):
        """Test that removing a participant deletes them from the activity"""
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"
        expected_status = 200
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/participants/{email}"
        )
        data = response.json()
        
        # Assert
        assert response.status_code == expected_status
        assert "message" in data
        assert "removed" in data["message"].lower()
    
    def test_remove_participant_decreases_count(self, client):
        """Test that removing a participant decreases the participant count"""
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"
        response_initial = client.get("/activities")
        initial_count = len(response_initial.json()[activity_name]["participants"])
        expected_count_after = initial_count - 1
        
        # Act
        client.delete(
            f"/activities/{activity_name}/participants/{email}"
        )
        response_updated = client.get("/activities")
        updated_count = len(response_updated.json()[activity_name]["participants"])
        
        # Assert
        assert updated_count == expected_count_after
    
    def test_remove_participant_email_not_in_list(self, client):
        """Test that removed email is no longer in the participants list"""
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"
        
        # Act
        client.delete(
            f"/activities/{activity_name}/participants/{email}"
        )
        response = client.get("/activities")
        participants = response.json()[activity_name]["participants"]
        
        # Assert
        assert email not in participants
    
    def test_remove_participant_increases_available_spots(self, client):
        """Test that removing a participant increases available spots"""
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"
        response_initial = client.get("/activities")
        initial_activity = response_initial.json()[activity_name]
        initial_spots = initial_activity["max_participants"] - len(initial_activity["participants"])
        expected_spots_after = initial_spots + 1
        
        # Act
        client.delete(
            f"/activities/{activity_name}/participants/{email}"
        )
        response_updated = client.get("/activities")
        updated_activity = response_updated.json()[activity_name]
        updated_spots = updated_activity["max_participants"] - len(updated_activity["participants"])
        
        # Assert
        assert updated_spots == expected_spots_after
    
    def test_remove_participant_others_remain(self, client):
        """Test that removing one participant doesn't affect others in the same activity"""
        # Arrange
        activity_name = "Chess Club"
        email_to_remove = "michael@mergington.edu"
        response_before = client.get("/activities")
        participants_before = response_before.json()[activity_name]["participants"].copy()
        
        # Act
        client.delete(
            f"/activities/{activity_name}/participants/{email_to_remove}"
        )
        response_after = client.get("/activities")
        participants_after = response_after.json()[activity_name]["participants"]
        
        # Assert - All others should still be there
        for participant in participants_before:
            if participant != email_to_remove:
                assert participant in participants_after


class TestRemoveParticipantErrorCases:
    """Error case tests for remove participant functionality"""
    
    def test_remove_nonexistent_activity_returns_404(self, client):
        """Test that removing from non-existent activity returns 404"""
        # Arrange
        activity_name = "Nonexistent Club"
        email = "student@mergington.edu"
        expected_status = 404
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/participants/{email}"
        )
        
        # Assert
        assert response.status_code == expected_status
        assert "not found" in response.json()["detail"].lower()
    
    def test_remove_nonexistent_participant_returns_404(self, client):
        """Test that removing non-existent participant returns 404"""
        # Arrange
        activity_name = "Chess Club"
        email = "nonexistent@mergington.edu"
        expected_status = 404
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/participants/{email}"
        )
        
        # Assert
        assert response.status_code == expected_status
        assert "not found" in response.json()["detail"].lower()
    
    def test_remove_participant_twice_returns_404(self, client):
        """Test that removing the same participant twice fails on second attempt"""
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"
        expected_success = 200
        expected_failure = 404
        
        # Act & Assert - First removal succeeds
        response1 = client.delete(
            f"/activities/{activity_name}/participants/{email}"
        )
        assert response1.status_code == expected_success
        
        # Act & Assert - Second removal fails
        response2 = client.delete(
            f"/activities/{activity_name}/participants/{email}"
        )
        assert response2.status_code == expected_failure


class TestRemoveParticipantEdgeCases:
    """Edge case tests for remove participant functionality"""
    
    def test_remove_last_participant_from_activity(self, client):
        """Test removing the last participant from an activity"""
        # Arrange
        activity_name = "Debate Team"
        email = "isabella@mergington.edu"
        expected_deletion_status = 200
        expected_final_count = 0
        
        # Verify initial state (should have 1 participant)
        response_initial = client.get("/activities")
        initial_participants = response_initial.json()[activity_name]["participants"]
        assert len(initial_participants) == 1
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/participants/{email}"
        )
        
        # Assert
        assert response.status_code == expected_deletion_status
        response_final = client.get("/activities")
        final_participants = response_final.json()[activity_name]["participants"]
        assert len(final_participants) == expected_final_count
    
    def test_remove_multiple_participants_sequentially(self, client):
        """Test removing multiple participants from the same activity"""
        # Arrange
        activity_name = "Chess Club"
        emails_to_remove = ["michael@mergington.edu", "daniel@mergington.edu"]
        expected_status = 200
        
        # Act - Remove each participant
        for email in emails_to_remove:
            response = client.delete(
                f"/activities/{activity_name}/participants/{email}"
            )
            assert response.status_code == expected_status
        
        # Assert - Verify all are removed
        response = client.get("/activities")
        participants = response.json()[activity_name]["participants"]
        for email in emails_to_remove:
            assert email not in participants
    
    def test_remove_participant_url_encoded_activity_name(self, client):
        """Test that activity names with spaces are properly handled in deletion"""
        # Arrange
        activity_name = "Programming Class"
        email = "emma@mergington.edu"
        expected_status = 200
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/participants/{email}"
        )
        
        # Assert
        assert response.status_code == expected_status
        response_verify = client.get("/activities")
        assert email not in response_verify.json()[activity_name]["participants"]
