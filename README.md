# WebPayAPI

## Auteurs
- Elias KHALLOUK
- Yoann LEHONG CHEFF SON
- Rayan LONGHI
- Mamadou Bah


## Description
WebPayAPI est une application Web développée en Flask pour gérer le paiement de commandes en ligne via une API REST. Elle permet :

- La récupération des produits disponibles.
- La création de commandes avec un produit.
- La gestion des informations client.
- Le paiement sécurisé via un service distant.

## Technologies utilisées
- **Python 3.6+**
- **Flask 1.1+**
- **SQLite3** (avec l'ORM Peewee)
- **requests** (pour récupérer les produits depuis l'API externe)
- **pytest & pytest-flask** (pour les tests unitaires)

## Structure du projet
```
WebPayAPI/
├── app/
│   ├── __init__.py
│   ├── routes.py
├── tests/
├── static/
├── templates/
├── config.py
├── run.py
├── Travail de session partie 1.pdf
├── README.md
```

## Installation
### 1️⃣ Cloner le dépôt
```bash
git clone https://github.com/EliasKhallouk/WebPayAPI.git
cd WebPayAPI
```

### 2️⃣ Créer un environnement virtuel
```bash
python -m venv venv
source venv/bin/activate  # (Linux/macOS)
venv\Scripts\activate  # (Windows)
```

### 3️⃣ Installer les dépendances
```bash
pip install flask peewee pytest pytest-flask requests
```

### 4️⃣ Initialiser la base de données
```bash
FLASK_DEBUG=True FLASK_APP=run.py flask init-db
```

## Utilisation
### Lancer l’application
```bash
export FLASK_APP=run.py  # (Linux/macOS)
export FLASK_DEBUG=True
flask run
```
Sur Windows :
```powershell
set FLASK_APP=run.py
set FLASK_DEBUG=True
flask run
```
L’application sera accessible sur [http://127.0.0.1:5000](http://127.0.0.1:5000).

## API Endpoints
### 🔹 Récupérer les produits disponibles
```http
GET /
```
Réponse :
```json
{
    "products": [
        {"id": 1, "name": "Brown eggs", "price": 28.1, "in_stock": true}
    ]
}
```

### 🔹 Créer une commande
```http
POST /order
Content-Type: application/json
{
    "product": {"id": 123, "quantity": 2}
}
```
Réponse :
```json
302 Found
Location: /order/<order_id>
```

### 🔹 Récupérer une commande
```http
GET /order/<order_id>
```

### 🔹 Ajouter les informations du client
```http
PUT /order/<order_id>
Content-Type: application/json
{
    "order": {
        "email": "client@email.com",
        "shipping_information": {"country": "Canada", "city": "Chicoutimi"}
    }
}
```

### 🔹 Payer une commande
```http
PUT /order/<order_id>
Content-Type: application/json
{
    "credit_card": {
        "name": "John Doe",
        "number": "4242 4242 4242 4242",
        "expiration_year": 2024,
        "expiration_month": 9,
        "cvv": "123"
    }
}
```

## Tests
Pour exécuter les tests unitaires :
```bash
pytest
```
