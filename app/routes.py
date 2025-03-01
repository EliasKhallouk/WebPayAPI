import requests
from flask import Blueprint, jsonify

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

@main.route('/')
def get_products():
    """ Retourne la liste des produits stockés en cache """
    return jsonify({"products": cached_products})

# Appel de fetch_products() au lancement de l'application
fetch_products()
