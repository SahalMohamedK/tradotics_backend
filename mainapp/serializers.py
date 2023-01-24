from rest_framework import serializers
import os
from .models import Brocker, Trade
from django.core.validators import FileExtensionValidator
from .consts import SUPPORTED_FILE_TYPES, PNL_STATUS, TRADE_TYPE


class UploadTradesSerializer(serializers.Serializer):
    file = serializers.FileField(validators=[FileExtensionValidator(allowed_extensions=SUPPORTED_FILE_TYPES)])
    brocker = serializers.IntegerField()


class FilterSerializer(serializers.Serializer):
    symbols = serializers.ListField(child = serializers.CharField(), default=[], required = False)
    start = serializers.IntegerField(default=0, required=False)
    limit = serializers.IntegerField(default = 25, required = False)

class OutputTradesSerializer(serializers.Serializer):
    symbol = serializers.CharField()
    breakeven_point = serializers.IntegerField()
    exchange = serializers.CharField()
    segment = serializers.CharField()
    entry_date = serializers.DateField()
    entry_time = serializers.TimeField()
    exit_date = serializers.DateField()
    exit_time = serializers.TimeField()
    trade_type = serializers.CharField()
    avg_buy_price = serializers.DecimalField(max_digits=30, decimal_places=15)
    avg_sell_price = serializers.DecimalField(max_digits=30, decimal_places=15)
    quantity = serializers.IntegerField()
    order_id = serializers.CharField()
    net_pnl = serializers.DecimalField(max_digits=30, decimal_places=15)
    roi = serializers.DecimalField(max_digits=30, decimal_places=5)
    status = serializers.IntegerField()

    # def pnl(self):
    #     if self.trade_type == TRADE_TYPE.BUY:
    #         return round((self.avg_sell_price - self.avg_buy_price) * self.quantity, 4)
    #     else:
    #         return round((self.avg_buy_price - self.avg_sell_price) * self.quantity, 4)

    # def get_pnl_status(self):
    #     if self.pnl > 0:
    #         return PNL_STATUS.WIN
    #     elif self.pnl < 0:
    #         return PNL_STATUS.LOSS
    #     return PNL_STATUS.BREAKEVEN

    # def duration(self):
    #     delta = datetime.combine(
    #         date.today(), self.exit_time) - datetime.combine(date.today(), self.entry_time)
    #     return delta
    
    # def roi(self):
    #     if self.trade_type == TRADE_TYPE.BUY:
    #         return round((self.avg_sell_price - self.avg_buy_price) / self.avg_buy_price, 4)
    #     return round((self.avg_buy_price - self.avg_sell_price) / self.avg_sell_price, 4)

    # def planned_rr(self):
    #     if self.trade_type == TRADE_TYPE.BUY:
    #         return round((self.target - self.avg_sell_price) / (self.avg_sell_price - self.stoploss), 4)
    #     return round((self.target - self.avg_sell_price) / (self.avg_sell_price - self.stoploss), 4)

    # def realised_rr(self):
    #     if self.trade_type == TRADE_TYPE.BUY:
    #         return round((self.avg_sell_price - self.avg_buy_price) / (self.avg_buy_price - self.stoploss), 4)
    #     return round((self.avg_buy_price - self.avg_sell_price) / (self.avg_sell_price - self.stoploss), 4)
    
    # def risk(self):
    #     if self.trade_type == TRADE_TYPE.BUY:
    #         return round((self.avg_buy_price - self.stoploss) * self.quantity, 4)
    #     return round((self.stoploss - self.avg_sell_price) * self.quantity, 4)
    
    # def charges(self):
    #     return round(self.pnl / 10, 4)

    # def gross_pnl(self):
    #     return self.pnl - self.charges

    # def cost(self):
    #     if self.trade_type == TRADE_TYPE.BUY:
    #         return self.avg_buy_price * self.quantity
    #     return self.avg_sell_price * self.quantity

    # def profit_distance(self):
    #     if self.trade_type == TRADE_TYPE.BUY:
    #         return (self.target - self.avg_buy_price) / self.avg_buy_price
    #     return (self.avg_sell_price - self.target) / self.avg_sell_price

    # def stop_distance(self):
    #     if self.trade_type == TRADE_TYPE.BUY:
    #         return round((self.avg_buy_price - self.stoploss) / self.avg_buy_price, 4)
    #     return round((self.stoploss - self.avg_sell_price) / self.avg_sell_price, 4)

    # def acc_balance(self):
    #     return self.gross_pnl



# class TradesSerializer(serializers.ModelSerializer):
#     pnl_status = serializers.SerializerMethodField()

#     class Meta:
#         model = Trade
#         fields = (
#             'id', 'user', 'symbol', 'date', 'breakeven_point', 'exchange', 'segment', 'entry_time', 'exit_time', 'trade_type',
#             'quantity', 'orders', 'target', 'stoploss', 'avg_sell_price', 'avg_buy_price', 'pnl', 'pnl_status', 'duration',
#             'roi', 'planned_rr', 'realised_rr', 'risk', 'charges', 'gross_pnl', 'cost', 'profit_distance', 'stop_distance', 'acc_balance',
#         )

#     def get_pnl_status(self, trade):
#         return trade.pnl_status

class BrockerNamesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brocker
        fields = ['name', 'pk']

class BrockerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brocker
        fields = ['name', 'desc']