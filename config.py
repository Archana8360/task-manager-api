import os
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()

class Config:
    """Base configuration settings."""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'a_default_hardcoded_secret_key'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///tasks.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class TestingConfig(Config):
    """Configuration for testing."""
    TESTING = True
    # Use an in-memory SQLite database for fast, isolated tests
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

