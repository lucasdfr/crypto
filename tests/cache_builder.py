import os
import threading

from web3 import Web3
from web3.middleware import geth_poa_middleware

from cache.utils import get_block
from config import Config

bsc = "https://bsc-dataseed.binance.org/"
w3 = Web3(Web3.HTTPProvider(bsc))
w3.middleware_onion.inject(geth_poa_middleware, layer=0)
Config.init(w3)

# end = w3.eth.blockNumber -1000
end = 23890000 # Dec-14-2022 06:34:29 AM
# start = 22565864  # NEXUS
start = 23590000 # Dec-03-2022 02:43:49 PM +UTC
print("start", start, "end", end)

nb_threads = 8
pt = int((end - start) / nb_threads)
# ok = 0
# for i in range(start, end) :
#     if os.path.exists(f"cache/{i}") :
#         ok = ok +1
#
# print("ok", ok, "total need", end-start, "p ok", 100*(ok/(end-start)))
# exit(0)
class BuildCacheThread(threading.Thread):

    def __init__(self, s, end, name):
        super().__init__()
        self.s = s
        self.end = end
        self.name = name

    def run(self) -> None:
        old_x = 0
        for x in range(self.s, self.end):
            p = round(((x - self.s) / (self.end - self.s)) * 100, 0)
            if p > old_x:
                print(f"Thread {self.name} {p}%")
                old_x = p
            block = get_block(x)


threads = []
for i in range(0, nb_threads):
    t = BuildCacheThread(start, min(start + pt, end ),f"{i}")
    threads.append(t)
    start = start + pt + 1

for t in threads:
    t.start()

for t in threads:
    t.join()
