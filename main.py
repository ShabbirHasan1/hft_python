# -*- coding: utf-8 -*-
"""
AimarketsCap HFT SYSTEM GUI
"""

import asyncio
import sys

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QAbstractTableModel, Qt

from asyncqt import QEventLoop
from PyQt5.uic import loadUiType
import ccxt
import ccxtpro
import pandas as pd
from readConf import readgrids
from orderManaging import hftinit

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
ex = None
global_ticker = None
grids = None
bal = None
symbol = None
orders = None
order_array = None
amount = None
threshold = None
factor = None
steps = None
api_key = None
api_id = None
order_data = None
#
#
# #

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


class pandasModel(QAbstractTableModel):

    def __init__(self, data):
        QAbstractTableModel.__init__(self)
        self._data = data

    def rowCount(self, parent=None):
        return self._data.shape[0]

    def columnCount(self, parnet=None):
        return self._data.shape[1]

    def data(self, index, role=Qt.DisplayRole):
        if index.isValid():
            if role == Qt.DisplayRole:
                return str(self._data.iloc[index.row(), index.column()])
        return None

    def headerData(self, col, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self._data.columns[col]
        return None


class MainApp(QtWidgets.QMainWindow, ui):
    symbol = 'BTC/USDT'
    ticker = None

    # exchange.setSandboxMode(True)

    def __init__(self, exchange):
        global order_data
        QtWidgets.QMainWindow.__init__(self)
        self.setupUi(self)
        self.exchange = exchange
        asyncio.ensure_future(self.xxx())
        # asyncio.ensure_future(self.ex.loadmarkets())

        self.activehftLabel.setText(grids[0][1])
        self.exchangeLabel.setText(grids[0][9])
        self.thresholdLabel.setText(str(grids[0][4]))
        self.leverageLabel.setText(grids[0][7])
        self.marginLabel.setText(grids[0][8])
        self.symbolLabel.setText(grids[0][12])

        # self.button1.clicked.connect(self.melo)
        self.hftinitButton.clicked.connect(self.init)




    def init(data):
        global ex

        order_data = {'factor': grids[0][5], 'threshold': grids[0][4], 'symbol': grids[0][12],
                      'steps': grids[0][6], 'amount': grids[0][3], 'ticker': global_ticker,
                      'center': None}

        hftinit(order_data, ex)


    async def xxx(self, ):
        await asyncio.gather(
            self.wticker(),
            self.fetchBalance(),
            self.wbalance(),
            self.worders()
        )

    # def addTableRow(self, table, row_data):
    #     row = table.rowCount()
    #     table.setRowCount(row + 1)
    #     col = 0
    #     for item in row_data:
    #         print(item)
    #         cell = QtWidgets.QTableWidgetItem(str(item))
    #         table.setItem(row, col, cell)
    #         col += 1

    #
    #     def melo(self):
    #         # print(self.orderTable)
    #         self.addTableRow(self.orderTable, row_1)
    #
    async def wticker(self):
        global global_ticker
        while True:
            try:
                self.ticker = await self.exchange.watch_ticker(self.symbol)
                global_ticker = self.ticker['last']
                self.lcdTicker.display(self.ticker['last'])
            except Exception as e:
                print(e)
            finally:
                print('t')
            # self.addTableRow(self.orderTable, row_1)
            # /¡self.logText.append('<span style="color:white">{}</span>'.format(str(self.ticker['last'])))
            # print_ticker()

    async def fetchBalance(self):

        try:
            global bal
            bal = await self.exchange.fetchBalance()
            self.walletcapitalLCD.display(bal['USDT']['free'])
            self.usedcapitalLcd.display(bal['USDT']['used'])
            # used = round((bal['USDT']['free'] - bal['USDT']['used']), 3)
            r = (bal['USDT']['used'] * 100 / bal['USDT']['total'])
            # print(r)
            self.usedcapitalBar.setValue(int(r))
        except Exception as e:
            print(e)
        finally:
            print('fb')
        # print(bal)

    async def worders(self):
        global orders
        df = pd.DataFrame(
            columns=['internal_status', 'symbol', 'cET', 'cOS', 'price', 'type', 'side', 'order_id', 'timestamp', 'L',
                     'n', 'N', 'l', 'z'])
        while True:
            try:
                orders = await self.exchange.watchOrders()
            except Exception as e:
                print(e)
            finally:
                print('wo')
            print(orders[0])
            currentExecutionType = orders[0]['info']['x']
            currentOrderStatus = orders[0]['info']['X']
            orderType = orders[0]['info']['o']
            orderId = int(orders[0]['info']['i'])
            amount = orders[0]['info']['q']
            side = orders[0]['info']['S']
            price = orders[0]['info']['p']
            lastExecutedPrice = float(orders[0]['info']['L'])
            timestamp = int(orders[0]['info']['T'])
            symbol = orders[0]['info']['s']

            if currentExecutionType == 'NEW' and currentOrderStatus == 'NEW':
                r = df.loc[df['order_id'] == orderId]
                if r.__len__() > 0:
                    print('order found not for save...')
                else:

                    df = df.append(
                        {'internal_status': 0, 'symbol': symbol, 'cET': currentExecutionType,
                         'cOS': currentOrderStatus, 'price': price,
                         'type': type, 'side': side, 'order_id': orderId, 'timestamp': timestamp, 'L': '', 'n': '',
                         'N': '',
                         'l': '', 'z': ''}, ignore_index=True)
                    model = pandasModel(df)
                    self.orderTable.setModel(model)

            if currentExecutionType == 'TRADE' and currentOrderStatus == 'FILLED':
                if type != 'MARKET':
                    commissionAmount = orders[0]['info']['n']
                    commisionAsset = orders[0]['info']['N']
                    lastExecutedQuantity = orders[0]['info']['l']
                    cumulativeFilledQuantity = orders[0]['info']['z']

                    r = df.loc[df['order_id'] == orderId]
                    # se revienta si el dataframe está vacío
                    df.at[r.index[0], 'L'] = lastExecutedPrice
                    df.at[r.index[0], 'n'] = commissionAmount
                    df.at[r.index[0], 'N'] = commisionAsset
                    df.at[r.index[0], 'l'] = lastExecutedQuantity
                    df.at[r.index[0], 'z'] = cumulativeFilledQuantity
                    df.at[r.index[0], 'cET'] = currentExecutionType
                    df.at[r.index[0], 'cOS'] = currentOrderStatus
                    df.at[r.index[0], 'internal_status'] = 1
                    df.at[r.index[0], 'timestamp'] = timestamp
                    df.at[r.index[0], 'order_id'] = orderId

            row_1 = ['<span style="color:green">313513513</span>', 'LIMIT', 'BUY', 'NEW', 'NEW', 46758.25, '1', 0.02]

            print(df)
            # self.logText.append(str(df))
            # self.logText.append('----------------')

    async def wbalance(self):
        while True:
            global bal
            try:
                bal = await self.exchange.watchBalance()
            except Exception as e:
                print(e)
            finally:
                print('wb')

            now = exchange.milliseconds()
            # # start color code
            print(bal)
            try:
                wb = float(bal['info']['a']['B'][0]['wb'])  # wallet balance
                cw = float(bal['info']['a']['B'][0]['cw'])  # free
                used = round((wb - cw), 3)
                self.walletcapitalLCD.display(wb)
                self.usedcapitalLcd.display(used)
                r = (100 - (cw * 100 / wb))
                self.usedcapitalBar.setValue(int(r))
            except Exception as e:
                pass
            finally:
                print('wb -e ')


if __name__ == "__main__":
    grids = readgrids()
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
            'newUpdates': True,
            'apiKey': grids[0][10],
            'secret': grids[0][11],
            'enableRateLimit': True,  # https://github.com/ccxt/ccxt/wiki/Manual#rate-limit
            'options': {
                'defaultType': 'future',
            },
        })
    exchange.set_sandbox_mode(True)

    ex = ccxt.binance(
        {
            'newUpdates': True,
            'apiKey': grids[0][10],
            'secret': grids[0][11],
            'enableRateLimit': True,  # https://github.com/ccxt/ccxt/wiki/Manual#rate-limit
            'options': {
                'defaultType': 'future',
            },
        })
    ex.set_sandbox_mode(True)

    asyncio.set_event_loop(loop)
    window = MainApp(exchange)
    window.show()
    with loop:
        loop.run_forever()
