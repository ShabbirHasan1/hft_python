from datetime import datetime

from sockets import positionrisk, pplm
import pandas as pd

from utils import pandasModel, message_status
from orderManaging import puts, cancelorder
import threading
from multiprocessing import Pool


async def worders(self, exchange, gamount, threshold, gsymbol, factor, ex):
    pools = Pool(processes=4)
    filled = 0
    await exchange.load_markets()
    ex.load_markets()
    filled = await positionrisk(self, exchange, gsymbol)

    df = pd.DataFrame(
        columns=['internal_status', 'symbol', 'cET', 'cOS', 'price', 'type', 'side', 'order_id', 'timestamp', 'L',
                 'n', 'N', 'l', 'z'])

    while True:
        try:
            orders = await exchange.watchOrders()
            self.statusbar.showMessage("Fetching WS ORDERS...")

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

            if orderType != 'MARKET':
                if currentExecutionType == 'NEW' and currentOrderStatus == 'NEW':
                    r = df.loc[df['order_id'] == orderId]
                    if r.__len__() > 0:
                        print('order found not for save...')
                    else:
                        try:
                            df = df.append(
                                {'internal_status': 0, 'symbol': gsymbol, 'cET': currentExecutionType,
                                 'cOS': currentOrderStatus, 'price': price,
                                 'type': orderType, 'side': side, 'order_id': orderId, 'timestamp': timestamp, 'L': '',
                                 'n': '',
                                 'N': '',
                                 'l': '', 'z': ''}, ignore_index=True)
                        except Exception as e:
                            print('peo en NEW NEW: ', e)

                        # self.orderTable.sortItems(4, Qt.DescendingOrder)

            if currentExecutionType == 'TRADE' and currentOrderStatus == 'FILLED':
                if orderType != 'MARKET':
                    try:
                        commissionAmount = orders[0]['info']['n']
                        commisionAsset = orders[0]['info']['N']
                        lastExecutedQuantity = orders[0]['info']['l']
                        cumulativeFilledQuantity = orders[0]['info']['z']

                        r = df.loc[df['order_id'] == orderId]
                        # se revienta si el dataframe está vacío
                        df.at[r.index[0], 'L'] = lastExecutedPrice
                        df.at[r.index[0], 'n'] = commissionAmount
                        df.at[r.index[0], 'N'] = commisionAsset
                        df.at[r.index[0], 'l'] = lastExecutedQuantity
                        df.at[r.index[0], 'z'] = cumulativeFilledQuantity
                        df.at[r.index[0], 'cET'] = currentExecutionType
                        df.at[r.index[0], 'cOS'] = currentOrderStatus
                        df.at[r.index[0], 'internal_status'] = 1
                        df.at[r.index[0], 'timestamp'] = timestamp
                        df.at[r.index[0], 'order_id'] = orderId
                    except Exception as e:
                        print('peo en TRADE FILED: ', e)

                    if side == 'BUY' and filled == 0:
                        count = 0
                        buycero = df.loc[(df['internal_status'] == 0) & (df['side'] == 'BUY')]
                        buycero.sort_values('price', inplace=True, ascending=True)
                        price = float(df.iloc[buycero.index[0]]['price']) - threshold
                        pools.apply_async(puts, (gsymbol, 'BUY', gamount, price, ex), )

                    if side == 'SELL' and filled == 0:
                        count = 0
                        sellcero = df.loc[(df['internal_status'] == 0) & (df['side'] == 'SELL')]
                        sellcero.sort_values('price', inplace=True, ascending=False)
                        price = float(df.iloc[sellcero.index[0]]['price']) + threshold
                        pools.apply_async(puts, (gsymbol, 'SELL', gamount, price, ex), )

                    #     ***********************************

                    if side == 'BUY' and filled == 1:
                        p = float(price) + threshold
                        pools.apply_async(puts, (gsymbol, 'SELL', gamount, p, ex), )

                        cbuy = df.loc[(df['internal_status'] == 0) & (df['side'] == 'SELL')]
                        cbuy.sort_values('price', inplace=True, ascending=False)
                        oid = df.iloc[cbuy.index[0]]['order_id']
                        print('mandé a cancelar en buy ', oid)
                        pools.apply_async(cancelorder, (oid, gsymbol, ex), )
                        # task_cancelorder.delay(api_key, api_id, oid, symbol)

                        puto = df.loc[(df['internal_status'] == 0) & (df['side'] == 'BUY')]
                        puto.sort_values('price', inplace=True, ascending=True)
                        price = float(df.iloc[puto.index[0]]['price']) - threshold
                        pools.apply_async(puts, (gsymbol, 'BUY', gamount, price, ex), )

                    if side == 'SELL' and filled == 1:
                        p = float(price) - threshold
                        pools.apply_async(puts, (gsymbol, 'BUY', gamount, p, ex), )

                        csell = df.loc[(df['internal_status'] == 0) & (df['side'] == 'BUY')]
                        csell.sort_values('price', inplace=True, ascending=True)
                        oid = df.iloc[csell.index[0]]['order_id']
                        print('mandé a cancelar en sell ', oid)
                        pools.apply_async(cancelorder, (oid, gsymbol, ex), )
                        # task_cancelorder.delay(api_key, api_id, oid, symbol)

                        puto = df.loc[(df['internal_status'] == 0) & (df['side'] == 'SELL')]
                        puto.sort_values('price', inplace=True, ascending=False)
                        price = float(df.iloc[puto.index[0]]['price']) + threshold
                        pools.apply_async(puts, (gsymbol, 'SELL', gamount, price, ex), )

                        # task_puto.delay(api_key, api_id, symbol, 'LIMIT', 'SELL', amount, price, e)

                    filled = 1

            if currentExecutionType == 'CANCELED':
                if orderType != 'MARKET':
                    r = df.loc[df['order_id'] == orderId]
                    print(r)
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
                        # df.at[r.index[0], 'grid_id'] = grid_id

                        # df.at[r.index[0], 'L'] = lastExecutedPrice
                        # df.at[r.index[0], 'n'] = commissionAmount
                        # df.at[r.index[0], 'symbol'] = symbol
                        # df.at[r.index[0], 'N'] = commisionAsset
                        # df.at[r.index[0], 'l'] = lastExecutedQuantity
                        # df.at[r.index[0], 'z'] = cumulativeFilledQuantity
                        df.at[r.index[0], 'cET'] = currentExecutionType
                        df.at[r.index[0], 'cOS'] = currentOrderStatus
                        df.at[r.index[0], 'internal_status'] = 5
                        df.at[r.index[0], 'timestamp'] = timestamp
                        # df.at[r.index[0], 'order_id'] = orderId

                    except Exception as e:
                        print("peo EN CANCELED '{}' ".format(e))
            self.orderTable.setModel(pandasModel(df))

            # pools.apply_async(pplm, (self, gsymbol, ex), )



        except Exception as e:
            print(e)
            self.statusbar.showMessage("ERROR {} Fetching WS ORDERS...".format(e))
        finally:
            pass
            # print('wo', orders)
        # print(orders[0])

        # self.logText.append(str(df))
        # self.logText.append('----------------')
