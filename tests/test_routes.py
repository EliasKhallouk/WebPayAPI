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
    assert response.status_code == 200 or response.status_code == 302
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

'''
def test_get_order(client):
    response = client.get('/order/1')
    assert response.status_code in [200, 404]  # Order may or may not exist yet

def test_update_order_success(client):
    update_data = {"email": "test@example.com", "shipping_information": {"country": "Canada", "city": "Chicoutimi"}}
    response = client.put('/order/1', json=update_data)
    assert response.status_code in [200, 404]  # Order may not exist yet

def test_pay_order_missing_fields(client):
    response = client.put('/order/1/pay', json={})
    assert response.status_code == 422
    data = response.get_json()
    assert "errors" in data

'''