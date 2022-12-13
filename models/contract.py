class Contract:
    def __init__(self, w3, address, abi):
        """
        :param w3: connection Web3
        :type w3: web3.Web3
        :param address: adresse du contrat
        :type address: str
        :param abi: ABI du contrat
        :type abi: str
        """
        self.w3 = w3
        self.address = w3.toChecksumAddress(address)
        self.cache = {}
        self.abi = abi
        self.contract = w3.eth.contract(address=self.address, abi=self.abi)

    def call_cache(self, name, function):
        if name in self.cache:
            return self.cache.get(name)
        res = function.call()
        self.cache[name] = res
        return res