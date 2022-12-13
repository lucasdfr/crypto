from web3 import Web3
from web3.middleware import geth_poa_middleware

from cache.utils import get_block
from config import Web3Config
from models.pancakeswap import PancakeSwapRouter, PancakeSwapFactory
from models.token import Token
from models.transaction import Transaction

bsc = "https://bsc-dataseed.binance.org/"
w3 = Web3(Web3.HTTPProvider(bsc))
w3.middleware_onion.inject(geth_poa_middleware, layer=0)
Web3Config.init(w3)

nexus = Token("NEXUS")
primal = Token("PRIMAL")
busd = Token("BUSD")

psr = PancakeSwapRouter()
psf = PancakeSwapFactory(psr)
nexus_bnb_pool = psf.get_pool(nexus, psr.wbnb())
primal_busd = psf.get_pool(nexus, psr.wbnb())


end = w3.eth.blockNumber
# start = end - (10**3)
start = 22565864 #NEXUS
# start = 149268  # WBNB
# start = 23199393

tx_dictionary = {}
# address = "0xeFdb93E14cd63B08561e86D3a30aAE0f3AaBaD9a" #NEXUS
address = psr.wbnb().address
# address = "0x3359b8287b4493a9318cff272468006284a01aa6"
# address = "0x6ac7ea33f8831ea9dcc53393aaa88b25a785dbf0"
old_x = 0

# transaction_d = w3.eth.get_transaction("0x8bea5793a89b80c718fbdf4f1551c1132aec6408b1b85ac67d7d401677899beb")
# t = Transaction(transaction_d)

# print(t.get_logs(nexus))


# exit(0)
result = []

for x in range(start, end):
    p = round(((x - start) / (end - start)) * 100, 0)
    if p > old_x:
        print(f"{p}%")
        old_x = p
    # block = w3.eth.getBlock(x, True)
    block = get_block(x)
    # for transaction_d in block.transactions:
    #     t = Transaction(transaction_d)
    #     if t.contains_address(address):
    #         print(t.hash)
    #         result.append(t.hash)
