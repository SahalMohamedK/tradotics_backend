import re
import pandas as pd
import hashlib
import math
import ast
import datetime
from .models import TradeHistory
from .consts import ASSETS_TYPE, TRADE_TYPE, OPTIONS_TYPE, STATUS
from .trades.filters import Filters
from .trades.utils import human_delta
from django.conf import settings

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

class MergedTrades:
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
        'assetType': Rule(r'^([0-9]|[1][0])$', type = int, choice=ASSETS_TYPE),
    }

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
                        merged_trade = {k: '' for k in self.columns.keys()}
                        for column_name in self.columns:
                            column = self.columns[column_name]
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
        is_trades = False
        self.trade_histories = TradeHistory.objects.filter(user=user, is_demo = False)
        if not self.trade_histories.exists():
            self.trade_histories = TradeHistory.objects.filter(user=user ,is_demo=True)
            self.is_demo = True
        for trade_history in self.trade_histories:
            output_filename = trade_history.output_trades
            output_trades = pd.read_csv(output_filename)
            output_trades.insert(1, 'tradeHistory', trade_history.pk)
            if is_trades:
                self.trades = pd.concat([self.trades, output_trades]).drop_duplicates()
            else:
                is_trades = True
                self.trades = output_trades
            self.trades = self.trades.fillna('')
        self.init()

    def init(self):
        for i, trade in self.trades.iterrows():
            avg_buy_price = trade['avgBuyPrice']
            avg_sell_price = trade['avgSellPrice']
            trade_type = trade['tradeType']
            quantity = trade['quantity']
            
            pnl = round((avg_sell_price - avg_buy_price) * quantity, 2)
            if trade_type == TRADE_TYPE.Repr.BUY:
                roi = round(100*(avg_sell_price - avg_buy_price) / avg_buy_price, 2)
                # realized_rr = round((avg_sell_price - avg_buy_price) / (avg_buy_price - stoploss))
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

            self.trades.loc[i, 'netPnl'] = pnl
            self.trades.loc[i, 'status'] = status
            self.trades.loc[i, 'roi'] = roi
            self.trades.loc[i, 'charge'] = round(pnl / 10, 4)
            self.trades.loc[i, 'dateToExpiry'] = date_to_expiry

        self.filters = Filters(self)
    
    def get(self, id = None):
        if id:
            trade = self.trades.loc[self.trades['id'] == id]
            if not trade.empty:
                trade = trade.to_dict('records')[0]
                setup = trade['setup']
                if not pd.isnull(setup):
                    trade['setup'] = list(filter(lambda i: i, trade['setup'].split(',')))
                else:
                    trade['setup'] = []
                
                mistakes = trade['mistakes']
                if not pd.isnull(mistakes):
                    trade['mistakes'] = list(filter(lambda i: i, trade['mistakes'].split(',')))
                else:
                    trade['mistakes'] = []
                
                tags = trade['tags']
                if not pd.isnull(tags):
                    trade['tags'] = list(filter(lambda i: i, trade['tags'].split(',')))
                else:
                    trade['tags'] = []
                return trade
            return None
        return self.trades.to_dict('records')
        
    def total_quantity(self):
        return sum(self.trades['quantity'].to_list())
    
    def cumulative_pnl(self):
        pnl_by_date = {}
        for i, trade in self.trades.iterrows():
            date = trade['entryDate']
            if date in pnl_by_date:
                pnl_by_date[date] += trade['netPnl']
            else:
                pnl_by_date[date] = trade['netPnl']
        
        labels = list(pnl_by_date.keys())
        labels.sort(key = lambda i: datetime.datetime.strptime(i, '%Y-%m-%d'))
        cumulative_pnls = []
        sum_pnl = 0
        for date in labels:
            pnl = pnl_by_date[date]
            sum_pnl += pnl
            cumulative_pnls.append(sum_pnl)
        return [labels ,cumulative_pnls]
    
    def total_net_pnl(self):
        return sum(self.trades['netPnl'].to_list())
    
    def total_trades(self):
        return len(self.trades)

    def avg_winners(self):
        return 3000

    def avg_losers(self):
        return 3000

    def profit_factor(self):
        winners = 0
        losers = 0
        for i, trade in self.trades.iterrows():
            if trade['status'] == STATUS.WIN:
                winners+= trade['netPnl']
            elif trade['status'] == STATUS.LOSS:
                losers+=trade['netPnl']
        if losers:
            return round(abs(winners/losers), 2)
        return 0
    
    def get_trades_by_days(self):
        trades = {}
        for i, trade in self.trades.iterrows():
            day = trade['entryDate']
            if day in trades:
                trades[day] = [trades[day][0]+trade['netPnl'], trades[day][1]+1]
            else:
                trades[day] = [trade['netPnl'], 1]
        return trades
    
    def winners_and_losers(self):
        winners = 0
        losers = 0
        for i, trade in self.trades.iterrows():
            if trade['status'] == STATUS.WIN:
                winners+=1
            elif trade['status'] == STATUS.LOSS:
                losers+=1
        return [winners, losers]

    def winners_and_losers_by_days(self):
        winners = 0
        losers = 0
        trades = {}
        for i, trade in self.trades.iterrows():
            day = trade['entryDate']
            if day in trades:
                trades[day] += trade['netPnl']
            else:
                trades[day] = trade['netPnl']
        for day in trades:
            net_pnl = trades[day]
            if net_pnl>0:
                winners += 1
            else:
                losers+=1
        return [winners, losers]

    def returns(self):
        returns = {
            'winners': 0,
            'losers': 0,
            'long': 0,
            'short': 0,
        }
        for i, trade in self.trades.iterrows():
            if trade['status'] == STATUS.WIN:
                returns['winners']+=trade['netPnl']
            elif trade['status'] == STATUS.LOSS:
                returns['losers']+=trade['netPnl']
            if trade['tradeType'] == TRADE_TYPE.Repr.BUY:
                returns['long']+= trade['netPnl']
            elif trade['tradeType'] == TRADE_TYPE.Repr.SELL:
                returns['short']+= trade['netPnl']
        return returns

    def days(self):
        days = {
            'winners': 0,
            'losers': 0,
            'total': 0,
            'consecWin': 0,
            'consecLoss': 0
        }
        trades = {}
        for i, trade in self.trades.iterrows():
            day = trade['entryDate']
            if day in trades:
                trades[day] += trade['netPnl']
            else:
                trades[day] = trade['netPnl']
        curDay = None
        consec = 1
        for day in trades:
            net_pnl = trades[day]
            if day != curDay:
                if net_pnl>0:
                    if days['consecWin'] < consec:
                        days['consecWin'] = consec
                elif net_pnl<0:
                    if days['consecLoss'] < consec:
                        days['consecLoss'] = consec
                consec = 1
            else:
                consec += 1
            if net_pnl>0:
                days['winners'] += 1
            elif net_pnl<0:
                days['losers']+=1
            days['total']+=1
            curDay = day
        return days
    
    def max_consec(self):
        consec_wins = []
        consec_loss = []
        wins = 0
        loss = 0
        for i, trade in self.trades.iterrows():

            if trade['status'] == STATUS.WIN:
                wins += 1
            else:
                if wins:
                    consec_wins.append(wins)
                wins = 0
            if trade['status'] == STATUS.LOSS:
                loss += 1
            else:
                if loss:
                    consec_loss.append(loss)
                loss = 0
        if wins:
            consec_wins.append(wins)
        if loss:
            consec_loss.append(loss)
        if consec_loss:
            loss = max(consec_loss)
        else:
            loss = 0
        if consec_wins:
            wins = max(consec_wins)
        else:
            wins = 0
        return [wins, loss]
    
    def counts(self):
        counts = {
            'winners': 0,
            'losers': 0,
            'short': 0,
            'long': 0,
        }
        for i, trade in self.trades.iterrows():
            if trade['status'] == STATUS.WIN:
                counts['winners'] += 1
            elif trade['status'] == STATUS.LOSS:
                counts['losers'] += 1
            
            if trade['tradeType'] == TRADE_TYPE.Repr.BUY:
                counts['long'] += 1
            else:
                counts['short'] += 1
        return counts
    
    def rois(self):
        rois = {
            'total': 0,
            'winners': 0,
            'losers': 0,
            'long': 0,
            'short': 0,
        }

        for i, trade in self.trades.iterrows():
            if trade['status'] == STATUS.WIN:
                rois['winners'] += trade['roi']
            elif trade['status'] == STATUS.LOSS:
                rois['losers'] += trade['roi']
            
            if trade['tradeType'] == TRADE_TYPE.Repr.BUY:
                rois['long'] += trade['roi']
            else:
                rois['short'] += trade['roi']
            rois['total']+= trade['roi']
        return rois

    def open_trades(self):
        return self.trades.loc[self.trades['isOpen'] == 1].to_dict('records')

    def pnl_by_days(self):
        trades = [0, 0, 0, 0, 0, 0, 0]
        pnls = [0, 0, 0, 0, 0, 0, 0]
        costs = [0, 0, 0, 0, 0, 0, 0]
        for i, trade in self.trades.iterrows():
            date = trade['entryDate']
            d = datetime.datetime.strptime(date, '%Y-%m-%d')
            pnls[(d.weekday()+1)%7] += trade['netPnl']
            trades[(d.weekday()+1)%7] += 1
            costs[(d.weekday()+1)%7] += trade['entryPrice']*trade['quantity']

        return  [pnls, trades, costs]

    def pnl_by_hours(self):
        _trades = [0 for _ in range(24)]
        _pnls = [0 for _ in range(24)]
        _costs = [0 for _ in range(24)]
        _labels = ['12am - 1am', '1am - 2am', '2am - 3am', '3am - 4am', '4am - 5am', '5am - 6am', '6am - 7am', '7am - 8am', '8am - 9am',
    '9am - 10am', '10am - 11am', '11am - 12pm', '12pm - 1pm', '1pm - 2pm', '2pm - 3pm', '3pm - 4pm', '4pm - 5pm', '5pm - 6pm', '6pm - 7pm', '7pm - 8pm', '8pm - 9pm',
    '9pm - 10pm', '10pm - 11pm', '11pm - 12am']
        for i, trade in self.trades.iterrows():
            time = trade['entryTime']
            t = datetime.datetime.strptime(time, '%H:%M:%S')
            _pnls[t.hour] += trade['netPnl']
            _trades[t.hour] += 1
            _costs[t.hour] += trade['entryPrice']*trade['quantity']
        
        trades = []
        pnls = []
        costs = []
        labels = []
        for i, trade in enumerate(_trades):
            if trade>0:
                trades.append(_trades[i])
                pnls.append(_pnls[i])
                costs.append(_costs[i])
                labels.append(_labels[i])
        return  [labels, pnls, trades, costs]
    
    def pnl_by_months(self):
        trades = [0 for _ in range(12)]
        pnls = [0 for _ in range(12)]
        costs = [0 for _ in range(12)]
        for i, trade in self.trades.iterrows():
            date = trade['entryDate']
            d = datetime.datetime.strptime(date, '%Y-%m-%d')
            pnls[d.month-1] += trade['netPnl']
            trades[d.month-1] += 1
            costs[d.month-1] += trade['entryPrice']*trade['quantity']
        return  [pnls, trades, costs]

    def pnl_by_setup(self):
        pnls = [0, 0, 0, 0, 0, 0, 0]
        trades = [0, 0, 0, 0, 0, 0, 0]
        costs = [0, 0, 0, 0, 0, 0, 0]
        # for i, trade in self.trades.iterrows():
        #     date = trade['entryDate']
        #     d = datetime.datetime.strptime(date, '%Y-%m-%d')
        #     pnls[d.month-1] += trade['netPnl']
        return  [pnls, trades, costs]
        
    def pnl_by_duration(self):
        pnls = [0, 0, 0, 0, 0]
        trades = [0, 0, 0, 0, 0]
        costs = [0, 0, 0, 0, 0]
        def dur_min(n):
            return datetime.timedelta(seconds = n*60)
        for i, trade in self.trades.iterrows():
            entryDate = trade['entryDate']
            entryTime = trade['entryTime']
            exitDate = trade['exitDate']
            exitTime = trade['exitTime']
            pnl = trade['netPnl']

            startTime = datetime.datetime.strptime(f'{entryDate} {entryTime}', '%Y-%m-%d %H:%M:%S')
            endTime = datetime.datetime.strptime(f'{exitDate} {exitTime}', '%Y-%m-%d %H:%M:%S')
            dur = endTime-startTime
            
            if dur >= dur_min(1) and dur <= dur_min(5):
                pnls[0] += pnl
                trades[0] += 1
                costs[0] += trade['entryPrice']*trade['quantity']
            elif dur > dur_min(5) and dur <= dur_min(10):
                pnls[1] += pnl
                trades[1] += 1
                costs[1] += trade['entryPrice']*trade['quantity']
            elif dur > dur_min(10) and dur <= dur_min(20):
                pnls[2] += pnl
                trades[2] += 1
                costs[2] += trade['entryPrice']*trade['quantity']
            elif dur > dur_min(20) and dur <= dur_min(40):
                pnls[3] += pnl
                trades[3] += 1
                costs[3] += trade['entryPrice']*trade['quantity']
            elif dur > dur_min(40):
                pnls[4] += pnl
                trades[4] += 1
                costs[4] += trade['entryPrice']*trade['quantity']
        return [pnls, trades, costs]

    def pnl_by_cost(self):
        min_cost = 10000**10
        max_cost = 0
        for i, trade in self.trades.iterrows():
            cost = trade['entryPrice']*trade['quantity']
            if cost < min_cost:
                min_cost = cost
            
            if cost>max_cost:
                max_cost = cost
        
        def magicRound(n, func):
            return func(n/(10**(len(str(int(n)))-1)))*(10**(len(str(int(n)))-1))

        min_cost = magicRound(min_cost, math.floor)
        max_cost = magicRound(max_cost, math.ceil)
        limits = sorted(set(map(lambda n: magicRound(n, math.floor), list(range(min_cost, max_cost+1, int((max_cost-min_cost)/10))))))
        
        labels = []
        i = 0
        while i<len(limits)-1:
            labels.append(f'${limits[i]} - ${limits[i+1]}')
            i+=1

        pnls = [0 for _ in range(len(limits))]
        trades = [0 for _ in range(len(limits))]
        costs = [0 for _ in range(len(limits))]
        for i, trade in self.trades.iterrows():
            cost = trade['entryPrice']*trade['quantity']
            j = 0
            while j<len(limits)-1:
                if limits[j]<=cost and cost < limits[j+1]:
                    pnls[j] += trade['netPnl'] 
                    trades[j] += 1
                    costs[j] += cost
                j+=1

        return [labels, pnls, trades, costs]

    def pnl_by_price(self):
        min_price = 10000**10
        max_price = 0
        for i, trade in self.trades.iterrows():
            price = trade['entryPrice']
            if price < min_price:
                min_price = price
            
            if price>max_price:
                max_price = price
        
        def magicRound(n, func):
            return func(n/(10**(len(str(int(n)))-1)))*(10**(len(str(int(n)))-1))

        min_price = magicRound(min_price, math.floor)
        max_price = magicRound(max_price, math.ceil)
        limits = sorted(set(map(lambda n: magicRound(n, math.floor), list(range(min_price, max_price+1, int((max_price-min_price)/10))))))
        
        labels = []
        i = 0
        while i<len(limits)-1:
            labels.append(f'${limits[i]} - ${limits[i+1]}')
            i+=1

        pnls = [0 for _ in range(len(limits))]
        trades = [0 for _ in range(len(limits))]
        costs = [0 for _ in range(len(limits))]
        for i, trade in self.trades.iterrows():
            price = trade['entryPrice']
            j = 0
            while j<len(limits)-1:
                if limits[j]<=price and price < limits[j+1]:
                    pnls[j] += trade['netPnl'] 
                    trades[j] += 1
                    costs[j] += trade['entryPrice']*trade['quantity']
                j+=1

        return [labels, pnls, trades, costs]

    def pnl_by_symbol(self):
        labels = self.trades['symbol'].drop_duplicates().to_list()
        
        pnls = [0 for _ in range(len(labels))]
        trades = [0 for _ in range(len(labels))]
        costs = [0 for _ in range(len(labels))]
        
        for i, trade in self.trades.iterrows():
            j = labels.index(trade['symbol'])
            pnls[j] += trade['netPnl'] 
            trades[j] += 1
            costs[j] += trade['entryPrice']*trade['quantity']
        
        return [labels, pnls, trades, costs]

    def open_and_close(self):
        return [len(self.trades.loc[self.trades['isOpen'] == 0]), len(self.trades.loc[self.trades['isOpen'] == 1])]

    def dialy_pnl(self):
        pnls = {}
        for i, trade in self.trades.iterrows():
            date = trade['entryDate']
            pnl = trade['netPnl']
            if date in pnls:
                pnls[date] += pnl
            else:
                pnls[date] = pnl
        return [list(pnls.keys()), list(pnls.values())]

    def highest_and_lowest_pnl(self):
        hTrade = {'entryDate': "2022-01-01", 'entryPrice': 0, 'entryTime': "10:10:10", 'exitDate': "2022-01-01", 
            'exitPrice': 0, 'exitTime': "10:10:10", 'netPnl': 0 , 'quantity': 0, 'roi': 0,
            'status': 0, 'symbol': "N/A", 'tradeType': "1", 'id':'N/A'}
        lTrade = {'entryDate': "2022-01-01", 'entryPrice': 0, 'entryTime': "10:10:10", 'exitDate': "2022-01-01", 
            'exitPrice': 0, 'exitTime': "10:10:10", 'netPnl': 100**10 , 'quantity': 0, 'roi': 0,
            'status': 0, 'symbol': "N/A", 'tradeType': "1", 'id':'N/A'}
        for i, trade in self.trades.iterrows():
            if hTrade['netPnl'] < trade['netPnl']:
                hTrade = trade.to_dict()
            if lTrade['netPnl'] > trade['netPnl']:
                lTrade = trade.to_dict()
        return [hTrade, lTrade]
    
    def hold_times(self):
        sum_hold_time = datetime.timedelta(0)
        sum_winners_hold_time = datetime.timedelta(0)
        sum_lossers_hold_time = datetime.timedelta(0)
        sum_long_hold_time = datetime.timedelta(0)
        sum_short_hold_time = datetime.timedelta(0)
        highest_hold_tile = datetime.timedelta(0)
        pnl = 0
        n = 0
        for i, trade in self.trades.iterrows():
            n+=1
            entryDate = trade['entryDate']
            entryTime = trade['entryTime']
            exitDate = trade['exitDate']
            exitTime = trade['exitTime']
            startTime = datetime.datetime.strptime(f'{entryDate} {entryTime}', '%Y-%m-%d %H:%M:%S')
            endTime = datetime.datetime.strptime(f'{exitDate} {exitTime}', '%Y-%m-%d %H:%M:%S')
            dur = endTime-startTime
            if pnl<trade['netPnl']:
                highest_hold_tile = dur
                pnl = trade['netPnl']

            sum_hold_time += dur
            if trade['status'] == STATUS.WIN:
                sum_winners_hold_time += dur
            elif trade['status'] == STATUS.LOSS:
                sum_lossers_hold_time += dur

            if trade['tradeType'] == TRADE_TYPE.Repr.BUY:
                sum_long_hold_time += dur
            else:
                sum_short_hold_time += dur
        return [
            human_delta(sum_hold_time/(n if n > 0 else 1)),
            human_delta(sum_winners_hold_time/(n if n > 0 else 1)),
            human_delta(sum_lossers_hold_time/(n if n > 0 else 1)),
            human_delta(sum_long_hold_time/(n if n > 0 else 1)),
            human_delta(sum_short_hold_time/(n if n > 0 else 1)),
            human_delta(highest_hold_tile),
            ]

    def dashboard_insights(self):
        insights = []
        winners_pnl = 0
        winners = 0
        lossers_pnl = 0
        lossers = 0
        for i, trade in self.trades.iterrows():
            if ASSETS_TYPE.is_options(trade['assetType']):
                insights.append('Most of profits are from in the money option strike (70% - $600)')
                break
            if trade['status'] == STATUS.WIN:
                winners_pnl+=trade['netPnl']
                winners += 1
            elif trade['status'] == STATUS.LOSS:
                lossers_pnl+=trade['netPnl']
                lossers += 1
        avg_winners = round(winners_pnl/winners, 2) if winners>0 else 0
        avg_lossers = abs(round(lossers_pnl/lossers, 2))if lossers>0 else 0
        if avg_lossers > avg_winners:
            insights.append(f'Your average losing trades is ${avg_lossers} while winning trades are only ${avg_winners}')
        return insights

    def date_to_expiry(self):
        labels = ['Same day', '1 day', '2 day', '3 day', '4 day', '5 day', '6 day', '6 to 30 days', '30+ days']
        trades = [0 for _ in range(len(labels))]
        pnls = [0 for _ in range(len(labels))]
        costs = [0 for _ in range(len(labels))]
        winrates = [0 for _ in range(len(labels))]
        for i, trade in self.trades.iterrows():
            date_to_expiry = trade['dateToExpiry']
            if date_to_expiry in labels:
                trades[labels.index(date_to_expiry)] += 1
                pnls[labels.index(date_to_expiry)] += trade['netPnl']
                costs[labels.index(date_to_expiry)] += trade['entryPrice']*trade['quantity']
                # winrates[labels.index(date_to_expiry)]  += 

        return [labels, pnls, trades, costs]            

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
                self.trades = self.trades.fillna('')
            
        self.filters = Filters(self)

    def get(self, layout):
        data = {}
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
            for field in layout.get('loop', []):
                if field.is_first:
                    field_data = field.start(trade)
                    field.is_first = False
                else:
                    field_data = field.next(data[field.name], trade)
                data[field.name] = field_data

        for field in layout.get('loop', []):
            data[field.name] = field.end(data[field.name])

        for field in layout.get('init', []):
            data[field.name] = field.get(data, self)

        return data