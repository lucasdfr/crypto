from web3 import Web3
import matplotlib.pyplot as plt
import pandas as pd
import json, os
import numpy as np

from api import get_account_transactions, get_abi
from config import Config
from models.financialtransaction import FinancialTransaction
from models.contract import Contract
from models.pool import Pool
from web3.middleware import geth_poa_middleware

from models.token import Token
from models.transaction import Transaction
from models.transfer import Transfer
from utils import is_token, is_pool, get_value_of_token

bsc = "https://bsc-dataseed.binance.org/"
w3 = Web3(Web3.HTTPProvider(bsc))
Config.init(w3, models=[Transaction])
w3.middleware_onion.inject(geth_poa_middleware, layer=0)

pd.options.mode.chained_assignment = None  # default='warn'

WALLET_ADDRESS = "0x1884856e3dfe96b143f0ba25bec9f8f1e5feb211"
COURS_BNB = 290


def get_transactions_json(address, internal=False):
    if internal:
        internal_suffix = 'internal_'
    else:
        internal_suffix = ''
    file_exists = os.path.exists(f'data/wallet_{internal_suffix}{address}.json')
    if not file_exists:
        transactions = get_account_transactions(address, offset=None, sort="desc", internal=internal)
        with open(f'data/wallet_{internal_suffix}{address}.json', 'w') as f:
            json.dump(transactions, f)
        return transactions
    with open(f"data/wallet_{internal_suffix}{address}.json", "r") as wallet_data:
        return json.load(wallet_data)['result']


def get_transactions_df(address, internal=False):
    df = pd.DataFrame(get_transactions_json(address, internal=internal))
    df['timeStamp'] = pd.to_datetime(df['timeStamp'], unit='s')
    return df


def transform_df(df, gas=False):
    df['isError'] = df['isError'].astype('int')
    df = df[df['isError'] == 0]
    df['value'] = df['value'].astype('float')
    df['value'] = df['value'] * 10 ** (-18)
    df['value'] = np.where(df['from'] == WALLET_ADDRESS,
                           df['value'] * -1,
                           df['value'])

    if gas:
        df['txn_fee'] = df['gasPrice'].astype('float') * df['gasUsed'].astype('float') * 10 ** (-18)
        df['value'] = df['value'] - df['txn_fee']
        df.drop(columns=['txn_fee', 'gasPrice', 'gasUsed'])
    return df.drop(columns=['isError'])


def compute_in_out(df, df_internal, title):
    df = df[['timeStamp', 'from', 'to', 'value', 'isError', 'gasPrice', 'gasUsed']]
    df_internal = df_internal[['timeStamp', 'from', 'to', 'value', 'isError']]
    df = transform_df(df, gas=True)
    df_internal = transform_df(df_internal)

    df = pd.concat([df, df_internal])
    df = df[['timeStamp', 'value']]

    df = df.groupby([df['timeStamp'].dt.date]).sum(numeric_only=True)
    df = df.sort_values(by='timeStamp')
    df['bnb_balance'] = df['value'].cumsum()
    df.plot.bar(stacked=True, title=title)
    plt.show()
    print(f"{title} :", df.head().to_string())


def plot_wallet(address, df, df_internal):
    # What we see on bscscan
    compute_in_out(df, df_internal, "Historique entrées sorties BSCscan")

    # Compute money received
    df_money_received = df[(df['methodId'] == '0x') & (df['from'] == address)]
    money_received = round((df_money_received['value'].astype(float) * 10 ** (-18)).sum(), 2)
    money_received_dollar = round(money_received * COURS_BNB, 2)
    df_money_put = df[(df['methodId'] == '0x') & (df['to'] == address)]

    money_put = round((df_money_put['value'].astype(float) * 10 ** (-18)).sum(), 2)
    money_put_dollar = round(money_put * COURS_BNB, 2)
    print("Argent retiré du wallet: ", money_received, " BNB or ", money_received_dollar, " $")
    print("Argent mis dans le wallet: ", money_put, " BNB or ", money_put_dollar, " $")

    # Compute lost/wins without transfers
    df_win_lose = df[(df['methodId'] != '0x') & ((df['from'] != address) | (df['to'] != address))]
    df_win_lose_internal = df_internal
    # print(df_win_lose_internal)
    compute_in_out(df_win_lose, df_win_lose_internal, "Argent gagné en tradant")



# df = get_transactions_df(WALLET_ADDRESS)
# df_internal = get_transactions_df(WALLET_ADDRESS, internal=True)



financial = FinancialTransaction('0x4c5727ac8c204fb1fdbc5a19a8f9cc4e9fd5e9f48b852cf5fcb13db4822d9b84')
print(financial.get_status())
print(financial.get_decoded_logs())
argentina = Token('0x715a26bf4c61304104e29bb50862bcdef24eab36')
print(get_value_of_token(argentina))
