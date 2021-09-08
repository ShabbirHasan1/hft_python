import random
import sys
from time import sleep
from PyQt5.QtCore import QRunnable
import gvars


class PositionRiskRunnable(QRunnable):
    def __init__(self, obj):
        super().__init__()
        self.symbol = gvars.symbol
        self.exchange = gvars.ex
        self.obj = obj

    def run(self):
        self.exchange.loadMarkets()
        self.obj.liquidationPriceLCD.setStyleSheet("color: yellow;")
        while True:
            if gvars.disconnect == 1:
                print('disconnect from pnl')
                break

            sleep(random.uniform(3.5, 12.3))
            try:
                pos = self.exchange.fapiPrivate_get_positionrisk()  # or fapiPrivate_get_positionrisk()
                market = self.exchange.market(self.symbol)['id']
                for i in pos:
                    if (i['symbol'] == market):
                        # print(i)
                        positionAmt = float(i['positionAmt'])
                        entryPrice = float(i['entryPrice'])
                        unRealizedProfit = round(float(i['unRealizedProfit']), 2)
                        liquidationPrice = float(i['liquidationPrice'])
                        isolatedMargin = round(float(i['isolatedMargin']), 2)
                        isolatedWallet = round(float(i['isolatedWallet']), 2)

                        if unRealizedProfit < 0:
                            # foreground colo
                            self.obj.pnlLCD.setStyleSheet("color: red;")
                        elif unRealizedProfit > 0:
                            self.obj.pnlLCD.setStyleSheet("color: green;")
                        else:
                            self.obj.pnlLCD.setStyleSheet("color: white;")

                        if positionAmt < 0:
                            self.obj.directionLabel.setStyleSheet("color: red;")
                            self.obj.directionLabel.setText('SELL')
                            positionAmt = positionAmt * (-1)
                        elif positionAmt == 0:
                            self.obj.directionLabel.setStyleSheet("color: white;")
                            self.obj.directionLabel.setText('---')
                        else:
                            self.obj.directionLabel.setStyleSheet("color: green;")
                            self.obj.directionLabel.setText('BUY')

                        self.obj.liquidationPriceLCD.display(liquidationPrice)
                        self.obj.entryLCD.display(entryPrice)
                        self.obj.positionLCD.display(positionAmt)
                        self.obj.pnlLCD.display(unRealizedProfit)
                        self.obj.marginLCD.display(isolatedMargin)

                        self.obj.isolatedwalletLCD.display(isolatedWallet)
                        t = isolatedMargin + isolatedWallet
                        self.obj.totalLCD.display(t)


            except Exception as e:
                if isinstance(e, RuntimeError):
                    sys.exit()
                print('ERROR IN RUNABLE DE FAPIPOSITION ', e)
        return
