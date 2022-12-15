from config import Web3Config
from models.w3 import W3

from utils import get_type_by_address


class Transfer(W3):

    def __init__(self, args: dict):
        super().__init__()
        self.value = None
        self.sender = None
        self.receiver = None
        self.get_transfer(args)


    def get_receiver(self):
        self.receiver = get_type_by_address(self.receiver, self.w3)
        return self.receiver

    def get_sender(self):
        self.sender = get_type_by_address(self.sender, self.w3)
        return self.sender

    def get_transfer(self, args: dict):
        if 'src' in args:
            self.sender = args['src']
        else:
            self.sender = args['from']
        if 'dst' in args:
            self.receiver = args['dst']
        else:
            self.receiver = args['to']
        if 'wad' in args:
            self.value = args['wad']
        else:
            self.value = args['value']

    def __repr__(self):
        return f"""Transfer 
        \tFrom : {self.sender}
        \tTo : {self.receiver}
        """
