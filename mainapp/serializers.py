from rest_framework import serializers
import os
from .models import Brocker, ImportTrade, Trade

class ImportTradesSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImportTrade
        fields = ['file', 'brocker']
    
    def save(self, **kwargs):
        kwargs['user'] = self.context['request'].user
        file = self.context['request'].FILES['file']
        ext = os.path.splitext(file.name)[-1]
        if ext != '.csv':
            raise serializers.ValidationError({"message": "Only csv files are allowed"})
        super().save(**kwargs)
        return self.instance

class TradesSerializer(serializers.ModelSerializer):
    pnl_status = serializers.SerializerMethodField()

    class Meta:
        model = Trade
        fields = (
            'id', 'user', 'symbol', 'date', 'breakeven_point', 'exchange', 'segment', 'entry_time', 'exit_time', 'trade_type',
            'quantity', 'orders', 'target', 'stoploss', 'avg_sell_price', 'avg_buy_price', 'pnl', 'pnl_status', 'duration',
            'roi', 'planned_rr', 'realised_rr', 'risk', 'charges', 'gross_pnl', 'cost', 'profit_distance', 'stop_distance', 'acc_balance',
        )

    def get_pnl_status(self, trade):
        return trade.pnl_status

class BrockerNamesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brocker
        fields = ['name', 'pk']

class BrockerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brocker
        fields = ['name', 'desc']