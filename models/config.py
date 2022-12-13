class Web3Config(object):
    w3 = None

    @staticmethod
    def init(w3):
        Web3Config.w3 = w3

    @staticmethod
    def get_web3():
        if Web3Config.w3 is None:
            raise Exception("Missing w3 configuration")
        return Web3Config.w3
