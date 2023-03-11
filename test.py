import pandas as pd
import datetime

class Column:
    def __init__(self, default = None, read_only = False):
        self.value = default
        self.read_only= read_only

    def __eq__(self, other):
        if isinstance(other, Column):
            return self.value == other.value
        return self.value == other

    def get(self):
        return str(self.value)

    def set(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)
    
    def __repr__(self):
        return self.__str__()

class IdColumn(Column):
    def get(self):
        return '1234'

class DateTimeColumn(Column):
    def __init__(self, default = '', format = '%Y-%m-%d %H:%M:%S', read_only = False):
        self.value = default
        self.format = format
        self.read_only= read_only
    
    def set(self, value):
        self.value = datetime.datetime.strptime(value, self.format)

class IntColumn(Column):
    def __init__(self, default = 0, read_only = False):
        super().__init__(default, read_only)

    def set(self, value):
        self.value = int(value)

class FloatColumn(Column):
    def __init__(self, default = 0.0, read_only = False):
        super().__init__(default, read_only)
    
    def set(self, value):
        self.value = float(value)

class CharColumn(Column):
    def __init__(self, default = '', read_only = False):
        super().__init__(default, read_only)

class ListColumn(Column):
    def __init__(self, child, unique = False, read_only = False):
        self.child = child
        self.value = []
        self.unique = unique
        self.read_only = read_only

    def __contains__(self, other):
        return other in map(lambda v: v.value, self.value)
    
    def set(self, value):
        self.value = []
        for v in value.split(','):
            self.append(v)
    
    def get(self):
        return ','.join(map(lambda v: v.get(), self.value))
    
    def append(self, value):

        if (self.unique and (value not in self)) or (not self.unique):
            child = self.child()
            child.set(value)
            self.value.append(child)

class Execution:
    def __init__(self):
        self.data = {
            'datetime': DateTimeColumn(),
            'price': FloatColumn(),
            'quantity': IntColumn(),
            'id': IdColumn(),
            'tid': IdColumn()
        }
    
    def __eq__(self, other):
        if type(other) == str:
            return self.data['id'] == other
        return self.data['id'] == other.data['id']

    def set(self, data):
        for k, v in data.items():
            self.data[k].set(v)

    def get(self):
        data = {}
        for k, v in self.data:
            data[k] = v.get()
        return data

    def save(self):
        pass

    def delete(self):
        pass

class Trade:
    def __init__(self, data):
        self.data = {
            'symbol': CharColumn(),
            'notes': CharColumn(),
            'tags': ListColumn(child = CharColumn, unique = True),
            'mistakes': ListColumn(child = CharColumn, unique = True),
            'setups': ListColumn(child = CharColumn, unique = True),
            'id': IdColumn(),
            'exitPrice': FloatColumn(read_only=True)
        }

    def __eq__(self, other):
        if type(other) == str:
            return self.data['id'] == other
        return self.data['id'] == other.data['id']

    def __contains__(self, other):
        if isinstance(other, Execution):
            return other.data['tid'] == self.data['id']
        return False
    
    def save(self):
        pass

    def delete(self):
        pass

    def set(self, data):
        for k, v in data.items():
            self.data[k].set(v)

    def get(self):
        data = {}
        for k, v in self.data:
            data[k] = v.get()
        return data

    
class Executions:
    def __init__(self, user):
        self.user = user

    def load(self):
        pass
    
    def get_by_tid(self, tid):
        pass

    def get_by_id(self, id):
        pass

    def get_all(self):
        pass

    def create(self, tid, data):
        pass
    
    def update(self, id, data):
        pass

    def delete(self, id):
        pass

    def delete_all(self, tid):
        pass

class Trades:
    def __init__(self, user):
        self.user = user
        self.is_demo = False
        self.errors = {}
        self.trades = None
        
    def load(self):
        self.trade_histories = TradeHistory.objects.filter(user = self.user, is_demo = False)
        if not self.trade_histories.exists():
            self.trade_histories = TradeHistory.objects.filter(user = self.user, is_demo = False)
            self.is_demo = True
        
        if not self.trade_histories.exists():
            self.errors['NO_TRADE_HISTORIES'] = 'No trade histories available'
        else:
            has_trades = False
            for trade_history in self.trade_histories:
                output_filename = trade_history.output_trades
                output_trades = pd.reac_csv(output_filename)
                output_trades.insert(1, 'thId', trade_history.pk)
                if has_trades:
                    self.trades = pd.concat([self.trades, output_trades]).

    def get_by_id(self, id):
        pass

    def get_all(self):
        pass

    def create(self, data):
        pass

    def update(self, id, data):
        pass

    def delete(self, id):
        pass

    def delete_all(self):
        pass
