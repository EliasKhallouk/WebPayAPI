
# WebPayAPI

## Auteurs
- Elias KHALLOUK
- Yoann LEHONG CHEFFSON
- Rayan LONGHI
- Mamadou Bah

## Description
WebPayAPI est une application Web développée en Flask pour gérer le paiement de commandes en ligne via une API REST. Elle permet :

- La récupération des produits disponibles.
- La création de commandes avec un produit.
- La gestion des informations client.
- Le paiement sécurisé via un service distant.

> **Note :** Les prix sont désormais stockés et manipulés en **cents**. Par exemple, un produit coûtant 28,10\$ est représenté par la valeur **2810**.

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
│   ├── models.py
│   ├── routes.py
├── tests/
│   ├── conftest.py
│   └── test_routes.py
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
venv\Scriptsctivate      # (Windows)
```

### 3️⃣ Installer les dépendances
```bash
pip install flask peewee pytest pytest-flask requests
```

### 4️⃣ Initialiser la base de données
La base de données se pré-initialise via une commande CLI personnalisée.  
Exécutez :
```bash
FLASK_DEBUG=True FLASK_APP=run.py flask init-db
```
Cette commande crée les tables nécessaires dans la base de données.

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

### 🔹 Créer une commande
```http
POST /order
Content-Type: application/json
{
    "product": {"id": 1, "quantity": 2}
}
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
        "shipping_information": {
            "country": "Canada",
            "address": "123 Test St",
            "postal_code": "G1A1A1",
            "city": "Chicoutimi",
            "province": "QC"
        }
    }
}
```

### 🔹 Payer une commande
> **Attention :** Seules les informations de paiement (*credit_card*) doivent être fournies dans ce payload. Les informations client (email et shipping_information) doivent avoir été ajoutées au préalable via l'endpoint PUT /order/<order_id>.

```http
PUT /order/<order_id>/pay
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
