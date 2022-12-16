from models.busd import BUSD
from models.pancakeswap import PancakeSwapRouter, PancakeSwapFactory
from models.pool import Pool
from models.wallet import Wallet
from models.token import Token
from models.wbnb import WBNB


def exchange_rate(psr: PancakeSwapRouter, pool: Pool):
    decimals = 10 ** 18
    reserves = pool.get_reserves()
    if reserves[1] > reserves[0]:
        return [psr.get_amount_out(decimals, reserves[1], reserves[0]) / decimals, reserves[0] / reserves[1]]
    else:
        return [psr.get_amount_out(decimals, reserves[0], reserves[1]) / decimals, reserves[1] / reserves[0]]


def get_value_of_token(token: Token, unit='WBNB'):
    ref_token = WBNB()
    psr = PancakeSwapRouter()
    if unit != 'WBNB':
        ref_token = BUSD()
    pool = PancakeSwapFactory(psr).get_pool(token, ref_token)
    print(pool)
    # print(0xf33f8f76c790e1da5e8acf8b21a2334b4697625b)
    # pool=Pool("0x0f1f63626b7b59358275d388d721b7db98211eec")
    return exchange_rate(psr, pool)


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
