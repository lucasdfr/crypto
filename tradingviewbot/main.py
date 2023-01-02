from web3 import Web3
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.executors.pool import ThreadPoolExecutor, ProcessPoolExecutor

from trading_models import Wallet, TradingBotHistory, Token, TokenValue, BNB

from tradingview_ta import TA_Handler, Interval

from api import get_bnb_price
from utils import get_value_of_token
from models.token import Token as TokenClass

from config import Config

bsc = "https://bsc-dataseed.binance.org/"
w3 = Web3(Web3.HTTPProvider(bsc))
Config.init(w3)

SCREENER = 'crypto'
EXCHANGE = 'BINANCE'
BASE_AMOUNT = 1000

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
                                           status_detail=status_detail)
    trading_bot.save()
    print(TradingBotHistory.get(id=trading_bot))


def bet(wallet, token, amount, method='buy', token_value=None, token_balance=None):
    if token_value is None:
        if token.symbol == 'WBNB':
            token_value = 0.1
        else:
            token_value = get_value_of_token(TokenClass(token.address))[0]
    if token_balance is None:
        token_balance = TokenValue.get_token_balance(token, wallet)
    if method == 'buy':
        current_balance = wallet.current_balance - amount
        if current_balance > 0:
            status = 1
            status_detail = 'success'
            wallet.current_balance = current_balance
            token_balance = token_balance + amount / token_value
            TokenValue.create(token=token, wallet=wallet, current_balance=token_balance, value=token_value).save()
            wallet.save()
        else:
            if wallet.current_balance > 0:
                status = 1
                status_detail = 'success'
                wallet.current_balance = 0
                token_balance = token_balance + wallet.current_balance / token_value
                TokenValue.create(token=token, wallet=wallet, current_balance=token_balance, value=token_value).save()
                wallet.save()
            else:
                status = 0
                status_detail = 'Not enough reserve on account'
    else:
        if token_balance - amount / token_value > 0:
            status = 1
            status_detail = 'success'
            wallet.current_balance = wallet.current_balance + amount
            token_balance = token_balance - amount / token_value
            TokenValue.create(token=token, wallet=wallet, current_balance=token_balance, value=token_value).save()
            wallet.save()
        else:
            if token_balance > 0:
                status = 1
                status_detail = 'success'
                wallet.current_balance = wallet.current_balance + token_balance * token_value
                token_balance = 0
                TokenValue.create(token=token, wallet=wallet, current_balance=token_balance, value=token_value).save()
                wallet.save()
            else:
                status = 0
                status_detail = 'Not enough reserve on account'

    bnb_price = BNB.select().order_by(BNB.id.desc()).get().value
    print(bnb_price)
    save_history(wallet, amount, method, status, status_detail, bnb_price)


def bet_all(wallet, token, method='buy'):
    bet(wallet, token, wallet.current_balance, method)


def sell_all(wallet, token, trade_amount, method='buy'):
    if method == 'buy':
        bet(wallet, token, trade_amount, method)
    else:
        if token.symbol == 'WBNB':
            token_value = 0.1
        else:
            token_value = get_value_of_token(TokenClass(token.address))[0]
        token_balance = TokenValue.get_token_balance(token, wallet)
        bet(wallet, token, trade_amount, method, token_balance * token_value, token_value)


# def sell_all(wallet, bnb_price, method='buy'):
#     if method == 'buy':
#         balance_dollar = wallet.balance_dollar - wallet.base_trade_amount
#         if balance_dollar > 0:
#             status = 1
#             status_detail = 'success'
#             balance_bnb = wallet.balance_bnb + wallet.base_trade_amount / bnb_price
#             wallet.balance_dollar = balance_dollar
#             wallet.balance_bnb = balance_bnb
#             wallet.potential_win = balance_dollar + balance_bnb * bnb_price - wallet.balance_initial
#             wallet.save()
#
#         else:
#             status = 0
#             status_detail = 'Not enough reserve on account'
#             wallet.potential_win = wallet.balance_dollar + wallet.balance_bnb * bnb_price - wallet.balance_initial
#             wallet.save()
#         save_history(wallet, wallet.base_trade_amount / bnb_price, method, status, status_detail, bnb_price)
#
#     else:
#         if wallet.balance_bnb > 0:
#             status = 1
#             status_detail = 'success'
#             wallet.balance_dollar = wallet.balance_dollar + wallet.balance_bnb * bnb_price
#             wallet.balance_bnb = 0
#             wallet.potential_win = wallet.balance_dollar - wallet.balance_initial
#             wallet.save()
#         else:
#             status = 0
#             status_detail = 'Not enough reserve on account'
#             wallet.potential_win = wallet.balance_dollar + wallet.balance_bnb * bnb_price - wallet.balance_initial
#             wallet.save()
#         save_history(wallet, wallet.balance_dollar, method, status, status_detail, bnb_price)
#     print(wallet)


def strategy_trade_view(wallet, token, recommandations, threshold):
    bnb_price = get_bnb_price()
    if recommandations['BUY'] > recommandations['SELL'] and percentage(recommandations['BUY'],
                                                                       recommandations['SELL']) > threshold:
        globals()[f'{wallet.strategy_of_bet}'](wallet, token, bnb_price)
        # bet_all(wallet, bnb_price)
    elif recommandations['SELL'] > recommandations['BUY'] and percentage(recommandations['SELL'],
                                                                         recommandations['BUY']) > threshold:
        globals()[f'{wallet.strategy_of_bet}'](wallet, token, bnb_price, 'sell')
    else:
        if recommandations['BUY'] > recommandations['SELL']:
            print(f"low percentage {percentage(recommandations['BUY'], recommandations['SELL'])}%")
        else:
            globals()[f'{wallet.strategy_of_bet}'](wallet, token, bnb_price, 'sell')


wallet = Wallet.create(current_balance=BASE_AMOUNT, initial_balance=BASE_AMOUNT,
                       ).save()

wbnb, created = Token.get_or_create(name='Wrapped BNB', symbol='WBNB',
                                    address="0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c")
wbnb_value = TokenValue.create(token=wbnb, wallet=wallet).save()


def trade():
    BNB.create().value
    wallet_1 = Wallet.select().order_by(Wallet.id.desc()).get()
    min_recommandation = get_signal(Interval.INTERVAL_1_MINUTE)
    med_recommandation = get_signal(Interval.INTERVAL_5_MINUTES)
    recommandations = compute_average_signal(min_recommandation, med_recommandation)
    bet(wallet_1, wbnb, 1, method='sell')

    strategy_trade_view(wallet, wbnb, recommandations, CONFIG['THRESHOLD'])


#
scheduler = BlockingScheduler(timezone='Europe/Paris', executors={'default': ThreadPoolExecutor(1)})
scheduler.add_job(trade, "interval", seconds=4.5, misfire_grace_time=30, max_instances=10000)
scheduler.start()
