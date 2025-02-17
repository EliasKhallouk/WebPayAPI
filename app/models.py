from peewee import Model, CharField, IntegerField, BooleanField, SqliteDatabase

db = SqliteDatabase('database.db')

class BaseModel(Model):
    class Meta:
        database = db

class Product(BaseModel):
    name = CharField()
    description = CharField()
    price = IntegerField()
    in_stock = BooleanField()
