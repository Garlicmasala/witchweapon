"""
Currency manager for Witch's Weapon.
Tracks gacha and upgrade currencies with validation and atomic consumption.
"""

class CurrencyManager:
    def __init__(self):
        self.balances = {
            "Gacha Gem": 1000,
            "Gacha Ticket": 5,
            "Weapon Affinity": 0,
            "Fashion Token": 0
        }

    def can_afford(self, cost):
        for currency, amount in cost.items():
            if self.balances.get(currency, 0) < amount:
                return False
        return True

    def consume(self, cost):
        if not self.can_afford(cost):
            return False
        for currency, amount in cost.items():
            self.balances[currency] -= amount
        return True

    def add(self, currency, amount):
        self.balances[currency] = self.balances.get(currency, 0) + amount

    def get_balances(self):
        return self.balances.copy()
