def test_update_order_success(client):
    # Création d'une commande
    order_data = {"product": {"id": 1, "quantity": 2}}
    post_response = client.post('/order', json=order_data, follow_redirects=True)
    # Avec follow_redirects=True, le status peut être 200 après redirection
    assert post_response.status_code in (200, 302)
    order = post_response.get_json()["order"]
    order_id = order["id"]

    # Mise à jour de la commande avec toutes les informations requises
    update_payload = {
        "order": {
            "email": "test@example.com",
            "shipping_information": {
                "country": "Canada",
                "address": "123 Test St",
                "postal_code": "G1A1A1",
                "city": "Montreal",
                "province": "QC"
            }
        }
    }
    put_response = client.put(f"/order/{order_id}", json=update_payload)
    assert put_response.status_code == 200
    updated_order = put_response.get_json()["order"]
    assert updated_order["email"] == "test@example.com"
    # Vérifie que les montants ont été calculés (si le produit est trouvé dans cached_products)
    assert updated_order["total_price"] is not None
    assert updated_order["shipping_price"] is not None
    assert updated_order["total_price_tax"] is not None

def test_update_order_missing_fields(client):
    # Création d'une commande
    order_data = {"product": {"id": 1, "quantity": 2}}
    post_response = client.post('/order', json=order_data, follow_redirects=True)
    order_id = post_response.get_json()["order"]["id"]

    # Envoi d'une mise à jour sans shipping_information
    update_payload = {
        "order": {
            "email": "test@example.com"
        }
    }
    put_response = client.put(f"/order/{order_id}", json=update_payload)
    assert put_response.status_code == 422
    data = put_response.get_json()
    assert "errors" in data

def test_pay_order_success(client, monkeypatch):
    # Création et mise à jour d'une commande
    order_data = {"product": {"id": 1, "quantity": 2}}
    post_response = client.post('/order', json=order_data, follow_redirects=True)
    order = post_response.get_json()["order"]
    order_id = order["id"]

    update_payload = {
        "order": {
            "email": "test@example.com",
            "shipping_information": {
                "country": "Canada",
                "address": "123 Test St",
                "postal_code": "G1A1A1",
                "city": "Montreal",
                "province": "QC"
            }
        }
    }
    update_response = client.put(f"/order/{order_id}", json=update_payload)
    assert update_response.status_code == 200

    # Création d'une fausse réponse pour simuler le service de paiement distant
    class FakeResponse:
        def __init__(self, status_code, data):
            self.status_code = status_code
            self._data = data
        def json(self):
            return self._data

    def fake_post(url, json):
        # Simule une réponse de paiement réussie
        payment_data = {
            "credit_card": {
                "name": json["credit_card"]["name"],
                "first_digits": "4242",
                "last_digits": "4242",
                "expiration_year": json["credit_card"]["expiration_year"],
                "expiration_month": json["credit_card"]["expiration_month"]
            },
            "transaction": {
                "id": "tx123",
                "success": True,
                "amount_charged": json["amount_charged"]
            }
        }
        return FakeResponse(200, payment_data)

    monkeypatch.setattr("app.routes.requests.post", fake_post)

    credit_card_payload = {
        "credit_card": {
            "name": "John Doe",
            "number": "4242 4242 4242 4242",
            "expiration_year": 2024,
            "expiration_month": 9,
            "cvv": "123"
        }
    }
    pay_response = client.put(f"/order/{order_id}/pay", json=credit_card_payload)
    assert pay_response.status_code == 200
    paid_order = pay_response.get_json()["order"]
    assert paid_order["paid"] is True
    assert "credit_card" in paid_order
    assert "transaction" in paid_order

def test_pay_order_missing_credit_card(client):
    # Création et mise à jour d'une commande
    order_data = {"product": {"id": 1, "quantity": 2}}
    post_response = client.post('/order', json=order_data, follow_redirects=True)
    order_id = post_response.get_json()["order"]["id"]

    update_payload = {
        "order": {
            "email": "test@example.com",
            "shipping_information": {
                "country": "Canada",
                "address": "123 Test St",
                "postal_code": "G1A1A1",
                "city": "Montreal",
                "province": "QC"
            }
        }
    }
    client.put(f"/order/{order_id}", json=update_payload)

    # Tentative de paiement sans fournir d'informations de carte
    pay_response = client.put(f"/order/{order_id}/pay", json={})
    assert pay_response.status_code == 422
    data = pay_response.get_json()
    assert "errors" in data

def test_pay_order_without_update(client):
    # Création d'une commande sans mise à jour (donc sans informations client)
    order_data = {"product": {"id": 1, "quantity": 2}}
    post_response = client.post('/order', json=order_data, follow_redirects=True)
    order_id = post_response.get_json()["order"]["id"]

    credit_card_payload = {
        "credit_card": {
            "name": "John Doe",
            "number": "4242 4242 4242 4242",
            "expiration_year": 2024,
            "expiration_month": 9,
            "cvv": "123"
        }
    }
    pay_response = client.put(f"/order/{order_id}/pay", json=credit_card_payload)
    # On attend une erreur 422 car les informations du client ne sont pas présentes
    assert pay_response.status_code == 422
    data = pay_response.get_json()
    assert "errors" in data

def test_pay_order_already_paid(client, monkeypatch):
    # Création et mise à jour d'une commande
    order_data = {"product": {"id": 1, "quantity": 2}}
    post_response = client.post('/order', json=order_data, follow_redirects=True)
    order = post_response.get_json()["order"]
    order_id = order["id"]

    update_payload = {
        "order": {
            "email": "test@example.com",
            "shipping_information": {
                "country": "Canada",
                "address": "123 Test St",
                "postal_code": "G1A1A1",
                "city": "Montreal",
                "province": "QC"
            }
        }
    }
    client.put(f"/order/{order_id}", json=update_payload)

    # Monkeypatch pour simuler le paiement réussi
    class FakeResponse:
        def __init__(self, status_code, data):
            self.status_code = status_code
            self._data = data
        def json(self):
            return self._data

    def fake_post(url, json):
        payment_data = {
            "credit_card": {
                "name": json["credit_card"]["name"],
                "first_digits": "4242",
                "last_digits": "4242",
                "expiration_year": json["credit_card"]["expiration_year"],
                "expiration_month": json["credit_card"]["expiration_month"]
            },
            "transaction": {
                "id": "tx123",
                "success": True,
                "amount_charged": json["amount_charged"]
            }
        }
        return FakeResponse(200, payment_data)

    monkeypatch.setattr("app.routes.requests.post", fake_post)
    credit_card_payload = {
        "credit_card": {
            "name": "John Doe",
            "number": "4242 4242 4242 4242",
            "expiration_year": 2024,
            "expiration_month": 9,
            "cvv": "123"
        }
    }
    # Premier paiement (devrait réussir)
    first_pay = client.put(f"/order/{order_id}/pay", json=credit_card_payload)
    assert first_pay.status_code == 200
    # Deuxième tentative de paiement (devrait renvoyer une erreur)
    second_pay = client.put(f"/order/{order_id}/pay", json=credit_card_payload)
    assert second_pay.status_code == 422
    data = second_pay.get_json()
    assert "errors" in data
