import pytest
import json
from app.models.board import Board
from app.models.card import Card


class TestDeleteCard:
    """Test DELETE /cards/<card_id> endpoint."""
    
    def test_delete_card_success(self, client, sample_card):
        """Test deleting a card successfully."""
        card_id = sample_card["id"]
        
        response = client.delete(f"/cards/{card_id}")
        
        assert response.status_code == 200
        data = response.get_json()
        assert "message" in data
        assert f"Card {card_id} deleted successfully" in data["message"]
    
    def test_delete_nonexistent_card(self, client):
        """Test deleting a card that doesn't exist."""
        response = client.delete("/cards/999")
        
        assert response.status_code == 404
        data = response.get_json()
        assert "message" in data
        assert "not found" in data["message"].lower()
    
    def test_delete_card_with_invalid_id(self, client):
        """Test deleting a card with invalid ID format."""
        response = client.delete("/cards/invalid")
        
        assert response.status_code == 400
        data = response.get_json()
        assert "message" in data
        assert "invalid" in data["message"].lower()
    
    def test_delete_card_verification(self, client, sample_board):
        """Test that card is actually deleted from database."""
        # Create a card first
        card_data = {
            "message": "Card to delete",
            "board_id": sample_board["id"]
        }
        
        create_response = client.post(
            f"/boards/{sample_board['id']}/cards",
            data=json.dumps(card_data),
            content_type="application/json"
        )
        assert create_response.status_code == 201
        
        card_id = create_response.get_json()["id"]
        
        # Delete the card
        delete_response = client.delete(f"/cards/{card_id}")
        assert delete_response.status_code == 200
        
        # Verify card is deleted by trying to get it
        get_response = client.get(f"/boards/{sample_board['id']}/cards")
        assert get_response.status_code == 200
        cards = get_response.get_json()
        
        # The card should not be in the list
        card_ids = [card["id"] for card in cards]
        assert card_id not in card_ids


class TestUpdateCardLikes:
    """Test PUT /cards/<card_id> endpoint."""
    
    def test_update_card_likes_success(self, client, sample_card):
        """Test updating card likes successfully."""
        card_id = sample_card["id"]
        initial_likes = sample_card["likes_count"]
        
        response = client.put(f"/cards/{card_id}")
        
        assert response.status_code == 200
        data = response.get_json()
        assert data["id"] == card_id
        assert data["likes_count"] == initial_likes + 1
        assert data["message"] == sample_card["message"]
        assert data["board_id"] == sample_card["board_id"]
    
    def test_update_card_likes_multiple_times(self, client, sample_card):
        """Test updating card likes multiple times."""
        card_id = sample_card["id"]
        initial_likes = sample_card["likes_count"]
        
        # First update
        response1 = client.put(f"/cards/{card_id}")
        assert response1.status_code == 200
        data1 = response1.get_json()
        assert data1["likes_count"] == initial_likes + 1
        
        # Second update
        response2 = client.put(f"/cards/{card_id}")
        assert response2.status_code == 200
        data2 = response2.get_json()
        assert data2["likes_count"] == initial_likes + 2
        
        # Third update
        response3 = client.put(f"/cards/{card_id}")
        assert response3.status_code == 200
        data3 = response3.get_json()
        assert data3["likes_count"] == initial_likes + 3
    
    def test_update_nonexistent_card_likes(self, client):
        """Test updating likes for a card that doesn't exist."""
        response = client.put("/cards/999")
        
        assert response.status_code == 404
        data = response.get_json()
        assert "message" in data
        assert "not found" in data["message"].lower()
    
    def test_update_card_likes_with_invalid_id(self, client):
        """Test updating likes with invalid ID format."""
        response = client.put("/cards/invalid")
        
        assert response.status_code == 400
        data = response.get_json()
        assert "message" in data
        assert "invalid" in data["message"].lower()
    
    def test_update_card_likes_persistence(self, client, sample_board):
        """Test that likes update persists in database."""
        # Create a card with 0 likes
        card_data = {
            "message": "Test card for likes",
            "likes_count": 0,
            "board_id": sample_board["id"]
        }
        
        create_response = client.post(
            f"/boards/{sample_board['id']}/cards",
            data=json.dumps(card_data),
            content_type="application/json"
        )
        assert create_response.status_code == 201
        
        card_id = create_response.get_json()["id"]
        
        # Update likes
        update_response = client.put(f"/cards/{card_id}")
        assert update_response.status_code == 200
        assert update_response.get_json()["likes_count"] == 1
        
        # Verify persistence by getting board cards
        get_response = client.get(f"/boards/{sample_board['id']}/cards")
        assert get_response.status_code == 200
        cards = get_response.get_json()
        
        # Find our card and verify likes count
        our_card = next((card for card in cards if card["id"] == card_id), None)
        assert our_card is not None
        assert our_card["likes_count"] == 1


class TestCardRoutesIntegration:
    """Integration tests for card routes."""
    
    def test_card_lifecycle(self, client, sample_board):
        """Test complete card lifecycle: create, update likes, delete."""
        # 1. Create a card
        card_data = {
            "message": "Integration test card",
            "board_id": sample_board["id"]
        }
        
        create_response = client.post(
            f"/boards/{sample_board['id']}/cards",
            data=json.dumps(card_data),
            content_type="application/json"
        )
        assert create_response.status_code == 201
        
        card_response = create_response.get_json()
        card_id = card_response["id"]
        assert card_response["message"] == "Integration test card"
        assert card_response["likes_count"] == 0
        
        # 2. Update likes multiple times
        for i in range(3):
            update_response = client.put(f"/cards/{card_id}")
            assert update_response.status_code == 200
            data = update_response.get_json()
            assert data["likes_count"] == i + 1
        
        # 3. Verify final likes count
        get_response = client.get(f"/boards/{sample_board['id']}/cards")
        assert get_response.status_code == 200
        cards = get_response.get_json()
        
        our_card = next((card for card in cards if card["id"] == card_id), None)
        assert our_card is not None
        assert our_card["likes_count"] == 3
        
        # 4. Delete the card
        delete_response = client.delete(f"/cards/{card_id}")
        assert delete_response.status_code == 200
        
        # 5. Verify deletion
        get_response_after_delete = client.get(f"/boards/{sample_board['id']}/cards")
        assert get_response_after_delete.status_code == 200
        cards_after_delete = get_response_after_delete.get_json()
        
        card_ids_after_delete = [card["id"] for card in cards_after_delete]
        assert card_id not in card_ids_after_delete
    
    def test_multiple_cards_likes_management(self, client, sample_board):
        """Test managing likes for multiple cards."""
        # Create multiple cards
        cards = []
        for i in range(3):
            card_data = {
                "message": f"Card {i+1}",
                "board_id": sample_board["id"]
            }
            
            response = client.post(
                f"/boards/{sample_board['id']}/cards",
                data=json.dumps(card_data),
                content_type="application/json"
            )
            assert response.status_code == 201
            cards.append(response.get_json())
        
        # Update likes for each card differently
        for i, card in enumerate(cards):
            for _ in range(i + 1):  # Card 1 gets 1 like, Card 2 gets 2 likes, etc.
                response = client.put(f"/cards/{card['id']}")
                assert response.status_code == 200
        
        # Verify all cards have correct likes
        get_response = client.get(f"/boards/{sample_board['id']}/cards")
        assert get_response.status_code == 200
        all_cards = get_response.get_json()
        
        for i, card in enumerate(cards):
            found_card = next((c for c in all_cards if c["id"] == card["id"]), None)
            assert found_card is not None
            assert found_card["likes_count"] == i + 1
    
    def test_card_operations_with_different_boards(self, client, multiple_boards):
        """Test card operations across different boards."""
        # Create cards for different boards
        cards_by_board = {}
        
        for i, board in enumerate(multiple_boards):
            card_data = {
                "message": f"Card for board {i+1}",
                "board_id": board["id"]
            }
            
            response = client.post(
                f"/boards/{board['id']}/cards",
                data=json.dumps(card_data),
                content_type="application/json"
            )
            assert response.status_code == 201
            cards_by_board[board["id"]] = response.get_json()
        
        # Update likes for each card
        for board_id, card in cards_by_board.items():
            response = client.put(f"/cards/{card['id']}")
            assert response.status_code == 200
            assert response.get_json()["likes_count"] == 1
        
        # Verify each board has its own cards with correct likes
        for board_id, card in cards_by_board.items():
            get_response = client.get(f"/boards/{board_id}/cards")
            assert get_response.status_code == 200
            board_cards = get_response.get_json()
            
            # Each board should have exactly one card
            assert len(board_cards) == 1
            assert board_cards[0]["id"] == card["id"]
            assert board_cards[0]["likes_count"] == 1


class TestCardRoutesErrorHandling:
    """Test error handling in card routes."""
    
    def test_delete_card_twice(self, client, sample_card):
        """Test deleting the same card twice."""
        card_id = sample_card["id"]
        
        # First deletion should succeed
        response1 = client.delete(f"/cards/{card_id}")
        assert response1.status_code == 200
        
        # Second deletion should fail
        response2 = client.delete(f"/cards/{card_id}")
        assert response2.status_code == 404
    
    def test_update_likes_for_deleted_card(self, client, sample_card):
        """Test updating likes for a deleted card."""
        card_id = sample_card["id"]
        
        # Delete the card first
        delete_response = client.delete(f"/cards/{card_id}")
        assert delete_response.status_code == 200
        
        # Try to update likes for deleted card
        update_response = client.put(f"/cards/{card_id}")
        assert update_response.status_code == 404
    
    def test_card_operations_with_malformed_ids(self, client):
        """Test card operations with various malformed IDs."""
        # These IDs should return 400 (Bad Request) because they're not valid integers
        malformed_ids = ["abc123", "invalid", "card", "test", "", "1.5", "1e10"]
    
        for malformed_id in malformed_ids:
            # Test delete
            delete_response = client.delete(f"/cards/{malformed_id}")
            if malformed_id == "":
                # Flask routing: /cards/ does not match /cards/<card_id>
                assert delete_response.status_code == 404, f"Expected 404 for empty ID, got {delete_response.status_code}"
            else:
                assert delete_response.status_code == 400, f"Expected 400 for malformed ID '{malformed_id}', got {delete_response.status_code}"
    
    def test_card_operations_with_nonexistent_ids(self, client):
        """Test card operations with valid but nonexistent IDs."""
        # These are valid integers but don't exist in the database
        nonexistent_ids = ["0", "-1", "999", "999999"]
        
        for nonexistent_id in nonexistent_ids:
            # Test delete
            delete_response = client.delete(f"/cards/{nonexistent_id}")
            assert delete_response.status_code == 404
            
            # Test update likes
            update_response = client.put(f"/cards/{nonexistent_id}")
            assert update_response.status_code == 404
    
    def test_card_operations_with_very_large_ids(self, client):
        """Test card operations with very large ID values."""
        large_ids = ["999999999999999999999", "9223372036854775807"]  # Max int64
        
        for large_id in large_ids:
            # Test delete
            delete_response = client.delete(f"/cards/{large_id}")
            assert delete_response.status_code == 404  # Should be 404, not 400
            
            # Test update likes
            update_response = client.put(f"/cards/{large_id}")
            assert update_response.status_code == 404  # Should be 404, not 400
