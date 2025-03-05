from peewee import *
import os

# Chemin et configuration de la base de données SQLite
DATABASE = SqliteDatabase(os.path.join(os.getcwd(), 'webpayapi.db'))

class BaseModel(Model):
    class Meta:
        database = DATABASE

class Product(BaseModel):
    id = IntegerField(primary_key=True)
    name = CharField()
    description = TextField(null=True)
    price = IntegerField()  # Le prix du produit est stocké en cents
    in_stock = BooleanField()
    weight = IntegerField()  # en grammes
    image = CharField()

class Order(BaseModel):
    id = AutoField()  # Identifiant unique auto-incrémenté
    product = ForeignKeyField(Product, backref='orders')
    quantity = IntegerField()
    email = CharField(null=True)
    shipping_country = CharField(null=True)
    shipping_address = CharField(null=True)
    shipping_postal_code = CharField(null=True)
    shipping_city = CharField(null=True)
    shipping_province = CharField(null=True)
    paid = BooleanField(default=False)
    total_price = IntegerField(null=True)      # Stocké en cents
    shipping_price = IntegerField(null=True)     # Stocké en cents
    total_price_tax = FloatField(null=True)      # Peut rester un float pour le calcul avec la taxe
    credit_card_info = TextField(null=True)   # Infos de carte stockées (JSON)
    transaction_info = TextField(null=True)

def init_db():
    if DATABASE.is_closed():
        DATABASE.connect()
    DATABASE.create_tables([Product, Order], safe=True)
    if not DATABASE.is_closed():
        DATABASE.close()
