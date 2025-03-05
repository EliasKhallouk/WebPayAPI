import click
from app import create_app
from app.models import init_db
from app.routes import fetch_products

app = create_app()

@app.cli.command("init-db")
def init_db_command():
    """Initialise la base de données."""
    init_db()
    click.echo("Base de données initialisée.")

if __name__ == '__main__':
    fetch_products()
    app.run(debug=True)
