from peewee import *
import datetime
from api import get_bnb_price

db = SqliteDatabase("../data/database.sqlite")


class BaseModel(Model):
    class Meta:
        database = db


class Wallet(BaseModel):
    current_balance = FloatField()
    initial_balance = FloatField()
    potential_win = FloatField(default=0)
    strategy_of_bet = CharField(default='sell_all')

    def __str__(self):
        return f"""Bet wallet {self.id}: current_balance: {self.current_balance} initial_balance: {self.initial_balance} potential_win: {self.potential_win}"""


class BNB(BaseModel):
    timestamp = DateTimeField(default=datetime.datetime.now)
    value = FloatField(default=get_bnb_price())


class Token(BaseModel):
    name = CharField()
    symbol = CharField()
    address = TextField(unique=True)

    def __str__(self):
        return f"""--Token {self.name} ({self.symbol}) of wallet {self.wallet.id} current balance : {self.current_balance}"""


class TokenValue(BaseModel):
    wallet=ForeignKeyField(Wallet, backref='tokens')
    token = ForeignKeyField(Token, backref='values')
    timestamp = DateTimeField(default=datetime.datetime.now)
    value = FloatField(default=0)
    current_balance = FloatField(default=0)

    @staticmethod
    def get_token_balance(token, wallet):
        print(TokenValue.select(token, wallet).order_by(TokenValue.id.desc()).get().current_balance)
        return TokenValue.select(token, wallet).order_by(TokenValue.id.desc()).get().current_balance



class TradingBotHistory(BaseModel):
    wallet = ForeignKeyField(Wallet, backref='transactions')
    timestamp = DateTimeField(default=datetime.datetime.now)
    method = CharField()
    amount = FloatField()
    status = BooleanField()
    status_detail = CharField()

    def __str__(self):
        return f"""--- Transaction of amount: {self.amount} method: {self.method} status: {self.status} status_detail: {self.status_detail}"""


db.connect()
# db.create_tables([Wallet, TradingBotHistory, Token, TokenValue, BNB])