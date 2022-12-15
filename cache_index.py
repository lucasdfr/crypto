import os

from cache import BLOCKS_PATH, CACHE_PATH

beg = None
before = None

with open(f"{CACHE_PATH}/block_index", "w+") as index_file:
    for f in os.listdir(BLOCKS_PATH):
        if f == "index":
            continue
        f = int(f)
        if beg is None:
            beg = f
            before = f
            continue
        if f != before + 1:
            if beg == before:
                index_file.write(f"{beg}\n")
            else:
                index_file.write(f"{beg}-{before}\n")
            beg = f
        before = f
