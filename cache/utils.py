import os
import pickle

from cache import BLOCKS_PATH
from config import Config


def _get_block_cache_path(n):
    return f"{BLOCKS_PATH}/{n}"


def get_block(n):
    if os.path.exists(_get_block_cache_path(n)):
        with open(_get_block_cache_path(n), "rb") as file:
            return pickle.load(file)
    data = Config.get_web3().eth.getBlock(n, True)
    with open(_get_block_cache_path(n), "wb+") as file:
        pickle.dump(data, file)
    return data
