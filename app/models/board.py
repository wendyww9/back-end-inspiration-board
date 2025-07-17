from sqlalchemy.orm import Mapped, mapped_column, relationship
from ..db import db


class Board(db.Model):
    board_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str]
    owner: Mapped[str]
    cards: Mapped[list["Card"]] = relationship(back_populates="board")

    def to_dict(self):
        board_dict = {
            "id": self.board_id,
            "title": self.title,
            "owner": self.owner  
        }
        if self.cards:
            board_dict["cards"] = [card.to_dict() for card in self.cards]
        return board_dict

    @classmethod
    def from_dict(cls, board_data):
        new_board = cls(
            title=board_data["title"],
            owner=board_data["owner"]
        )
        return new_board
    
    def safe_delete(self, force=False):
        """
        Safely delete a board and its cards.
        
        Args:
            force (bool): If True, delete the board and all its cards.
                         If False, raise an error if the board has cards.
        
        Raises:
            ValueError: If force=False and the board has cards.
        """
        if not force and self.cards:
            card_count = len(self.cards)
            raise ValueError(
                f"Cannot delete board '{self.title}' because it has {card_count} card(s). "
                f"Use force=True to delete the board and all its cards."
            )
        
        # Delete all cards first
        for card in self.cards:
            db.session.delete(card)
        
        # Then delete the board
        db.session.delete(self)
