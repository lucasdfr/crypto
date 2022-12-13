import os
import pickle

from cache import BLOCKS_PATH


def _get_block_cache_path(n):
    return f"{BLOCKS_PATH}/{n}"


def get_block(n):
    if os.path.exists(_get_block_cache_path(n)):
        with open(_get_block_cache_path(n), "r") as file:
            return pickle.load(file)
    # data =
