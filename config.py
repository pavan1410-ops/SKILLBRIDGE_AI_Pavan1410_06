import os


class Config:

    SECRET_KEY = os.getenv(
        "SECRET_KEY",
        "skillbridge-development-secret-key"
    )

    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        "sqlite:///skillbridge.db"
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False