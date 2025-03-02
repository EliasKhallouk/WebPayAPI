import requests
from flask import Blueprint, jsonify, request, redirect, url_for

main = Blueprint('main', __name__)

# URL de l'API des produits
PRODUCTS_API_URL = "http://dimensweb.uqac.ca/~jgnault/shops/products/"

# Stockage en cache des produits (évite d'appeler l'API à chaque requête)
cached_products = []

def fetch_products():
    """ Récupère les produits depuis l'API externe et les stocke en cache """
    global cached_products
    try:
        response = requests.get(PRODUCTS_API_URL)
        if response.status_code == 200:
            cached_products = response.json().get("products", [])
        else:
            print("Erreur lors de la récupération des produits :", response.status_code)
    except requests.RequestException as e:
        print("Erreur de connexion à l'API des produits :", e)

def calculate_shipping(weight):
    """ Calcule le prix d'expédition en fonction du poids """
    if weight <= 500:
        return 5
    elif 500 < weight < 2000:
        return 10
    return 25

def calculate_tax(province):
    """ Retourne le pourcentage de taxe en fonction de la province """
    tax_rates = {
        "QC": 0.15,  # Québec
        "ON": 0.13,  # Ontario
        "AB": 0.05,  # Alberta
        "BC": 0.12,  # Colombie-Britannique
        "NS": 0.14   # Nouvelle-Écosse
    }
    return tax_rates.get(province, 0)




@main.route('/')
def get_products():
    """ Retourne la liste des produits stockés en cache """
    return jsonify({"products": cached_products})

@main.route('/order', methods=['POST'])
def create_order():
    """ Crée une nouvelle commande """
    data = request.json
    if "product" not in data or "id" not in data["product"] or "quantity" not in data["product"]:
        return jsonify({"errors": {"product": {"code": "missing-fields", "name": "La création d'une commande nécessite un produit"}}}), 422
    
    product_id = data["product"]["id"]
    quantity = data["product"]["quantity"]
    
    if quantity < 1:
        return jsonify({"errors": {"product": {"code": "missing-fields", "name": "La quantité doit être supérieure ou égale à 1"}}}), 422
    
    new_product = {
        "id": product_id,
        "quantity": quantity
    }
    cached_products.append(new_product)
    return redirect(url_for('main.get_order', order_id=product_id), code=302)

@main.route('/order/<int:order_id>', methods=['GET'])
def get_order(order_id):
    order = next((item for item in cached_products if item.get('id') == order_id), None)
    if not order:
        return jsonify({"errors": {"order": {"code": "not-found", "name": "Commande introuvable"}}}), 404
    return jsonify({"order": order})



'''
@main.route('/order/<int:order_id>', methods=['PUT'])
def update_order(order_id):
    """ Met à jour une commande (ajout email et informations de livraison) """
    data = request.json
    if "email" not in data or "shipping_information" not in data:
        return jsonify({"errors": {"order": {"code": "missing-fields", "name": "Informations obligatoires manquantes"}}}), 422
    
    return jsonify({"order": {"id": order_id, "email": data["email"], "shipping_information": data["shipping_information"], "message": "Commande mise à jour"}}), 200



@main.route('/order/<int:order_id>/pay', methods=['PUT'])
def pay_order(order_id):
    """ Gère le paiement d'une commande """
    data = request.json
    if "credit_card" not in data:
        return jsonify({"errors": {"payment": {"code": "missing-fields", "name": "Les informations de paiement sont obligatoires"}}}), 422
    
    return jsonify({"order": {"id": order_id, "paid": True, "transaction": "successful", "message": "Commande payée avec succès"}}), 200
'''


# Appel de fetch_products() au lancement de l'application
fetch_products()
