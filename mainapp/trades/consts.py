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

class ASSETS_TYPE(ChoiceConst):
    def __init__(self):
        self.consts = (
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

    def is_options(self, asset_type):
        return asset_type in [self.FOREX_OPTIONS, self.CRYPTO_OPTIONS, self.EQUITY_OPTIONS, self.COMMODITY_OPTIONS]

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