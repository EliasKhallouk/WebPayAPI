import os
import sys
import pytest

# Ajoute le dossier parent (la racine du projet) au sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from app.models import DATABASE, Product, Order

@pytest.fixture(autouse=True)
def setup_database():
    """
    Configure une base de données SQLite en mémoire pour les tests,
    crée les tables avant chaque test et les supprime ensuite.
    """
    # Utilisation d'une base en mémoire pour éviter les interférences avec la DB de développement
    DATABASE.init(':memory:')
    DATABASE.connect()
    DATABASE.create_tables([Product, Order])
    yield
    DATABASE.drop_tables([Product, Order])
    DATABASE.close()

@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client
