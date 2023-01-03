from statistics import pvariance

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.executors.pool import ThreadPoolExecutor

from tradingviewbot.trading_view import compute_amount

from utils import get_value_of_token
from models.token import Token as TokenClass

from trading_utils import sell_all

THRESHOLD = 0.2


def high_variation(wallet, token):
    amount = compute_amount(wallet.current_balance)
    token_value = get_value_of_token(TokenClass(token.address))[0]
    variations += [token_value]
    if pvariance(variations) > THRESHOLD:
        globals()[f'{wallet.strategy_of_bet}'](wallet, token, amount)
    elif pvariance(variations) < THRESHOLD:
        globals()[f'{wallet.strategy_of_bet}'](wallet, token, amount, 'sell')
    else:
        print("Do Nothing")


def main_high_variation(wallet, token):
    global variations
    variations = []
    scheduler = BlockingScheduler(timezone='Europe/Paris', executors={'default': ThreadPoolExecutor(1)})
    scheduler.add_job(high_variation, "interval", seconds=4.5, misfire_grace_time=30, max_instances=10000,
                      kwargs={'wallet': wallet, 'token': token})
    scheduler.start()
