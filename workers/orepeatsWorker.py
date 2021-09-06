import operator
import random
import time
from time import sleep
from PyQt5.QtCore import QRunnable

import gvars
grilla = []

class OrepeatsRunnable(QRunnable):
    def __init__(self, obj):
        super().__init__()
        self.symbol = gvars.symbol
        self.obj = obj
        self.exchange = gvars.ex

    def run(self):
        global grilla
        while True:
            if gvars.disconnect == 1:
                print('disconnect from repeats')
                break
            sleep(random.uniform(2.1, 4.3))
            grilla = self.order_list()
            grilla_size = len(grilla)

            eliminar = []
            if grilla_size != 0:
                for n in range(grilla_size - 1):
                    if (grilla[n][2]) == (grilla[n + 1][2]):
                        temporal = []
                        temporal.extend([n, grilla[n][1]])
                        eliminar.append(temporal)

            if len(eliminar) != 0:
                print("DELETING ", eliminar)

            # elimino las ordenes que están en la lista "eliminar"
            if (len(eliminar)) != 0:
                for n in range(len(eliminar)):
                    print("Trying to drop", (eliminar[n][0]), (eliminar[n][1]))
                    try:
                        o = self.exchange.cancel_order(eliminar[n][1], self.symbol)
                        # print(o)
                    except Exception as e:
                        print('ERROR IN CANCEL A DUPLICATE ORDER {}'.format(e))

            if (len(eliminar)) != 0:
                for n in range(len(eliminar)):
                    match = self.order_match(eliminar[n][1])
                    grilla.pop(match - 1)
                    grilla = self.sorting_list(grilla)

        return

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
            print('ERROR FETCHING ORDER IN CANCEL A DUPLICATE ORDER {}'.format(e))

        grid = self.sorting_list(grid)
        return grid

    def order_match(self, order_id_):
        global steps
        match = 0
        steps = len(grilla)
        for i in range(0, steps):
            if grilla[i][1] == order_id_:
                match = (i + 1)
        return match
