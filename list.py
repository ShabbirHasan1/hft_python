import operator

import asyncio

from readConf import readgrids

import ccxt
import ccxtpro

#
grids = readgrids()

loop = asyncio.get_event_loop()
#
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
# exchange.set_sandbox_mode(True)


flag = 0
grilla = []


def sorting_list(nested_list):
    sorted_list = sorted(nested_list, key=operator.itemgetter(2))
    for i in range(0, len(sorted_list)):
        sorted_list[i][0] = i
    return sorted_list


def cancel_order(symbol_, order_id_, exchange_):
    e = exchange_.cancel_order(order_id_, grids[0][12])
    status = e['info']['status']


async def order_list():
    grid = []
    n = 0
    orders_ = await exchange.fetch_open_orders(grids[0][12])
    for i in orders_:
        temporal = []
        temporal.extend([n, i['id'], i['price'], i['side'].upper()])
        grid.append(temporal)
        n += 1
    grid = sorting_list(grid)
    return grid


def order_match(order_id_):
    global steps
    match = 0
    steps = len(grilla)
    for i in range(0, steps):
        if (grilla[i][1] == order_id_):
            match = (i + 1)
    return match


async def main(loop):
    threshold = grids[0][4]
    stepsbyside = int(grids[0][6] / 2)
    grilla = []
    # await pplm(self, grids[0][12], exchange)
    await exchange.load_markets()

    grilla = await order_list()
    # grilla_size = len(grilla)
    # print (grilla_size)
    #
    # eliminar = []
    # if grilla_size != 0:
    #     for n in range(grilla_size - 1):
    #         if (grilla[n][2]) == (grilla[n + 1][2]):
    #             temporal = []
    #             temporal.extend([n, grilla[n][1]])
    #             eliminar.append(temporal)
    #
    # if len(eliminar) != 0:
    #     print("No orders")
    #     print("DELETING ", eliminar)
    #     print("DROP ", len(eliminar), "ORDERS")
    #
    # # elimino las ordenes que están en la lista "eliminar"
    # if (len(eliminar)) != 0:
    #     for n in range(len(eliminar)):
    #         print("Trying to drop", (eliminar[n][0]), (eliminar[n][1]))
    #         o = await exchange.cancel_order(eliminar[n][1], grids[0][12])
    #         print(o)
    #
    #         # Actualizo la lista, luego de haber eliminado las ordenes en el exchange
    # # esto tal vez se pueda poner en el lazo anterior
    # if (len(eliminar)) != 0:
    #     for n in range(len(eliminar)):
    #         match = order_match(eliminar[n][1])
    #         grilla.pop(match - 1)
    #         grilla = sorting_list(grilla)
    #
    #
    #
    #
    # grillau = [[0, '2754718063', 49163.48, 'BUY'], [1, '2754718047', 49263.48, 'BUY'], [2, '2754718045', 49363.48, 'BUY'], [3, '2754718049', 49463.48, 'BUY'], [4, '2754718053', 49663.48, 'SELL'], [5, '2754718050', 49763.48, 'SELL'], [6, '2754718048', 49963.48, 'SELL']]

    # print(grillau)
    sorted_list = sorted(grilla, key=operator.itemgetter(2), reverse=True)
    selllist = []
    buylist = []
    countbuy = 0
    countsell = 0
    print('STEPS By ', stepsbyside)
    for i in range(len(sorted_list)):
        # print(sorted_list)
        if sorted_list[i][3:][0] == 'SELL':
            selllist.append(sorted_list[i])
            countsell += 1
            # print(sorted_list[i])
        if sorted_list[i][3:][0] == 'BUY':
            buylist.append(sorted_list[i])
            countbuy += 1
            # print(sorted_list[i])
    #
    # if len(selllist) == stepsbyside:
    #     pass
    # else:
    #
    #     print('countsell is bad')
    #     if len(selllist) > stepsbyside:
    #         print('selllist is >')
    #         todrop = len(selllist) - stepsbyside
    #         for i in range(0, todrop):
    #             await exchange.cancel_order(selllist[i][1], grids[0][12])
    #             print(selllist[i][1])
    #
    #
    #
    #     if len(selllist) < stepsbyside:
    #         print('selllist is <')
    #         x = 0
    #         temp = None
    #         first = None
    #         first = selllist[len(selllist) - 1][2]
    #         for i in range(0, stepsbyside):
    #             if x == 0:
    #                 temp = first
    #                 x = 1
    #             else:
    #                 temp = temp + threshold
    #             res = any(temp in sub for sub in selllist)
    #             if not res:
    #                 await exchange.create_order(grids[0][12], 'LIMIT', 'SELL', 0.012, temp)
    #                 print(temp, res)
    #
    # if len(buylist) == stepsbyside:
    #     pass
    # else:
    #     print('countbuy is bad')
    #     if len(buylist) > stepsbyside:
    #         todrop = len(buylist) - stepsbyside
    #         print(todrop)
    #         print(buylist)
    #         buylisttmp =  buylist[-todrop:]
    #         for i in range(0, len(buylisttmp) ):
    #             await exchange.cancel_order(buylisttmp[i][1], grids[0][12])
    #
    #     if len(buylist) < stepsbyside:
    #         print('buylist is <')
    #         first = None
    #         x = 0
    #         temp = None
    #         first = buylist[len(buylist) - 1][2]
    #         for i in range(0, stepsbyside):
    #             if x == 0:
    #                 temp = first
    #                 x = 1
    #             else:
    #                 temp = temp + threshold
    #             res = any(temp in sub for sub in buylist)
    #             if not res:
    #                 await exchange.create_order(grids[0][12], 'LIMIT', 'BUY', 0.012, temp)
    #                 print(temp, res)
    #

    minsell = selllist[len(selllist) - 1][2]
    maxbuy = buylist[0][2]
    print('thresahold: ', threshold)
    gap = round(minsell - maxbuy, 2)

    if gap > (threshold * 2):
        print('Min sell order: ', minsell)
        print('Max buy order: ', maxbuy)
        print('GAP: ', gap)

    # GAP

    # st = int(grids[0][6])
    # steps = int(grids[0][6] / 2)
    # threshold = grids[0][4]
    # countbuy = 0
    # countsell = 0
    # selllist = []
    # buylist = []
    #
    # for i in range(len(sorted_list)):
    #     # print(sorted_list)
    #     if sorted_list[i][3:][0] == 'SELL':
    #         countsell += 1
    #         selllist.append(sorted_list[i])
    #         # print(sorted_list[i])
    #     if sorted_list[i][3:][0] == 'BUY':
    #         buylist.append(sorted_list[i])
    #         countbuy += 1
    #         # print(sorted_list[i])
    #
    # # print('countsell ', countsell)
    # # print('countbuy ', countbuy)
    #
    # if not (countsell == countbuy):
    #     print('steps ', steps)
    #     x = 0
    #     temp = None
    #
    # if countbuy == steps:
    #     print('countbuy is fine')
    #     # print(countbuy)
    # else:
    #     print('countbuy is bad')
    #     # print(countbuy)
    #     first = buylist[len(buylist) - 1][2]
    #     x = 0
    #     temp = None
    #     for i in range(0, steps):
    #         if x == 0:
    #             temp = first
    #             x = 1
    #         else:
    #             temp = temp + threshold
    #         res = any(temp in sub for sub in buylist)
    #         print(temp, res)
    #
    # if countsell == steps:
    #     print('countsell is fine')
    #     # print(countsell)
    # else:
    #     print('countsell is bad')
    #     # print(selllist)
    #     first = selllist[len(selllist) - 1][2]
    #     for i in range(0, steps):
    #         if x == 0:
    #             temp = first
    #             x = 1
    #         else:
    #             temp = temp + threshold
    #         res = any(temp in sub for sub in selllist)
    #         if not res:
    #             print(temp, res)

    await exchange.close()


# loop.run_until_complete(main(loop))


x = [
    # [0, 'NEW', 16475745288, '7', 'SELL', 2.9319, 'ADAUSDT'],
    # [1, 'NEW', 16475745461, '7', 'SELL', 2.9219, 'ADAUSDT'],
    # [2, 'NEW', 16475745550, '7', 'SELL', 2.9119, 'ADAUSDT'],
    # [3, 'NEW', 16475745558, '7', 'SELL', 2.9019, 'ADAUSDT'],

    [0, 'NEW', 16475745551, '7', 'BUY', 2.8919, 'ADAUSDT'],
    [1, 'NEW', 16475745560, '7', 'BUY', 2.8819, 'ADAUSDT'],
    [2, 'NEW', 16475745520, '7', 'BUY', 2.8719, 'ADAUSDT'],
    [3, 'NEW', 16475745470, '7', 'BUY', 2.8619, 'ADAUSDT'],
    [4, 'NEW', 16475745585, '7', 'BUY', 2.8519, 'ADAUSDT']
]

# val = 16475439509
# m = [index for index, row in enumerate(x) if val in row][0]
print(x[-1:])



# order_id = jsonx['o']['i']
            # amount = jsonx['o']['q']
            # type = jsonx['o']['o']
            # side = jsonx['o']['S']
            # price = jsonx['o']['p']
            # currentExecutionType = jsonx['o']['x']  # Current execution type
            # currentOrderStatus = jsonx['o']['X']  # Current order status
            # lastExecutedPrice = jsonx['o']['L']
            # timestamp = int(jsonx['o']['T'])

            # new new
            # if currentExecutionType == 'NEW' and currentOrderStatus == 'NEW':
            #     if type != 'MARKET':
            #         cancel = 0
            #         print('-------------------')
            #         print('New Order')
            #         print('ORDER ID ', order_id)
            #         print('PRICE : ', price)
            #         print('SIDE : ', side)
            #         print('-------------------')
            #         r = df.loc[df['i'] == order_id]
            #         if r.__len__() > 0:
            #             print('order found not for save...')
            #         else:
            #             df = df.append(
            #                 {'internal_status': 0, 's': gsymbol, 'x': currentExecutionType,
            #                  'X': currentOrderStatus, 'p': price,
            #                  'o': type, 'S': side, 'i': order_id, 'T': timestamp, 'L': '', 'n': '', 'N': '',
            #                  'l': '', 'z': ''}, ignore_index=True)

                        # print(yellow + 'SAVING NEW ORDER ... ID: ' + str(order_id) + ' ' + str(price) + ' ' + res)
                        # if df.shape[0] == 6:
                        #     print(df)

            # # trade filled **************************************************************************************
            # if jsonx['o']['x'] == 'TRADE' and jsonx['o']['X'] == 'FILLED':
            #     if type != 'MARKET':
            #         commissionAmount = jsonx['o']['n']
            #         commisionAsset = jsonx['o']['N']
            #         lastExecutedQuantity = jsonx['o']['l']
            #         cumulativeFilledQuantity = jsonx['o']['z']
            #
            #         r = df.loc[df['i'] == order_id]
            #         # se revienta si el dataframe está vacío
            #         df.at[r.index[0], 'L'] = lastExecutedPrice
            #         df.at[r.index[0], 'n'] = commissionAmount
            #         df.at[r.index[0], 'N'] = commisionAsset
            #         df.at[r.index[0], 'l'] = lastExecutedQuantity
            #         df.at[r.index[0], 'z'] = cumulativeFilledQuantity
            #         df.at[r.index[0], 'x'] = currentExecutionType
            #         df.at[r.index[0], 'X'] = currentOrderStatus
            #         df.at[r.index[0], 'internal_status'] = 1
            #         df.at[r.index[0], 'T'] = timestamp
            #         df.at[r.index[0], 'i'] = order_id
            #
            #         print('*  A UPDATED ', side, 'FROM NEW A FILLED ID:    *', order_id)

                    # if side == 'BUY' and filled == 0:
                    #     count = 0
                    #     print('-------------------')
                    #     print('BUY TRADE FILLED ON ZERO')
                    #     r = df.loc[df['i'] == order_id]
                    #     buycero = df.loc[(df['internal_status'] == 0) & (df['S'] == 'BUY')]
                    #     buycero.sort_values('p', inplace=True, ascending=True)
                    #     price = float(df.iloc[buycero.index[0]]['p']) - threshold
                    #     print('MORE LOW BUY ORDER PRICE: ', df.iloc[buycero.index[0]]['p'])
                    #     print('MAKING BUY ORDER AT PRICE  ', price)
                    #
                    #     t = threading.Thread(target=puts, args=(gsymbol, 'BUY', gamount, price))
                    #     t.start()
                    #     # task_puto.delay(api_key, api_id, symbol, 'LIMIT', 'BUY', amount, price, e)
                    #
                    # if side == 'SELL' and filled == 0:
                    #     count = 0
                    #     print('-------------------')
                    #     print('SELL TRADE FILLED ON ZERO')
                    #     sellcero = df.loc[(df['internal_status'] == 0) & (df['S'] == 'SELL')]
                    #     sellcero.sort_values('p', inplace=True, ascending=False)
                    #     price = float(df.iloc[sellcero.index[0]]['p']) + threshold
                    #     print('MORE HIGH SELL ORDER PRICE: ', df.iloc[sellcero.index[0]]['p'])
                    #     print('MAKING SELL ORDER AT PRICE  ', price)
                    #     # print('MORE HIGH SELL ORDER PRICE: ', df.iloc[sellcero.index[0]]['p'])
                    #     # print('MAKING SELL ORDER AT PRICE:  ', price)
                    #
                    #     t = threading.Thread(target=puts, args=(gsymbol, 'BUY', gamount, price))
                    #     t.start()
                    #     # task_puto.delay(api_key, api_id, symbol, 'LIMIT', 'SELL', amount, price, e)
                    #
                    #     print('-------------------')

            #         if side == 'BUY' and filled == 1:
            #             if type != 'MARKET':
            #
            #                 print('THERE HAS BEEN A BUY ')
            #                 print('ORDER ID:  ', order_id)
            #                 print('BALANCE  ', sockets.balance)
            #                 # print('TRADES  ', trades)
            #                 if sockets.balance == 0:
            #                     trades = trades + 1
            #                     n = datetime.now()
            #                     done = str(n.strftime("%b - %d - %Y %H:%M:%S"))
            #                     print("***********************************************************")
            #                     print("GRID FINISHED IN BUY ")
            #
            #                     print("GRID STOP IN  {0} ".format(done))
            #                     print("TRADES = {0} ".format(trades))
            #                     # print("INITIAL BALANCE = {0} ".format(initial_balance))
            #                     print("***********************************************************")
            #
            #                     # dataframe_end_time = str(n.strftime("%b_%d_%Y_%H_%M"))
            #                     df = df[df['x'] != 'CANCELED']
            #                     # task_dataframe_to_csv(df, str(dataframe_start_time), str(dataframe_end_time))
            #                     # task_cancelallorders(api_key, api_id, symbol)
            #                     cancel = 1
            #                     filled = 0
            #                     trades = 0
            #                     # print(res)
            #                 else:
            #                     cancel = 0
            #                     trades = trades + 1
            #                     p = float(price) + threshold
            #                     now = datetime.now()
            #                     # print(buycolor)
            #                     n = now.strftime("%H:%M:%S")
            #                     print('[' + n + '] MAKING SELL ORDER  ON CENTER:  ', float(p))
            #                     # print(res)
            #
            #                     t = threading.Thread(target=puts, args=(gsymbol, 'SELL', gamount, float(p)))
            #                     t.start()
            #                     # task_puto.delay(api_key, api_id, symbol, 'LIMIT', 'SELL', float(amount), float(p))
            #                     cbuy = df.loc[(df['internal_status'] == 0) & (df['S'] == 'SELL')]
            #                     cbuy.sort_values('p', inplace=True, ascending=False)
            #                     oid = df.iloc[cbuy.index[0]]['i']
            #                     print('[' + n + ']  CANCELING THE LAST SELL ORDER : ', oid)
            #
            #                     # task_cancelorder.delay(api_key, api_id, oid, symbol)
            #
            #                     puto = df.loc[(df['internal_status'] == 0) & (df['S'] == 'BUY')]
            #                     puto.sort_values('p', inplace=True, ascending=True)
            #                     price = float(df.iloc[puto.index[0]]['p']) - threshold
            #
            #                     print('[' + n + ']' + 'PUT BUY ORDER AT BOTTOM  ', p)
            #
            #                     e = 1
            #                     t = threading.Thread(target=puts, args=(gsymbol, 'BUY', gamount, price))
            #                     t.start()
            #                     # task_puto.delay(api_key, api_id, symbol, 'LIMIT', 'BUY', amount, price, e)
            #                     e = 0
            #                     # PONER UN SELL  (BUY + Tthreshold) y borrar el primer sell
            #
            #         if side == 'SELL' and filled == 1:
            #             if type != 'MARKET':
            #                 print('THERE AS BEEN A SELL ')
            #                 print('ORDER ID:  ', order_id)
            #                 print('BALANCE    ', sockets.balance)
            #                 print('TRADES     ', trades)
            #
            #                 if sockets.balance == 0:
            #                     trades = trades + 1
            #                     n = datetime.now()
            #
            #                     done = str(n.strftime("%b - %d - %Y %H:%M:%S"))
            #                     print("***********************************************************")
            #                     print("GRID FINISHED IN SELL")
            #
            #                     print("GRID STOP IN  {0}".format(done))
            #                     print("TRADES = {0}".format(trades))
            #                     print("***********************************************************")
            #
            #                     dataframe_end_time = str(n.strftime("%b_%d_%Y_%H_%M"))
            #                     df = df[df['x'] != 'CANCELED']
            #                     # task_dataframe_to_csv(df, str(dataframe_start_time), str(dataframe_end_time))
            #                     # task_cancelallorders(api_key, api_id, symbol)
            #                     cancel = 1
            #                     filled = 0
            #                     trades = 0
            #                     # print(res)
            #                 else:
            #                     cancel = 0
            #                     trades = trades + 1
            #                     p = float(price) - threshold
            #                     now = datetime.now()
            #                     n = now.strftime("%H:%M:%S")
            #                     print('[' + n + ']' + ' MAKING BUY ORDER ON CENTER:  ',
            #                           float(p))
            #                     t = threading.Thread(target=puts, args=(gsymbol, 'BUY', gamount, p))
            #                     t.start()
            #                     # task_puto.delay(api_key, api_id, symbol, 'LIMIT', 'BUY', amount, p)
            #                     csell = df.loc[(df['internal_status'] == 0) & (df['S'] == 'BUY')]
            #                     csell.sort_values('p', inplace=True, ascending=True)
            #                     # print(csell)
            #                     oid = df.iloc[csell.index[0]]['i']
            #                     print('[' + n + ']' + 'CANCEL BUY ORDER AT BOTTOM: ', oid)
            #
            #                     e = 1
            #                     # task_cancelorder.delay(api_key, api_id, oid, symbol)
            #                     e = 0
            #                     puto = df.loc[(df['internal_status'] == 0) & (df['S'] == 'SELL')]
            #                     puto.sort_values('p', inplace=True, ascending=False)
            #                     price = float(df.iloc[puto.index[0]]['p']) + threshold
            #                     # exchange.create_order(symbol, 'LIMIT', 'SELL', amount, p)
            #                     n = now.strftime("%H:%M:%S")
            #
            #                     print('[' + n + ']' + 'PUT SELL ORDER  AT TOP  ', p)
            #
            #                     e = 1
            #                     t = threading.Thread(target=puts, args=(gsymbol, 'BUY', gamount, price))
            #                     t.start()
            #                     # task_puto.delay(api_key, api_id, symbol, 'LIMIT', 'SELL', amount, price, e)
            #                     e = 0
            #
            #                     # PONER UN BUY  (SELL - Tthreshold) y borrar el ultimo buy
            #
            #         filled = 1
            #
            # if jsonx['o']['X'] == 'CANCELED':
            #
            #     if type != 'MARKET':
            #         # r = df.loc[df['i'] == order_id]
            #         if cancel == 1:
            #             oo = exchange.fetch_open_orders(gsymbol)
            #             if oo.__len__() == 0:
            #                 df.drop(df.index, inplace=True)
            #                 final_balance = exchange.fetch_balance()
            #                 final_balance = final_balance['USDT']['free']
            #                 # re = final_balance - initial_balance
            #                 # print(geen + "***************************************")
            #                 # print("INITIAL BALANCE = {0}".format(str(initial_balance)))
            #                 # print("FINAL BALANCE = {0}".format(str(final_balance)))
            #                 # print(res)
            #                 # if re > 0:
            #                 #     print(" YOUR PROFIT: ", re)
            #                 # if re < 0:
            #                 #     print(red + "YOUR LOSS: ", re)
            #                 #     print(res)
            #
            #                 # print(geen + "***************************************")
            #                 # print(res)
            #                 df = pd.DataFrame(
            #                     columns=['grid_id', 'internal_status', 's', 'x', 'X', 'p', 'o', 'S', 'i',
            #                              'T', 'L', 'n', 'N', 'l', 'z'])
            #                 # time.sleep(1)
            #                 # print('OPERATE...')
            #                 cancel = 0
            #                 filled = 0
            #                 trades = 0
            #                 # task_operate(nm, 0)
            #
            #         r = df.loc[df['i'] == order_id]
            #         if r.__len__() > 0:
            #             print('NO order for cancell ')
            #         else:
            #             now = datetime.now()
            #             now = now.strftime("%H:%M:%S")
            #             print('-------------------')
            #             print('[' + now + ']' + 'cancelling order...')
            #             print('Order id: ', order_id)
            #             print('-------------------')
            #         try:
            #
            #             df.at[r.index[0], 'L'] = lastExecutedPrice
            #             # df.at[r.index[0], 'n'] = commissionAmount
            #             df.at[r.index[0], 's'] = gsymbol
            #             # df.at[r.index[0], 'N'] = commisionAsset
            #             # df.at[r.index[0], 'l'] = lastExecutedQuantity
            #             # df.at[r.index[0], 'z'] = cumulativeFilledQuantity
            #             df.at[r.index[0], 'x'] = currentExecutionType
            #             df.at[r.index[0], 'X'] = currentOrderStatus
            #             df.at[r.index[0], 'internal_status'] = 5
            #             df.at[r.index[0], 'T'] = timestamp
            #             df.at[r.index[0], 'i'] = order_id
            #             df.at[r.index[0], 'p'] = float(price)
            #
            #         except Exception as e:
            #             pass
            #         finally:
            #             pass

            # # print( gvars.order_array_buy)
            # # print( gvars.order_array_sell)
            # # print(orders)
            # # print(gvars.order_array)
            #
            # # # print(orders)
            # # # print('price ticker ', sockets.price_ticker)
            # # # print('balance ', sockets.balance)
            # # # self.statusbar.showMessage("Fetching WS ORDERS...")
            # currentExecutionType = orders[0]['info']['x']
            # currentOrderStatus = orders[0]['info']['X']
            # orderType = orders[0]['info']['o']
            # orderId = int(orders[0]['info']['i'])
            # amount = orders[0]['info']['q']
            # side = orders[0]['info']['S']
            # price = float(orders[0]['info']['p'])
            # # lastExecutedPrice = float(orders[0]['info']['L'])
            # # timestamp = int(orders[0]['info']['T'])
            # symbol = orders[0]['info']['s']
            #
            # if orderType != 'MARKET':
            #
            #     if currentExecutionType == 'NEW' and currentOrderStatus == 'NEW':
            #         if side == 'BUY':
            #             grid_buy.append([
            #                 currentExecutionType,
            #                 currentOrderStatus,
            #                 orderId,
            #                 amount,
            #                 side,
            #                 price,
            #                 symbol,
            #             ])
            #             grid_buy = orderManaging.sort_ws_list(grid_buy, True)
            #         if side == 'SELL':
            #             grid_sell.append([
            #                 currentExecutionType,
            #                 currentOrderStatus,
            #                 orderId,
            #                 amount,
            #                 side,
            #                 price,
            #                 symbol])
            #             grid_sell = orderManaging.sort_ws_list(grid_sell, True)
            #
            #     if currentExecutionType == 'TRADE' and currentOrderStatus == 'FILLED':
            #
            #         if side == 'BUY' and filled == 0:
            #             price = gvars.order_array_buy[0][4] - threshold
            #             t = threading.Thread(target=puts, args=(gsymbol, 'BUY', gamount, price))
            #             t.start()
            #
            #         if side == 'SELL' and filled == 0:
            #             price = gvars.order_array_sell[0][4] + threshold
            #             t = threading.Thread(target=puts, args=(gsymbol, 'SELL', gamount, price))
            #             t.start()
            #
            #
            #
            #         if side == 'BUY' and filled == 1:
            #             # arridx = [index for index, row in enumerate(grid_buy) if orderId in row][0]
            #             # grid_buy[arridx][1] = 'FILLED'
            #             print('balance ', sockets.balance)
            #             if sockets.balance == 0:
            #                 pass
            #             else:
            #                 grid_sell = orderManaging.sort_ws_list(grid_sell, True)
            #                 grid_buy = orderManaging.sort_ws_list(grid_buy, True)
            #
            #                 price = grid_sell[-1:][5] - threshold
            #                 t = threading.Thread(target=puts, args=(gsymbol, 'SELL', gamount, price))
            #                 t.start()
            #
            #                 price = grid_buy[-1:][5] - threshold
            #                 t = threading.Thread(target=puts, args=(gsymbol, 'BUY', gamount, price))
            #                 t.start()
            #
            #
            #         if side == 'SELL' and filled == 1:
            #             # arridx = [index for index, row in enumerate(grid_buy) if orderId in row][0]
            #             # grid_buy[arridx][1] = 'FILLED'
            #             print('balance ', sockets.balance)
            #             if sockets.balance == 0:
            #                 pass
            #             else:
            #                 grid_sell = orderManaging.sort_ws_list(grid_sell, True)
            #                 grid_buy = orderManaging.sort_ws_list(grid_buy, True)
            #                 price = grid_buy[0][5] + threshold
            #                 t = threading.Thread(target=puts, args=(gsymbol, 'BUY', gamount, price))
            #                 t.start()
            #
            #                 price = grid_sell[0][5] + threshold
            #                 t = threading.Thread(target=puts, args=(gsymbol, 'SELL', gamount, price))
            #                 t.start()
            #
            #         filled = 1
            #
            #     if currentExecutionType == 'CANCELED':
            #         pass
            #
            # # grid_buy = orderManaging.sort_ws_list(grid_buy, True)
            # # grid_sell = orderManaging.sort_ws_list(grid_sell, True)
            #
            # # for i in range(len(grid_sell)):
            # #     print(grid_sell[i])
            # #
            # # for i in range(len(grid_buy)):
            # #     print(grid_buy[i])
            # print('len sell ', len(grid_sell))
            # print('len buy ', len(grid_buy))

            #
            # # if orderType != 'MARKET':
            # #     # if currentExecutionType == 'NEW' and currentOrderStatus == 'NEW':
            # #     #     r = dataf.loc[dataf['order_id'] == orderId]
            # #     #     if r.__len__() > 0:
            # #     #         print('order found not for save...')
            # #     #     else:
            # #     #         try:
            # #     #             dataf = dataf.append(
            # #     #                 {'internal_status': 0, 'symbol': gsymbol, 'cET': currentExecutionType,
            # #     #                  'cOS': currentOrderStatus, 'price': price,
            # #     #                  'type': orderType, 'side': side, 'order_id': orderId, 'timestamp': timestamp, 'L': '',
            # #     #                  'n': '',
            # #     #                  'N': '',
            # #     #                  'l': '', 'z': ''}, ignore_index=True)
            # #     #         except Exception as e:
            # #     #             print('peo en NEW NEW: ', e)
            # #     #
            # #     #         # self.orderTable.sortItems(4, Qt.DescendingOrder)
            #
            # if currentExecutionType == 'TRADE' and currentOrderStatus == 'FILLED':
            #     if orderType != 'MARKET':
            #         try:
            #             commissionAmount = orders[0]['info']['n']
            #             commisionAsset = orders[0]['info']['N']
            #             lastExecutedQuantity = orders[0]['info']['l']
            #             cumulativeFilledQuantity = orders[0]['info']['z']
            #
            #             r = dataf.loc[dataf['order_id'] == orderId]
            #             # se revienta si el dataframe está vacío
            #             dataf.at[r.index[0], 'L'] = lastExecutedPrice
            #             dataf.at[r.index[0], 'n'] = commissionAmount
            #             dataf.at[r.index[0], 'N'] = commisionAsset
            #             dataf.at[r.index[0], 'l'] = lastExecutedQuantity
            #             dataf.at[r.index[0], 'z'] = cumulativeFilledQuantity
            #             dataf.at[r.index[0], 'cET'] = currentExecutionType
            #             dataf.at[r.index[0], 'cOS'] = currentOrderStatus
            #             dataf.at[r.index[0], 'internal_status'] = 1
            #             dataf.at[r.index[0], 'timestamp'] = timestamp
            #             dataf.at[r.index[0], 'order_id'] = orderId
            #         except Exception as e:
            #             print('peo en TRADE FILED: ', e)
            #
            #         if side == 'BUY' and filled == 0:
            #             count = 0
            #             # buycero = dataf.loc[(df['internal_status'] == 0) & (df['side'] == 'BUY')]
            #             # buycero.sort_values('price', inplace=True, ascending=True)
            #             # price = float(dataf.iloc[buycero.index[0]]['price']) - threshold
            #             pools.apply_async(put_first_order, (gsymbol, 'BUY', gamount, threshold, dataf, ex), )
            #             # pools.apply_async(puts, (gsymbol, 'BUY', gamount, price, ex), )
            #
            #         if side == 'SELL' and filled == 0:
            #             count = 0
            #             # sellcero = dataf.loc[(df['internal_status'] == 0) & (df['side'] == 'SELL')]
            #             # sellcero.sort_values('price', inplace=True, ascending=False)
            #             # price = float(dataf.iloc[sellcero.index[0]]['price']) + threshold
            #             pools.apply_async(put_first_order, (gsymbol, 'SELL', gamount, threshold, dataf, ex), )
            #             # pools.apply_async(puts, (gsymbol, 'SELL', gamount, price, ex), )
            #
            #         #     ***********************************
            #
            #         if side == 'BUY' and filled == 1:
            #             p = float(price) + threshold
            #             pools.apply_async(puts, (gsymbol, 'SELL', gamount, p, ex), )
            #
            #             # cbuy = dataf.loc[(dataf['internal_status'] == 0) & (dataf['side'] == 'SELL')]
            #             # cbuy.sort_values('price', inplace=True, ascending=False)
            #             # oid = dataf.iloc[cbuy.index[0]]['order_id']
            #             # print('mandé a cancelar en buy ', oid)
            #             #
            #             # pools.apply_async(cancelorder, (oid, gsymbol, ex), )
            #             # # task_cancelorder.delay(api_key, api_id, oid, symbol)
            #             #
            #             # puto = dataf.loc[(dataf['internal_status'] == 0) & (dataf['side'] == 'BUY')]
            #             # puto.sort_values('price', inplace=True, ascending=True)
            #             # price = float(dataf.iloc[puto.index[0]]['price']) - threshold
            #             # pools.apply_async(puts, (gsymbol, 'BUY', gamount, price, ex), )
            #
            #         if side == 'SELL' and filled == 1:
            #             p = float(price) - threshold
            #             pools.apply_async(puts, (gsymbol, 'BUY', gamount, p, ex), )
            #
            #             # csell = dataf.loc[(dataf['internal_status'] == 0) & (dataf['side'] == 'BUY')]
            #             # csell.sort_values('price', inplace=True, ascending=True)
            #             # oid = dataf.iloc[csell.index[0]]['order_id']
            #             # print('mandé a cancelar en sell ', oid)
            #             # pools.apply_async(cancelorder, (oid, gsymbol, ex), )
            #             # # task_cancelorder.delay(api_key, api_id, oid, symbol)
            #             #
            #             # puto = dataf.loc[(dataf['internal_status'] == 0) & (dataf['side'] == 'SELL')]
            #             # puto.sort_values('price', inplace=True, ascending=False)
            #             # price = float(dataf.iloc[puto.index[0]]['price']) + threshold
            #             # pools.apply_async(puts, (gsymbol, 'SELL', gamount, price, ex), )
            #
            #             # task_puto.delay(api_key, api_id, symbol, 'LIMIT', 'SELL', amount, price, e)
            #
            #         filled = 1
            #
            # if currentExecutionType == 'CANCELED':
            #     if orderType != 'MARKET':
            #         r = dataf.loc[dataf['order_id'] == orderId]
            #         # print(r)
            #         if r.__len__() > 0:
            #             print('NO order for cancell ')
            #         else:
            #             now = datetime.now()
            #             now = now.strftime("%H:%M:%S")
            #             print('-------------------')
            #             print('[' + now + ']' + 'cancelling order...')
            #             print('Order id: ', orderId)
            #             print('-------------------')
            #         try:
            #             dataf.at[r.index[0], 'cET'] = currentExecutionType
            #             dataf.at[r.index[0], 'cOS'] = currentOrderStatus
            #             dataf.at[r.index[0], 'internal_status'] = 5
            #             dataf.at[r.index[0], 'timestamp'] = timestamp
            #
            #         except Exception as e:
            #             print("peo EN CANCELED '{}' ".format(e))
            # self.orderTable.setModel(pandasModel(dataf))

            # pools.apply_async(pplm, (self, gsymbol, ex), )

