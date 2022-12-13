import threading

from web3 import Web3
from web3.middleware import geth_poa_middleware

from cache.utils import get_block
from config import Web3Config

bsc = "https://bsc-dataseed.binance.org/"
w3 = Web3(Web3.HTTPProvider(bsc))
w3.middleware_onion.inject(geth_poa_middleware, layer=0)
Web3Config.init(w3)

end = w3.eth.blockNumber
start = 22565864  # NEXUS
print("start", start, "end", end)

nb_threads = 8
pt = int((end - start) / nb_threads)


class BuildCacheThread(threading.Thread):

    def __init__(self, s, end, name):
        super().__init__()
        self.s = s
        self.end = end
        self.name = name

    def run(self) -> None:
        old_x = 0
        for x in range(self.s, self.end):
            p = round(((x - self.s) / (end - self.s)) * 100, 0)
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
