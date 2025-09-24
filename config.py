# App configuration (DB URI, secret key, etc.)
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = "super-secret-key"
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.join(BASE_DIR, 'instance', 'app.sqlite')}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
