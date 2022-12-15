class Config(object):
    w3 = None

    @staticmethod
    def init(w3):
        Config.w3 = w3

    @staticmethod
    def get_web3():
        if Config.w3 is None:
            raise Exception("Missing w3 configuration")
        return Config.w3

