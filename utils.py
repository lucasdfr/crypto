from models.pancakeswap import PancakeSwapRouter
from models.pool import Pool
from models.wallet import Wallet
from models.token import Token


def exchange_rate(psr: PancakeSwapRouter, pool: Pool):
    decimals = 10 ** 18
    reserves = pool.get_reserves()
    return [psr.get_amount_out(decimals, reserves[0], reserves[1]) / decimals, reserves[1] / reserves[0]]


def is_pancake_swap_router(address):
    return address == PancakeSwapRouter().address


def is_wallet(address: str, w3):
    return w3.eth.get_code(address).hex() == '0x'


def is_pool(address: str):
    try:
        symbol = Token(address).get_symbol()
        return symbol == PancakeSwapRouter().SYMBOL
    except:
        return False


def is_token(address: str):
    try:
        symbol = Token(address).get_symbol()
        return symbol != PancakeSwapRouter().SYMBOL
    except:
        return False


def get_type_by_address(address: str, w3):
    if is_wallet(address, w3):
        return Wallet(address)
    if is_token(address):
        return Token(address)
    if is_pancake_swap_router(address):
        return PancakeSwapRouter()
    if is_pool(address):
        return Pool(address)
