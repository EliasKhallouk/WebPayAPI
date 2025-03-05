from flask import Flask
from config import Config
from app.routes import main, fetch_products
import click
from app.models import init_db  # importe la fonction d'initialisation

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    app.register_blueprint(main)

    # Appeler fetch_products() immédiatement si on n'est pas en mode test
    if not app.config.get("TESTING", False):
        with app.app_context():
            fetch_products()

    return app

# Ajoute la commande CLI pour initialiser la base de données
def register_commands(app):
    @app.cli.command("init-db")
    def init_db_command():
        """Initialise la base de données en créant les tables nécessaires."""
        init_db()  # Appelle la fonction définie dans models.py
        click.echo("Base de données initialisée.")

# Enregistre la commande dans l'application créée
app = create_app()
register_commands(app)
