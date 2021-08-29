from sockets import positionrisk
import pandas as pd

from utils import pandasModel, message_status
from orderManaging import puts, cancelorder
import threading
from multiprocessing import Pool

async def worders(self, exchange, gamount, threshold, gsymbol, factor, ex):
    pools = Pool(processes=2)
    filled = 0
    await exchange.load_markets()
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

            if currentExecutionType == 'NEW' and currentOrderStatus == 'NEW':
                r = df.loc[df['order_id'] == orderId]
                if r.__len__() > 0:
                    print('order found not for save...')
                else:

                    df = df.append(
                        {'internal_status': 0, 'symbol': symbol, 'cET': currentExecutionType,
                         'cOS': currentOrderStatus, 'price': price,
                         'type': orderType, 'side': side, 'order_id': orderId, 'timestamp': timestamp, 'L': '', 'n': '',
                         'N': '',
                         'l': '', 'z': ''}, ignore_index=True)


                    # self.orderTable.sortItems(4, Qt.DescendingOrder)

            if currentExecutionType == 'TRADE' and currentOrderStatus == 'FILLED':
                if orderType != 'MARKET':
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

                    if side == 'BUY' and filled == 0:
                        count = 0
                        print('BUY TRADE FILLED ON ZERO')
                        buycero = df.loc[(df['internal_status'] == 0) & (df['side'] == 'BUY')]
                        buycero.sort_values('price', inplace=True, ascending=True)
                        price = float(df.iloc[buycero.index[0]]['price']) - threshold
                        # print('MORE LOW BUY ORDER PRICE: ', df.iloc[buycero.index[0]]['price'])
                        print('MAKING BUY ORDER AT PRICE  ', price)
                        pools.apply_async(puts, (gsymbol, 'BUY', gamount, price, ex), )
                        # task_puto.delay(api_key, api_id, symbol, 'LIMIT', 'BUY', amount, price, e)

                    if side == 'SELL' and filled == 0:
                        count = 0
                        print('SELL TRADE FILLED ON ZERO')
                        sellcero = df.loc[(df['internal_status'] == 0) & (df['side'] == 'SELL')]
                        sellcero.sort_values('price', inplace=True, ascending=False)
                        price = float(df.iloc[sellcero.index[0]]['price']) + threshold
                        # print('MORE HIGH SELL ORDER PRICE: ', df.iloc[sellcero.index[0]]['price'])
                        print('MAKING SELL ORDER AT PRICE  ', price)
                        pools.apply_async(puts, (gsymbol, 'SELL', gamount, price, ex), )

                    #     ***********************************

                    if side == 'BUY' and filled == 1:
                        p = float(price) + threshold
                        pools.apply_async(puts, (gsymbol, 'SELL', gamount, p, ex), ) #

                    if side == 'SELL' and filled == 1:
                        p = float(price) - threshold
                        pools.apply_async(puts, (gsymbol, 'BUY', gamount, p, ex), )



                    filled = 1

            if currentExecutionType == 'CANCEL':
                pass

            self.orderTable.setModel(pandasModel(df))


        except Exception as e:
            print(e)
            self.statusbar.showMessage("ERROR {} Fetching WS ORDERS...".format(e))
        finally:
            pass
            # print('wo', orders)
        # print(orders[0])

        # self.logText.append(str(df))
        # self.logText.append('----------------')
