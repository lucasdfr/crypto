from models.w3 import W3


class Contract(W3):
    def __init__(self, address, abi):
        """
        :param address: adresse du contrat
        :type address: str
        :param abi: ABI du contrat
        :type abi: str
        """
        super().__init__()
        # self.w3 = Web3Config.get_web3()
        self.address = self.w3.toChecksumAddress(address)
        self.cache = {}
        self.abi = abi
        self.contract = self.w3.eth.contract(address=self.address, abi=self.abi)

    def call_cache(self, name, function):
        if name in self.cache:
            return self.cache.get(name)
        res = function.call()
        self.cache[name] = res
        return res
