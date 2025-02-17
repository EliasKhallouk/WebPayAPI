from models import db, Product

def init_db():
    db.connect()
    db.create_tables([Product], safe=True)
    db.close()
