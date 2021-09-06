import json
import threading
import time
from datetime import datetime

from sockets import positionrisk
import pandas as pd
from utils import pandasModel, message_status
from orderManaging import puts, cancelorder, put_first_order
import orderManaging
import sockets
import gvars

cancel_global = 0

async def worders(self):
    gamount = gvars.amount
    gsymbol = gvars.symbol
    threshold = gvars.threshold
    ex = gvars.ex
    exchange = gvars.exchange

    await exchange.load_markets()
    ex.load_markets()
    filled = await positionrisk(self, exchange, gsymbol)
    market = exchange.market(gsymbol)['id']
    df = pd.DataFrame(
        columns=['internal_status', 's', 'x', 'X', 'p', 'o', 'S', 'i', 'T', 'L', 'n', 'N', 'l', 'z'])
    cancel = 0

    while True:
        if gvars.disconnect == 1:
            await exchange.close()
            print('disconnect from wsorders')
            break
        try:
            jsonx = await exchange.watchOrders()

            if gvars.init == 1:
                cancel = 0
                filled = 0
                df = None
                df = pd.DataFrame(
                    columns=['internal_status', 's', 'x', 'X', 'p', 'o', 'S', 'i', 'T', 'L', 'n', 'N', 'l', 'z'])
                gvars.restart = 0
                gvars.init = 0

            if gvars.restart == 1:
                cancel = 0
                filled = 1
                df = None
                df = pd.DataFrame(
                    columns=['internal_status', 's', 'x', 'X', 'p', 'o', 'S', 'i', 'T', 'L', 'n', 'N', 'l', 'z'])
                gvars.restart = 0

            # if filled == 1 and sockets.balance == 0:
            #     filled = 0
            #     cancel = 0
            #     df = None
            #     df = pd.DataFrame(
            #         columns=['internal_status', 's', 'x', 'X', 'p', 'o', 'S', 'i', 'T', 'L', 'n', 'N', 'l', 'z'])
            #     time.sleep(1)
            #     order_data = {'factor': gvars.factor, 'threshold': gvars.threshold, 'symbol': gvars.symbol,
            #                   'steps': gvars.steps, 'amount': gvars.amount, 'ticker': sockets.price_ticker,
            #                   'center': None}
            #     nt = threading.Thread(target=orderManaging.h, args=(order_data))
            #     nt.start()
            #


            currentExecutionType = jsonx[0]['info']['x']
            currentOrderStatus = jsonx[0]['info']['X']
            orderType = jsonx[0]['info']['o']
            orderId = int(jsonx[0]['info']['i'])
            side = jsonx[0]['info']['S']
            price = float(jsonx[0]['info']['p'])
            # lastExecutedPrice = float(jsonx[0]['info']['L'])
            timestamp = int(jsonx[0]['info']['T'])

            if currentExecutionType == 'NEW' and currentOrderStatus == 'NEW':
                if type != 'MARKET':
                    cancel = 0

                    # print('New Order')
                    # print('ORDER ID ', orderId)
                    # print('PRICE : ', price)
                    # print('SIDE : ', side)
                    # print('-------------------')
                    r = df.loc[df['i'] == orderId]
                    if r.__len__() > 0:
                        print('order found not for save...')
                    else:
                        df = df.append(
                            {'grid_id': 0, 'internal_status': 0, 's': gsymbol, 'x': currentExecutionType,
                             'X': currentOrderStatus, 'p': price,
                             'o': orderType, 'S': side, 'i': orderId, 'T': timestamp, 'L': '', 'n': '', 'N': '',
                             'l': '', 'z': ''}, ignore_index=True)

            if currentExecutionType == 'TRADE' and currentOrderStatus == 'FILLED':
                if type != 'MARKET':
                    # commissionAmount = jsonx['o']['n']
                    # commisionAsset = jsonx['o']['N']
                    # lastExecutedQuantity = jsonx['o']['l']
                    # cumulativeFilledQuantity = jsonx['o']['z']

                    r = df.loc[df['i'] == orderId]
                    # se revienta si el dataframe está vacío
                    df.at[r.index[0], 'grid_id'] = 0
                    df.at[r.index[0], 'L'] = float(jsonx[0]['info']['L'])
                    # df.at[r.index[0], 'n'] = commissionAmount
                    # df.at[r.index[0], 'N'] = commisionAsset
                    # df.at[r.index[0], 'l'] = lastExecutedQuantity
                    # df.at[r.index[0], 'z'] = cumulativeFilledQuantity
                    df.at[r.index[0], 'x'] = currentExecutionType
                    df.at[r.index[0], 'X'] = currentOrderStatus
                    df.at[r.index[0], 'internal_status'] = 1
                    df.at[r.index[0], 'T'] = timestamp
                    df.at[r.index[0], 'i'] = orderId
                    print('*  A UPDATED ', side, 'FROM NEW A FILLED ID:    *', orderId)

                    if side == 'BUY' and filled == 0:
                        t = None
                        count = 0
                        print('-------------------')
                        print('BUY TRADE FILLED ON ZERO')
                        buycero = df.loc[(df['internal_status'] == 0) & (df['S'] == 'BUY')]
                        buycero.sort_values('p', inplace=True, ascending=True)
                        priceb = float(df.iloc[buycero.index[0]]['p']) - threshold
                        # print('MORE LOW BUY ORDER PRICE: ', df.iloc[buycero.index[0]]['p'])
                        # print('MAKING BUY ORDER AT PRICE  ', price)
                        t = threading.Thread(target=puts, args=(gsymbol, 'BUY', gamount, priceb))
                        t.start()
                        # task_puto.delay(api_key, api_id, symbol, 'LIMIT', 'BUY', amount, price, e)

                        print('-------------------')

                    if side == 'SELL' and filled == 0:
                        t = None
                        count = 0
                        print('-------------------')
                        print('SELL TRADE FILLED ON ZERO')
                        sellcero = df.loc[(df['internal_status'] == 0) & (df['S'] == 'SELL')]
                        sellcero.sort_values('p', inplace=True, ascending=False)
                        prices = float(df.iloc[sellcero.index[0]]['p']) + threshold
                        # print('MORE HIGH SELL ORDER PRICE: ', df.iloc[sellcero.index[0]]['p'])
                        # print('MAKING SELL ORDER AT PRICE  ', price)
                        t = threading.Thread(target=puts, args=(gsymbol, 'SELL', gamount, prices))
                        t.start()
                        # task_puto.delay(api_key, api_id, symbol, 'LIMIT', 'SELL', amount, price, e)
                        print('-------------------')

                    if side == 'BUY' and filled == 1:
                        if type != 'MARKET':

                            print('THERE HAS BEEN A BUY')
                            print('ORDER ID:  ', orderId)
                            print('BALANCE  ', sockets.balance)
                            # print('TRADES  ', trades)
                            if sockets.balance == 0:
                                cancel = 1
                                filled = 0
                                cancel = 0
                                df = None
                                df = pd.DataFrame(
                                    columns=['internal_status', 's', 'x', 'X', 'p', 'o', 'S', 'i', 'T', 'L', 'n',
                                             'N', 'l', 'z'])
                                time.sleep(2)
                                order_data = {'factor': gvars.factor, 'threshold': gvars.threshold,
                                              'symbol': gvars.symbol,
                                              'steps': gvars.steps, 'amount': gvars.amount,
                                              'ticker': sockets.price_ticker,
                                              'center': None}
                                nt = threading.Thread(target=orderManaging.h, args=(order_data))
                                nt.start()


                                # trades = trades + 1
                                n = datetime.now()
                                # print(geen)
                                # done = str(n.strftime("%b - %d - %Y %H:%M:%S"))
                                # print("***********************************************************")
                                print("GRID FINISHED IN BUY ")
                                # print("GRID START IN {0} ".format(
                                #     str(grid_start_time)))
                                # print("GRID STOP IN  {0} ".format(done))
                                # print("TRADES = {0} ".format(trades))
                                # print("INITIAL BALANCE = {0} ".format(initial_balance))
                                # print("***********************************************************")
                                # print(res)
                                # # dataframe_end_time = str(n.strftime("%b_%d_%Y_%H_%M"))
                                # df = df[df['x'] != 'CANCELED']
                                # # task_dataframe_to_csv(df, str(dataframe_start_time), str(dataframe_end_time))
                                # task_cancelallorders(api_key, api_id, symbol)
                                # cancel = 1
                                # filled = 0
                                # trades = 0
                                # print(res)
                            else:
                                t = None
                                cancel = 0

                                p = float(price) + threshold
                                now = datetime.now()

                                n = now.strftime("%H:%M:%S")
                                print('[' + n + '] MAKING SELL ORDER  ON CENTER:  ', float(p))
                                t = threading.Thread(target=puts, args=(gsymbol, 'SELL', gamount, float(p)))
                                t.start()

                                # task_puto.delay(api_key, api_id, symbol, 'LIMIT', 'SELL', float(amount), float(p))
                                cbuy = df.loc[(df['internal_status'] == 0) & (df['S'] == 'SELL')]
                                cbuy.sort_values('p', inplace=True, ascending=False)
                                oid = df.iloc[cbuy.index[0]]['i']
                                print('[' + n + ']  CANCELING THE LAST SELL ORDER : ', oid)

                                # e = 1
                                # task_cancelorder.delay(api_key, api_id, oid, symbol)
                                # e = 0
                                puto = df.loc[(df['internal_status'] == 0) & (df['S'] == 'BUY')]
                                puto.sort_values('p', inplace=True, ascending=True)
                                pricefb = float(df.iloc[puto.index[0]]['p']) - threshold

                                print('[' + n + ']' + 'PUT BUY ORDER AT BOTTOM  ', p)
                                t = threading.Thread(target=puts, args=(gsymbol, 'BUY', gamount, pricefb))
                                t.start()
                                # task_puto.delay(api_key, api_id, symbol, 'LIMIT', 'BUY', amount, price, e)

                                # PONER UN SELL  (BUY + Tthreshold) y borrar el primer sell

                    if side == 'SELL' and filled == 1:
                        if type != 'MARKET':
                            print('THERE AS BEEN A SELL ')
                            print('ORDER ID:  ', orderId)
                            print('BALANCE    ', sockets.balance)

                            if sockets.balance == 0:
                                cancel = 1
                                cancel = 1
                                filled = 0
                                cancel = 0
                                df = None
                                df = pd.DataFrame(
                                    columns=['internal_status', 's', 'x', 'X', 'p', 'o', 'S', 'i', 'T', 'L', 'n',
                                             'N', 'l', 'z'])
                                time.sleep(2)
                                order_data = {'factor': gvars.factor, 'threshold': gvars.threshold,
                                              'symbol': gvars.symbol,
                                              'steps': gvars.steps, 'amount': gvars.amount,
                                              'ticker': sockets.price_ticker,
                                              'center': None}
                                nt = threading.Thread(target=orderManaging.h, args=(order_data))
                                nt.start()
                                # trades = trades + 1
                                # n = datetime.now()
                                # done = str(n.strftime("%b - %d - %Y %H:%M:%S"))
                                print("***********************************************************")
                                print("GRID FINISHED IN SELL")
                                # print("GRID START IN {0}".format(str(grid_start_time)))
                                # print("GRID STOP IN  {0}".format(done))
                                # print("TRADES = {0}".format(trades))
                                # print("***********************************************************")
                                # print(res)
                                # dataframe_end_time = str(n.strftime("%b_%d_%Y_%H_%M"))
                                # df = df[df['x'] != 'CANCELED']
                                # # task_dataframe_to_csv(df, str(dataframe_start_time), str(dataframe_end_time))
                                # task_cancelallorders(api_key, api_id, symbol)
                                # cancel = 1
                                # filled = 0
                                # trades = 0

                            else:
                                t = None
                                cancel = 0
                                p = float(price) - threshold
                                now = datetime.now()
                                n = now.strftime("%H:%M:%S")
                                print('[' + n + ']' + ' MAKING BUY ORDER ON CENTER:  ', float(p))
                                t = threading.Thread(target=puts, args=(gsymbol, 'BUY', gamount, p))
                                t.start()
                                # task_puto.delay(api_key, api_id, symbol, 'LIMIT', 'BUY', amount, p)
                                csell = df.loc[(df['internal_status'] == 0) & (df['S'] == 'BUY')]
                                csell.sort_values('p', inplace=True, ascending=True)
                                # print(csell)
                                oid = df.iloc[csell.index[0]]['i']
                                print('[' + n + ']' + 'CANCEL BUY ORDER AT BOTTOM: ', oid)

                                # e = 1
                                # task_cancelorder.delay(api_key, api_id, oid, symbol)
                                # e = 0
                                puto = df.loc[(df['internal_status'] == 0) & (df['S'] == 'SELL')]
                                puto.sort_values('p', inplace=True, ascending=False)
                                price = float(df.iloc[puto.index[0]]['p']) + threshold
                                # exchange.create_order(symbol, 'LIMIT', 'SELL', amount, p)
                                n = now.strftime("%H:%M:%S")

                                print('[' + n + ']' + 'PUT SELL ORDER  AT TOP  ', p)

                                t = threading.Thread(target=puts, args=(gsymbol, 'SELL', gamount, price))
                                t.start()
                                # task_puto.delay(api_key, api_id, symbol, 'LIMIT', 'SELL', amount, price, e)

                                # PONER UN BUY  (SELL - Tthreshold) y borrar el ultimo buy

                    filled = 1

            if currentExecutionType == 'CANCELED':

                if type != 'MARKET':
                    # r = df.loc[df['i'] == order_id]
                    if cancel == 1:
                        pass
                        oo = exchange.fetch_open_orders(gsymbol)
                        if oo.__len__() == 0:
                            df.drop(df.index, inplace=True)

                            cancel = 0
                            filled = 0


                    r = df.loc[df['i'] == orderId]
                    if r.__len__() > 0:
                        print('NO order for cancell ')
                    else:
                        now = datetime.now()
                        now = now.strftime("%H:%M:%S")
                        print('-------------------')
                        print('[' + now + ']' + 'cancelling order...')
                        print('Order id: ', orderId)
                        print('-------------------')
                    try:
                        df.at[r.index[0], 'grid_id'] = 0

                        # df.at[r.index[0], 'L'] = lastExecutedPrice
                        # df.at[r.index[0], 'n'] = commissionAmount
                        df.at[r.index[0], 's'] = gsymbol
                        # df.at[r.index[0], 'N'] = commisionAsset
                        # df.at[r.index[0], 'l'] = lastExecutedQuantity
                        # df.at[r.index[0], 'z'] = cumulativeFilledQuantity
                        df.at[r.index[0], 'x'] = currentExecutionType
                        df.at[r.index[0], 'X'] = currentOrderStatus
                        df.at[r.index[0], 'internal_status'] = 5
                        df.at[r.index[0], 'T'] = timestamp
                        df.at[r.index[0], 'i'] = orderId
                        df.at[r.index[0], 'p'] = float(price)
                    except Exception as e:
                        print('EN SOCKETS CANCELL, ', e)
                    finally:
                        pass

            self.orderTable.setModel(pandasModel(df))

            # pools.apply_async(sockets.pplm, (self, gsymbol, ex), )
        except Exception as e:
            print(e)
            self.statusbar.showMessage("ERROR {} Fetching WS ORDERS...".format(e))
        finally:
            pass
            # print('wo', orders)
        # print(orders[0])

        # self.logText.append(str(df))
        # self.logText.append('----------------')

    return
