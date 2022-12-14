import rlp
from eth_utils import keccak, to_checksum_address, to_bytes, is_checksum_address

from config import Web3Config
from models.contract import Contract


class Transaction:
    def __init__(self, address):
        """
        :param address: adresse de la transaction
        :type address: str
        """
        self.w3 = Web3Config.get_web3()
        self.cache = {}

        transaction_dict = self.get_transaction(address)
        self.nonce = transaction_dict["nonce"]
        self.sender = to_checksum_address(transaction_dict["from"])
        to_addr = transaction_dict["to"]
        self.receiver = to_checksum_address(to_addr) if to_addr is not None else None
        self.receiver = None
        self.block_number = transaction_dict["blockNumber"]
        self.gas = transaction_dict["gas"]
        self.gas_price = transaction_dict["gasPrice"]
        self.hash = transaction_dict["hash"].hex()
        self.index = transaction_dict["transactionIndex"]
        self.receipt = None
        self.logs = None


    def get_transaction(self, address):
        return self.w3.eth.get_transaction(address)

    def get_receipt(self):
        if self.receipt is not None:
            return self.receipt
        self.receipt = self.w3.eth.get_transaction_receipt(self.hash)
        return self.receipt

    def get_logs(self, contract: Contract):
        r = self.get_receipt()
        self.logs = contract.contract.events.Transfer().processReceipt(r)
        return self.logs

    def is_contract_creation(self) -> bool:
        return self.receiver is None

    def created_contract_address(self) -> str:
        if not self.is_contract_creation():
            raise Exception("Transaction is not a contract creation")
        sender_bytes = to_bytes(hexstr=self.sender)
        raw = rlp.encode([sender_bytes, self.nonce])
        return to_checksum_address(keccak(raw)[12:])

    def contains_address(self, address: str) -> bool:
        if not is_checksum_address(address):
            raise Exception(f"{address} is not a checksum address")
        if self.sender == address:
            return True
        if self.receiver is None:
            return self.created_contract_address() == address
        return self.receiver == address

    def __repr__(self):
        return f"""Transaction {self.hash}
        \tFrom : {self.sender}
        \tTo : {self.receiver}
        """
