from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.executors.pool import ThreadPoolExecutor

from tradingviewbot.trading_models import BNB
from tradingview_ta import TA_Handler, Interval

from trading_utils import sell_all

SCREENER = 'crypto'
EXCHANGE = 'BINANCE'

CONFIG = {

    "DAILY_GOAL": 30,
    "WAITING_TIME": 265000,
    "THRESHOLD": 55
}


def get_signal(interval):
    binance = TA_Handler(
        symbol="BNBUSDT",
        screener=SCREENER,
        exchange=EXCHANGE,
        interval=interval,
    )

    return binance.get_analysis().summary


def percentage(a, b):
    return (100 * a) / (a + b)


def compute_average_signal(min_recommandation, med_recommandation):
    average_buy = (min_recommandation['BUY'] + med_recommandation['BUY']) / 2
    average_sell = (min_recommandation['SELL'] + med_recommandation['SELL']) / 2
    average_neutral = (min_recommandation['NEUTRAL'] + med_recommandation['NEUTRAL']) / 2
    return {
        "BUY": average_buy,
        "SELL": average_sell,
        "NEUTRAL": average_neutral,
    }


def compute_amount(wallet_balance):
    amount = round(0.1 * wallet_balance, 2)
    if amount < 10:
        amount = 10
    return amount


def strategy_trade_view(wallet, token, recommandations, threshold):
    amount = compute_amount(wallet.current_balance)
    if recommandations['BUY'] > recommandations['SELL'] and percentage(recommandations['BUY'],
                                                                       recommandations['SELL']) > threshold:
        globals()[f'{wallet.strategy_of_bet}'](wallet, token, amount)
    elif recommandations['SELL'] > recommandations['BUY'] and percentage(recommandations['SELL'],
                                                                         recommandations['BUY']) > threshold:
        globals()[f'{wallet.strategy_of_bet}'](wallet, token, amount, 'sell')
    else:
        if recommandations['BUY'] > recommandations['SELL']:
            print(f"low percentage {percentage(recommandations['BUY'], recommandations['SELL'])}%")
        else:
            globals()[f'{wallet.strategy_of_bet}'](wallet, token, amount, 'sell')


def trade_view(wallet, token):
    bnb_price = BNB.create().value
    print(bnb_price)
    min_recommandation = get_signal(Interval.INTERVAL_1_MINUTE)
    med_recommandation = get_signal(Interval.INTERVAL_5_MINUTES)
    recommandations = compute_average_signal(min_recommandation, med_recommandation)
    strategy_trade_view(wallet, token, recommandations, CONFIG['THRESHOLD'])


def main_trade_view(wallet, token):
    scheduler = BlockingScheduler(timezone='Europe/Paris', executors={'default': ThreadPoolExecutor(1)})
    scheduler.add_job(trade_view, "interval", seconds=4.5, misfire_grace_time=30, max_instances=10000,
                      kwargs={'wallet': wallet, 'token': token})
    scheduler.start()
