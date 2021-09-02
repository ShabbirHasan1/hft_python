import operator
import time
from datetime import datetime
from sockets import positionrisk
import pandas as pd
from utils import pandasModel, message_status
from orderManaging import puts, cancelorder
from multiprocessing import Pool
import sockets

grilla = []

trades = 0

async def worders(self, exchange, gamount, threshold, gsymbol, factor, ex, steps):
    global grilla
    global trades


    pools = Pool(processes=8)
    filled = 0
    saldo = None
    balance = sockets.balance

    i = 0
    n = 0

    cancel = 0
    enter = 0

    position_amount = 0
    inicio_sell = 0
    inicio_buy = 0

    arr = {}

    await exchange.load_markets()
    ex.load_markets()
    filled = await positionrisk(self, exchange, gsymbol)
    while True:
        try:
            orders = await exchange.watchOrders()

            # print('price ticker ', sockets.price_ticker)
            # print('balance ', sockets.balance)

            # self.statusbar.showMessage("Fetching WS ORDERS...")

            currentExecutionType = orders[0]['info']['x']
            currentOrderStatus = orders[0]['info']['X']
            orderType = orders[0]['info']['o']
            orderId = int(orders[0]['info']['i'])
            amount = orders[0]['info']['q']
            side = orders[0]['info']['S']
            price = float(orders[0]['info']['p'])
            lastExecutedPrice = float(orders[0]['info']['L'])
            timestamp = int(orders[0]['info']['T'])
            symbol = orders[0]['info']['s']

            if (currentExecutionType == 'NEW') and (currentOrderStatus == 'NEW'):
                if type != 'MARKET':
                    cancel = 0
                    now = datetime.now()
                    now = now.timestamp()
                    print('[' + ('{:.4f}'.format(now)) + ']' + '    NEW ORDER: ORDER ID: ' + str(
                        orderId) + ' PRICE: ' + (
                              '{:.4f}'.format(price)) + ' SIDE: ' + side)
                    # Construcción de la grilla en una lista con todos los elementos que estan activos unicamente
                    temporal = []
                    temporal.extend([n, orderId, price, side])
                    grilla.append(temporal)
                    n = n + 1
                    grilla = sorting_list(grilla)

            if currentExecutionType == 'TRADE' and currentOrderStatus == 'FILLED':
                if type != 'MARKET':
                    #                     commission_amount = json_reply['o']['n']
                    #                     commision_asset = json_reply['o']['N']
                    #                     last_executed_quantity = json_reply['o']['l']
                    #                     cumulative_filled_quantity = json_reply['o']['z']
                    match = order_match(orderId)  # esto puede suprimirse por if sell and if buy
                    side = grilla[match - 1][3]

                    now = datetime.now()
                    now = now.timestamp()
                    trades = trades + 1

                    print(
                        '[' + ('{:.4f}'.format(now)) + ']' + ' ORDER FILLED: ORDER ID: ' + str(orderId) + ' PRICE: ' + (
                            '{:.4f}'.format(price)) + ' SIDE: ' + side)
                    if balance != None:
                        print('[' + ('{:.4f}'.format(now)) + ']' + ' BALANCE: ' + str(abs(balance)) + ' TRADES: ' + str(
                            trades) + " ON " + side)

                    if side == 'BUY' and filled == 0:
                        border = grilla[0][2]
                        price = border - threshold
                        grilla.pop(match - 1)
                        grilla = sorting_list(grilla)
                        print('[' + ('{:.4f}'.format(now)) + ']' + ' ENTRADA A LA GRILLA: ' + (
                            '{:.4f}'.format(price)) + ' ON ' + side)
                        pools.apply_async(puts, (gsymbol, side, amount, price, ex), )

                    if side == 'SELL' and filled == 0:
                        border = grilla[steps - 1][2]
                        price = border + threshold
                        grilla.pop(match - 1)
                        grilla = sorting_list(grilla)
                        print('[' + ('{:.4f}'.format(now)) + ']' + ' ENTRADA A LA GRILLA: ' + (
                            '{:.4f}'.format(price)) + ' ON ' + side)
                        pools.apply_async(puts, (gsymbol, side, gamount, price, ex), )

                    # aqui termina la parte donde inicia la grilla desde cero y comienza la parte donde la grilla trabaja hasta el fin

                    if side == 'BUY' and filled == 1:
                        order_to_cancel = grilla[-1][1]
                        grilla.pop(match-1)
                        grilla = sorting_list(grilla)

                        if balance == 0:
                            cancel = 1
                            filled = 0
                            trades = 0
                            # esto ha de ser asi si voy a detener la grilla cuando cierre
                            ex.cancel_all_orders(symbol)
                            grilla.clear()
                        else:
                            cancel = 0
                            sell_value = float(price) + threshold
                            buy_value = grilla[0][2] - threshold
                            grilla.pop(-1)
                            grilla = sorting_list(grilla)
                            pools.apply_async(puts, (gsymbol, 'SELL', gamount, sell_value, ex), )
                            pools.apply_async(puts, (gsymbol, 'BUY', gamount, buy_value, ex), )
                            pools.apply_async(cancelorder, (order_to_cancel, gsymbol, ex), )

                    if side == 'SELL' and filled == 1:
                        order_to_cancel = grilla[0][1]
                        grilla.pop(match - 1)
                        grilla = sorting_list(grilla)

                        if balance == 0:
                            cancel = 1
                            filled = 0
                            trades = 0
                            # esto ha de ser asi si voy a detener la grilla cuando cierre
                            ex.cancel_all_orders(symbol)
                            grilla.clear()

                        else:
                            cancel = 0
                            buy_value = float(price) - threshold
                            sell_value = grilla[-1][2] + threshold
                            grilla.pop(0)
                            grilla = sorting_list(grilla)
                            pools.apply_async(puts, (gsymbol, 'BUY', gamount, buy_value, ex), )
                            pools.apply_async(puts, (gsymbol, 'SELL', gamount, sell_value, ex), )
                            pools.apply_async(cancelorder, (order_to_cancel, gsymbol, ex), )

                    filled = 1

            if currentOrderStatus == 'CANCELED':
                if type != 'MARKET':
                    match = order_match(orderId)

                    # esta parte tengo que verificarla y todo eso
                    if cancel == 1:
                        oo = exchange.fetch_open_orders(gsymbol)
                        if oo.__len__() == 0:  # aqui verifio si todas las ordenes han sido canceladas

                            time.sleep(1)

                            print('OPERATE...')
                            cancel = 0
                            filled = 0
                            trades = 0



                    if (match == 0):
                        print('[' + ('{:.4f}'.format(now)) + ']' + '    CANCELLED: ORDER ID: ' + str(
                            orderId) + ' PRICE: ' + ('{:.4f}'.format(price)) + ' SIDE: ' + side)
                    else:
                        grilla.pop(match - 1)
                        # yo me imagino que hay que saber que carajos orden (match-1) se murio y ver como carajos van las ordenes nuevas

                        grilla = sorting_list(grilla)


        except Exception as e:
            #print(e)
            raise
            #self.statusbar.showMessage("ERROR {} Fetching WS ORDERS...".format(e))

            # print('wo', orders)
        # print(orders[0])

        # self.logText.append(str(df))
        # self.logText.append('----------------')


def sorting_list(nested_list):
    sorted_list = sorted(nested_list, key=operator.itemgetter(2))
    for i in range(0, len(sorted_list)):
        sorted_list[i][0] = i
    return sorted_list


def order_match(orderId_):
    global grilla
    global steps
    match = 0
    steps = len(grilla)
    for i in range(0, steps):
        if (grilla[i][1] == orderId_):
            match = (i + 1)
    return match
