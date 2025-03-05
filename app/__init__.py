from flask import Flask
from config import Config
from app.routes import main, fetch_products


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    app.register_blueprint(main)

    # Appeler fetch_products() immédiatement si on n'est pas en mode test
    if not app.config.get("TESTING", False):
        with app.app_context():
            fetch_products()

    return app
