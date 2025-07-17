from flask import Blueprint, request
from ..db import db
from ..models.board import Board
from ..models.card import Card
from .route_utilities import validate_models, create_model

bp = Blueprint('board_bp', __name__, url_prefix='/boards')

@bp.get("")
def get_all_boards():
    """Get all boards."""
    query = db.select(Board)
    boards = db.session.scalars(query)
    boards_response = [board.to_dict() for board in boards]

    return boards_response

@bp.get("/<board_id>")
def get_one_board(board_id):
    """Get a selected board."""
    board = validate_models(Board, board_id)

    board_response = board.to_dict()
    return board_response

@bp.post("")
def create_one_board():
    """Create a new board."""
    board_data = request.get_json()
    new_board = create_model(Board, board_data)

    return new_board

@bp.post("/<board_id>/cards")
def create_one_card(board_id):
    """Create a new card for a selected board."""
    board = validate_models(Board, board_id)
    card_data = request.get_json()
    new_card = create_model(Card, card_data)
    return new_card

@bp.get("/<board_id>/cards")
def get_board_cards(board_id):
    """Get all cards for a selected board."""
    board = validate_models(Board, board_id)
    cards_list = [card.to_dict() for card in board.cards]
    return cards_list, 200
    # return board.cards, 200

