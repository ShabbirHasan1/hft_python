import operator
import random
import time
from time import sleep
from PyQt5.QtCore import QRunnable

import gvars


class SimetryRunnable(QRunnable):
    def __init__(self, obj):
        super().__init__()
        self.symbol = gvars.symbol
        self.obj = obj
        self.exchange = gvars.ex
        self.steps = int(gvars.steps / 2)
        self.symbol = gvars.symbol
        self.threshold = gvars.threshold
        self.amount = gvars.amount

    def run(self):
        stepsbyside = self.steps
        symbol = self.symbol
        threshold = self.threshold
        amount = self.amount
        entry = 0

        grid = self.order_list()

        if len(grid) > 0:
            sorted_list = sorted(grid, key=operator.itemgetter(2), reverse=True)
            selllist = []
            buylist = []
            countbuy = 0
            countsell = 0
            print("CHECK SIMETRY...")
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

            if len(selllist) == stepsbyside:
                pass
            else:
                print('countsell is bad')
                if len(selllist) > stepsbyside:
                    print('selllist is >')
                    todrop = len(selllist) - stepsbyside
                    for i in range(0, todrop):
                        self.exchange.cancel_order(selllist[i][1], symbol)
                        # print(selllist[i][1])
                if len(selllist) < stepsbyside:
                    x = 0
                    temp = None
                    first = None
                    first = selllist[len(selllist) - 1][2]
                    for i in range(0, stepsbyside):
                        if x == 0:
                            temp = first
                            x = 1
                        else:
                            temp = temp + threshold
                        res = any(temp in sub for sub in selllist)
                        if not res:
                            self.exchange.create_order(symbol, 'LIMIT', 'SELL', amount, temp)
                            print(temp, res)

            if len(buylist) == stepsbyside:
                pass
            else:
                print('countbuy is bad')
                if len(buylist) > stepsbyside:
                    todrop = len(buylist) - stepsbyside
                    print(todrop)
                    print(buylist)
                    buylisttmp = buylist[-todrop:]
                    for i in range(0, len(buylisttmp)):
                        self.exchange.cancel_order(buylisttmp[i][1], self.grids[0][12])
                        sleep(1)
                if len(buylist) < stepsbyside:
                    print('buylist is <')
                    first = None
                    x = 0
                    temp = None
                    first = buylist[len(buylist) - 1][2]
                    for i in range(0, stepsbyside):
                        sleep(1)
                        if x == 0:
                            temp = first
                            x = 1
                        else:
                            temp = temp + threshold
                        res = any(temp in sub for sub in buylist)
                        if not res:
                            self.exchange.create_order(symbol, 'LIMIT', 'BUY', amount, temp)
                        sleep(1)
                        # print(temp, res)
        return
        # st = int(self.grids[0][6])
        # steps = int(self.grids[0][6] / 2)
        # threshold = self.grids[0][4]
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
        # if not (countsell == countbuy):
        #     print('steps ', steps)
        #     x = 0
        #     temp = None
        #
        #     if countbuy == steps:
        #         print('countbuy is fine')
        #         # print(countbuy)
        #     else:
        #         print('countbuy is bad')
        #         # print(countbuy)
        #         first = buylist[len(buylist) - 1][2]
        #         x = 0
        #         temp = None
        #         for i in range(0, steps):
        #             if x == 0:
        #                 temp = first
        #                 x = 1
        #             else:
        #                 temp = temp + threshold
        #             res = any(temp in sub for sub in buylist)
        #             if not res:
        #                 o = self.exchange.create_order(self.symbol, 'LIMIT', 'BUY', self.grids[0][3], temp)
        #                 print(temp, res)
        #             print(temp, res)
        #
        #     if countsell == steps:
        #         print('countsell is fine')
        #         # print(countsell)
        #     else:
        #         print('countsell is bad')
        #         # print(selllist)
        #         first = selllist[len(selllist) - 1][2]
        #         for i in range(0, steps):
        #             if x == 0:
        #                 temp = first
        #                 x = 1
        #             else:
        #                 temp = temp + threshold
        #             res = any(temp in sub for sub in selllist)
        #             if not res:
        #                 o = self.exchange.create_order(self.symbol, 'LIMIT', 'SELL', self.grids[0][3], temp)
        #                 print(temp, res)

        # selllist = []
        # buylist = []
        # if len(sorted_list_for_gap) > 1:
        #     for i in range(len(sorted_list_for_gap)):
        #         # print(sorted_list)
        #         if sorted_list_for_gap[i][3:][0] == 'SELL':
        #             selllist.append(sorted_list_for_gap[i])
        #             # print(sorted_list[i])
        #         if sorted_list_for_gap[i][3:][0] == 'BUY':
        #             buylist.append(sorted_list_for_gap[i])
        #             # print(sorted_list[i])
        #     minsell = selllist[len(selllist) - 1][2]
        #     maxbuy = buylist[0][2]
        #     gap = minsell - maxbuy
        #
        #     if gap > (threshold * 2):
        #         order_data = {'factor': self.grids[0][5], 'threshold': self.grids[0][4], 'symbol': self.grids[0][12],
        #                       'steps': self.grids[0][6], 'amount': self.grids[0][3], 'ticker': sockets.price_ticker,
        #                       'center': sockets.price_ticker}
        #         print('Grid Has GAP ')
        #         x = self.exchange.cancel_all_orders(self.symbol)
        #         # print(minsell)
        #         # print(maxbuy)
        #         hftinit(order_data, self.exchange)
        #         print(gap)

    def sorting_list(self, nested_list):
        sorted_list = sorted(nested_list, key=operator.itemgetter(2))
        for i in range(0, len(sorted_list)):
            sorted_list[i][0] = i
        return sorted_list

    def order_list(self):
        grid = []
        n = 0
        try:
            orders_ = self.exchange.fetch_open_orders(self.symbol)
            # print(o)
            for i in orders_:
                #   print(i['id'], " ", i['info']['status'], " ", i['side'], " ", i['price'], " ", i['amount'], " ", i['remaining'])
                temporal = []
                temporal.extend([n, i['id'], i['price'], i['side'].upper()])
                grid.append(temporal)
                n = n + 1
        except Exception as e:
            print('ERROR FETCHING ORDER IN SIMETRY WORKER {}'.format(e))

        grid = self.sorting_list(grid)
        return grid

    def order_match(self, order_id_):
        global grid
        global steps
        match = 0
        steps = len(grid)
        for i in range(0, steps):
            if grid[i][1] == order_id_:
                match = (i + 1)
        return match
