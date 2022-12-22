"""
Tissou est un robot trader qui possède un portefeuille
"""


class Tissou:

    def __init__(self, initial_balance):
        self.initial_balance = initial_balance
        self.current_balance = initial_balance
        self.is_active = False

    def get_current_balance(self):
        """
        Permet de connaître à tout moment la balance et les positions d'un Tissou
        :return: 
        """
        pass

    def add_balance(self, balance):
        """
        Permet d'ajouter de l'argent sur un portefeuille d'un Tissou
        :param balance:
        :return:
        """
        self.current_balance = self.current_balance + balance
        return self.current_balance

    def retrieve_balance(self, balance):
        """
        Permet de retirer de l'argent sur un portefeuille d'un Tissou
        :param balance:
        :return:
        """
        pass

    def switch_on(self):
        """
        Permet d'activer un Tissou
        :return:
        """
        self.is_active = True
        return self.is_active

    def switch_off(self):
        """
        Permet d'éteindre un Tissou
        :return:
        """
        self.is_active = False
        return self.is_active

    def destroy(self):
        """
        Permet d'annuler toutes les positions d'un Tissou
        :return:
        """
        pass
