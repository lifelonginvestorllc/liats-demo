# region imports
from core.LIConfiguration import *


# endregion

class LIBollingerBand:
    def __init__(self, bollingerBands: BollingerBands, bollingerBand: IndicatorBase):
        self.bollingerBands = bollingerBands
        self.bollingerBand = bollingerBand

        self.nextBand: LIBollingerBand = None
        self.prevBand: LIBollingerBand = None

    def getName(self):
        return self.bollingerBand.Name

    def getIndex(self):
        return int(self.getName().split("-")[1][1:])

    def getPrice(self):
        return self.bollingerBand.Current.Value

    def getWidth(self):
        return self.bollingerBands.BandWidth.Current.Value

    def isReady(self):
        return self.bollingerBand.IsReady

    def isUpper(self):
        return "upper" in self.getName()

    def isMiddle(self):
        return "middle" in self.getName()

    def isLower(self):
        return "lower" in self.getName()

    def isBoundary(self):
        return not self.nextBand or not self.prevBand

    def __str__(self) -> str:
        return f"bollingerBand={{name={self.getName()},price={self.getPrice():.5f},width={self.getWidth():.5f}}}"
