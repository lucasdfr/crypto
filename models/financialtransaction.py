from api import get_abi
from models.contract import Contract
from models.transaction import Transaction


class FinancialTransaction(Transaction):

    def __init__(self, address):
        super().__init__(address)
        self.timestamp = self.get_timestamp()
        self.is_internal = self.is_internal()
        self.decoded_logs = None
        self.status=0

    def get_timestamp(self):
        self.timestamp = self.w3.eth.get_block(self.block_number)['timestamp']
        return self.timestamp

    def is_internal(self):
        self.is_internal = self.w3.eth.get_code(self.receiver).hex() != '0x' if self.receiver is not None else False
        return self.is_internal

    def decoded_logs(self):
        if self.is_internal and self.receipt is None:
            self.receipt = self.get_receipt()
            log = self.receipt['logs'][0]
            # smart_contract = self.receipt["address"]
            # abi = get_abi(log["address"])
            contract = Contract(self.w3.toChecksumAddress(self.receipt["address"]), get_abi(log["address"]))
