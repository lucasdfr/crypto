from models.pancakeswap import PancakeSwapRouter
from models.pool import Pool


def exchange_rate(psr: PancakeSwapRouter, pool: Pool):
    decimals = 10 ** 18
    reserves = pool.get_reserves()
    return [psr.get_amount_out(decimals, reserves[0], reserves[1]) / decimals, reserves[1] / reserves[0]]
