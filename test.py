import pandas as pd
import re
import ast

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

class TradeHandler:
    def __init__(self, filename):
        self.filename = filename
        self.rules = []
    
    def addRule(self, rule):
        self.rules.append(rule)
    
    def convert(self):
        trades = pd.read_csv(self.filename)
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
            order_id = trade['order_id']
            if order_id in mTrades:
                mTrades[order_id]['quantity'] = float(mTrades[order_id]['quantity'])+float(trade['quantity'])
            else:
                mTrades[order_id] = trade
        return mTrades.values()

fields_rule = Rule("""{
        'symbol': [0, r'.*'],
        'trade_date': [2, r'.*'],
        'exchange': [3, r'.*'],
        'segment': [4, r'.*'],
        'trade_type': [6, r'.*'],
        'quantity': [7, r'.*'],
        'price': [8, r'.*'],
        'order_id': [10, r'.*'],
        'order_execution_time': [11, r'.*(\d\d:\d\d:\d\d)$'],
        'strike_price': [None, ''],
        'expiry_date': [None, ''],
        'options_type': [0, r'.*\d(PE|CE)$'],
    }""")
assets_rule = CheckRule('assets_type', """{
        'cash': [4, r'\bEQ\b'],
        'equity_options': [[4, r'\bFO\b'], [0, r'.*((CE$)|(PE$))']],
        'equity_futures': [[4, r'\bFO\b'], [0, r'.*(FUT$)']],
        'forex_spot':  [None, ''],
        'forex_options': [[4, r'\bCDS\b'], [0, r'.*((CE$)|(PE$))']],
        'forex_futures': [[4, r'\bCDS\b'], [0, r'.*(FUT$)']],
        'commodity_futures': [[4, r'\bCOM\b'], [0, r'.*((CE$)|(PE$))']],
        'commodity_options': [[4, r'\bCOM\b'], [0, r'.*(FUT$)']],
        'crypto_spot': [None, ''],
        'crypto_futures':  [None, ''],
        'crypto_options':  [None, ''],
    }""")
options_rule = CheckRule('options_type', """
{
    'calls': [None, ''],
    'puts': [None, ''],
}""")
th = TradeHandler('D:\\Users\\saifk\\Documents\\Sahal\\Ink Signature Designs\\artists\\ATT00001 Sahal Mohamed\\works\\Tradotics\\libs\\tradebook-TP6870-EQ (7) (1).csv')
th.addRule(fields_rule)
th.addRule(assets_rule)
th.addRule(options_rule)
trades = th.convert()
df = pd.DataFrame(trades)
symbols = df['symbol'].drop_duplicates()
tradeOutputs = []
for symbol in symbols:
    sdf = df.loc[df['symbol'] == symbol]
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
            breakpoint+=1
            sum_sell_price += trade['quantity']*trade['price']
            n_sell_trades += trade['quantity']
            quantity -= trade['quantity']
            buy_quantity += trade['quantity']
        elif trade['trade_type'] == 'buy':
            breakpoint+=1
            sum_buy_price += trade['quantity']*trade['price']
            n_buy_trades += trade['quantity']
            quantity+=trade['quantity']
            sell_quantity += trade['quantity']
        if quantity == 0:
            trade.drop(['trade_date', 'order_id', 'order_execution_time'])
            trade['entry_date'] = entry_date
            trade['entry_time'] = entry_time
            trade['exit_date'] = trade['trade_date']
            trade['exit_time'] = trade['order_execution_time']
            trade['breakeven_point'] = breakpoint
            trade['trade_type'] = trade_type
            trade['avg_buy_price'] = sum_buy_price/n_buy_trades
            trade['avg_sell_price'] = sum_sell_price/n_sell_trades
            trade['quantity'] = max(buy_quantity, sell_quantity)
            sum_buy_price = 0
            n_buy_trades = 0
            sum_sell_price = 0
            n_sell_trades = 0
            breakpoint = 0
            buy_quantity =0
            sell_quantity =0

            tradeOutputs.append(trade)

todf = pd.DataFrame(tradeOutputs)
todf.to_csv('test.csv', index = False)

print(len(todf))

# Symbol enter_date	Breakeven Point	Exchange	Segment	Entry time	Exit time	Trade Type	Avg Buy Price	Avg Sell Price	Quantity	Order ID

# symbol, , exchange,segment,trade_type,quantity,price,order_id,order_execution_time,strike_price,expiry_date,options_type,assets_type


    