# -*- coding: utf-8 -*-
"""
AimarketsCap HFT SYSTEM GUI order managing
"""
import sys
import threading
import time
from datetime import datetime
import ccxt

class ExchangeOrderManaging:
    def __init__(self, exchange):
        pass

    def createorder(self, exchange, side):
        pass

    def deleteorder(self, exchange):
        pass

    def cancelorder(self, exchange):
        pass

    def cancelallorders(self, exchange):
        pass

    def closetrade(self, exchange):
        pass

def hftinit(data, exchange):

    grid = []
    factor = int(data['factor'])
    threshold = data['threshold']
    symbol = data['symbol']
    steps = int(data['steps'] / 2)
    amount = data['amount']

    ticker = data['ticker']
    center = data['center']

    if factor == 0:
        ticker = int(ticker)
    else:
        ticker = (int((int(ticker * factor)) / 5) * 5) / factor

    if center != None:
        x = center
        low = x - (threshold * (steps))
    else:
        x = ticker
        low = x - (threshold * (steps - 1))

    print('CERO: ', x)
    # Armo la lista en orden para que tenga todos los datos de la grid, antes de inicializarla
    side = 'BUY'
    for buy in range(steps):
        temporal = []
        temporal.append(buy)
        temporal.append(low)
        temporal.append(side)
        grid.append(temporal)
        low = low + threshold

    if center != None:
        low = low + threshold

    side = 'SELL'
    for sell in range((steps), (steps * 2)):
        temporal = []
        temporal.append(sell)
        temporal.append(low)
        temporal.append(side)
        grid.append(temporal)
        low = low + threshold

    for buy in range(steps):
        time.sleep(0.12)
        sell = (steps * 2) - buy - 1
        # s = await exchange.create_order(symbol, 'LIMIT', grid[sell][2], amount, grid[sell][1])
        # b = await exchange.create_order(symbol, 'LIMIT', grid[buy][2], amount, grid[buy][1])
        thread = threading.Thread(target=put,
                                  args=(sell, symbol, grid[sell][2], amount, grid[sell][1], exchange))
        thread.start()
        # time.sleep(0.3)
        thread = threading.Thread(target=put, args=(buy, symbol, grid[buy][2], amount, grid[buy][1], exchange))
        thread.start()

def put(n_, symbol_, dir_, amount_, price_, exchange_):
    e = exchange_.create_order(symbol_, 'LIMIT', dir_, amount_, price_)
    status = e['info']['status'].upper()

    #    if status == 'new':
    #        status = 'NEW'
    now = datetime.now()
    millisec = now.timestamp()
    print(str(n_) + ' [' + ('{:.4f}'.format(millisec)) + '] [' + ('{:.2f}'.format(price_)) + '] ' + dir_)
    return e
