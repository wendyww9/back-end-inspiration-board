import pytest
from app.models.board import Board
from app.models.card import Card
from app.db import db


class TestBoardModel:
    """Test the Board model."""
    
    def test_board_creation(self, app):
        """Test creating a board with valid data."""
        with app.app_context():
            board = Board(title="Test Board", owner="test_user")
            db.session.add(board)
            db.session.commit()
            
            assert board.board_id is not None
            assert board.title == "Test Board"
            assert board.owner == "test_user"
            assert board.cards == []
    
    def test_board_creation_without_optional_fields(self, app):
        """Test creating a board with only required fields."""
        with app.app_context():
            board = Board(title="Minimal Board", owner="user")
            db.session.add(board)
            db.session.commit()
            
            assert board.board_id is not None
            assert board.title == "Minimal Board"
            assert board.owner == "user"
    
    def test_board_to_dict(self, app):
        """Test board serialization to dictionary."""
        with app.app_context():
            board = Board(title="Test Board", owner="test_user")
            db.session.add(board)
            db.session.commit()
            
            board_dict = board.to_dict()
            assert board_dict["id"] == board.board_id
            assert board_dict["title"] == "Test Board"
            assert board_dict["owner"] == "test_user"
            # Note: to_dict() doesn't include relationships by default
    
    def test_board_from_dict(self, app):
        """Test board creation from dictionary."""
        with app.app_context():
            board_data = {
                "title": "From Dict Board",
                "owner": "dict_user"
            }
            
            board = Board.from_dict(board_data)
            assert board.title == "From Dict Board"
            assert board.owner == "dict_user"
            assert board.board_id is None  # Not committed yet
    
    def test_board_from_dict_with_id(self, app):
        """Test board creation from dictionary with existing ID."""
        with app.app_context():
            # First create a board
            board = Board(title="Original Board", owner="user")
            db.session.add(board)
            db.session.commit()
            original_id = board.board_id
            
            # Create from dict with ID (note: from_dict ignores 'id' field)
            board_data = {
                "id": original_id,
                "title": "Updated Board",
                "owner": "updated_user"
            }
            
            updated_board = Board.from_dict(board_data)
            # from_dict() doesn't set board_id, it creates a new instance
            assert updated_board.board_id is None  # New instance, not committed
            assert updated_board.title == "Updated Board"
            assert updated_board.owner == "updated_user"
    
    def test_board_relationship_with_cards(self, app):
        """Test board-card relationship."""
        with app.app_context():
            # Create board
            board = Board(title="Board with Cards", owner="user")
            db.session.add(board)
            db.session.commit()
            
            # Create cards for the board
            card1 = Card(message="First card", board_id=board.board_id)
            card2 = Card(message="Second card", board_id=board.board_id)
            db.session.add_all([card1, card2])
            db.session.commit()
            
            # Refresh to get the relationship
            db.session.refresh(board)
            
            assert len(board.cards) == 2
            assert board.cards[0].message == "First card"
            assert board.cards[1].message == "Second card"
    
    def test_board_update(self, app):
        """Test updating board attributes."""
        with app.app_context():
            board = Board(title="Original Title", owner="original_user")
            db.session.add(board)
            db.session.commit()
            
            # Update the board
            board.title = "Updated Title"
            board.owner = "updated_user"
            db.session.commit()
            
            # Verify changes
            assert board.title == "Updated Title"
            assert board.owner == "updated_user"
    
    def test_board_delete(self, app):
        """Test deleting a board."""
        with app.app_context():
            board = Board(title="To Delete", owner="user")
            db.session.add(board)
            db.session.commit()
            board_id = board.board_id
            
            # Delete the board
            db.session.delete(board)
            db.session.commit()
            
            # Verify it's gone
            deleted_board = db.session.get(Board, board_id)
            assert deleted_board is None
    
    def test_board_safe_delete_without_force(self, app):
        """Test safe_delete without force parameter (should fail if board has cards)."""
        with app.app_context():
            # Create board with cards
            board = Board(title="Board to Safe Delete", owner="user")
            db.session.add(board)
            db.session.commit()
            
            card = Card(message="Test card", board_id=board.board_id)
            db.session.add(card)
            db.session.commit()
            
            # Try to safe_delete without force (should raise ValueError)
            with pytest.raises(ValueError) as exc_info:
                board.safe_delete(force=False)
            
            # Verify the error message
            error_msg = str(exc_info.value)
            assert "Cannot delete board" in error_msg
            assert "1 card(s)" in error_msg
            assert "force=True" in error_msg
            
            # Verify board and card still exist
            existing_board = db.session.get(Board, board.board_id)
            existing_card = db.session.get(Card, card.card_id)
            assert existing_board is not None
            assert existing_card is not None
    
    def test_board_safe_delete_with_force(self, app):
        """Test safe_delete with force parameter (should delete board and cards)."""
        with app.app_context():
            # Create board with cards
            board = Board(title="Board to Force Delete", owner="user")
            db.session.add(board)
            db.session.commit()
            
            card1 = Card(message="Card 1", board_id=board.board_id)
            card2 = Card(message="Card 2", board_id=board.board_id)
            db.session.add_all([card1, card2])
            db.session.commit()
            
            board_id = board.board_id
            card1_id = card1.card_id
            card2_id = card2.card_id
            
            # Safe delete with force=True
            board.safe_delete(force=True)
            db.session.commit()
            
            # Verify both board and cards are deleted
            deleted_board = db.session.get(Board, board_id)
            deleted_card1 = db.session.get(Card, card1_id)
            deleted_card2 = db.session.get(Card, card2_id)
            
            assert deleted_board is None
            assert deleted_card1 is None
            assert deleted_card2 is None
    
    def test_board_safe_delete_empty_board(self, app):
        """Test safe_delete on a board without cards (should work without force)."""
        with app.app_context():
            # Create board without cards
            board = Board(title="Empty Board", owner="user")
            db.session.add(board)
            db.session.commit()
            
            board_id = board.board_id
            
            # Safe delete without force (should work for empty board)
            board.safe_delete(force=False)
            db.session.commit()
            
            # Verify board is deleted
            deleted_board = db.session.get(Board, board_id)
            assert deleted_board is None
    
    def test_board_safe_delete_without_force(self, app):
        """Test safe_delete without force parameter (should fail if board has cards)."""
        with app.app_context():
            # Create board with cards
            board = Board(title="Board to Safe Delete", owner="user")
            db.session.add(board)
            db.session.commit()
            
            card = Card(message="Test card", board_id=board.board_id)
            db.session.add(card)
            db.session.commit()
            
            # Try to safe_delete without force (should raise ValueError)
            with pytest.raises(ValueError) as exc_info:
                board.safe_delete(force=False)
            
            # Verify the error message
            error_msg = str(exc_info.value)
            assert "Cannot delete board" in error_msg
            assert "1 card(s)" in error_msg
            assert "force=True" in error_msg
            
            # Verify board and card still exist
            existing_board = db.session.get(Board, board.board_id)
            existing_card = db.session.get(Card, card.card_id)
            assert existing_board is not None
            assert existing_card is not None
    
    def test_board_safe_delete_with_force(self, app):
        """Test safe_delete with force parameter (should delete board and cards)."""
        with app.app_context():
            # Create board with cards
            board = Board(title="Board to Force Delete", owner="user")
            db.session.add(board)
            db.session.commit()
            
            card1 = Card(message="Card 1", board_id=board.board_id)
            card2 = Card(message="Card 2", board_id=board.board_id)
            db.session.add_all([card1, card2])
            db.session.commit()
            
            board_id = board.board_id
            card1_id = card1.card_id
            card2_id = card2.card_id
            
            # Safe delete with force=True
            board.safe_delete(force=True)
            db.session.commit()
            
            # Verify both board and cards are deleted
            deleted_board = db.session.get(Board, board_id)
            deleted_card1 = db.session.get(Card, card1_id)
            deleted_card2 = db.session.get(Card, card2_id)
            
            assert deleted_board is None
            assert deleted_card1 is None
            assert deleted_card2 is None
    
    def test_board_safe_delete_empty_board(self, app):
        """Test safe_delete on a board without cards (should work without force)."""
        with app.app_context():
            # Create board without cards
            board = Board(title="Empty Board", owner="user")
            db.session.add(board)
            db.session.commit()
            
            board_id = board.board_id
            
            # Safe delete without force (should work for empty board)
            board.safe_delete(force=False)
            db.session.commit()
            
            # Verify board is deleted
            deleted_board = db.session.get(Board, board_id)
            assert deleted_board is None


class TestCardModel:
    """Test the Card model."""
    
    def test_card_creation(self, app, sample_board):
        """Test creating a card with valid data."""
        with app.app_context():
            card = Card(message="Test card message", board_id=sample_board["id"])
            db.session.add(card)
            db.session.commit()
            
            assert card.card_id is not None
            assert card.message == "Test card message"
            assert card.board_id == sample_board["id"]
            assert card.likes_count == 0  # Default value
    
    def test_card_creation_with_likes(self, app, sample_board):
        """Test creating a card with specified likes count."""
        with app.app_context():
            card = Card(
                message="Liked card",
                board_id=sample_board["id"],
                likes_count=5
            )
            db.session.add(card)
            db.session.commit()
            
            assert card.likes_count == 5
    
    def test_card_to_dict(self, app, sample_board):
        """Test card serialization to dictionary."""
        with app.app_context():
            card = Card(message="Test card", board_id=sample_board["id"])
            db.session.add(card)
            db.session.commit()
            
            card_dict = card.to_dict()
            assert card_dict["id"] == card.card_id
            assert card_dict["message"] == "Test card"
            assert card_dict["board_id"] == sample_board["id"]
            assert card_dict["likes_count"] == 0
    
    def test_card_from_dict(self, app, sample_board):
        """Test card creation from dictionary."""
        with app.app_context():
            card_data = {
                "message": "From Dict Card",
                "board_id": sample_board["id"]
            }
            
            card = Card.from_dict(card_data)
            assert card.message == "From Dict Card"
            assert card.board_id == sample_board["id"]
            assert card.likes_count == 0  # Default value
            assert card.card_id is None  # Not committed yet
    
    def test_card_from_dict_with_likes(self, app, sample_board):
        """Test card creation from dictionary with likes count."""
        with app.app_context():
            card_data = {
                "message": "Liked Card",
                "board_id": sample_board["id"],
                "likes_count": 10
            }
            
            card = Card.from_dict(card_data)
            assert card.message == "Liked Card"
            assert card.board_id == sample_board["id"]
            assert card.likes_count == 10
    
    def test_card_from_dict_with_id(self, app, sample_board):
        """Test card creation from dictionary with existing ID."""
        with app.app_context():
            # First create a card
            card = Card(message="Original Card", board_id=sample_board["id"])
            db.session.add(card)
            db.session.commit()
            original_id = card.card_id
            
            # Create from dict with ID (note: from_dict ignores 'id' field)
            card_data = {
                "id": original_id,
                "message": "Updated Card",
                "board_id": sample_board["id"],
                "likes_count": 5
            }
            
            updated_card = Card.from_dict(card_data)
            # from_dict() doesn't set card_id, it creates a new instance
            assert updated_card.card_id is None  # New instance, not committed
            assert updated_card.message == "Updated Card"
            assert updated_card.likes_count == 5
    
    def test_card_relationship_with_board(self, app, sample_board):
        """Test card-board relationship."""
        with app.app_context():
            card = Card(message="Test card", board_id=sample_board["id"])
            db.session.add(card)
            db.session.commit()
            
            # Get the board through relationship
            board = db.session.get(Board, sample_board["id"])
            assert board is not None
            assert len(board.cards) == 1
            assert board.cards[0].card_id == card.card_id
    
    def test_card_update(self, app, sample_board):
        """Test updating card attributes."""
        with app.app_context():
            card = Card(message="Original message", board_id=sample_board["id"])
            db.session.add(card)
            db.session.commit()
            
            # Update the card
            card.message = "Updated message"
            card.likes_count = 15
            db.session.commit()
            
            # Verify changes
            assert card.message == "Updated message"
            assert card.likes_count == 15
    
    def test_card_delete(self, app, sample_board):
        """Test deleting a card."""
        with app.app_context():
            card = Card(message="To Delete", board_id=sample_board["id"])
            db.session.add(card)
            db.session.commit()
            card_id = card.card_id
            
            # Delete the card
            db.session.delete(card)
            db.session.commit()
            
            # Verify it's gone
            deleted_card = db.session.get(Card, card_id)
            assert deleted_card is None
    
    def test_card_likes_increment(self, app, sample_board):
        """Test incrementing card likes."""
        with app.app_context():
            card = Card(message="Test card", board_id=sample_board["id"])
            db.session.add(card)
            db.session.commit()
            
            initial_likes = card.likes_count
            card.likes_count += 1
            db.session.commit()
            
            assert card.likes_count == initial_likes + 1


class TestModelValidation:
    """Test model validation and edge cases."""
    
    def test_board_empty_title(self, app):
        """Test board creation with empty title."""
        with app.app_context():
            board = Board(title="", owner="user")
            db.session.add(board)
            db.session.commit()
            
            # Should allow empty title (unless there's a constraint)
            assert board.title == ""
    
    def test_board_long_title(self, app):
        """Test board creation with very long title."""
        with app.app_context():
            long_title = "A" * 1000  # Very long title
            board = Board(title=long_title, owner="user")
            db.session.add(board)
            db.session.commit()
            
            assert board.title == long_title
    
    def test_card_empty_message(self, app, sample_board):
        """Test card creation with empty message."""
        with app.app_context():
            card = Card(message="", board_id=sample_board["id"])
            db.session.add(card)
            db.session.commit()
            
            # Should allow empty message (unless there's a constraint)
            assert card.message == ""
    
    def test_card_long_message(self, app, sample_board):
        """Test card creation with very long message."""
        with app.app_context():
            long_message = "B" * 2000  # Very long message
            card = Card(message=long_message, board_id=sample_board["id"])
            db.session.add(card)
            db.session.commit()
            
            assert card.message == long_message
    
    def test_card_negative_likes(self, app, sample_board):
        """Test card creation with negative likes count."""
        with app.app_context():
            card = Card(
                message="Negative likes",
                board_id=sample_board["id"],
                likes_count=-5
            )
            db.session.add(card)
            db.session.commit()
            
            # Should allow negative likes (unless there's a constraint)
            assert card.likes_count == -5


class TestModelQueries:
    """Test database queries and relationships."""
    
    def test_get_board_by_id(self, app):
        """Test retrieving board by ID."""
        with app.app_context():
            board = Board(title="Query Test Board", owner="query_user")
            db.session.add(board)
            db.session.commit()
            
            # Query by ID
            retrieved_board = db.session.get(Board, board.board_id)
            assert retrieved_board is not None
            assert retrieved_board.title == "Query Test Board"
    
    def test_get_cards_by_board(self, app, sample_board):
        """Test retrieving all cards for a board."""
        with app.app_context():
            # Create multiple cards for the board
            cards = []
            for i in range(3):
                card = Card(message=f"Card {i+1}", board_id=sample_board["id"])
                cards.append(card)
            
            db.session.add_all(cards)
            db.session.commit()
            
            # Query cards by board
            board_cards = db.session.query(Card).filter_by(board_id=sample_board["id"]).all()
            assert len(board_cards) == 3
            assert all(card.board_id == sample_board["id"] for card in board_cards)
    
    def test_board_cards_relationship_query(self, app):
        """Test querying cards through board relationship."""
        with app.app_context():
            board = Board(title="Relationship Board", owner="user")
            db.session.add(board)
            db.session.commit()
            
            # Add cards
            card1 = Card(message="First", board_id=board.board_id)
            card2 = Card(message="Second", board_id=board.board_id)
            db.session.add_all([card1, card2])
            db.session.commit()
            
            # Query through relationship
            db.session.refresh(board)
            assert len(board.cards) == 2
            assert {card.message for card in board.cards} == {"First", "Second"}