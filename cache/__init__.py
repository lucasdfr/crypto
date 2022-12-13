import os
CACHE_PATH = "cache"
BLOCKS_PATH =  f"{CACHE_PATH}/_blocks"
if not os.path.exists(BLOCKS_PATH):
    os.mkdir(BLOCKS_PATH)
