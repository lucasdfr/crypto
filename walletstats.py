from web3 import Web3
import matplotlib.pyplot as plt
import pandas as pd
import json, os
import numpy as np

from api import get_account_transactions, get_abi
from config import Web3Config
from models.financialtransaction import FinancialTransaction
from web3.middleware import geth_poa_middleware

from models.transfer import Transfer

bsc = "https://bsc-dataseed.binance.org/"
w3 = Web3(Web3.HTTPProvider(bsc))
Web3Config.init(w3)
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


def get_transactions_detail(transaction_hash):
    receipt = w3.eth.get_transaction_receipt(transaction_hash)
    for log in receipt['logs']:
        print(log['address'])
    for log in receipt['logs']:
        # log = receipt['logs'][0]
        smart_contract = log["address"]
        # print(smart_contract)
        abi = get_abi(log["address"])
        if abi is not None:
            contract = w3.eth.contract(smart_contract, abi=abi)
            transfers = []
            decoded_logs = list(contract.events.Transfer().processReceipt(receipt))
            for decoded_log in decoded_logs:
                print(Transfer(decoded_log['args']))
            # print(contract.events.Transfer().processReceipt(receipt))
            # for decoded_log in decoded_logs:
            #     if 'from' in decoded_logs[0]['args']:
            #         transfer = {}
            #         transfer['from'] = decoded_log['args']['from']
            #         transfer['to'] = decoded_log['args']['to']
            #         transfer['value'] = float(decoded_log['args']['value'])
            #         transfers += [transfer]
            # return pd.DataFrame(transfers)


def get_holders(df, address):
    abi = get_abi(address)
    contract = w3.eth.contract(address=w3.toChecksumAddress(address), abi=abi)
    df_holders = pd.DataFrame(columns=['HOLDER_HASH', 'WALLET', 'UNIT', 'MONEY_IN', 'TIME_IN', 'MONEY_OUT', 'TIME_OUT'])
    for index, tx in df.iterrows():
        if tx['from'] is not None:
            wallet_balance = w3.eth.getBalance(w3.toChecksumAddress(tx['from']))
            token_balance = contract.functions.balanceOf(tx['from']).call()
            print(w3.fromWei(wallet_balance, "ether"))
            print(w3.fromWei(token_balance, "ether"))


def get_tokens_analytics(df):
    for index, tx in df.iterrows():
        print(get_transactions_detail(tx['hash']))


df = get_transactions_df(WALLET_ADDRESS)
df_internal = get_transactions_df(WALLET_ADDRESS, internal=True)

transaction = FinancialTransaction("0x3c6123c33d0f400b4c0248e290274d1ebdac25a2f4ab378bb972678680f3738c")
print(transaction.is_internal)
# print(get_transactions_detail("0x91c04789dfe3f138f4aaac7b7de3fb67f96fcb71b957161c32868cbcc27e6ed4"))
