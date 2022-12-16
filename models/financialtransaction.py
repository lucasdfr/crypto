from api import get_abi
from models.contract import Contract
from models.transaction import Transaction
from models.transfer import Transfer
from utils import get_type_by_address


class FinancialTransaction(Transaction):

    def __init__(self, address: str):
        super().__init__(address)
        self.timestamp = self.get_timestamp()
        self.is_internal = self.is_internal()
        self.decoded_logs = []
        self.status = 0
        self.value = 0
        self.fees = 0
        self.type = None
        self.unit = 'BNB'

    def get_timestamp(self):
        return self.w3.eth.get_block(self.block_number)['timestamp']

    def get_status(self):
        if self.receipt is None:
            self.get_receipt()
        self.status = self.receipt['status']
        return self.status

    def is_internal(self) -> bool:
        return self.w3.eth.get_code(self.receiver).hex() != '0x' if self.receiver is not None else False

    def get_receiver(self):
        self.receiver = get_type_by_address(self.receiver, self.w3)
        return self.receiver

    def get_sender(self):
        self.sender = get_type_by_address(self.sender, self.w3)
        return self.sender

    def get_decoded_logs(self) -> list:
        if len(self.decoded_logs) > 0:
            return self.decoded_logs
        if self.is_internal:
            if self.receipt is None:
                self.get_receipt()
            log = self.receipt['logs'][0]
            contract = Contract(self.w3.toChecksumAddress(log["address"]), get_abi(log["address"]))
            decoded_logs = list(contract.contract.events.Transfer().processReceipt(self.receipt))
            for decoded_log in decoded_logs:
                transfer = Transfer(decoded_log['args'])
                transfer.get_sender()
                transfer.get_receiver()
                self.decoded_logs += [transfer]
            return self.decoded_logs
        return []
