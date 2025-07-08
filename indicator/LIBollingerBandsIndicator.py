# region imports

from indicator.LIBollingerBand import *
from indicator.LIInsightIndicator import *


# endregion

class LIBollingerBandsIndicator(LIInsightIndicator):
    """
    A list of standard bollinger bands combined as this customized bollinger bands stack from top to bottom.
    [Bollinger Bands](https://www.investopedia.com/trading/using-bollinger-bands-to-gauge-trends/)
    ![Define Bands and Tiers](docs/guidelines/6E-1Year-Bands-Tiers.png)
    """

    def __init__(self, securityMonitor, positionManager, mainChart, configs):
        super().__init__(securityMonitor, positionManager, mainChart, configs)

        self.middleBandName = "band-#0-middle"
        self.verbose = configs.get(LIConfigKey.verbose, LIDefault.verbose)
        self.bollingerBandsParams = configs.get(LIConfigKey.bollingerBandsParams, LIDefault.bollingerBandsParams)

        self.bollingerBandsList: list[BollingerBands] = []  # A list of original bollinger bands
        self.headBand: LIBollingerBand = None  # The top/upper/first bollinger band, double linked to other bands
        self.middleBand: LIBollingerBand = None  # The middle bollinger band, default starter band
        self.startBand: LIBollingerBand = None  # The current start band, from middle band by default

        self.rollingWindowSize: int = 5
        self.rollingWindowBands: List[LIBollingerBand] = []  # A rolling bands, the first one is the most recent one!

        if self.bollingerBandsParams:
            signalSymbol = self.securityMonitor.getSymbol()
            for index, params in enumerate(self.bollingerBandsParams):
                index += 1
                resolution = getResolution(params[2]) if len(params) > 2 else Resolution.Daily
                # Simple moving average type performs better for multiple layers of bollinger bands
                movingAverageType = MovingAverageType.Simple if len(self.bollingerBandsParams) > 2 else MovingAverageType.Exponential
                # # Use a customized bollinger bands as if the BB one is not working as expected and update it periodically!
                # bollingerBands = BollingerBands(params[0], params[1], movingAverageType)
                bollingerBands = getAlgo().BB(signalSymbol, params[0], params[1], movingAverageType, resolution=resolution)
                bollingerBands.Updated += self.onBollingerBandsUpdated  # Callback to emit trade insights/signals
                self.bollingerBandsList.append(bollingerBands)
                if index == 1:  # Add all three bands
                    bollingerBands.UpperBand.Name = f"band-#{index}-upper"
                    self.headBand = LIBollingerBand(bollingerBands, bollingerBands.UpperBand)
                    bollingerBands.MiddleBand.Name = self.middleBandName
                    middleBand = LIBollingerBand(bollingerBands, bollingerBands.MiddleBand)
                    self.appendBand(middleBand)
                    self.middleBand = middleBand
                    bollingerBands.LowerBand.Name = f"band-#{index}-lower"
                    self.appendBand(LIBollingerBand(bollingerBands, bollingerBands.LowerBand))
                else:
                    bollingerBands.UpperBand.Name = f"band-#{index}-upper"
                    self.prependBand(LIBollingerBand(bollingerBands, bollingerBands.UpperBand))
                    bollingerBands.MiddleBand.Name = f"band-#{index}-middle"
                    bollingerBands.LowerBand.Name = f"band-#{index}-lower"
                    self.appendBand(LIBollingerBand(bollingerBands, bollingerBands.LowerBand))
                # # Warm up indicator is NOT fetching enough history data for sampling!
                # getAlgo().WarmUpIndicator(signalSymbol, bollingerBands, resolution=resolution)
                barType = QuoteBar if useQuoteBar(self.securityMonitor.securityType) else TradeBar
                # To fill the gaps, need more history data to warm up the indicator to be more accurate!
                for bar in getAlgo().History[barType](signalSymbol, round(bollingerBands.WarmUpPeriod * 1.5), resolution):
                    # if self.verbose:
                    #     log(f"{signalSymbol.Value}: History bar of symbol={bar.Symbol.Value}, endTime={bar.EndTime}, {bar}")
                    if bollingerBands:
                        bollingerBands.Update(bar.EndTime, bar.Close)
                if not bollingerBands.IsReady:
                    terminate(f"{signalSymbol.Value}: Please warm up the Bollinger Bands with params={params}, samples={bollingerBands.Samples} first!"
                              f" You might need to reduce the periods param in order to have enough history data to warm up the indicator.")

            self.resetStartBand(self.getMiddleBand().getName())  # by default

    def getBand(self, bandName: str) -> LIBollingerBand:
        band = self.headBand
        while band:
            if not bandName and band.isMiddle():
                return band
            elif band.getName() == bandName:
                return band
            band = band.nextBand

    def getStartBand(self):
        return self.startBand

    def getHeadBand(self):
        return self.headBand

    def getMiddleBand(self):
        return self.middleBand

    def getTailBand(self):
        band = self.headBand
        while band and band.nextBand:
            band = band.nextBand
        return band

    def prependBand(self, band: LIBollingerBand):
        self.headBand.prevBand = band
        band.nextBand = self.headBand
        self.headBand = band

    def appendBand(self, band: LIBollingerBand):
        tailBand = self.getTailBand()
        tailBand.nextBand = band
        band.prevBand = tailBand

    def countBands(self):
        bandsCount = 0
        upperBandsCount = 0
        lowerBandsCount = 0
        band = self.getHeadBand()
        while band:
            bandsCount += 1
            if band.isUpper():
                upperBandsCount += 1
            if band.isLower():
                lowerBandsCount += 1
            band = band.nextBand
        return bandsCount, upperBandsCount, lowerBandsCount

    def countUpperBands(self):
        return self.countBands()[1]

    def countLowerBands(self):
        return self.countBands()[2]

    def getBandPrices(self):
        prices = []
        band = self.getHeadBand()
        while band:
            prices.append(self.positionManager.roundSecurityPrice(band.getPrice()))
            band = band.nextBand
        return prices

    def getBandNames(self) -> []:
        names = []
        band = self.getHeadBand()
        while band:
            names.append(band.getName())
            band = band.nextBand
        return names

    def resetStartBand(self, bandName: str):
        self.startBand = self.getBand(bandName)
        self.rollingWindowBands.clear()
        self.rollingWindowBands.append(self.startBand)

    def onMonitorBarUpdated(self, bar: Bar):
        if self.getSymbol() != bar.Symbol:
            return

        # self.dataConsolidator.Update(bar)
        self.updateRollingWindow(bar)

        tradeInsight = self.predictTradeInsight(bar.Time, bar)
        if tradeInsight:
            for listener in self.tradeInsightListeners:
                listener.onEmitTradeInsight(tradeInsight)

    def updateRollingWindow(self, bar: Bar):
        tradingBand = self.getTradingBand(bar.Close)
        # Add the most recent one to first position
        if self.rollingWindowBands[0] != tradingBand:
            self.rollingWindowBands.insert(0, tradingBand)
            self.purgeRollingWindow()
            log(f"{self.securityMonitor.getSymbolAlias()}: Updated bollinger bands rolling window with marketPrice={bar.Close}, {self}", self.verbose)

    def getTradingBand(self, targetPrice):
        beyondBand = self.middleBand
        # Compare bar price with upper bands
        if targetPrice > self.middleBand.getPrice():
            band = self.getHeadBand()
            while band and not band.isMiddle():
                if targetPrice > band.getPrice() * (1 + band.getWidth() / 100 / 100):  # Adjust the threshold
                    beyondBand = band
                    break
                band = band.nextBand
        # Compare bar price with lower bands
        if targetPrice < self.middleBand.getPrice():
            band = self.getTailBand()
            while band and not band.isMiddle():
                if targetPrice < band.getPrice() * (1 + band.getWidth() / 100 / 100):  # Adjust the threshold
                    beyondBand = band
                    break
                band = band.prevBand
        return beyondBand

    def getTradingTierName(self, targetPrice=None):
        if targetPrice is None:
            targetPrice = self.securityMonitor.getMarketPrice()
        if targetPrice > self.middleBand.getPrice():
            return f"tier-#{self.getTradingBand(targetPrice).getIndex()}-upper"
        else:
            return f"tier-#{self.getTradingBand(targetPrice).getIndex()}-lower"

    def predictTradeInsight(self, timestamp=None, updated=None) -> LITradeInsight:
        startBand = self.rollingWindowBands[0]
        if startBand.isUpper():
            startBand = startBand.nextBand
        elif startBand.isLower():
            startBand = startBand.prevBand
        if startBand != self.startBand:
            log(f"{self.securityMonitor.getSymbolAlias()}: Emit trade insight to switch start band from {self.startBand} to {startBand}")
            signalType = LISignalType.RISING if startBand.getPrice() > self.startBand.getPrice() else LISignalType.FALLING
            self.startBand = startBand
            return LITradeInsight(serialId=self.tradeInsight.serialId + 1,
                                  symbolStr=self.getSymbol().Value,
                                  signalType=signalType,
                                  timestamp=timestamp)

    def purgeRollingWindow(self):
        # Remove last/staled/tailing bands!
        while len(self.rollingWindowBands) > self.rollingWindowSize:
            self.rollingWindowBands.pop()

    def onBollingerBandsUpdated(self, sender: BollingerBands, updated: IndicatorDataPoint):
        if not sender.is_ready:
            return

        plot(self.mainChart.name, sender.upper_band.name, sender.upper_band.current.value)
        if sender.middle_band.name == self.middleBandName:
            plot(self.mainChart.name, sender.middle_band.name, sender.middle_band.current.value)
        plot(self.mainChart.name, sender.lower_band.name, sender.lower_band.current.value)

    def __str__(self) -> str:
        result = ""
        if self.startBand:
            result += f"startBand={self.startBand.getName()}, "
        if self.middleBand:
            result += f"middleBand={self.middleBand.getName()}, "
        result += f"rollingWindowBands: "
        for band in self.rollingWindowBands:
            result += f"\n{band}"
        return result
