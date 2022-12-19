from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.executors.pool import ThreadPoolExecutor, ProcessPoolExecutor

from peewee import *
import datetime

from tradingview_ta import TA_Handler, Interval

from api import get_bnb_price

db = SqliteDatabase("../data/database.sqlite")


class BaseModel(Model):
    class Meta:
        database = db


class Wallet(BaseModel):
    number = IntegerField()
    balance_dollar = FloatField()
    balance_bnb = FloatField(default=0)
    balance_initial = FloatField()
    base_trade_amount = FloatField()
    potential_win = FloatField(default=0)
    strategy_of_bet = CharField(default='sell_all')

    def __str__(self):
        return f"""Bet wallet {self.number}: balance_dollar: {self.balance_dollar} balance_bnb: {self.balance_bnb} potential_win: {self.potential_win}"""


class TradingBotHistory(BaseModel):
    wallet = ForeignKeyField(Wallet, backref='transactions')
    timestamp = DateTimeField(default=datetime.datetime.now)
    method = CharField()
    amount = FloatField()
    status = BooleanField()
    status_detail = CharField()
    bnb_price = FloatField()

    def __str__(self):
        return f"""--- Transaction of amount: {self.amount} bnb_price: {self.bnb_price} method: {self.method} status: {self.status} status_detail: {self.status_detail}"""


db.connect()
# db.create_tables([Wallet, TradingBotHistory])

SCREENER = 'crypto'
EXCHANGE = 'BINANCE'
BASE_AMOUNT = 1000
WALLET_NUMBER = 0

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


def save_history(wallet, amount, method, status, status_detail, bnb_price):
    trading_bot = TradingBotHistory.create(wallet=wallet, amount=amount, method=method, status=status,
                                           status_detail=status_detail, bnb_price=bnb_price)
    trading_bot.save()
    print(TradingBotHistory.get(id=trading_bot))


def bet_all(wallet, bnb_price, method='buy'):
    if method == 'buy':
        if wallet.balance_dollar > 0:
            status = 1
            status_detail = 'success'
            wallet.balance_bnb = wallet.balance_dollar / bnb_price
            wallet.balance_dollar = 0
            wallet.potential_win = wallet.balance_bnb * bnb_price - wallet.balance_initial
            wallet.save()
        else:
            status = 0
            status_detail = 'Not enough reserve on account'

    else:
        if wallet.balance_bnb > 0:
            status = 1
            status_detail = 'success'
            wallet.balance_dollar = wallet.balance_bnb * bnb_price
            wallet.balance_bnb = 0
            wallet.potential_win = wallet.balance_dollar - wallet.balance_initial
            wallet.save()
        else:
            status = 0
            status_detail = 'Not enough reserve on account'
    save_history(wallet, wallet.base_trade_amount / bnb_price, method, status, status_detail, bnb_price)
    print(wallet)


def sell_all(wallet, bnb_price, method='buy'):
    if method == 'buy':
        balance_dollar = wallet.balance_dollar - wallet.base_trade_amount
        if balance_dollar > 0:
            status = 1
            status_detail = 'success'
            balance_bnb = wallet.balance_bnb + wallet.base_trade_amount / bnb_price
            wallet.balance_dollar = balance_dollar
            wallet.balance_bnb = balance_bnb
            wallet.potential_win = balance_dollar + balance_bnb * bnb_price - wallet.balance_initial
            wallet.save()

        else:
            status = 0
            status_detail = 'Not enough reserve on account'
    else:
        if wallet.balance_bnb > 0:
            status = 1
            status_detail = 'success'
            wallet.balance_dollar = wallet.balance_bnb * bnb_price
            wallet.balance_bnb = 0
            wallet.potential_win = wallet.balance_dollar - wallet.balance_initial
            wallet.save()
        else:
            status = 0
            status_detail = 'Not enough reserve on account'
    save_history(wallet, wallet.base_trade_amount / bnb_price, method, status, status_detail, bnb_price)
    print(wallet)


def strategy(wallet, recommandations, threshold):
    bnb_price = get_bnb_price()
    if recommandations['BUY'] > recommandations['SELL'] and percentage(recommandations['BUY'],
                                                                       recommandations['SELL']) > threshold:
        globals()[f'{wallet.strategy_of_bet}'](wallet, bnb_price)
        # bet_all(wallet, bnb_price)
    elif recommandations['SELL'] > recommandations['BUY'] and percentage(recommandations['SELL'],
                                                                         recommandations['BUY']) > threshold:
        globals()[f'{wallet.strategy_of_bet}'](wallet, bnb_price, 'sell')
    else:
        if recommandations['BUY'] > recommandations['SELL']:
            print(f"low percentage {percentage(recommandations['BUY'], recommandations['SELL'])}%")
        else:
            print(f"low percentage {percentage(recommandations['SELL'], recommandations['BUY'])}%")


wallet = Wallet.create(number=WALLET_NUMBER, balance_initial=BASE_AMOUNT, balance_dollar=BASE_AMOUNT,
                       base_trade_amount=4).save()


def trade():
    wallet = Wallet.get(number=WALLET_NUMBER)
    min_recommandation = get_signal(Interval.INTERVAL_1_MINUTE)
    med_recommandation = get_signal(Interval.INTERVAL_5_MINUTES)
    recommandations = compute_average_signal(min_recommandation, med_recommandation)
    strategy(wallet, recommandations, CONFIG['THRESHOLD'])


scheduler = BlockingScheduler(timezone='Europe/Paris', executors={'default': ThreadPoolExecutor(1)})
scheduler.add_job(trade, "interval", seconds=4.5, misfire_grace_time=30, max_instances=10000)
scheduler.start()
