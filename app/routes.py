from flask import Blueprint, jsonify

main = Blueprint('main', __name__)

@main.route('/')
def index():
    view = """
    <html>
        <body>
            <h1>HEY !!!</h1>
        </body>
    </html>
    """
    return view
