# region imports
import sys
from core.LIGridBaseLot import *
from core.LIPositionManager import *


# endregion

class LIGridTradingLot(LIGridBaseLot):
    def __init__(self, lotId, gridTrading):
        super().__init__(lotId, gridTrading)

    def manageLotOrderTickets(self, bar=None, openWithMarketOrder=False, closeWithMarketOrder=False):
        if not self.positionManager.isExchangeOpen():
            return False  # Abort, wait for market open!
        result = False
        result = self.manageLotOpenOrderTicket(useMarketOrder=openWithMarketOrder) or result
        if not self.isBuyAndHoldMode():
            result = self.manageLotCloseOrderTicket(useMarketOrder=closeWithMarketOrder) or result
        return result

    def getSortedOpenPrice(self, targetPrice, marketPrice, openFromPrice=None, useMarketOrder=False):
        openPrice = targetPrice
        if self.isLongLot():
            if self.isMomentumMode():
                openPrice = marketPrice if useMarketOrder else max(marketPrice, targetPrice)  # Take advantage of market gap
                openPrice = max(openFromPrice, openPrice) if openFromPrice else openPrice
            elif self.isContrarianMode():
                openPrice = marketPrice if useMarketOrder else min(marketPrice, targetPrice)  # Take advantage of market gap
                openPrice = min(openFromPrice, openPrice) if openFromPrice else openPrice
        if self.isShortLot():
            if self.isMomentumMode():
                openPrice = marketPrice if useMarketOrder else min(marketPrice, targetPrice)  # Take advantage of market gap
                openPrice = min(openFromPrice, openPrice) if openFromPrice else openPrice
            elif self.isContrarianMode():
                openPrice = marketPrice if useMarketOrder else max(marketPrice, targetPrice)  # Take advantage of market gap
                openPrice = max(openFromPrice, openPrice) if openFromPrice else openPrice
        return openPrice

    def manageLotOpenOrderTicket(self, useMarketOrder=False, boostMorePositions=False):
        if self.gridTrading.gridNoMoreOpenOrders:
            log(f"{self.getSymbolAlias()}@{self.getLotName()}: Abort placing open order ticket as "
                f"{LIConfigKey.gridNoMoreOpenOrders}={self.gridTrading.gridNoMoreOpenOrders}", self.verbose)
            return False  # Abort, no more open orders!

        if self.gridTrading.gridOpenFromPrices:
            if self.isMomentumMode() and not self.gridTrading.reachedOpenPrice:
                log(f"{self.getSymbolAlias()}@{self.getLotName()}: Abort placing open order ticket as marketPrice={self.getMarketPrice()} not reached "
                    f"gridOpenFromPrices={self.gridTrading.gridOpenFromPrices} yet!", self.verbose)
                return False

        marketPrice = self.getMarketPrice()
        targetPrice = self.getOpenTargetPrice()
        targetQuantity = self.getUnfilledQuantity()
        stoppedLossPrices = self.gridTrading.stoppedLossPrices
        maintainOpenOrders = self.gridTrading.gridMaintainOpenOrders

        # Check whether market revert back to the liquidated price
        if self.gridTrading.liquidateLossAndLimitTrading:
            if self.isContrarianMode():
                if self.isLongLot() and self.getGridSide() in stoppedLossPrices and targetPrice < stoppedLossPrices[self.getGridSide()]:
                    return False
                if self.isShortLot() and self.getGridSide() in stoppedLossPrices and targetPrice > stoppedLossPrices[self.getGridSide()]:
                    return False

        # Reset paused trading if market price came back
        if self.isPausedOpening():
            if self.isMomentumMode() and self.gridLotPauseAfterProfit:
                if (self.isLongLot() and targetPrice > marketPrice) or (self.isShortLot() and targetPrice < marketPrice):
                    log(f"{self.getSymbolAlias()}@{self.getLotName()}: Enable this lot's trading again since market price reverts to "
                        f"targetPrice={targetPrice}, marketPrice={marketPrice}.")
                    self.pausedOpening = False  # Enable again
            elif self.isContrarianMode() and self.gridLotPauseAfterStopLoss:
                stopLossPrice = self.getStopLossPrice()
                unpausePrice = stopLossPrice[0] if stopLossPrice else targetPrice
                if (self.isLongLot() and unpausePrice < marketPrice) or (self.isShortLot() and unpausePrice > marketPrice):
                    log(f"{self.getSymbolAlias()}@{self.getLotName()}: Enable this lot's trading again since market price reverts to "
                        f"unpausePrice={unpausePrice}, marketPrice={marketPrice}, targetPrice={targetPrice}, stopLossPrice={stopLossPrice}.")
                    self.pausedOpening = False  # Enable again

        if self.isPausedOpening():
            return False  # Abort

        if self.hasOpenPosition() and not boostMorePositions:
            return False  # Abort, fully filled!

        if self.gridLotMinQuantity and abs(targetQuantity) < self.gridLotMinQuantity:
            log(f"{self.getSymbolAlias()}@{self.getLotName()}: The targetQuantity={targetQuantity} is too small to open an order as "
                f"{LIConfigKey.gridLotMinQuantity}={self.gridLotMinQuantity}")
            return False

        if targetPrice <= 0:  # Important! Avoid initialization failure.
            return False  # Abort, invalid target price!

        if self.gridTrailingOpenPriceFactor and marketPrice != self.gridTrading.lastTradingMarketPrice:
            trailingOpenPrice = self.getTrailingOpenPrice(marketPrice=marketPrice)
            newTargetPrice = None
            if self.isMomentumMode():
                if self.isLongLot():
                    newTargetPrice = max(min(targetPrice, trailingOpenPrice), self.trailingOpenPrice if self.trailingOpenPrice else sys.float_info.min)
                if self.isShortLot():
                    newTargetPrice = min(max(targetPrice, trailingOpenPrice, self.trailingOpenPrice if self.trailingOpenPrice else sys.float_info.max))
            elif self.isContrarianMode():
                if self.isLongLot():
                    newTargetPrice = max(max(targetPrice, trailingOpenPrice), self.trailingOpenPrice if self.trailingOpenPrice else sys.float_info.min)
                if self.isShortLot():
                    newTargetPrice = min(min(targetPrice, trailingOpenPrice), self.trailingOpenPrice if self.trailingOpenPrice else sys.float_info.max)
            # Only adjust the very last lot's target price based on current market price
            if self.isLastOpeningLot():
                oldTargetPrice = (self.trailingOpenPrice if self.trailingOpenPrice else targetPrice)
                if oldTargetPrice != newTargetPrice:  # Reduce amount of logging
                    log(f"{self.getSymbolAlias()}@{self.getLotName()}: Adjusted open price from {oldTargetPrice} to {newTargetPrice} "
                        f"in order to fill back open orders/positions sooner as startPrice={self.getStartPrice()}, "
                        f"marketPrice={marketPrice}, targetPrice={targetPrice}, trailingOpenPrice={trailingOpenPrice}, "
                        f"{LIConfigKey.gridTrailingOpenPriceFactor}={self.gridTrailingOpenPriceFactor}.")
                targetPrice = self.trailingOpenPrice = newTargetPrice

        openFromPrice = None
        if self.isContrarianMode():
            openFromPrice = self.getOpenFromPrice()

        openPrice = self.getSortedOpenPrice(targetPrice, marketPrice, openFromPrice, useMarketOrder)

        # Adjust open price according to boost more positions!
        if boostMorePositions:
            maxHoldQuantity = self.gridTrading.gridBoostingMaxHoldQuantity
            investedQuantity = self.gridTrading.getInvestedQuantity()
            targetQuantity = min(self.getTargetQuantity(), maxHoldQuantity - investedQuantity)
            if targetQuantity <= 0:
                log(f"{self.getSymbolAlias()}@{self.getLotName()}: Abort boosting more positions as targetQuantity={targetQuantity}, "
                    f"investedQuantity={investedQuantity}, maxHoldQuantity={maxHoldQuantity}.")
                return False
            openPrice = marketPrice
            if self.openWithMarketOrderType:
                useMarketOrder = True
            if self.openOrderTicket and not isOrderTicketUpdatable(self.openOrderTicket):
                self.openOrderTicket = None  # Reset ever filled open order ticket
            log(f"{self.getSymbolAlias()}@{self.getLotName()}: Boosting more positions now as targetQuantity={targetQuantity}, "
                f"investedQuantity={investedQuantity}, maxHoldQuantity={maxHoldQuantity}, "
                f"profitLossFactor={self.getProfitLossFactor()} >= boostingProfitFactor={self.getBoostingProfitFactor()}.")

        #  Adjust open price according to trade insight if enabled!
        openPositionsNow = False
        if self.gridTrading.gridUseTradeInsight:
            tradeInsight = self.gridTrading.getTradeInsight()
            if not tradeInsight or tradeInsight.isNoneSignal():
                return  # Abort as no signal yet!
            if tradeInsight.isLongSignal():
                if self.isShortLot():
                    self.pausedOpening = False  # Enable counterpart lot for future short signal
                    self.cancelOpenOrderTicket(f"Cancel {LITradeType.OPENING} order as per tradeInsight={tradeInsight}.")
                    return  # Abort as against the Long signal
                elif self.isFirstLongLot() and self.hasNoOpenPosition():
                    openPositionsNow = True
            elif tradeInsight.isShortSignal():
                if self.isLongLot():
                    self.pausedOpening = False  # Enable counterpart lot for future long signal
                    self.cancelOpenOrderTicket(f"Cancel {LITradeType.OPENING} order as per tradeInsight={tradeInsight}.")
                    return  # Abort as against the Short signal
                elif self.isFirstShortLot() and self.hasNoOpenPosition():
                    openPositionsNow = True
            elif tradeInsight.isCloseSignal():
                self.cancelOpenOrderTicket(f"Cancel {LITradeType.OPENING} order as per tradeInsight={tradeInsight}.")
                return  # Abort as per the Close signal
            else:
                raise TypeError(f"Not support tradeInsight={tradeInsight}!")
            if openPositionsNow:
                openPrice = marketPrice
                if self.openWithMarketOrderType:
                    useMarketOrder = True
                log(f"{self.getSymbolAlias()}@{self.getLotName()}: Opening positions now as per tradeInsight={tradeInsight}.")

        # Adjust open price according to counterpart losing lots!
        if self.gridTrading.gridHedgeEnabled:
            hedgeOverLosingLots = self.gridTrading.gridHedgeOverLosingLots
            if hedgeOverLosingLots:
                losingLots = self.gridTrading.countLosingLots(peerLot=self.getCounterpartLot())
                if losingLots > hedgeOverLosingLots:
                    openPrice = marketPrice
                    if self.openWithMarketOrderType:
                        useMarketOrder = True
                    log(f"{self.getSymbolAlias()}@{self.getLotName()}: Opening positions now as counterpart losing lots are greater than {losingLots}.")

        # Make sure the open prices are NOT too close!
        if self.gridTrading.gridKeepOpenOrdersApart:
            priorLot = self.getPriorLot()
            if not priorLot.isStartLot() and priorLot.filledOpenPrice:
                if abs(openPrice - priorLot.filledOpenPrice) < abs(self.getOpenTargetPrice() - priorLot.getOpenTargetPrice()) / 2:
                    log(f"{self.getSymbolAlias()}@{self.getLotName()}: Skip the open order ({openPrice}) as "
                        f"it's too close to prior lot's open price ({priorLot.filledOpenPrice}).")
                    return False  # Abort, too close!

        tradeType = LITradeType.OPENING_LIMIT
        stopLimitPrices = None  # (stopPrice, limitPrice, stopPriceFactor)
        if self.openWithStopOrderType:
            softLimitPrice = self.positionManager.softenLimitPrice2(targetQuantity, openPrice)
            stopLimitPrices = (openPrice, softLimitPrice)
            tradeType = LITradeType.OPENING_STOP_LIMIT
        elif useMarketOrder or (self.openWithMarketOrderType and not self.isContrarianMode()):
            tradeType = LITradeType.OPENING_LIMIT_MARKET if self.positionManager.enableLimitMarketOrder else LITradeType.OPENING_MARKET

        if useMarketOrder:
            if isOrderTicketUpdatable(self.openOrderTicket):
                if self.openOrderTicket.OrderType in [OrderType.MARKET, OrderType.MARKET_ON_OPEN, OrderType.MARKET_ON_CLOSE]:
                    log(f"{self.getSymbolAlias()}@{self.getLotName()}: Waiting for open order to be filled: orderId={self.openOrderTicket.order_id}, "
                        f"status={getEnumName(self.openOrderTicket.status, OrderStatus)}; {self.openOrderTicket.tag}")
                    return True
                else:
                    tagLog = f"Cancel {LITradeType.OPENING} {self.openOrderTicket.OrderType} order to use {tradeType} order! tag=[{self.openOrderTicket.Tag}]."
                    self.positionManager.cancelOrder(self.openOrderTicket, tagLog)
            tagLog = (f"{self.getLotName()}: Submit {tradeType} order at openPrice={openPrice}, targetPrice={targetPrice}, "
                      f"targetQuantity={targetQuantity}, {self.printGridLotPrices()}, marketPrice={marketPrice}, "
                      f"closeTargetPrice={self.getCloseTargetPrice()}.")
            if boostMorePositions:
                tagLog = tagLog.replace("Submit ", "Boosting ")
                tagLog += f" profitLossFactor={self.getProfitLossFactor()} >= boostingProfitFactor={self.getBoostingProfitFactor()}."
            log(f"{self.getSymbolAlias()}@{tagLog}")
            self.openOrderTicket = self.positionManager.limitMarketOrder(targetQuantity, tagLog)
            self.lotStatus = LILotStatus.OPENING
            self.fireOrderEvents(self.openOrderTicket)
            liveSleep(5)  # A little break
            return True
        elif isOrderTicketUpdatable(self.openOrderTicket):
            if targetQuantity == 0:
                tagLog = f"Cancel {LITradeType.OPENING} order as target quantity is 0 now!"
                self.positionManager.cancelOrder(self.openOrderTicket, tagLog)
                return True  # Abort, invalid order!
            if isStopOrderType(self.openOrderTicket) and not stopLimitPrices:
                terminate(f"Missing stopLimitPrices for the openOrderTicket!")
            if self.openOrderTicket.OrderType == OrderType.Market or self.openOrderTicket.OrderType == OrderType.MarketOnOpen:
                return True  # Abort, wait for market open
            openPriceMsg = f"stopLimitPrices={printStopLimitPrices(stopLimitPrices)}" if stopLimitPrices else f"openPrice={openPrice}"
            tagLog = (f"{self.getLotName()}: Update {tradeType} order at {openPriceMsg}, targetPrice={targetPrice}, "
                      f"targetQuantity={targetQuantity}, {self.printGridLotPrices()}, marketPrice={marketPrice}, "
                      f"closeTargetPrice={self.getCloseTargetPrice()}.")
            needToUpdate = False
            updateFields = UpdateOrderFields()
            if self.isMomentumMode():
                if self.openOrderTicket.OrderType == OrderType.STOP_LIMIT and (self.openOrderTicket.Get(OrderField.StopPrice) != targetPrice or
                                                                               self.openOrderTicket.Get(OrderField.LimitPrice) != stopLimitPrices[1]):
                    updateFields.StopPrice = targetPrice  # NOT update to open price as it is syncing with market price!
                    updateFields.LimitPrice = stopLimitPrices[1]
                    needToUpdate = True
                elif (self.isLongLot() and openPrice <= marketPrice) or (self.isShortLot() and openPrice >= marketPrice):
                    if self.openOrderTicket.OrderType == OrderType.LIMIT and self.openOrderTicket.Get(OrderField.LimitPrice) != openPrice:
                        updateFields.LimitPrice = openPrice
                        needToUpdate = True
            elif self.isContrarianMode():
                if self.openOrderTicket.Get(OrderField.LimitPrice) != openPrice:
                    updateFields.LimitPrice = openPrice
                    needToUpdate = True
            if needToUpdate:
                log(f"{self.getSymbolAlias()}@{tagLog}", self.verbose)
                updateFields.Quantity = targetQuantity
                updateFields.Tag = decorateTag(tagLog)
                self.openOrderTicket.Update(updateFields)
                self.lotStatus = LILotStatus.OPENING
                liveSleep(1)  # A little break
            return needToUpdate
        elif (targetQuantity != 0 and not self.openOrderTicket and
              (boostMorePositions or
               (maintainOpenOrders == 1 and self.canSubmitOpenOrder1()) or
               (maintainOpenOrders == 2 and self.canSubmitOpenOrder2()) or
               (maintainOpenOrders == 3 and self.canSubmitOpenOrder3()))):
            openPriceMsg = f"stopLimitPrices={printStopLimitPrices(stopLimitPrices)}" if stopLimitPrices else f"openPrice={openPrice}"
            tagLog = (f"{self.getLotName()}: Submit {tradeType} order at {openPriceMsg}, targetPrice={targetPrice}, "
                      f"targetQuantity={targetQuantity}, {self.printGridLotPrices()}, marketPrice={marketPrice}, "
                      f"closeTargetPrice={self.getCloseTargetPrice()}.")
            if boostMorePositions:
                tagLog = tagLog.replace("Submit ", "Boosting ")
                tagLog += f" profitLossFactor={self.getProfitLossFactor()} >= boostingProfitFactor={self.getBoostingProfitFactor()}."
            if self.isMomentumMode():
                if self.openWithStopOrderType:
                    log(f"{self.getSymbolAlias()}@{tagLog}")
                    self.openOrderTicket = getAlgo().StopLimitOrder(self.getSymbol(), targetQuantity, stopLimitPrices[0], stopLimitPrices[1],
                                                                    tag=decorateTag(tagLog))
                    self.lotStatus = LILotStatus.OPENING
                    liveSleep(1)  # A little break to propagate status
                    return True
                elif (self.isLongLot() and openPrice <= marketPrice) or (self.isShortLot() and openPrice >= marketPrice):
                    log(f"{self.getSymbolAlias()}@{tagLog}")
                    # TEST: It performs better with (limit) market order than stop limit order at this point!
                    if self.openWithMarketOrderType:
                        self.openOrderTicket = self.positionManager.limitMarketOrder(targetQuantity, tagLog)
                        self.fireOrderEvents(self.openOrderTicket)
                    else:
                        self.openOrderTicket = getAlgo().LimitOrder(self.getSymbol(), targetQuantity, marketPrice, tag=decorateTag(tagLog))
                    self.lotStatus = LILotStatus.OPENING
                    liveSleep(1)  # A little break to propagate status
                    return True
            elif self.isContrarianMode():
                log(f"{self.getSymbolAlias()}@{tagLog}")
                self.openOrderTicket = getAlgo().LimitOrder(self.getSymbol(), targetQuantity, openPrice, tag=decorateTag(tagLog))
                self.lotStatus = LILotStatus.OPENING
                liveSleep(1)  # A little break to propagate status
                return True
        elif self.openOrderTicket and self.openOrderTicket.status != OrderStatus.CANCEL_PENDING:
            alert(f"{self.getLotName()}: Seeing unexpected existing openOrderTicket={self.openOrderTicket}")
            self.fireOrderEvents(self.openOrderTicket)
            liveSleep(1)  # A little break to propagate status
            return True

        # Verify open order ticket status, skip it as an invalid order is still updatable and can be fixed later!
        # if self.openOrderTicket and self.openOrderTicket.Status == OrderStatus.Invalid:
        #     self.openOrderTicket = None  # Abort as invalid, catch error within onOrderEvent()
        #     return False

    def manageLotCloseOrderTicket(self, useMarketOrder=False):
        if self.gridTrading.gridNoMoreCloseOrders:
            log(f"{self.getSymbolAlias()}@{self.getLotName()}: Abort placing close order ticket as "
                f"{LIConfigKey.gridNoMoreCloseOrders}={self.gridTrading.gridNoMoreCloseOrders}", self.verbose)
            return False  # Abort, no more open orders!

        if self.hasNoOpenPosition():
            return False  # Abort, not filled open order yet!
        if not self.gridLotTakeProfitFactor:
            return False  # Abort, not specified profit factor!

        closePrice = 0
        marketPrice = self.getMarketPrice()
        targetPrice = self.getCloseTargetPrice()
        targetQuantity = -self.filledOpenQuantity

        # if self.gridLotMinQuantity and abs(targetQuantity) < self.gridLotMinQuantity:
        #     log(f"{self.getSymbolAlias()}@{self.getLotName()}: The targetQuantity={targetQuantity} is too small to close an order as "
        #         f"{LIConfigKey.gridLotMinQuantity}={self.gridLotMinQuantity}")
        #     return False

        # manualCloseOrder = self.gridTrading.detectManualCloseOrder(self)
        # if manualCloseOrder:
        #     alert(f"{self.getNotifyPrefix()}: Skip submitting close order ticket as detected a manual close order: {orderTicket}")
        #     return False

        if targetPrice <= 0:  # Important!
            return False  # Abort, invalid target price!

        leakingQuantity = self.gridTrading.getLeakingQuantity()
        if self.isLongLot():
            closePrice = marketPrice if useMarketOrder else max(marketPrice, targetPrice)  # Take advantage of market gap
            if not self.gridTrading.tradeBothSides():  # Both sides could have closing orders!
                if leakingQuantity > 0 and self.gridTrading.hasLeakingPositions(leakingQuantity):
                    targetQuantity = -min(self.filledOpenQuantity, leakingQuantity)
        if self.isShortLot():
            closePrice = marketPrice if useMarketOrder else min(marketPrice, targetPrice)  # Take advantage of market gap
            if not self.gridTrading.tradeBothSides():  # Both sides could have closing orders!
                if leakingQuantity < 0 and self.gridTrading.hasLeakingPositions(leakingQuantity):
                    targetQuantity = -max(self.filledOpenQuantity, leakingQuantity)

        targetQuantity = self.positionManager.roundSecuritySize(targetQuantity)

        # Adjust close price according to trade insight if enabled!
        closePositionsNow = False
        if self.gridTrading.gridUseTradeInsight:
            tradeInsight = self.gridTrading.getTradeInsight()
            if not tradeInsight or tradeInsight.isNoneSignal():
                return  # Abort as no signal yet!
            if tradeInsight.isLongSignal():
                if self.isShortLot():
                    closePositionsNow = True
            elif tradeInsight.isShortSignal():
                if self.isLongLot():
                    closePositionsNow = True
            elif tradeInsight.isCloseSignal():
                closePositionsNow = True
            else:
                raise TypeError(f"Not support tradeInsight={tradeInsight}!")
            if closePositionsNow:
                closePrice = marketPrice
                if self.closeWithMarketOrderType:
                    useMarketOrder = True
                log(f"{self.getSymbolAlias()}@{self.getLotName()}: Closing positions now as per tradeInsight={tradeInsight}.", self.verbose)

        tradeType = LITradeType.CLOSING_LIMIT
        if useMarketOrder or self.closeWithMarketOrderType:
            tradeType = LITradeType.CLOSING_LIMIT_MARKET if self.positionManager.enableLimitMarketOrder else LITradeType.CLOSING_MARKET

        stopLossPrice = self.getStopLossPrice()
        maxProfitPrice = self.getMaxProfitPrice()
        stopProfitPrice = self.getStopProfitPrice()
        stopLimitPrices = None  # (stopPrice, limitPrice, stopPriceFactor)
        trailingStopPrices = None  # (stopPrice, trailingAmount, trailingAsPercentage, trailingAmountFactor)
        if self.isLongLot():
            targetPrice += self.accruedLostPoints
            if closePositionsNow:
                pass  # As it is
            elif maxProfitPrice and marketPrice >= maxProfitPrice[0] >= targetPrice:
                stopLimitPrices = (marketPrice, maxProfitPrice[0], maxProfitPrice[1])
                tradeType = LITradeType.CLOSING_MAX_PROFIT
            elif stopProfitPrice and (marketPrice > stopProfitPrice[0] > targetPrice or self.trailingStopProfitPrice):
                self.trailingStopProfitPrice = max(stopProfitPrice[0], self.trailingStopProfitPrice if self.trailingStopProfitPrice else sys.float_info.min)
                stopLimitPrices = (self.trailingStopProfitPrice, self.trailingStopProfitPrice, stopProfitPrice[1])
                tradeType = LITradeType.CLOSING_STOP_PROFIT
            elif not stopProfitPrice and marketPrice > targetPrice:
                self.trailingStopProfitPrice = None
                stopLimitPrices = (marketPrice, marketPrice, 0)
                tradeType = LITradeType.CLOSING_TAKE_PROFIT
            elif stopLossPrice:  # Check stop loss at last!
                self.trailingStopProfitPrice = None
                stopLimitPrices = (stopLossPrice[0], stopLossPrice[0], stopLossPrice[1])
                tradeType = LITradeType.CLOSING_STOP_LOSS
                if self.enableTrailingStopLoss:
                    self.trailingStopLossPrice = max(stopLossPrice[0], self.trailingStopLossPrice if self.trailingStopLossPrice else sys.float_info.min)
                    stopLimitPrices = (self.trailingStopLossPrice, self.trailingStopLossPrice, stopLossPrice[1])
                    tradeType = LITradeType.CLOSING_TRAILING_STOP_LOSS
        if self.isShortLot():
            targetPrice -= self.accruedLostPoints
            if closePositionsNow:
                pass  # As it is
            elif maxProfitPrice and marketPrice <= maxProfitPrice[0] <= targetPrice:
                stopLimitPrices = (marketPrice, maxProfitPrice[0], maxProfitPrice[1])
                tradeType = LITradeType.CLOSING_MAX_PROFIT
            elif stopProfitPrice and (marketPrice < stopProfitPrice[0] < targetPrice or self.trailingStopProfitPrice):
                self.trailingStopProfitPrice = min(stopProfitPrice[0], self.trailingStopProfitPrice if self.trailingStopProfitPrice else sys.float_info.max)
                stopLimitPrices = (self.trailingStopProfitPrice, self.trailingStopProfitPrice, stopProfitPrice[1])
                tradeType = LITradeType.CLOSING_STOP_PROFIT
            elif not stopProfitPrice and marketPrice < targetPrice:
                self.trailingStopProfitPrice = None
                stopLimitPrices = (marketPrice, marketPrice, 0)
                tradeType = LITradeType.CLOSING_TAKE_PROFIT
            elif stopLossPrice:  # Check stop loss at last!
                self.trailingStopProfitPrice = None
                stopLimitPrices = (stopLossPrice[0], stopLossPrice[0], stopLossPrice[1])
                tradeType = LITradeType.CLOSING_STOP_LOSS
                if self.enableTrailingStopLoss:
                    self.trailingStopLossPrice = min(stopLossPrice[0], self.trailingStopLossPrice if self.trailingStopLossPrice else sys.float_info.max)
                    stopLimitPrices = (self.trailingStopLossPrice, self.trailingStopLossPrice, stopLossPrice[1])
                    tradeType = LITradeType.CLOSING_TRAILING_STOP_LOSS
        if stopLimitPrices:
            if self.closeWithStopOrderType:
                softLimitPrice = self.positionManager.softenLimitPrice2(targetQuantity, stopLimitPrices[0])
                stopLimitPrices = (stopLimitPrices[0], softLimitPrice, stopLimitPrices[2])
                if self.submitTrailingStopOrder:
                    stopPriceFactor = stopLimitPrices[2]
                    if self.gridLotLevelAmount:
                        trailingStopPrices = (stopLimitPrices[0],
                                              self.positionManager.roundSecurityPrice(self.getAugmentedAmount() * stopPriceFactor),
                                              False, stopPriceFactor)
                    elif self.gridLotLevelPercent:
                        trailingStopPrices = (stopLimitPrices[0],
                                              round(self.getAugmentedPercent() * stopPriceFactor / 100, LIGlobal.percentPrecision),
                                              True, stopPriceFactor)

        if useMarketOrder:
            if self.closeOrderTicket and self.closeOrderTicket.OrderType in [OrderType.MARKET, OrderType.MARKET_ON_OPEN, OrderType.MARKET_ON_CLOSE]:
                log(f"{self.getSymbolAlias()}@{self.getLotName()}: Waiting for close order to be filled: orderId={self.closeOrderTicket.order_id}, "
                    f"status={getEnumName(self.closeOrderTicket.status, OrderStatus)}; {self.closeOrderTicket.tag}")
                self.lotStatus = LILotStatus.CLOSING
                return True
            elif isOrderTicketUpdatable(self.closeOrderTicket):
                tagLog = f"Cancel {LITradeType.CLOSING} {self.closeOrderTicket.OrderType} order to use {tradeType} order! tag=[{self.closeOrderTicket.Tag}]."
                self.positionManager.cancelOrder(self.closeOrderTicket, tagLog)
            closePriceMsg = f"stopLimitPrices={printStopLimitPrices(stopLimitPrices)}" if stopLimitPrices else f"closePrice={closePrice}"
            tagLog = f"{self.getLotName()}: Submit {tradeType} order at {closePriceMsg}, targetPrice={targetPrice}, " \
                     f"targetQuantity={targetQuantity}, {self.printGridLotPrices()}, marketPrice={marketPrice}, " \
                     f"{self.printOpenPrices()}."
            log(f"{self.getSymbolAlias()}@{tagLog}")
            self.closeOrderTicket = self.positionManager.limitMarketOrder(targetQuantity, tagLog)
            self.lotStatus = LILotStatus.CLOSING
            self.fireOrderEvents(self.closeOrderTicket)
            liveSleep(5)  # A little break
            return True
        elif isOrderTicketUpdatable(self.closeOrderTicket):
            if self.closeOrderTicket.OrderType in [OrderType.MARKET, OrderType.MARKET_ON_OPEN, OrderType.MARKET_ON_CLOSE]:
                return False  # Abort, waiting for market open or order to be filled
            if isStopOrderType(self.closeOrderTicket) and not stopLimitPrices:
                if self.gridLotStopLossFactor and not closePositionsNow:
                    terminate(f"Missing stopLimitPrices for the closeOrderTicket!")
                else:
                    tagLog = f"Cancel {self.closeOrderTicket.OrderType} order to start over! tag=[{self.closeOrderTicket.Tag}]."
                    self.positionManager.cancelOrder(self.closeOrderTicket, tagLog)
                    return False
            closePriceMsg = self.getClosePriceMsg(closePrice, stopLimitPrices, trailingStopPrices)
            tagLog = f"{self.getLotName()}: Update {tradeType} order at {closePriceMsg}, targetPrice={targetPrice}, " \
                     f"targetQuantity={targetQuantity}, {self.printGridLotPrices()}, marketPrice={marketPrice}, " \
                     f"{self.printOpenPrices()}."
            needToUpdate = False
            updateFields = UpdateOrderFields()
            if self.closeOrderTicket.Quantity != targetQuantity:
                updateFields.Quantity = targetQuantity
                needToUpdate = True
            if stopLimitPrices:
                if self.closeOrderTicket.OrderType == OrderType.Limit:
                    if self.closeOrderTicket.Get(OrderField.LimitPrice) != stopLimitPrices[1]:
                        updateFields.LimitPrice = stopLimitPrices[1]
                        needToUpdate = True
                elif self.closeOrderTicket.OrderType == OrderType.StopLimit:
                    if (self.closeOrderTicket.Get(OrderField.StopPrice) != stopLimitPrices[0] or
                            self.closeOrderTicket.Get(OrderField.LimitPrice) != stopLimitPrices[1]):
                        updateFields.StopPrice = stopLimitPrices[0]
                        updateFields.LimitPrice = stopLimitPrices[1]
                        needToUpdate = True
                elif self.closeOrderTicket.OrderType == OrderType.StopMarket:
                    if self.closeOrderTicket.Get(OrderField.StopPrice) != stopLimitPrices[0]:
                        updateFields.StopPrice = stopLimitPrices[0]
                        needToUpdate = True
                elif self.closeOrderTicket.OrderType == OrderType.TrailingStop:
                    if self.updateTrailingStopPrice and self.closeOrderTicket.Get(OrderField.StopPrice) != trailingStopPrices[0]:
                        updateFields.StopPrice = trailingStopPrices[0]
                        needToUpdate = True
                    if self.closeOrderTicket.Get(OrderField.TrailingAmount) != trailingStopPrices[1]:
                        updateFields.TrailingAmount = trailingStopPrices[1]
                        needToUpdate = True
            elif closePrice:
                if self.closeOrderTicket.Get(OrderField.LimitPrice) != closePrice:
                    updateFields.LimitPrice = closePrice
                    needToUpdate = True
            if needToUpdate:
                log(f"{self.getSymbolAlias()}@{tagLog}", self.verbose)
                updateFields.Tag = decorateTag(tagLog)
                orderResponse = self.closeOrderTicket.Update(updateFields)
                if orderResponse and orderResponse.IsError:
                    notify(f"{self.getNotifyPrefix()}: Failed to update close order ticket fields: {orderResponse}, tag=[{self.closeOrderTicket.Tag}].")
                self.lotStatus = LILotStatus.CLOSING
            return needToUpdate
        elif targetQuantity != 0 and self.canSubmitCloseOrder(tradeType):
            closePriceMsg = self.getClosePriceMsg(closePrice, stopLimitPrices, trailingStopPrices)
            tagLog = f"{self.getLotName()}: Submit {tradeType} order at {closePriceMsg}, targetPrice={targetPrice}, " \
                     f"targetQuantity={targetQuantity}, {self.printGridLotPrices()}, marketPrice={marketPrice}, " \
                     f"{self.printOpenPrices()}."
            if stopLimitPrices:
                if self.closeWithStopOrderType:
                    log(f"{self.getSymbolAlias()}@{tagLog}")
                    if self.submitTrailingStopOrder:
                        if self.updateTrailingStopPrice:
                            self.closeOrderTicket = getAlgo().TrailingStopOrder(self.getSymbol(), quantity=targetQuantity, stopPrice=trailingStopPrices[0],
                                                                                trailingAmount=trailingStopPrices[1],
                                                                                trailingAsPercentage=trailingStopPrices[2], tag=decorateTag(tagLog))
                        else:
                            self.closeOrderTicket = getAlgo().TrailingStopOrder(self.getSymbol(), quantity=targetQuantity,
                                                                                trailingAmount=trailingStopPrices[1],
                                                                                trailingAsPercentage=trailingStopPrices[2], tag=decorateTag(tagLog))
                    elif self.submitStopMarketOrder:
                        self.closeOrderTicket = getAlgo().StopMarketOrder(self.getSymbol(), quantity=targetQuantity, stopPrice=stopLimitPrices[0],
                                                                          tag=decorateTag(tagLog))
                    else:
                        self.closeOrderTicket = getAlgo().StopLimitOrder(self.getSymbol(), quantity=targetQuantity, stopPrice=stopLimitPrices[0],
                                                                         limitPrice=stopLimitPrices[1],
                                                                         tag=decorateTag(tagLog))
                    self.lotStatus = LILotStatus.CLOSING
                    return True
                elif maxProfitPrice and (
                        (self.isLongLot() and maxProfitPrice[0] < marketPrice) or (self.isShortLot() and maxProfitPrice[0] > marketPrice)):
                    log(f"{self.getSymbolAlias()}@{tagLog}")
                    # self.closeOrderTicket = self.positionManager.limitOrder(targetQuantity, softLimitPrice, tagLog)
                    # TEST: It performs better with limit market order than stop limit order at this point!
                    if self.closeWithMarketOrderType:
                        self.closeOrderTicket = self.positionManager.limitMarketOrder(targetQuantity, tagLog)
                        self.fireOrderEvents(self.closeOrderTicket)
                    else:
                        self.closeOrderTicket = getAlgo().LimitOrder(self.getSymbol(), targetQuantity, marketPrice, tag=decorateTag(tagLog))
                    self.lotStatus = LILotStatus.CLOSING
                    return True
                elif (self.isLongLot() and stopLimitPrices[0] > marketPrice) or (self.isShortLot() and stopLimitPrices[0] < marketPrice):
                    log(f"{self.getSymbolAlias()}@{tagLog}")
                    # self.closeOrderTicket = self.positionManager.limitOrder(targetQuantity, softLimitPrice, tagLog)
                    # TEST: It performs better with limit market order than stop limit order at this point!
                    if self.closeWithMarketOrderType:
                        self.closeOrderTicket = self.positionManager.limitMarketOrder(targetQuantity, tagLog)
                        self.fireOrderEvents(self.closeOrderTicket)
                    else:
                        self.closeOrderTicket = getAlgo().LimitOrder(self.getSymbol(), targetQuantity, marketPrice, tag=decorateTag(tagLog))
                    self.lotStatus = LILotStatus.CLOSING
                    return True
                else:
                    self.markClosingLotStatus(stopLimitPrices, closePrice, targetQuantity)
                    return False
            elif stopProfitPrice:
                self.markClosingLotStatus(stopLimitPrices, closePrice, targetQuantity)
                return False
            else:
                log(f"{self.getSymbolAlias()}@{tagLog}")
                self.closeOrderTicket = getAlgo().LimitOrder(self.getSymbol(), targetQuantity, closePrice, tag=decorateTag(tagLog))
                self.lotStatus = LILotStatus.CLOSING
                return True
        elif targetQuantity != 0:
            self.markClosingLotStatus(stopLimitPrices, closePrice, targetQuantity)
            return False

        if self.isBoostingLot():
            closingPrice = self.getClosingPrice()
            if self.isLongLot() and closingPrice < self.filledOpenPrice:
                alert(f"{self.getNotifyPrefix()}@{self.getLotName()}: The closingPrice={closingPrice} should be greater than openPrice={self.filledOpenPrice}.")
            if self.isShortLot() and closingPrice > self.filledOpenPrice:
                alert(f"{self.getNotifyPrefix()}@{self.getLotName()}: The closingPrice={closingPrice} should be less than openPrice={self.filledOpenPrice}")

        # Verify close order ticket status, skip it as an invalid order is still updatable!
        # if self.closeOrderTicket and self.closeOrderTicket.Status == OrderStatus.Invalid:
        #     self.closeOrderTicket = None  # Abort as invalid, catch error within onOrderEvent()
        #     return False

    def getClosePriceMsg(self, closePrice, stopLimitPrices, trailingStopPrices):
        if trailingStopPrices:
            closePriceMsg = f"trailingStopPrices={printTrailingStopPrices(trailingStopPrices, self.updateTrailingStopPrice)}"
        elif stopLimitPrices:
            closePriceMsg = f"stopLimitPrices={printStopLimitPrices(stopLimitPrices)}"
        else:
            closePriceMsg = f"closePrice={closePrice}"
        return closePriceMsg

    def resetTradingLot(self, reason=None):
        self.cancelOpenOrderTicket(f"Cancel {LITradeType.OPENING} order upon resetting trading lot: {reason}.")
        self.cancelCloseOrderTicket(f"Cancel {LITradeType.CLOSING} order upon resetting trading lot: {reason}.")

        self.resetOpeningProps()
        self.openOrderTicket = None
        self.openOrderTransferId = None
        self.createdOpenOrderTime = None

        self.stopOrderPrice = 0
        self.trailingAmount = 0
        self.closeOrderPrice = 0
        self.closeOrderQuantity = 0
        self.closeOrderTicket = None
        self.closeOrderTransferId = None
        self.trailingStopLossPrice = None
        self.trailingStopProfitPrice = None

        self.accruedFees = 0.0
        self.lotStatus = LILotStatus.IDLING

    def restartTradingLot(self, reason=None):
        self.pausedOpening = False
        self.accruedLostPoints = 0
        self.closedTradesCount = 0
        self.realizedProfitLoss = 0.0
        self.resetTradingLot(reason)

    def resetOpeningProps(self, preserveOpenPrice=False):
        if preserveOpenPrice:
            if not self.actualOpenPrice:
                self.actualOpenPrice = self.filledOpenPrice
        else:
            self.actualOpenPrice = 0
        self.filledOpenPrice = 0
        self.filledOpenQuantity = 0
        self.trailingOpenPrice = 0

    def fireOrderEvents(self, orderTicket: OrderTicket):
        # NOTE: this fire order events could cause "maximum recursion depth exceeded" for option trading
        # Only need to fire order evens for market order in backtest mode!!!
        # if orderTicket.OrderType == OrderType.Market:
        for orderEvent in orderTicket.OrderEvents:
            self.onOrderEvent(orderEvent)
            orderEvent.OrderId *= -1  # Avoid repeating order event

    def markClosingLotStatus(self, stopLimitPrices, closePrice, closeQuantity):
        if stopLimitPrices:
            self.stopOrderPrice = stopLimitPrices[0]
            self.closeOrderPrice = stopLimitPrices[1]
        else:
            self.closeOrderPrice = closePrice
        self.closeOrderQuantity = closeQuantity
        self.lotStatus = LILotStatus.CLOSING

    def cancelOpenOrderTicket(self, tagLog=None):
        if isOrderTicketUpdatable(self.openOrderTicket):
            tagLog = f"{self.getLotName()}: {tagLog if tagLog else f'Cancel {LITradeType.OPENING} order upon resetting trading lot.'}"
            self.positionManager.cancelOrder(self.openOrderTicket, tagLog)
            log(f"{self.getSymbolAlias()}@{tagLog}")
            return True
        self.openOrderTicket = None

    def cancelCloseOrderTicket(self, tagLog=None):
        if isOrderTicketUpdatable(self.closeOrderTicket):
            tagLog = f"{self.getLotName()}: {tagLog if tagLog else f'Cancel {LITradeType.CLOSING} order upon resetting trading lot.'}"
            self.positionManager.cancelOrder(self.closeOrderTicket, tagLog)
            log(f"{self.getSymbolAlias()}@{tagLog}")
            return True
        self.closeOrderTicket = None

    def isLastOpeningLot(self):
        return ((self.isLongLot() and (self.prevLot.isStartLot() or self.prevLot.pausedOpening or self.prevLot.hasOpenPosition())) or
                (self.isShortLot() and (self.nextLot.isStartLot() or self.nextLot.pausedOpening or self.nextLot.hasOpenPosition())))

    # Maintain 1 active/open order ticket at a time!
    def canSubmitOpenOrder1(self):
        return False or (
                (self.isLongLot() and (
                        self.prevLot.isStartLot() or
                        self.prevLot.pausedOpening or
                        (self.prevLot.hasOpenPosition() and self.gridTrading.countOpenOrders(peerLot=self) < 1))) or
                (self.isShortLot() and (
                        self.nextLot.isStartLot() or
                        self.nextLot.pausedOpening or
                        (self.nextLot.hasOpenPosition() and self.gridTrading.countOpenOrders(peerLot=self) < 1))))

    # Maintain 2 active/open order tickets at a time!
    def canSubmitOpenOrder2(self):
        return self.canSubmitOpenOrder1() or (
                (self.isLongLot() and (
                        self.prevLot.prevLot.isStartLot() or
                        self.prevLot.prevLot.pausedOpening or
                        (self.prevLot.prevLot.hasOpenPosition() and self.gridTrading.countOpenOrders(peerLot=self) < 2))) or
                (self.isShortLot() and (
                        self.nextLot.nextLot.isStartLot() or
                        self.nextLot.nextLot.pausedOpening or
                        (self.nextLot.nextLot.hasOpenPosition() and self.gridTrading.countOpenOrders(peerLot=self) < 2))))

    # Maintain 3 active/open order tickets at a time!
    def canSubmitOpenOrder3(self):
        return self.canSubmitOpenOrder2() or (
                (self.isLongLot() and (
                        self.prevLot.prevLot.prevLot.isStartLot() or
                        self.prevLot.prevLot.prevLot.pausedOpening or
                        (self.prevLot.prevLot.prevLot.hasOpenPosition() and self.gridTrading.countOpenOrders(peerLot=self) < 3))) or
                (self.isShortLot() and (
                        self.nextLot.nextLot.nextLot.isStartLot() or
                        self.nextLot.nextLot.nextLot.pausedOpening or
                        (self.nextLot.nextLot.nextLot.hasOpenPosition() and self.gridTrading.countOpenOrders(peerLot=self) < 3))))

    def canSubmitCloseOrder(self, tradeType):
        # if not self.closeWithStopOrderType:
        #     return True # No need to check!
        if self.isBoostingLot():
            return True  # Make sure boosting lot always been protected by stop loss order!
        if self.isLongLot():
            # Check possible close orders from the first long lot first
            closingOrders = 0
            lot = self.gridTrading.getFirstLongLot()
            while lot and lot.isLongLot() and closingOrders < self.gridTrading.gridKeepStartCloseOrders:
                if lot.isNotRetainedLot():
                    if self == lot and (tradeType == LITradeType.CLOSING_STOP_LOSS if self.isContrarianMode() else True):
                        return True
                    if lot.hasClosePosition() or lot.hasCloseOrderTicket():
                        closingOrders += 1
                lot = lot.nextLot
            # Check possible close orders from the last long lot for the rest
            restCloseOrders = self.gridTrading.gridMaintainCloseOrders - closingOrders
            lot = self.gridTrading.getLastLongLot()
            while lot and lot.isLongLot() and restCloseOrders > 0:
                if lot.isNotRetainedLot():
                    if self == lot:
                        return True
                    if lot.hasClosePosition() or lot.hasCloseOrderTicket():
                        restCloseOrders -= 1
                lot = lot.prevLot
        if self.isShortLot():
            # Check possible close orders from the first short lot first
            closingOrders = 0
            lot = self.gridTrading.getFirstShortLot()
            while lot and lot.isShortLot() and closingOrders < self.gridTrading.gridKeepStartCloseOrders:
                if lot.isNotRetainedLot():
                    if self == lot and (tradeType == LITradeType.CLOSING_STOP_LOSS if self.isContrarianMode() else True):
                        return True
                    if lot.hasClosePosition() or lot.hasCloseOrderTicket():
                        closingOrders += 1
                lot = lot.prevLot
            # Check possible close orders from the last long lot for the rest
            restCloseOrders = self.gridTrading.gridMaintainCloseOrders - closingOrders
            lot = self.gridTrading.getLastShortLot()
            while lot and lot.isShortLot() and restCloseOrders > 0:
                if lot.isNotRetainedLot():
                    if self == lot:
                        return True
                    if lot.hasClosePosition() or lot.hasCloseOrderTicket():
                        restCloseOrders -= 1
                lot = lot.nextLot
        return False

    def onOrderEvent(self, orderEvent: OrderEvent):
        delayMaxMsgs = 0 if self.isMomentumMode() else 0
        if (self.openOrderTicket and self.openOrderTicket.OrderId == orderEvent.OrderId) or (
                self.openOrderTransferId and self.openOrderTransferId == orderEvent.OrderId):
            if orderEvent.Status == OrderStatus.Submitted:
                self.lotStatus = LILotStatus.OPENING
                return True
            elif orderEvent.Status == OrderStatus.Canceled or orderEvent.Status == OrderStatus.Invalid:
                self.lotStatus = LILotStatus.HOLDING if self.hasOpenPosition() else LILotStatus.IDLING
                self.openOrderTicket = None
                return True
            elif orderEvent.Status == OrderStatus.PartiallyFilled:
                self.lotStatus = LILotStatus.HOLDING
                self.accruedFees += orderEvent.OrderFee.Value.Amount
                return True
            elif orderEvent.Status == OrderStatus.Filled:
                self.lotStatus = LILotStatus.HOLDING
                '''Can get info from either order event or order ticket'''
                ticketTag = self.openOrderTicket.Tag if self.openOrderTicket else LITradeType.TRANSFER
                filledPrice = self.openOrderTicket.AverageFillPrice if self.openOrderTicket else orderEvent.FillPrice
                filledQuantity = self.openOrderTicket.QuantityFilled if self.openOrderTicket else orderEvent.FillQuantity
                self.filledOpenPrice = ((filledPrice * filledQuantity + self.filledOpenPrice * self.filledOpenQuantity) /
                                        (filledQuantity + self.filledOpenQuantity))
                self.filledOpenPrice = self.positionManager.roundSecurityPrice(self.filledOpenPrice)
                self.filledOpenQuantity += filledQuantity
                self.actualOpenPrice = 0  # Clear it!
                self.accruedFees += orderEvent.OrderFee.Value.Amount
                self.createdOpenOrderTime = self.openOrderTicket.Time if self.openOrderTicket else orderEvent.UtcTime
                orderEvent.FillPrice = filledPrice  # Overwrite with average filled price
                orderEvent.FillQuantity = filledQuantity  # Overwrite with actual filled quantity
                orderEvent.Quantity = filledQuantity  # Overwrite with actual fill quantity
                orderEvent.OrderFee.Value = CashAmount(self.accruedFees, orderEvent.OrderFee.Value.Currency)  # Overwrite with all open orders' fees
                if self.isBuyAndHoldMode():
                    self.gridTrading.dcaLastInvestedDate = getAlgo().Time
                # log(f"{self.getSymbolAlias()}: Notify open order {self.openOrderTicket} filled event: {orderEvent}.")
                additionalMsgs = f"totalProfitLoss={self.gridTrading.getMaxProfitLossAmount()}({self.gridTrading.getMaxProfitLossPercent()}%)"
                if self.isBoostingLot():
                    # self.trailingStopLossPrice = None # Refresh as the average filled open price been changed
                    # self.trailingStopProfitPrice = None # Refresh as the average filled open price been changed
                    additionalMsgs += f", profitLossFactor={self.getProfitLossFactor()}"
                self.positionManager.notifyOrderFilled(orderEvent, netProfit=0, additionalMsgs=additionalMsgs, delayMaxMsgs=delayMaxMsgs)
                if self.gridTrading.tradeBothSides():
                    if self.isMomentumMode() and self.gridTrading.gridTransfer2Counterpart:
                        investedQuantity = self.gridTrading.getInvestedQuantity()
                        counterpartLot = self.gridTrading.getFirstOpenedCounterpartLot(self)
                        if counterpartLot and counterpartLot.filledOpenQuantity == filledQuantity:
                            orderEvent.OrderId = orderEvent.OrderId * 100  # Set a new unique order id
                            orderEvent.OrderFee.Value = CashAmount(0.0, orderEvent.OrderFee.Value.Currency)  # Already count in
                            orderEvent.Message = orderEvent.Message if orderEvent.Message else f"Transfer from {self.getLotName()}."
                            counterpartLot.closeOrderTransferId = orderEvent.OrderId
                            log(f"{self.getSymbolAlias()}@{self.getLotName()}: Transfer to reset the counterpart {counterpartLot.getLotName()} "
                                f"as counterpartLotFilledOpenQuantity={counterpartLot.filledOpenQuantity}, filledOpenQuantity={self.filledOpenQuantity}, "
                                f"investedQuantity={investedQuantity}, filledLots={self.gridTrading.countFilledLots()}.")
                            counterpartLot.onOrderEvent(orderEvent)  # Trigger to close this counterpart lot!
                    elif self.isContrarianMode() and self.gridTrading.gridCloseCounterpartLots:
                        investedQuantity = self.gridTrading.getInvestedQuantity()
                        counterpartLot = self.gridTrading.getFirstOpenedCounterpartLot(self)
                        while counterpartLot:
                            log(f"{self.getSymbolAlias()}@{self.getLotName()}: Force to close the counterpart {counterpartLot.getLotName()} first "
                                f"as counterpartLotFilledOpenQuantity={counterpartLot.filledOpenQuantity}, filledOpenQuantity={self.filledOpenQuantity}, "
                                f"investedQuantity={investedQuantity}, filledLots={self.gridTrading.countFilledLots()}.")
                            counterpartLot.manageLotCloseOrderTicket(useMarketOrder=True)
                            counterpartLot = self.gridTrading.getFirstOpenedCounterpartLot(self)
                if self.gridTrading.gridUseTradeInsight:
                    if self.isFirstLongLot():
                        self.gridTrading.manageGridStartPrices(retainOpenedLots=1, filledMarketPrice=self.filledOpenPrice, overwriteStartPrices=True)
                    if self.isFirstShortLot():
                        self.gridTrading.manageGridStartPrices(retainOpenedLots=-1, filledMarketPrice=self.filledOpenPrice, overwriteStartPrices=True)
                self.gridTrading.manageGridTrading(forceTrade=True)  # Trigger all related actions
                return True
        elif (self.closeOrderTicket and self.closeOrderTicket.OrderId == orderEvent.OrderId) or (
                self.closeOrderTransferId and self.closeOrderTransferId == orderEvent.OrderId):
            if orderEvent.Status == OrderStatus.Submitted:
                self.lotStatus = LILotStatus.CLOSING
                return True
            elif orderEvent.Status == OrderStatus.Canceled or orderEvent.Status == OrderStatus.Invalid:
                self.lotStatus = LILotStatus.HOLDING if self.hasOpenPosition() else LILotStatus.IDLING
                self.closeOrderTicket = None
                return True
            elif orderEvent.Status == OrderStatus.PartiallyFilled:
                self.lotStatus = LILotStatus.CLOSING
                self.accruedFees += orderEvent.OrderFee.Value.Amount
                return True
            elif orderEvent.Status == OrderStatus.Filled:
                self.lotStatus = LILotStatus.IDLING
                if self.closeOrderTransferId and self.closeOrderTransferId == orderEvent.OrderId:
                    self.cancelCloseOrderTicket(tagLog=f"Cancel close order upon {LITradeType.TRANSFER} a lot.")
                ticketTag = self.closeOrderTicket.Tag if self.closeOrderTicket else LITradeType.TRANSFER
                filledPrice = self.closeOrderTicket.AverageFillPrice if self.closeOrderTicket else orderEvent.FillPrice
                filledQuantity = self.closeOrderTicket.QuantityFilled if self.closeOrderTicket else orderEvent.FillQuantity
                profitLossPoints = self.getProfitLossPoints(filledPrice) if filledPrice else 0
                profitLoss = round(profitLossPoints * abs(filledQuantity) * self.getSecurityMultiplier(), 2)
                self.accruedFees += orderEvent.OrderFee.Value.Amount
                # Add up the lost points and reset it when profit points can cover the lost points at last!
                self.accruedLostPoints = 0 if profitLossPoints >= self.accruedLostPoints else self.accruedLostPoints + abs(min(profitLossPoints, 0))
                quantity = abs(filledQuantity)
                capital = round(quantity * getMaintenanceMargin(self.getSymbol(), filledPrice), 2)
                duration = 0
                if self.createdOpenOrderTime:
                    closedOrderTime = self.closeOrderTicket.Time if self.closeOrderTicket else orderEvent.UtcTime
                    duration = (closedOrderTime - self.createdOpenOrderTime).total_seconds()
                netProfit = round(profitLoss - self.accruedFees, 2)  # Use local calculated value
                orderEvent.FillPrice = filledPrice  # Overwrite with average fill price
                orderEvent.FillQuantity = filledQuantity  # Overwrite with actual fill quantity
                orderEvent.Quantity = filledQuantity  # Overwrite with actual fill quantity
                orderEvent.OrderFee.Value = CashAmount(self.accruedFees / 2, orderEvent.OrderFee.Value.Currency)  # Overwrite with all close orders' fees
                self.addRealizedProfitLoss(netProfit)
                additionalMsgs = (f"openPrice={self.getFinalOpenPrice()}, filledPrice={filledPrice}, "
                                  f"totalProfitLoss={self.gridTrading.getMaxProfitLossAmount()}({self.gridTrading.getMaxProfitLossPercent()}%)")
                self.positionManager.notifyOrderFilled(orderEvent, netProfit=netProfit, additionalMsgs=additionalMsgs, delayMaxMsgs=delayMaxMsgs)
                addDailyClosedTrade(self.canonicalSymbol.value, [profitLoss, self.accruedFees, capital, quantity, duration])
                if self.gridLotPauseAfterProfit and profitLossPoints > 0:
                    self.pausedOpening = True
                    notify(f"{self.getNotifyPrefix()}@{self.getLotName()}: Paused this lot's trading after took profit: {self.printOpenPrices()}, "
                           f"closePrice={filledPrice}, profitLossPoints={profitLossPoints}, netProfit={netProfit}, accruedLostPoints={self.accruedLostPoints}.")
                elif (self.gridLotPauseAfterStopLoss and profitLossPoints < 0 and
                      (LITradeType.CLOSING_STOP_LOSS in ticketTag or LITradeType.CLOSING_TRAILING_STOP_LOSS in ticketTag)):
                    self.pausedOpening = True
                    notify(f"{self.getNotifyPrefix()}@{self.getLotName()}: Paused this lot's trading after stopped loss: {self.printOpenPrices()}, "
                           f"closePrice={filledPrice}, profitLossPoints={profitLossPoints}, netProfit={netProfit}, accruedLostPoints={self.accruedLostPoints}.")
                if self.isPausedOpening() and self.verbose:
                    self.gridTrading.printGridSession()
                self.resetTradingLot(reason=f"Filled close order: {ticketTag}.")
                # self.gridTrading.resetGridStartPrices(emptyStartPrices=True)  # less drawdown, but less profit!
                if self.gridCancelOrdersAfterClosed:
                    self.gridTrading.cancelOpenOrders(peerLot=self, tagLog=f"Closed {self.getLotName()}, need to resubmit open orders.")
                self.gridTrading.manageGridTrading(forceTrade=True)  # Trigger all related actions
                return True

    def __str__(self) -> str:
        result = f"{self.getLotName()}, lotStatus={self.lotStatus}"
        if self.isPausedOpening():
            result += f", pausedOpening={self.pausedOpening}"
        if self.accruedLostPoints:
            result += f", accruedLostPoints={self.accruedLostPoints}"
        result += ": "
        if self.hasOpenPosition():
            result += f"\n\topenPosition=[filledQuantity={self.filledOpenQuantity}, {self.printOpenPrices()}]"
        if self.openOrderTicket:
            result += f"\n\topenOrderTicket={self.printOrderTicket(self.openOrderTicket)}"
        if self.hasClosePosition():
            result += (f"\n\tclosePosition=[stopPrice={self.stopOrderPrice}, trailingAmount={self.trailingAmount}, "
                       f"closePrice={self.closeOrderPrice}, closeQuantity={self.closeOrderQuantity}]")
        if self.closeOrderTicket:
            result += f"\n\tcloseOrderTicket={self.printOrderTicket(self.closeOrderTicket)}"
        return result.rstrip(': ')

    def printOpenPrices(self):
        return f"openPrice={self.filledOpenPrice}{f', actualOpenPrice={self.actualOpenPrice}' if self.actualOpenPrice else ''}"

    def printTicketPrice(self, orderTicket: OrderTicket):
        priceType = None
        orderPrice = None
        if orderTicket.OrderType == OrderType.StopLimit:
            priceType = "stopLimitPrice"
            orderPrice = f"{orderTicket.Get(OrderField.StopPrice)}/{orderTicket.Get(OrderField.LimitPrice)}"
        elif orderTicket.OrderType == OrderType.TrailingStop:
            priceType = "trailingStopPrice"
            orderPrice = f"{orderTicket.Get(OrderField.StopPrice)}/{orderTicket.Get(OrderField.TrailingAmount)}"
        elif orderTicket.OrderType == OrderType.StopMarket:
            priceType = "stopMarketPrice"
            orderPrice = f"{orderTicket.Get(OrderField.StopPrice)}"
        elif orderTicket.OrderType == OrderType.Limit:
            priceType = "limitPrice"
            orderPrice = f"{orderTicket.Get(OrderField.LimitPrice)}"
        elif orderTicket.OrderType == OrderType.Market:
            priceType = "marketPrice"
            orderPrice = f"{self.positionManager.getMarketPrice()}"
        return f"{priceType}={orderPrice}, " if priceType else ""

    def printOrderTicket(self, ticket: OrderTicket):
        if ticket is None:
            return "None"
        return f"[orderId={ticket.OrderId}, status={getEnumName(ticket.Status, OrderStatus)}, " \
               f"filledPrice={self.positionManager.roundSecurityPrice(ticket.AverageFillPrice)}, " \
               f"filledQuantity={self.positionManager.roundSecuritySize(ticket.QuantityFilled)}, {self.printTicketPrice(ticket)}" \
               f"updatedTime={ticket.Time.strftime(LIGlobal.minuteFormat)}, tag=[{ticket.Tag}]."

    def printGridLotPrices(self):
        result = f"startPrice={self.getStartPrice()}"
        if self.getOpenFromPrice():
            result += f", openFromPrice={self.getOpenFromPrice()}"
        if self.getBoundaryPrice():
            result += f", boundaryPrice={self.getBoundaryPrice()}"
        if self.gridTrading.bollingerBandsIndicator:
            result += f", bollingerBandPrices={self.gridTrading.bollingerBandsIndicator.getBandPrices()}"
        return result

    def restoreLotMetadata(self, postRollover=False):
        self.pausedOpening = self.getLotMetadata(LIMetadataKey.pausedOpening, False)
        self.filledOpenPrice = self.getLotMetadata(LIMetadataKey.filledOpenPrice, 0.0)
        self.filledOpenQuantity = self.getLotMetadata(LIMetadataKey.filledOpenQuantity, 0)
        self.actualOpenPrice = self.getLotMetadata(LIMetadataKey.actualOpenPrice, 0)
        self.accruedLostPoints = self.getLotMetadata(LIMetadataKey.accruedLostPoints, 0)
        self.closedTradesCount = self.getLotMetadata(LIMetadataKey.closedTradesCount, 0)
        self.realizedProfitLoss = self.getLotMetadata(LIMetadataKey.realizedProfitLoss, 0.0)
        if self.gridTrailingOpenPriceFactor:
            self.trailingOpenPrice = self.getLotMetadata(LIMetadataKey.trailingOpenPrice, 0.0)
        if self.enableTrailingStopLoss:
            self.trailingStopLossPrice = self.getLotMetadata(LIMetadataKey.trailingStopLossPrice, None)
        if self.gridLotStopProfitFactors:
            self.trailingStopProfitPrice = self.getLotMetadata(LIMetadataKey.trailingStopProfitPrice, None)
        if self.hasOpenPosition():
            self.lotStatus = LILotStatus.HOLDING

    def refreshLotMetadata(self):
        self.putLotMetadata(LIMetadataKey.pausedOpening, self.pausedOpening)
        self.putLotMetadata(LIMetadataKey.filledOpenPrice, self.filledOpenPrice)
        self.putLotMetadata(LIMetadataKey.filledOpenQuantity, self.filledOpenQuantity)
        self.putLotMetadata(LIMetadataKey.actualOpenPrice, self.actualOpenPrice)
        self.putLotMetadata(LIMetadataKey.accruedLostPoints, self.accruedLostPoints)
        self.putLotMetadata(LIMetadataKey.closedTradesCount, self.closedTradesCount)
        self.putLotMetadata(LIMetadataKey.realizedProfitLoss, self.realizedProfitLoss)
        if self.gridTrailingOpenPriceFactor:
            self.putLotMetadata(LIMetadataKey.trailingOpenPrice, self.trailingOpenPrice)
        if self.enableTrailingStopLoss:
            self.putLotMetadata(LIMetadataKey.trailingStopLossPrice, self.trailingStopLossPrice)
        if self.gridLotStopProfitFactors:
            self.putLotMetadata(LIMetadataKey.trailingStopProfitPrice, self.trailingStopProfitPrice)
