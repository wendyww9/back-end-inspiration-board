from flask import Flask
from flask_cors import CORS
import os
# Import models, blueprints, and anything else needed to set up the app or database
from .models import board
from .models import card
from app.routes.board_routes import bp as board_bp
from app.routes.card_routes import bp as card_bp
from .db import db, migrate

def create_app(config=None):
    app = Flask(__name__)

    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('SQLALCHEMY_DATABASE_URI')

    if config:
        app.config.update(config)

    # Initialize app with SQLAlchemy db and Migrate
    db.init_app(app)
    migrate.init_app(app, db)

    # Register Blueprints
    app.register_blueprint(board_bp)
    app.register_blueprint(card_bp)

    CORS(app)
    return app
