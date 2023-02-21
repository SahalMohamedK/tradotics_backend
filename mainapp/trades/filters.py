from ..consts import TRADE_TYPE, STATUS, ASSETS_TYPE, OPTIONS_TYPE, DAYS, YES_OR_NO

class Formatter:
    def __init__(self, formatter = '{cur} - {next}', more = True):
        self.more = more
        self.formatter = formatter

    def local(self, n):
        return str(n)

    def format(self, cur, next):
        if next == '+':
            if self.more:
                cur = self.local(eval(cur))
                return f'{cur} +'
            return
        cur = self.local(eval(cur))
        next = self.local(eval(next))
        return self.formatter.format(cur = cur, next=next)

class DurationFormatter(Formatter):
    def local(self, n):
        if n > 60:
            return str(n//60)+' hr'
        return str(n)+' min'

class TimeFormatter(Formatter):
    more = False
    def local(self, n):
        if n<24 and n>12:
            return f'{n%12} pm' 
        elif n ==0 or n == 24:
            return '12 am'
        elif n == 12:
            return '12 pm'
        return f'{n%12} am'

class ChoiceFilter:
    def __init__(self, name= None, column = None, choices = None):
        self.column = column
        self.choices = choices
        self.name = name
        
    def options(self, trades):
        choices = self.choices
        if not choices:
            choices = trades[self.column].drop_duplicates().to_list()
            choices.sort()
            choices = zip(choices, choices)
        _choices = {}
        for i, choice in choices:
            _choices[i] = choice
        return _choices

    def apply(self, options, trades):
        if options:
            return trades.loc[trades[self.column].isin(options)]
        return trades

class RangeFilter:
    def __init__(self, name= None, column = None, limits = [], formatter = Formatter()):
        self.column = column
        self.limits = limits
        self.formatter = formatter
        self.name = name
    
    def options(self, trades):
        ranges = {}
        if self.limits:
            i = 0
            while i<len(self.limits)-1:
                formated_string = self.formatter.format(cur = str(self.limits[i]), next=str(self.limits[i+1]))
                ranges[i] = formated_string
                i+=1
        formated_string = self.formatter.format(cur = str(self.limits[i]), next='+')
        if formated_string:
            ranges[i] = formated_string
        return ranges
    
    def apply(self, options, trades):
        for i in options:
            if i+1<len(self.limits):
                trades = trades[trades[self.column].between(self.limits[i], self.limits[i+1])]
            else:
                trades = trades[self.limits[i]<=trades[self.column]]
        return trades

class IncludesFilter:
    def __init__(self, name= None, column = None,):
        self.name = name
        self.column = column

    def options(self, trades):
        options = {}
        for i, trade in trades.iterrows():
            svalues = trade[self.column]
            if svalues:
                values = svalues.split(',')
                if values:
                    for value in values:
                        if value not in options:
                            options[value] = value
        return options
    
    def apply(self, options, trades):
        if options:
            return trades[trades[self.column].apply(lambda x: any(i in x.split(',') for i in options))]
        return trades

class Filters:
    def __init__(self, trades):
        self.trades = trades
        self.filters = {
            'symbol': ChoiceFilter(),
            'side': ChoiceFilter(column = 'tradeType', choices = [('buy', 'Buy'), ('sell', 'Sell')]),
            'price': RangeFilter(column = 'entryPrice', limits = [0, 5, 10, 20, 50, 100, 150, 200, 500, 1000, 2000, 5000, 10000], formatter=Formatter(formatter='${cur} - ${next}')),
            'setup': IncludesFilter(),
            'mistakes': IncludesFilter(),
            'tags': IncludesFilter(),
            'status': ChoiceFilter(choices = STATUS.choices),
            'asset_type': ChoiceFilter(column='assetType',choices=ASSETS_TYPE.choices),
            'duration': RangeFilter(limits = [0, 1, 5, 10, 20, 30, 45, 60, 90, 120, 180, 240], formatter = DurationFormatter())	,
            'day': ChoiceFilter(choices = DAYS.choices),
            'call_put': ChoiceFilter(name = 'Call / Put', choices=OPTIONS_TYPE.choices),
            'hour': RangeFilter(limits = range(0, 25), formatter=TimeFormatter(more = False)),
            'r_mutiple': RangeFilter(limits=[-5, -4, -3, -2, -1.5, -1, -0.5, 0, 0.5, 1, 1.5, 2, 3, 4, 5], formatter = Formatter(formatter = '{cur}R to {next}R', more = False)),
            'notes_filled': ChoiceFilter(choices=YES_OR_NO.choices),
        }

        for filter_key in self.filters:
            filter = self.filters[filter_key]
            if not filter.name:
                filter.name = ' '.join(filter_key.split('_')).capitalize()
            if not filter.column:
                filter.column = filter_key
                
    def get(self):
        filters = {}
        for filter_key in self.filters:
            filter = self.filters[filter_key]
            filters[filter_key] = [filter.name, filter.options(self.trades.trades)]
        return filters

    def apply(self, filters):
        for filter_key in filters:
            options = filters[filter_key]
            filter_obj = self.filters[filter_key]
            self.trades.trades = filter_obj.apply(options, self.trades.trades)