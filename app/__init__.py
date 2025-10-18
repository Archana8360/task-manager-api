from flask import Flask
from flasgger import Swagger
from config import Config
from .extensions import db
from .auth import auth as auth_blueprint
from .routes import main as main_blueprint

def create_app(config_class=Config):
    """
    Application factory function to create and configure the Flask app.
    """
    app = Flask(__name__)
    app.config.from_object(config_class)

    # --- Swagger Configuration Template ---
    # This template defines the overall structure of your API documentation,
    # including the crucial 'definitions' section for your models.
    template = {
        "swagger": "2.0",
        "info": {
            "title": "Task Manager API",
            "description": "A RESTful API for managing tasks.",
            "version": "1.0.0"
        },
        "securityDefinitions": {
            "ApiKeyAuth": {
                "type": "apiKey",
                "name": "x-access-token",
                "in": "header",
                "description": "JWT token for authentication (e.g., eyJhbGciOiJIUzI1Ni...)"
            }
        },
        "definitions": {
            "Task": {
                "type": "object",
                "properties": {
                    "id": {"type": "integer", "description": "The unique task identifier."},
                    "title": {"type": "string", "description": "The title of the task."},
                    "description": {"type": "string", "description": "The task's description."},
                    "completed": {"type": "boolean", "description": "Whether the task is complete."},
                    "created_at": {"type": "string", "format": "date-time", "description": "Timestamp of task creation."},
                    "updated_at": {"type": "string", "format": "date-time", "description": "Timestamp of last update."},
                    "user_id": {"type": "integer", "description": "The ID of the owner user."}
                }
            },
            "UserRegistration": {
                "type": "object",
                "properties": {
                    "username": {"type": "string", "example": "newuser"},
                    "password": {"type": "string", "example": "strongpassword123"}
                },
                "required": ["username", "password"]
            },
            "UserLogin": {
                "type": "object",
                "properties": {
                    "username": {"type": "string", "example": "newuser"},
                    "password": {"type": "string", "example": "strongpassword123"}
                },
                "required": ["username", "password"]
            }
        }
    }

    # Initialize extensions with the app instance
    db.init_app(app)
    
    # Initialize Flasgger with the template
    Swagger(app, template=template)

    # Register blueprints to organize routes
    app.register_blueprint(auth_blueprint, url_prefix='/auth')
    app.register_blueprint(main_blueprint)

    with app.app_context():
        db.create_all()

    return app

