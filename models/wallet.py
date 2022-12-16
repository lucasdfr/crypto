import pandas as pd
from models.w3 import W3


class Wallet(W3):

    def __init__(self, address: str):
        super().__init__()
        self.address = self.w3.toChecksumAddress(address)
        self.current_balance = self.get_balance()

        self.transactions = pd.DataFrame([])
        self.money_received = 0
        self.money_put = 0

    def get_transactions(self, transactions):
        # todo un fois qu'on aura indexé:
        self.transactions = pd.DataFrame(transactions)
        self.transactions['timeStamp'] = pd.to_datetime(self.transactions['timeStamp'], unit='s')
        return self.transactions

    def get_balance(self) -> float:
        self.current_balance = self.w3.eth.get_balance(self.address)
        return self.current_balance

    def __repr__(self):
        return f"""Wallet {self.address}
        \tBalance : {self.current_balance}
        """
