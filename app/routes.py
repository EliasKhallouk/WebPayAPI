import json
import requests
from flask import Blueprint, jsonify, request, redirect, url_for
from app.models import Product, Order

main = Blueprint('main', __name__)

# URL de l'API externe des produits
PRODUCTS_API_URL = "http://dimensweb.uqac.ca/~jgnault/shops/products/"

def calculate_shipping(total_weight):
    """Calcule le coût d'expédition en fonction du poids total (en grammes)."""
    if total_weight <= 500:
        return 5
    elif total_weight <= 2000:
        return 10
    else:
        return 25

def calculate_tax(province):
    """Retourne le taux de taxe selon la province."""
    tax_rates = {
        "QC": 0.15,  # Québec
        "ON": 0.13,  # Ontario
        "AB": 0.05,  # Alberta
        "BC": 0.12,  # Colombie-Britannique
        "NS": 0.14   # Nouvelle-Écosse
    }
    return tax_rates.get(province, 0)

def fetch_products():
    """
    Récupère les produits depuis l'API externe et les insère dans la base de données
    s'ils n'existent pas déjà.
    """
    try:
        response = requests.get(PRODUCTS_API_URL)
        if response.status_code == 200:
            products = response.json().get("products", [])
            for p in products:
                Product.get_or_create(
                    id=p.get("id"),
                    defaults={
                        "name": p.get("name"),
                        "description": p.get("description"),
                        "price": p.get("price"),
                        "in_stock": p.get("in_stock"),
                        "weight": p.get("weight"),
                        "image": p.get("image")
                    }
                )
        else:
            print("Erreur lors de la récupération des produits :", response.status_code)
    except requests.RequestException as e:
        print("Erreur de connexion à l'API des produits :", e)

@main.route('/')
def get_products():
    """Retourne la liste des produits depuis la base de données."""
    products = Product.select()
    products_list = [p.__data__ for p in products]
    return jsonify({"products": products_list})

@main.route('/order', methods=['POST'])
def create_order():
    data = request.json
    if "product" not in data or "id" not in data["product"] or "quantity" not in data["product"]:
        return jsonify({"errors": {
            "product": {"code": "missing-fields", "name": "La création d'une commande nécessite un produit"}
        }}), 422

    product_id = data["product"]["id"]
    quantity = data["product"]["quantity"]

    if quantity < 1:
        return jsonify({"errors": {
            "product": {"code": "missing-fields", "name": "La quantité doit être supérieure ou égale à 1"}
        }}), 422

    try:
        product = Product.get(Product.id == product_id)
    except Product.DoesNotExist:
        return jsonify({"errors": {
            "product": {"code": "not-found", "name": "Produit non trouvé"}
        }}), 404

    if not product.in_stock:
        return jsonify({"errors": {
            "product": {"code": "out-of-inventory", "name": "Le produit demandé n'est pas en inventaire"}
        }}), 422

    # Création de la commande dans la base de données
    order = Order.create(
        product=product,
        quantity=quantity,
        email=None,
        shipping_country=None,
        shipping_address=None,
        shipping_postal_code=None,
        shipping_city=None,
        shipping_province=None,
        paid=False
    )

    # Utilise order.id pour construire l'URL de redirection
    return redirect(url_for('main.get_order', order_id=order.id), code=302)

@main.route('/order/<int:order_id>', methods=['GET'])
def get_order(order_id):
    """Retourne une commande en fonction de son identifiant."""
    try:
        order = Order.get(Order.id == order_id)
        return jsonify({"order": order.__data__}), 200
    except Order.DoesNotExist:
        return jsonify({"errors": {"order": {"code": "not-found", "name": "Commande introuvable"}}}), 404

@main.route('/order/<int:order_id>', methods=['PUT'])
def update_order(order_id):
    """
    Met à jour une commande avec les informations du client (email et shipping_information)
    et recalcule les montants (total, frais d'expédition et total avec taxe).
    """
    data = request.json
    if "order" not in data:
        return jsonify({"errors": {
            "order": {"code": "missing-fields", "name": "Les informations de commande sont obligatoires"}
        }}), 422

    order_data = data["order"]
    for field in ["email", "shipping_information"]:
        if field not in order_data:
            return jsonify({"errors": {"order": {"code": "missing-fields", "name": f"Le champ {field} est obligatoire"}}}), 422

    shipping_info = order_data["shipping_information"]
    for field in ["country", "address", "postal_code", "city", "province"]:
        if field not in shipping_info:
            return jsonify({"errors": {"order": {"code": "missing-fields",
                                                 "name": f"Le champ {field} dans shipping_information est obligatoire"}}}), 422

    try:
        order = Order.get(Order.id == order_id)
    except Order.DoesNotExist:
        return jsonify({"errors": {"order": {"code": "not-found", "name": "Commande introuvable"}}}), 404

    order.email = order_data["email"]
    order.shipping_country = shipping_info["country"]
    order.shipping_address = shipping_info["address"]
    order.shipping_postal_code = shipping_info["postal_code"]
    order.shipping_city = shipping_info["city"]
    order.shipping_province = shipping_info["province"]

    product = order.product
    price = product.price
    weight = product.weight
    quantity = order.quantity
    total_price = price * quantity
    shipping_price = calculate_shipping(weight * quantity)
    tax_rate = calculate_tax(order.shipping_province)
    total_price_tax = total_price * (1 + tax_rate)

    order.total_price = total_price
    order.shipping_price = shipping_price
    order.total_price_tax = total_price_tax

    order.save()
    return jsonify({"order": order.__data__}), 200

@main.route('/order/<int:order_id>/pay', methods=['PUT'])
def pay_order(order_id):
    """
    Gère le paiement d'une commande :
      - Vérifie que les informations du client sont présentes.
      - Communique avec le service de paiement distant.
      - Met à jour l'état de la commande en cas de succès.
    """
    data = request.json
    if "credit_card" not in data:
        return jsonify({"errors": {
            "payment": {"code": "missing-fields", "name": "Les informations de paiement sont obligatoires"}
        }}), 422

    try:
        order = Order.get(Order.id == order_id)
    except Order.DoesNotExist:
        return jsonify({"errors": {"order": {"code": "not-found", "name": "Commande introuvable"}}}), 404

    if not order.email or not order.shipping_country:
        return jsonify({"errors": {"order": {"code": "missing-fields",
                                             "name": "Les informations du client sont nécessaires avant le paiement"}}}), 422

    if order.paid:
        return jsonify({"errors": {"order": {"code": "already-paid", "name": "La commande a déjà été payée"}}}), 422

    if order.total_price is None or order.shipping_price is None:
        return jsonify({"errors": {"order": {"code": "calculation-error", "name": "Les montants n'ont pas été calculés"}}}), 422

    amount_charged = order.total_price + order.shipping_price
    payment_payload = {
        "credit_card": data["credit_card"],
        "amount_charged": amount_charged
    }

    try:
        payment_response = requests.post("http://dimensweb.uqac.ca/~jgnault/shops/pay/", json=payment_payload)
        if payment_response.status_code != 200:
            return jsonify(payment_response.json()), payment_response.status_code
        payment_data = payment_response.json()
    except requests.RequestException:
        return jsonify({"errors": {
            "payment": {"code": "service-unavailable", "name": "Le service de paiement est inaccessible"}
        }}), 503

    order.paid = True
    order.credit_card_info = json.dumps(payment_data.get("credit_card"))
    order.transaction_info = json.dumps(payment_data.get("transaction"))
    order.save()

    # Prépare la réponse en renvoyant les clés "credit_card" et "transaction"
    order_data = order.__data__.copy()
    if order_data.get("credit_card_info"):
        order_data["credit_card"] = json.loads(order_data["credit_card_info"])
    if order_data.get("transaction_info"):
        order_data["transaction"] = json.loads(order_data["transaction_info"])
    order_data.pop("credit_card_info", None)
    order_data.pop("transaction_info", None)

    return jsonify({"order": order_data}), 200
