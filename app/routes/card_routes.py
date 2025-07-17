from flask import Blueprint, request
from ..db import db
from ..models.board import Board
from ..models.card import Card
from .route_utilities import validate_models, create_model

bp = Blueprint('card_bp', __name__, url_prefix='/cards')

@bp.delete("/<card_id>")
def delete_card(card_id):
    """Delete a card."""
    card = validate_models(Card, card_id)
    db.session.delete(card)
    db.session.commit()
    delete_response = {"message": f"Card {card_id} deleted successfully"}
    return delete_response


@bp.put("/<card_id>/likes")
def update_card_likes(card_id):
    """Update the likes count of a card."""
    card = validate_models(Card, card_id)
    card.likes_count += 1
    db.session.commit()

    return card.to_dict()