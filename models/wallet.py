from config import Web3Config
import pandas as pd


class Wallet:

    def __init__(self, address):
        self.w3 = Web3Config.get_web3()

        self.address = self.w3.toChecksumAddress(address)
        self.transactions = pd.DataFrame([])
        self.money_received = 0
        self.money_put = 0

    def get_transactions(self, transactions):
        # todo un fois qu'on aura indexé:
        self.transactions = pd.DataFrame(transactions)
        self.transactions['timeStamp'] = pd.to_datetime(self.transactions['timeStamp'], unit='s')
        return self.transactions

    def get_holders(self):
        pass
