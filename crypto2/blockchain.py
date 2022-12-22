from web3 import Web3
from web3.middleware import geth_poa_middleware


class Blockchain:

    def __init__(self, blockchain='binance'):
        if blockchain == 'binance':
            bsc = "https://bsc-dataseed.binance.org/"
            self.w3 = Web3(Web3.HTTPProvider(bsc))
            self.w3.middleware_onion.inject(geth_poa_middleware, layer=0)
