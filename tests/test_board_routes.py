import pytest
import json
from app.models.board import Board
from app.models.card import Card


class TestGetAllBoards:
    """Test GET /boards endpoint."""
    
    def test_get_all_boards_empty(self, client):
        """Test getting all boards when none exist."""
        response = client.get("/boards")
        
        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, list)
        assert len(data) == 0
    
    def test_get_all_boards_with_data(self, client, multiple_boards):
        """Test getting all boards when boards exist."""
        response = client.get("/boards")
        
        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, list)
        assert len(data) == 3
        
        # Verify board data structure
        for board in data:
            assert "id" in board
            assert "title" in board
            assert "owner" in board
            assert isinstance(board["id"], int)
            assert isinstance(board["title"], str)
            assert isinstance(board["owner"], str)


class TestGetOneBoard:
    """Test GET /boards/<board_id> endpoint."""
    
    def test_get_existing_board(self, client, sample_board):
        """Test getting an existing board."""
        response = client.get(f"/boards/{sample_board['id']}")
        
        assert response.status_code == 200
        data = response.get_json()
        assert data["id"] == sample_board["id"]
        assert data["title"] == sample_board["title"]
        assert data["owner"] == sample_board["owner"]
    
    def test_get_nonexistent_board(self, client):
        """Test getting a board that doesn't exist."""
        response = client.get("/boards/999")
        
        assert response.status_code == 404
        data = response.get_json()
        assert "message" in data
        assert "not found" in data["message"].lower()
    
    def test_get_board_with_invalid_id(self, client):
        """Test getting a board with invalid ID format."""
        response = client.get("/boards/invalid")
        
        assert response.status_code == 400
        data = response.get_json()
        assert "message" in data
        assert "invalid" in data["message"].lower()


class TestCreateBoard:
    """Test POST /boards endpoint."""
    
    def test_create_board_success(self, client):
        """Test creating a board successfully."""
        board_data = {
            "title": "New Test Board",
            "owner": "test_user"
        }
        
        response = client.post(
            "/boards",
            data=json.dumps(board_data),
            content_type="application/json"
        )
        
        assert response.status_code == 201
        data = response.get_json()
        assert data["title"] == "New Test Board"
        assert data["owner"] == "test_user"
        assert "id" in data
        assert isinstance(data["id"], int)
    
    def test_create_board_missing_title(self, client):
        """Test creating a board with missing title."""
        board_data = {
            "owner": "test_user"
        }
        
        response = client.post(
            "/boards",
            data=json.dumps(board_data),
            content_type="application/json"
        )
        
        assert response.status_code == 400
        data = response.get_json()
        assert "message" in data
        assert "invalid data" in data["message"].lower()
    
    def test_create_board_missing_owner(self, client):
        """Test creating a board with missing owner."""
        board_data = {
            "title": "New Test Board"
        }
        
        response = client.post(
            "/boards",
            data=json.dumps(board_data),
            content_type="application/json"
        )
        
        assert response.status_code == 400
        data = response.get_json()
        assert "message" in data
        assert "invalid data" in data["message"].lower()
    
    def test_create_board_empty_data(self, client):
        """Test creating a board with empty data."""
        response = client.post(
            "/boards",
            data=json.dumps({}),
            content_type="application/json"
        )
        
        assert response.status_code == 400
        data = response.get_json()
        assert "message" in data
        assert "invalid data" in data["message"].lower()
    
    def test_create_board_invalid_json(self, client):
        """Test creating a board with invalid JSON."""
        response = client.post(
            "/boards",
            data="invalid json",
            content_type="application/json"
        )
        
        assert response.status_code == 400


class TestCreateCard:
    """Test POST /boards/<board_id>/cards endpoint."""
    
    def test_create_card_success(self, client, sample_board):
        """Test creating a card successfully."""
        card_data = {
            "message": "New test card",
            "board_id": sample_board["id"]
        }
        
        response = client.post(
            f"/boards/{sample_board['id']}/cards",
            data=json.dumps(card_data),
            content_type="application/json"
        )
        
        assert response.status_code == 201
        data = response.get_json()
        assert data["message"] == "New test card"
        assert data["board_id"] == sample_board["id"]
        assert data["likes_count"] == 0  # Default value
        assert "id" in data
        assert isinstance(data["id"], int)
    
    def test_create_card_with_likes(self, client, sample_board):
        """Test creating a card with specified likes count."""
        card_data = {
            "message": "New test card",
            "likes_count": 5,
            "board_id": sample_board["id"]
        }
        
        response = client.post(
            f"/boards/{sample_board['id']}/cards",
            data=json.dumps(card_data),
            content_type="application/json"
        )
        
        assert response.status_code == 201
        data = response.get_json()
        assert data["message"] == "New test card"
        assert data["likes_count"] == 5
        assert data["board_id"] == sample_board["id"]
    
    def test_create_card_nonexistent_board(self, client):
        """Test creating a card for a board that doesn't exist."""
        card_data = {
            "message": "New test card",
            "board_id": 999
        }
        
        response = client.post(
            "/boards/999/cards",
            data=json.dumps(card_data),
            content_type="application/json"
        )
        
        assert response.status_code == 404
        data = response.get_json()
        assert "message" in data
        assert "not found" in data["message"].lower()
    
    def test_create_card_invalid_board_id(self, client):
        """Test creating a card with invalid board ID format."""
        card_data = {
            "message": "New test card",
            "board_id": 1
        }
        
        response = client.post(
            "/boards/invalid/cards",
            data=json.dumps(card_data),
            content_type="application/json"
        )
        
        assert response.status_code == 400
        data = response.get_json()
        assert "message" in data
        assert "invalid" in data["message"].lower()
    
    def test_create_card_missing_message(self, client, sample_board):
        """Test creating a card with missing message."""
        card_data = {
            "board_id": sample_board["id"]
        }
        
        response = client.post(
            f"/boards/{sample_board['id']}/cards",
            data=json.dumps(card_data),
            content_type="application/json"
        )
        
        assert response.status_code == 400
        data = response.get_json()
        assert "message" in data
        assert "invalid data" in data["message"].lower()
    
    def test_create_card_missing_board_id(self, client, sample_board):
        """Test creating a card with missing board_id in data."""
        card_data = {
            "message": "New test card"
        }
        
        response = client.post(
            f"/boards/{sample_board['id']}/cards",
            data=json.dumps(card_data),
            content_type="application/json"
        )
        
        assert response.status_code == 400
        data = response.get_json()
        assert "message" in data
        assert "invalid data" in data["message"].lower()


class TestGetBoardCards:
    """Test GET /boards/<board_id>/cards endpoint."""
    
    def test_get_board_cards_empty(self, client, sample_board):
        """Test getting cards for a board with no cards."""
        response = client.get(f"/boards/{sample_board['id']}/cards")
        
        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, list)
        assert len(data) == 0
    
    def test_get_board_cards_with_data(self, client, sample_board):
        """Test getting cards for a board with cards."""
        # Create some cards for the board
        card1 = Card(message="Card 1", board_id=sample_board["id"])
        card2 = Card(message="Card 2", board_id=sample_board["id"])
        card3 = Card(message="Card 3", board_id=sample_board["id"])
        
        from app.db import db
        db.session.add_all([card1, card2, card3])
        db.session.commit()
        
        response = client.get(f"/boards/{sample_board['id']}/cards")
        
        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, list)
        assert len(data) == 3
        
        # Verify card data structure
        for card in data:
            assert "id" in card
            assert "message" in card
            assert "likes_count" in card
            assert "board_id" in card
            assert isinstance(card["id"], int)
            assert isinstance(card["message"], str)
            assert isinstance(card["likes_count"], int)
            assert isinstance(card["board_id"], int)
    
    def test_get_board_cards_nonexistent_board(self, client):
        """Test getting cards for a board that doesn't exist."""
        response = client.get("/boards/999/cards")
        
        assert response.status_code == 404
        data = response.get_json()
        assert "message" in data
        assert "not found" in data["message"].lower()
    
    def test_get_board_cards_invalid_board_id(self, client):
        """Test getting cards with invalid board ID format."""
        response = client.get("/boards/invalid/cards")
        
        assert response.status_code == 400
        data = response.get_json()
        assert "message" in data
        assert "invalid" in data["message"].lower()


class TestBoardRoutesIntegration:
    """Integration tests for board routes."""
    
    def test_full_board_workflow(self, client):
        """Test complete workflow: create board, add cards, retrieve all."""
        # 1. Create a board
        board_data = {
            "title": "Integration Test Board",
            "owner": "integration_user"
        }
        
        response = client.post(
            "/boards",
            data=json.dumps(board_data),
            content_type="application/json"
        )
        assert response.status_code == 201
        board_response = response.get_json()
        board_id = board_response["id"]
        
        # 2. Add cards to the board
        card_data1 = {
            "message": "First card",
            "board_id": board_id
        }
        card_data2 = {
            "message": "Second card",
            "likes_count": 3,
            "board_id": board_id
        }
        
        response1 = client.post(
            f"/boards/{board_id}/cards",
            data=json.dumps(card_data1),
            content_type="application/json"
        )
        assert response1.status_code == 201
        
        response2 = client.post(
            f"/boards/{board_id}/cards",
            data=json.dumps(card_data2),
            content_type="application/json"
        )
        assert response2.status_code == 201
        
        # 3. Get the board
        response = client.get(f"/boards/{board_id}")
        assert response.status_code == 200
        board_data = response.get_json()
        assert board_data["title"] == "Integration Test Board"
        assert board_data["owner"] == "integration_user"
        
        # 4. Get board cards
        response = client.get(f"/boards/{board_id}/cards")
        assert response.status_code == 200
        cards_data = response.get_json()
        assert len(cards_data) == 2
        
        # 5. Get all boards
        response = client.get("/boards")
        assert response.status_code == 200
        all_boards = response.get_json()
        assert len(all_boards) >= 1
        
        # Find our board in the list
        our_board = next((b for b in all_boards if b["id"] == board_id), None)
        assert our_board is not None
        assert our_board["title"] == "Integration Test Board"
    
    def test_board_cards_relationship_consistency(self, client, sample_board):
        """Test that cards are properly associated with their board."""
        # sample_board is now a dictionary, not a SQLAlchemy object
        card_data = {
            "message": "Test card",
            "board_id": sample_board["id"]
        }
        
        response = client.post(
            f"/boards/{sample_board['id']}/cards",
            data=json.dumps(card_data),
            content_type="application/json"
        )
        assert response.status_code == 201
        
        # Get board cards
        response = client.get(f"/boards/{sample_board['id']}/cards")
        assert response.status_code == 200
        cards = response.get_json()
        
        # Verify all cards belong to this board
        for card in cards:
            assert card["board_id"] == sample_board["id"]
