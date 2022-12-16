from peewee import SqliteDatabase


class Config(object):
    w3 = None
    database = SqliteDatabase("data/database.sqlite")  # Base de donnee de stockage
    models = []

    @staticmethod
    def init(w3, models=[]):
        Config.w3 = w3
        Config.database.connect()
        Config.database.create_tables(models)

    @staticmethod
    def get_web3():
        if Config.w3 is None:
            raise Exception("Missing w3 configuration")
        return Config.w3

    @staticmethod
    def get_database():
        return Config.database
