# config.py
from decouple import config

class Config:
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = "mysql+mysqlconnector://{username}:{password}@{hostname}/{databasename}".format(
        username=config("DB_USERNAME"),
        password=config("DB_PASSWORD"),
        hostname=config("DB_HOSTNAME"),
        databasename=config("DB_NAME"),
    )
    SQLALCHEMY_POOL_RECYCLE = 299
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = config("SECRET_KEY")
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_recycle": 280,
        "pool_pre_ping": True,
    }