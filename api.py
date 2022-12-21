import requests as re
import json

API_KEY = 'WWVWQ2KD6JR8GX6DMMPRTXEY6STVG2ZARC'
BASE_URL = 'https://api.bscscan.com/api?'
BASE_TEST_URL = 'https://api-testnet.bscscan.com/api?'

TEST = True


def call_api(api_arguments):
    url = BASE_URL
    url += f"module={api_arguments['module']}"
    for key in api_arguments:
        if key != 'module':
            url += f'&{key}={api_arguments[key]}'
    url += f'&apikey={API_KEY}'
    return re.get(url).json()


def get_abi(address):
    api_arguments = {'module': 'contract', 'action': 'getabi', "address": address}
    abi = call_api(api_arguments)
    if abi['status'] == '1':
        return json.loads(abi["result"])


def get_account_transactions(address, offset=1, sort='asc', internal=False):
    """
    Retourne la balance d'un ou plusieurs comptes
    :param address:liste de hash ou hash simple
    :return:
    """
    api_arguments = {'module': 'account', "address": address, "startblock": "0",
                     "endblock": "99999999", "page": "1", "sort": sort}
    if internal:
        api_arguments['action'] = 'txlistinternal'
    else:
        api_arguments['action'] = 'txlist'

    if offset is not None:
        api_arguments["offset"] = offset

    return call_api(api_arguments)


def get_account_first_and_last_block(address):
    """
        Retourne le premier et le dernier block d'un contract
        :param address:liste de hash ou hash simple
        :return:
        """
    return get_account_transactions(address)['result'][0]['blockNumber'], \
           get_account_transactions(address, sort='desc')['result'][0]['blockNumber']


def get_token_balance(address):
    """
    Retourne la balance d'un token
    :param address:hash
    :return:
    """
    api_arguments = {'module': 'account', 'action': 'balance', "address": address}
    return call_api(api_arguments)


def get_bnb_price():
    url="https://api.binance.com/api/v3/ticker/price?symbol=BNBUSDT"
    return float(re.get(url).json()['price'])