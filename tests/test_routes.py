import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import create_app


@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_get_products(client):
    response = client.get('/')
    assert response.status_code == 200
    data = response.get_json()
    assert "products" in data

def test_create_order_success(client):
    order_data = {"product": {"id": 1, "quantity": 2}}
    response = client.post('/order', json=order_data, follow_redirects=True)
    assert response.status_code == 302
    data = response.get_json()
    assert "order" in data
    assert data["order"]["id"] == 1

def test_create_order_missing_fields(client):
    order_data = {"product": {"quantity": 2}}  # Missing product id
    response = client.post('/order', json=order_data)
    assert response.status_code == 422
    data = response.get_json()
    assert "errors" in data

def test_create_order_invalid_product(client):
    order_data = {"product": {"id": 999, "quantity": 0}}  # Non-existent product id
    response = client.post('/order', json=order_data)
    assert response.status_code == 422
    data = response.get_json()
    assert "errors" in data

def test_get_order_success(client):
    # Création d'une commande au préalable
    order_data = {"product": {"id": 999, "quantity": 3}}
    post_response = client.post('/order', json=order_data, follow_redirects=True)
    assert post_response.status_code == 200
    data = post_response.get_json()
    assert "order" in data
    order_id = data["order"]["id"]

    # Récupération de la commande créée via GET /order/<order_id>
    get_response = client.get(f"/order/{order_id}")
    assert get_response.status_code == 200
    order = get_response.get_json().get("order")
    assert order["id"] == order_id
    assert order["quantity"] == order_data["product"]["quantity"]

def test_get_order_not_found(client):
    # Tentative de récupération d'une commande inexistante
    response = client.get("/order/99999")
    assert response.status_code == 404
    data = response.get_json()
    assert "errors" in data