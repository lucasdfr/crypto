from peewee import Model

from config import Config


class BaseModel(Model):
    class Meta:
        database = Config.get_database()
