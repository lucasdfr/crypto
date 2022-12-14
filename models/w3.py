from config import Web3Config


class W3:
    def __init__(self):
        self.w3 = Web3Config.get_web3()
