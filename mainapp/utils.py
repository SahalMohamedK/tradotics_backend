import pandas as pd
import re
import ast
from .consts import TRADE_TYPE, PNL_STATUS

class Rule:
    def __init__(self, rules):
        self.rules = ast.literal_eval(rules)

    def match(self, regex, value):
        if regex and value:
            typeValue = type(value)
            regex = regex.replace('\x08', '\\b')
            match = re.match(regex, str(value))
            if match:
                if len(match.groups()) > 0:
                    return typeValue(match.groups()[0])
                return typeValue(match.group())

    def getValue(self, col, trade):
        no = self.rules[col][0]
        regex = self.rules[col][1]
        value = trade.get(no)
        value = self.match(regex, value)
        return col, value
    
    def convert(self, trades):
        nTrades = []
        for trade in trades:
            nTrade = {}
            for col in self.rules:
                col, value = self.getValue(col, trade)
                nTrade[col] = value
            nTrades.append(nTrade)
        return nTrades

class CheckRule(Rule):
    def __init__(self, col, rules):
        Rule.__init__(self, rules)
        self.col = col

    def getValue(self, col, trade):
        rule = self.rules[col]
        value = None
        if type(rule[0]) == list:
            vs = []
            for n, r in rule:
                v = trade.get(n)
                r = r.replace('\x08', '\\b')
                v = self.match(r,v)
                vs.append(v)
            if all(vs):
                return self.col, col
        else:
            no = self.rules[col][0]
            regex = self.rules[col][1]
            value = trade.get(no)
            regex = regex.replace('\x08', '\\b')
            if self.match(regex, value):
                return self.col, col
        return self.col, None
        
    def convert(self, trades):
        nTrades = []
        for trade in trades:
            nTrade = trade if type(trade) == dict else {self.col: None}
            for col in self.rules:
                col, value = self.getValue(col, trade)
                if col and value:
                    nTrade[col] = value
            nTrades.append(nTrade)
        return nTrades

class MergedTrades:
    def __init__(self, uploadFile):
        self.uploadFile = uploadFile
        self.rules = []
    
    def addRule(self, rule):
        self.rules.append(rule)
    
    def save(self, filename):
        trades = pd.read_csv(self.uploadFile)
        iTrades = []
        for idx, trade in trades.iterrows():
            iTrades.append(trade)
        cTrades = []
        for rule in self.rules:
            oTrades = rule.convert(iTrades)
            for i, trade in enumerate(oTrades):
                if i<len(cTrades):
                    cTrades[i].update(trade)
                else:
                    cTrades.append(trade)
        mTrades = {}
        for trade in cTrades:
            order_id = trade.get('order_id')
            if order_id:
                if order_id in mTrades:
                    mTrades[order_id]['quantity'] += trade['quantity']
                else:
                    mTrades[order_id] = trade
        mTradeDf = pd.DataFrame(mTrades.values())
        mTradeDf.to_csv(filename, index=False)
        return mTradeDf
        

class OutputTrades:
    def __init__(self, mTradeDf):
        self.mTradeDf = mTradeDf

    def save(self, filename):
        symbols = self.mTradeDf['symbol'].drop_duplicates()
        outpuTrades = []
        for symbol in symbols:
            sdf = self.mTradeDf.loc[self.mTradeDf['symbol'] == symbol]
            sdf.sort_values(by=['trade_date', 'order_execution_time'], ascending=[True, True], na_position='first')
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
            for idx, trade in sdf.iterrows():
                if quantity == 0:
                    entry_date = trade['trade_date']
                    entry_time = trade['order_execution_time']
                    trade_type = trade['trade_type']
                if trade['trade_type'] == 'sell':
                    breakpoint += 1
                    sum_sell_price += trade['quantity']*trade['price']
                    n_sell_trades += trade['quantity']
                    quantity -= trade['quantity']
                    buy_quantity += trade['quantity']
                elif trade['trade_type'] == 'buy':
                    breakpoint += 1
                    sum_buy_price += trade['quantity']*trade['price']
                    n_buy_trades += trade['quantity']
                    quantity += trade['quantity']
                    sell_quantity += trade['quantity']
                if quantity == 0:
                    avg_sell_price = sum_sell_price/n_sell_trades
                    avg_buy_price = sum_buy_price/n_buy_trades
                    qty = (buy_quantity+sell_quantity)
                    if trade_type == TRADE_TYPE.BUY:
                        pnl = round((avg_sell_price - avg_buy_price) * qty, 4)
                    else:
                        pnl = round((avg_buy_price - avg_sell_price) * qty, 4)
                    pnl_status = PNL_STATUS.BREAKEVEN
                    if pnl > 0:
                        pnl_status = PNL_STATUS.WIN
                    elif pnl < 0:
                        pnl_status = PNL_STATUS.LOSS
                    roi = round((avg_buy_price - avg_sell_price) / avg_sell_price, 4)
                    if trade_type == "buy":
                        roi = round((avg_sell_price - avg_buy_price) / avg_buy_price, 4)
                    trade.drop(['trade_date', 'order_id','order_execution_time'])
                    trade['entry_date'] = entry_date
                    trade['entry_time'] = entry_time
                    trade['exit_date'] = trade['trade_date']
                    trade['exit_time'] = trade['order_execution_time']
                    trade['breakeven_point'] = breakpoint
                    trade['trade_type'] = trade_type
                    trade['avg_buy_price'] = avg_buy_price
                    trade['avg_sell_price'] = avg_sell_price
                    trade['quantity'] = qty
                    trade['net_pnl'] = pnl
                    trade['status'] = pnl_status
                    trade['roi'] = roi
                    sum_buy_price = 0
                    n_buy_trades = 0
                    sum_sell_price = 0
                    n_sell_trades = 0
                    breakpoint = 0
                    buy_quantity = 0
                    sell_quantity = 0
                    outpuTrades.append(trade)
        todf = pd.DataFrame(outpuTrades)
        todf.to_csv(filename, index=False)
        return todf

def uniqueTrades(trades):
    unique_trades = {}
    for trade_history in trades:
        output_filename = trade_history.output_trades
        output_trades = pd.read_csv(output_filename)
        for i, trade in output_trades.iterrows():
            order_id = trade['order_id']
            if order_id not in unique_trades:
                unique_trades[order_id] = trade
    return pd.DataFrame(unique_trades.values())
