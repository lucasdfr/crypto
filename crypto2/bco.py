import asyncio
from dataclasses import dataclass

from blacksheep import Application
from eth_utils import to_checksum_address
from web3 import Web3
from web3.middleware import geth_poa_middleware

app = Application()
bsc = "https://bsc-dataseed.binance.org/"
w3 = Web3(Web3.HTTPProvider(bsc))
w3.middleware_onion.inject(geth_poa_middleware, layer=0)
run_task = None

address = to_checksum_address("0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c")

to_print = []
i = 0


@dataclass
class Transaction:
    sender: str
    receiver: str
    hash: str


def analyse_block(block):
    result = []
    for infos in block.transactions:
        receiver = to_checksum_address(infos["to"]) if infos["to"] is not None else None
        t = Transaction(to_checksum_address(infos["from"]), receiver, infos["hash"].hex())
        if t.sender == address or receiver == address:
            print(t)
            result.append(t)
    return result


async def run():
    global to_print, i
    while True:
        i = w3.eth.blockNumber
        result = analyse_block(w3.eth.getBlock(i, True))
        to_print = to_print + result
        await asyncio.sleep(3)


@app.route("/")
def home():
    global run_task
    if run_task is None:
        run_task = asyncio.create_task(run())
    return f"{i}{to_print}"
