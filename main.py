# -*- coding: utf-8 -*-
"""
AimarketsCap HFT SYSTEM GUI
"""
# key jiqXyMUh9zqCzzisgTsHek0t7DPdKoC6mM1nrPqIcbilsmPGOtCfEHXuQgND9g3A
# secret wDND7jmFTfVP8GJKjVUyTnG2dtRavWvRlQldQTe4aLK1WcKpE2vMwWimWBQaAwa8

import asyncio
import sys

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt, QPersistentModelIndex, QModelIndex
from PyQt5.QtCore import pyqtSignal
from asyncqt import QEventLoop
from PyQt5.uic import loadUiType
import ccxt
import ccxtpro

from readConf import readgrids
from orderManaging import hftinit, h
from sockets import wbalance, fetchBalance, loadm
from wsorders import worders
from sockets import global_ticker
from utils import message_status
ui, _ = loadUiType('main2.ui')

exchange = None
global_ticker = None
ex = None
grids = None
bal = None
symbol = None
order_array = None
amount = None
threshold = None
factor = None
steps = None
api_key = None
api_id = None
order_data = None

disconnect = 0

row_1 = ['<span style="color:green">313513513</span>', 'LIMIT', 'BUY', 'NEW', 'NEW', 46758.25, '1', 0.02]

async def wticker(self):
    global global_ticker
    self.statusbar.showMessage("Fetching PRICE...")
    while True:
        try:

            self.ticker = await self.exchange.watch_ticker(self.symbol)
            global_ticker = self.ticker['last']
            self.lcdTicker.display(self.ticker['last'])
            await message_status(self, "New PRICE event...", 0.3)
        except Exception as e:
            print(e)
            self.statusbar.showMessage("ERROR: '{}' Fetching WS TICKER...".format(e))
            break
        finally:
            # print('t')
            pass


class MainApp(QtWidgets.QMainWindow, ui):


    def __init__(self, exchange):
        global order_data
        QtWidgets.QMainWindow.__init__(self)
        self.setupUi(self)
        self.exchange = exchange
        # asyncio.ensure_future(self.startsockets())
        # asyncio.ensure_future()
        self.activehftLabel.setText(grids[0][1])
        self.exchangeLabel.setText(grids[0][9])
        self.thresholdLabel.setText(str(grids[0][4]))
        self.leverageLabel.setText(grids[0][7])
        self.marginLabel.setText(grids[0][8])
        self.symbolLabel.setText(grids[0][12])
        self.symbol = grids[0][12]
        # self.button1.clicked.connect(self.melo)
        self.connectButton.clicked.connect(self.unclick)
        self.hftinitButton.clicked.connect(self.initi)
        self.cancellallordersButton.clicked.connect(self.callo)
        self.hftrestartButton.clicked.connect(self.reiniti)
        self.closetradeButton.clicked.connect(self.remove)

        self.disconnectButton.clicked.connect(self.discon)

    def remove(self):
        indexes =[QPersistentModelIndex(index) for index in self.orderTable.selectionModel()]
        print(indexes)
        maxrow = max(indexes, key=lambda x: x.row()).row()
        next_ix = QPersistentModelIndex(self.QSModel.index(maxrow+1, 0))
        for index in indexes:
            print('Deleting row %d...' % index.row())
            self.QSModel.removeRow(index.row())
        self.orderTable.setCurrentIndex(QModelIndex(next_ix))


    def callo(self,):
        x = ex.cancel_all_orders(self.symbol)
        # index_list = []
        # for model_index in self.tableView.selectionModel().selectedRows():
        #     index = QtCore.QPersistentModelIndex(model_index)
        #     index_list.append(index)
        #
        # for index in index_list:
        #     self.model.removeRow(index.row())


    def unclick(self):
        return asyncio.ensure_future(self.startsockets())

    def initi(self):
        order_data = {'factor': grids[0][5], 'threshold': grids[0][4], 'symbol': grids[0][12],
                      'steps': grids[0][6], 'amount': grids[0][3], 'ticker': global_ticker,
                      'center': None}

        h(order_data, ex)

    def reiniti(self):
        order_data = {'factor': grids[0][5], 'threshold': grids[0][4], 'symbol': grids[0][12],
                      'steps': grids[0][6], 'amount': grids[0][3], 'ticker': global_ticker,
                      'center': global_ticker}
        self.callo()
        hftinit(order_data, ex)

    def discon(self ):
        return asyncio.ensure_future(self.xx())

    async def xx(self):

        await exchange.close()



    async def startsockets(self, ):
        await asyncio.gather(
            loadm(self, ex, exchange),
            fetchBalance(self, exchange),
            wticker(self),
            wbalance(self, exchange),
            worders(self, exchange, amount, threshold, symbol, factor, ex)
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
    symbol = grids[0][12]
    amount = grids[0][3]
    threshold = grids[0][4]
    steps = grids[0][6]
    factor = grids[0][5]

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
