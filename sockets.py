import asyncio

import pandas as pd

from utils import pandasModel, message_status
from PyQt5.QtCore import Qt
global_ticker = None

async def wticker(self, exchange):
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


        # self.addTableRow(self.orderTable, row_1)
        # /¡self.logText.append('<span style="color:white">{}</span>'.format(str(self.ticker['last'])))
        # print_ticker()


async def wohlc(self, exchange):
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
        finally:

            print('t')
        # self.addTableRow(self.orderTable, row_1)
        # /¡self.logText.append('<span style="color:white">{}</span>'.format(str(self.ticker['last'])))
        # print_ticker()

async def fetchBalance(self, exchange):
    try:

        global bal
        bal = await self.exchange.fetchBalance()
        self.statusbar.showMessage("Fetching Balance...")
        self.walletcapitalLCD.display(bal['USDT']['free'])
        self.usedcapitalLcd.display(bal['USDT']['used'])
        # used = round((bal['USDT']['free'] - bal['USDT']['used']), 3)
        r = (bal['USDT']['used'] * 100 / bal['USDT']['total'])
        # print(r)
        self.usedcapitalBar.setValue(int(r))
    except Exception as e:
        print(e)
        self.statusbar.showMessage("ERROR {} Fetching BALANCE...".format(e))
    finally:
        print('fb')
    # print(bal)





async def loadm(self, ex, exchange):
    self.statusbar.showMessage("Fetching Markets...")
    ex.load_markets()
    await exchange.load_markets()


async def wbalance(self, exchange):
    while True:
        global bal
        try:
            self.statusbar.showMessage("Fetching WS Balance...")
            bal = await self.exchange.watchBalance()
            self.walletcapitalLCD.display(bal['USDT']['free'])
            # print(bal)
            # print(bal['info'])
        except Exception as e:
            print(e)
            self.statusbar.showMessage("ERROR {} Fetching WS BALANCE...".format(e))
            print("ERROR {} Fetching WS BALANCE...".format(e))
        finally:
            pass
            # print('wb')

        now = exchange.milliseconds()
        # # start color code
        # print(bal)
        try:
            wb = float(bal['info']['a']['B'][0]['wb'])  # wallet balance
            cw = float(bal['info']['a']['B'][0]['cw'])  # free
            used = round((wb - cw), 3)
            self.walletcapitalLCD.display(wb)
            self.usedcapitalLcd.display(used)
            r = (100 - (cw * 100 / wb))
            self.usedcapitalBar.setValue(int(r))
        except Exception as e:
            print("ERROR {} Fetching WS BALANCE...".format(e))
            pass
        finally:
            pass
            # print('wb -e ')


async def positionrisk(self, exchange, symbol, amount):
    pos = await exchange.fapiPrivate_get_positionrisk()  # or fapiPrivate_get_positionrisk()
    posval = 0
    market = exchange.market(symbol)['id']
    for i in pos:
        if (i['symbol'] == market):
            old_trades = float(i['positionAmt']) / amount
            trades = int(old_trades)
            print(i)
            print('FOUND  TRADES ', trades)
            posval = float(i['positionAmt'])
    if posval != 0:
        filled = 1
    else:
        filled = 0
    return filled

async def positionrisk(self, exchange, symbol):
    while True:
        pos = await exchange.fapiPrivate_get_positionrisk()  # or fapiPrivate_get_positionrisk()
        posval = 0
        market = exchange.market(symbol)['id']
        for i in pos:
            if (i['symbol'] == market):
                posval = float(i['positionAmt'])
        if posval != 0:
            filled = 1
        else:
            filled = 0
        return filled
        time.sleep()