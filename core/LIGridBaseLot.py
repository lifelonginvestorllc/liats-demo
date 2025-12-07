from AlgorithmImports import *
from core.LITradingLot import *


class LIGridBaseLot(LITradingLot):
    def __init__(self, lotId, gridTrading):
        super().__init__(lotId, gridTrading.positionManager)

        self.gridTrading = gridTrading
        configs = gridTrading.configs

        self.nextLot: LIGridTradingLot = None
        self.prevLot: LIGridTradingLot = None

        self.openWithStopOrderType = configs.get(LIConfigKey.openWithStopOrderType, LIDefault.openWithStopOrderType)
        self.openWithMarketOrderType = configs.get(LIConfigKey.openWithMarketOrderType, LIDefault.openWithMarketOrderType)
        self.closeWithStopOrderType = configs.get(LIConfigKey.closeWithStopOrderType, LIDefault.closeWithStopOrderType)
        self.closeWithMarketOrderType = configs.get(LIConfigKey.closeWithMarketOrderType, LIDefault.closeWithMarketOrderType)
        self.enableTrailingStopLoss = configs.get(LIConfigKey.enableTrailingStopLoss, LIDefault.enableTrailingStopLoss)
        self.submitStopMarketOrder = configs.get(LIConfigKey.submitStopMarketOrder, LIDefault.submitStopMarketOrder)
        self.submitTrailingStopOrder = configs.get(LIConfigKey.submitTrailingStopOrder, LIDefault.submitTrailingStopOrder)
        self.updateTrailingStopPrice = configs.get(LIConfigKey.updateTrailingStopPrice, LIDefault.updateTrailingStopPrice)

        self.gridLotMinQuantity = configs.get(LIConfigKey.gridLotMinQuantity, LIDefault.gridLotMinQuantity)
        self.gridLotLevelAmount = configs.get(LIConfigKey.gridLotLevelAmount, LIDefault.gridLotLevelAmount)
        self.gridLotLevelPercent = configs.get(LIConfigKey.gridLotLevelPercent, LIDefault.gridLotLevelPercent)
        self.gridLotLevelAugment = configs.get(LIConfigKey.gridLotLevelAugment, LIDefault.gridLotLevelAugment)
        self.gridLotStopLossFactor = configs.get(LIConfigKey.gridLotStopLossFactor, LIDefault.gridLotStopLossFactor)
        self.gridLotMaxProfitFactor = configs.get(LIConfigKey.gridLotMaxProfitFactor, LIDefault.gridLotMaxProfitFactor)
        self.gridLotTakeProfitFactor = configs.get(LIConfigKey.gridLotTakeProfitFactor, LIDefault.gridLotTakeProfitFactor)
        self.gridLotPauseAfterProfit = configs.get(LIConfigKey.gridLotPauseAfterProfit, LIDefault.gridLotPauseAfterProfit)
        self.gridLotPauseAfterStopLoss = configs.get(LIConfigKey.gridLotPauseAfterStopLoss, LIDefault.gridLotPauseAfterStopLoss)
        self.gridLotStopProfitFactors = configs.get(LIConfigKey.gridLotStopProfitFactors, LIDefault.gridLotStopProfitFactors)
        self.gridLotBoostingProfitFactor = configs.get(LIConfigKey.gridLotBoostingProfitFactor, LIDefault.gridLotBoostingProfitFactor)
        self.gridLotBoostingDesireProfit = configs.get(LIConfigKey.gridLotBoostingDesireProfit, LIDefault.gridLotBoostingDesireProfit)

        self.gridLotsInStopProfitFactor = configs.get(LIConfigKey.gridLotsInStopProfitFactor, LIDefault.gridLotsInStopProfitFactor)
        self.gridPriceInStopProfitFactor = configs.get(LIConfigKey.gridPriceInStopProfitFactor, LIDefault.gridPriceInStopProfitFactor)
        self.gridCancelOrdersAfterClosed = configs.get(LIConfigKey.gridCancelOrdersAfterClosed, LIDefault.gridCancelOrdersAfterClosed)
        self.gridTrailingOpenPriceFactor = configs.get(LIConfigKey.gridTrailingOpenPriceFactor, LIDefault.gridTrailingOpenPriceFactor)

        self.gridLotOpenUponTradeInsight = configs.get(LIConfigKey.gridLotOpenUponTradeInsight, LIDefault.gridLotOpenUponTradeInsight)
        self.gridLotCloseUponTradeInsight = configs.get(LIConfigKey.gridLotCloseUponTradeInsight, LIDefault.gridLotCloseUponTradeInsight)

        if self.isMomentumMode():
            if self.gridPriceInStopProfitFactor:
                terminate(f"{LIConfigKey.gridPriceInStopProfitFactor} is not applicable for {self.getGridMode()} mode.")
            if self.gridLotBoostingProfitFactor:
                terminate(f"{LIConfigKey.gridLotBoostingProfitFactor} is not applicable for {self.getGridMode()} mode.")
            if self.gridTrailingOpenPriceFactor:
                terminate(f"Please note {LIConfigKey.gridTrailingOpenPriceFactor} can only apply to {LIGridMode.CONTRARIAN}!")
        elif self.isContrarianMode():
            if self.openWithStopOrderType:
                terminate(f"{LIConfigKey.openWithStopOrderType} is not applicable for {self.getGridMode()} mode.")
            # if self.openWithMarketOrderType and not self.gridLotBoostingProfitFactor:
            #     terminate(f"{LIConfigKey.openWithMarketOrderType} is not applicable for {self.getGridMode()} mode.")
        if self.gridLotMaxProfitFactor and self.gridLotTakeProfitFactor and self.gridLotMaxProfitFactor < self.gridLotTakeProfitFactor:
            terminate(f"Please make sure {LIConfigKey.gridLotMaxProfitFactor} is greater than {LIConfigKey.gridLotTakeProfitFactor}.")
        if self.gridLotStopProfitFactors and self.gridLotStopProfitFactors[0] > self.gridLotStopProfitFactors[1]:
            terminate(f"Please specify valid {LIConfigKey.gridLotStopProfitFactors}={self.gridLotStopProfitFactors}.")
        if self.gridLotBoostingProfitFactor:
            if not self.gridTrading.gridBoostingMaxHoldQuantity:
                terminate(f"Please specify both {LIConfigKey.gridLotBoostingProfitFactor} and {LIConfigKey.gridBoostingMaxHoldQuantity}.")
            if self.gridLotBoostingProfitFactor < self.gridLotTakeProfitFactor:
                terminate(f"Please make sure {LIConfigKey.gridLotBoostingProfitFactor} is greater than {LIConfigKey.gridLotTakeProfitFactor}.")
        if self.isMomentumMode() and not self.gridLotStopLossFactor:
            terminate(f"Please set {LIConfigKey.gridLotStopLossFactor} as gridMode={self.gridTrading.gridMode}.")

        self.canonicalSymbol = self.positionManager.getCanonicalSymbol()
        self.trailingOpenPrice = 0.0
        self.actualOpenPrice = 0.0
        self.accruedLostPoints = 0

    def getMarketPrice(self, bar=None):
        return self.gridTrading.getMarketPrice(bar)

    def getLotName(self):
        return f"Lot#{self.lotId}/{self.gridTrading.sessionId}"

    def getLotMetadata(self, key, default=None):
        # Please note to convert lot id to string first!
        return self.gridTrading.gridLotsMetadata.get(str(self.lotId), {}).get(key, default)

    def putLotMetadata(self, key, value):
        if self.lotId not in self.gridTrading.gridLotsMetadata:
            self.gridTrading.gridLotsMetadata[self.lotId] = {}
        self.gridTrading.gridLotsMetadata[self.lotId][key] = value

    def getStartLot(self):
        return self.gridTrading.startLot

    def getNextLot(self):
        lot = self.nextLot
        while lot:
            if lot.isTradeLot():
                return lot
            lot = lot.nextLot
        return None

    def getPrevLot(self):
        lot = self.prevLot
        while lot:
            if lot.isTradeLot():
                return lot
            lot = lot.prevLot
        return None

    def getCounterpartLot(self):
        return self.gridTrading.getCounterpartLot(peerLot=self)

    def isStartLot(self):
        return self.lotId == 0

    def isPausedOpening(self):
        return self.pausedOpening

    def isTradeLot(self):
        return not self.isStartLot()

    def isPausedLot(self):
        return self.isTradeLot() and self.pausedOpening

    def isIdlingLot(self):
        return self.isTradeLot() and self.lotStatus == LILotStatus.IDLING

    def isVacantLot(self):
        return self.isIdlingLot() and not self.isPausedLot()

    def isLongLot(self):
        return self.filledOpenQuantity > 0 or self.lotId > 0

    def isShortLot(self):
        return self.filledOpenQuantity < 0 or self.lotId < 0

    def isFirstLongLot(self):
        if self.gridTrading.getFirstLongLot():
            return self.lotId == self.gridTrading.getFirstLongLot().lotId
        return None

    def isFirstShortLot(self):
        if self.gridTrading.getFirstShortLot():
            return self.lotId == self.gridTrading.getFirstShortLot().lotId
        return None

    def isLastLongLot(self):
        if self.gridTrading.getLastLongLot():
            return self.lotId == self.gridTrading.getLastLongLot().lotId
        return None

    def isLastShortLot(self):
        if self.gridTrading.getLastShortLot():
            return self.lotId == self.gridTrading.getLastShortLot().lotId
        return None

    def isRetainedLot(self):
        return abs(self.gridTrading.gridRetainOpenedLots) >= abs(self.lotId)

    def isNotRetainedLot(self):
        return not self.isRetainedLot()

    def isBoostingLot(self):
        return self.gridLotBoostingProfitFactor and self.hasOpenPosition() and self.filledOpenQuantity > self.getTargetQuantity()

    def isBoostingTriggered(self):
        return self.gridLotBoostingProfitFactor and self.getProfitLossFactor() >= self.getBoostingProfitFactor()

    def isLosingLot(self):
        return self.getProfitLossPoints() < 0

    def isCommandMode(self):
        return self.gridTrading.isCommandMode()

    def isNotCommandMode(self):
        return self.gridTrading.isNotCommandMode()

    def isMomentumMode(self):
        return self.gridTrading.isMomentumMode()

    def isContrarianMode(self):
        return self.gridTrading.isContrarianMode()

    def isBuyAndHoldMode(self):
        return self.gridTrading.isBuyAndHoldMode()

    def getPriorLot(self):
        if self.isLongLot():
            return self.prevLot
        if self.isShortLot():
            return self.nextLot
        return None

    def getGridMode(self):
        return self.gridTrading.gridMode

    def getGridSide(self):
        if self.isLongLot() or self.isStartLot():
            if self.isMomentumMode():
                return LIGridSide.BTU
            elif self.isContrarianMode():
                return LIGridSide.BTD
        if self.isShortLot():
            if self.isMomentumMode():
                return LIGridSide.STD
            elif self.isContrarianMode():
                return LIGridSide.STU
        return None

    def hasOpenPosition(self):
        # Open order ticket could be null!
        return (self.filledOpenPrice or self.actualOpenPrice) and self.filledOpenQuantity

    def hasNoOpenPosition(self):
        return not self.hasOpenPosition()

    def hasClosePosition(self):
        # Close order ticket could be null!
        return self.closeOrderQuantity and (self.closeOrderPrice or self.stopOrderPrice or self.trailingAmount)

    def hasOrderTickets(self):
        return self.openOrderTicket or self.closeOrderTicket

    def hasOpenOrderTicket(self):
        return isOrderTicketUpdatable(self.openOrderTicket)

    def hasNoOpenOrderTicket(self):
        return not self.hasOpenOrderTicket()

    def hasCloseOrderTicket(self):
        return isOrderTicketUpdatable(self.closeOrderTicket)

    def hasNoCloseOrderTicket(self):
        return not self.hasCloseOrderTicket()

    def getStartPrice(self):
        return self.gridTrading.gridStartPrices[self.getGridSide()]

    def getOpenFromPrice(self):
        if self.getGridSide() in self.gridTrading.gridOpenFromPrices:
            return self.gridTrading.gridOpenFromPrices[self.getGridSide()]
        return None

    def getTicketPrice(self, orderTicket: OrderTicket):
        if orderTicket.order_type == OrderType.STOP_LIMIT:
            return orderTicket.get(OrderField.LIMIT_PRICE)
        elif orderTicket.order_type == OrderType.TRAILING_STOP:
            return orderTicket.get(OrderField.STOP_PRICE)
        elif orderTicket.order_type == OrderType.STOP_MARKET:
            return orderTicket.get(OrderField.STOP_PRICE)
        elif orderTicket.order_type == OrderType.LIMIT:
            return orderTicket.get(OrderField.LIMIT_PRICE)
        elif orderTicket.order_type == OrderType.MARKET:
            return self.gridTrading.getMarketPrice()
        return None

    def getTargetQuantity(self):
        return self.gridTrading.getTargetQuantity(self)

    def getAugmentedAmount(self):
        return self.gridTrading.getAugmentedAmount(self.lotId)

    def getAugmentedPercent(self):
        return self.gridTrading.getAugmentedPercent(self.lotId)

    def getStopProfitFactor(self):
        if self.gridLotStopProfitFactors:
            factorRange = self.gridLotStopProfitFactors[1] - self.gridLotStopProfitFactors[0]

            # TEST: It performs worse to use price ranges to calculate the factor!
            marketPriceDistance = abs(self.getMarketPrice() - self.getStartPrice())
            lastLotPriceDistance = abs(self.gridTrading.getLastLot(self).getOpenTargetPrice() - self.getStartPrice())
            # distance = (marketPriceDistance * factorRange / lastLotPriceDistance) if lastLotPriceDistance else 0
            priceDistanceRatio = marketPriceDistance / lastLotPriceDistance

            gridLots = self.gridTrading.gridLongLots if self.isLongLot() else self.gridTrading.gridShortLots
            filledLots = self.gridTrading.countFilledLots(self) if self.gridLotsInStopProfitFactor else self.lotId
            distance = (filledLots - 1) * factorRange / (gridLots - 1) if filledLots and gridLots > 1 else 0

            if self.gridPriceInStopProfitFactor:
                distance *= priceDistanceRatio

            return round(self.gridLotStopProfitFactors[0] + distance, LIGlobal.percentPrecision)
            # return round(self.gridLotStopProfitFactors[1] - distance, LIGlobal.percentPrecision)
        return None

    def getTargetGainPoints(self):
        targetPoints = 0
        if self.isLongLot():
            targetPoints = self.getCloseTargetPrice() - self.getOpenTargetPrice()
        if self.isShortLot():
            targetPoints = self.getOpenTargetPrice() - self.getCloseTargetPrice()
        targetPoints *= self.getSecurityMultiplier()
        return max(targetPoints, 1)

    def getTargetLossPoints(self):
        targetPoints = 0
        if self.isLongLot():
            targetPoints = self.getStopLossPrice()[0] - self.getOpenTargetPrice()
        if self.isShortLot():
            targetPoints = self.getOpenTargetPrice() - self.getStopLossPrice()[0]
        targetPoints *= self.getSecurityMultiplier()
        return min(targetPoints, -1)

    def getFinalOpenPrice(self):
        return self.actualOpenPrice if self.actualOpenPrice else (self.filledOpenPrice if self.filledOpenPrice else 0)

    def getProfitLossPoints(self, currentPrice=None):
        profitLossPoints = 0
        if self.hasOpenPosition():
            if not currentPrice:
                currentPrice = self.getMarketPrice()
            if self.isLongLot():
                profitLossPoints = currentPrice - self.getFinalOpenPrice()
            if self.isShortLot():
                profitLossPoints = self.getFinalOpenPrice() - currentPrice
            return self.positionManager.roundSecurityPrice(profitLossPoints)
        return profitLossPoints

    def getProfitLossPercent(self, currentPrice=None):
        if self.hasOpenPosition():
            return self.getProfitLossPoints(currentPrice) / self.getFinalOpenPrice() * 100
        return 0

    def getProfitLossFactor(self):
        if self.hasOpenPosition():
            if self.gridLotLevelAmount:
                return round(self.getProfitLossPoints(self.getMarketPrice()) / self.getAugmentedAmount(), LIGlobal.percentPrecision)
            if self.gridLotLevelPercent:
                return round(self.getProfitLossPercent(self.getMarketPrice()) / self.getAugmentedPercent(), LIGlobal.percentPrecision)
        return 0

    def getPriceDistanceFactor(self, sortedOpenPrice):
        priceDistance = abs(self.getMarketPrice() - sortedOpenPrice)
        if self.gridLotLevelAmount:
            return round(priceDistance / self.getAugmentedAmount(), LIGlobal.percentPrecision)
        if self.gridLotLevelPercent:
            return round(((priceDistance / sortedOpenPrice) * 100) / self.getAugmentedPercent(), LIGlobal.percentPrecision)
        return 0

    def getInvestedCapital(self):
        return self.filledOpenPrice * abs(self.filledOpenQuantity) * self.getSecurityMultiplier()

    def getClosingPrice(self):
        return self.closeOrderTicket.get(OrderField.LIMIT_PRICE)

    def getClosingQuantity(self):
        return self.closeOrderTicket.quantity - self.closeOrderTicket.quantity_filled if self.closeOrderTicket else self.closeOrderQuantity

    def getUnfilledQuantity(self):
        if self.tradeOrder:
            targetQuantity = self.tradeOrder.getQuantity()
        else:
            targetQuantity = self.getTargetQuantity()
        if self.isLongLot() and targetQuantity > self.filledOpenQuantity:
            targetQuantity = targetQuantity - self.filledOpenQuantity
        if self.isShortLot() and targetQuantity < self.filledOpenQuantity:
            targetQuantity = targetQuantity - self.filledOpenQuantity
        return self.positionManager.roundSecuritySize(targetQuantity)

    def addRealizedProfitLoss(self, netProfit):
        self.closedTradesCount += 1
        self.realizedProfitLoss = round(self.realizedProfitLoss + netProfit, LIGlobal.moneyPrecision)
        self.gridTrading.closedTradesCount += 1
        self.gridTrading.realizedProfitLoss = round(self.gridTrading.realizedProfitLoss + netProfit, LIGlobal.moneyPrecision)

    def getRealizedProfitAmount(self):
        return self.realizedProfitLoss

    def getUnrealizedProfitAmount(self):
        currentPrice = self.getMarketPrice()
        profitLossPoints = self.getProfitLossPoints(currentPrice)
        return profitLossPoints * abs(self.filledOpenQuantity) * self.getSecurityMultiplier()

    def getStopLossPrice(self) -> tuple[float, float]:
        stopLossPrice = None
        if self.gridTrading.liquidateLossAndLimitTrading:
            stoppedLossPrices = self.gridTrading.stoppedLossPrices
            if stoppedLossPrices and self.getGridSide() in stoppedLossPrices:
                return stoppedLossPrices[self.getGridSide()], 0
        if self.gridLotStopLossFactor:
            openPrice = self.filledOpenPrice if self.filledOpenPrice else self.getOpenTargetPrice()
            if self.enableTrailingStopLoss:
                if self.isLongLot():
                    openPrice = max(openPrice, self.getMarketPrice())
                if self.isShortLot():
                    openPrice = min(openPrice, self.getMarketPrice())
            if self.gridLotLevelPercent:
                if self.isLongLot() or self.isStartLot():
                    stopLossPrice = openPrice * (1 - self.getAugmentedPercent() / 100 * self.gridLotStopLossFactor)
                if self.isShortLot():
                    stopLossPrice = openPrice * (1 + self.getAugmentedPercent() / 100 * self.gridLotStopLossFactor)
            elif self.gridLotLevelAmount:
                if self.isLongLot() or self.isStartLot():
                    stopLossPrice = openPrice - self.getAugmentedAmount() * self.gridLotStopLossFactor
                if self.isShortLot():
                    stopLossPrice = openPrice + self.getAugmentedAmount() * self.gridLotStopLossFactor
            stopLossPrice = self.positionManager.roundSecurityPrice(stopLossPrice)
            return stopLossPrice, self.gridLotStopLossFactor
        return None

    def getMaxProfitPrice(self) -> tuple[float, float]:
        maxProfitPrice = None
        if self.gridLotMaxProfitFactor:
            openPrice = self.filledOpenPrice
            if self.gridLotLevelPercent:
                if self.isLongLot():
                    maxProfitPrice = openPrice * (1 + self.getAugmentedPercent() / 100 * self.gridLotMaxProfitFactor)
                if self.isShortLot():
                    maxProfitPrice = openPrice * (1 - self.getAugmentedPercent() / 100 * self.gridLotMaxProfitFactor)
            elif self.gridLotLevelAugment:
                if self.isLongLot():
                    maxProfitPrice = openPrice + self.getAugmentedAmount() * self.gridLotMaxProfitFactor
                if self.isShortLot():
                    maxProfitPrice = openPrice - self.getAugmentedAmount() * self.gridLotMaxProfitFactor
            maxProfitPrice = self.positionManager.roundSecurityPrice(maxProfitPrice)
            return maxProfitPrice, self.gridLotMaxProfitFactor
        return None

    def getStopProfitPrice(self) -> tuple[float, float]:
        stopProfitPrice = None
        stopProfitFactor = self.getStopProfitFactor()
        if self.isBoostingLot() and self.gridLotBoostingDesireProfit:  # Reduce profit factor to protect the boosting profit
            stopProfitFactor = round(stopProfitFactor * self.getTargetQuantity() / self.filledOpenQuantity, LIGlobal.percentPrecision)
            # stopProfitFactor = round(stopProfitFactor * 0.5, LIGlobal.percentPrecision)
        if stopProfitFactor:
            marketPrice = self.getMarketPrice()
            if self.gridLotLevelAmount:
                if self.isLongLot():
                    stopProfitPrice = marketPrice - self.getAugmentedAmount() * stopProfitFactor
                if self.isShortLot():
                    stopProfitPrice = marketPrice + self.getAugmentedAmount() * stopProfitFactor
            elif self.gridLotLevelPercent:
                if self.isLongLot():
                    stopProfitPrice = marketPrice * (1 - self.getAugmentedPercent() / 100 * stopProfitFactor)
                if self.isShortLot():
                    stopProfitPrice = marketPrice * (1 + self.getAugmentedPercent() / 100 * stopProfitFactor)
            stopProfitPrice = self.positionManager.roundSecurityPrice(stopProfitPrice)
            return stopProfitPrice, stopProfitFactor
        return None

    def getOpenTargetPrice(self, startPrice=None):
        targetPrice = None
        if self.tradeOrder:
            targetPrice = self.tradeOrder.getLimitPrice()
        else:
            startPrice = startPrice if startPrice else self.getStartPrice()
            if self.gridLotLevelPercent:
                # Calculate geometric prices
                if self.isLongLot() or self.isStartLot():
                    if self.isMomentumMode():
                        targetPrice = startPrice * pow(1 + self.getAugmentedPercent() / 100, self.lotId)
                    elif self.isContrarianMode():
                        targetPrice = startPrice * pow(1 - self.getAugmentedPercent() / 100, self.lotId)
                if self.isShortLot():
                    if self.isMomentumMode():
                        targetPrice = startPrice * pow(1 - self.getAugmentedPercent() / 100, abs(self.lotId))
                    elif self.isContrarianMode():
                        targetPrice = startPrice * pow(1 + self.getAugmentedPercent() / 100, abs(self.lotId))
            elif self.gridLotLevelAmount:
                # Calculate arithmetic prices
                if self.isLongLot() or self.isStartLot():
                    if self.isMomentumMode():
                        targetPrice = startPrice + (self.getAugmentedAmount() * self.lotId)
                    elif self.isContrarianMode():
                        targetPrice = startPrice - (self.getAugmentedAmount() * self.lotId)
                if self.isShortLot():
                    if self.isMomentumMode():
                        targetPrice = startPrice - (self.getAugmentedAmount() * abs(self.lotId))
                    elif self.isContrarianMode():
                        targetPrice = startPrice + (self.getAugmentedAmount() * abs(self.lotId))
        if targetPrice <= 0.0:
            targetPrice = 0.0
            # error(f"{self.getSymbolAlias()}: Got unexpected negative/zero open target price: {targetPrice}!")
        return self.positionManager.roundSecurityPrice(targetPrice)

    def getTrailingOpenPrice(self, marketPrice=None):
        targetPrice = None
        limitFactor = self.gridTrailingOpenPriceFactor
        marketPrice = marketPrice if marketPrice else self.getMarketPrice()
        limitStartPrice = self.gridTrading.getLimitStartPrice(self.getGridSide())
        if limitStartPrice:
            if self.isLongLot():
                marketPrice = min(marketPrice, limitStartPrice)
            if self.isShortLot():
                marketPrice = max(marketPrice, limitStartPrice)
        if self.gridLotLevelPercent:
            # Calculate geometric prices
            if self.isLongLot() or self.isStartLot():
                if self.isMomentumMode():
                    targetPrice = marketPrice * (1 + self.getAugmentedPercent() * limitFactor / 100)
                elif self.isContrarianMode():
                    targetPrice = marketPrice * (1 - self.getAugmentedPercent() * limitFactor / 100)
            if self.isShortLot():
                if self.isMomentumMode():
                    targetPrice = marketPrice * (1 - self.getAugmentedPercent() * limitFactor / 100)
                elif self.isContrarianMode():
                    targetPrice = marketPrice * (1 + self.getAugmentedPercent() * limitFactor / 100)
        elif self.gridLotLevelAmount:
            # Calculate arithmetic prices
            if self.isLongLot() or self.isStartLot():
                if self.isMomentumMode():
                    targetPrice = marketPrice + (self.getAugmentedAmount() * limitFactor)
                elif self.isContrarianMode():
                    targetPrice = marketPrice - (self.getAugmentedAmount() * limitFactor)
            if self.isShortLot():
                if self.isMomentumMode():
                    targetPrice = marketPrice - (self.getAugmentedAmount() * limitFactor)
                elif self.isContrarianMode():
                    targetPrice = marketPrice + (self.getAugmentedAmount() * limitFactor)
        if targetPrice <= 0.0:
            targetPrice = 0.0
            # error(f"{self.getSymbolAlias()}: Got unexpected negative/zero open target price: {targetPrice}!")
        return self.positionManager.roundSecurityPrice(targetPrice)

    def getFavorOpenPrice(self):
        openPrice = self.getOpenTargetPrice()
        filledPrice = self.filledOpenPrice
        if self.isContrarianMode() and self.gridTrading.gridOpenFromPrices:
            # Pick the favorable open price!
            if self.filledOpenPrice:
                if self.isLongLot():
                    openPrice = max(openPrice, filledPrice)
                if self.isShortLot():
                    openPrice = min(openPrice, filledPrice)
        elif filledPrice:
            openPrice = filledPrice
        return openPrice

    def getCloseTargetPrice(self):
        targetPrice = None
        if self.tradeOrder:
            return self.tradeOrder.stopLoss
        if self.isBuyAndHoldMode():
            return targetPrice
        openPrice = self.getFavorOpenPrice()
        if self.gridLotLevelPercent:
            if self.isLongLot() or self.isStartLot():
                targetPrice = openPrice * (1 + self.getAugmentedPercent() / 100 * self.gridLotTakeProfitFactor)
            if self.isShortLot():
                targetPrice = openPrice * (1 - self.getAugmentedPercent() / 100 * self.gridLotTakeProfitFactor)
        elif self.gridLotLevelAmount:
            if self.isLongLot() or self.isStartLot():
                targetPrice = openPrice + self.getAugmentedAmount() * self.gridLotTakeProfitFactor
            if self.isShortLot():
                targetPrice = openPrice - self.getAugmentedAmount() * self.gridLotTakeProfitFactor
        if targetPrice <= 0.0:
            targetPrice = 0.0
            # error(f"{self.getSymbolAlias()}: Got unexpected negative/zero close target price: {targetPrice}!")
        return self.positionManager.roundSecurityPrice(targetPrice)

    def getBoostingProfitFactor(self):
        stopProfitFactor = self.getStopProfitFactor()  # Reduce both drawdown and performance!
        # stopProfitFactor = 0  # Increase both drawdown and performance!
        return round(self.gridLotBoostingProfitFactor + (stopProfitFactor if stopProfitFactor else 0), LIGlobal.percentPrecision)

    def cloneTradingProps(self, sourceLot):
        self.filledOpenPrice = sourceLot.filledOpenPrice
        self.filledOpenQuantity = sourceLot.filledOpenQuantity
        self.actualOpenPrice = sourceLot.actualOpenPrice
        self.openOrderTicket = sourceLot.openOrderTicket
        self.openOrderTransferId = sourceLot.openOrderTransferId
        self.createdOpenOrderTime = sourceLot.createdOpenOrderTime

        self.stopOrderPrice = sourceLot.stopOrderPrice
        self.trailingAmount = sourceLot.trailingAmount
        self.closeOrderPrice = sourceLot.closeOrderPrice
        self.closeOrderQuantity = sourceLot.closeOrderQuantity
        self.closeOrderTicket = sourceLot.closeOrderTicket
        self.closeOrderTransferId = sourceLot.closeOrderTransferId
        self.trailingStopLossPrice = sourceLot.trailingStopLossPrice

        self.pausedOpening = sourceLot.pausedOpening
        self.closedTradesCount = sourceLot.closedTradesCount
        self.realizedProfitLoss = sourceLot.realizedProfitLoss

        self.accruedFees = sourceLot.accruedFees
        self.lotStatus = sourceLot.lotStatus
