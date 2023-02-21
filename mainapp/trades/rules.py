import re
from .consts import OPTIONS_TYPE, TRADE_TYPE, ASSETS_TYPE

class Rule:
    def __init__(self, regex = r'.*', type = str, required = True, default = '', choice = None):
        self.regex = regex
        self.type = type
        self.required = required
        self.default = default
        self.choice = choice
        self.value = ''
        self.error = ''

    def set(self, value):
        match = re.match(self.regex, str(value))
        if match:
            value = match.group()
            if self.choice:
                value = self.choice.reducer[value]
            self.value = self.type(value)

    def is_valid(self):
        if self.value == '':
            if self.required:
                self.error = f"Invalied brocker rules"
                return False
            else:
                self.value = self.default
        return True

    def get(self):
        return self.value

columns = {
    'symbol': Rule(r'.*'),
    'tradeDate': Rule(r'^\d\d\d\d-\d\d-\d\d$'),
    'exchange': Rule(r'.*'),
    'quantity': Rule(r'^([0-9]+)', type = int),
    'price': Rule(r'.*', type = float),
    'executionTime': Rule(r'.*'),
    'strikePrice': Rule(r'.*', required = False),
    'expiryDate': Rule(r'^\d\d\d\d-\d\d-\d\d$', required = False),
    'optionsType': Rule(r'^([0]|[1])$', type = int,  choice= OPTIONS_TYPE),
    'tradeType': Rule(r'^([0]|[1]|[2])$', type = int, choice= TRADE_TYPE),
    'assetType': Rule(r'^([0-9]|[1][0])$', type = int, choice= ASSETS_TYPE),
}