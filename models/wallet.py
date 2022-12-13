from models.config import Web3Config

class Wallet:

    def __init__(self, address):
        self.address=address
        self.holders=[]
