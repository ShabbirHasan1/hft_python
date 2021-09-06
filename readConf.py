# -*- coding: utf-8 -*-
"""
AimarketsCap HFT SYSTEM GUI order managing
"""
import pathlib
import sqlite3


def readgrids():
    mainpath = pathlib.Path().resolve()
    con = sqlite3.connect('./database.sqlite')
    cur = con.cursor()
    # symbols = cur.execute("SELECT * FROM symbols").fetchAll()
    grids = cur.execute("""SELECT g.name, s.name, s.icon, g.amount, g.threshold, g.factor, g.quantity, g.leverage, 
    g.margin_type, e.name, e.api_key, e.secret, s.symbol, s.market_name FROM grids g JOIN symbols s ON s.id = g.symbol_id 
    JOIN exchanges e ON e.id = g.exchange_id where g.active = '1'""").fetchall()

    return grids


class readConfig:
    def __init__(self, exchange):
        pass
