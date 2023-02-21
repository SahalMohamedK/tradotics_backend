import re
import pandas as pd
import hashlib
import math
import ast
import datetime
from mainapp.models import TradeHistory
from .filters import Filters
from .utils import human_delta
from django.conf import settings
from .rules import columns
from .consts import TRADE_TYPE, STATUS

class MergedTrades:
    def __init__(self, brocker_rules):
        self.brocker_rules = ast.literal_eval(brocker_rules)
        self.error = ''
        self.merged_trades = []

    def __len__(self):
        return len(self.merged_trades)

    def load(self, file):
        try:
            trades = pd.read_csv(file)
        except:
            self.error = 'Could not read the file.'
            return
        merged_trades = {}
        if 'orderId' in self.brocker_rules:
            order_id_rule = self.brocker_rules['orderId']
            order_id_no = order_id_rule['col']
            order_id_regex = order_id_rule['regex']
            for i, trade in trades.iterrows():
                order_id = trade[order_id_no]
                match = re.match(order_id_regex, str(order_id))
                if match:
                    value = match.groupdict().get('value', '')
                    if value:
                        merged_trade = {k: '' for k in columns.keys()}
                        for column_name in columns:
                            column = columns[column_name]
                            if column_name not in self.brocker_rules:
                                if column.required:
                                    self.error = f"Invalied brocker rules. Brocker rule has no rule for '{column_name}'"
                                    return
                                merged_trade[column_name] = ''
                                continue
                            else:
                                column_rule = self.brocker_rules[column_name]
                            column_type = column_rule['type']
                            if column_type == 'field':
                                column_no = column_rule['col']
                                column_regex = column_rule['regex']
                                if column_no < len(trades.columns):
                                    value = trade[column_no]
                                    match = re.match(column_regex, str(value))
                                    if match:
                                        value = match.groupdict().get('value', '')
                                        column.set(value)
                                        if column.is_valid():
                                            value = column.get()
                                            merged_trade[column_name] = value
                                        else:
                                            self.error = column.error
                                            return
                                    else:
                                        self.error = f"Your file is not matching to the general format in the column '{column_name}'"
                                        return
                                elif column.required:
                                    self.error = f"Your file is not matching to the general format in the column '{column_name}' which is required"
                                    return                              
                            elif column_type == 'check':
                                column_values = column_rule['values']
                                for column_value in column_values:
                                    matchs  = []
                                    for column_value_rule in column_values[column_value]:
                                        column_no = column_value_rule['col']
                                        column_regex = column_value_rule['regex']
                                        value = trade[column_no]
                                        matchs.append(re.match(column_regex, str(value)))
                                    if all(matchs):
                                        merged_trade[column_name] = column_value
                                        break
                            merged_trade['id'] = hashlib.md5(':'.join(map(lambda i: str(i), merged_trade.values())).encode()).hexdigest()
                        if order_id in merged_trades:
                            merged_trades[order_id]['quantity'] += merged_trade['quantity']
                            merged_trades[order_id]['price'] += merged_trade['price']*merged_trade['quantity']
                        else:
                            merged_trades[order_id] = merged_trade
                            merged_trades[order_id]['price'] = merged_trade['price']*merged_trade['quantity']

                    else:
                        self.error = f"Your file is not matching to the general format in the column 'orderId'"
                        return
                else:
                    self.error = f"Your file is not matching to the general format in the column 'OrderId'"
                    return
        else: 
            self.error = f"Invalied brocker rules. Brocker rule has no rule for 'orderId'"
            return
        self.merged_trades = pd.DataFrame(list(merged_trades.values()))
        for idx, trade in self.merged_trades.iterrows():
            self.merged_trades.loc[idx, 'price'] = trade['price']/trade['quantity']

    def save(self, filename):
        self.merged_trades.to_csv(filename, index = False)

class OutputTrades:
    def __init__(self, merged_trades ):
        self.merged_trades = merged_trades.merged_trades
        self.output_trades = []

    def __len__(self):
        return len(self.output_trades)

    def save(self, filename):
        symbols = self.merged_trades['symbol'].drop_duplicates()
        output_trades = []
        for symbol in symbols:
            sorted_trades = self.merged_trades.loc[self.merged_trades['symbol'] == symbol]
            sorted_trades.sort_values(by=['tradeDate', 'executionTime'], ascending=[True, True], na_position='first')
            quantity = 0
            entry_date = None
            entry_time = None
            breakpoint = 0
            sum_buy_price = 0
            n_buy_trades = 0
            sum_sell_price = 0
            n_sell_trades = 0
            buy_quantity = 0
            sell_quantity = 0
            idxs = []
            for idx, trade in sorted_trades.iterrows():
                idxs.append(idx)
                if quantity == 0:
                    entry_date = trade['tradeDate']
                    entry_time = trade['executionTime']
                    trade_type = trade['tradeType']
                if trade['tradeType'] == 'sell':
                    breakpoint += 1
                    sum_sell_price += trade['quantity']*trade['price']
                    n_sell_trades += trade['quantity']
                    quantity -= trade['quantity']
                    buy_quantity += trade['quantity']
                elif trade['tradeType'] == 'buy':
                    breakpoint += 1
                    sum_buy_price += trade['quantity']*trade['price']
                    n_buy_trades += trade['quantity']
                    quantity += trade['quantity']
                    sell_quantity += trade['quantity']
                if quantity == 0:
                    avg_sell_price = round(sum_sell_price/n_sell_trades, 2) if n_sell_trades>0 else 0
                    avg_buy_price = round(sum_buy_price/n_buy_trades, 2) if n_buy_trades>0 else 0
                    qty = int((buy_quantity+sell_quantity)/2)
                    trade['entryPrice'] = avg_buy_price if trade_type == 'buy' else avg_sell_price
                    trade['entryDate'] = entry_date
                    trade['entryTime'] = entry_time
                    trade['exitPrice'] = avg_sell_price if trade_type == 'buy' else avg_buy_price
                    trade['exitDate'] = trade['tradeDate']
                    trade['exitTime'] = trade['executionTime']
                    trade['breakeven'] = breakpoint
                    trade['tradeType'] = trade_type
                    trade['avgBuyPrice'] = avg_buy_price
                    trade['avgSellPrice'] = avg_sell_price
                    trade['quantity'] = qty
                    trade['isOpen'] = 0
                    trade['stoploss'] = 0
                    trade['target'] = 0
                    trade['id'] = hashlib.md5(':'.join(map(lambda i: str(i), trade.to_list())).encode()).hexdigest()
                    trade['note'] = ''
                    trade['setup'] = ''
                    trade['mistakes'] = ''
                    trade['tags'] = ''
                    for i in idxs:
                        self.merged_trades.loc[i, 'tradeId'] = trade['id']
                    sum_buy_price = 0
                    n_buy_trades = 0
                    sum_sell_price = 0
                    n_sell_trades = 0
                    breakpoint = 0
                    buy_quantity = 0
                    sell_quantity = 0
                    idxs = []
                    output_trades.append(trade)
            if quantity != 0:
                avg_sell_price = round(sum_sell_price/n_sell_trades, 2) if n_sell_trades>0 else 0
                avg_buy_price = round(sum_buy_price/n_buy_trades, 2) if n_buy_trades>0 else 0
                qty = int((buy_quantity+sell_quantity)/2)
                trade['entryPrice'] = avg_buy_price if trade_type == 'buy' else avg_sell_price
                trade['entryDate'] = entry_date
                trade['entryTime'] = entry_time
                trade['exitPrice'] = avg_sell_price if trade_type == 'buy' else avg_buy_price
                trade['exitDate'] = trade['tradeDate']
                trade['exitTime'] = trade['executionTime']
                trade['breakeven'] = breakpoint
                trade['tradeType'] = trade_type
                trade['avgBuyPrice'] = avg_buy_price
                trade['avgSellPrice'] = avg_sell_price
                trade['quantity'] = qty
                trade['isOpen'] = 1
                trade['stoploss'] = 0
                trade['target'] = 0
                trade['id'] = hashlib.md5(':'.join(map(lambda i: str(i), trade.to_list())).encode()).hexdigest()
                trade['note'] = ''
                trade['setup'] = ''
                trade['mistakes'] = ''
                trade['tags'] = ''
                for i in idxs:
                    self.merged_trades.loc[i, 'tradeId'] = trade['id']
                output_trades.append(trade)
        todf = pd.DataFrame(output_trades)
        todf.drop(['tradeDate','executionTime', 'price'], axis = 1, inplace=True)
        todf.to_csv(filename, index=False)
        self.output_trades = output_trades
        return todf

class Trades:
    def __init__(self, user):
        self.user = user
        self.trades = None
        self.is_demo = False
        self.is_error = False

        self.trade_histories = TradeHistory.objects.filter(user=user, is_demo = False)
        if not self.trade_histories.exists():
            self.trade_histories = TradeHistory.objects.filter(user=user ,is_demo=True)
            self.is_demo = True

        if not self.trade_histories.exists():
            self.is_error = True
        else:
            is_trades = False
            for trade_history in self.trade_histories:
                output_filename = trade_history.output_trades
                output_trades = pd.read_csv(output_filename)
                output_trades.insert(1, 'tradeHistory', trade_history.pk)
                if is_trades:
                    self.trades = pd.concat([self.trades, output_trades]).drop_duplicates()
                else:
                    is_trades = True
                    self.trades = output_trades
                self.trades = self.trades.fillna('').sort_values('entryDate')
            
        self.filters = Filters(self)

    def get(self, layout):
        data = {}

        for field in layout:
            field.init(self.trades)

        for i, trade in self.trades.iterrows():
            trade = trade.to_dict()

            avg_buy_price = trade['avgBuyPrice']
            avg_sell_price = trade['avgSellPrice']
            trade_type = trade['tradeType']
            quantity = trade['quantity']
            
            pnl = round((avg_sell_price - avg_buy_price) * quantity, 2)
            if trade_type == TRADE_TYPE.Repr.BUY:
                roi = round(100*(avg_sell_price - avg_buy_price) / avg_buy_price, 2)
            else:
                roi = round(100*(avg_buy_price - avg_sell_price) / avg_sell_price, 2)

            status = STATUS.BREAKEVEN
            if pnl > 0:
                status = STATUS.WIN
            elif pnl < 0:
                status = STATUS.LOSS

            date_to_expiry = 'N/A'
            if trade['expiryDate']:
                expiry_date = datetime.datetime.strptime(trade['expiryDate'], '%Y-%m-%d')
                entry_date = datetime.datetime.strptime(trade['entryDate'], '%Y-%m-%d')

                date_to_expiry = (expiry_date - entry_date).days

                if date_to_expiry>=30:
                    date_to_expiry = '30+ days'
                elif date_to_expiry>6:
                    date_to_expiry = '6 to 30 days'
                elif date_to_expiry == 0:
                    date_to_expiry = 'Same day'
                else:
                    date_to_expiry = f'{date_to_expiry} days'

            trade['netPnl'] = pnl
            trade['status'] = status
            trade['roi'] = roi
            trade['charge'] = round(pnl / 10, 4)
            trade['dateToExpiry'] = date_to_expiry
            trade['setup'] = list(filter(lambda i: i != '', str(trade['setup']).split(',')))
            trade['mistakes'] = list(filter(lambda i: i != '', str(trade['mistakes']).split(',')))
            trade['tags'] = list(filter(lambda i: i != '', str(trade['tags']).split(',')))
            for field in layout:
                field.get(trade)

        for field in layout:
            field.convert(data, self)
            data[field.name] = field.data

        return data

    def update(self, trade_update):
        trade_history = TradeHistory.objects.filter(user=self.user, pk = trade_update['tradeHistory'])
        if trade_history.exists():
            trade_history = trade_history[0]
            output_trades = pd.read_csv(trade_history.output_trades)
            trade = output_trades[output_trades['id'] == trade_update['id']]
            index = trade.index[0]
            trade = trade.to_dict('records')[0]
            trade_update['setup'] = ','.join(trade_update['setup'])
            trade_update['mistakes'] = ','.join(trade_update['mistakes'])
            trade_update['tags'] = ','.join(trade_update['tags'])
            for column in trade_update:
                if column in trade and trade[column] != trade_update[column]:
                    output_trades.loc[index, column] = trade_update[column]
            output_trades.to_csv(trade_history.output_trades, index=False)
            return True
        return False

class Orders:
    def __init__(self, user):
        self.user = user
        self.orders = None
        self.is_demo = False
        self.is_error = False

        self.trade_histories = TradeHistory.objects.filter(user=user, is_demo = False)
        if not self.trade_histories.exists():
            self.trade_histories = TradeHistory.objects.filter(user=user ,is_demo=True)
            self.is_demo = True

        if not self.trade_histories.exists():
            self.is_error = True
        else:
            is_orders = False
            for trade_history in self.trade_histories:
                merged_filename = trade_history.merged_trades
                merged_trades = pd.read_csv(merged_filename)
                merged_trades.insert(1, 'tradeHistory', trade_history.pk)
                if is_orders:
                    self.orders = pd.concat([self.orders, merged_trades]).drop_duplicates()
                else:
                    is_orders = True
                    self.orders = merged_trades
                self.orders = self.orders.fillna('').sort_values('tradeDate')
    
    def get(self, layout):
        data = {}

        for field in layout:
            field.init(self.orders)

        for i, order in self.orders.iterrows():
            order = order.to_dict()

            for field in layout:
                field.get(order)

        for field in layout:
            field.convert(data, self)
            data[field.name] = field.data

        return data
    
    # def update(self, order_update):
    #     trade_history = TradeHistory.objects.filter(user=self.user, pk = order_update['tradeHistory'])
    #     if trade_history.exists():
    #         trade_history = trade_history[0]
    #         merged_trades = pd.read_csv(trade_history.merged_trades)
    #         order = merged_trades[merged_trades['id'] == order_update['id']]
    #         index = order.index[0]
    #         order = order.to_dict('records')[0]
    #         for column in order_update:
    #             if column in order and order[column] != order_update[column]:
    #                 merged_trades.loc[index, column] = order_update[column]
    #         merged_trades.to_csv(trade_history.merged_trades, index=False)
            
    #         trades = Trades(self.user)
    #         layout = [
    #             fields.trade(order['tradeId']),
    #             fields.orders(order['tradeId'])
    #         ]
    #         data = trades.get(layout)
    #         trade_update = {}
    #         quantity = 0
    #         entry_date = None
    #         entry_time = None
    #         breakpoint = 0
    #         sum_buy_price = 0
    #         n_buy_trades = 0
    #         sum_sell_price = 0
    #         n_sell_trades = 0
    #         buy_quantity = 0
    #         sell_quantity = 0
    #         for trade in data['orders']:
    #             if quantity == 0:
    #                 entry_date = trade['tradeDate']
    #                 entry_time = trade['executionTime']
    #                 trade_type = trade['tradeType']
    #             if trade['tradeType'] == 'sell':
    #                 breakpoint += 1
    #                 sum_sell_price += trade['quantity']*trade['price']
    #                 n_sell_trades += trade['quantity']
    #                 quantity -= trade['quantity']
    #                 buy_quantity += trade['quantity']
    #             elif trade['tradeType'] == 'buy':
    #                 breakpoint += 1
    #                 sum_buy_price += trade['quantity']*trade['price']
    #                 n_buy_trades += trade['quantity']
    #                 quantity += trade['quantity']
    #                 sell_quantity += trade['quantity']
    #             if quantity == 0:
    #                 avg_sell_price = round(sum_sell_price/n_sell_trades, 2) if n_sell_trades>0 else 0
    #                 avg_buy_price = round(sum_buy_price/n_buy_trades, 2) if n_buy_trades>0 else 0
    #                 qty = int((buy_quantity+sell_quantity)/2)
    #                 trade['entryPrice'] = avg_buy_price if trade_type == 'buy' else avg_sell_price
    #                 trade['entryDate'] = entry_date
    #                 trade['entryTime'] = entry_time
    #                 trade['exitPrice'] = avg_sell_price if trade_type == 'buy' else avg_buy_price
    #                 trade['exitDate'] = trade['tradeDate']
    #                 trade['exitTime'] = trade['executionTime']
    #                 trade['breakeven'] = breakpoint
    #                 trade['tradeType'] = trade_type
    #                 trade['avgBuyPrice'] = avg_buy_price
    #                 trade['avgSellPrice'] = avg_sell_price
    #                 trade['quantity'] = qty
    #                 trade['isOpen'] = 0
    #                 trade['stoploss'] = 0
    #                 trade['target'] = 0
    #                 trade['id'] = hashlib.md5(':'.join(map(lambda i: str(i), trade.to_list())).encode()).hexdigest()
    #                 trade['note'] = ''
    #                 trade['setup'] = ''
    #                 trade['mistakes'] = ''
    #                 trade['tags'] = ''
    #                 sum_buy_price = 0
    #                 n_buy_trades = 0
    #                 sum_sell_price = 0
    #                 n_sell_trades = 0
    #                 breakpoint = 0
    #                 buy_quantity = 0
    #                 sell_quantity = 0
    #                 idxs = []
    #                 output_trades.append(trade)
    #         if quantity != 0:
    #             avg_sell_price = round(sum_sell_price/n_sell_trades, 2) if n_sell_trades>0 else 0
    #             avg_buy_price = round(sum_buy_price/n_buy_trades, 2) if n_buy_trades>0 else 0
    #             qty = int((buy_quantity+sell_quantity)/2)
    #             trade['entryPrice'] = avg_buy_price if trade_type == 'buy' else avg_sell_price
    #             trade['entryDate'] = entry_date
    #             trade['entryTime'] = entry_time
    #             trade['exitPrice'] = avg_sell_price if trade_type == 'buy' else avg_buy_price
    #             trade['exitDate'] = trade['tradeDate']
    #             trade['exitTime'] = trade['executionTime']
    #             trade['breakeven'] = breakpoint
    #             trade['tradeType'] = trade_type
    #             trade['avgBuyPrice'] = avg_buy_price
    #             trade['avgSellPrice'] = avg_sell_price
    #             trade['quantity'] = qty
    #             trade['isOpen'] = 1
    #             trade['stoploss'] = 0
    #             trade['target'] = 0
    #             trade['id'] = hashlib.md5(':'.join(map(lambda i: str(i), trade.to_list())).encode()).hexdigest()
    #             trade['note'] = ''
    #             trade['setup'] = ''
    #             trade['mistakes'] = ''
    #             trade['tags'] = ''
    #             for i in idxs:
    #                 self.merged_trades.loc[i, 'tradeId'] = trade['id']
    #             output_trades.append(trade)
    #     todf = pd.DataFrame(output_trades)
    #     todf.drop(['tradeDate','executionTime', 'price'], axis = 1, inplace=True)
    #     todf.to_csv(filename, index=False)
    #     self.output_trades = output_trades
    #         trades.update()
    #         return True
    #     return False
