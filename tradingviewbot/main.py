from web3 import Web3


from trading_models import Wallet, Token, TokenValue

from config import Config
from tradingviewbot.high_variation import main_high_variation
from tradingviewbot.trading_view import main_trade_view

bsc = "https://bsc-dataseed.binance.org/"
w3 = Web3(Web3.HTTPProvider(bsc))
Config.init(w3)

BASE_AMOUNT = 1000





def global_trade():
    wallet, wallet_created = Wallet.get_or_create(id=1, initial_balance=BASE_AMOUNT)
    if wallet_created:
        wallet.current_balance = wallet.initial_balance
        wallet.save()

    # wbnb, wbnb_created = Token.get_or_create(name='Wrapped BNB', symbol='WBNB',
    #                                          address="0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c")
    nexus, nexus_created=Token.get_or_create(name='NEXUSPAD PROTOCOL', symbol='NEXUS',
                                             address="0xeFdb93E14cd63B08561e86D3a30aAE0f3AaBaD9a")

    # if wbnb_created or wallet_created:
    #     wbnb_value = TokenValue.create(token=wbnb, wallet=wallet).save()

    if nexus_created or wallet_created:
        nexus_value = TokenValue.create(token=nexus, wallet=wallet).save()

    # main_trade_view(wallet, wbnb)
    main_high_variation(wallet, nexus)


# if __name__ == 'main':
global_trade()
