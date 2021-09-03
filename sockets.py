import time
from utils import message_status

price_ticker = None
balance = None


async def wticker(self):
    self.statusbar.showMessage("Fetching PRICE...")
    while True:
        try:
            global price_ticker
            self.ticker = await self.exchange.watch_ticker(self.symbol)
            price_ticker = self.ticker['last']
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
        b = await self.exchange.fetchBalance()
        self.statusbar.showMessage("Fetching Balance...")
        self.walletcapitalLCD.display(b['USDT']['free'])
        self.usedcapitalLcd.display(b['USDT']['used'])
        # used = round((b['USDT']['free'] - b['USDT']['used']), 3)
        r = (b['USDT']['used'] * 100 / b['USDT']['total'])
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
        global balance
        try:
            self.statusbar.showMessage("Fetching WS Balance...")
            bal = await self.exchange.watchBalance()
            self.walletcapitalLCD.display(bal['USDT']['free'])
            # x = {'info': {'e': 'ACCOUNT_UPDATE', 'T': 1630546431781, 'E': 1630546431784,
            #           'a': {'B': [{'a': 'USDT', 'wb': '9996.63709378', 'cw': '9947.27881141', 'bc': '0'}], 'P': [
            #               {'s': 'BTCUSDT', 'pa': '-0.005', 'ep': '49335.39000', 'cr': '4.61880003', 'up': '-0.01987353',
            #                'mt': 'isolated', 'iw': '49.35828237', 'ps': 'BOTH', 'ma': 'USDT'}], 'm': 'ORDER'}},
            #  'USDT': {'free': None, 'used': None, 'total': 9996.63709378}, 'timestamp': None, 'datetime': None,
            #  'free': {'USDT': None}, 'used': {'USDT': None}, 'total': {'USDT': 9996.63709378}}
            # print( bal['info']['a'])
            try:
                balance = bal['info']['a']['P'][0]['pa']
                print('BALANCE EW WATCHBALANCE: ', bal['info']['a']['P'][0]['pa'])
            except Exception as e:
                print('problem in balance socket ', e)

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
            # print(bal['info'])
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


async def positionrisk(self, exchange, symbol):
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


def pplm(self, s, eo):
    eo.loadMarkets()
    print('entré en pplm')
    try:
        pos = eo.fapiPrivate_get_positionrisk()  # or fapiPrivate_get_positionrisk()
        market = eo.market(s)['id']
        for i in pos:
            if (i['symbol'] == market):
                print(i)
                positionAmt = i['positionAmt']
                entryPrice = i['entryPrice']
                unRealizedProfit = i['unRealizedProfit']
                liquidationPrice = i['liquidationPrice']
                isolatedMargin = i['isolatedMargin']

                # self.positionLCD.display(positionAmt)
                # self.pnlLCD.display(unRealizedProfit)
                # self.liquidationPriceLCD.display(liquidationPrice)
                # self.marginLCD.display(isolatedMargin)
    except Exception as e:
        print(e)
