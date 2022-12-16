from web3 import Web3
from web3.middleware import geth_poa_middleware

from config import Config
from models.transaction import Transaction

bsc = "https://bsc-dataseed.binance.org/"
w3 = Web3(Web3.HTTPProvider(bsc))
w3.middleware_onion.inject(geth_poa_middleware, layer=0)
Config.init(w3)


