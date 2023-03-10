from collections import OrderedDict

class ChoiceConst:
    class Repr:
        pass

    def __init__(self, *consts):
        self.consts = ()
        if consts:
            self.consts = consts

        self.choices = []
        self.repr = object
        for i, const in enumerate(self.consts):
            setattr(self, const.upper(), i)
            self.choices.append((i, const.replace('_', ' ').capitalize()))
            setattr(self.Repr, const.upper(), const)
    
    def reducer(self, const):
        return self.consts.index(const)
    
    def expander(self, i):
        return self.consts[i]

    def contains(self, i):
        assert 0<=i and i<len(self.consts)

ASSETS_TYPE = ChoiceConst(
    'cash', 
    'equity_options', 
    'equity_futures', 
    'forex_spot', 
    'forex_futures', 
    'forex_options',  
    'commodity_futures', 
    'commodity_options', 
    'crypto_spot', 
    'crypto_futures', 
    'crypto_options'
)

STATUS = ChoiceConst(
    'loss', 
    'win', 
    'breakeven'
)

TRADE_TYPE = ChoiceConst(
    'buy', 
    'sell'
)

OPTIONS_TYPE = ChoiceConst(
    'puts', 
    'calls'
)

DAYS = ChoiceConst(
    'sunday', 
    'monday', 
    'tuesday', 
    'wednesday', 
    'thursday', 
    'friday', 
    'saturday'
)

YES_OR_NO = ChoiceConst(
    'yes', 
    'no'
)

DEFUALT_RULE = f"""{{
    'symbol':{{
        'type': 'field',
        'col': 0,
        'regex': r'(?P<value>.*)'
    }},
    'tradeDate': {{
        'type': 'field',
        'col': 2,
        'regex': r'(?P<value>.*)'
    }},
    'exchange': {{
        'type': 'field',
        'col': 3,
        'regex': r'(?P<value>.*)'
    }},
    'segment': {{
        'type': 'field',
        'col': 4,
        'regex': r'(?P<value>.*)'
    }},
    'quantity': {{
        'type': 'field',
        'col': 8,
        'regex': r'(?P<value>.*)'
    }},
    'price': {{
        'type': 'field',
        'col': 9,
        'regex': r'(?P<value>.*)'
    }},
    'orderId':{{
        'type': 'field',
        'col': 11,
        'regex': r'(?P<value>.*)',
    }},
    'executionTime': {{
        'type': 'field',
        'col': 12,
        'regex': r'.*(?P<value>\d\d:\d\d:\d\d)$'
    }},
    'optionsType': {{
        'type': 'check',
        'values': {{
            '{OPTIONS_TYPE.Repr.PUTS}': [
                {{
                    'col': 0,
                    'regex': '.*\d(PE)$'
                }}
            ],
            '{OPTIONS_TYPE.Repr.CALLS}': [
                {{
                    'col': 0,
                    'regex': '.*\d(CE)$'
                }}
            ]
        }}
    }},
    'tradeType': {{
        'type': 'check',
        'values': {{
            '{TRADE_TYPE.Repr.SELL}': [
                {{
                    'col': 6,
                    'regex': r'^(sell)$'
                }}
            ],
            '{TRADE_TYPE.Repr.BUY}': [
                {{
                    'col': 6,
                    'regex': r'^(buy)$'
                }}
            ]
        }}
    }},
    'assetType': {{
        'type': 'check',
        'values': {{
            '{ASSETS_TYPE.Repr.CASH}': [
                {{
                    'col': 4,
                    'regex': r'^EQ$'
                }}
            ],
            '{ASSETS_TYPE.Repr.EQUITY_OPTIONS}': [
                {{
                    'col': 4,
                    'regex': r'^FO$'
                }},
                {{
                    'col': 0, 
                    'regex': r'.*(CE|PE)$'
                }}
            ],
            '{ASSETS_TYPE.Repr.EQUITY_FUTURES}': [
                {{
                    'col': 4,
                    'regex': r'^FO$'
                }},
                {{
                    'col': 0, 
                    'regex': r'.*(FUT$)'
                }}
            ],
            '{ASSETS_TYPE.Repr.FOREX_OPTIONS}': [
                {{
                    'col': 4,
                    'regex': r'^CDS$'
                }},
                {{
                    'col':0, 
                    'regex': r'.*(CE|PE)$'
                }}
            ],
            '{ASSETS_TYPE.Repr.FOREX_FUTURES}': [
                {{
                    'col': 4,
                    'regex': r'^CDS$'
                }},
                {{
                    'col': 0, 
                    'regex': r'.*(FUT)$'
                }}
            ],
            '{ASSETS_TYPE.Repr.COMMODITY_OPTIONS}': [
                {{
                    'col': 4,
                    'regex': r'^COM$'
                }},
                {{
                    'col': 0, 
                    'regex': r'.*(CE|PE)$'
                }}
            ],
            '{ASSETS_TYPE.Repr.COMMODITY_FUTURES}': [
                {{
                    'col': 4,
                    'regex': r'^COM$'
                }},
                {{
                    'col': 0, 
                    'regex': r'.*(FUT)$'
                }}
            ],
        }}
    }}
}}"""

SUPPORTED_FILE_TYPES = ['csv']

class ERROR:
    INVALIED_TRADE = 0
    NO_TRADE_HISTORIES = 1
    TRADE_UPDATE_FAILED = 2
    NO_COMPARISON = 3