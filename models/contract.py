from api import get_abi
from models.w3 import W3


class Contract(W3):
    def __init__(self, address, abi=None):
        """
        :param address: adresse du contrat
        :type address: str
        :param abi: ABI du contrat
        :type abi: str
        """
        super().__init__()
        self.address = self.w3.toChecksumAddress(address)
        self.cache = {}
        if abi is not None:
            self.abi = abi
        else:
            self.abi = get_abi(address)
        self.contract = self.w3.eth.contract(address=self.address, abi=self.abi)

    def call_cache(self, name, function):
        if name in self.cache:
            return self.cache.get(name)
        res = function.call()
        self.cache[name] = res
        return res

    def __repr__(self):
        return f"""Contract {self.address}
        """
