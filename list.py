import operator

from sqlalchemy.util import asyncio

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
exchange.set_sandbox_mode(True)


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
   n=0
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
         match = (i+1)
   return match



async def main(loop):
    grilla = []
    # await pplm(self, grids[0][12], exchange)
    await exchange.load_markets()

    grilla = await order_list()
    grilla_size = len(grilla)
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
    st = int(grids[0][6])
    steps = int(grids[0][6] / 2)
    threshold = grids[0][4]
    countbuy = 0
    countsell = 0
    selllist = []
    buylist = []

    for i in range(len(sorted_list)):
        # print(sorted_list)
        if sorted_list[i][3:][0] == 'SELL':
            countsell += 1
            selllist.append(sorted_list[i])
            # print(sorted_list[i])
        if sorted_list[i][3:][0] == 'BUY':
            buylist.append(sorted_list[i])
            countbuy += 1
            # print(sorted_list[i])

    # print('countsell ', countsell)
    # print('countbuy ', countbuy)

    if not (countsell == countbuy):
        print('steps ', steps)
        x = 0
        temp = None

        if countbuy == steps:
            print('countbuy is fine')
            # print(countbuy)
        else:
            print('countbuy is bad')
            # print(countbuy)
            first = buylist[len(buylist) - 1][2]
            x = 0
            temp = None
            for i in range(0, steps):
                if x == 0:
                    temp = first
                    x = 1
                else:
                    temp = temp + threshold
                res = any(temp in sub for sub in buylist)
                print(temp, res)

        if countsell == steps:
            print('countsell is fine')
            # print(countsell)
        else:
            print('countsell is bad')
            # print(selllist)
            first = selllist[len(selllist) - 1][2]
            for i in range(0, steps):
                if x == 0:
                    temp = first
                    x = 1
                else:
                    temp = temp + threshold
                res = any(temp in sub for sub in selllist)
                # print(temp, res)

    await exchange.close()


loop.run_until_complete(main(loop))