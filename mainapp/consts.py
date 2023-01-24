class PNL_STATUS:
    WIN = 0
    LOSS = 1
    BREAKEVEN = 3

class TRADE_TYPE:
    BUY = 0
    SELL = 1

    choices = (
        (BUY, "Buy"),
        (SELL, "Sell"),
    )

class OPTIONS_TYPE:
    CALLS = 'calls'
    PUTS = 'puts'

    choice = (
        (CALLS, 'Calls'),
        (PUTS, 'Puts')
    )

class ASSETS_TYPE:
    CASH = 'cash'
    EQUITY_OPTIONS = 'equity_options'
    EQUITY_FUTURES = 'equity_futures'
    FOREX_SPOT = 'forex_spot'
    FOREX_FUTURES = 'forex_futures'
    FOREX_OPTIONS = 'forex_options'
    COMMODITY_FUTURES = 'commodity_futures'
    COMMODITY_OPTIONS = 'commodity_options'
    CRYPTO_SPOT = 'crypto_spot'
    CRYPTO_FUTURES = 'crypto_futures'
    CRYPTO_OPTIONS = 'crypto_options'

    choice = (
        (CASH, 'Cash'),
        (EQUITY_OPTIONS, 'Equity Options'),
        (EQUITY_FUTURES, 'Equity Futures'),
        (FOREX_SPOT, 'Forex Spot'),
        (FOREX_FUTURES, 'Forex Futures'),
        (FOREX_OPTIONS, 'Forex Options'),
        (COMMODITY_FUTURES, 'Commodity Futures'),
        (COMMODITY_OPTIONS, 'Commodity Options'),
        (CRYPTO_SPOT, 'Crypto Spot'),
        (CRYPTO_FUTURES, 'Crypto Futures'),
        (CRYPTO_OPTIONS, 'Crypto Options')
    )

DEFUALT_FIELDS_RULE = """{
    'symbol': [None, ''],
    'trade_date': [None, ''],
    'exchange': [None, ''],
    'segment': [None, ''],
    'trade_type': [None, ''],
    'quantity': [None, ''],
    'price': [None, ''],
    'order_id': [None, ''],
    'order_execution_time': [None, ''],
    'strike_price': [None, ''],
    'expiry_date': [None, ''],
}"""

DEFUALT_ASSETS_RULE = """{
    'cash': [None, ''],
    'equity_options': [[None, ''], [None, '']],
    'equity_futures': [[None, ''], [None, '']],
    'forex_spot':  [None, ''],
    'forex_options': [[None, ''], [None, '']],
    'forex_futures': [[None, ''], [None, '']],
    'commodity_futures': [[None, ''], [None, '']],
    'commodity_options': [[None, ''], [None, '']],
    'crypto_spot': [None, ''],
    'crypto_futures':  [None, ''],
    'crypto_options':  [None, ''],
}
"""

DEFUALT_OPTIONS_RULE = """{
    'calls': [None, ''],
    'puts': [None, ''],
}
"""

SUPPORTED_FILE_TYPES = ['csv']