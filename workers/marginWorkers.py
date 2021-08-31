import random
from time import sleep
from PyQt5.QtCore import QRunnable


class MarginRunnable(QRunnable):
    def __init__(self, symbol, exchange, obj, operation):
        super().__init__()
        self.symbol = symbol
        self.obj = obj
        self.exchange = exchange
        self.operation = operation

    def run(self):
        if self.operation == 'add':
            self.addmargin()
        else:
            self.reducemargin()
        return

    def addmargin(self):
        amnt = self.obj.addmarginText.text()
        try:
            margin = self.exchange.add_margin(self.symbol, amnt)
            self.obj.addmarginText.setText('')
            # print(margin)
        except Exception as e:
            print('PEO EN ADD MARGIN ', e)
        return

    def reducemargin(self):
        amnt = self.obj.reducemarginText.text()
        try:
            margin = self.exchange.reduce_margin(self.symbol, amnt)
            # print(margin)
            self.obj.reducemarginText.setText('')
        except Exception as e:
            print('PEO EN REDUCE MARGIN ', e)
        return
