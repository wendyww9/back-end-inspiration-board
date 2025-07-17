
import pytest
from app import create_app, db
from flask.signals import request_finished
from dotenv import load_dotenv
import os
from app.models.board import Board
from app.models.card import Card

load_dotenv()

@pytest.fixture
def app():
    """Create and configure a new app instance for each test."""
    test_config = {
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": os.environ.get("SQLALCHEMY_TEST_DATABASE_URI", "sqlite:///:memory:")
    }

    app = create_app(test_config)

    @request_finished.connect_via(app)
    def expire_session(sender, response, **extra):
        """Clear the database session after each request."""
        db.session.remove()
    
    with app.app_context():
        db.create_all()
        yield app

    with app.app_context():
        db.drop_all()

@pytest.fixture
def client(app):
    """Create a test client for the app."""
    return app.test_client()


@pytest.fixture
def session(app):
    """Create a new database session for a test."""
    with app.app_context():
        # Use Flask-SQLAlchemy's session directly
        yield db.session
        
        # Clean up after each test
        db.session.rollback()
        db.session.remove()


@pytest.fixture
def db_session(app):
    """Alternative session fixture for tests that need more control."""
    with app.app_context():
        # Create a new session for this test
        session = db.session
        
        yield session
        
        # Clean up
        session.rollback()
        session.remove()


@pytest.fixture
def sample_board(app):
    """Create a sample board for testing."""
    with app.app_context():
        board = Board(title="Test Board", owner="test_user")
        db.session.add(board)
        db.session.commit()
        # Get the board_id before returning to avoid detached instance issues
        board_id = board.board_id
        return {"id": board_id, "title": board.title, "owner": board.owner}


@pytest.fixture
def sample_card(app, sample_board):
    """Create a sample card for testing."""
    with app.app_context():
        card = Card(message="Test card message", board_id=sample_board["id"])
        db.session.add(card)
        db.session.commit()
        # Get the card_id before returning to avoid detached instance issues
        card_id = card.card_id
        return {"id": card_id, "message": card.message, "board_id": card.board_id, "likes_count": card.likes_count}


@pytest.fixture
def multiple_boards(app):
    """Create multiple boards for testing."""
    with app.app_context():
        boards = []
        for i in range(3):
            board = Board(title=f"Board {i+1}", owner=f"user_{i+1}")
            db.session.add(board)
            boards.append(board)
        db.session.commit()
        # Return board data instead of objects to avoid detached instance issues
        return [{"id": board.board_id, "title": board.title, "owner": board.owner} for board in boards]


@pytest.fixture
def multiple_cards(app, sample_board):
    """Create multiple cards for testing."""
    with app.app_context():
        cards = []
        for i in range(3):
            card = Card(
                message=f"Card message {i+1}",
                likes_count=i,
                board_id=sample_board["id"]
            )
            db.session.add(card)
            cards.append(card)
        db.session.commit()
        # Return card data instead of objects to avoid detached instance issues
        return [{"id": card.card_id, "message": card.message, "board_id": card.board_id, "likes_count": card.likes_count} for card in cards]
