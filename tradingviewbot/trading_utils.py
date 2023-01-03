from tradingviewbot.trading_models import TradingBotHistory, BNB, TokenValue
from utils import get_value_of_token
from models.token import Token as TokenClass


def save_history(wallet, amount, method, status, status_detail, token_value):
    trading_bot = TradingBotHistory.create(wallet=wallet.id, amount=amount, method=method, status=status,
                                           status_detail=status_detail)
    trading_bot.save()
    print(TradingBotHistory.get(id=trading_bot), token_value)


def bet(wallet, token, amount, method='buy', token_value=None, token_balance=None):
    bnb_price = BNB.select().order_by(BNB.id.desc()).get().value
    if token_value is None:
        if token.symbol == 'WBNB':
            token_value = bnb_price
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
            TokenValue.create(token=token.id, wallet=wallet.id, current_balance=token_balance, value=token_value)
            wallet.save()
        else:
            if wallet.current_balance > 0:
                status = 1
                status_detail = 'success'
                token_balance = token_balance + wallet.current_balance / token_value
                wallet.current_balance = 0
                TokenValue.create(token=token.id, wallet=wallet.id, current_balance=token_balance, value=token_value)
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
            TokenValue.create(token=token.id, wallet=wallet.id, current_balance=token_balance, value=token_value).save()
            wallet.save()
        else:
            if token_balance > 0:
                status = 1
                status_detail = 'success'
                wallet.current_balance = wallet.current_balance + token_balance * token_value
                token_balance = 0
                TokenValue.create(token=token.id, wallet=wallet.id, current_balance=token_balance, value=token_value).save()
                wallet.save()
            else:
                status = 0
                status_detail = 'Not enough reserve on account'
    save_history(wallet, amount, method, status, status_detail, token_value)
    wallet.compute_positions()
    print(wallet)


def bet_all(wallet, token, method='buy'):
    bet(wallet, token, wallet.current_balance, method)


def sell_all(wallet, token, trade_amount, method='buy'):
    bnb_price = BNB.select().order_by(BNB.id.desc()).get().value
    if method == 'buy':
        bet(wallet, token, trade_amount, method)
    else:
        if token.symbol == 'WBNB':
            token_value = bnb_price
        else:
            token_value = get_value_of_token(TokenClass(token.address))[0]
        token_balance = TokenValue.get_token_balance(token, wallet)
        bet(wallet, token, token_balance * token_value, method, token_value, token_balance)