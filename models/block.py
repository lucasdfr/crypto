import os
import pickle

from peewee import IntegerField, BooleanField

from models.w3 import W3

BLOCKS_PATH = "data/_blocks"


class Block(W3):
    number = IntegerField(primary_key=True)
    parsed = BooleanField(default=False)

    def _get_file_path(self):
        return f"{BLOCKS_PATH}/{self.number}"

    def get_infos(self):
        if os.path.exists(self._get_block_cache_path()):
            with open(self._get_block_cache_path(), "rb") as file:
                return pickle.load(file)
        data = self.w3.eth.getBlock(self.number, True)
        with open(self._get_block_cache_path(), "wb+") as file:
            pickle.dump(data, file)
        return data
