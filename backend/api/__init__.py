from flask import Flask
from flask_cors import CORS
from .routes import api_blueprint

def create_app():
    app = Flask(__name__)

    # Enable CORS to allow frontend to access backend APIs (e.g., http://localhost:5173)
    CORS(app)

    # Register API blueprint
    app.register_blueprint(api_blueprint)

    return app
