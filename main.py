# -*- coding: utf-8 -*-
"""
AimarketsCap HFT SYSTEM GUI
"""

import asyncio
import sys

from PyQt5 import QtCore, QtGui, QtWidgets

from asyncqt import QEventLoop
from PyQt5.uic import loadUiType
import ccxt
import ccxtpro

from readConf import readgrids
from orderManaging import ExchangeOrderManaging
#

# import asyncio
#
# from PyQt5 import QtCore, QtGui, QtWidgets
# import sys
#
# from PyQt5.uic import loadUiType
#
#

#
ui, _ = loadUiType('main2.ui')

exchange = None
global_ticker = None
grids = None
bal = None
symbol = None

amount = None
threshold = None
factor = None
steps = None

#
#
# #
# # class DictionaryTableModel(QtCore.QAbstractTableModel):
# #     def __init__(self, data, headers):
# #         super(DictionaryTableModel, self).__init__()
# #         self._data = data
# #         self._headers = headers
# #
# #     def data(self, index, role):
# #         if role == Qt.DisplayRole:
# #             # Look up the key by header index.
# #             column = index.column()
# #             column_key = self._headers[column]
# #             return self._data[index.row()][column_key]
# #
# #     def rowCount(self, index):
# #         # The length of the outer list.
# #         return len(self._data)
# #
# #     def columnCount(self, index):
# #         # The length of our headers.
# #         return len(self._headers)
# #
# #     def headerData(self, section, orientation, role):
# #         # section is the index of the column/row.
# #         if role == Qt.DisplayRole:
# #             if orientation == Qt.Horizontal:
# #                 return str(self._headers[section])
# #
# #             if orientation == Qt.Vertical:
# #                 return str(section)
# #
#
#
#
#

row_1 = ['<span style="color:green">313513513</span>', 'LIMIT', 'BUY', 'NEW', 'NEW', 46758.25, '1', 0.02]


#
#

def print_ticker():
    print(grids[0])


class MainApp(QtWidgets.QMainWindow, ui):
    symbol = 'BTC/USDT'
    ticker = None

    # exchange.setSandboxMode(True)

    def __init__(self, exchange):
        QtWidgets.QMainWindow.__init__(self)
        self.setupUi(self)
        self.exchange = exchange
        # asyncio.ensure_future(self.ex.loadmarkets())

        asyncio.ensure_future(self.xxx())

        self.activehftLabel.setText(grids[0][1])
        self.exchangeLabel.setText(grids[0][9])
        self.thresholdLabel.setText(str(grids[0][4]))
        self.leverageLabel.setText(grids[0][7])
        self.marginLabel.setText(grids[0][8])
        self.symbolLabel.setText(grids[0][12])

    # self.button1.clicked.connect(self.melo)

    async def xxx(self, ):
        await asyncio.gather(
            self.wticker(),
            self.fetchBalance(),
            self.wbalance()
        )

    def addTableRow(self, table, row_data):
        row = table.rowCount()
        table.setRowCount(row + 1)
        col = 0
        for item in row_data:
            cell = QtWidgets.QTableWidgetItem(str(item))
            table.setItem(row, col, cell)
            col += 1

    #
    #     def melo(self):
    #         # print(self.orderTable)
    #         self.addTableRow(self.orderTable, row_1)
    #
    async def wticker(self):
        global global_ticker
        while True:
            self.addTableRow(self.orderTable, row_1)
            self.ticker = await self.exchange.watch_ticker(self.symbol)
            global_ticker = self.ticker['last']
            self.lcdTicker.display(self.ticker['last'])
            self.logText.append('<span style="color:white">{}</span>'.format(str(self.ticker['last'])))
            # print_ticker()

    async def fetchBalance(self):
        global bal
        bal = await self.exchange.fetchBalance()
        print(bal)
        self.walletcapitalLCD.display(bal['USDT']['free'])
        self.usedcapitalLcd.display(bal['USDT']['used'])
        # used = round((bal['USDT']['free'] - bal['USDT']['used']), 3)
        r = (bal['USDT']['used'] * 100 / bal['USDT']['total'])
        print(r)
        self.usedcapitalBar.setValue(int(r))

        return bal

    async def worders(self):
        while True:
            print(self.symbol)
            print(self.exchange)
            self.ticker = await self.exchange.watch_ticker(self.symbol)
            now = self.exchange.milliseconds()
            # # start color code
            self.lcdTicker.display(self.ticker['last'])
            print(self.exchange.iso8601(now), self.symbol, self.ticker['last'])

    async def wbalance(self):
        while True:
            global bal
            bal = await self.exchange.watchBalance()
            now = exchange.milliseconds()
            # # start color code
            wb = float(bal['info']['a']['B'][0]['wb']) # wallet balance
            cw = float(bal['info']['a']['B'][0]['cw']) # free
            used = round((wb - cw), 3)
            self.walletcapitalLCD.display(wb)
            self.usedcapitalLcd.display(used)
            r = (100 - (cw * 100 / wb))
            self.usedcapitalBar.setValue(int(r))


x = {'info':
         {'e': 'ACCOUNT_UPDATE', 'T': 1629672475846, 'E': 1629672475849, 'a':
             {
                 'B': [{'a': 'USDT', 'wb': '10001.04627647', 'cw': '10001.04627647', 'bc': '0'}],
                 'P': [{'s': 'BTCUSDT', 'pa': '0', 'ep': '0.00000', 'cr': '-1.79409000', 'up': '0', 'mt': 'isolated', 'iw': '0', 'ps': 'BOTH', 'ma': 'USDT'}], 'm': 'ORDER'}},
                'USDT': {'free': None, 'used': None, 'total': 10001.04627647}, 'timestamp': None, 'datetime': None, 'free': {'USDT': None}, 'used': {'USDT': None}, 'total': {'USDT': 10001.04627647}}

#
#         #
#
#
# def main():
#     global exchange, symbol
#
#     app = QtWidgets.QApplication(sys.argv)
#
#     File = QtCore.QFile('theme.qss')
#     if not File.open(QtCore.QFile.ReadOnly | QtCore.QFile.Text):
#         return
#     qss = QtCore.QTextStream(File)
#     # setup stylesheet
#     app.setStyleSheet(qss.readAll())
#     window = MainApp()
#
#     window.show()
#     app.exec_()
#
#
# if __name__ == "__main__":
#     main()

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    File = QtCore.QFile('theme.scss')
    if not File.open(QtCore.QFile.ReadOnly | QtCore.QFile.Text):
        sys.exit()
    qss = QtCore.QTextStream(File)
    # setup stylesheet
    app.setStyleSheet(qss.readAll())

    loop = QEventLoop(app)
    exchange = ccxtpro.binance(
        {
            'asyncio_loop': loop,
            'apiKey': 'e9c5d8c2cf90df88f5af9d5266aefc83d82d981bc271f0cf249bb2991d4265e9',
            'secret': 'dcd56c1ff1639753ddabcac8d8d1171ae05d4d5dc148334156053282bb442581',
            'enableRateLimit': True,  # https://github.com/ccxt/ccxt/wiki/Manual#rate-limit
            'options': {
                'defaultType': 'future',
            },
        })
    exchange.set_sandbox_mode(True)
    grids = readgrids()
    asyncio.set_event_loop(loop)
    window = MainApp(exchange)
    window.show()
    with loop:
        loop.run_forever()
