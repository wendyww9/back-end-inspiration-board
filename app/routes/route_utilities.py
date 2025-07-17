from flask import abort, make_response
from ..db import db

def validate_models(cls, model_id):
    try:
        model_id = int(model_id)
    except:
        response = {"message": f"{cls.__name__} with ID {model_id} invalid."}
        abort(make_response(response, "400 Bad Request"))
    if cls.__name__ == "Board":
        query = db.select(cls).where(cls.board_id == model_id)
    else:   # Assuming cls is Card
        query = db.select(cls).where(cls.card_id == model_id)
    model = db.session.scalar(query)
    if model is None:
        response = {"message": f"{cls.__name__} with ID {model_id} not found."}
        abort(make_response(response, "404 Not Found"))

    return model

def create_model(cls, model_data):
    try:
        new_model = cls.from_dict(model_data)
    except KeyError:
        response = {"message": "Invalid data"}
        abort(make_response(response, "400 Bad Request"))

    db.session.add(new_model)
    db.session.commit()

    return new_model.to_dict(), 201