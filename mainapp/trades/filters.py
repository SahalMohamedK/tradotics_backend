import datetime
from mainapp.consts import TRADE_TYPE, STATUS, ASSETS_TYPE, OPTIONS_TYPE, DAYS, YES_OR_NO

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
            n = n/60
            n = int(n) if int(n) == n else n
            return str(n)+' hr'
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
    def __init__(self, name= None, column = None, choices = None, converter = lambda v: v):
        self.column = column
        self.choices = choices
        self.name = name
        self.converter = converter
        
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

    def apply(self, options, trade):
        if options:
            value = trade[self.column]
            value = self.converter(value)
            if value in options:
                return trade
            return
        return trade

class RangeFilter:
    def __init__(self, name= None, column = None, limits = [], formatter = Formatter(), converter = lambda v: v):
        self.column = column
        self.limits = limits
        self.name = name
        self.formatter = formatter
        self.converter = converter
    
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
    
    def apply(self, options, trade):
        for i in options:
            value = trade[self.column]
            value = self.converter(value)
            if not ((i+1<len(self.limits) and self.limits[i]<= value and value<self.limits[i+1]) or
                (i+1>=len(self.limits) and self.limits[i]<=trade[self.column])):
                return
        return trade
            

class IncludesFilter:
    def __init__(self, name= None, column = None):
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
    
    def apply(self, options, trade):
        if options:
            result = False
            for value in trade[self.column]:
                result = result or (value in options)
            if result:
                return trade
        return trade
    
class DateFilter:
    def __init__(self, name= None, column = None, dir = 'from'):
        self.name = name
        self.column = column
        self.dir = dir

    def options(self, trades):
        return 
    
    def apply(self, date, trade):
        if date:
            date = datetime.datetime.strptime(date, '%Y-%m-%d')
            tradeDate = datetime.datetime.strptime(trade[self.column], '%Y-%m-%d')
            if (self.dir == 'from' and date<=tradeDate) or (self.dir == 'to' and date>=tradeDate):
                return trade
            return
        return trade

class Filters:
    def __init__(self, trades):
        self.trades = trades
        self.filters = {
            'symbol': ChoiceFilter(),
            'side': ChoiceFilter(
                column = 'tradeType', 
                choices = TRADE_TYPE.choices),
            'price': RangeFilter(
                column = 'entryPrice', 
                limits = [0, 5, 10, 20, 50, 100, 150, 200, 500, 1000, 2000, 5000, 10000], 
                formatter=Formatter(formatter='${cur} - ${next}')),
            'setup': IncludesFilter(),
            'mistakes': IncludesFilter(),
            'tags': IncludesFilter(),
            'status': ChoiceFilter(choices = STATUS.choices),
            'assetType': ChoiceFilter(choices=ASSETS_TYPE.choices),
            'duration': RangeFilter(
                limits = [0, 1, 5, 10, 20, 30, 45, 60, 90, 120, 180, 240], 
                formatter = DurationFormatter(),
                converter=lambda v:  (v.days*86400 + v.seconds)/60)	,
            'day': ChoiceFilter(
                column='entryDate',
                choices = DAYS.choices,
                converter = lambda v: datetime.datetime.strptime(v, '%Y-%m-%d').weekday()+1),
            'optionsType': ChoiceFilter(
                name = 'Call / Put', 
                choices=OPTIONS_TYPE.choices),
            'hour': RangeFilter(
                column = 'entryTime',
                limits = range(0, 25), 
                formatter=TimeFormatter(more = False),
                converter=lambda v: datetime.datetime.strptime(v, '%H:%M:%S').hour),
            # 'r_mutiple': RangeFilter(
            #     limits=[-5, -4, -3, -2, -1.5, -1, -0.5, 0, 0.5, 1, 1.5, 2, 3, 4, 5], 
            #     formatter = Formatter(formatter = '{cur}R to {next}R', more = False)),
            'notesFilled': ChoiceFilter(
                name='Notes filled',
                choices=YES_OR_NO.choices),
            'fromDate': DateFilter(column = 'entryDate', dir='from'),
            'toDate': DateFilter(column = 'entryDate', dir='to'),
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
            options = filter.options(self.trades.trades)
            if options:
                filters[filter_key] = [filter.name, options]
        return filters

    def apply(self, filters, trade):
        for filter_key in filters:
            options = filters[filter_key]
            filter_obj = self.filters[filter_key]
            if trade:
                trade = filter_obj.apply(options, trade)
        return trade
