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
from workers.orepeatsWorker import OrepeatsRunnable

from readConf import readgrids
import orderManaging
from orderManaging import hftinit, h, callo
from sockets import wbalance, fetchBalance, loadm, wticker
from workers.simetryWorker import SimetryRunnable
from wsorders import worders
from utils import message_status, pandasModel
import sockets
import gvars

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
testnet = False
gvars.disconnect = 0
stopfapi = False


class MainApp(QtWidgets.QMainWindow, ui):
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        self.setupUi(self)
        self.model = pandasModel(None)

        self.activehftLabel.setText(gvars.hftname)
        self.exchangeLabel.setText(gvars.exchangename )
        self.thresholdLabel.setText(str(gvars.threshold))
        self.leverageLabel.setText(gvars.leverage)
        self.marginLabel.setText(gvars.margintype)
        self.symbolLabel.setText(symbol)

        self.symbol = symbol
        self.grids = grids
        # self.button1.clicked.connect(self.melo)
        self.connectButton.clicked.connect(self.unclick)
        self.hftinitButton.clicked.connect(self.initi)
        self.cancellallordersButton.clicked.connect(self.callo)
        self.hftrestartButton.clicked.connect(self.reiniti)
        self.closetradeButton.clicked.connect(self.remove)
        self.testnetCheck.stateChanged.connect(self.enabletestnet)
        self.checkButton.clicked.connect(self.simerty)

        self.addmarginButton.clicked.connect(self.add_margin)
        self.reducemarginButton.clicked.connect(self.reduce_margin)
        self.disconnectButton.clicked.connect(self.discon)

        self.objects = self
        # self.pnl(symbol, ex)
        # self.duplicates()
        # self.simerty()

    def discon(self):
        gvars.disconnect = 1


    def simerty(self):
        pool = QThreadPool.globalInstance()
        runnable = SimetryRunnable(self.objects)
        pool.start(runnable)

    def duplicates(self):
        pool = QThreadPool.globalInstance()
        runnable = OrepeatsRunnable(self.objects)
        pool.start(runnable)

    def add_margin(self):
        pool = QThreadPool.globalInstance()
        runnable = MarginRunnable(self.objects, 'add')
        pool.start(runnable)

    def reduce_margin(self):
        pool = QThreadPool.globalInstance()
        runnable = MarginRunnable(self.objects, 'reduce')
        pool.start(runnable)

    def pnl(self, symbol, ex):
        threadCount = QThreadPool.globalInstance().maxThreadCount()
        pool = QThreadPool.globalInstance()
        runnable = PositionRiskRunnable(self.objects)
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
        orderManaging.start_trade = 0
        x = gvars.ex.cancel_all_orders(self.symbol)

    def unclick(self):
        return asyncio.ensure_future(self.startsockets())

    def initi(self):

        order_data = {'factor': gvars.factor, 'threshold': gvars.threshold, 'symbol': gvars.symbol,
                      'steps': gvars.steps, 'amount': gvars.amount, 'ticker': sockets.price_ticker,
                      'center': None}

        h(order_data)

    def reiniti(self):

        order_data = {'factor': gvars.factor, 'threshold': gvars.threshold, 'symbol': gvars.symbol,
                      'steps': gvars.steps, 'amount': gvars.amount, 'ticker': sockets.price_ticker,
                      'center': sockets.price_ticker}
        self.callo()
        hftinit(order_data)

    async def startsockets(self, ):
        await asyncio.gather(
            loadm(self, ),
            wticker(self),
            wbalance(self, ),
            fetchBalance(self, ),
            worders(self,),
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

    gvars.symbol = grids[0][12]
    gvars.amount = grids[0][3]
    gvars.threshold = grids[0][4]
    gvars.steps = grids[0][6]
    gvars.factor = grids[0][5]
    gvars.hftname = grids[0][1]
    gvars.exchangename = grids[0][9]
    gvars.leverage = grids[0][7]
    gvars.margintype = grids[0][8]
    gvars.api_key = grids[0][10]
    gvars.secret = grids[0][11]

    gvars.exchange = ccxtpro.binance(
        {
            'asyncio_loop': loop,
            'newUpdates': True,
            'apiKey': gvars.api_key,
            'secret': gvars.secret,
            'enableRateLimit': True,  # https://github.com/ccxt/ccxt/wiki/Manual#rate-limit
            'options': {
                'defaultType': 'future',
            },
        })
    if testnet:
        gvars.exchange.set_sandbox_mode(True)
    else:
        gvars.exchange.set_sandbox_mode(False)
    gvars.ex = ccxt.binance(
        {
            'newUpdates': True,
            'apiKey': gvars.api_key,
            'secret': gvars.secret,
            'enableRateLimit': True,  # https://github.com/ccxt/ccxt/wiki/Manual#rate-limit
            'options': {
                'defaultType': 'future',
            },
        })
    if testnet:
        gvars.ex.set_sandbox_mode(True)
    else:
        gvars.ex.set_sandbox_mode(False)

    asyncio.set_event_loop(loop)
    window = MainApp()
    window.show()
    with loop:
        loop.run_forever()
