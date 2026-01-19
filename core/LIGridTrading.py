from AlgorithmImports import *
from core.LIGridBase import *

"""
Please look into README.md to understand: What is grid trading?
"""


class LIGridTrading(LIGridBase):
    def __init__(self, symbolStr, securityType, investAmount, gridMode, **configs):
        super().__init__(symbolStr, securityType, investAmount, gridMode, **configs)

    def getLeakingQuantity(self):
        investedQuantity = self.getInvestedQuantity()
        openingQuantity = self.getOpeningQuantity()
        # QuantConnect sometimes has issues to get correct filled quantity from IBKR, so we need to double check it!
        if (not (self.isBuyAndHoldMode() or self.gridResetStartPrices or self.gridResetLotsMetadata or self.gridRealignOpenPositions)
                and openingQuantity > 0 and investedQuantity >= openingQuantity * 2):
            alert(f"{self.getNotifyPrefix()}: Extra large leaking quantity detected, will try to auto resolve it. "
                  f"Please double check and resolve it manually with gridRealignOpenPositions=True if necessary: "
                  f"investedQuantity={investedQuantity} vs. openingQuantity={openingQuantity}!",
                  "Extra Leaking Quantity")
        return investedQuantity - openingQuantity - self.dcaHoldingQuantity

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
            maxCapital = getAlgo().portfolio.total_portfolio_value * self.investAmount.maxHolding
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
            for orderTicket in self.positionManager.getActiveOrderTickets():
                if isOrderTicketUpdatable(orderTicket) and orderTicket.quantity == -(self.getInvestedQuantity() - self.dcaHoldingQuantity):
                    return orderTicket
        return None

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
                        if not self.gridSortSkewedLots:
                            alert(f"{self.getNotifyPrefix()}: Skewed grid lots, "
                                  f"two lots with filled open price not in sequence order: \n-> {lot}\n-> {nextLot}", self.verbose)
                        return True
                    elif self.isContrarianMode() and lot.filledOpenPrice < nextLot.filledOpenPrice:
                        if not self.gridSortSkewedLots:
                            alert(f"{self.getNotifyPrefix()}: Skewed grid lots, "
                                  f"two lots with filled open price not in sequence order: \n-> {lot}\n-> {nextLot}", self.verbose)
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
                        if self.gridSortSkewedLots:
                            alert(f"{self.getNotifyPrefix()}: Skewed grid lots, following two lots with "
                                  f"filled open price not in sequence order: \n-> {lot}\n-> {prevLot}")
                        return True
                    elif self.isContrarianMode() and lot.filledOpenPrice > prevLot.filledOpenPrice:
                        if self.gridSortSkewedLots:
                            alert(f"{self.getNotifyPrefix()}: Skewed grid lots, following two lots with "
                                  f"filled open price not in sequence order: \n-> {lot}\n-> {prevLot}")
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
                log(f"{self.getSymbolAlias()}: Swapped lot {lot} with {lot.nextLot} to keep in order.", self.verbose)
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
                log(f"{self.getSymbolAlias()}: Swapped lot {lot} with {lot.nextLot} to keep in order.", self.verbose)
                if nextLot and nextLot.isShortLot():
                    lot = nextLot  # Back off one
                    continue
            lot = lot.prevLot

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
            elif self.gridResetStartPrices is not None:  # Could be empty {}
                self.gridNoMoreOpenOrders = True
                self.gridNoMoreCloseOrders = True
                self.restartGridSession(startPrices=self.gridResetStartPrices)
                settings = f"{LIConfigKey.gridResetStartPrices}={self.gridResetStartPrices}"
                notify(f"{self.getNotifyPrefix()}: Stopped trading after reset start prices as {self.gridStartPrices}, please remove {settings} and redeploy!")
            elif self.startLot is None:
                self.startGridSession()
            elif not self.positionManager.isInvested():
                self.restartGridSession(reason="Add new security")

    def onData(self, data: Slice):
        # log(f"onData: {data}")
        pass

    def onEmitTradeInsight(self, tradeInsight: LITradeInsight):
        super().onEmitTradeInsight(tradeInsight)
        if tradeInsight.signalType == LISignalType.CLOSE and self.getInvestedQuantity() != 0:
            tagLog = f"Liquidated upon CLOSE signal"
            if self.liquidateGridSession(tagLog):
                notify(f"{self.getNotifyPrefix()}: Restarted a new trading session after {tagLog}!")
            self.restartGridSession(reason="Restart after liquidation")
            return
        if tradeInsight.tradeOrderSet:
            # Initialize trading lots if not yet
            if self.startLot is None:
                self.startLot = self.createGridLot(0)
            # Assign trade orders to trading lots
            for tradeOrder in tradeInsight.tradeOrderSet:
                tradingLot = self.getLotById(tradeOrder.lotId)
                if tradingLot is None:
                    self.createGridLots(tradeOrder.lotId)
                    tradingLot = self.getLotById(tradeOrder.lotId)
                tradingLot.setTradeOrder(tradeOrder)
        if self.startLot is not None:
            if self.isCommandMode():
                self.manageGridCommand(forceTrade=True)  # Trigger all related actions
            elif self.isBoostingMode():
                self.manageGridBoosting(forceTrade=True)  # Trigger all related actions
            else:
                self.manageGridTrading(forceTrade=True)  # Trigger all related actions

    def onTradeInsightChanged(self, oldTradeInsight: LITradeInsight, newTradeInsight: LITradeInsight):
        super().onTradeInsightChanged(oldTradeInsight, newTradeInsight)
        if self.gridSignalStartPrices:
            marketPrice = self.getMarketPrice()
            if marketPrice is None:
                return  # Abort
            startPrices = {}
            if self.gridLongLots and newTradeInsight.signalType == LISignalType.LONG:
                startPrices[self.getGridLongSide()] = marketPrice
            if self.gridShortLots and newTradeInsight.signalType == LISignalType.SHORT:
                startPrices[self.getGridShortSide()] = marketPrice
            # Make sure grid start prices have been initialized first!
            if all(key in self.gridStartPrices for key in startPrices.keys()):
                self.resetGridStartPrices(startPrices=startPrices)
        if self.liquidateOnSignalTypeFlipped:
            if ((oldTradeInsight.signalType == LISignalType.LONG and newTradeInsight.signalType == LISignalType.SHORT) or
                    (oldTradeInsight.signalType == LISignalType.SHORT and newTradeInsight.signalType == LISignalType.LONG)):
                tagLog = f"signalType flipped from {oldTradeInsight.signalType} to {newTradeInsight.signalType}"
                if self.liquidateGridSession(tagLog):
                    notify(f"{self.getNotifyPrefix()}: Restart a new trading session after {tagLog}!")
                    self.restartGridSession(reason="Restart after liquidation")

    def restartGridSession(self, startPrices=None, reason=None):
        if self.isBoostingModeActivated():
            self.cancelActiveOrders()
            self.manageGridBoosting()
            return  # Abort
        self.sessionId += 1
        self.reachedOpenPrice = False
        self.liquidatedAlready = False
        self.sessionStartedTime = getAlgoTime()
        self.initializeGridLots()
        self.restartTradingLots(reason)
        self.deleteGridMetadata()
        self.resetGridStartPrices(startPrices, emptyStartPrices=True, emptyOpenFromPrices=True)
        self.cancelActiveOrders()
        self.manageGridTrading()
        self.printGridTargetPrices()
        self.printGridSession(withLots=True)

    def manageGridCommand(self, bar=None, forceTrade=False):
        if forceTrade:
            self.positionManager.enableTempTradable()

        marketPrice = self.getMarketPrice(bar)

        if self.isGridTradingPaused() or self.manageGridLiquidation(bar):
            self.positionManager.disableTempTradable()
            return False

        if self.positionManager.isNotExchangeOpen():
            return False  # Abort, wait for market open!

        self.manageGridOrderTickets(bar=bar)

        if forceTrade:
            self.positionManager.disableTempTradable()
        return True

    def manageGridTrading(self, bar=None, forceTrade=False):
        if forceTrade:
            self.positionManager.enableTempTradable()

        marketPrice = self.getMarketPrice(bar)

        if self.isGridTradingPaused() or self.manageGridLiquidation(bar):
            self.positionManager.disableTempTradable()
            return False

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

        if self.gridSortSkewedLots and self.areGridLotsSkewed():
            self.sortGridTradingLots()
            # self.printGridSession(withLots=True)

        # Do following standard procedures
        self.manageGridRollover(bar=bar)
        self.manageGridStartPrices(bar=bar)
        self.manageGridOrderTickets(bar=bar)
        self.manageForeclosingOrders(bar=bar)

        if forceTrade:
            self.positionManager.disableTempTradable()

        return True

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
            if (not self.gridMonitorPeriodFactors or
                    (bar and isTickTime(timestamp=bar.end_time,
                                        delta=self.gridMonitorPeriodFactors.get(self.getGridLongSide(), 1) * self.getMonitorPeriodDelta()))):
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
            if (not self.gridMonitorPeriodFactors or
                    (bar and isTickTime(timestamp=bar.end_time,
                                        delta=self.gridMonitorPeriodFactors.get(self.getGridShortSide(), 1) * self.getMonitorPeriodDelta()))):
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

    def manageForeclosingOrders(self, bar=None):
        if not self.forecloseHoldingPositions:
            return False  # Abort, not enabled

        self.cancelExpiredCloseOrder()

        marketPrice = self.getMarketPrice()
        investedQuantity = self.getInvestedQuantity()

        if not investedQuantity:
            return False  # Abort, no invested yet!

        if self.closeOrderTicket:
            return False  # Abort, already has a foreclosing order!

        for criteria in self.forecloseHoldingPositions:
            quantity = abs(criteria[0])  # Convert to positive by default!
            targetPrice = criteria[1]
            if (investedQuantity >= quantity > 0 and marketPrice < targetPrice) or (investedQuantity <= -quantity < 0 and marketPrice > targetPrice):
                quantity = -quantity if investedQuantity > 0 else quantity
                tagLog = f"{self.gridMode}: Foreclose {LITradeType.CLOSING_LIMIT} order, quantity={quantity}, targetPrice={targetPrice}, marketPrice={marketPrice}."
                log(f"{self.getSymbolAlias()}@{tagLog}")
                self.closeOrderTicket = self.positionManager.limitOrder(quantity, targetPrice, tagLog)
                return True  # Had created a foreclosing order!

        return False

    def liquidateGridSession(self, reason, markRollover=False, markStopLoss=False):
        if foundLiquidationOrder(self.positionManager.getSecurity()):
            return False  # Abort
        if self.positionManager.isNotExchangeOpen():
            return False  # Abort, wait for market open!
        if self.isBuyAndHoldMode():
            notify(f"Please liquidate positions manually as {LIConfigKey.gridMode}={self.gridMode}!")
            return False
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
        liquidatedPrice = liquidateSecurity(self.positionManager.getSecurity(), tagLog)
        if self.getInvestedQuantity() != 0:
            alert(f"{self.getNotifyPrefix()}: Failed to liquidate security, waiting for next cycle!")
            return False
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
        elif isinstance(self.stoppedLossPrices, dict):
            self.stoppedLossPrices.pop(self.getGridTradingSide(), None)
        else:
            alert(f"Unexpected stoppedLossPrices={self.stoppedLossPrices}", title="Unexpected stopLossPrices")
        notifyMsg = (f"{self.getNotifyPrefix()}: Liquidated due to {reason} and closed session#{self.sessionId}: liquidatedPrice={liquidatedPrice}, "
                     f"tradesCount={tradesCount}, ordersCount={ordersCount}, filledLots={filledLots[0]}, investedQuantity={investedQuantity}, "
                     f"investedCapital={investedCapital}, totalNetProfit={totalNetProfitAmount}({totalNetProfitPercent}%), "
                     f"unrealizedProfit={unrealizedProfitAmount}({unrealizedProfitPercent}%), stoppedLossPrices={self.stoppedLossPrices}, "
                     f"rolloverCriteria={self.gridRolloverCriteria}. ")
        notify(notifyMsg)
        return True  # Return True after liquidated successfully!

    def liquidateGridSecurity(self, security: Security, reason, markRollover=False, markStopLoss=False):
        if foundLiquidationOrder(security):
            return False  # Abort
        if self.positionManager.isNotExchangeOpen():
            return False  # Abort, wait for market open!
        if self.isBuyAndHoldMode():
            notify(f"Please liquidate positions manually as {LIConfigKey.gridMode}={self.gridMode}!")
            return False
        securityHolding = getAlgo().portfolio[security.symbol]
        investedQuantity = securityHolding.quantity
        if not investedQuantity:
            log(f"{self.getSymbolAlias()}: No need to liquidate grid security {cleanSymbolValue(security.symbol)} as investedQuantity={investedQuantity}.")
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
            for orderTicket in getAlgo().transactions.get_open_order_tickets(security.symbol):
                if orderTicket.order_type == OrderType.LIMIT and isOrderTicketUpdatable(orderTicket):
                    if investedQuantity > 0 > orderTicket.quantity:
                        filledLots = (0 if filledLots is None else filledLots) + 1
                    if investedQuantity < 0 < orderTicket.quantity:
                        filledLots = (0 if filledLots is None else filledLots) - 1
            log(f"{self.getSymbolAlias()}: Got filledLots={filledLots} from {LITradeType.CLOSING} order tickets.")
        # Last, ask to specify the gridRolloverFilledLots manually
        if isLiveMode() and filledLots is None:  # Could be zero as specified by user
            alert(f"{self.getNotifyPrefix()}: Failed to figure out filled lots, please specify {LIConfigKey.gridRolloverCriteria}!")
            getAlgo().quit("Quit algorithm on ROLLOVER QUANTITIES!")
            return False
        investedCapital = securityHolding.absolute_holdings_cost
        unrealizedProfitAmount = securityHolding.unrealized_profit
        unrealizedProfitPercent = securityHolding.unrealized_profit_percent
        self.storeGridMetadata()
        tagLog = f"{LITradeType.LIQUIDATE} grid trading security {security.Symbol.Value} as {reason}."
        liquidatedPrice = liquidateSecurity(security, tagLog)
        if self.getInvestedQuantity() != 0:
            alert(f"{self.getNotifyPrefix()}: Failed to liquidate security, waiting for next cycle!")
            return False
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
        elif isinstance(self.stoppedLossPrices, dict):
            self.stoppedLossPrices.pop(self.getGridTradingSide(), None)
        else:
            alert(f"Unexpected stoppedLossPrices={self.stoppedLossPrices}", title="Unexpected stopLossPrices")
        notifyMsg = (f"{self.getNotifyPrefix()}: Liquidated grid trading security {security.Symbol.Value} due to {reason}: liquidatedPrice={liquidatedPrice}, "
                     f"filledLots={filledLots}, investedQuantity={investedQuantity}, investedCapital={investedCapital}, "
                     f"unrealizedProfit={unrealizedProfitAmount}({unrealizedProfitPercent:.2f}%), "
                     f"stoppedLossPrices={self.stoppedLossPrices}, rolloverCriteria={self.gridRolloverCriteria}.")
        notify(notifyMsg)
        return True  # Return True after liquidated successfully!

    def isGridTradingPaused(self) -> bool:
        if self.pauseTradingTillTime:
            if self.pauseTradingTillTime > getAlgoTime():
                # self.resetGridStartPrices()  # Might need to reset start prices after a long pause!
                log(f"{self.getSymbolAlias()}: Abort trading as {LIMetadataKey.pauseTradingTillTime}={self.pauseTradingTillTime.strftime(LIGlobal.secondFormat)}")
                return True  # True means still pause trading
            else:
                self.pauseTradingTillTime = None  # Reset
        return False  # False means resume trading

    def setFlipToSignalType(self, reason: str):
        if self.tradeInsight:
            if self.tradeInsight.signalType == LISignalType.LONG:
                self.flipToSignalType = LISignalType.SHORT
            elif self.tradeInsight.signalType == LISignalType.SHORT:
                self.flipToSignalType = LISignalType.LONG
        if self.flipToSignalType:
            notify(f"{self.getNotifyPrefix()}: Set flipToSignalType={self.flipToSignalType} due to {reason}!")
            self.storeGridMetadata()

    def cleanFlipToSignalType(self, reason: str):
        self.flipToSignalType = None
        notify(f"{self.getNotifyPrefix()}: Clean flipToSignalType as {reason}!")
        self.storeGridMetadata()

    def manageGridLiquidation(self, bar=None) -> bool:
        if self.liquidatedAlready:
            return True  # Abort, avoid liquidating repeatedly!
        # Liquidate and stop trading on demand!
        if self.liquidateAndStopTrading:
            if self.liquidateGridSession(f"{LIConfigKey.liquidateAndStopTrading}={self.liquidateAndStopTrading}"):
                notify(f"{self.getNotifyPrefix()}: Stopped trading as {LIConfigKey.liquidateAndStopTrading}={self.liquidateAndStopTrading}, "
                       f"please remove {LIConfigKey.liquidateAndStopTrading} to start a new session or keep stopping!")
                self.postLiquidationMetadata()
                return True  # Abort on demand
        marketPrice = self.getMarketPrice(bar)
        # countFilledLots = self.countFilledLots()
        investedQuantity = self.getInvestedQuantity()
        unrealizedProfitAmount = self.getUnrealizedProfitAmount()
        unrealizedProfitPercent = self.getUnrealizedProfitPercent()
        # Check whether it's a manual liquidation to take profit!
        # if not self.liquidatedAlready and (self.isBoostingMode() or self.countFilledLots() != 0) and self.getInvestedQuantity() == 0:
        #     tagLog = f"manual liquidation"
        #     self.liquidateGridSession(tagLog)
        #     if self.liquidateProfitAndRestartTrading:
        #         notify(f"{self.getNotifyPrefix()}: Restart a new trading session after {tagLog}, "
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
                if self.liquidateGridSession(tagLog):
                    if self.liquidateProfitAndRestartTrading:
                        notify(f"{self.getNotifyPrefix()}: Restart a new trading session after liquidated due to {tagLog}, "
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
            if self.liquidateGridSession(tagLog):
                if self.liquidateProfitAndRestartTrading:
                    notify(f"{self.getNotifyPrefix()}: Restart a new trading session after liquidated due to {tagLog}, "
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
            if self.liquidateGridSession(tagLog):
                if self.liquidateProfitAndRestartTrading:
                    notify(f"{self.getNotifyPrefix()}: Restart a new trading session after liquidated due to {tagLog}, "
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
        if self.getLiquidateOnStopLossAmount():
            if self.flipSignalAtLiquidateFactor:
                if self.flipToSignalType and unrealizedProfitAmount >= 0:
                    self.cleanFlipToSignalType(f"unrealizedProfitAmount={unrealizedProfitAmount} >= 0")
                stopLossFlipAmount = -abs(self.getLiquidateOnStopLossAmount() * self.flipSignalAtLiquidateFactor)
                if not self.flipToSignalType and unrealizedProfitAmount <= stopLossFlipAmount:
                    self.setFlipToSignalType(f"unrealizedProfitAmount={unrealizedProfitAmount} <= stopLossFlipAmount={stopLossFlipAmount}")
            if unrealizedProfitAmount <= -abs(self.getLiquidateOnStopLossAmount()):
                tagLog = f"unrealizedProfit={unrealizedProfitAmount}({unrealizedProfitPercent}%) <= stopLossAmount=-{abs(self.getLiquidateOnStopLossAmount())}"
                if self.liquidateGridSession(tagLog, markStopLoss=True):
                    if investedQuantity > 0:  # Only handle long positions
                        self.positionManager.backfillEquity(abs(unrealizedProfitAmount))
                    if self.liquidateLossAndRestartTrading:
                        notify(f"{self.getNotifyPrefix()}: Restart a new trading session after liquidated due to {tagLog}, "
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
        if self.liquidateOnStopLossPercent:
            if self.flipSignalAtLiquidateFactor:
                if self.flipToSignalType and unrealizedProfitPercent >= 0:
                    self.cleanFlipToSignalType(f"unrealizedProfitPercent={unrealizedProfitPercent} >= 0")
                stopLossFlipPercent = -abs(self.getLiquidateOnStopLossPercent() * self.flipSignalAtLiquidateFactor)
                if not self.flipToSignalType and unrealizedProfitPercent <= stopLossFlipPercent:
                    self.setFlipToSignalType(f"unrealizedProfitPercent={unrealizedProfitPercent}% <= stopLossFlipPercent={stopLossFlipPercent}")
            if unrealizedProfitPercent <= -abs(self.liquidateOnStopLossPercent):
                tagLog = f"unrealizedProfit={unrealizedProfitPercent}%({unrealizedProfitAmount}) <= stopLossPercent=-{self.liquidateOnStopLossPercent}%"
                if self.liquidateGridSession(tagLog, markStopLoss=True):
                    if investedQuantity > 0:  # Only handle long positions
                        self.positionManager.backfillEquity(abs(unrealizedProfitAmount))
                    if self.liquidateLossAndRestartTrading:
                        notify(f"{self.getNotifyPrefix()}: Restart a new trading session after liquidated due to {tagLog}, "
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
                notify(f"{self.getNotifyPrefix()}: Restart a new trading session after liquidated due to all {allPausedSide} lots have been paused!")
                if self.liquidateGridSession(f"gridRestartIfAllLotsPaused={self.gridRestartIfAllLotsPaused}"):
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
        stopLossAmount = 0
        if self.liquidateOnStopLossAmount:
            stopLossAmount = self.liquidateOnStopLossAmount
        stopLossAmount *= self.getLiquidateBaselineRatio()
        return stopLossAmount

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
        takeProfitAmount *= self.getLiquidateBaselineRatio()
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

        if self.positionManager.isNotExchangeOpen():
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
                self.cancelActiveOrders()
                self.storeGridMetadata()
                notify(f"{self.getNotifyPrefix()}: Activated the {LIGridMode.BOOSTING} mode as "
                       f"marketPrice={self.getMarketPrice()}, "
                       f"filledLots(total/long/short)={self.countFilledLots()}, "
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
            if not self.getTradeInsight().isNoneSignal():
                if self.getTradeInsight().isLongSignal():
                    if targetQuantity < 0:
                        return None
                elif self.getTradeInsight().isShortSignal():
                    if targetQuantity > 0:
                        return None
                else:
                    raise TypeError(f"Not support tradeInsight: {self.getTradeInsight()}!")

            tradeType = LITradeType.OPENING_LIMIT
            if self.openWithMarketOrderType:
                tradeType = LITradeType.OPENING_LIMIT_MARKET if self.positionManager.enableLimitMarketOrder else LITradeType.OPENING_MARKET

            tagLog = f"{self.gridMode}: Submit {tradeType} order at targetQuantity={targetQuantity}, marketPrice={self.getMarketPrice()}."
            log(f"{self.getSymbolAlias()}@{tagLog}")
            if self.openWithMarketOrderType:
                self.openOrderTicket = self.positionManager.limitMarketOrder(targetQuantity, tagLog)
            else:
                self.openOrderTicket = self.positionManager.limitOrder(targetQuantity, self.getMarketPrice(), tagLog)
            self.fireOrderEvents(self.openOrderTicket)
            liveSleep(1)  # A little break
            return True
        return None

    def manageBoostingClosedOrders(self):
        if not self.isBoostingMode():
            return False  # Abort, not in boosting mode yet!

        self.cancelExpiredCloseOrder()

        marketPrice = self.getMarketPrice()
        investedQuantity = self.getInvestedQuantity()

        if not investedQuantity:
            return False  # Abort, no invested yet!

        # Act according to trade insight
        closePositionsNow = False
        if not self.getTradeInsight().isNoneSignal():
            if self.getTradeInsight().isLongSignal():
                if investedQuantity < 0:
                    closePositionsNow = True
            elif self.getTradeInsight().isShortSignal():
                if investedQuantity > 0:
                    closePositionsNow = True
            elif self.getTradeInsight().isCloseSignal():
                closePositionsNow = True
            else:
                raise TypeError(f"Not support tradeInsight: {self.getTradeInsight()}!")
        if closePositionsNow:
            log(f"{self.getSymbolAlias()}: Closing open positions now as investedQuantity={investedQuantity} against tradeInsight: {self.getTradeInsight()}.",
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
                self.closeOrderTicket = self.positionManager.trailingStopOrder(targetQuantity, trailingStopPrices[0], trailingStopPrices[1],
                                                                               trailingStopPrices[2], tagLog)
            elif isOrderTicketUpdatable(self.closeOrderTicket):
                if self.closeOrderTicket.order_type in [OrderType.MARKET, OrderType.MARKET_ON_OPEN, OrderType.MARKET_ON_CLOSE]:
                    return False  # Abort, waiting for market open or order to be filled
                updateFields = UpdateOrderFields()
                needToUpdate = False
                if self.closeOrderTicket.quantity != targetQuantity:
                    updateFields.quantity = targetQuantity
                    needToUpdate = True
                if self.closeOrderTicket.order_type == OrderType.TRAILING_STOP:
                    if self.closeOrderTicket.get(OrderField.TRAILING_AMOUNT) != trailingStopPrices[1]:
                        updateFields.trailing_amount = trailingStopPrices[1]
                        needToUpdate = True
                if needToUpdate:
                    self.closeOrderUpdatedTimes += 1
                    tagLog = (f"{self.gridMode}: Update {tradeType} order @{self.closeOrderUpdatedTimes}, targetQuantity={targetQuantity}, "
                              f"marketPrice={marketPrice}, averagePrice={averagePrice}, {stopPricesMsg}, {stopProfitLevelMsg}.")
                    log(f"{self.getSymbolAlias()}@{tagLog}", self.verbose)
                    updateFields.tag = decorateTag(tagLog)
                    orderResponse = self.closeOrderTicket.update(updateFields)
                    if orderResponse and orderResponse.is_error:
                        notify(f"{self.getNotifyPrefix()}: Failed to update close order ticket fields: {orderResponse}, tag=[{self.closeOrderTicket.tag}].")
            else:
                alert(f"{self.getNotifyPrefix()}: The close order ticket is NOT updatable as expected: {self.closeOrderTicket}.")
            return isOrderTicketUpdatable(self.closeOrderTicket)
        elif isOrderTicketUpdatable(self.closeOrderTicket) and self.closeOrderTicket.order_type in [OrderType.LIMIT]:
            if self.closeOrderTicket.get(OrderField.LIMIT_PRICE) != marketPrice:
                self.closeOrderUpdatedTimes += 1
                updateFields = UpdateOrderFields()
                tagLog = (f"{self.gridMode}: Update {tradeType} order @{self.closeOrderUpdatedTimes}, targetQuantity={targetQuantity}, "
                          f"marketPrice={marketPrice}, averagePrice={averagePrice}, {stopProfitLevelMsg}.")
                log(f"{self.getSymbolAlias()}@{tagLog}", self.verbose)
                updateFields.limit_price = marketPrice
                updateFields.tag = decorateTag(tagLog)
                orderResponse = self.closeOrderTicket.update(updateFields)
                if orderResponse and orderResponse.is_error:
                    notify(f"{self.getNotifyPrefix()}: Failed to update close order ticket fields: {orderResponse}, tag=[{self.closeOrderTicket.tag}].")
            return None
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
                    self.closeOrderTicket = self.positionManager.limitOrder(targetQuantity, marketPrice, tagLog)
                return True
            return None

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
        settledOpenQuantity = self.gridMetadata.get(LIMetadataKey.settledOpenQuantity, 0)
        diffQuantity = settledOpenQuantity - self.getInvestedQuantity()
        if isNotLiveMode() and diffQuantity != 0:
            tagLog = f"Fulfill backtest with {diffQuantity} open positions at market order!"
            self.positionManager.marketOrder(diffQuantity, tagLog, False)
            log(f"{self.getSymbolAlias()}: {tagLog}")
            if settledOpenQuantity != self.getInvestedQuantity():
                error(f"Failed to fulfill {diffQuantity} open positions for backtest!")

    def cancelActiveOrders(self, onlyAlgoOrders=False):
        """ Cancel open order tickets for once if required!"""
        # DO NOT change exchange open status here, as we always want to cancel potential active orders!
        # if self.positionManager.isNotExchangeOpen():
        #     return  # Abort, wait for market open!
        self.positionManager.cancelActiveOrders(onlyAlgoOrders)

    def cancelExtraOpenOrders(self):
        """
        It's possible to submitted more/extra open orders during the course of trading session.
        """
        if self.positionManager.isNotExchangeOpen():
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
        if self.positionManager.isNotExchangeOpen():
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
                        if lot.closeOrderTicket.order_type == OrderType.LIMIT:
                            lot.closeOrderPrice = lot.closeOrderTicket.get(OrderField.LIMIT_PRICE)
                        elif lot.closeOrderTicket.order_type == OrderType.STOP_LIMIT:
                            lot.stopOrderPrice = lot.closeOrderTicket.get(OrderField.STOP_PRICE)
                            lot.closeOrderPrice = lot.closeOrderTicket.get(OrderField.LIMIT_PRICE)
                        elif lot.closeOrderTicket.order_type == OrderType.STOP_MARKET:
                            lot.stopOrderPrice = lot.closeOrderTicket.get(OrderField.STOP_PRICE)
                        elif lot.closeOrderTicket.order_type == OrderType.TRAILING_STOP:
                            lot.stopOrderPrice = lot.closeOrderTicket.get(OrderField.STOP_PRICE)
                            lot.trailingAmount = lot.closeOrderTicket.get(OrderField.TRAILING_AMOUNT)
                        lot.closeOrderQuantity = lot.closeOrderTicket.quantity
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
                        if lot.closeOrderTicket.order_type == OrderType.LIMIT:
                            lot.closeOrderPrice = lot.closeOrderTicket.get(OrderField.LIMIT_PRICE)
                        elif lot.closeOrderTicket.order_type == OrderType.STOP_LIMIT:
                            lot.stopOrderPrice = lot.closeOrderTicket.get(OrderField.STOP_PRICE)
                            lot.closeOrderPrice = lot.closeOrderTicket.get(OrderField.LIMIT_PRICE)
                        elif lot.closeOrderTicket.order_type == OrderType.STOP_MARKET:
                            lot.stopOrderPrice = lot.closeOrderTicket.get(OrderField.STOP_PRICE)
                        elif lot.closeOrderTicket.order_type == OrderType.TRAILING_STOP:
                            lot.stopOrderPrice = lot.closeOrderTicket.get(OrderField.STOP_PRICE)
                            lot.trailingAmount = lot.closeOrderTicket.get(OrderField.TRAILING_AMOUNT)
                        lot.closeOrderQuantity = lot.closeOrderTicket.quantity
                        lot.cancelCloseOrderTicket(
                            f"Cancel extra {LITradeType.CLOSING} order ticket as closingOrders={self.countCloseOrders(peerLot=lot)}>{self.gridMaintainCloseOrders}.")
                        lot.lotStatus = LILotStatus.CLOSING
                lot = lot.nextLot

    def manageGridRollover(self, bar=None):
        """Rollover, force to fill the same amount of lots with market price!"""
        if self.positionManager.isNotExchangeOpen():
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
        if self.gridRolloverCriteria[2] and not self.positionManager.isInvested():  # Skip if already invested!
            limitStartPrices = f", limitStartPrices={self.gridLimitStartPrices}" if self.gridLimitStartPrices else ""
            fixedStartPrices = f", fixedStartPrices={self.gridFixedStartPrices}" if self.gridFixedStartPrices else ""
            tagLog = f"Rolled over {self.gridRolloverCriteria} with marketPrice={self.getMarketPrice()}{limitStartPrices}{fixedStartPrices}"
            if not self.rolloverOrderTicket:
                self.rolloverOrderTicket = self.positionManager.limitMarketOrder(self.gridRolloverCriteria[2], tagLog)
                liveSleep(10)  # Wait a few seconds for limit market order to be filled
            if self.rolloverOrderTicket.status != OrderStatus.FILLED:
                return  # Abort, not filled yet!
            retainStartPrices = self.manageGridStartPrices(retainOpenedLots=self.gridRolloverCriteria[1],
                                                           filledMarketPrice=self.rolloverOrderTicket.average_fill_price,
                                                           overwriteStartPrices=False)  # Keep tracking max/min start prices
            filledQuantity = f", filledQuantity={self.rolloverOrderTicket.quantity}"
            avgFilledPrice = f", avgFilledPrice={self.rolloverOrderTicket.average_fill_price}"
            retainStartPrices = f", retainStartPrices={retainStartPrices}" if retainStartPrices else ""
            notify(f"{self.getNotifyPrefix()}: {tagLog}{avgFilledPrice}{filledQuantity}{retainStartPrices} and final {self.printGridPrices()}!")
            self.rolloverOrderTicket = None  # Clear it for next time
        self.gridRolloverCriteria = None  # Mark it completed!

    def getAugmentedAmount(self, lotIdFactor):
        return self.gridLotLevelAmount + self.gridLotLevelAugment * (abs(lotIdFactor) - 1)

    def getAugmentedPercent(self, lotIdFactor):
        return self.gridLotLevelPercent + self.gridLotLevelAugment * (abs(lotIdFactor) - 1)

    def fireOrderEvents(self, orderTicket: OrderTicket):
        # NOTE: this fire order events could cause "maximum recursion depth exceeded" for option trading
        # Only need to fire order evens for market order in backtest mode!!!
        # if orderTicket.order_type == OrderType.MARKET:
        for orderEvent in orderTicket.order_events:
            self.onOrderEvent(orderEvent)
            orderEvent.order_id *= -1  # Avoid repeating order event

    def onOrderEvent(self, orderEvent: OrderEvent):
        if orderEvent.symbol != self.getSymbol():
            return  # Abort, not for this symbol!
        filledAnyOrder = False
        if orderEvent.status == OrderStatus.FILLED or orderEvent.fill_quantity != 0:
            log(f"{self.getSymbolAlias()}: Received filled order event: {orderEvent}", self.verbose)
        if orderEvent.status == OrderStatus.INVALID:
            self.invalidOrderCount += 1
            if self.invalidOrderCount == 1:  # Only alert once!
                alert(f"{self.getNotifyPrefix()}: Received invalid order event: {orderEvent}")
        if self.openOrderTicket:
            filledAnyOrder = self.onOpenOrderEvent(orderEvent) or filledAnyOrder
        if self.closeOrderTicket:
            filledAnyOrder = self.onCloseOrderEvent(orderEvent) or filledAnyOrder
        # Pass down to lots
        lot = self.getTradeLot()
        while lot:
            filledAnyOrder = lot.onOrderEvent(orderEvent) or filledAnyOrder
            lot = lot.getNextLot()
        if filledAnyOrder:
            # self.saveSessionMetadata(False)
            # self.printGridSession(withLots=False)
            # TEST: It performs worse a bit with this immediate refresh
            # self.manageGridOrderTickets()
            return  # Already handled!
        if orderEvent.status == OrderStatus.FILLED or orderEvent.fill_quantity != 0:
            order = getAlgo().transactions.get_order_by_id(orderEvent.order_id)
            log(f"{self.getSymbolAlias()}: Received filled order event for stop loss/profit orders: {orderEvent}; {order}", self.verbose)
            if not order or not order.tag or not re.match(r'^\d{2}/\d{2}/\d{2}T\d{2}:\d{2}', order.tag):
                log(f"{self.getSymbolAlias()}: Detected a manual order has been filled: {orderEvent}; {order}")
                self.manageLeakingPositions(orderEvent=orderEvent)

    def onOpenOrderEvent(self, orderEvent):
        if self.openOrderTicket and self.openOrderTicket.order_id == orderEvent.order_id:
            if orderEvent.status == OrderStatus.NEW or orderEvent.status == OrderStatus.SUBMITTED or orderEvent.status == OrderStatus.UPDATE_SUBMITTED:
                return True
            elif orderEvent.status == OrderStatus.CANCELED or orderEvent.status == OrderStatus.INVALID:
                self.openOrderTicket = None
                return True
            elif orderEvent.status == OrderStatus.PARTIALLY_FILLED:
                self.accruedFees += orderEvent.order_fee.value.amount
                return True
            elif orderEvent.status == OrderStatus.FILLED:
                '''Can get info from either order event or order ticket'''
                filledOpenPrice = self.openOrderTicket.average_fill_price if self.openOrderTicket else orderEvent.fill_price
                filledOpenPrice = self.positionManager.roundSecurityPrice(filledOpenPrice)
                filledOpenQuantity = self.openOrderTicket.quantity_filled if self.openOrderTicket else orderEvent.fill_quantity
                self.accruedFees += orderEvent.order_fee.value.amount
                orderEvent.fill_price = filledOpenPrice  # Overwrite with average fill price
                orderEvent.fill_quantity = filledOpenQuantity  # Overwrite with actual fill quantity
                orderEvent.quantity = filledOpenQuantity  # Overwrite with actual fill quantity
                orderEvent.order_fee.value = CashAmount(self.accruedFees, orderEvent.order_fee.value.currency)  # Overwrite with all open orders' fees
                additionalMsgs = f"maxProfitLoss={self.getMaxProfitLossAmount()}({self.getMaxProfitLossPercent()}%)"
                self.positionManager.notifyOrderFilled(orderEvent, netProfit=0, additionalMsgs=additionalMsgs, delayMaxMsgs=3)
                self.accruedFees = 0.0
                self.openOrderTicket = None
                self.avgFilledOpenPrice = self.positionManager.getAveragePrice()  # Save it before positions closed!
                if self.isBoostingMode():
                    self.manageGridBoosting(forceTrade=True)  # Trigger all related actions
                else:
                    self.manageGridTrading(forceTrade=True)  # Trigger all related actions
                return True
        return None

    def onCloseOrderEvent(self, orderEvent):
        delayMaxMsgs = 0 if self.isBoostingMode() else 0
        if self.closeOrderTicket and self.closeOrderTicket.order_id == orderEvent.order_id:
            if orderEvent.status == OrderStatus.NEW or orderEvent.status == OrderStatus.SUBMITTED or orderEvent.status == OrderStatus.UPDATE_SUBMITTED:
                return True
            elif orderEvent.status == OrderStatus.CANCELED or orderEvent.status == OrderStatus.INVALID:
                self.closeOrderTicket = None
                return True
            elif orderEvent.status == OrderStatus.PARTIALLY_FILLED:
                self.accruedFees += orderEvent.order_fee.value.amount
                return True
            elif orderEvent.status == OrderStatus.FILLED:
                filledPrice = self.closeOrderTicket.average_fill_price if self.closeOrderTicket else orderEvent.fill_price
                filledQuantity = self.closeOrderTicket.quantity_filled if self.closeOrderTicket else orderEvent.fill_quantity
                if self.avgFilledOpenPrice:
                    profitLossPoints = (filledPrice - self.avgFilledOpenPrice) * (1 if filledQuantity < 0 else -1)
                    profitLossPoints *= abs(filledQuantity)
                else:
                    order = getAlgo().transactions.get_order_by_id(orderEvent.order_id)
                    closedTrade = self.positionManager.getLastClosedTrade(order.last_fill_time)
                    profitLossPoints = closedTrade.profit_loss if closedTrade else 0.0
                profitLoss = round(profitLossPoints * self.positionManager.getSecurityMultiplier(), LIGlobal.moneyPrecision)
                self.accruedFees += orderEvent.order_fee.value.amount
                quantity = abs(filledQuantity)
                capital = round(quantity * getMaintenanceMargin(self.getSymbol(), filledPrice), LIGlobal.moneyPrecision)
                duration = 0
                netProfit = round(profitLoss - self.accruedFees, LIGlobal.moneyPrecision)  # Use local calculated value
                orderEvent.fill_price = filledPrice  # Overwrite with average fill price
                orderEvent.fill_quantity = filledQuantity  # Overwrite with actual fill quantity
                orderEvent.quantity = filledQuantity  # Overwrite with actual fill quantity
                orderEvent.order_fee.value = CashAmount(self.accruedFees / 2, orderEvent.order_fee.value.currency)  # Overwrite with all close orders' fees
                self.realizedProfitLoss = round(self.realizedProfitLoss + netProfit, LIGlobal.moneyPrecision)
                self.closedTradesCount += 1
                additionalMsgs = f"maxProfitLoss={self.getMaxProfitLossAmount()}({self.getMaxProfitLossPercent()}%)"
                self.positionManager.notifyOrderFilled(orderEvent, netProfit=netProfit, additionalMsgs=additionalMsgs, delayMaxMsgs=delayMaxMsgs)
                addDailyClosedTrade(self.canonicalSymbol.value, [profitLoss, self.accruedFees, capital, quantity, duration])
                self.accruedFees = 0.0
                self.realizedProfitLoss = 0.0
                self.closeOrderTicket = None
                self.trailingStopPrice = None
                self.avgFilledOpenPrice = None
                if self.pauseTradingProfitLossHours and netProfit > self.pauseTradingProfitLossHours[0]:
                    self.pauseTradingTillTime = getAlgoTime() + timedelta(hours=self.pauseTradingProfitLossHours[1])
                if self.isBoostingMode():
                    self.switchOffBoostingMode()
                if self.forecloseHoldingPositions:
                    self.forecloseHoldingPositions = self.forecloseHoldingPositions[1:]  # Remove the first item
                    self.manageGridTrading()
                return True
        return None

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
                if self.getSymbol() == order.symbol:
                    if self.liquidateGridSession("MARGIN CALLED"):
                        newQuantity = 0  # Already liquidated grid session!
                        requests[i] = SubmitOrderRequest(order.order_type, order.security_type,
                                                         order.symbol, newQuantity, order.stop_price,
                                                         order.limit_price, 0, getAlgoTime(), "Already liquidated on margin call!")
                        getAlgo().quit("Quit algorithm upon margin call, please adjust settings and redeploy!")
        return requests

    def onCloseOfMarket(self):
        if getAlgoTime().weekday() == 4:
            if self.liquidateOnFridayClose:
                if self.liquidateGridSession("FRIDAY CLOSE"):
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
            self.cancelActiveOrders(onlyAlgoOrders=True)
        if self.gridMetadataKey and self.saveMetadataAtEnd:
            self.storeGridMetadata()
        # sendDailyReport()  # Testing purpose for the daily report
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
            f"{self.getSymbolAlias()}: Session#{self.sessionId}, gridLots={self.countTradeLots()}, filledLots(total/long/short)={self.countFilledLots()}, "
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
        ellipsisLine = "#...lots..."
        while lot:
            if printHeadTailLots and printHeadTailLots < abs(lot.lotId) < (tradeLots[1] if lot.isLongLot() else tradeLots[2]) - printHeadTailLots:
                if targetPrices and targetPrices[-1] != ellipsisLine:
                    targetPrices.append(ellipsisLine)
            else:
                openPrice = lot.getOpenTargetPrice()
                closePrice = lot.getCloseTargetPrice()
                stopLossPrice = lot.getStopLossPrice()
                targetPrices.append(f"#{lot.lotId}/{openPrice}"
                                    f"{f'/{closePrice - openPrice:+.2f}' if closePrice and openPrice and not self.isBuyAndHoldMode() else ''}"
                                    f"{f'/{stopLossPrice[0] - openPrice:+.2f}' if stopLossPrice and openPrice else ''}")
            lot = lot.getNextLot()
        notifyMsg = (
            f"{self.getSymbolAlias()}: Session#{self.sessionId}, marketPrice={self.getMarketPrice()}, "
            f"filledLots(total/long/short)={self.countFilledLots()}, investedQuantity={self.getInvestedQuantity()}, "
            f"unrealizedProfit={self.getUnrealizedProfitAmount()}, totalNetProfit={self.getTotalNetProfitAmount()}, "
            f"overallMaxProfitLoss={self.overallMaxProfitLoss}, {self.printGridPrices()}, signalType={self.getTradeInsight().signalType}, ")
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
                getAlgo().quit("Quit algorithm on INITIALIZE SESSION!")
                return  # Quit execution immediately!
            else:
                self.restartGridSession(startPrices=self.gridStartPrices, reason="Start grid session")
        else:
            self.initBacktestStatus()
            self.restoreGridMetadata()
            self.resetGridStartPrices()
            self.realignOpenPositions()
            self.cancelActiveOrders(onlyAlgoOrders=True)
            self.manageGridTrading()
            self.sessionStartedTime = getAlgoTime()
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
        return None

    def getOpenFromPrice(self, gridSide: LIGridSide):
        if self.gridFixedOpenFromPrices:
            return self.gridFixedOpenFromPrices[gridSide]
        elif self.gridBandingOpenFromPrices:
            return self.positionManager.roundSecurityPrice(self.bollingerBandsIndicator.getBand(self.gridBandingOpenFromPrices[gridSide]).getPrice())
        return None

    def getLimitStartPrice(self, gridSide: LIGridSide):
        if self.gridLimitStartPrices:
            return self.gridLimitStartPrices[gridSide]
        elif self.gridBandingLimitStartPrices:
            return self.positionManager.roundSecurityPrice(self.bollingerBandsIndicator.getBand(self.gridBandingLimitStartPrices[gridSide]).getPrice())
        return None

    def estimateFilledLots(self, investedQuantity):
        """Recalculate the filled lots based on market price or lot quantity."""
        newFilledLots = 0
        if investedQuantity:
            if self.isLongSideActive():
                targetLot = self.startLot.nextLot
                while targetLot and investedQuantity > 0:
                    if targetLot.isLongLot() and not targetLot.pausedOpening:
                        investedQuantity -= abs(self.getTargetQuantity(targetLot))
                        newFilledLots += 1
                    targetLot = targetLot.nextLot
            if self.isShortSideActive():
                targetLot = self.startLot.prevLot
                while targetLot and investedQuantity < 0:
                    if targetLot.isShortLot() and not targetLot.pausedOpening:
                        investedQuantity += abs(self.getTargetQuantity(targetLot))
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

        investedQuantity = self.getInvestedQuantity() - self.dcaHoldingQuantity
        newFilledLots = abs(self.estimateFilledLots(investedQuantity))
        newLotQuantity = self.positionManager.roundSecuritySize(investedQuantity / newFilledLots) if newFilledLots else 0
        log(f"{self.getSymbolAlias()}: Realign investedQuantity={investedQuantity} from filledLots(total/long/short)={self.countFilledLots()} to "
            f"newFilledLots={newFilledLots}, newLotQuantity={newLotQuantity}.")

        # Calculate new start prices accordingly!
        self.resetGridStartPrices(emptyStartPrices=True, emptyOpenFromPrices=True)
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
                getAlgo().quit("Quit algorithm on REALIGNED OPEN POSITIONS!")
            else:
                notify(f"{self.getNotifyPrefix()}: Applied the settings: {settings}!")

    def resetOpeningProps(self, preserveOpenPrice=False):
        lot = self.getTradeLot()
        while lot:
            lot.resetOpeningProps(preserveOpenPrice=preserveOpenPrice)
            lot = lot.getNextLot()

    def hasLeakingPositions(self, leakingQuantity):
        return (leakingQuantity
                and (not self.gridLotMinAmount or abs(leakingQuantity * self.getMarketPrice()) >= abs(self.gridLotMinAmount))
                and (not self.gridLotMinQuantity or abs(leakingQuantity) >= abs(self.gridLotMinQuantity)))

    def manageLeakingPositions(self, lotQuantity=None, orderEvent=None, realignOpenPositions=False, logAssignment=True):
        """Assign possible leaking open positions to proper trading grid lots!"""
        if not (lotQuantity or orderEvent or realignOpenPositions or self.positionManager.isExchangeOpen()):
            return  # Abort, wait for market open!

        resetStartPrices = False  # Whether need to reset start prices!

        # if orderEvent and self.settledOpenQuantity != 0 and self.getInvestedQuantity() == 0:
        #     # Special case: all positions closed but having order event with large fill quantity
        #     notify(f"{self.getNotifyPrefix()}: Restart grid session due to full position close event: {orderEvent}")
        #     self.restartGridSession(reason="Restart after liquidation")
        #     self.settledOpenQuantity = 0
        #     return  # Already restarted grid session!

        # LONG side: When having leaking open positions, assign them to proper lots
        leakingQuantity = self.getLeakingQuantity()
        if (not orderEvent and leakingQuantity > 0
                and (self.settledOpenQuantity > 0 or self.isLongSideActive())
                and (not self.tradeInsight or self.tradeInsight.signalType != LISignalType.SHORT)):
            log(f"{self.getSymbolAlias()}: Manage leaking positions #1 for long side: leakingQuantity={leakingQuantity}", self.verbose)
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

        # SHORT side: When having leaking open positions, assign them to proper lots
        leakingQuantity = self.getLeakingQuantity()
        if (not orderEvent and leakingQuantity < 0
                and (self.settledOpenQuantity < 0 or self.isShortSideActive())
                and (not self.tradeInsight or self.tradeInsight.signalType != LISignalType.LONG)):
            log(f"{self.getSymbolAlias()}: Manage leaking positions #2 for short side: leakingQuantity={leakingQuantity}", self.verbose)
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

        # LONG side: Could be caused by manual or market order due to manual intervene, stop loss hedging or margin call! Reset some lots
        leakingQuantity = self.getLeakingQuantity()
        if (leakingQuantity < 0
                and (self.settledOpenQuantity > 0 or self.isLongSideActive())
                and abs(self.getOpeningQuantity()) >= abs(leakingQuantity)):
            log(f"{self.getSymbolAlias()}: Manage leaking positions #3 for long side: leakingQuantity={leakingQuantity}", self.verbose)
            lot = self.getLastLongLot()
            while lot and lot != self.startLot and leakingQuantity < 0 and self.hasLeakingPositions(leakingQuantity):
                if lot.isLongLot() and not lot.pausedOpening and lot.hasOpenPosition():
                    reason = f"Reset lot to fix leaking positions"
                    lot.resetTradingLot(reason)
                    resetStartPrices = True
                    notify(f"{self.getSymbolAlias()}: {reason}: {lot}")
                    leakingQuantity = self.getLeakingQuantity()
                lot = lot.prevLot

        # SHORT side: Could be caused by manual or market order due to manual intervene, stop loss hedging or margin call! Reset some lots
        leakingQuantity = self.getLeakingQuantity()
        if (leakingQuantity > 0
                and (self.settledOpenQuantity < 0 or self.isShortSideActive())
                and abs(self.getOpeningQuantity()) >= abs(leakingQuantity)):
            log(f"{self.getSymbolAlias()}: Manage leaking positions #4 for short side: leakingQuantity={leakingQuantity}", self.verbose)
            lot = self.getLastShortLot()
            while lot and lot != self.startLot and leakingQuantity > 0 and self.hasLeakingPositions(leakingQuantity):
                if lot.isShortLot() and not lot.pausedOpening and lot.hasOpenPosition():
                    reason = f"Reset lot to fix leaking positions"
                    lot.resetTradingLot(reason)
                    resetStartPrices = True
                    notify(f"{self.getSymbolAlias()}: {reason}: {lot}")
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
            log(f"{self.getSymbolAlias()}: Manage leaking positions #5 for final try: leakingQuantity={leakingQuantity}", self.verbose)
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
                      f"Quantity(invested/opening/closing)={self.getInvestedQuantity()}/{self.getOpeningQuantity()}/{self.getClosingQuantity()}. "
                      f"You can manually close these leaking positions to align with grid lots status.")
            self.printGridSession(withLots=True)

        # Reset grid start prices if needed, so next trading will be aligned with current market price
        if resetStartPrices:
            self.resetGridStartPrices(emptyStartPrices=True, emptyOpenFromPrices=True)

        # Store invested quantity after resolved leaking positions for next time comparison
        if self.getLeakingQuantity() == 0:
            self.settledOpenQuantity = self.getInvestedQuantity()

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
        if (not (self.marketBias or self.gridFixedStartPrices or self.gridBandingStartPrices or self.gridHedgeEnabled)
                and self.tradeBothSides() and self.gridStartPrices.get(self.getGridLongSide()) and self.gridStartPrices.get(self.getGridShortSide())):
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
        if (self.extendedMarketHours or isActiveMarketTime(getAlgoTime()) or
                (atMarketOpenTime(delta=self.getMonitorPeriodDelta()) and self.getInvestedQuantity() == 0)):
            if self.gridMonitorPeriodFactors:
                if self.getInvestedQuantity() >= 0 and not isTickTime(timestamp=bar.end_time,
                                                                      delta=self.gridMonitorPeriodFactors.get(self.getGridLongSide(),
                                                                                                              1) * self.getMonitorPeriodDelta()):
                    return  # Abort
                if self.getInvestedQuantity() < 0 and not isTickTime(timestamp=bar.end_time,
                                                                     delta=self.gridMonitorPeriodFactors.get(self.getGridShortSide(),
                                                                                                             1) * self.getMonitorPeriodDelta()):
                    return  # Abort
            marketPrice = self.positionManager.roundSecurityPrice(bar.close)
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
        #     log(f"{self.getSymbolAlias()}: onMonitorBarUpdated={bar} endTime: {bar.end_time.strftime(LIGlobal.secondFormat)}, "
        #         f"isExchangeOpen={self.positionManager.isExchangeOpen()}, filledLots(total/long/short)={self.countFilledLots()}")
        if self.plotDefaultChart:
            plot(self.mainChart.name, "Price", bar.close)
        self.lastBar = bar  # Cache closed bar
        if self.gridHeikinAshies:
            self.gridHeikinAshies[0].update(bar)
        else:
            self.updateGridSession(bar)

    def onHeikinAshiUpdated(self, sender: HeikinAshi, updated: IndicatorDataPoint):
        if not sender.is_ready:
            return  # Abort
        bar = TradeBar(self.lastBar.time,
                       sender.current.symbol,
                       sender.open.current.value,
                       sender.high.current.value,
                       sender.low.current.value,
                       sender.close.current.value,
                       sender.volume.current.value,
                       self.lastBar.period)
        n = int(sender.name)
        if n < len(self.gridHeikinAshies) - 1:
            self.gridHeikinAshies[n + 1].update(bar)  # Call next ply
        else:
            if self.plotDefaultChart:
                plot(self.mainChart.name, "HPrice", bar.close)
            self.updateGridSession(bar)
