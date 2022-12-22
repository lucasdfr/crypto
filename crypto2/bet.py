class Bet:

    def bet_up(self, wallet, token_price, amount):
        """
        Fonction qui permet d'acheter un token
        :param wallet:
        :param token_price:
        :param amount:
        :return:
        """
        if wallet.balance - token_price * amount > 0:
            wallet.balance = wallet.balance - token_price * amount
        return wallet

    def bet_down(self, wallet, token_price, amount):
        """
        Fonction qui permet de vendre un token
        :param wallet:
        :param token_price:
        :param amount:
        :return:
        """
        wallet.balance = wallet.balance + token_price * amount
        return wallet
