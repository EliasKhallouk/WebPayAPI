from app import create_app
from app.routes import fetch_products

app = create_app()

if __name__ == '__main__':
    fetch_products()
    app.run(debug=True)
