# config.py
class Config:
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = "mysql+mysqlconnector://{username}:{password}@{hostname}/{databasename}".format(
        username="funk0r",
        password="Timbersaw2025!",
        hostname="funk0r.mysql.pythonanywhere-services.com",
        databasename="funk0r$kochrezepte",
    )
    SQLALCHEMY_POOL_RECYCLE = 299
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = 'dein_geheimes_schluessel'
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_recycle": 280,
        "pool_pre_ping": True,
    }