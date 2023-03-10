"""
    Ink Signature Designs

    Artist: Sahal Mohamed 

    Copyright (c) 2022-2023 by Ink Signature Designs.  All rights reserved.

    This module contains the all the default fields that can be given in the layout for the Trades serializer
"""

import datetime
from mainapp.consts import STATUS, TRADE_TYPE, ASSETS_TYPE
from .utils import human_delta, safe_devide
import math

class Field:
    include_open_trades = False
    def __init__(self, name = ''):
        self.name = name if name else self.__class__.__name__

    def init(self, trades):
        self.data = None

    def get(self, trade):
        pass

    def convert(self, data, trades):
        pass

class isDemo(Field):
    def init(self, trades):
        self.data = False
    
    def convert(self, data, trades):
        self.data = trades.is_demo

class symbols(Field):
    def init(self, trades):
        self.data = []

    def get(self, trade):
        symbol = trade['symbol']
        if not symbol in self.data:
            self.data.append(symbol)

class cumulativePnl(Field):
    def init(self, trades):
        self.data = {}
    
    def get(self, trade):
        date = trade['entryDate']
        if date in self.data:
            self.data[date] += trade['netPnl']
        else:
            self.data[date] = trade['netPnl']
        
    def convert(self, *args):    
        labels = list(self.data.keys())
        labels.sort(key = lambda i: datetime.datetime.strptime(i, '%Y-%m-%d'))
        cumulative_pnls = []
        sum_pnl = 0
        for date in labels:
            sum_pnl += self.data[date]
            cumulative_pnls.append(sum_pnl)
        self.data = [labels ,cumulative_pnls]

class totalPnl(Field):
    def init(self, trades):
        self.data = 0
    
    def get(self, trade):
        self.data += trade['netPnl']

class totalQuantity(Field):
    def init(self, trades):
        self.data = 0
    
    def get(self, trade):
        self.data += trade['quantity']

class totalDates(Field):
    def init(self, trades):
        self.data = 0
        self.dates = []

    def get(self, trade):
        date = trade['entryDate']
        if date not in self.dates:
            self.dates.append(date)
    
    def convert(self, *args):
        self.data = len(self.dates)

class counts(Field):
    def init(self, trades):
        # ['total', 'winners', 'lossers', 'long', 'short']
        self.data = [0, 0, 0, 0, 0]

    def get(self, trade):
        self.data[0] += 1
        if trade['status'] == STATUS.WIN:
            self.data[1] += 1
        elif trade['status'] == STATUS.LOSS:
            self.data[2] += 1
            
        if trade['tradeType'] == TRADE_TYPE.Repr.BUY:
            self.data[3] += 1
        else:
            self.data[4] += 1

class countsByDay(Field):
    def init(self, trades):
        # [winners, lossers]
        self.data = [0, 0]
        self.pnl_by_dates ={}
    
    def get(self, trade):
        date = trade['entryDate']
        if date in self.pnl_by_dates:
            self.pnl_by_dates[date] += trade['netPnl']
        else:
            self.pnl_by_dates[date] = trade['netPnl']

    def convert(self, *args):
        for date in self.pnl_by_dates:
            if self.pnl_by_dates[date]>0:
                self.data[0] += 1
            else:
                self.data[1] += 1
                
class countsByRoi(Field):
    def init(self, trades):
        # [ 'total', 'winners', 'lossers', 'long', 'short' ]
        self.data = [ 0, 0, 0, 0, 0 ]
    
    def get(self, trade):
        if trade['status'] == STATUS.WIN:
            self.data[1] += trade['roi']
        elif trade['status'] == STATUS.LOSS:
            self.data[2] += trade['roi']
        
        if trade['tradeType'] == TRADE_TYPE.Repr.BUY:
            self.data[3] += trade['roi']
        else:
            self.data[4] += trade['roi']
        self.data[0]+= trade['roi']

class profitFactor(Field):
    def init(self, trades):
        self.wins = 0
        self.loss = 0
        self.data = 0
    
    def get(self, trade):
        pnl = trade['netPnl']
        if pnl > 0:
            self.wins += pnl
        else:
            self.loss -= pnl
    
    def convert(self, *args):
        self.data = round(safe_devide(self.wins, self.loss), 2)

class pnlByStatus(Field):
    def init(self, trades):
        # ['winners', 'lossers]
        self.data = [0, 0]

    def get(self, trade):
        if trade['status'] == STATUS.WIN:
            self.data[0] += trade['netPnl']
        elif trade['status'] == STATUS.LOSS:
            self.data[1] += trade['netPnl']

class pnlByDates(Field):
    def init(self, trades):
        self.data = {}
    
    def get(self, trade):
        date = trade['entryDate']
        if date in self.data:
            self.data[date] = [self.data[date][0]+trade['netPnl'], self.data[date][1]+1]
        else:
            self.data[date] = [trade['netPnl'], 1]

class pnlByTradeTypes(Field):
    def init(self, trades):
        # ['longs', 'shorts']
        self.data = [0, 0]

    def get(self, trade):
        if trade['tradeType'] == TRADE_TYPE.Repr.BUY:
            self.data[0] += trade['netPnl']
        elif trade['tradeType'] == TRADE_TYPE.Repr.SELL:
            self.data[1] += trade['netPnl']

class pnlByDays(Field):
    def init(self, trades):
        # [ days in order ]
        self.data = [0, 0, 0, 0, 0, 0, 0]

    def get(self, trade):
        d = datetime.datetime.strptime(trade['entryDate'], '%Y-%m-%d')
        self.data[(d.weekday()+1)%7] += trade['netPnl']

class pnlByMonths(Field):
    def init(self, trades):
        # [ months in order]
        self.data = [0 for _ in range(12)]

    def get(self, trade):
        d = datetime.datetime.strptime(trade['entryDate'], '%Y-%m-%d')
        self.data[d.month-1] += trade['netPnl']

class pnlBySetup(Field):
    def init(self, trades):
        # [ 'labels', 'values' ]
        self.data = [[], []]
        self.pnl_by_setup = {}

    def get(self, trade):
        setups = trade['setup']
        for setup in setups:
            if setup in self.pnl_by_setup:
                self.pnl_by_setup[setup] += trade['netPnl']
            else:
                self.pnl_by_setup[setup] = trade['netPnl']
    
    def convert(self, *args):
        self.data = [list(self.pnl_by_setup.keys()), list(self.pnl_by_setup.values())]

class pnlByMistakes(Field):
    def init(self, trades):
        # [ 'labels', 'values' ]
        self.data = [[], []]
        self.pnl_by_mistakes = {}

    def get(self, trade):
        mistakes = trade['mistakes']
        for mistake in mistakes:
            if mistake in self.pnl_by_mistakes:
                self.pnl_by_mistakes[mistake] += trade['netPnl']
            else:
                self.pnl_by_mistakes[mistake] = trade['netPnl']
    
    def convert(self, *args):
        self.data = [list(self.pnl_by_mistakes.keys()), list(self.pnl_by_mistakes.values())]

class pnlByTags(Field):
    def init(self, trades):
        # [ 'labels', 'values' ]
        self.data = [[], []]
        self.pnl_by_tags = {}

    def get(self, trade):
        tags = trade['tags']
        for tag in tags:
            if tag in self.pnl_by_tags:
                self.pnl_by_tags[tag] += trade['netPnl']
            else:
                self.pnl_by_tags[tag] = trade['netPnl']
    
    def convert(self, *args):
        self.data = [list(self.pnl_by_tags.keys()), list(self.pnl_by_tags.values())]

class pnlByDuration(Field):
    def init(self, trades):
        # [ durations in order ]
        self.data = [0, 0, 0, 0, 0]
    
    def get(self, trade):
        def dur_min(n):
            return datetime.timedelta(seconds = n*60)

        entryDate = trade['entryDate']
        entryTime = trade['entryTime']
        exitDate = trade['exitDate']
        exitTime = trade['exitTime']
        pnl = trade['netPnl']

        startTime = datetime.datetime.strptime(f'{entryDate} {entryTime}', '%Y-%m-%d %H:%M:%S')
        endTime = datetime.datetime.strptime(f'{exitDate} {exitTime}', '%Y-%m-%d %H:%M:%S')
        dur = endTime-startTime
        
        if dur >= dur_min(1) and dur <= dur_min(5):
            self.data[0] += pnl
        elif dur > dur_min(5) and dur <= dur_min(10):
            self.data[1] += pnl
        elif dur > dur_min(10) and dur <= dur_min(20):
            self.data[2] += pnl
        elif dur > dur_min(20) and dur <= dur_min(40):
            self.data[3] += pnl
        elif dur > dur_min(40):
            self.data[4] += pnl

class pnlByHours(Field):
    def init(self, trades):
        # [ 'labels', 'hours' ]
        self.data = [
            ['12am - 1am', '1am - 2am', '2am - 3am', '3am - 4am', '4am - 5am', '5am - 6am', '6am - 7am', '7am - 8am', '8am - 9am',
            '9am - 10am', '10am - 11am', '11am - 12pm', '12pm - 1pm', '1pm - 2pm', '2pm - 3pm', '3pm - 4pm', '4pm - 5pm', '5pm - 6pm', '6pm - 7pm', '7pm - 8pm', '8pm - 9pm',
            '9pm - 10pm', '10pm - 11pm', '11pm - 12am'], 
            [0 for _ in range(24)]
        ]

    def get(self ,trade):
        time = trade['entryTime']
        t = datetime.datetime.strptime(time, '%H:%M:%S')
        self.data[1][t.hour] += trade['netPnl']

    def convert(self, *args):
        pnls = []
        labels = []
        for i, pnl in enumerate(self.data[1]):
            if pnl != 0:
                labels.append(self.data[0][i])
                pnls.append(self.data[1][i])
        self.data = [labels, pnls]

class dateWise(pnlByDates):
    def convert(self, *args):
        # ['total', 'winners', 'lossers', 'consecWin', 'consecLoss']
        data = [0, 0, 0, 0, 0]
        curDay = None
        consec = 1
        for day in self.data:
            net_pnl = self.data[day][0]
            if day != curDay:
                if net_pnl>0:
                    if data[3] < consec:
                        data[3] = consec
                elif net_pnl<0:
                    if data[4] < consec:
                        data[4] = consec
                consec = 1
            else:
                consec += 1
            if net_pnl>0:
                data[1] += 1
            elif net_pnl<0:
                data[2] += 1
            data[0] += 1
            curDay = day
        self.data = data

class maxConsec(Field):
    def init(self, trades):
        # [ 'winners', 'lossers' ]
        self.data = [0, 0]
        self.wins = 0
        self.loss = 0
        self.consec_wins = []
        self.consec_loss = []

    def get(self, trade):
        if trade['status'] == STATUS.WIN:
            self.wins += 1
        else:
            if self.wins:
                self.consec_wins.append(self.wins)
            self.wins = 0

        if trade['status'] == STATUS.LOSS:
            self.loss += 1
        else:
            if self.loss:
                self.consec_loss.append(self.loss)
            self.loss = 0
    
    def convert(self, *args):
        if self.wins:
            self.consec_wins.append(self.wins)

        if self.loss:
            self.consec_loss.append(self.loss)

        if self.consec_wins:
            self.data[0] = max(self.consec_wins)
        else:
            self.data[0] = 0
        if self.consec_loss:
            self.data[1] = max(self.consec_loss)
        else:
            self.data[1] = 0

class openAndClose(Field):
    include_open_trades = True
    def init(self, trades):
        # [ 'opened', 'closed' ]
        self.data = [0, 0]
    
    def get(self, trade):
        if trade['isOpen']:
            self.data[0] += 1
        else:
            self.data[1] += 1

class dialyPnl(Field):
    def init(self, trades):
        # [ 'labels', 'value' ]
        self.data = [ [], [] ]
        self.pnl_by_dates = {}
    
    def get(self, trade):
        date = trade['entryDate']
        if date in self.data:
            self.pnl_by_dates[date] += trade['netPnl']
        else:
            self.pnl_by_dates[date] = trade['netPnl']
        
    def convert(self, *args):
        self.data = [list(self.pnl_by_dates.keys()), list(self.pnl_by_dates.values())]

class highestPnlTrade(Field):
    def init(self, trades):
        # trade
        self.data = {'entryDate': "2022-01-01", 'entryPrice': 0, 'entryTime': "10:10:10", 'exitDate': "2022-01-01", 
            'exitPrice': 0, 'exitTime': "10:10:10", 'netPnl': 0 , 'quantity': 0, 'roi': 0,
            'status': 0, 'symbol': "N/A", 'tradeType': "1", 'id':'N/A'}
    
    def get(self, trade):
        if self.data['netPnl'] < trade['netPnl']:
            self.data = trade

class lowestPnlTrade(Field):
    # trade
    def init(self, trades):
        self.data = {'entryDate': "2022-01-01", 'entryPrice': 0, 'entryTime': "10:10:10", 'exitDate': "2022-01-01", 
        'exitPrice': 0, 'exitTime': "10:10:10", 'netPnl': 100**10 , 'quantity': 0, 'roi': 0,
        'status': 0, 'symbol': "N/A", 'tradeType': "1", 'id':'N/A'}
    
    def get(self, trade):
        if self.data['netPnl'] > trade['netPnl']:
            self.data = trade

class holdTimes(Field):
    def init(self, trades):
        # [ 'avg hold_time', 'avg winners_hold_time', 'avg lossers_hold_time', 'avg long_hold_time', 'avg short_hold_time', 'highest_hold_tile' ]
        self.data = [ 0, 0, 0, 0, 0, 0 ]
        self.sum_hold_time = datetime.timedelta(0)
        self.sum_winners_hold_time = datetime.timedelta(0)
        self.sum_lossers_hold_time = datetime.timedelta(0)
        self.sum_long_hold_time = datetime.timedelta(0)
        self.sum_short_hold_time = datetime.timedelta(0)
        self.highest_hold_tile = datetime.timedelta(0)
        self.pnl = 0
        self.n = 0
    
    def get(self, trade):
        self.n+=1
        entryDate = trade['entryDate']
        entryTime = trade['entryTime']
        exitDate = trade['exitDate']
        exitTime = trade['exitTime']
        startTime = datetime.datetime.strptime(f'{entryDate} {entryTime}', '%Y-%m-%d %H:%M:%S')
        endTime = datetime.datetime.strptime(f'{exitDate} {exitTime}', '%Y-%m-%d %H:%M:%S')
        dur = endTime-startTime
        if self.pnl<trade['netPnl']:
            self.highest_hold_tile = dur
            self.pnl = trade['netPnl']

        self.sum_hold_time += dur
        if trade['status'] == STATUS.WIN:
            self.sum_winners_hold_time += dur
        elif trade['status'] == STATUS.LOSS:
            self.sum_lossers_hold_time += dur

        if trade['tradeType'] == TRADE_TYPE.Repr.BUY:
            self.sum_long_hold_time += dur
        else:
            self.sum_short_hold_time += dur
        
    def convert(self, *args):
        self.data = [
            human_delta(safe_devide(self.sum_hold_time, self.n)),
            human_delta(safe_devide(self.sum_winners_hold_time, self.n)),
            human_delta(safe_devide(self.sum_lossers_hold_time, self.n)),
            human_delta(safe_devide(self.sum_long_hold_time, self.n)),
            human_delta(safe_devide(self.sum_short_hold_time, self.n)),
            human_delta(self.highest_hold_tile),
            ]

class dataByExpiryDate(Field):
    def init(self, trades):
        self.labels = ['Same day', '1 day', '2 day', '3 day', '4 day', '5 day', '6 day', '6 to 30 days', '30+ days']
        self.trades = [0 for _ in range(len(self.labels))]
        self.pnls = [0 for _ in range(len(self.labels))]
        self.costs = [0 for _ in range(len(self.labels))]
        self.winrates = [[0, 0] for _ in range(len(self.labels))]
    
    def get(self, trade):
        date_to_expiry = trade['daysToExpiry']
        if date_to_expiry in self.labels:
            self.trades[self.labels.index(date_to_expiry)] += 1
            self.pnls[self.labels.index(date_to_expiry)] += trade['netPnl']
            self.costs[self.labels.index(date_to_expiry)] += trade['entryPrice']*trade['quantity']
            i = date_to_expiry
            if i>6 and i<=30:
                i = 7
            elif i>30:
                i = 8
            if i>=0:
                if trade['netPnl'] > 0:
                    self.winrates[i][0] += 1
                else:
                    self.winrates[i][1] += 1
    
    def convert(self ,*args):
        self.data = [self.labels, self.pnls, self.trades, self.costs, self.winrates] 

class dataByDates(Field):
    def __init__(self, start, size, name = ''):
        super().__init__(name)
        self.start = start
        self.size = size
        self.cur = 0

    def init(self, trades):
        # [ [ ['cumulativePnl by hours'], 'total', 'winners', 'lossers', 'volume', 'profit factor'] ]
        self.data = []
        self.data_by_dates = {}
    
    def get(self, trade):
        date = trade['entryDate']
        pnl = trade['netPnl']
        isWin = pnl > 0
        isLoss = pnl < 0

        if date in self.data_by_dates:
            self.data_by_dates[date][0][1].append(self.data_by_dates[date][0][1][-1]+pnl)
            self.data_by_dates[date][0][0].append(trade['entryTime'])
            self.data_by_dates[date][1] += 1
            if isWin:
                self.data_by_dates[date][2] += 1 
                self.data_by_dates[date][5][0] += pnl
            if isLoss:
                self.data_by_dates[date][3] += 1
                self.data_by_dates[date][5][1] += pnl
            self.data_by_dates[date][4] += trade['quantity']
            self.data_by_dates[date][6].append(trade)
            
        else:
            self.data_by_dates[date] = [
                [
                    [trade['entryTime']],
                    [pnl]
                ],
                1,
                1 if isWin else 0,
                1 if isLoss else 0,
                trade['quantity'],
                [
                    pnl if isWin else 0,
                    pnl if isLoss else 0
                ],
                [trade]
            ]

    def convert(self, *args):
        for date in self.data_by_dates:
            if self.cur >= self.start and self.cur < self.start+self.size:
                self.data_by_dates[date][5] = round((self.data_by_dates[date][5][0]/self.data_by_dates[date][5][1]) if self.data_by_dates[date][5][1] else 0, 2)
                self.data.append([date, self.data_by_dates[date]])
            self.cur += 1

class dayDistribution(Field):
    def init(self, trades):
        self.data = []
        self.trades = [0, 0, 0, 0, 0, 0, 0]
        self.pnls = [0, 0, 0, 0, 0, 0, 0]
        self.costs = [0, 0, 0, 0, 0, 0, 0]
        self.winrates = [[0,0] for _ in range(7)]
    
    def get(self, trade):
        date = trade['entryDate']
        d = datetime.datetime.strptime(date, '%Y-%m-%d')
        self.pnls[(d.weekday()+1)%7] += trade['netPnl']
        self.trades[(d.weekday()+1)%7] += 1
        self.costs[(d.weekday()+1)%7] += trade['entryPrice']*trade['quantity']
        if trade['netPnl'] > 0:
            self.winrates[(d.weekday()+1)%7][0] += 1
        else:
            self.winrates[(d.weekday()+1)%7][1] += 1
    
    def convert(self, *args):
        self.data = [self.pnls, self.trades, self.costs, self.winrates]

class hourDistribution(Field):
    def init(self, trades):
        self.data = []
        self.trades = [0 for _ in range(24)]
        self.pnls = [0 for _ in range(24)]
        self.costs = [0 for _ in range(24)]
        self.labels = ['12am - 1am', '1am - 2am', '2am - 3am', '3am - 4am', '4am - 5am', '5am - 6am', '6am - 7am', '7am - 8am', '8am - 9am',
            '9am - 10am', '10am - 11am', '11am - 12pm', '12pm - 1pm', '1pm - 2pm', '2pm - 3pm', '3pm - 4pm', '4pm - 5pm', '5pm - 6pm', '6pm - 7pm', '7pm - 8pm', '8pm - 9pm',
            '9pm - 10pm', '10pm - 11pm', '11pm - 12am']
        self.winrates = [[0,0] for _ in range(24)]

    def get(self, trade):
        time = trade['entryTime']
        t = datetime.datetime.strptime(time, '%H:%M:%S')
        self.pnls[t.hour] += trade['netPnl']
        self.trades[t.hour] += 1
        self.costs[t.hour] += trade['entryPrice']*trade['quantity']
        if trade['netPnl'] > 0:
            self.winrates[t.hour][0] += 1
        else:
            self.winrates[t.hour][1] += 1
        

    def convert(self, *args):
        labels = [] 
        pnls = [] 
        trades = [] 
        costs = [] 
        winrates =[]

        for i, trade in enumerate(self.trades):
            if trade > 0:
                labels.append(self.labels[i])
                pnls.append(self.pnls[i])
                trades.append(self.trades[i])
                costs.append(self.costs[i])
                winrates.append(self.winrates[i])

        self.data = [labels, pnls, trades, costs, winrates]
                
class monthDistribution(Field):
    def init(self, trades):
        self.trades = [0 for _ in range(12)]
        self.pnls = [0 for _ in range(12)]
        self.costs = [0 for _ in range(12)]
        self.winrates = [[0,0] for _ in range(12)]
        self.data = []
    
    def get(self, trade):
        date = trade['entryDate']
        d = datetime.datetime.strptime(date, '%Y-%m-%d')
        self.pnls[d.month-1] += trade['netPnl']
        self.trades[d.month-1] += 1
        self.costs[d.month-1] += trade['entryPrice']*trade['quantity']
        if trade['netPnl'] > 0:
            self.winrates[d.month-1][0] += 1
        else:
            self.winrates[d.month-1][1] += 1


    def convert(self, *args):
        self.data = [self.pnls, self.trades, self.costs, self.winrates]

class setupDistribution(Field):
    def init(self, trades):
        self.data = []
        self.labels = []
        self.pnls = []
        self.trades = []
        self.costs = []
        self.winrates = []

    def get(self, trade):
        setup = trade['setup']
        if setup:
            if setup in self.labels:
                self.pnls[self.labels.index(setup)] += trade['netPnl']
                self.trades[self.labels.index(setup)] += 1
                self.costs[self.labels.index(setup)] += trade['entryPrice']*trade['quantity']
                if trade['netPnl'] > 0:
                    self.winrates[self.labels.index(setup)][0] += 1
                else:
                    self.winrates[self.labels.index(setup)][1] += 1
            else:
                self.labels.append(setup)
                self.pnls.append(trade['netPnl'])
                self.trades.append(1)
                self.costs.append(trade['entryPrice']*trade['quantity'])
                if trade['netPnl'] > 0:
                    self.winrates.append([1,0])
                else:
                    self.winrates.append([0,1])

    def convert(self, *args):
        self.data = [self.labels, self.pnls, self.trades, self.costs, self.winrates]

class tagsDistribution(Field):
    def init(self, trades):
        self.data = []
        self.labels = []
        self.pnls = []
        self.trades = []
        self.costs = []
        self.winrates = []

    def get(self, trade):
        tags = trade['tags']
        for tag in tags:
            if tag:
                if tag in self.labels:
                    self.pnls[self.labels.index(tag)] += trade['netPnl']
                    self.trades[self.labels.index(tag)] += 1
                    self.costs[self.labels.index(tag)] += trade['entryPrice']*trade['quantity']
                    if trade['netPnl'] > 0:
                        self.winrates[self.labels.index(tag)][0] += 1
                    else:
                        self.winrates[self.labels.index(tag)][1] += 1
                else:
                    self.labels.append(tag)
                    self.pnls.append(trade['netPnl'])
                    self.trades.append(1)
                    self.costs.append(trade['entryPrice']*trade['quantity'])
                    if trade['netPnl'] > 0:
                        self.winrates.append([1,0])
                    else:
                        self.winrates.append([0,1])

    def convert(self, *args):
        self.data = [self.labels, self.pnls, self.trades, self.costs, self.winrates]

class mistakesDistribution(Field):
    def init(self, trades):
        self.data = []
        self.labels = []
        self.pnls = []
        self.trades = []
        self.costs = []
        self.winrates = []

    def get(self, trade):
        mistakes = trade['mistakes']
        for mistake in mistakes:
            if mistake:
                if mistake in self.labels:
                    self.pnls[self.labels.index(mistake)] += trade['netPnl']
                    self.trades[self.labels.index(mistake)] += 1
                    self.costs[self.labels.index(mistake)] += trade['entryPrice']*trade['quantity']
                    if trade['netPnl'] > 0:
                        self.winrates[self.labels.index(mistake)][0] += 1
                    else:
                        self.winrates[self.labels.index(mistake)][1] += 1
                else:
                    self.labels.append(mistake)
                    self.pnls.append(trade['netPnl'])
                    self.trades.append(1)
                    self.costs.append(trade['entryPrice']*trade['quantity'])
                    if trade['netPnl'] > 0:
                        self.winrates.append([1,0])
                    else:
                        self.winrates.append([0,1])

    def convert(self, *args):
        self.data = [self.labels, self.pnls, self.trades, self.costs, self.winrates]

class durationDistribution(Field):
    def init(self, trades):
        self.data = []
        self.pnls = [0, 0, 0, 0, 0]
        self.trades = [0, 0, 0, 0, 0]
        self.costs = [0, 0, 0, 0, 0]
        self.winrates = [[0,0] for _ in range(5)]

    def get(self, trade):
        
        def dur_min(n):
            return datetime.timedelta(seconds = n*60)

        entryDate = trade['entryDate']
        entryTime = trade['entryTime']
        exitDate = trade['exitDate']
        exitTime = trade['exitTime']

        startTime = datetime.datetime.strptime(f'{entryDate} {entryTime}', '%Y-%m-%d %H:%M:%S')
        endTime = datetime.datetime.strptime(f'{exitDate} {exitTime}', '%Y-%m-%d %H:%M:%S')
        dur = endTime-startTime

        n = None
        if dur >= dur_min(1) and dur <= dur_min(5):
            n = 0
        elif dur > dur_min(5) and dur <= dur_min(10):
            n = 1
        elif dur > dur_min(10) and dur <= dur_min(20):
            n = 2
        elif dur > dur_min(20) and dur <= dur_min(40):
            n = 3
        elif dur > dur_min(40):
            n = 4
        
        if n != None:
            self.pnls[n] += trade['netPnl']
            self.trades[n] += 1
            self.costs[n] += trade['entryPrice']*trade['quantity']
            if trade['netPnl'] > 0:
                self.winrates[n][0] += 1
            else:
                self.winrates[n][1] += 1
        

    def convert(self, *args):
        self.data = [self.pnls, self.trades, self.costs, self.winrates]

class costDistribution(Field):
    def init(self, trades):
        self.data = []
        min_cost = 10000**10
        max_cost = 0
        for i, trade in trades.iterrows():
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
        
        self.labels = []
        i = 0
        while i<len(limits)-1:
            self.labels.append(f'${limits[i]} - ${limits[i+1]}')
            i+=1

        self.pnls = [0 for _ in range(len(limits))]
        self.trades = [0 for _ in range(len(limits))]
        self.costs = [0 for _ in range(len(limits))]
        self.winrates = [[0,0] for _ in range(len(limits))]
        self.limits = limits

    def get(self, trade):
        cost = trade['entryPrice']*trade['quantity']
        j = 0
        while j<len(self.limits)-1:
            if self.limits[j]<=cost and cost < self.limits[j+1]:
                self.pnls[j] += trade['netPnl'] 
                self.trades[j] += 1
                self.costs[j] += cost
                if trade['netPnl'] > 0:
                    self.winrates[j][0] += 1
                else:
                    self.winrates[j][1] += 1
                break
            j+=1

    def convert(self, *args):
        self.data = [self.labels, self.pnls, self.trades, self.costs, self.winrates]

class priceDistribution(Field):
    def init(self, trades):
        self.data = []
        min_price = 10000**10
        max_price = 0
        for i, trade in trades.iterrows():
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
        
        self.labels = []
        i = 0
        while i<len(limits)-1:
            self.labels.append(f'${limits[i]} - ${limits[i+1]}')
            i+=1

        self.pnls = [0 for _ in range(len(limits))]
        self.trades = [0 for _ in range(len(limits))]
        self.costs = [0 for _ in range(len(limits))]
        self.winrates = [[0,0] for _ in range(len(limits))]
        self.limits = limits

    def get(self, trade):
        price = trade['entryPrice']
        j = 0
        while j<len(self.limits)-1:
            if self.limits[j]<=price and price < self.limits[j+1]:
                self.pnls[j] += trade['netPnl'] 
                self.trades[j] += 1
                self.costs[j] += price
                if trade['netPnl'] > 0:
                    self.winrates[j][0] += 1
                else:
                    self.winrates[j][1] += 1
                break
            j+=1

    def convert(self, *args):
        self.data = [self.labels, self.pnls, self.trades, self.costs, self.winrates]

class symbolDistribution(Field):
    def init(self, trades):
        self.data = []
        self.labels = trades['symbol'].drop_duplicates().to_list()
        
        self.pnls = [0 for _ in range(len(self.labels))]
        self.trades = [0 for _ in range(len(self.labels))]
        self.costs = [0 for _ in range(len(self.labels))]
        self.winrates = [[0,0] for _ in range(len(self.labels))]

    def get(self, trade):
        j = self.labels.index(trade['symbol'])
        self.pnls[j] += trade['netPnl'] 
        self.trades[j] += 1
        self.costs[j] += trade['entryPrice']*trade['quantity']
        if trade['netPnl'] > 0:
            self.winrates[j][0] += 1
        else:
            self.winrates[j][1] += 1

    def convert(self, *args):
        self.data = [self.labels, self.pnls, self.trades, self.costs, self.winrates]

class trade(Field):
    def __init__(self, id, name=''):
        super().__init__(name)
        self.id = id
    
    def init(self, trades):
        # trade
        self.data = {'entryDate': "2022-01-01", 'entryPrice': 0, 'entryTime': "10:10:10", 'exitDate': "2022-01-01", 
            'exitPrice': 0, 'exitTime': "10:10:10", 'netPnl': 0 , 'quantity': 0, 'roi': 0,
            'status': 0, 'symbol': "N/A", 'tradeType': "1", 'id':'N/A', 'prevTrade': '', 'nextTrade': ''}
        self.i = -1
        self.cur = 0
    
    def get(self, trade):
        self.i += 1
        if trade['id'] == self.id:
            self.data = trade
            self.cur = self.i
    
    def convert(self, data, trades):
        if self.cur > 0:
            self.data['prevTrade'] = trades.trades.loc[self.cur-1]['id']
        
        if self.cur<len(trades.trades)-1:
            self.data['nextTrade'] = trades.trades.loc[self.cur+1]['id']

class trades(Field):
    def __init__(self, start, size):
        super().__init__()
        self.start = start
        self.size = size
    
    def init(self, trades):
        self.cur = 0
        self.data = []
    
    def get(self, trade):
        if self.cur >= self.start and self.cur < self.start+self.size:
            self.data.append(trade)
        self.cur += 1     

class openTrades(Field):
    include_open_trades = True
    def init(self, trades):
        self.data = []

    def get(self, trade):
        if trade['isOpen']:
            self.data.append(trade)

class insights(Field):
    def init(self, trades):
        self.winners = 0
        self.winners_pnl = 0
        self.lossers = 0
        self.lossers_pnl  = 0
        self.total_pnl = 0
        self.counts = 0
        self.hours_per_day = {}
        self.pnl_by_setup = {}
        self.data = []
    
    def get(self, trade):
        self.counts += 1
        self.total_pnl += trade['netPnl']

        # if ASSETS_TYPE.is_options(trade['assetType']):
        #     insights.append('Most of profits are from in the money option strike (70% - $600)')
        
        # date_to_expiry = 'N/A'
        # if trade['expiryDate']:
        #     expiry_date = datetime.datetime.strptime(trade['expiryDate'], '%Y-%m-%d')
        #     entry_date = datetime.datetime.strptime(trade['entryDate'], '%Y-%m-%d')

        #     date_to_expiry = (expiry_date - entry_date).days

        #     if date_to_expiry>=30:
        #         date_to_expiry = '30+ days'
        #     elif date_to_expiry>6:
        #         date_to_expiry = '6 to 30 days'
        #     elif date_to_expiry == 0:
        #         date_to_expiry = 'Same day'
        #     else:
        #         date_to_expiry = f'{date_to_expiry} days'


        # You spend an average of {hours} hours per day for trading
        entryDate = trade['entryDate']
        entryTime = trade['entryTime']
        exitDate = trade['exitDate']
        exitTime = trade['exitTime']

        startTime = datetime.datetime.strptime(f'{entryDate} {entryTime}', '%Y-%m-%d %H:%M:%S')
        endTime = datetime.datetime.strptime(f'{exitDate} {exitTime}', '%Y-%m-%d %H:%M:%S')

        if entryDate in self.hours_per_day:
            if startTime < self.hours_per_day[entryDate][0]:
                self.hours_per_day[entryDate][0] = startTime
            if endTime > self.hours_per_day[entryDate][1]:
                self.hours_per_day[entryDate][1] = endTime
        else:
            self.hours_per_day[entryDate] = [endTime, endTime]    

        # {highst_counted_setup} is the most traded setup generating {percentage}({sum_of_pnl}) of your profits
        setups = trade['setup']
        for setup in setups:
            if setup in self.pnl_by_setup:
                self.pnl_by_setup[setup] = [self.pnl_by_setup[setup][0]+trade['netPnl'], self.pnl_by_setup[setup][1]+1]
            else:
                self.pnl_by_setup[setup] = [trade['netPnl'], 1]

        # Your average losing trades is {avg_lossers} while winning trades are only {avg_winners}
        if trade['status'] == STATUS.WIN:
            self.winners_pnl += trade['netPnl']
            self.winners += 1
        elif trade['status'] == STATUS.LOSS:
            self.lossers_pnl += trade['netPnl']
            self.lossers += 1
    
    def convert(self, *args):
        # You spend an average of {hours} hours per day for trading
        sum_hours_per_day = datetime.timedelta(0)
        for date in self.hours_per_day:
            sum_hours_per_day += (self.hours_per_day[date][1]-self.hours_per_day[date][0])
        self.data.append(f'You spend an average of {human_delta(sum_hours_per_day/self.counts) if self.counts else 0} per day for trading')

        # {highst_counted_setup} is the most traded setup generating {percentage}({sum_of_pnl}) of your profits
        highest_traded_setup = None
        highest_traded_setup_pnl = 0
        highest_traded_setup_count = 0
        highest_profitable_setup = None
        highest_profitable_setup_pnl = -10000**10
        for setup in self.pnl_by_setup:
            if highest_traded_setup_count < self.pnl_by_setup[setup][1]:
                highest_traded_setup_count = self.pnl_by_setup[setup][1]
                highest_traded_setup = setup
                highest_traded_setup_pnl = self.pnl_by_setup[setup][0]

            if highest_profitable_setup_pnl < self.pnl_by_setup[setup][0]:
                highest_profitable_setup_pnl = self.pnl_by_setup[setup][0]
                highest_profitable_setup = setup

        if highest_traded_setup:
            self.data.append(f'{highest_traded_setup} is the most traded setup generating {round((highest_traded_setup_pnl/self.total_pnl) if self.total_pnl else 0, 2)}% (${highest_traded_setup_pnl}) of your profits')
        
        if highest_profitable_setup:
            self.data.append(f'{highest_profitable_setup} is the most profitable setup generating {round((highest_profitable_setup_pnl/self.total_pnl) if self.total_pnl else 0, 2)}% (${highest_profitable_setup_pnl}) of your profits')    

        # Your average losing trades is {avg_lossers} while winning trades are only {avg_winners}
        avg_winners = round(self.winners_pnl/self.winners, 2) if self.winners>0 else 0
        avg_lossers = abs(round(self.lossers_pnl/self.lossers, 2)) if self.lossers>0 else 0
        if avg_lossers > avg_winners:
            self.data.append(f'Your average losing trades is ${avg_lossers} while winning trades are only ${avg_winners}')

#orders
class ordersByTrade(Field):
    def __init__(self, id, name=''):
        super().__init__(name)
        self.id = id

    def init(self, trades):
        self.data = []

    
    def get(self, order):
        if order['tradeId'] == self.id:
            self.data.append(order)         