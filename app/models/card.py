from sqlalchemy.orm import Mapped, mapped_column, relationship
from ..db import db

class Card(db.Model):
    card_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    message: Mapped[str]
    likes_count: Mapped[int] = mapped_column(default=0)
    board: Mapped["Board"] = relationship(back_populates="cards")
    # Foreign key to link the card to a board
    board_id: Mapped[int] = mapped_column(db.ForeignKey('board.board_id'))

    def to_dict(self):
        card_dict = {
            "id": self.card_id,
            "message": self.message,
            "likes_count": self.likes_count,
            "board_id": self.board_id
        }
        return card_dict
    
    @classmethod
    def from_dict(cls, card_data):
        new_card = cls(
            message=card_data["message"],
            likes_count=card_data.get("likes_count", 0),
            board_id=card_data["board_id"]
        )
        return new_card