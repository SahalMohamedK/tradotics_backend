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
        print(len(cTrades))
        for trade in cTrades:
            order_id = trade['order_id']
            if order_id in mTrades:
                mTrades[order_id]['quantity'] = float(mTrades[order_id]['quantity'])+float(trade['quantity'])
            else:
                mTrades[order_id] = trade
        
        print(len(mTrades))
        return mTrades.values()
