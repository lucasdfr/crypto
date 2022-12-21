import time

from eth_abi import encode_abi, decode_abi
from hexbytes import HexBytes
from web3 import Web3
from web3.middleware import geth_poa_middleware

from config import Config
from models.token import Token

# wallet = "0xcd06AF254D0dA9dbf95F62a75361C4CaB182F13b"
# wallet = "0x0000000000f7cDcB778b0c33b09e175e4786f943"
wallet = "0xcd06AF254D0dA9dbf95F62a75361C4CaB182F13b"

bsc = "https://bsc-dataseed.binance.org/"
w3 = Web3(Web3.HTTPProvider(bsc))
w3.middleware_onion.inject(geth_poa_middleware, layer=0)
Config.init(w3)

# block = w3.eth.get_block('latest', True)
# from_block = 24042882 - 100
from_block = w3.eth.get_block_number() - 100
encoded_wallet = w3.toHex(encode_abi(['address'], [wallet]))
transferEventSignature = w3.toHex(Web3.sha3(text='Transfer(address,address,uint256)'))
# event_filter = w3.eth.filter({"topics": [transferEventSignature, None, encoded_wallet]})
event_filter = w3.eth.filter({"fromBlock": from_block, "topics": [transferEventSignature, None, encoded_wallet]})
#
while True:
    for event in event_filter.get_all_entries():
    # for event in event_filter.get_new_entries():
        decoded_address = decode_abi(['address'], HexBytes(event.topics[2]))  # decoding wallet
        value = decode_abi(['uint256'], HexBytes(event.data))  # decoding event.data

        tokenContractAddress = event.address
        token = Token(tokenContractAddress)

        name = token.get_name()
        symbol = token.get_symbol()


        print(decoded_address, value, name, symbol)
        # getting any token information

        # doing some useful stuff
    break
    time.sleep(2)