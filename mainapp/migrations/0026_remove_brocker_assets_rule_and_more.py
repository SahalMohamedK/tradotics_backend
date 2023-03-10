# Generated by Django 4.1.4 on 2023-01-30 23:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mainapp', '0025_rename_trade_tradehistory'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='brocker',
            name='assets_rule',
        ),
        migrations.RemoveField(
            model_name='brocker',
            name='fields_rule',
        ),
        migrations.RemoveField(
            model_name='brocker',
            name='options_rule',
        ),
        migrations.AddField(
            model_name='brocker',
            name='rules',
            field=models.TextField(default="{\n    'symbol':{\n        'type': 'field',\n        'col': 0,\n        'regex': r'(?P<value>.*)'\n    },\n    'tradeDate': {\n        'type': 'field',\n        'col': 2,\n        'regex': r'(?P<value>.*)'\n    },\n    'exchange': {\n        'type': 'field',\n        'col': 3,\n        'regex': r'(?P<value>.*)'\n    },\n    'segment': {\n        'type': 'field',\n        'col': 4,\n        'regex': r'(?P<value>.*)'\n    },\n    'quantity': {\n        'type': 'field',\n        'col': 8,\n        'regex': r'(?P<value>.*)'\n    },\n    'price': {\n        'type': 'field',\n        'col': 9,\n        'regex': r'(?P<value>.*)'\n    },\n    'orderId':{\n        'type': 'field',\n        'col': 11,\n        'regex': r'(?P<value>.*)',\n    },\n    'executionTime': {\n        'type': 'field',\n        'col': 12,\n        'regex': r'.*(?P<value>\\d\\d:\\d\\d:\\d\\d)$'\n    },\n    'optionsType': {\n        'type': 'check',\n        'values': {\n            0: [\n                {\n                    'col': 0,\n                    'regex': '.*\\d(PE)$'\n                }\n            ],\n            1: [\n                {\n                    'col': 0,\n                    'regex': '.*\\d(CE)$'\n                }\n            ]\n        }\n    },\n    'tradeType': {\n        'type': 'check',\n        'values': {\n            0: [\n                {\n                    'col': 6,\n                    'regex': r'^(sell)$'\n                }\n            ],\n            1: [\n                {\n                    'col': 6,\n                    'regex': r'^(buy)$'\n                }\n            ]\n        }\n    },\n    'assetType': {\n        'type': 'check',\n        'values': {\n            1: [\n                {\n                    'col': 4,\n                    'regex': r'\x08EQ\x08'\n                }\n            ],\n            2: [\n                {\n                    'col': 4,\n                    'regex': r'\x08FO\x08'\n                },\n                {\n                    'col': 0, \n                    'regex': r'.*((CE$)|(PE$))'\n                }\n            ],\n            3: [\n                {\n                    'col': 4,\n                    'regex': r'\x08FO\x08'\n                },\n                {\n                    'col': 0, \n                    'regex': r'.*(FUT$)'\n                }\n            ],\n            4: [\n                {\n                    'col': 4,\n                    'regex': r'\x08CDS\x08'\n                },\n                {\n                    'col':0, \n                    'regex': r'.*((CE$)|(PE$))'\n                }\n            ],\n            5: [\n                {\n                    'col': 4,\n                    'regex': r'\x08CDS\x08'\n                },\n                {\n                    'col': 0, \n                    'regex': r'.*(FUT$)'\n                }\n            ],\n            6: [\n                {\n                    'col': 4,\n                    'regex': r'\x08COM\x08'\n                },\n                {\n                    'col': 0, \n                    'regex': r'.*((CE$)|(PE$))'\n                }\n            ],\n            '7': [\n                {\n                    'col': 4,\n                    'regex': r'\x08COM\x08'\n                },\n                {\n                    'col': 0, \n                    'regex': r'.*(FUT$)'\n                }\n            ],\n        }\n    }\n}"),
        ),
    ]
