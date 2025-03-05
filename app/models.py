import os
from peewee import *

# Chemin et configuration de la base de données SQLite
DATABASE = SqliteDatabase(os.path.join(os.getcwd(), 'webpayapi.db'))

class BaseModel(Model):
    class Meta:
        database = DATABASE

class Product(BaseModel):
    id = IntegerField(primary_key=True)
    name = CharField()
    description = TextField(null=True)
    price = FloatField()  # Indique si c'est en dollars ou en cents selon ta convention
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
    total_price = FloatField(null=True)
    shipping_price = FloatField(null=True)
    total_price_tax = FloatField(null=True)
    credit_card_info = TextField(null=True)   # On peut stocker ces infos au format JSON par exemple
    transaction_info = TextField(null=True)

def init_db():
    DATABASE.connect()
    DATABASE.create_tables([Product, Order], safe=True)
    DATABASE.close()
