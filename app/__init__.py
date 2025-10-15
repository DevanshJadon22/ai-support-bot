# from flask import Flask
# from .models import db

# def create_app():
#     app = Flask(__name__)
#     # This configures the app to use a SQLite database file named 'chat_sessions.db'
#     app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///chat_sessions.db'
#     app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

#     # Initialize the database with the app
#     db.init_app(app)

#     with app.app_context():
#         # Import routes after the app is created to avoid circular imports
#         from . import routes 
#         # This command creates the database tables based on your models.py
#         db.create_all() 

#     return app

# app/__init__.py

from flask import Flask, render_template
from .models import db
from flask_cors import CORS # Import CORS

def create_app():
    app = Flask(__name__)
    CORS(app) # Enable CORS for the entire app
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///chat_sessions.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    with app.app_context():
        from . import routes
        db.create_all()

    # Add a route to serve the frontend
    @app.route('/')
    def index():
        return render_template('index.html')

    return app