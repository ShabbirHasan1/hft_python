# -*- coding: utf-8 -*-
"""
AimarketsCap HFT SYSTEM GUI order managing
"""
import operator
import threading
import time
import ccxt
import gvars

start_trade = 0
exchange = gvars.exchange
ex = gvars.ex


class ExchangeOrderManaging:
    def __init__(self, exchange):
        pass

    def createorder(self, exchange, side):
        pass

    def deleteorder(self, exchange):
        pass


def cancelorder(oids):
    try:
        x = exchange.cancel_order(oids, symbol)
    except Exception as e:
        print('exception in cancell order ', e)
    return

    # def cancelallorders(self, exchange):
    #     pass


def closetrade(self, exchange):
    pass


def callo(symbol):
    x = ex.cancel_all_orders(symbol)
    return
    # print('afefw -->',  x)


def h(data):
    global start_trade
    global order_array
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
        low = x - (threshold * steps)
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
        time.sleep(0.2)
        sell = (steps * 2) - buy - 1
        s = threading.Thread(target=put, args=(sell, symbol, grid[sell][2], amount, grid[sell][1]), )
        s.start()
        b = threading.Thread(target=put, args=(buy, symbol, grid[buy][2], amount, grid[buy][1]), )
        b.start()
        # gvars.order_array_sell.append([sell, symbol, grid[sell][2], amount, grid[sell][1]])
        # gvars.order_array_buy.append([buy, symbol, grid[buy][2], amount, grid[buy][1]])
        # print((sell, symbol, grid[sell][2], amount, grid[sell][1]))
        # print((buy, symbol, grid[buy][2], amount, grid[buy][1]))

    # gvars.order_array_sell = sorting_list(gvars.order_array_sell)
    # gvars.order_array_buy = sorting_list(gvars.order_array_buy)

    # print(gvars.order_array_sell)
    # print(gvars.order_array_buy)

    start_trade = 1
    return

def sort_ws_list(nested_list, reverse=None):
    sorted_list = sorted(nested_list, key=operator.itemgetter(5),  reverse=reverse)
    for i in range(0, len(sorted_list)):
        sorted_list[i][0] = i
    return sorted_list


def sorting_list(nested_list):
    sorted_list = sorted(nested_list, key=operator.itemgetter(2))
    for i in range(0, len(sorted_list)):
        sorted_list[i][0] = i
    return sorted_list


def hftinit(data):
    global start_trade
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
        time.sleep(0.1)
        sell = (steps * 2) - buy - 1

        # s = await exchange.
        # (symbol, 'LIMIT', grid[sell][2], amount, grid[sell][1])
        # b = await exchange.create_order(symbol, 'LIMIT', grid[buy][2], amount, grid[buy][1])
        thread = threading.Thread(target=put,
                                  args=(sell, symbol, grid[sell][2], amount, grid[sell][1], exchange))
        thread.start()
        time.sleep(0.1)
        thread = threading.Thread(target=put, args=(buy, symbol, grid[buy][2], amount, grid[buy][1], exchange))
        thread.start()

    start_trade = 1
    return


def put(n_, symbol_, dir_, amount_, price_):
    global start_trade
    global ex
    try:
        start_trade = 0
        gvars.ex.create_order(symbol_, 'LIMIT', dir_, amount_, price_)
    except ccxt.NetworkError as e:
        print(gvars.ex.id, 'failed due to a network error:', str(e))
        # retry or whatever
    except ccxt.ExchangeError as e:
        print(gvars.ex.id, 'failed due to exchange error:', str(e))
        # retry or whatever
    except Exception as e:
        print(gvars.ex.id, 'failed with:', str(e))
    finally:
        start_trade = 1
    return


async def pu(n_, symbol_, dir_, amount_, price_, exchange_):
    global start_trade
    start_trade = 0
    e = await exchange.create_order(symbol_, 'LIMIT', dir_, amount_, price_)
    start_trade = 1
    return e


def put_first_order(symbol, direction, amount, threshold, dataf, exchange):
    global start_trade
    start_trade = 0
    try:
        if direction == 'BUY':
            buycero = dataf.loc[(dataf['internal_status'] == 0) & (dataf['side'] == direction)]
            buycero.sort_values('price', inplace=True, ascending=True)
            price = float(dataf.iloc[buycero.index[0]]['price']) - threshold
        else:
            sellcero = dataf.loc[(dataf['internal_status'] == 0) & (dataf['side'] == direction)]
            sellcero.sort_values('price', inplace=True, ascending=False)
            price = float(dataf.iloc[sellcero.index[0]]['price']) + threshold
        o = exchange.create_order(symbol, 'LIMIT', direction, amount, price)
    except Exception as e:
        print('exception in putS order ', e)
        raise
    finally:
        start_trade = 1
    return


def puts(symbol, dir, amount, price):
    global start_trade
    start_trade = 0
    try:
        # print('creando...', gvars.ex)
        o = gvars.ex.create_order(symbol, 'LIMIT', dir, amount, price)
    except ccxt.NetworkError as e:
        print(gvars.ex.id, 'failed due to a network error:', str(e))
        # retry or whatever
    except ccxt.ExchangeError as e:
        print(gvars.ex.id, 'failed due to exchange error:', str(e))
        # retry or whatever
    except Exception as e:
        print(gvars.ex.id, 'failed with:', str(e))


async def addmargin(self, symbol, amount, exchange):
    await exchange.add_margin(symbol, amount)
