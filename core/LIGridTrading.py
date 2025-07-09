# region imports

from core.LIGridBase import *

# endregion

"""
Please look into README.md to understand: What is grid trading?
"""


class LIGridTrading(LIGridBase):
    def __init__(self, symbolStr, securityType, investAmount, gridMode, **configs):
        super().__init__(symbolStr, securityType, investAmount, gridMode, **configs)

    def getPeriodicityTimedelta(self) -> timedelta:
        if self.dcaInvestPeriodicity == LIPeriodicity.DAILY:
            return timedelta(days=1)
        elif self.dcaInvestPeriodicity == LIPeriodicity.WEEKLY:
            return timedelta(weeks=1)
        elif self.dcaInvestPeriodicity == LIPeriodicity.MONTHLY:
            return timedelta(weeks=4)
        else:
            terminate(f"Not support {LIConfigKey.dcaInvestPeriodicity}={self.dcaInvestPeriodicity}")

    def getHeadLot(self):
        lot = self.startLot
        while lot and lot.prevLot:
            lot = lot.prevLot
        return lot

    def getTailLot(self):
        lot = self.startLot
        while lot and lot.nextLot:
            lot = lot.nextLot
        return lot

    def getTradeLot(self):
        lot = self.getHeadLot()
        while lot:
            if lot.isTradeLot():
                return lot
            lot = lot.nextLot
        return lot

    def getFirstLot(self, peerLot):
        if peerLot.isLongLot():
            return self.getFirstLongLot()
        if peerLot.isShortLot():
            return self.getFirstShortLot()

    def getLastLot(self, peerLot):
        if peerLot.isLongLot():
            return self.getLastLongLot()
        if peerLot.isShortLot():
            return self.getLastShortLot()

    def getLastOpenedLot(self, peerLot):
        if peerLot.isLongLot():
            return self.getLastOpenedLongLot()
        if peerLot.isShortLot():
            return self.getLastOpenedShortLot()

    def getCounterpartLot(self, peerLot):
        lot = self.getHeadLot()
        while lot:
            if lot.lotId == -peerLot.lotId:
                return lot
            lot = lot.nextLot

    def getLastOpenedCounterpartLot(self, peerLot):
        if peerLot.isLongLot():
            return self.getLastOpenedShortLot()
        if peerLot.isShortLot():
            return self.getLastOpenedLongLot()

    def getFirstOpenedCounterpartLot(self, peerLot):
        if peerLot.isLongLot():
            return self.getFirstOpenedShortLot()
        if peerLot.isShortLot():
            return self.getFirstOpenedLongLot()

    def getFirstOpenedLongLot(self):
        lot = self.startLot.nextLot
        while lot:
            if lot.hasOpenPosition():
                return lot
            lot = lot.nextLot

    def getLastOpenedLongLot(self):
        lastOpenedLot = None
        lot = self.startLot.nextLot
        while lot:
            if lot.hasOpenPosition():
                lastOpenedLot = lot
            lot = lot.nextLot
        return lastOpenedLot

    def getLastLongLot(self):
        lot = self.getTailLot()
        return lot if lot.isLongLot() else None

    def getLastShortLot(self):
        lot = self.getHeadLot()
        return lot if lot.isShortLot() else None

    def getFirstLongLot(self):
        return self.startLot.nextLot

    def getFirstShortLot(self):
        return self.startLot.prevLot

    def getFirstOpenedShortLot(self):
        lot = self.startLot.prevLot
        while lot:
            if lot.hasOpenPosition():
                return lot
            lot = lot.prevLot

    def getLastOpenedShortLot(self):
        lastOpenedLot = None
        lot = self.startLot.prevLot
        while lot:
            if lot.hasOpenPosition():
                lastOpenedLot = lot
            lot = lot.prevLot
        return lastOpenedLot

    def getSecondLongLot(self):
        if self.getFirstLongLot():
            return self.getFirstLongLot().nextLot

    def getSecondShortLot(self):
        if self.getFirstShortLot():
            return self.getFirstShortLot().prevLot

    def getNextOpeningLongLot(self):
        if self.getLastOpenedLongLot():
            return self.getLastOpenedLongLot().nextLot
        else:
            return self.getFirstLongLot()

    def getNextOpeningShortLot(self):
        if self.getLastOpenedShortLot():
            return self.getLastOpenedShortLot().prevLot
        else:
            return self.getFirstShortLot()

    def addLastLongLot(self):
        # Add new lot to tail
        tail = self.getTailLot()
        temp = self.createGridLot(tail.lotId + 1)
        tail.nextLot = temp
        temp.prevLot = tail
        tail = temp
        return tail

    def addLastShortLot(self):
        # Add new lot to head
        head = self.getHeadLot()
        temp = self.createGridLot(head.lotId - 1)
        temp.nextLot = head
        head.prevLot = temp
        head = temp
        return head

    def dropLastLongLot(self):
        lastLongLot = self.getLastLongLot()  # Drop this last long lot
        if lastLongLot:
            lastLongLot.prevLot.nextLot = None
            lastLongLot.prevLot = None
        return lastLongLot

    def dropLastShortLot(self):
        lastShortLot = self.getLastShortLot()  # Drop this last short lot
        if lastShortLot:
            lastShortLot.nextLot.prevLot = None
            lastShortLot.nextLot = None
        return lastShortLot

    def initializeGridLots(self):
        if self.countTradeLots()[0] == 0:
            self.startLot = self.createGridLot(0)
            if self.gridLongLots:
                for idx in range(self.gridLongLots):
                    self.addLastLongLot()
            if self.gridShortLots:
                for idx in range(self.gridShortLots):
                    self.addLastShortLot()

    def createGridLot(self, lotId):
        return LIGridTradingLot(lotId, self)

    def resetGridLotIds(self):
        temp = self.startLot
        while temp.nextLot:
            temp.nextLot.lotId = temp.lotId + 1
            temp = temp.nextLot
        temp = self.startLot
        while temp.prevLot:
            temp.prevLot.lotId = temp.lotId - 1
            temp = temp.prevLot

    def getGridLongSide(self):
        if self.isMomentumMode():
            return LIGridSide.BTU
        elif self.isContrarianMode():
            return LIGridSide.BTD

    def getGridShortSide(self):
        if self.isMomentumMode():
            return LIGridSide.STD
        elif self.isContrarianMode():
            return LIGridSide.STU

    def getGridTradingSide(self):
        return self.getGridLongSide() if self.getInvestedQuantity() >= 0 else self.getGridShortSide()

    def countOrderTickets(self):
        orderTicketsCount = 0
        for orderTicket in self.positionManager.getActiveOrderTickets():
            if isOrderTicketUpdatable(orderTicket):
                orderTicketsCount += 1
        return orderTicketsCount

    def countOpenOrders(self, peerLot=None):
        openOrdersCount = 0
        lot = self.getTradeLot()
        while lot:
            if lot.hasOpenOrderTicket():
                openOrdersCount += (0 if peerLot and peerLot.lotId * lot.lotId < 0 else 1)
            lot = lot.getNextLot()
        return openOrdersCount

    def cancelOpenOrders(self, peerLot=None, tagLog=None):
        openOrdersCount = 0
        lot = self.getTradeLot()
        while lot:
            if not peerLot or arePeerLots(lot, peerLot):
                lot.cancelOpenOrderTicket(tagLog)
            openOrdersCount += 1
            lot = lot.getNextLot()
        return openOrdersCount

    def countCloseOrders(self, peerLot=None):
        closeOrdersCount = 0
        lot = self.getTradeLot()
        while lot:
            if lot.hasCloseOrderTicket():
                closeOrdersCount += (0 if peerLot and peerLot.lotId * lot.lotId < 0 else 1)
            lot = lot.getNextLot()
        return closeOrdersCount

    def cancelCloseOrders(self, tagLog=None):
        closeOrdersCount = 0
        lot = self.getTradeLot()
        while lot:
            lot.cancelCloseOrderTicket(tagLog)
            closeOrdersCount += 1
            lot = lot.getNextLot()
        return closeOrdersCount

    def getOpeningQuantity(self):
        filledQuantity = 0
        lot = self.getTradeLot()
        while lot:
            filledQuantity += lot.filledOpenQuantity
            if lot.isPausedLot() and lot.filledOpenQuantity:
                terminate(f"The paused grid lot should NOT have filled quantity!")
            lot = lot.getNextLot()
        return self.positionManager.roundSecuritySize(filledQuantity)

    def getClosingQuantity(self):
        closingQuantity = 0
        lot = self.getTradeLot()
        while lot:
            closingQuantity += lot.getClosingQuantity()
            if lot.isPausedLot() and lot.getClosingQuantity():
                terminate(f"The paused grid lot should NOT have filled quantity!")
            lot = lot.getNextLot()
        return self.positionManager.roundSecuritySize(closingQuantity)

    def getLeakingQuantity(self):
        return self.getInvestedQuantity() - self.getOpeningQuantity() - self.dcaHoldingQuantity

    def countTradeLots(self):
        longLotsCount, shortLotsCount = 0, 0
        lot = self.getTradeLot()
        while lot:
            if lot.isLongLot():
                longLotsCount += 1
            if lot.isShortLot():
                shortLotsCount += 1
            lot = lot.getNextLot()
        return longLotsCount + shortLotsCount, longLotsCount, shortLotsCount

    def countLongLots(self):
        return self.countTradeLots()[1]

    def countShortLots(self):
        return self.countTradeLots()[2]

    def countAllTrades(self):
        tradesCount = 0
        lot = self.getTradeLot()
        while lot:
            if lot.hasOpenPosition():
                tradesCount += 1
            tradesCount += lot.closedTradesCount
            lot = lot.getNextLot()
        return tradesCount

    def countFilledLots(self, peerLot=None):
        longLotsCount, shortLotsCount = 0, 0
        lot = self.getTradeLot()
        while lot:
            if lot.hasOpenPosition():
                if lot.isLongLot():
                    longLotsCount += 0 if peerLot and peerLot.lotId * lot.lotId < 0 else 1
                if lot.isShortLot():
                    shortLotsCount += 0 if peerLot and peerLot.lotId * lot.lotId < 0 else 1
            lot = lot.getNextLot()
        if peerLot:
            return longLotsCount if peerLot.isLongLot() else shortLotsCount
        else:
            return longLotsCount + shortLotsCount, longLotsCount, shortLotsCount

    def countLosingLots(self, peerLot=None):
        longLotsCount, shortLotsCount = 0, 0
        lot = self.getTradeLot()
        while lot:
            if lot.isLosingLot():
                if lot.isLongLot():
                    longLotsCount += 0 if peerLot and peerLot.lotId * lot.lotId < 0 else 1
                if lot.isShortLot():
                    shortLotsCount += 0 if peerLot and peerLot.lotId * lot.lotId < 0 else 1
            lot = lot.getNextLot()
        if peerLot:
            return longLotsCount if peerLot.isLongLot() else shortLotsCount
        else:
            return longLotsCount + shortLotsCount, longLotsCount, shortLotsCount

    def countPausedLots(self, peerLot=None):
        pausedLotsCount = 0
        lot = self.getTradeLot()
        while lot:
            pausedLotsCount += (0 if peerLot and peerLot.lotId * lot.lotId < 0 else (1 if lot.pausedOpening else 0))
            lot = lot.getNextLot()
        return pausedLotsCount

    def getInvestedCapital(self):
        investedCapital = 0
        lot = self.getTradeLot()
        while lot:
            investedCapital += lot.getInvestedCapital()
            lot = lot.getNextLot()
        return round(investedCapital, LIGlobal.moneyPrecision)

    def getTargetQuantity(self, targetLot, gridMode=None):
        targetQuantity = 0
        if self.gridLongLotsQty and targetLot.isLongLot():
            targetQuantity = self.gridLongLotsQty[abs(targetLot.lotId) - 1]
        elif self.gridShortLotsQty and targetLot.isShortLot():
            targetQuantity = self.gridShortLotsQty[abs(targetLot.lotId) - 1]
        elif self.investAmount.lotQuantity:
            targetQuantity = self.investAmount.lotQuantity
        elif self.investAmount.maxQuantity:
            targetQuantity = self.investAmount.maxQuantity / (self.gridLongLots if targetLot.lotId >= 0 else self.gridShortLots)
            targetQuantity = self.positionManager.roundSecuritySize(targetQuantity)
        elif self.investAmount.maxCapital:
            targetQuantity = self.calculateTargetQuantity(targetLot, self.investAmount.maxCapital, gridMode)
        elif self.investAmount.maxHolding:
            maxCapital = getAlgo().Portfolio.TotalPortfolioValue * self.investAmount.maxHolding
            targetQuantity = self.calculateTargetQuantity(targetLot, maxCapital, gridMode)

        if targetQuantity < 0:
            terminate(f"{self.getSymbolAlias()}: Got unexpected target quantity: {targetQuantity} based on {self.investAmount}!")

        if targetLot.isShortLot():
            targetQuantity = -targetQuantity

        if self.investAmountTierFactors and not self.gridRealignOpenPositions:
            targetQuantity *= self.investAmountTierFactors[self.getTradingTierFactorIndex()]

        return targetQuantity

    def calculateTargetQuantity(self, targetLot, maxCapital, gridMode=None):
        targetQuantity = 0
        if self.positionManager.isDerivative():
            openTargetPrice = self.securityMonitor.getMaintenanceMargin()
            if openTargetPrice:
                targetQuantity = maxCapital / (self.gridLongLots if targetLot.lotId >= 0 else self.gridShortLots) / openTargetPrice
        else:
            openTargetPrice = self.getMarketPrice() if targetLot.isRetainedLot() else targetLot.getOpenTargetPrice()
            if openTargetPrice:
                targetQuantity = maxCapital / (self.gridLongLots if targetLot.lotId >= 0 else self.gridShortLots) / openTargetPrice
        targetQuantity = self.positionManager.roundSecuritySize(targetQuantity)
        log(f"{self.getSymbolAlias()}: Calculate target quantity for {targetLot}, maxCapital={maxCapital:.2f}, marketPrice={self.getMarketPrice()}, "
            f"openTargetPrice={openTargetPrice}, targetQuantity={targetQuantity}.", self.verbose)
        return targetQuantity

    def getAvgProfitAmount(self):
        profitAmount = 0
        averagePrice = self.positionManager.getAveragePrice()
        if self.getInvestedQuantity() > 0:
            profitAmount = self.getMarketPrice() - averagePrice
        if self.getInvestedQuantity() < 0:
            profitAmount = averagePrice - self.getMarketPrice()
        return round(profitAmount, LIGlobal.moneyPrecision)

    def getAvgProfitPercent(self):
        marketPrice = self.getMarketPrice()
        return round(self.getAvgProfitAmount() / marketPrice * 100, LIGlobal.percentPrecision) if marketPrice else 0

    def storedFilledLots(self):
        filledLots = 0
        for value in self.gridLotsMetadata.values():
            quantity = value.get(LIMetadataKey.filledOpenQuantity, 0)
            if quantity > 0:
                filledLots += 1
            elif quantity < 0:
                filledLots -= 1
        return filledLots

    def sumInvestedQuantity(self):
        investedQuantity = 0
        for value in self.gridLotsMetadata.values():
            investedQuantity += value.get(LIMetadataKey.filledOpenQuantity, 0)
        return investedQuantity

    def detectManualCloseOrder(self, peerLot):
        """Manual close order usually matches grid's invested quantity"""
        if self.countFilledLots(peerLot) > 1:
            for orderTicket in self.getOpenOrderTickets():
                if isOrderTicketUpdatable(orderTicket) and orderTicket.Quantity == -(self.getInvestedQuantity() - self.dcaHoldingQuantity):
                    return orderTicket

    def areGridLotsSkewed(self):
        longLots = shortLots = 0
        totalLots = self.countTradeLots()[0]

        # Check the paused lots in ascending order
        pausedLotMaxId = -totalLots
        filledLotMinId = totalLots
        lot = self.startLot.nextLot
        while lot and not lot.isStartLot():
            if lot.pausedOpening:
                pausedLotMaxId = max(pausedLotMaxId, lot.lotId)
                if lot.hasOpenPosition() or lot.hasClosePosition():
                    alert(f"{self.getNotifyPrefix()}: Skewed grid lots, please reset the paused lot: {lot}")
                    return True
            elif lot.hasOpenPosition() and lot.isNotRetainedLot():
                filledLotMinId = min(filledLotMinId, lot.lotId)
            lot = lot.nextLot
        if self.countFilledLots()[1] and pausedLotMaxId > filledLotMinId:
            alert(f"{self.getNotifyPrefix()}: Skewed grid lots, the paused lots should stay close to head: "
                  f"pausedLotMaxId={pausedLotMaxId}, filledLotMinId={filledLotMinId}.")
            return True

        # Check the paused lots in descending order
        pausedLotMinId = totalLots
        filledLotMaxId = -totalLots
        lot = self.startLot.prevLot
        while lot and not lot.isStartLot():
            if lot.pausedOpening:
                pausedLotMinId = min(pausedLotMinId, lot.lotId)
                if lot.hasOpenPosition() or lot.hasClosePosition():
                    alert(f"{self.getNotifyPrefix()}: Skewed grid lots, please reset the paused lot {lot}")
            elif lot.hasOpenPosition() and lot.isNotRetainedLot():
                filledLotMaxId = max(filledLotMaxId, lot.lotId)
            lot = lot.prevLot
        if self.countFilledLots()[2] and pausedLotMinId < filledLotMaxId:
            alert(f"{self.getNotifyPrefix()}: Skewed grid lots, the paused lots should stay close to tail: "
                  f"pausedLotMaxId={pausedLotMaxId}, filledLotMinId={filledLotMinId}.")
            return True

        # Check long side lots prices
        lot = self.startLot.nextLot
        while lot:
            longLots += 1
            nextLot = lot.nextLot
            if lot.accruedLostPoints == 0 and lot.isNotRetainedLot() and nextLot:
                if lot.lotId >= nextLot.lotId:
                    return True  # lot id is not in order
                if lot.hasOpenPosition() and nextLot.hasOpenPosition():
                    if self.isMomentumMode() and lot.filledOpenPrice > nextLot.filledOpenPrice:
                        alert(f"{self.getNotifyPrefix()}: Skewed grid lots, two lots with filled open price not in sequence order: \n->{lot}\n->{nextLot}",
                              self.verbose)
                        return True
                    elif self.isContrarianMode() and lot.filledOpenPrice < nextLot.filledOpenPrice:
                        alert(f"{self.getNotifyPrefix()}: Skewed grid lots, two lots with filled open price not in sequence order: \n->{lot}\n->{nextLot}",
                              self.verbose)
                        return True
            lot = nextLot

        # Check short side lots prices
        lot = self.startLot.prevLot
        while lot:
            shortLots += 1
            prevLot = lot.prevLot
            if lot.accruedLostPoints == 0 and lot.isNotRetainedLot() and prevLot:
                if lot.lotId <= prevLot.lotId:
                    return True  # lot id is not in order
                if lot.hasOpenPosition() and prevLot.hasOpenPosition():
                    if self.isMomentumMode() and lot.filledOpenPrice < prevLot.filledOpenPrice:
                        alert(f"{self.getNotifyPrefix()}: Skewed grid lots, following two lots with "
                              f"filled open price not in sequence order: \n->{lot}\n->{prevLot}")
                        return True
                    elif self.isContrarianMode() and lot.filledOpenPrice > prevLot.filledOpenPrice:
                        alert(f"{self.getNotifyPrefix()}: Skewed grid lots, following two lots with "
                              f"filled open price not in sequence order: \n->{lot}\n->{prevLot}")
                        return True
            lot = prevLot

        return longLots != self.gridLongLots or shortLots != self.gridShortLots

    def sortGridTradingLots(self):
        # Sort long side lots
        lot = self.startLot.nextLot
        while lot and lot.nextLot:
            prevLot = lot.prevLot
            if lot.isNotRetainedLot() and not areLotsInOrder(lot, lot.nextLot):
                swapGridLots(lot, lot.nextLot)
                log(f"{self.getSymbolAlias()}: Swapped lot {lot} with {lot.nextLot}.", self.verbose)
                if prevLot and prevLot.isLongLot():
                    lot = prevLot  # Back off one
                    continue
            lot = lot.nextLot
        # Sort short side lots
        lot = self.startLot.prevLot
        while lot and lot.prevLot:
            nextLot = lot.nextLot
            if lot.isNotRetainedLot() and not areLotsInOrder(lot, lot.prevLot):
                swapGridLots(lot, lot.prevLot)
                log(f"{self.getSymbolAlias()}: Swapped lot {lot} with {lot.nextLot}.", self.verbose)
                if nextLot and nextLot.isShortLot():
                    lot = nextLot  # Back off one
                    continue
            lot = lot.prevLot

    def getTotalNetProfitAmount(self):
        totalNetProfit = self.getUnrealizedProfitAmount()
        totalNetProfit += self.realizedProfitLoss
        return round(totalNetProfit, LIGlobal.moneyPrecision)

    def onSecurityChanged(self, removedSecurity: Security):
        self.initializeMetadata()
        self.liquidatedAlready = False
        if removedSecurity:
            if self.positionManager.isExchangeOpen():
                if removedSecurity == self.positionManager.getSecurity():
                    self.liquidateGridSession("SECURITY REMOVED", markRollover=True)
                else:
                    self.liquidateGridSecurity(removedSecurity, "SECURITY REMOVED", markRollover=True)
        else:
            # Following will be called by addSecurity()
            if self.isBoostingModeActivated():
                self.initBacktestStatus()
                self.cancelActiveOrders()
                self.manageGridBoosting()
                return  # Abort!
            if self.gridResetStartPrices is not None:  # Could be empty {}
                self.gridNoMoreOpenOrders = True
                self.gridNoMoreCloseOrders = True
                self.restartGridSession(startPrices=self.gridResetStartPrices)
                settings = f"{LIConfigKey.gridResetStartPrices}={self.gridResetStartPrices}"
                notify(f"{self.getNotifyPrefix()}: Stopped trading after reset start prices as {self.gridStartPrices}, please remove {settings} and redeploy!")
                return  # Abort!
            if self.startLot is None:
                self.startGridSession()
            elif not self.positionManager.isInvested():
                self.restartGridSession(reason="Add new security")

    def onData(self, data: Slice):
        # log(f"onData: {data}")
        pass

    def onEmitTradeInsight(self, tradeInsight: LITradeInsight):
        if self.isReadyToTrade:
            log(f"{self.getSymbolAlias()}: Received trade insight: {tradeInsight}")
            if self.isBoostingMode():
                self.manageGridBoosting(forceTrade=True)  # Trigger all related actions
            else:
                self.manageGridTrading(forceTrade=True)  # Trigger all related actions

    def restartGridSession(self, startPrices=None, reason=None):
        if self.isBoostingModeActivated():
            self.cancelActiveOrders()
            self.manageGridBoosting()
            return  # Abort
        self.sessionId += 1
        self.reachedOpenPrice = False
        self.liquidatedAlready = False
        self.sessionStartedTime = getAlgo().Time
        self.initializeGridLots()
        self.restartTradingLots(reason)
        self.deleteGridMetadata()
        self.resetGridStartPrices(startPrices, emptyStartPrices=True, emptyOpenFromPrices=True)
        self.cancelActiveOrders()
        self.manageGridTrading()
        self.printGridTargetPrices()
        self.printGridSession(withLots=True)

    def manageGridTrading(self, bar=None, forceTrade=False):
        if forceTrade:
            self.positionManager.enableTempTradable()

        marketPrice = self.getMarketPrice(bar)

        if self.gridOpenFromPrices:
            if not self.reachedOpenPrice and self.reachedOpenFromPrices(bar):
                self.resetGridStartPrices(emptyStartPrices=True)
                self.reachedOpenPrice = True  # Reset after restarted or liquidated!
                notify(f"{self.getNotifyPrefix()}: Start placing open orders as marketPrice={marketPrice} and "
                       f"{LIMetadataKey.startPrices}={self.gridStartPrices} reached {LIMetadataKey.openFromPrices}={self.gridOpenFromPrices}.")

        if self.bollingerBandsIndicator:
            newTierName = self.bollingerBandsIndicator.getTradingTierName(targetPrice=marketPrice)
            if self.tradingTierName != newTierName:
                log(f"{self.getSymbolAlias()}: Switching {LIMetadataKey.tradingTierName} from {self.tradingTierName} to {newTierName}.")
                self.tradingTierName = newTierName
                if self.monitorPeriodTierFactors:
                    tierFactorIndex = self.getTradingTierFactorIndex()
                    if self.gridLongLots:
                        self.gridMonitorPeriodFactors = {self.getGridLongSide(): self.monitorPeriodTierFactors[tierFactorIndex]}
                    if self.gridShortLots:
                        self.gridMonitorPeriodFactors = {self.getGridShortSide(): self.monitorPeriodTierFactors[tierFactorIndex]}

        if self.isGridTradingPaused() or self.manageGridLiquidation(bar):
            self.positionManager.disableTempTradable()
            return  # Abort upon trading paused or liquidated

        if self.gridSortSkewedLots and self.areGridLotsSkewed():
            self.sortGridTradingLots()

        # Do following standard procedures
        self.manageGridRollover()
        self.manageGridStartPrices(bar=bar)
        self.manageGridOrderTickets(bar=bar)

        self.lastTradingMarketPrice = marketPrice

        if forceTrade:
            self.positionManager.disableTempTradable()

    def manageGridOrderTickets(self, bar=None, openWithMarketOrder=False, closeWithMarketOrder=False):
        """
        Create or update/adjust trading lots order tickets, keep trading grid in consistency.
        This function should be able to run repeatably without any side effects or harms!!!
        :return: True if had any updates
        """
        hasAnyUpdates = False
        # log(f"{self.getSymbolAlias()}: isExchangeOpen={self.positionManager.isExchangeOpen()}")

        # Run some conditional operations
        self.manageLeakingPositions()

        bestBoostingLot = None
        # Loop through long grid lots
        if self.isLongSideActive():
            if (not self.gridMonitorPeriodFactors or (bar and
                                                      isTickTime(timestamp=bar.EndTime, delta=self.gridMonitorPeriodFactors.get(self.getGridLongSide(),
                                                                                                                                1) * self.getMonitorPeriodDelta()))):
                lot = self.startLot.nextLot
                while lot:
                    hasAnyUpdates = lot.manageLotOrderTickets(bar, openWithMarketOrder, closeWithMarketOrder) or hasAnyUpdates
                    if hasAnyUpdates:
                        liveSleep(3)  # Avoid stressing brokerage API and submitting duplicate tickets
                    if lot.isBoostingTriggered():
                        if not bestBoostingLot or bestBoostingLot.getProfitLossFactor() < lot.getProfitLossPoints(self.getMarketPrice()):
                            bestBoostingLot = lot
                    lot = lot.nextLot
        # Loop through short grid lots
        if self.isShortSideActive():
            if (not self.gridMonitorPeriodFactors or (bar and
                                                      isTickTime(timestamp=bar.EndTime, delta=self.gridMonitorPeriodFactors.get(self.getGridShortSide(),
                                                                                                                                1) * self.getMonitorPeriodDelta()))):
                lot = self.startLot.prevLot
                while lot:
                    hasAnyUpdates = lot.manageLotOrderTickets(bar, openWithMarketOrder, closeWithMarketOrder) or hasAnyUpdates
                    if hasAnyUpdates:
                        liveSleep(3)  # Avoid stressing brokerage API and submitting duplicate tickets
                    if lot.isBoostingTriggered():
                        if not bestBoostingLot or bestBoostingLot.getProfitLossFactor() < lot.getProfitLossPoints(self.getMarketPrice()):
                            bestBoostingLot = lot
                    lot = lot.prevLot

        # Boost more positions for the best profiting lot
        if bestBoostingLot:
            hasAnyUpdates = bestBoostingLot.manageLotOpenOrderTicket(boostMorePositions=True) or hasAnyUpdates

        # Cancel possible extra order
        self.cancelExtraOpenOrders()
        self.cancelExtraCloseOrders()

        # if hasAnyUpdates:
        #     self.printGridSession(withLots=True)

        return hasAnyUpdates

    def liquidateGridSession(self, reason, markRollover=False, markStopLoss=False):
        if foundLiquidationOrder(self.positionManager.getSecurity()):
            return False  # Abort
        if self.isBuyAndHoldMode():
            notify(f"Please liquidate positions manually as {LIConfigKey.gridMode}={self.gridMode}!")
            return  # Abort
        ordersCount = self.countOrderTickets()
        investedQuantity = self.getInvestedQuantity()
        self.storeGridMetadata()
        tradesCount = self.countAllTrades()
        filledLots = self.countFilledLots()
        investedCapital = self.getInvestedCapital()
        totalNetProfitAmount = self.getTotalNetProfitAmount()
        totalNetProfitPercent = self.getTotalNetProfitPercent()
        unrealizedProfitAmount = self.getUnrealizedProfitAmount()
        unrealizedProfitPercent = self.getUnrealizedProfitPercent()
        tagLog = f"{LITradeType.LIQUIDATE} grid trading session#{self.sessionId} as {reason}."
        liquidateSecurity(self.positionManager.getSecurity(), tagLog)
        self.liquidateByTrailingProfit = 0.0  # Reset trailing profit!
        self.liquidatedAlready = True
        if unrealizedProfitAmount or investedCapital or investedQuantity:
            self.realizedProfitLoss = round(self.realizedProfitLoss + unrealizedProfitAmount, LIGlobal.moneyPrecision)
            addDailyClosedTrade(self.canonicalSymbol.value, [unrealizedProfitAmount, 0, investedCapital, investedQuantity, 0])
        if markRollover:
            self.gridRolloverCriteria = (self.getSymbolValue(), filledLots[0], investedQuantity,
                                         unrealizedProfitAmount + self.rolloverProfitLoss)  # Mark to rollover in next session!
        else:
            self.rolloverProfitLoss = 0.0
        if markStopLoss:
            self.stoppedLossPrices[self.getGridTradingSide()] = self.getMarketPrice()
        else:
            self.stoppedLossPrices.pop(self.getGridTradingSide(), None)
        notifyMsg = f"{self.getNotifyPrefix()}: Liquidated due to {reason} and closed session#{self.sessionId}: " \
                    f"tradesCount={tradesCount}, " \
                    f"ordersCount={ordersCount}, " \
                    f"filledLots={filledLots[0]}, " \
                    f"investedQuantity={investedQuantity}, " \
                    f"investedCapital={investedCapital:.2f}, " \
                    f"totalNetProfit={totalNetProfitAmount:,.2f}({totalNetProfitPercent}%), " \
                    f"unrealizedProfit={unrealizedProfitAmount:,.2f}({unrealizedProfitPercent}%), " \
                    f"stoppedLossPrices={self.stoppedLossPrices}, rolloverCriteria={self.gridRolloverCriteria}. "
        notify(notifyMsg)
        return True

    def liquidateGridSecurity(self, security: Security, reason, markRollover=False, markStopLoss=False):
        if foundLiquidationOrder(security):
            return False  # Abort
        if self.isBuyAndHoldMode():
            notify(f"Please liquidate positions manually as {LIConfigKey.gridMode}={self.gridMode}!")
            return
        securityHolding = getAlgo().Portfolio[security.Symbol]
        investedQuantity = securityHolding.Quantity
        if not investedQuantity:
            log(f"{self.getSymbolAlias()}: No need to liquidate grid security {cleanSymbolValue(security.Symbol)} as investedQuantity={investedQuantity}.")
            return True
        filledLots = None
        if self.gridRolloverCriteria:
            filledLots = self.gridRolloverCriteria[0]
        # First, try to get filled lots from metadata
        if filledLots is None and self.gridLotsMetadata:
            filledLots = self.storedFilledLots()
            log(f"{self.getSymbolAlias()}: Got filledLots={filledLots} from {self.gridLotsMetadataKey}.")
        # Second, try to get filled lots based on closing orders
        if filledLots is None:
            for orderTicket in getAlgo().Transactions.GetOpenOrderTickets(security.Symbol):
                if orderTicket.OrderType == OrderType.Limit and isOrderTicketUpdatable(orderTicket):
                    if investedQuantity > 0 > orderTicket.Quantity:
                        filledLots = (0 if filledLots is None else filledLots) + 1
                    if investedQuantity < 0 < orderTicket.Quantity:
                        filledLots = (0 if filledLots is None else filledLots) - 1
            log(f"{self.getSymbolAlias()}: Got filledLots={filledLots} from {LITradeType.CLOSING} order tickets.")
        # Last, ask to specify the gridRolloverFilledLots manually
        if isLiveMode() and filledLots is None:  # Could be zero as specified by user
            alert(f"{self.getNotifyPrefix()}: Failed to figure out filled lots, please specify {LIConfigKey.gridRolloverCriteria}!")
            getAlgo().Quit("Quit algorithm on ROLLOVER QUANTITIES!")
            return  # Quit execution immediately!
        investedCapital = securityHolding.AbsoluteHoldingsCost
        unrealizedProfitAmount = securityHolding.UnrealizedProfit
        unrealizedProfitPercent = securityHolding.UnrealizedProfitPercent
        self.storeGridMetadata()
        tagLog = f"{LITradeType.LIQUIDATE} grid trading security {security.Symbol.Value} as {reason}."
        liquidateSecurity(security, tagLog)
        self.liquidateByTrailingProfit = 0.0  # Reset trailing profit!
        self.liquidatedAlready = True
        if unrealizedProfitAmount or investedCapital or investedQuantity:
            self.realizedProfitLoss = round(self.realizedProfitLoss + unrealizedProfitAmount, LIGlobal.moneyPrecision)
            addDailyClosedTrade(self.canonicalSymbol.value, [unrealizedProfitAmount, 0, investedCapital, investedQuantity, 0])
        if markRollover:
            self.gridRolloverCriteria = (self.getSymbolValue(), filledLots, investedQuantity,
                                         unrealizedProfitAmount + self.rolloverProfitLoss)  # Mark to rollover in next session!
        else:
            self.rolloverProfitLoss = 0.0
        if markStopLoss:
            self.stoppedLossPrices[self.getGridTradingSide()] = self.getMarketPrice()
        else:
            self.stoppedLossPrices.pop(self.getGridTradingSide(), None)
        notifyMsg = f"{self.getNotifyPrefix()}: Liquidated grid trading security {security.Symbol.Value} due to {reason}: " \
                    f"filledLots={filledLots}, " \
                    f"investedQuantity={investedQuantity}, " \
                    f"investedCapital={investedCapital:.2f}, " \
                    f"unrealizedProfit={unrealizedProfitAmount:,.2f}({unrealizedProfitPercent:.2f}%), " \
                    f"stoppedLossPrices={self.stoppedLossPrices}, rolloverCriteria={self.gridRolloverCriteria}."
        notify(notifyMsg)
        return True

    def isGridTradingPaused(self) -> bool:
        if self.pauseTradingTillTime:
            if self.pauseTradingTillTime > getAlgo().Time:
                log(f"{self.getSymbolAlias()}: Abort trading as {LIMetadataKey.pauseTradingTillTime}={self.pauseTradingTillTime.strftime(LIGlobal.secondFormat)}")
                return True  # True means still pause trading
            else:
                self.pauseTradingTillTime = None  # Reset
        return False  # False means resume trading

    def manageGridLiquidation(self, bar=None) -> bool:
        # Liquidate and stop trading on demand!
        if self.liquidateAndStopTrading:
            if not self.liquidatedAlready:
                self.liquidateGridSession(f"{LIConfigKey.liquidateAndStopTrading}={self.liquidateAndStopTrading}")
                notify(f"{self.getNotifyPrefix()}: Stopped trading as {LIConfigKey.liquidateAndStopTrading}={self.liquidateAndStopTrading}, "
                       f"please remove {LIConfigKey.liquidateAndStopTrading} to start a new session or keep stopping!")
                self.postLiquidationMetadata()
            return True  # Abort on demand
        marketPrice = self.getMarketPrice(bar)
        # countFilledLots = self.countFilledLots()
        unrealizedProfitAmount = self.getUnrealizedProfitAmount()
        unrealizedProfitPercent = self.getUnrealizedProfitPercent()
        if self.liquidatedAlready and isMarketCloseTime(getAlgo().time):
            return True  # Abort, avoid submitting duplicate orders!
        # Check whether it's a manual liquidation to take profit!
        # if not self.liquidatedAlready and (self.isBoostingMode() or self.countFilledLots() != 0) and self.getInvestedQuantity() == 0:
        #     tagLog = f"manual liquidation"
        #     self.liquidateGridSession(tagLog)
        #     if self.liquidateProfitAndRestartTrading:
        #         notify(f"{self.getNotifyPrefix()}: Restarted a new trading session after {tagLog}, "
        #                f"unrealizedProfit={unrealizedProfitAmount}({unrealizedProfitPercent}%), "
        #                f"please remove {LIConfigKey.liquidateOnReachedPrices} or redeploy ASAP!")
        #         self.restartGridSession()
        #     else:
        #         notify(f"{self.getNotifyPrefix()}: Stopped trading after {tagLog}, "
        #                f"unrealizedProfit={unrealizedProfitAmount}({unrealizedProfitPercent}%), "
        #                f"please remove or adjust {LIConfigKey.liquidateOnReachedPrices} and redeploy ASAP!")
        #         self.deleteGridMetadata()  # Next session will use fresh start prices
        #         self.saveMetadataAtEnd = False
        #         self.liquidateAndStopTrading = True
        #     return True
        # Liquidate on reached prices with profit: liquidate and stop or restart trading!
        if self.liquidateOnReachedPrices and unrealizedProfitAmount > 0:
            if (self.liquidateByTrailingProfit > 0 or
                    (self.getInvestedQuantity() > 0 and marketPrice >= self.liquidateOnReachedPrices[self.getGridLongSide()]) or
                    (self.getInvestedQuantity() < 0 and marketPrice <= self.liquidateOnReachedPrices[self.getGridShortSide()])):
                tagLog = f"marketPrice={marketPrice}"
                if self.getInvestedQuantity() > 0:
                    if self.liquidateByTrailingProfitPercent:
                        self.liquidateByTrailingProfit = self.positionManager.roundSecurityPrice(
                            max(marketPrice * (1 - self.liquidateByTrailingProfitPercent / 100),
                                self.liquidateByTrailingProfit if self.liquidateByTrailingProfit else sys.float_info.min))
                        if marketPrice > self.liquidateByTrailingProfit:
                            return False  # Abort, keep holding
                    tagLog += f" <= trailingStopPrice={self.liquidateByTrailingProfit}" if self.liquidateByTrailingProfit \
                        else f" >= reachedMinPrice={self.liquidateOnReachedPrices[self.getGridLongSide()]}"
                if self.getInvestedQuantity() < 0:
                    if self.liquidateByTrailingProfitPercent:
                        self.liquidateByTrailingProfit = self.positionManager.roundSecurityPrice(
                            min(marketPrice * (1 + self.liquidateByTrailingProfitPercent / 100),
                                self.liquidateByTrailingProfit if self.liquidateByTrailingProfit else sys.float_info.max))
                        if marketPrice < self.liquidateByTrailingProfit:
                            return False  # Abort, keep holding
                    tagLog += f" >= trailingStopPrice={self.liquidateByTrailingProfit}" if self.liquidateByTrailingProfit \
                        else f" <= reachedMaxPrice={self.liquidateOnReachedPrices[self.getGridShortSide()]}"
                self.liquidateGridSession(tagLog)
                if self.liquidateProfitAndRestartTrading:
                    notify(f"{self.getNotifyPrefix()}: Restarted a new trading session after liquidated due to {tagLog}, "
                           f"unrealizedProfit={unrealizedProfitAmount}({unrealizedProfitPercent}%), "
                           f"please remove {LIConfigKey.liquidateOnReachedPrices} or redeploy ASAP!")
                    # self.liquidateOnReachedPrices = None  # Not reset will restrict future trading within the range of reached prices
                    self.restartGridSession(reason="Restart after liquidation")
                else:
                    notify(f"{self.getNotifyPrefix()}: Stopped trading after liquidated due to {tagLog}, "
                           f"unrealizedProfit={unrealizedProfitAmount}({unrealizedProfitPercent}%), "
                           f"please remove or adjust {LIConfigKey.liquidateOnReachedPrices} and redeploy ASAP!")
                    self.liquidateAndStopTrading = True
                    self.postLiquidationMetadata()
                return True  # Abort on demand
        # Liquidate on take profit amount: liquidate and stop or restart trading!
        if self.getLiquidateOnTakeProfitAmount() and (self.liquidateByTrailingProfit > 0 or
                                                      0 < unrealizedProfitAmount >= self.getLiquidateOnTakeProfitAmount()):
            if self.liquidateByTrailingProfitPercent:
                self.liquidateByTrailingProfit = max(unrealizedProfitAmount * (1 - self.liquidateByTrailingProfitPercent / 100),
                                                     self.liquidateByTrailingProfit if self.liquidateByTrailingProfit else sys.float_info.min)
                self.liquidateByTrailingProfit = round(self.liquidateByTrailingProfit, LIGlobal.moneyPrecision)
                if unrealizedProfitAmount > self.liquidateByTrailingProfit:
                    return False  # Abort, keep holding
            tagLog = f"unrealizedProfit={unrealizedProfitAmount}({unrealizedProfitPercent}%)"
            tagLog += f" <= trailingStopProfitAmount={self.liquidateByTrailingProfit}" if self.liquidateByTrailingProfit \
                else f" >= takeProfitAmount={self.getLiquidateOnTakeProfitAmount()}"
            self.liquidateGridSession(tagLog)
            if self.liquidateProfitAndRestartTrading:
                notify(f"{self.getNotifyPrefix()}: Restarted a new trading session after liquidated due to {tagLog}, "
                       f"please remove {LIConfigKey.liquidateOnTakeProfitAmount} or keep as it is!")
                self.restartGridSession(reason="Restart after liquidation")
            else:
                notify(f"{self.getNotifyPrefix()}: Stopped trading after liquidated due to {tagLog}, "
                       f"{LIMetadataKey.liquidateByTrailingProfit}={self.liquidateByTrailingProfit}, "
                       f"please remove {LIConfigKey.liquidateOnTakeProfitAmount} and redeploy ASAP!")
                self.liquidateAndStopTrading = True
                self.postLiquidationMetadata()
            return True  # Abort on demand
        # Liquidate on take profit percent: liquidate and stop or restart trading!
        if self.liquidateOnTakeProfitPercent and (self.liquidateByTrailingProfit > 0 or
                                                  0 < unrealizedProfitPercent >= self.liquidateOnTakeProfitPercent):
            if self.liquidateByTrailingProfitPercent:
                self.liquidateByTrailingProfit = max(unrealizedProfitPercent - self.liquidateByTrailingProfitPercent,
                                                     self.liquidateByTrailingProfit if self.liquidateByTrailingProfit else sys.float_info.min)
                self.liquidateByTrailingProfit = round(self.liquidateByTrailingProfit, LIGlobal.percentPrecision)
                if unrealizedProfitPercent > self.liquidateByTrailingProfit:
                    return False  # Abort, keep holding
            tagLog = f"unrealizedProfit={unrealizedProfitPercent}%({unrealizedProfitAmount})"
            tagLog += f" <= trailingStopProfitPercent={self.liquidateByTrailingProfit}%" if self.liquidateByTrailingProfit \
                else f" >= takeProfitPercent={self.liquidateOnTakeProfitPercent}%"
            self.liquidateGridSession(tagLog)
            if self.liquidateProfitAndRestartTrading:
                notify(f"{self.getNotifyPrefix()}: Restarted a new trading session after liquidated due to {tagLog}, "
                       f"{LIMetadataKey.liquidateByTrailingProfit}={self.liquidateByTrailingProfit}%, "
                       f"please remove {LIConfigKey.liquidateOnTakeProfitPercent} or keep as it is!")
                self.restartGridSession(reason="Restart after liquidation")
            else:
                notify(f"{self.getNotifyPrefix()}: Stopped trading after liquidated due to {tagLog}, "
                       f"{LIMetadataKey.liquidateByTrailingProfit}={self.liquidateByTrailingProfit}%, "
                       f"please remove {LIConfigKey.liquidateOnTakeProfitPercent} and redeploy ASAP!")
                self.liquidateAndStopTrading = True
                self.postLiquidationMetadata()
            return True  # Abort on demand
        # Liquidate on stop loss amount: liquidate and stop or restart trading!
        if self.getLiquidateOnStopLossAmount() and 0 > unrealizedProfitAmount <= -abs(self.getLiquidateOnStopLossAmount()):
            tagLog = f"unrealizedProfit={unrealizedProfitAmount}({unrealizedProfitPercent}%) <= stopLossAmount=-{abs(self.getLiquidateOnStopLossAmount())}"
            self.liquidateGridSession(tagLog, markStopLoss=True)
            if self.liquidateLossAndRestartTrading:
                notify(f"{self.getNotifyPrefix()}: Restarted a new trading session after liquidated due to {tagLog}, "
                       f"please remove {LIConfigKey.liquidateOnStopLossAmount} or keep as it is!")
                self.restartGridSession(reason="Restart after liquidation")
            elif self.liquidateLossAndLimitTrading:
                notify(f"{self.getNotifyPrefix()}: Limit {self.getGridTradingSide()} side of trading after liquidated due to {tagLog}, "
                       f"will resume trading once market price revert back to {self.stoppedLossPrices}!")
                self.resetTradingLots(reason="Reset after stop loss liquidation")
                self.resetGridStartPrices(emptyStartPrices=True, emptyOpenFromPrices=True)
            else:
                notify(f"{self.getNotifyPrefix()}: Stopped trading after liquidated due to {tagLog}, "
                       f"please study market, adjust settings and redeploy ASAP!")
                self.liquidateAndStopTrading = True
                self.postLiquidationMetadata()
            return True  # Abort on demand
        # Liquidate on stop loss percent: liquidate and stop trading!
        if self.liquidateOnStopLossPercent and 0 > unrealizedProfitPercent <= -abs(self.liquidateOnStopLossPercent):
            tagLog = f"unrealizedProfit={unrealizedProfitPercent}%({unrealizedProfitAmount}) <= stopLossPercent=-{self.liquidateOnStopLossPercent}%"
            self.liquidateGridSession(tagLog, markStopLoss=True)
            if self.liquidateLossAndRestartTrading:
                notify(f"{self.getNotifyPrefix()}: Restarted a new trading session after liquidated due to {tagLog}, "
                       f"please remove {LIConfigKey.liquidateOnStopLossPercent}% or keep as it is!")
                self.restartGridSession(reason="Restart after liquidation")
            elif self.liquidateLossAndLimitTrading:
                notify(f"{self.getNotifyPrefix()}: Limit {self.getGridTradingSide()} side of trading after liquidated due to {tagLog}, "
                       f"will resume trading once market price revert back to {self.stoppedLossPrices}!")
                self.resetTradingLots(reason="Reset after stop loss liquidation")
                self.resetGridStartPrices(emptyStartPrices=True, emptyOpenFromPrices=True)
            else:
                notify(f"{self.getNotifyPrefix()}: Stopped trading after liquidated due to {tagLog}, "
                       f"please study market, adjust settings and redeploy ASAP!")
                self.liquidateAndStopTrading = True
                self.postLiquidationMetadata()
            return True  # Abort on demand
        # Restart if all lots on the same side have been paused!
        if self.gridRestartIfAllLotsPaused and not (self.isBoostingMode() or self.isBuyAndHoldMode()):
            allPausedSide = None
            if self.gridLongLots and self.countPausedLots(self.getFirstLongLot()) == self.gridLongLots:
                allPausedSide = "long"
            if self.gridShortLots and self.countPausedLots(self.getFirstShortLot()) == self.gridShortLots:
                allPausedSide = "short"
            if allPausedSide:
                notify(f"{self.getNotifyPrefix()}: Restarted a new trading session after liquidated due to all {allPausedSide} lots have been paused!")
                self.liquidateGridSession(f"gridRestartIfAllLotsPaused={self.gridRestartIfAllLotsPaused}")
                self.restartGridSession(reason="Restart after liquidation")
                return True  # Abort on demand
        return False  # Not liquidated at last!

    def postLiquidationMetadata(self):
        # self.deleteGridMetadata()  # Next session will use fresh start prices
        # self.saveMetadataAtEnd = False
        self.saveTradingMetadata(logging=True)
        notifyMsg = f"Liquidated this trading account {LIGlobal.algoName} with following metadata:\n\n"
        metadata = collectMetadata()
        for key in sorted(metadata.keys()):
            notifyMsg += f"{key}: \n{metadata[key]}\n\n"
        alert(notifyMsg, "Metadata")

    def getLiquidateOnStopLossAmount(self):
        if self.liquidateOnStopLossAmount:
            return self.liquidateOnStopLossAmount * self.getBaselineRatio()

    def getLiquidateOnTakeProfitAmount(self):
        takeProfitAmount = 0
        if self.liquidateOnTakeProfitAmount:
            takeProfitAmount = self.liquidateOnTakeProfitAmount
        elif self.liquidateOnTakeProfitAmounts:
            if self.getInvestedQuantity() >= 0:
                takeProfitAmount = self.liquidateOnTakeProfitAmounts[self.getGridLongSide()]
            else:
                takeProfitAmount = self.liquidateOnTakeProfitAmounts[self.getGridShortSide()]
        if self.takeProfitAmountTierFactors:
            takeProfitAmount *= self.takeProfitAmountTierFactors[self.getTradingTierFactorIndex()]
        takeProfitAmount *= self.getBaselineRatio()
        return takeProfitAmount

    def manageGridBoosting(self, bar=None, forceTrade=False):
        if forceTrade:
            self.positionManager.enableTempTradable()

        if self.isGridTradingPaused() or self.manageGridLiquidation(bar):
            if self.isBoostingMode():
                self.switchOffBoostingMode()
            self.positionManager.disableTempTradable()
            return False  # Abort upon trading paused or liquidated

        if not self.isBoostingModeActivated():
            self.positionManager.disableTempTradable()
            return False  # Abort, not triggered in boosting mode yet!

        if not self.positionManager.isExchangeOpen():
            return False  # Abort, wait for market open!

        self.manageBoostingOpenOrders()
        self.manageBoostingClosedOrders()

        if forceTrade:
            self.positionManager.disableTempTradable()

        return self.isBoostingMode()

    def isBoostingModeActivated(self):
        # Is it time to activate boosting mode?
        if not self.isBoostingMode():
            if self.isBoostingEffective():
                self.gridMode = LIGridMode.BOOSTING
                self.positionManager.cancelActiveOrders()
                self.storeGridMetadata()
                notify(f"{self.getNotifyPrefix()}: Activated the {LIGridMode.BOOSTING} mode as "
                       f"marketPrice={self.getMarketPrice()}, "
                       f"filledLots={self.countFilledLots()}, "
                       f"investedQuantity={self.getInvestedQuantity()}, "
                       f"avgProfitAmount={self.getAvgProfitAmount()}, "
                       f"avgProfitPercent={self.getAvgProfitPercent()}%!")
                return True
        return self.isBoostingMode()

    def manageBoostingOpenOrders(self):
        if not self.isBoostingMode():
            return False  # Abort, not in boosting mode yet!

        if self.gridNoMoreOpenOrders:
            log(f"{self.getSymbolAlias()}: Abort placing open order ticket as {LIConfigKey.gridNoMoreOpenOrders}={self.gridNoMoreOpenOrders}", self.verbose)
            return False  # Abort, no more open orders!

        if self.isBoostingEffective():
            investedQuantity = self.getInvestedQuantity()
            targetQuantity = min(self.investAmount.lotQuantity, abs(self.gridBoostingMaxHoldQuantity) - abs(investedQuantity))
            if investedQuantity < 0:
                targetQuantity = -targetQuantity

            if not targetQuantity:
                return False  # Abort, invalid target quantity!

            # Act according to trade insight
            if self.gridUseTradeInsight:
                tradeInsight = self.getTradeInsight()
                if not tradeInsight or tradeInsight.isNoneSignal():
                    return  # Abort as no signal yet!
                if tradeInsight.isLongSignal():
                    if targetQuantity < 0:
                        return  # Abort as against the Long signal
                elif tradeInsight.isShortSignal():
                    if targetQuantity > 0:
                        return  # Abort as against the Short signal
                else:
                    raise TypeError(f"Not support tradeInsight={tradeInsight}!")

            tradeType = LITradeType.OPENING_LIMIT
            if self.openWithMarketOrderType:
                tradeType = LITradeType.OPENING_LIMIT_MARKET if self.positionManager.enableLimitMarketOrder else LITradeType.OPENING_MARKET

            tagLog = f"{self.gridMode}: Submit {tradeType} order at targetQuantity={targetQuantity}, marketPrice={self.getMarketPrice()}."
            log(f"{self.getSymbolAlias()}@{tagLog}")
            if self.openWithMarketOrderType:
                self.openOrderTicket = self.positionManager.limitMarketOrder(targetQuantity, decorateTag(tagLog))
            else:
                self.openOrderTicket = getAlgo().LimitOrder(self.getSymbol(), targetQuantity, self.getMarketPrice(), tag=decorateTag(tagLog))
            self.fireOrderEvents(self.openOrderTicket)
            liveSleep(1)  # A little break
            return True

    def manageBoostingClosedOrders(self):
        if not self.isBoostingMode():
            return False  # Abort, not in boosting mode yet!

        marketPrice = self.getMarketPrice()
        investedQuantity = self.getInvestedQuantity()

        # Cancel closing order if not invested yet
        if not investedQuantity:
            if isOrderTicketUpdatable(self.closeOrderTicket):
                tagLog = f"{self.gridMode}: Cancel {LITradeType.CLOSING} order as not invested yet! tag=[{self.closeOrderTicket.Tag}]."
                if self.positionManager.cancelOrder(self.closeOrderTicket, tagLog):
                    self.closeOrderTicket = None
                    self.trailingStopPrice = None
                    self.closeOrderUpdatedTimes = 0
                    log(f"{self.getSymbolAlias()}@{tagLog}")
            return False  # Abort!

        # Act according to trade insight
        closePositionsNow = False
        if self.gridUseTradeInsight:
            tradeInsight = self.getTradeInsight()
            if not tradeInsight or tradeInsight.isNoneSignal():
                return  # Abort as no signal yet!
            if tradeInsight.isLongSignal():
                if investedQuantity < 0:
                    closePositionsNow = True
            elif tradeInsight.isShortSignal():
                if investedQuantity > 0:
                    closePositionsNow = True
            elif tradeInsight.isCloseSignal():
                closePositionsNow = True
            else:
                raise TypeError(f"Not support tradeInsight={tradeInsight}!")
            if closePositionsNow:
                log(f"{self.getSymbolAlias()}: Closing open positions now as investedQuantity={investedQuantity} against tradeInsight={tradeInsight}.",
                    self.verbose)

        # Calculate dynamic stop profit amount or percent
        stopProfitAmount = None
        stopProfitPercent = None
        if self.gridBoostingStopProfitAmounts:
            stopProfitAmount = getDistributedValue(abs(self.getInvestedQuantity()), self.gridBoostingMaxHoldQuantity, self.gridBoostingStopProfitAmounts)
        if self.gridBoostingStopProfitPercents:
            stopProfitPercent = getDistributedValue(abs(self.getInvestedQuantity()), self.gridBoostingMaxHoldQuantity, self.gridBoostingStopProfitPercents)

        # Calculate new trailing stop price accordingly
        isProfitable = False
        submitTrailingStopOrder = False
        targetQuantity = -investedQuantity
        averagePrice = self.positionManager.getAveragePrice()
        if not closePositionsNow and self.gridBoostingTrailingStopQuantity and abs(targetQuantity) >= self.gridBoostingTrailingStopQuantity:
            submitTrailingStopOrder = True
        if investedQuantity > 0:
            stopPrice = max(averagePrice, marketPrice)
            if stopProfitAmount:
                stopPrice = stopPrice - stopProfitAmount
            elif stopProfitPercent:
                stopPrice = stopPrice * (1 - stopProfitPercent / 100)
            stopPrice = max(averagePrice, stopPrice)
            self.trailingStopPrice = max(stopPrice, self.trailingStopPrice if self.trailingStopPrice else sys.float_info.min)
            isProfitable = marketPrice > self.trailingStopPrice > averagePrice
        elif investedQuantity < 0:
            stopPrice = min(averagePrice, marketPrice)
            if stopProfitAmount:
                stopPrice = stopPrice + stopProfitAmount
            elif stopProfitPercent:
                stopPrice = stopPrice * (1 + stopProfitPercent / 100)
            stopPrice = min(averagePrice, stopPrice)
            self.trailingStopPrice = min(stopPrice, self.trailingStopPrice if self.trailingStopPrice else sys.float_info.max)
            isProfitable = marketPrice < self.trailingStopPrice < averagePrice
        self.trailingStopPrice = self.positionManager.roundSecurityPrice(self.trailingStopPrice)

        # Sort out trade type and trailing stop prices
        stopProfitLevelMsg = None
        trailingStopPrices = None  # 3 items tuple
        if stopProfitAmount:
            stopProfitLevelMsg = f"stopProfitAmount={stopProfitAmount}"
            if submitTrailingStopOrder:
                trailingStopPrices = (self.trailingStopPrice, stopProfitAmount, False)
        elif stopProfitPercent:
            stopProfitLevelMsg = f"stopProfitPercent={stopProfitPercent}"
            if submitTrailingStopOrder:
                trailingStopPrices = (self.trailingStopPrice, stopProfitPercent / 100, True)
        tradeType = LITradeType.CLOSING_LIMIT
        if self.closeWithMarketOrderType:
            tradeType = LITradeType.CLOSING_LIMIT_MARKET if self.positionManager.enableLimitMarketOrder else LITradeType.CLOSING_MARKET
        if trailingStopPrices:
            tradeType = LITradeType.CLOSING_STOP_PROFIT if isProfitable else LITradeType.CLOSING_STOP_LOSS
            if submitTrailingStopOrder:
                tradeType = LITradeType.CLOSING_TRAILING_STOP_PROFIT if isProfitable else LITradeType.CLOSING_TRAILING_STOP_LOSS

        # Submit or update close order ticket
        self.avgFilledOpenPrice = averagePrice  # Save it before positions closed!
        if submitTrailingStopOrder:
            stopPricesMsg = f"trailingStopPrices={printTrailingStopPrices(trailingStopPrices, False)}"
            if self.closeOrderTicket is None:
                self.closeOrderUpdatedTimes = 0
                tagLog = (f"{self.gridMode}: Submit {tradeType} order, targetQuantity={targetQuantity}, "
                          f"marketPrice={marketPrice}, averagePrice={averagePrice}, {stopPricesMsg}, {stopProfitLevelMsg}.")
                log(f"{self.getSymbolAlias()}@{tagLog}")
                self.closeOrderTicket = getAlgo().TrailingStopOrder(self.getSymbol(), quantity=targetQuantity, stopPrice=trailingStopPrices[0],
                                                                    trailingAmount=trailingStopPrices[1], trailingAsPercentage=trailingStopPrices[2],
                                                                    tag=decorateTag(tagLog))
            elif isOrderTicketUpdatable(self.closeOrderTicket):
                if self.closeOrderTicket.OrderType in [OrderType.MARKET, OrderType.MARKET_ON_OPEN, OrderType.MARKET_ON_CLOSE]:
                    return False  # Abort, waiting for market open or order to be filled
                updateFields = UpdateOrderFields()
                needToUpdate = False
                if self.closeOrderTicket.Quantity != targetQuantity:
                    updateFields.Quantity = targetQuantity
                    needToUpdate = True
                if self.closeOrderTicket.OrderType == OrderType.TrailingStop:
                    if self.closeOrderTicket.Get(OrderField.TrailingAmount) != trailingStopPrices[1]:
                        updateFields.TrailingAmount = trailingStopPrices[1]
                        needToUpdate = True
                if needToUpdate:
                    self.closeOrderUpdatedTimes += 1
                    tagLog = (f"{self.gridMode}: Update {tradeType} order @{self.closeOrderUpdatedTimes}, targetQuantity={targetQuantity}, "
                              f"marketPrice={marketPrice}, averagePrice={averagePrice}, {stopPricesMsg}, {stopProfitLevelMsg}.")
                    log(f"{self.getSymbolAlias()}@{tagLog}", self.verbose)
                    updateFields.Tag = decorateTag(tagLog)
                    orderResponse = self.closeOrderTicket.Update(updateFields)
                    if orderResponse and orderResponse.IsError:
                        notify(f"{self.getNotifyPrefix()}: Failed to update close order ticket fields: {orderResponse}, tag=[{self.closeOrderTicket.Tag}].")
            else:
                alert(f"{self.getNotifyPrefix()}: The close order ticket is NOT updatable as expected: {self.closeOrderTicket}.")
            return isOrderTicketUpdatable(self.closeOrderTicket)
        elif isOrderTicketUpdatable(self.closeOrderTicket) and self.closeOrderTicket.OrderType in [OrderType.LIMIT]:
            if self.closeOrderTicket.Get(OrderField.LimitPrice) != marketPrice:
                self.closeOrderUpdatedTimes += 1
                updateFields = UpdateOrderFields()
                tagLog = (f"{self.gridMode}: Update {tradeType} order @{self.closeOrderUpdatedTimes}, targetQuantity={targetQuantity}, "
                          f"marketPrice={marketPrice}, averagePrice={averagePrice}, {stopProfitLevelMsg}.")
                log(f"{self.getSymbolAlias()}@{tagLog}", self.verbose)
                updateFields.LimitPrice = marketPrice
                updateFields.Tag = decorateTag(tagLog)
                orderResponse = self.closeOrderTicket.Update(updateFields)
                if orderResponse and orderResponse.IsError:
                    notify(f"{self.getNotifyPrefix()}: Failed to update close order ticket fields: {orderResponse}, tag=[{self.closeOrderTicket.Tag}].")
        else:
            # log(f"{self.getSymbolAlias()}: marketPrice={marketPrice}, stopLimitPrice={stopLimitPrices}.")
            if (closePositionsNow or
                    (investedQuantity > 0 and self.trailingStopPrice >= marketPrice) or
                    (investedQuantity < 0 and self.trailingStopPrice <= marketPrice)):
                tagLog = (f"{self.gridMode}: Submit {tradeType} order, targetQuantity={targetQuantity}, marketPrice={marketPrice}, "
                          f"averagePrice={averagePrice}, trailingStopPrice={self.trailingStopPrice}, {stopProfitLevelMsg}.")
                log(f"{self.getSymbolAlias()}@{tagLog}")
                # self.closeOrderTicket = self.limitOrder(targetQuantity, softLimitPrice, tagLog)
                # TEST: It performs better with limit market order than stop limit order at this point!
                if self.closeWithMarketOrderType:
                    self.closeOrderTicket = self.positionManager.limitMarketOrder(targetQuantity, tagLog)
                    self.fireOrderEvents(self.closeOrderTicket)
                else:
                    self.closeOrderTicket = getAlgo().LimitOrder(self.getSymbol(), targetQuantity, marketPrice, tag=decorateTag(tagLog))
                return True

    def isBoostingEffective(self):
        return ((self.gridBoostingTriggerAmount and self.gridBoostingTriggerAmount < self.getAvgProfitAmount()) or
                (self.gridBoostingTriggerPercent and self.gridBoostingTriggerPercent < self.getAvgProfitPercent()))

    def reachedOpenFromPrices(self, bar):
        marketPrice = self.getMarketPrice(bar)
        middlePrice = None
        if self.tradeBothSides():
            middlePrice = (self.gridOpenFromPrices[self.getGridLongSide()] + self.gridOpenFromPrices[self.getGridShortSide()]) / 2
        elif self.gridLongLots:
            middlePrice = self.gridOpenFromPrices[self.getGridLongSide()]
        elif self.gridShortLots:
            middlePrice = self.gridOpenFromPrices[self.getGridShortSide()]
        if self.isMomentumMode():
            if marketPrice >= middlePrice and self.getGridLongSide() in self.gridOpenFromPrices:
                return marketPrice > self.gridOpenFromPrices[self.getGridLongSide()]
            if marketPrice < middlePrice and self.getGridShortSide() in self.gridOpenFromPrices:
                return marketPrice < self.gridOpenFromPrices[self.getGridShortSide()]
        elif self.isContrarianMode():
            if marketPrice <= middlePrice and self.getGridLongSide() in self.gridOpenFromPrices:
                return marketPrice < self.gridOpenFromPrices[self.getGridLongSide()]
            if marketPrice > middlePrice and self.getGridShortSide() in self.gridOpenFromPrices:
                return marketPrice > self.gridOpenFromPrices[self.getGridShortSide()]
        return True  # By default

    def initBacktestStatus(self):
        storedInvestedQuantity = self.gridMetadata.get(LIMetadataKey.investedQuantity, 0)
        diffQuantity = storedInvestedQuantity - self.getInvestedQuantity()
        if isNotLiveMode() and diffQuantity != 0:
            tagLog = f"Fulfill backtest with {diffQuantity} open positions at market order!"
            getAlgo().MarketOrder(self.getSymbol(), diffQuantity, tag=decorateTag(tagLog))
            log(f"{self.getSymbolAlias()}: {tagLog}")
            if storedInvestedQuantity != self.getInvestedQuantity():
                error(f"Failed to fulfill {diffQuantity} open positions for backtest!")

    def cancelActiveOrders(self):
        """ Cancel open order tickets for once if required!"""
        if not self.positionManager.isExchangeOpen():
            return  # Abort, wait for market open!
        self.positionManager.cancelActiveOrders()

    def cancelExtraOpenOrders(self):
        """
        It's possible to submitted more/extra open orders during the course of trading session.
        """
        if not self.positionManager.isExchangeOpen():
            return  # Abort, wait for market open!
        if self.gridLongLots > 0:
            openOrders = 0
            lot = self.startLot.nextLot
            while lot:
                if lot.hasOpenOrderTicket():
                    openOrders += 1
                if openOrders > self.gridMaintainOpenOrders:
                    # self.printGridSession(withLots=True)
                    lot.cancelOpenOrderTicket(
                        f"Cancel extra {LITradeType.OPENING} order tickets as openOrders={self.countOpenOrders(peerLot=lot)}>{self.gridMaintainOpenOrders}.")
                    lot.lotStatus = LILotStatus.IDLING
                lot = lot.nextLot
        if self.gridShortLots > 0:
            openOrders = 0
            lot = self.startLot.prevLot
            while lot:
                if lot.hasOpenOrderTicket():
                    openOrders += 1
                if openOrders > self.gridMaintainOpenOrders:
                    # self.printGridSession(withLots=True)
                    lot.cancelOpenOrderTicket(
                        f"Cancel extra {LITradeType.OPENING} order tickets as openOrders={self.countOpenOrders(peerLot=lot)}>{self.gridMaintainOpenOrders}.")
                    lot.lotStatus = LILotStatus.IDLING
                lot = lot.prevLot

    def cancelExtraCloseOrders(self):
        """
        It's possible to submitted more/extra close orders during the course of trading session.
        """
        if not self.positionManager.isExchangeOpen():
            return  # Abort, wait for market open!
        if self.isLongSideActive():
            # Check possible close orders from the start lot first
            closingOrders = 0
            lastGridLot = self.startLot
            while lastGridLot:
                if not lastGridLot.isRetainedLot() and not lastGridLot.isBoostingLot() and lastGridLot.hasCloseOrderTicket():
                    closingOrders += 1
                    if closingOrders >= self.gridKeepStartCloseOrders:
                        break
                lastGridLot = lastGridLot.nextLot
            # Check possible close orders from the last lot for the rest
            lot = self.getLastLongLot()
            while lot and lot.isLongLot() and lot != lastGridLot:
                if lot.isNotRetainedLot() and not lot.isBoostingLot() and lot.hasCloseOrderTicket():
                    closingOrders += 1
                    if closingOrders > self.gridMaintainCloseOrders:
                        if lot.closeOrderTicket.OrderType == OrderType.Limit:
                            lot.closeOrderPrice = lot.closeOrderTicket.Get(OrderField.LimitPrice)
                        elif lot.closeOrderTicket.OrderType == OrderType.StopLimit:
                            lot.stopOrderPrice = lot.closeOrderTicket.Get(OrderField.StopPrice)
                            lot.closeOrderPrice = lot.closeOrderTicket.Get(OrderField.LimitPrice)
                        elif lot.closeOrderTicket.OrderType == OrderType.StopMarket:
                            lot.stopOrderPrice = lot.closeOrderTicket.Get(OrderField.StopPrice)
                        elif lot.closeOrderTicket.OrderType == OrderType.TrailingStop:
                            lot.stopOrderPrice = lot.closeOrderTicket.Get(OrderField.StopPrice)
                            lot.trailingAmount = lot.closeOrderTicket.Get(OrderField.TrailingAmount)
                        lot.closeOrderQuantity = lot.closeOrderTicket.Quantity
                        lot.cancelCloseOrderTicket(
                            f"Cancel extra {LITradeType.CLOSING} order ticket as closingOrders={self.countCloseOrders(peerLot=lot)}>{self.gridMaintainCloseOrders}.")
                        lot.lotStatus = LILotStatus.CLOSING
                lot = lot.prevLot
        if self.isShortSideActive():
            # Check possible close orders from the start lot first
            closingOrders = 0
            lastGridLot = self.startLot
            while lastGridLot:
                if not lastGridLot.isRetainedLot() and not lastGridLot.isBoostingLot() and lastGridLot.hasCloseOrderTicket():
                    closingOrders += 1
                    if closingOrders >= self.gridKeepStartCloseOrders:
                        break
                lastGridLot = lastGridLot.prevLot
            # Check possible close orders from the last lot for the rest
            lot = self.getLastShortLot()
            while lot and lot.isShortLot() and lot != lastGridLot:
                if lot.isNotRetainedLot() and not lot.isBoostingLot() and lot.hasCloseOrderTicket():
                    closingOrders += 1
                    if closingOrders > self.gridMaintainCloseOrders:
                        if lot.closeOrderTicket.OrderType == OrderType.Limit:
                            lot.closeOrderPrice = lot.closeOrderTicket.Get(OrderField.LimitPrice)
                        elif lot.closeOrderTicket.OrderType == OrderType.StopLimit:
                            lot.stopOrderPrice = lot.closeOrderTicket.Get(OrderField.StopPrice)
                            lot.closeOrderPrice = lot.closeOrderTicket.Get(OrderField.LimitPrice)
                        elif lot.closeOrderTicket.OrderType == OrderType.StopMarket:
                            lot.stopOrderPrice = lot.closeOrderTicket.Get(OrderField.StopPrice)
                        elif lot.closeOrderTicket.OrderType == OrderType.TrailingStop:
                            lot.stopOrderPrice = lot.closeOrderTicket.Get(OrderField.StopPrice)
                            lot.trailingAmount = lot.closeOrderTicket.Get(OrderField.TrailingAmount)
                        lot.closeOrderQuantity = lot.closeOrderTicket.Quantity
                        lot.cancelCloseOrderTicket(
                            f"Cancel extra {LITradeType.CLOSING} order ticket as closingOrders={self.countCloseOrders(peerLot=lot)}>{self.gridMaintainCloseOrders}.")
                        lot.lotStatus = LILotStatus.CLOSING
                lot = lot.nextLot

    def manageGridRollover(self):
        """Rollover, force to fill the same amount of lots with market price!"""
        if not self.positionManager.isExchangeOpen():
            return  # Abort, wait for market open!
        if not self.gridRolloverCriteria:
            return  # Abort, not required to rollover!
        # Rollover grid metadata
        toPrefix = self.getMetadataKeyPrefix()
        fromPrefix = toPrefix.replace(self.getSymbolValue(), self.gridRolloverCriteria[0])
        rolloverMetadata(fromPrefix, toPrefix)
        self.gridMetadata: dict = readMetadata(self.gridMetadataKey, "dict", default={})
        self.gridLotsMetadata: dict = readMetadata(self.gridLotsMetadataKey, "dict", default={})
        self.restoreGridMetadata(postRollover=True)
        self.rolloverProfitLoss = self.gridRolloverCriteria[3]
        # Rollover holding positions
        if self.gridRolloverCriteria[2] > 0 and not self.positionManager.isInvested():  # Skip if already invested!
            limitStartPrices = f", limitStartPrices={self.gridLimitStartPrices}" if self.gridLimitStartPrices else ""
            fixedStartPrices = f", fixedStartPrices={self.gridFixedStartPrices}" if self.gridFixedStartPrices else ""
            tagLog = f"Rolled over {self.gridRolloverCriteria} with marketPrice={self.getMarketPrice()}{limitStartPrices}{fixedStartPrices}"
            orderTicket = self.positionManager.limitMarketOrder(self.gridRolloverCriteria[2], tagLog)
            retainStartPrices = self.manageGridStartPrices(retainOpenedLots=self.gridRolloverCriteria[1], filledMarketPrice=orderTicket.AverageFillPrice,
                                                           overwriteStartPrices=False)  # Keep tracking max/min start prices
            filledQuantity = f", filledQuantity={orderTicket.Quantity}" if orderTicket else ""
            avgFilledPrice = f", avgFilledPrice={orderTicket.AverageFillPrice}" if orderTicket else ""
            retainStartPrices = f", retainStartPrices={retainStartPrices}" if retainStartPrices else ""
            notify(f"{self.getNotifyPrefix()}: {tagLog}{avgFilledPrice}{filledQuantity}{retainStartPrices} and final {self.printGridPrices()}!")
        self.gridRolloverCriteria = None  # Mark it completed!

    def getAugmentedAmount(self, lotIdFactor):
        return self.gridLotLevelAmount * self.getBaselineRatio() + self.gridLotLevelAugment * (abs(lotIdFactor) - 1)

    def getAugmentedPercent(self, lotIdFactor):
        return self.gridLotLevelPercent + self.gridLotLevelAugment * (abs(lotIdFactor) - 1)

    def getBaselineRatio(self):
        return self.getMarketPrice() / self.gridBaselinePrice if self.gridBaselinePrice else 1

    def onWarmupFinished(self):
        super().onWarmupFinished()

    def onBrokerageReconnect(self):
        super().onBrokerageReconnect()

    def fireOrderEvents(self, orderTicket: OrderTicket):
        # NOTE: this fire order events could cause "maximum recursion depth exceeded" for option trading
        # Only need to fire order evens for market order in backtest mode!!!
        # if orderTicket.OrderType == OrderType.Market:
        for orderEvent in orderTicket.OrderEvents:
            self.onOrderEvent(orderEvent)
            orderEvent.OrderId *= -1  # Avoid repeating order event

    def onOrderEvent(self, orderEvent: OrderEvent):
        filledAnyOrder = False
        if orderEvent.Status == OrderStatus.Invalid:
            self.invalidOrderCount += 1
            if self.invalidOrderCount == 1:  # Only alert once!
                alert(f"{self.getNotifyPrefix()}: Received invalid order event: {orderEvent}")
        if self.isBoostingMode():
            filledAnyOrder = self.onOpenOrderEvent(orderEvent) or self.onCloseOrderEvent(orderEvent)
        else:
            lot = self.getTradeLot()
            while lot:
                filledAnyOrder = lot.onOrderEvent(orderEvent) or filledAnyOrder
                lot = lot.getNextLot()
        if filledAnyOrder:
            # self.saveSessionMetadata(False)
            # self.printGridSession(withLots=False)
            # TEST: It performs worse a bit with this immediate refresh
            # self.manageGridOrderTickets()
            pass

    def onOpenOrderEvent(self, orderEvent):
        if self.openOrderTicket and self.openOrderTicket.OrderId == orderEvent.OrderId:
            if orderEvent.Status == OrderStatus.Submitted:
                return True
            elif orderEvent.Status == OrderStatus.Canceled or orderEvent.Status == OrderStatus.Invalid:
                self.openOrderTicket = None
                return True
            elif orderEvent.Status == OrderStatus.PartiallyFilled:
                self.accruedFees += orderEvent.OrderFee.Value.Amount
                return True
            elif orderEvent.Status == OrderStatus.Filled:
                '''Can get info from either order event or order ticket'''
                filledOpenPrice = self.openOrderTicket.AverageFillPrice if self.openOrderTicket else orderEvent.FillPrice
                filledOpenPrice = self.positionManager.roundSecurityPrice(filledOpenPrice)
                filledOpenQuantity = self.openOrderTicket.QuantityFilled if self.openOrderTicket else orderEvent.FillQuantity
                self.accruedFees += orderEvent.OrderFee.Value.Amount
                orderEvent.FillPrice = filledOpenPrice  # Overwrite with average fill price
                orderEvent.FillQuantity = filledOpenQuantity  # Overwrite with actual fill quantity
                orderEvent.Quantity = filledOpenQuantity  # Overwrite with actual fill quantity
                orderEvent.OrderFee.Value = CashAmount(self.accruedFees, orderEvent.OrderFee.Value.Currency)  # Overwrite with all open orders' fees
                additionalMsgs = f"totalProfitLoss={self.getMaxProfitLossAmount()}({self.getMaxProfitLossPercent()}%)"
                self.positionManager.notifyOrderFilled(orderEvent, netProfit=0, additionalMsgs=additionalMsgs, delayMaxMsgs=3)
                self.accruedFees = 0.0
                self.openOrderTicket = None
                self.avgFilledOpenPrice = self.positionManager.getAveragePrice()  # Save it before positions closed!
                if self.isBoostingMode():
                    self.manageGridBoosting(forceTrade=True)  # Trigger all related actions
                else:
                    self.manageGridTrading(forceTrade=True)  # Trigger all related actions
                return True

    def onCloseOrderEvent(self, orderEvent):
        delayMaxMsgs = 0 if self.isBoostingMode() else 0
        if self.closeOrderTicket and self.closeOrderTicket.OrderId == orderEvent.OrderId:
            if orderEvent.Status == OrderStatus.Submitted:
                return True
            elif orderEvent.Status == OrderStatus.Canceled or orderEvent.Status == OrderStatus.Invalid:
                self.closeOrderTicket = None
                return True
            elif orderEvent.Status == OrderStatus.PartiallyFilled:
                self.accruedFees += orderEvent.OrderFee.Value.Amount
                return True
            elif orderEvent.Status == OrderStatus.Filled:
                filledPrice = self.closeOrderTicket.AverageFillPrice if self.closeOrderTicket else orderEvent.FillPrice
                filledQuantity = self.closeOrderTicket.QuantityFilled if self.closeOrderTicket else orderEvent.FillQuantity
                profitLossPoints = (filledPrice - self.avgFilledOpenPrice) * (1 if filledQuantity < 0 else -1)
                profitLoss = round(profitLossPoints * abs(filledQuantity) * self.positionManager.getSecurityMultiplier(), LIGlobal.moneyPrecision)
                self.accruedFees += orderEvent.OrderFee.Value.Amount
                quantity = abs(filledQuantity)
                capital = round(quantity * getMaintenanceMargin(self.getSymbol(), filledPrice), LIGlobal.moneyPrecision)
                duration = 0
                netProfit = round(profitLoss - self.accruedFees, LIGlobal.moneyPrecision)  # Use local calculated value
                orderEvent.FillPrice = filledPrice  # Overwrite with average fill price
                orderEvent.FillQuantity = filledQuantity  # Overwrite with actual fill quantity
                orderEvent.Quantity = filledQuantity  # Overwrite with actual fill quantity
                orderEvent.OrderFee.Value = CashAmount(self.accruedFees / 2, orderEvent.OrderFee.Value.Currency)  # Overwrite with all close orders' fees
                self.realizedProfitLoss = round(self.realizedProfitLoss + netProfit, LIGlobal.moneyPrecision)
                self.closedTradesCount += 1
                additionalMsgs = f"totalProfitLoss={self.getMaxProfitLossAmount()}({self.getMaxProfitLossPercent()}%)"
                self.positionManager.notifyOrderFilled(orderEvent, netProfit=netProfit, additionalMsgs=additionalMsgs, delayMaxMsgs=delayMaxMsgs)
                addDailyClosedTrade(self.canonicalSymbol.value, [profitLoss, self.accruedFees, capital, quantity, duration])
                self.accruedFees = 0.0
                self.realizedProfitLoss = 0.0
                self.closeOrderTicket = None
                self.trailingStopPrice = None
                self.avgFilledOpenPrice = None
                if self.gridPauseTradingProfitHours and netProfit > self.gridPauseTradingProfitHours[0]:
                    self.pauseTradingTillTime = getAlgo().Time + timedelta(days=self.gridPauseTradingProfitHours[1])
                if self.isBoostingMode():
                    self.switchOffBoostingMode()
                return True

    def switchOffBoostingMode(self):
        # It's time to switch back to origin mode
        self.gridMode = self.gridInitMode
        self.storeGridMetadata()
        self.restartGridSession(reason="Switch off Boosting Mode")
        if self.gridBoostingKeepTrading:
            self.liquidateAndStopTrading = False
        else:
            self.liquidateAndStopTrading = True
            notify(f"{self.getNotifyPrefix()}: Paused trading after liquidated the boosting mode, please plan to redeploy and continue grid trading.")

    def onMarginCall(self, requests: List[SubmitOrderRequest]) -> List[SubmitOrderRequest]:
        if self.liquidateOnMarginCall:
            for i, order in enumerate(requests):
                if self.getSymbol() == order.Symbol:
                    self.liquidateGridSession("MARGIN CALLED")
                    newQuantity = 0  # Already liquidated grid session!
                    requests[i] = SubmitOrderRequest(order.OrderType, order.SecurityType,
                                                     order.Symbol, newQuantity, order.StopPrice,
                                                     order.LimitPrice, 0, getAlgo().Time, "Already liquidated on margin call!")
                    getAlgo().Quit("Quit algorithm upon margin call, please adjust settings and redeploy!")
        return requests

    def onCloseOfMarket(self):
        if getAlgo().Time.weekday() == 4:
            if self.liquidateOnFridayClose:
                self.liquidateGridSession("FRIDAY CLOSE")
                if self.gridRestartOnFridayClose:
                    self.restartGridSession(reason="Restart on FRIDAY CLOSE")
        super().onCloseOfMarket()

    def onEndOfDay(self, symbol: Symbol):
        if symbol == self.getSymbol():
            if self.saveMetadataAtEnd and isLiveMode():
                self.storeGridMetadata(logging=False)
            if self.gridRealignForMaxHolding and self.investAmount.maxHolding:
                self.realignOpenPositions(forceOnDemand=True, resetFilledLots=True)
                # self.realignOpenPositions(forceOnDemand=True, resetFilledLots=False)
            super().onEndOfDay(symbol)

    def onEndOfAlgorithm(self):
        if self.startLot:
            self.printGridSession()
        if self.gridCancelOrdersOnExit:
            self.cancelActiveOrders()
        if self.gridMetadataKey and self.saveMetadataAtEnd:
            self.storeGridMetadata()
        super().onEndOfAlgorithm()

    def printGridPrices(self):
        result = f"startPrices={self.gridStartPrices}"
        if self.gridOpenFromPrices:
            result += f", openFromPrices={self.gridOpenFromPrices}"
        if self.bollingerBandsIndicator:
            result += f", allBandPrices={self.bollingerBandsIndicator.getBandPrices()}"
        return result

    def printGridSession(self, withLots=True):
        result = (
            f"{self.getSymbolAlias()}: Session#{self.sessionId}, gridLots={self.countTradeLots()}, filledLots={self.countFilledLots()}, "
            f"pausedLots={self.countPausedLots()}, {self.printGridPrices()}, tradesCount={self.countAllTrades()}, "
            f"totalNetProfit={self.getTotalNetProfitAmount()}, ordersCount={self.countOrderTickets()}, openOrdersCount={self.countOpenOrders()}, "
            f"closeOrdersCount={self.countCloseOrders()}, closingQuantity={self.positionManager.roundSecuritySize(self.getClosingQuantity())}, "
            f"investedQuantity={self.getInvestedQuantity()}, investedCapital={self.getInvestedCapital()}, holdingCost={self.positionManager.getHoldingCost()}, "
            f"maintenanceMargin={self.positionManager.getMaintenanceMargin()}, averagePrice={self.positionManager.getAveragePrice()}, "
            f"avgProfitAmount={self.getAvgProfitAmount()}, avgProfitPercent={self.getAvgProfitPercent()}%, "
            f"unrealizedProfit={self.getUnrealizedProfitAmount()}({self.getUnrealizedProfitPercent()}%).")
        if withLots and self.countFilledLots()[0]:
            result += f" {self.countFilledLots()[0]} filled opening lots: "
            lot = self.getTradeLot()
            while lot:
                if lot.hasOpenPosition() or lot.hasOrderTickets():
                    result += f"\n\t{lot}"
                lot = lot.getNextLot()
        log(result)

    def printGridTargetPrices(self):
        targetPrices = []
        printHeadTailLots = 0
        tradeLots = self.countTradeLots()
        lot = self.getTradeLot()
        ellipsis = "#...lots..."
        while lot:
            if printHeadTailLots and printHeadTailLots < abs(lot.lotId) < (tradeLots[1] if lot.isLongLot() else tradeLots[2]) - printHeadTailLots:
                if targetPrices and targetPrices[-1] != ellipsis:
                    targetPrices.append(ellipsis)
            else:
                openPrice = lot.getOpenTargetPrice()
                closePrice = lot.getCloseTargetPrice()
                stopLossPrice = lot.getStopLossPrice()
                targetPrices.append(f"#{lot.lotId}/{openPrice}"
                                    f"{'' if self.isBuyAndHoldMode() else f'/{closePrice}'}"
                                    f"{f'/{stopLossPrice[0]}' if self.gridLotStopLossFactor else ''}")
            lot = lot.getNextLot()
        notifyMsg = (f"{self.getSymbolAlias()}: Session#{self.sessionId}, marketPrice={self.getMarketPrice()}, filledLots={self.countFilledLots()}, "
                     f"investedQuantity={self.getInvestedQuantity()}, totalNetProfit={self.getTotalNetProfitAmount()}, "
                     f"overallMaxProfitLoss={self.overallMaxProfitLoss}, {self.printGridPrices()}, ")
        if self.isBuyAndHoldMode():
            notifyMsg += (f"dcaMaxStartPrice={self.dcaMaxStartPrice}, dcaHoldingQuantity={self.dcaHoldingQuantity}, "
                          f"dcaLastInvestedDate={printFullTime(self.dcaLastInvestedDate)}, ")
        notifyMsg += f"targetPrices(lot#/open{'' if self.isBuyAndHoldMode() else '/close'}{'/stopLoss' if self.gridLotStopLossFactor else ''})={targetPrices}"
        if self.gridNotifyTargetPrices:
            notifyMsg = self.getSettingsMsg(f"Grid Trading {self.gridMode}") + "\n" + notifyMsg
            notify(notifyMsg)
        else:
            log(notifyMsg)

    def startGridSession(self):
        self.initializeGridLots()
        if self.gridInitializeSession:
            self.liquidateGridSession("INITIALIZE SESSION")
            if isLiveMode():  # Avoid auto redeploy (crash/reboot) to initialize session repeatedly!
                settings = f"{LIConfigKey.gridInitializeSession}={self.gridInitializeSession}"
                notify(f"{self.getNotifyPrefix()}: Quit algorithm after applied the settings: {settings}, please remove it and redeploy!")
                getAlgo().Quit("Quit algorithm on INITIALIZE SESSION!")
                return  # Quit execution immediately!
            else:
                self.restartGridSession(startPrices=self.gridStartPrices, reason="Start grid session")
        else:
            self.initBacktestStatus()
            self.restoreGridMetadata()
            self.resetGridStartPrices()
            self.realignOpenPositions()
            self.cancelActiveOrders()
            self.manageGridTrading()
            self.sessionStartedTime = getAlgo().Time
            self.printGridTargetPrices()
            self.printGridSession(withLots=True)

    def resetTradingLots(self, reason=None):
        lot = self.getTradeLot()
        while lot:
            lot.resetTradingLot(reason)
            lot = lot.getNextLot()

    def restartTradingLots(self, reason=None):
        lot = self.getTradeLot()
        while lot:
            lot.restartTradingLot(reason)
            lot = lot.getNextLot()

    def pauseTradingLots(self, countFilledLots=None):
        if not countFilledLots or countFilledLots[1] > 0:  # Long side lots
            temp = self.startLot
            while temp.nextLot:
                temp.nextLot.pausedOpening = True
                temp = temp.nextLot
        if not countFilledLots or countFilledLots[2] > 0:  # Short side lots
            temp = self.startLot
            while temp.prevLot:
                temp.prevLot.pausedOpening = True
                temp = temp.prevLot

    def isLongSideActive(self) -> bool:
        if self.tradeBothSides():
            isActive = True
            gridSide = self.getGridLongSide()
            marketPrice = self.getMarketPrice()
            startPrice = self.getStartPrice(gridSide)
            if startPrice:
                if self.isMomentumMode():
                    isActive &= marketPrice > startPrice
                elif self.isContrarianMode():
                    isActive &= marketPrice < startPrice
            limitStartPrice = self.getLimitStartPrice(gridSide)
            if limitStartPrice:
                if self.isMomentumMode():
                    isActive &= marketPrice > limitStartPrice
                elif self.isContrarianMode():
                    isActive &= marketPrice < limitStartPrice
            return isActive
        return self.gridLongLots

    def isShortSideActive(self) -> bool:
        if self.tradeBothSides():
            isActive = True
            gridSide = self.getGridShortSide()
            marketPrice = self.getMarketPrice()
            startPrice = self.getStartPrice(gridSide)
            if startPrice:
                if self.isMomentumMode():
                    isActive &= marketPrice < startPrice
                elif self.isContrarianMode():
                    isActive &= marketPrice > startPrice
            limitStartPrice = self.getLimitStartPrice(gridSide)
            if limitStartPrice:
                if self.isMomentumMode():
                    isActive &= marketPrice < limitStartPrice
                elif self.isContrarianMode():
                    isActive &= marketPrice > limitStartPrice
            return isActive
        return self.gridShortLots

    def getStartPrice(self, gridSide):
        if self.gridFixedStartPrices:
            return self.gridFixedStartPrices[gridSide]
        elif self.gridBandingStartPrices:
            return self.positionManager.roundSecurityPrice(self.bollingerBandsIndicator.getBand(self.gridBandingStartPrices[gridSide]).getPrice())

    def getOpenFromPrice(self, gridSide: LIGridSide):
        if self.gridFixedOpenFromPrices:
            return self.gridFixedOpenFromPrices[gridSide]
        elif self.gridBandingOpenFromPrices:
            return self.positionManager.roundSecurityPrice(self.bollingerBandsIndicator.getBand(self.gridBandingOpenFromPrices[gridSide]).getPrice())

    def getLimitStartPrice(self, gridSide: LIGridSide):
        if self.gridLimitStartPrices:
            return self.gridLimitStartPrices[gridSide]
        elif self.gridBandingLimitStartPrices:
            return self.positionManager.roundSecurityPrice(self.bollingerBandsIndicator.getBand(self.gridBandingLimitStartPrices[gridSide]).getPrice())

    def estimateFilledLots(self, investedQuantity):
        """Recalculate the filled lots based on market price or lot quantity."""
        newFilledLots = 0
        if investedQuantity:
            if self.isLongSideActive():
                targetLot = self.startLot.nextLot
                while targetLot and investedQuantity > 0:
                    if targetLot.isLongLot() and not targetLot.pausedOpening:
                        investedQuantity -= abs(self.getTargetQuantity(self.startLot))
                        newFilledLots += 1
                    targetLot = targetLot.nextLot
            if self.isShortSideActive():
                targetLot = self.startLot.prevLot
                while targetLot and investedQuantity < 0:
                    if targetLot.isShortLot and not targetLot.pausedOpening:
                        investedQuantity += abs(self.getTargetQuantity(self.startLot))
                        newFilledLots -= 1
                    targetLot = targetLot.prevLot
        return newFilledLots

    def realignOpenPositions(self, forceOnDemand=False, resetFilledLots=True, placeholderLots=0):
        # The saved metadata could be stale, but can be fixed by checkLeakingOpenPositions()!
        if self.gridFixedStartPrices and self.gridFixedStartPrices != self.gridStartPrices:
            log(f"{self.getSymbolAlias()}: Reset filled positions due to {LIConfigKey.gridFixedStartPrices}={self.gridFixedStartPrices} "
                f"overriding startPrices={self.gridStartPrices}.")
            self.resetOpeningProps(preserveOpenPrice=True)

        if not (forceOnDemand or self.gridRealignOpenPositions):
            return  # Abort

        self.resetGridStartPrices(emptyStartPrices=True, emptyOpenFromPrices=True)

        investedQuantity = self.getInvestedQuantity() - self.dcaHoldingQuantity
        newFilledLots = abs(self.estimateFilledLots(investedQuantity))
        newLotQuantity = self.positionManager.roundSecuritySize(investedQuantity / newFilledLots) if newFilledLots else 0
        log(f"{self.getSymbolAlias()}: Realign investedQuantity={investedQuantity} from filledLots={self.countFilledLots()} to "
            f"newFilledLots={newFilledLots}, newLotQuantity={newLotQuantity}.")

        # Calculate new start prices accordingly!
        self.manageGridStartPrices(retainOpenedLots=newFilledLots + placeholderLots, overwriteStartPrices=True)

        if resetFilledLots:
            self.resetOpeningProps(preserveOpenPrice=True)
            self.manageLeakingPositions(lotQuantity=newLotQuantity, realignOpenPositions=True)

        self.storeGridMetadata()

        if self.gridRealignOpenPositions:
            settings = f"{LIConfigKey.gridRealignOpenPositions}={self.gridRealignOpenPositions}"
            if isLiveMode():  # Avoid auto redeploy (crash/reboot) to realign open positions repeatedly!
                notify(f"{self.getNotifyPrefix()}: Quit algorithm after realigned open positions to {newFilledLots} lots, "
                       f"please remove {settings} and redeploy!")
                self.saveMetadataAtEnd = False
                getAlgo().Quit("Quit algorithm on REALIGNED OPEN POSITIONS!")
            else:
                notify(f"{self.getNotifyPrefix()}: Applied the settings: {settings}!")

    def resetOpeningProps(self, preserveOpenPrice=False):
        lot = self.getTradeLot()
        while lot:
            lot.resetOpeningProps(preserveOpenPrice=preserveOpenPrice)
            lot = lot.getNextLot()

    def hasLeakingPositions(self, leakingQuantity):
        return leakingQuantity and (not self.gridLotMinQuantity or abs(leakingQuantity) >= abs(self.gridLotMinQuantity))

    def manageLeakingPositions(self, lotQuantity=None, realignOpenPositions=False, logAssignment=True):
        """Assign possible leaking open positions to proper trading grid lots!"""
        if not (realignOpenPositions or self.positionManager.isExchangeOpen()):
            return  # Abort, wait for market open!

        # When having leaking long open positions
        leakingQuantity = self.getLeakingQuantity()
        if self.isLongSideActive() > 0:
            lot = self.getFirstLongLot()
            while lot and leakingQuantity > 0 and self.hasLeakingPositions(leakingQuantity):
                if lot.isLongLot() and not lot.pausedOpening:
                    if not lot.hasOpenPosition():
                        lot.filledOpenPrice = lot.getOpenTargetPrice()
                        targetQuantity = lotQuantity if lotQuantity else lot.getTargetQuantity()
                        lot.filledOpenQuantity = min(leakingQuantity, targetQuantity)
                        lot.lotStatus = LILotStatus.OPENING
                        if logAssignment:
                            log(f"{self.getSymbolAlias()}: Assigned leaking open position to: {lot}")
                    leakingQuantity = self.getLeakingQuantity()
                lot = lot.nextLot
        # When having leaking short open positions
        leakingQuantity = self.getLeakingQuantity()
        if self.isShortSideActive():
            lot = self.getFirstShortLot()
            while lot and leakingQuantity < 0 and self.hasLeakingPositions(leakingQuantity):
                if lot.isShortLot() and not lot.pausedOpening:
                    if not lot.hasOpenPosition():
                        lot.filledOpenPrice = lot.getOpenTargetPrice()
                        targetQuantity = lotQuantity if lotQuantity else lot.getTargetQuantity()
                        lot.filledOpenQuantity = max(leakingQuantity, targetQuantity)
                        lot.lotStatus = LILotStatus.OPENING
                        if logAssignment:
                            log(f"{self.getSymbolAlias()}: Assigned leaking open position to: {lot}")
                    leakingQuantity = self.getLeakingQuantity()
                lot = lot.prevLot

        # Could be caused by market order due to stop loss hedging or margin call!
        leakingQuantity = self.getLeakingQuantity()
        if self.isLongSideActive():
            lot = self.getLastLongLot()
            while lot != self.startLot and leakingQuantity < 0 and self.hasLeakingPositions(leakingQuantity):
                if lot.isLongLot() and not lot.pausedOpening and lot.hasOpenPosition():
                    reason = f"Reset lot to fix leaking positions"
                    lot.resetTradingLot(reason)
                    log(f"{self.getSymbolAlias()}: {reason}: {lot}")
                    leakingQuantity = self.getLeakingQuantity()
                lot = lot.prevLot
        # Could be caused by market order due to stop loss hedging or margin call!
        leakingQuantity = self.getLeakingQuantity()
        if self.isShortSideActive():
            lot = self.getLastShortLot()
            while lot != self.startLot and leakingQuantity > 0 and self.hasLeakingPositions(leakingQuantity):
                if lot.isShortLot() and not lot.pausedOpening and lot.hasOpenPosition():
                    reason = f"Reset lot to fix leaking positions"
                    lot.resetTradingLot(reason)
                    log(f"{self.getSymbolAlias()}: {reason}: {lot}")
                    leakingQuantity = self.getLeakingQuantity()
                lot = lot.nextLot

        # Mark closing status in favor of managing lot close order
        lot = self.getTradeLot()
        while lot:
            if not self.isBuyAndHoldMode() and lot.hasOpenPosition() and not lot.hasClosePosition():
                # Attempt to submit close order ticket in next step!
                lot.closeOrderPrice = lot.getCloseTargetPrice()
                lot.closeOrderQuantity = -lot.filledOpenQuantity
                lot.lotStatus = LILotStatus.CLOSING
            lot = lot.getNextLot()

        # Force to close extra positions or send alert if still leaking!
        leakingQuantity = self.getLeakingQuantity()
        if self.hasLeakingPositions(leakingQuantity):
            if self.gridFixLeakingPositions:
                fixLeaking = "Fixing leaking positions"
                fixLeakingTicket = self.positionManager.getActiveOrderTickets(tagKeywords=fixLeaking)
                if fixLeakingTicket:
                    log(f"{self.getSymbolAlias()}: Waiting for the leaking order ticket to be filled: {fixLeakingTicket}")
                else:
                    reason = (f"{fixLeaking} with limit market order at marketPrice={self.getMarketPrice()}, "
                              f"investedQuantity={self.getInvestedQuantity()}, fulfillQuantity={-leakingQuantity}!")
                    notify(f"{self.getNotifyPrefix()}: {reason}")
                    self.positionManager.limitMarketOrder(-leakingQuantity, reason)
            else:
                alert(f"{self.getNotifyPrefix()}: Failed to assign leaking {leakingQuantity} positions as "
                      f"investedQuantity/openingQuantity/closingQuantity={self.getInvestedQuantity()}/{self.getOpeningQuantity()}/{self.getClosingQuantity()}. "
                      f"You can manually close these leaking positions to align with grid lots status.")
            self.printGridSession(withLots=True)

    def recalculateStartPrice(self, marketPrice, lotIdFactor=None):
        startPrice = marketPrice
        if lotIdFactor:
            if lotIdFactor > 0:
                if self.gridLotLevelPercent:
                    if self.isMomentumMode():
                        startPrice = marketPrice / pow(1 + self.getAugmentedPercent(lotIdFactor) / 100, lotIdFactor)
                    elif self.isContrarianMode():
                        startPrice = marketPrice / pow(1 - self.getAugmentedPercent(lotIdFactor) / 100, lotIdFactor)
                elif self.gridLotLevelAmount:
                    if self.isMomentumMode():
                        startPrice = marketPrice - (self.getAugmentedAmount(lotIdFactor) * lotIdFactor)
                    elif self.isContrarianMode():
                        startPrice = marketPrice + (self.getAugmentedAmount(lotIdFactor) * lotIdFactor)
            if lotIdFactor < 0:
                if self.gridLotLevelPercent:
                    if self.isMomentumMode():
                        startPrice = marketPrice / pow(1 - self.getAugmentedPercent(lotIdFactor) / 100, abs(lotIdFactor))
                    elif self.isContrarianMode():
                        startPrice = marketPrice / pow(1 + self.getAugmentedPercent(lotIdFactor) / 100, abs(lotIdFactor))
                elif self.gridLotLevelAmount:
                    if self.isMomentumMode():
                        startPrice = marketPrice + (self.getAugmentedAmount(lotIdFactor) * abs(lotIdFactor))
                    elif self.isContrarianMode():
                        startPrice = marketPrice - (self.getAugmentedAmount(lotIdFactor) * abs(lotIdFactor))
        return self.positionManager.roundSecurityPrice(startPrice)

    def manageGridStartPrices(self, bar=None, retainOpenedLots=None, filledMarketPrice=None, overwriteStartPrices=False):
        marketPrice = filledMarketPrice if filledMarketPrice else self.getMarketPrice(bar)
        # Apply retaining opened lots logic to reserve some lots
        retainStartPrices = dict()
        if not retainOpenedLots or (self.gridInitOpenedLots and abs(self.gridInitOpenedLots) > abs(retainOpenedLots)):
            retainOpenedLots = self.gridInitOpenedLots
        if not retainOpenedLots or (self.gridRetainOpenedLots and abs(self.gridRetainOpenedLots) > abs(retainOpenedLots)):
            retainOpenedLots = self.gridRetainOpenedLots
        if retainOpenedLots and self.positionManager:
            # Recalculate retain start prices with the current market price and filled grid lots.
            # So that order tickets will be updated to stick to the market price closely in favor of trading.
            # log(f"{self.getSymbolAlias()}: Recalculate start prices with retainOpenedLots={retainOpenedLots}.")
            # TEST: It performs better without checking the retainOpenedLots vs. countFilledLots!
            if self.gridLongLots and retainOpenedLots > 0:  # and retainOpenedLots >= self.countFilledLots():
                retainStartPrice = self.recalculateStartPrice(marketPrice, retainOpenedLots)
                # retainStartPrice += self.recalculateStartPrice(marketPrice, retainOpenedLots + 1)
                # retainStartPrice /= 2  # Pick the middle point of the last retained lot
                retainStartPrice = self.positionManager.roundSecurityPrice(retainStartPrice)
                if (overwriteStartPrices or self.gridStickToMarketTrend) \
                        or (self.isMomentumMode() and self.gridStartPrices[self.getGridLongSide()] > retainStartPrice) \
                        or (self.isContrarianMode() and self.gridStartPrices[self.getGridLongSide()] < retainStartPrice):
                    startPrices = copy.deepcopy(self.gridStartPrices)
                    self.gridStartPrices[self.getGridLongSide()] = retainStartPrice
                    retainStartPrices[self.getGridLongSide()] = retainStartPrice
                    if self.gridInitOpenedLots:
                        notify(f"{self.getNotifyPrefix()}: Adjusted start {self.getGridLongSide()} price to initiate {retainOpenedLots} opened lots: "
                               f"from {startPrices} to {self.gridStartPrices}, please remove {LIConfigKey.gridInitOpenedLots} and redeploy ASAP!")
                        self.gridInitOpenedLots = 0  # Just apply for the first time!
                    else:
                        log(f"{self.getSymbolAlias()}: Adjusted start {self.getGridLongSide()} price to retain/realign {retainOpenedLots} opened lots: "
                            f"from {startPrices} to {self.gridStartPrices}", self.verbose)
            # TEST: It performs better without checking the retainOpenedLots vs. countFilledLots!
            if self.gridShortLots and retainOpenedLots < 0:  # and abs(retainOpenedLots) >= abs(self.countFilledLots()):
                retainStartPrice = self.recalculateStartPrice(marketPrice, retainOpenedLots)
                # retainStartPrice += self.recalculateStartPrice(marketPrice, retainOpenedLots - 1)
                # retainStartPrice /= 2  # Pick the middle point of the last retained lot
                retainStartPrice = self.positionManager.roundSecurityPrice(retainStartPrice)
                if (overwriteStartPrices or self.gridStickToMarketTrend) \
                        or (self.isMomentumMode() and self.gridStartPrices[self.getGridShortSide()] < retainStartPrice) \
                        or (self.isContrarianMode() and self.gridStartPrices[self.getGridShortSide()] > retainStartPrice):
                    startPrices = copy.deepcopy(self.gridStartPrices)
                    self.gridStartPrices[self.getGridShortSide()] = retainStartPrice
                    retainStartPrices[self.getGridShortSide()] = retainStartPrice
                    if self.gridInitOpenedLots:
                        notify(f"{self.getNotifyPrefix()}: Adjusted start {self.getGridShortSide()} price to initiate {retainOpenedLots} opened lots: "
                               f"from {startPrices} to {self.gridStartPrices}, please remove {LIConfigKey.gridInitOpenedLots} and redeploy ASAP!")
                        self.gridInitOpenedLots = 0  # Just apply for the first time!
                    else:
                        log(f"{self.getSymbolAlias()}: Adjusted start {self.getGridShortSide()} price to retain/realign {retainOpenedLots} opened lots: "
                            f"from {startPrices} to {self.gridStartPrices}", self.verbose)

        # Apply fixed start prices if specified, means it won't follow/respect the market price
        if self.gridFixedStartPrices or self.gridBandingStartPrices:
            if retainStartPrices and not self.tradeBothSides():
                notifyMsg = (f"{self.getNotifyPrefix()}: The retainOpenedLots={retainOpenedLots} requests to update "
                             f"{LIConfigKey.gridFixedStartPrices} as {self.gridStartPrices}, please adjust settings and redeploy or keep as it is!")
                if self.gridLongLots and self.gridStartPrices[self.getGridLongSide()] != self.getStartPrice(self.getGridLongSide()):
                    notify(notifyMsg)
                if self.gridShortLots and self.gridStartPrices[self.getGridShortSide()] != self.getStartPrice(self.getGridShortSide()):
                    notify(notifyMsg)
            else:
                if self.gridLongLots:
                    self.gridStartPrices[self.getGridLongSide()] = self.getStartPrice(self.getGridLongSide())
                if self.gridShortLots:
                    self.gridStartPrices[self.getGridShortSide()] = self.getStartPrice(self.getGridShortSide())
                log(f"{self.getSymbolAlias()}: Set {LIConfigKey.gridStartPrices}={self.gridStartPrices} "
                    f"as {LIConfigKey.gridFixedStartPrices}={self.gridFixedStartPrices}, {LIConfigKey.gridBandingStartPrices}={self.gridBandingStartPrices}!",
                    self.verbose)

        # Apply fixed open from prices if specified, means it will avoid opening order until reached this price
        if self.gridFixedOpenFromPrices or self.gridBandingOpenFromPrices:
            if self.gridLongLots:
                self.gridOpenFromPrices[self.getGridLongSide()] = self.getOpenFromPrice(self.getGridLongSide())
            if self.gridShortLots:
                self.gridOpenFromPrices[self.getGridShortSide()] = self.getOpenFromPrice(self.getGridShortSide())

        # Apply boundary/stop prices if specified, means only retain opened lots within the boundary prices
        if self.gridLimitStartPrices or self.gridBandingLimitStartPrices:
            if retainStartPrices and not self.tradeBothSides():
                notifyMsg = (f"{self.getNotifyPrefix()}: The retainOpenedLots={retainOpenedLots} requests to update "
                             f"{LIConfigKey.gridLimitStartPrices} as {self.gridStartPrices}, please adjust settings and redeploy or keep as it is!")
                if self.gridLongLots and self.gridStartPrices[self.getGridLongSide()] > self.getLimitStartPrice(self.getGridLongSide()):
                    notify(notifyMsg)
                if self.gridShortLots and self.gridStartPrices[self.getGridShortSide()] < self.getLimitStartPrice(self.getGridShortSide()):
                    notify(notifyMsg)
            else:
                if self.gridLongLots:
                    self.gridStartPrices[self.getGridLongSide()] = min(self.gridStartPrices[self.getGridLongSide()],
                                                                       self.getLimitStartPrice(self.getGridLongSide()))
                if self.gridShortLots:
                    self.gridStartPrices[self.getGridShortSide()] = max(self.gridStartPrices[self.getGridShortSide()],
                                                                        self.getLimitStartPrice(self.getGridShortSide()))

        # Force fully filled grid lots to catch up with the adverse market trend
        if self.isContrarianMode() and self.gridFollowAdverseTrend:
            startPrices = {}
            countFilledLots = self.countFilledLots()
            # Push down start price one lot to catch up downtrend!
            if countFilledLots[1] > 0 and self.getLastLongLot().hasOpenPosition() and self.getLastLongLot().filledOpenPrice > marketPrice:
                if self.gridStartPrices[LIGridSide.BTD] != self.getFirstLongLot().filledOpenPrice:
                    startPrices[LIGridSide.BTD] = self.getFirstLongLot().filledOpenPrice
            # Pull up start price one lot to catch up uptrend!
            if countFilledLots[2] > 0 and self.getLastShortLot().hasOpenPosition() and self.getLastShortLot().filledOpenPrice < marketPrice:
                if self.gridStartPrices[LIGridSide.STU] != self.getFirstShortLot().filledOpenPrice:
                    startPrices[LIGridSide.STU] = self.getFirstShortLot().filledOpenPrice
            if startPrices:
                notify(f"{self.getNotifyPrefix()}: Shift start prices from {self.gridStartPrices} to {self.gridStartPrices | startPrices} "
                       f"to catch up with the adverse market trend!")
                self.resetGridStartPrices(startPrices)
                self.resetOpeningProps(preserveOpenPrice=True)
                self.manageLeakingPositions(realignOpenPositions=True, logAssignment=False)
                if self.verbose:
                    self.printGridTargetPrices()

        # Long side price should be always less than or equal to Short side price!
        if (not (self.gridFixedStartPrices or self.gridBandingStartPrices or self.gridUseTradeInsight or self.gridHedgeEnabled)
                and self.tradeBothSides() and self.gridStartPrices.get(self.getGridLongSide())
                and self.gridStartPrices.get(self.getGridShortSide())):
            if self.gridStartPrices[self.getGridLongSide()] > self.gridStartPrices[self.getGridShortSide()]:
                terminate(f"{self.getGridLongSide()} price should be less than or equal to {self.getGridShortSide()} price, "
                          f"but startPrices={self.gridStartPrices}!")
        # No need to check the open from prices as it'd go against the long/short logic within a hedging strategy
        # if (not self.gridOpenFromPrices and self.tradeBothSides() and self.gridOpenFromPrices.get(self.getGridLongSide())
        #         and self.gridOpenFromPrices.get(self.getGridShortSide())):
        #     if self.gridOpenFromPrices[self.getGridLongSide()] > self.gridOpenFromPrices[self.getGridShortSide()]:
        #         terminate(f"{self.getGridLongSide()} price should be less than or equal to {self.getGridShortSide()} price, "
        #                   f"but openFromPrices={self.gridOpenFromPrices}!")

        return retainStartPrices

    def updateGridSession(self, bar):
        # Dynamically adjusting starting prices to catch up with the market price!
        if (self.extendedMarketHours or isActiveMarketTime(getAlgo().Time) or
                (atMarketOpenTime(delta=self.getMonitorPeriodDelta()) and self.getInvestedQuantity() == 0)):
            if self.gridMonitorPeriodFactors:
                if self.getInvestedQuantity() >= 0 and not isTickTime(timestamp=bar.EndTime,
                                                                      delta=self.gridMonitorPeriodFactors.get(self.getGridLongSide(),
                                                                                                              1) * self.getMonitorPeriodDelta()):
                    return  # Abort
                if self.getInvestedQuantity() < 0 and not isTickTime(timestamp=bar.EndTime,
                                                                     delta=self.gridMonitorPeriodFactors.get(self.getGridShortSide(),
                                                                                                             1) * self.getMonitorPeriodDelta()):
                    return  # Abort
            marketPrice = self.positionManager.roundSecurityPrice(bar.Close)
            if self.isLongSideActive():
                if self.isMomentumMode():
                    self.gridStartPrices[self.getGridLongSide()] = min(marketPrice, self.gridStartPrices[self.getGridLongSide()])
                elif self.isContrarianMode():
                    self.gridStartPrices[self.getGridLongSide()] = max(marketPrice, self.gridStartPrices[self.getGridLongSide()])
                    self.manageDCABuyAndHold(bar)
            if self.isShortSideActive():
                if self.isMomentumMode():
                    self.gridStartPrices[self.getGridShortSide()] = max(marketPrice, self.gridStartPrices[self.getGridShortSide()])
                elif self.isContrarianMode():
                    self.gridStartPrices[self.getGridShortSide()] = min(marketPrice, self.gridStartPrices[self.getGridShortSide()])
            if self.isBoostingModeActivated():
                self.manageGridBoosting(bar=bar)
            else:
                self.manageGridTrading(bar=bar)
        # Clean up work to do at the end of day!
        if atMarketCloseTime(delta=self.getMonitorPeriodDelta()):
            self.onCloseOfMarket()

    def onMonitorBarUpdated(self, bar):
        # Log or set break point for a particular date
        # if dateIs(2024, 1, 25):
        #     log(f"{self.getSymbolAlias()}: onMonitorBarUpdated={bar} endTime: {bar.EndTime.strftime(LIGlobal.secondFormat)}, "
        #         f"isExchangeOpen={self.positionManager.isExchangeOpen()}, filledLots={self.countFilledLots()}")
        if self.plotDefaultChart:
            plot(self.mainChart.name, "Price", bar.close)
        if self.gridHeikinAshies:
            self.gridHeikinAshies[0].Update(bar)
        else:
            self.updateGridSession(bar)

    def onHeikinAshiUpdated(self, sender: HeikinAshi, updated: IndicatorDataPoint):
        if not sender.IsReady:
            return  # Abort
        bar = TradeBar(sender.Current.EndTime,
                       sender.Current.Symbol,
                       sender.Open.Current.Value,
                       sender.High.Current.Value,
                       sender.Low.Current.Value,
                       sender.Close.Current.Value,
                       sender.Volume.Current.Value,
                       self.getMonitorPeriodDelta())
        n = int(sender.name)
        if n < len(self.gridHeikinAshies) - 1:
            self.gridHeikinAshies[n + 1].update(bar)  # Call next ply
        else:
            if self.plotDefaultChart:
                plot(self.mainChart.name, "HPrice", bar.close)
            self.updateGridSession(bar)
