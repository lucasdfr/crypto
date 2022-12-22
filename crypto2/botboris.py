from api import get_bnb_price
from crypto2.bet import Bet
from crypto2.blockchain import Blockchain
from crypto2.tissou import Tissou
from tradingview_ta import TA_Handler, Interval

from utils import percentage


class BotBoris(Tissou, Blockchain, Bet):
    """
    Implémentation du bot de boris avec les classes
    todo:finaliser le bot, permettre qu'il s'exécute en direct, qu'il puisse s'abonner à d'autres tokens, faire des stratégies plus complexes, etc
    """

    def __init__(self, initial_balance, screener, blockchain, symbol, threshold):
        super().__init__(initial_balance)
        self.screener = screener
        self.blockchain = blockchain
        self.symbol = symbol
        self.threshold = threshold

        self.token_price = 0
        self.wallet = ""

    def get_token_price(self):
        self.token_price = get_bnb_price()
        return self.token_price

    def strategy(self, recommandations):
        if recommandations['BUY'] > recommandations['SELL'] and percentage(recommandations['BUY'],
                                                                           recommandations['SELL']) > threshold:
            return 'up'
            # bet_all(wallet, bnb_price)
        elif recommandations['SELL'] > recommandations['BUY'] and percentage(recommandations['SELL'],
                                                                             recommandations['BUY']) > threshold:
            return 'down'
        else:
            if recommandations['BUY'] > recommandations['SELL']:
                return 'neutral'
            else:
                return 'down'

    def bet_up(self, wallet):
        token_price = self.get_token_price()
        balance = self.current_balance * 0.1
        return super().bet_up(wallet, token_price, balance)

    def bet_down(self, wallet):
        token_price = self.get_token_price()
        balance = self.current_balance
        return super().bet_up(wallet, token_price, balance)

    def get_signal(self, interval):
        blockchain = TA_Handler(
            symbol=self.symbol,
            screener=self.screener,
            exchange=self.blockchain,
            interval=interval,
        )

        return blockchain.get_analysis().summary

    @staticmethod
    def compute_average_signal(min_recommandation, med_recommandation):
        average_buy = (min_recommandation['BUY'] + med_recommandation['BUY']) / 2
        average_sell = (min_recommandation['SELL'] + med_recommandation['SELL']) / 2
        average_neutral = (min_recommandation['NEUTRAL'] + med_recommandation['NEUTRAL']) / 2
        return {
            "BUY": average_buy,
            "SELL": average_sell,
            "NEUTRAL": average_neutral,
        }

    def trade(self):
        min_recommandation = self.get_signal(Interval.INTERVAL_1_MINUTE)
        med_recommandation = self.get_signal(Interval.INTERVAL_5_MINUTES)
        recommandations = self.compute_average_signal(min_recommandation, med_recommandation)
        strategy = self.strategy(recommandations)
        if strategy == 'up':
            return self.bet_up(self.wallet)
        elif strategy == 'down':
            return self.bet_up(self.wallet)
        else:
            print('Do Nothing')


BotBoris(1000, 'crypto', "BINANCE", "BNBUSDT", 55)
