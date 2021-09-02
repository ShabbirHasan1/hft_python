# -*- coding: utf-8 -*-
"""
AimarketsCap HFT SYSTEM GUI
"""
# key jiqXyMUh9zqCzzisgTsHek0t7DPdKoC6mM1nrPqIcbilsmPGOtCfEHXuQgND9g3A
# secret wDND7jmFTfVP8GJKjVUyTnG2dtRavWvRlQldQTe4aLK1WcKpE2vMwWimWBQaAwa8

import asyncio
import sys

from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import QThreadPool
from asyncqt import QEventLoop
from PyQt5.uic import loadUiType
import ccxt
import ccxtpro
from workers.exchangeWorkers import PositionRiskRunnable
from workers.marginWorkers import MarginRunnable

from readConf import readgrids
from orderManaging import hftinit, h, callo
from sockets import wbalance, fetchBalance, loadm, wticker
from wsorders import worders
from utils import message_status, pandasModel
import sockets

ui, _ = loadUiType('main2.ui')

exchange = None
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
testnet = True
disconnect = 0
stopfapi = False

class MainApp(QtWidgets.QMainWindow, ui):
    def __init__(self, exchange):
        global order_data
        QtWidgets.QMainWindow.__init__(self)
        self.setupUi(self)
        self.model = pandasModel(None)
        self.exchange = exchange
        self.ex = ex
        # self.pools = Pool(processes=12)
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
        self.testnetCheck.stateChanged.connect(self.enabletestnet)
        self.disconnectButton.clicked.connect(self.discon)

        self.addmarginButton.clicked.connect(self.add_margin)
        self.reducemarginButton.clicked.connect(self.reduce_margin)

        self.objects = self
        self.pnl(symbol, ex)

    def discon(self):
        rin = PositionRiskRunnable(symbol, ex, self.objects, True)

    def add_margin(self):
        pool = QThreadPool.globalInstance()
        runnable = MarginRunnable(symbol, self.ex, self.objects, 'add')
        pool.start(runnable)

    def reduce_margin(self):
        pool = QThreadPool.globalInstance()
        runnable = MarginRunnable(symbol, self.ex, self.objects, 'reduce')
        pool.start(runnable)

    def pnl(self, symbol, ex):
        threadCount = QThreadPool.globalInstance().maxThreadCount()
        pool = QThreadPool.globalInstance()
        runnable = PositionRiskRunnable(symbol, ex, self.objects, stopfapi)
        pool.start(runnable)

    def enabletestnet(self):
        if self.testnetCheck.isChecked():
            testnet = True
        else:
            testnet = False

    def remove(self):
        indexes = self.orderTable.selectedIndexes()
        if indexes:
            # Indexes is a list of a single item in single-select mode.
            index = indexes[0]
            # Remove the item and refresh.
            del self.model._data[index.row()]
            self.model.layoutChanged.emit()
            # Clear the selection (as it is no longer valid).
            self.orderTable.clearSelection()
            self.save()

    def callo(self, ):
        x = ex.cancel_all_orders(self.symbol)

    def unclick(self):
        return asyncio.ensure_future(self.startsockets())

    def initi(self):
        order_data = {'factor': grids[0][5], 'threshold': grids[0][4], 'symbol': grids[0][12],
                      'steps': grids[0][6], 'amount': grids[0][3], 'ticker': sockets.price_ticker,
                      'center': None}

        h(order_data, ex)

    def reiniti(self):
        order_data = {'factor': grids[0][5], 'threshold': grids[0][4], 'symbol': grids[0][12],
                      'steps': grids[0][6], 'amount': grids[0][3], 'ticker': sockets.price_ticker,
                      'center': sockets.price_ticker}
        self.callo()
        hftinit(order_data, ex)

    async def startsockets(self, ):
        await asyncio.gather(
            loadm(self, ex, exchange),
            wticker(self),
            wbalance(self, exchange),
            fetchBalance(self, exchange),
            worders(self, exchange, amount, threshold, symbol, factor, ex, int(steps)
                    ),
        )

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
    if testnet:
        exchange.set_sandbox_mode(True)
    else:
        exchange.set_sandbox_mode(False)

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
    if testnet:
        ex.set_sandbox_mode(True)
    else:
        ex.set_sandbox_mode(False)

    asyncio.set_event_loop(loop)
    window = MainApp(exchange)
    window.show()
    with loop:
        loop.run_forever()
