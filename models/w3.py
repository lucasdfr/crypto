from config import Config


class W3:
    def __init__(self):
        self.w3 = Config.get_web3()
