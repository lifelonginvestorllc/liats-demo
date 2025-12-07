from AlgorithmImports import *
from core.LITrading import *
from core.LIGridTradingLot import *
from indicator.LIComboTrendingIndicator import *
from indicator.LIBollingerBandsIndicator import *

import copy

"""
LIGridBase helps to prevent LIGridTrading growing too big and exceeding the maximum size of 128,000 characters.
"""


def arePeerLots(lotX: LITradingLot, lotY: LITradingLot):
    return lotX.lotId * lotY.lotId > 0


def areLotsInOrder(lotX: LIGridTradingLot, lotY: LIGridTradingLot):
    if lotX.isPausedLot():
        return True
    if lotX.isLongLot() and lotY.isLongLot():
        if lotY.hasOpenPosition():
            if lotX.isMomentumMode():
                return not lotX.isVacantLot() and lotX.filledOpenPrice <= lotY.filledOpenPrice
            if lotX.isContrarianMode():
                return not lotX.isVacantLot() and lotX.filledOpenPrice >= lotY.filledOpenPrice
    if lotX.isShortLot() and lotY.isShortLot():
        if lotY.hasOpenPosition():
            if lotX.isMomentumMode():
                return not lotX.isVacantLot() and lotX.filledOpenPrice >= lotY.filledOpenPrice
            if lotX.isContrarianMode():
                return not lotX.isVacantLot() and lotX.filledOpenPrice <= lotY.filledOpenPrice
    return True


def swapGridLots(lotX: LIGridTradingLot, lotY: LIGridTradingLot):
    """
    Swap the lots by making the previous adjacent pointer of X to be previous adjacent pointer of Y and next adjacent pointer of X
    to be next adjacent pointer of Y and vice versa.
    """
    temp = lotX.nextLot
    lotX.nextLot = lotY.nextLot
    lotY.nextLot = temp

    if lotX.nextLot:
        lotX.nextLot.prevLot = lotX
    if lotY.nextLot:
        lotY.nextLot.prevLot = lotY

    temp = lotX.prevLot
    lotX.prevLot = lotY.prevLot
    lotY.prevLot = temp

    if lotX.prevLot:
        lotX.prevLot.nextLot = lotX
    if lotY.prevLot:
        lotY.prevLot.nextLot = lotY

    temp = lotX.lotId
    lotX.lotId = lotY.lotId
    lotY.lotId = temp


class LIGridBase(LITrading):
    def __init__(self, symbolStr, securityType, investAmount, gridMode, **configs):
        super().__init__(symbolStr, securityType, investAmount, LIStrategyCode.GRID, **configs)

        self.gridMode: LIGridMode = gridMode
        self.gridInitMode: LIGridMode = gridMode
        self.gridLongLots = configs.get(LIConfigKey.gridLongLots, LIDefault.gridLongLots)
        self.gridShortLots = configs.get(LIConfigKey.gridShortLots, LIDefault.gridShortLots)
        self.gridLongLotsQty = configs.get(LIConfigKey.gridLongLotsQty, LIDefault.gridLongLotsQty)
        self.gridShortLotsQty = configs.get(LIConfigKey.gridShortLotsQty, LIDefault.gridShortLotsQty)
        self.gridSortSkewedLots = configs.get(LIConfigKey.gridSortSkewedLots, LIDefault.gridSortSkewedLots)
        self.gridHeikinAshiPlies = configs.get(LIConfigKey.gridHeikinAshiPlies, LIDefault.gridHeikinAshiPlies)
        self.gridLimitStartPrices = configs.get(LIConfigKey.gridLimitStartPrices, LIDefault.gridLimitStartPrices)
        self.gridResetStartPrices = configs.get(LIConfigKey.gridResetStartPrices, LIDefault.gridResetStartPrices)
        self.gridFixedStartPrices = configs.get(LIConfigKey.gridFixedStartPrices, LIDefault.gridFixedStartPrices)
        self.gridSignalStartPrices = configs.get(LIConfigKey.gridSignalStartPrices, LIDefault.gridSignalStartPrices)
        self.gridFixedOpenFromPrices = configs.get(LIConfigKey.gridFixedOpenFromPrices, LIDefault.gridFixedOpenFromPrices)
        self.gridResetLotsMetadata = configs.get(LIConfigKey.gridResetLotsMetadata, LIDefault.gridResetLotsMetadata)
        self.gridRolloverCriteria = configs.get(LIConfigKey.gridRolloverCriteria, LIDefault.gridRolloverCriteria)
        self.gridInitializeSession = configs.get(LIConfigKey.gridInitializeSession, LIDefault.gridInitializeSession)

        self.gridBandingStartPrices = configs.get(LIConfigKey.gridBandingStartPrices, LIDefault.gridBandingStartPrices)
        self.gridBandingOpenFromPrices = configs.get(LIConfigKey.gridBandingOpenFromPrices, LIDefault.gridBandingOpenFromPrices)
        self.gridBandingLimitStartPrices = configs.get(LIConfigKey.gridBandingLimitStartPrices, LIDefault.gridBandingLimitStartPrices)

        self.gridLotMinQuantity = configs.get(LIConfigKey.gridLotMinQuantity, LIDefault.gridLotMinQuantity)
        self.gridLotLevelAmount = configs.get(LIConfigKey.gridLotLevelAmount, LIDefault.gridLotLevelAmount)
        self.gridLotLevelPercent = configs.get(LIConfigKey.gridLotLevelPercent, LIDefault.gridLotLevelPercent)
        self.gridLotLevelAugment = configs.get(LIConfigKey.gridLotLevelAugment, LIDefault.gridLotLevelAugment)
        self.gridLotStopLossFactor = configs.get(LIConfigKey.gridLotStopLossFactor, LIDefault.gridLotStopLossFactor)

        self.gridInitOpenedLots = configs.get(LIConfigKey.gridInitOpenedLots, LIDefault.gridInitOpenedLots)
        self.gridRetainOpenedLots = configs.get(LIConfigKey.gridRetainOpenedLots, LIDefault.gridRetainOpenedLots)
        self.gridNoMoreOpenOrders = configs.get(LIConfigKey.gridNoMoreOpenOrders, LIDefault.gridNoMoreOpenOrders)
        self.gridNoMoreCloseOrders = configs.get(LIConfigKey.gridNoMoreCloseOrders, LIDefault.gridNoMoreCloseOrders)
        self.gridMaintainOpenOrders = configs.get(LIConfigKey.gridMaintainOpenOrders, LIDefault.gridMaintainOpenOrders)
        self.gridKeepOpenOrdersApart = configs.get(LIConfigKey.gridKeepOpenOrdersApart, LIDefault.gridKeepOpenOrdersApart)
        self.gridMaintainCloseOrders = configs.get(LIConfigKey.gridMaintainCloseOrders, LIDefault.gridMaintainCloseOrders)
        self.gridKeepStartCloseOrders = configs.get(LIConfigKey.gridKeepStartCloseOrders, LIDefault.gridKeepStartCloseOrders)
        self.gridFollowAdverseTrend = configs.get(LIConfigKey.gridFollowAdverseTrend, LIDefault.gridFollowAdverseTrend)
        self.gridStickToMarketTrend = configs.get(LIConfigKey.gridStickToMarketTrend, LIDefault.gridStickToMarketTrend)
        self.gridCancelOrdersOnExit = configs.get(LIConfigKey.gridCancelOrdersOnExit, LIDefault.gridCancelOrdersOnExit)
        self.gridNotifyTargetPrices = configs.get(LIConfigKey.gridNotifyTargetPrices, LIDefault.gridNotifyTargetPrices)
        self.gridMonitorPeriodFactors = configs.get(LIConfigKey.gridMonitorPeriodFactors, LIDefault.gridMonitorPeriodFactors)
        self.gridTransfer2Counterpart = configs.get(LIConfigKey.gridTransfer2Counterpart, LIDefault.gridTransfer2Counterpart)
        self.gridCloseCounterpartLots = configs.get(LIConfigKey.gridCloseCounterpartLots, LIDefault.gridCloseCounterpartLots)
        self.gridFixLeakingPositions = configs.get(LIConfigKey.gridFixLeakingPositions, LIDefault.gridFixLeakingPositions)
        self.gridRealignOpenPositions = configs.get(LIConfigKey.gridRealignOpenPositions, LIDefault.gridRealignOpenPositions)
        self.gridRealignForMaxHolding = configs.get(LIConfigKey.gridRealignForMaxHolding, LIDefault.gridRealignForMaxHolding)
        self.gridRestartOnFridayClose = configs.get(LIConfigKey.gridRestartOnFridayClose, LIDefault.gridRestartOnFridayClose)
        self.gridRestartIfAllLotsPaused = configs.get(LIConfigKey.gridRestartIfAllLotsPaused, LIDefault.gridRestartIfAllLotsPaused)

        self.gridBoostingKeepTrading = configs.get(LIConfigKey.gridBoostingKeepTrading, LIDefault.gridBoostingKeepTrading)
        self.gridBoostingTriggerAmount = configs.get(LIConfigKey.gridBoostingTriggerAmount, LIDefault.gridBoostingTriggerAmount)
        self.gridBoostingTriggerPercent = configs.get(LIConfigKey.gridBoostingTriggerPercent, LIDefault.gridBoostingTriggerPercent)
        self.gridBoostingMaxHoldQuantity = configs.get(LIConfigKey.gridBoostingMaxHoldQuantity, LIDefault.gridBoostingMaxHoldQuantity)
        self.gridBoostingStopProfitAmounts = configs.get(LIConfigKey.gridBoostingStopProfitAmounts, LIDefault.gridBoostingStopProfitAmounts)
        self.gridBoostingStopProfitPercents = configs.get(LIConfigKey.gridBoostingStopProfitPercents, LIDefault.gridBoostingStopProfitPercents)
        self.gridBoostingTrailingStopQuantity = configs.get(LIConfigKey.gridBoostingTrailingStopQuantity, LIDefault.gridBoostingTrailingStopQuantity)

        self.gridHedgeEnabled = configs.get(LIConfigKey.gridHedgeEnabled, LIDefault.gridHedgeEnabled)
        self.gridHedgeOverLosingLots = configs.get(LIConfigKey.gridHedgeOverLosingLots, LIDefault.gridHedgeOverLosingLots)

        if not (1 <= self.gridMaintainOpenOrders <= 3):
            terminate(f"Please specify {LIConfigKey.gridMaintainOpenOrders} between 1 and 3!")
        if not (2 <= self.gridMaintainCloseOrders <= 10):
            terminate(f"Please specify {LIConfigKey.gridMaintainCloseOrders} between 2 and 10!")
        if not 0 <= self.gridLongLots <= 100 or not 0 <= self.gridShortLots <= 100:
            terminate(f"Please specify value between 0 and 25 for {LIConfigKey.gridLongLots} or {LIConfigKey.gridShortLots}!")
        if self.gridLongLotsQty and len(self.gridLongLotsQty) != self.gridLongLots:
            terminate(f"Please correct {LIConfigKey.gridLongLotsQty} to match {LIConfigKey.gridLongLots}!")
        if self.gridShortLotsQty and len(self.gridShortLotsQty) != self.gridShortLots:
            terminate(f"Please correct {LIConfigKey.gridShortLotsQty} to match {LIConfigKey.gridShortLots}!")
        if self.gridLimitStartPrices and self.gridFixedStartPrices:
            terminate(f"Please specify either {LIConfigKey.gridLimitStartPrices} or {LIConfigKey.gridFixedStartPrices}!")
        if self.gridInitOpenedLots and self.gridRetainOpenedLots:
            terminate(f"Please specify either {LIConfigKey.gridInitOpenedLots} or {LIConfigKey.gridRetainOpenedLots}!")
        if self.gridLongLots and not self.gridShortLots and self.gridRetainOpenedLots < 0:
            terminate(f"Please specify positive {LIConfigKey.gridRetainOpenedLots} as {LIConfigKey.gridLongLots}={self.gridLongLots}!")
        if self.gridShortLots and not self.gridLongLots and self.gridRetainOpenedLots > 0:
            terminate(f"Please specify negative {LIConfigKey.gridRetainOpenedLots} as {LIConfigKey.gridShortLots}={self.gridShortLots}!")
        if self.gridFixedStartPrices and self.gridInitOpenedLots:
            terminate(f"Please specify either {LIConfigKey.gridFixedStartPrices} or {LIConfigKey.gridInitOpenedLots}!")
        if self.gridFixedStartPrices and self.gridRetainOpenedLots:
            terminate(f"Please specify either {LIConfigKey.gridFixedStartPrices} or {LIConfigKey.gridRetainOpenedLots}!")
        if self.gridFixedStartPrices and self.gridResetStartPrices:
            terminate(f"Please specify either {LIConfigKey.gridResetStartPrices} or {LIConfigKey.gridFixedStartPrices}!")
        if self.gridFixedStartPrices and self.gridSignalStartPrices:
            terminate(f"Please specify either {LIConfigKey.gridFixedStartPrices} or {LIConfigKey.gridSignalStartPrices}!")
        if self.gridFixedStartPrices and self.gridFollowAdverseTrend:
            terminate(f"Please specify either {LIConfigKey.gridFixedStartPrices} or {LIConfigKey.gridFollowAdverseTrend}!")
        if self.gridFixedStartPrices and self.gridStickToMarketTrend:
            terminate(f"Please specify either {LIConfigKey.gridFixedStartPrices} or {LIConfigKey.gridStickToMarketTrend}!")
        if self.gridFixedStartPrices and self.gridRealignOpenPositions:
            terminate(f"Please specify either {LIConfigKey.gridFixedStartPrices} or {LIConfigKey.gridRealignOpenPositions}!")
        if self.gridLimitStartPrices and self.gridRealignOpenPositions:
            terminate(f"Please specify either {LIConfigKey.gridLimitStartPrices} or {LIConfigKey.gridRealignOpenPositions}!")
        if self.gridResetStartPrices and self.gridResetLotsMetadata:
            terminate(f"Please specify either {LIConfigKey.gridResetStartPrices} or {LIConfigKey.gridResetLotsMetadata}!")
        if self.gridResetLotsMetadata and self.gridInitializeSession:
            terminate(f"Please specify either {LIConfigKey.gridResetLotsMetadata} or {LIConfigKey.gridInitializeSession}!")
        if self.gridLotLevelAmount and self.gridLotLevelPercent:
            terminate(f"Please specify either {LIConfigKey.gridLotLevelAmount} or {LIConfigKey.gridLotLevelPercent}!")
        if self.isNotCommandMode() and not self.gridLotLevelAmount and not self.gridLotLevelPercent:
            terminate(f"Please specify either {LIConfigKey.gridLotLevelAmount} or {LIConfigKey.gridLotLevelPercent}!")
        if self.gridHedgeEnabled:
            reason = f"{LIConfigKey.gridHedgeEnabled}={self.gridHedgeEnabled}"
            if not self.gridHedgeOverLosingLots:
                terminate(f"Please specify {LIConfigKey.gridHedgeOverLosingLots} since {reason}!")
            if self.gridLongLots != self.gridShortLots:
                terminate(f"Please specify the same long and short lots since {reason}!")
        if self.isNotCommandMode() and self.investAmount.maxHolding and not self.gridLotMinQuantity:
            terminate(f"Please specify {LIConfigKey.gridLotMinQuantity} since maxHolding={self.investAmount.maxHolding}!")
        if self.isNotCommandMode() and self.investAmount.maxCapital and not self.gridLotMinQuantity:
            terminate(f"Please specify {LIConfigKey.gridLotMinQuantity} since maxCapital={self.investAmount.maxCapital}!")
        if isNotLiveMode() and self.gridInitializeSession is None:
            terminate(f"Please specify {LIConfigKey.gridInitializeSession} explicitly for backtest mode!")

        # Verify grid settings' integrity upon grid mode
        if self.isContrarianMode() and self.openWithMarketOrderType:
            terminate(f"Please disable {LIConfigKey.openWithMarketOrderType} for {self.gridMode} mode!")
        if self.gridLimitStartPrices:
            if self.gridLongLots and not self.gridLimitStartPrices.get(self.getGridLongSide()):
                terminate(f"Please specify both {LIConfigKey.gridLongLots} and {LIConfigKey.gridLimitStartPrices}[{self.getGridLongSide()}]!")
            if self.gridShortLots and not self.gridLimitStartPrices.get(self.getGridShortSide()):
                terminate(f"Please specify both {LIConfigKey.gridShortLots} and {LIConfigKey.gridLimitStartPrices}[{self.getGridShortSide()}]!")
        if self.gridFixedStartPrices:
            if self.gridLongLots and not self.gridFixedStartPrices.get(self.getGridLongSide()):
                terminate(f"Please specify both {LIConfigKey.gridLongLots} and {LIConfigKey.gridFixedStartPrices}[{self.getGridLongSide()}]!")
            if self.gridShortLots and not self.gridFixedStartPrices.get(self.getGridShortSide()):
                terminate(f"Please specify both {LIConfigKey.gridShortLots} and {LIConfigKey.gridFixedStartPrices}[{self.getGridShortSide()}]!")
        if self.gridResetStartPrices:
            if self.gridLongLots and not self.gridResetStartPrices.get(self.getGridLongSide()):
                terminate(f"Please specify both {LIConfigKey.gridLongLots} and {LIConfigKey.gridResetStartPrices}[{self.getGridLongSide()}]!")
            if self.gridShortLots and not self.gridResetStartPrices.get(self.getGridShortSide()):
                terminate(f"Please specify both {LIConfigKey.gridShortLots} and {LIConfigKey.gridResetStartPrices}[{self.getGridShortSide()}]!")
        if self.gridFixedOpenFromPrices:
            if self.isContrarianMode() and not self.gridFixedStartPrices:
                terminate(f"Please specify {LIConfigKey.gridFixedStartPrices} as {LIConfigKey.gridFixedOpenFromPrices}={self.gridFixedOpenFromPrices}!")
            if self.gridLongLots and not self.gridFixedOpenFromPrices.get(self.getGridLongSide()):
                terminate(f"Please specify both {LIConfigKey.gridLongLots} and {LIConfigKey.gridFixedOpenFromPrices}[{self.getGridLongSide()}]!")
            if self.gridShortLots and not self.gridFixedOpenFromPrices.get(self.getGridShortSide()):
                terminate(f"Please specify both {LIConfigKey.gridShortLots} and {LIConfigKey.gridFixedOpenFromPrices}[{self.getGridShortSide()}]!")
        if self.gridBandingStartPrices:
            if self.gridLongLots and not self.gridBandingStartPrices.get(self.getGridLongSide()):
                terminate(f"Please specify both {LIConfigKey.gridLongLots} and {LIConfigKey.gridBandingStartPrices}[{self.getGridLongSide()}]!")
            if self.gridShortLots and not self.gridBandingStartPrices.get(self.getGridShortSide()):
                terminate(f"Please specify both {LIConfigKey.gridShortLots} and {LIConfigKey.gridBandingStartPrices}[{self.getGridShortSide()}]!")
            if self.gridRetainOpenedLots:
                terminate(f"Please remove {LIConfigKey.gridRetainOpenedLots} as {LIConfigKey.gridBandingStartPrices}={self.gridBandingStartPrices}.")
            if self.gridFixedStartPrices:
                terminate(f"Please remove {LIConfigKey.gridFixedStartPrices} as {LIConfigKey.gridBandingStartPrices}={self.gridBandingStartPrices}.")
            if not self.bollingerBandsParams:
                terminate(f"Please specify {LIConfigKey.bollingerBandsParams} as {LIConfigKey.gridBandingStartPrices}={self.gridBandingStartPrices}.")
        if self.gridBandingOpenFromPrices:
            if self.gridLongLots and not self.gridBandingOpenFromPrices.get(self.getGridLongSide()):
                terminate(f"Please specify both {LIConfigKey.gridLongLots} and {LIConfigKey.gridBandingOpenFromPrices}[{self.getGridLongSide()}]!")
            if self.gridShortLots and not self.gridBandingOpenFromPrices.get(self.getGridShortSide()):
                terminate(f"Please specify both {LIConfigKey.gridShortLots} and {LIConfigKey.gridBandingOpenFromPrices}[{self.getGridShortSide()}]!")
            if self.isMomentumMode() and self.gridFixedStartPrices:
                terminate(f"Please remove {LIConfigKey.gridFixedStartPrices} as {LIConfigKey.gridBandingOpenFromPrices}={self.gridBandingOpenFromPrices}!")
            elif self.isContrarianMode() and not self.gridBandingStartPrices:
                terminate(f"Please specify {LIConfigKey.gridBandingStartPrices} as {LIConfigKey.gridBandingOpenFromPrices}={self.gridBandingOpenFromPrices}!")
            if not self.bollingerBandsParams:
                terminate(f"Please specify {LIConfigKey.bollingerBandsParams} as {LIConfigKey.gridBandingOpenFromPrices}={self.gridBandingOpenFromPrices}!")
        if self.gridBandingLimitStartPrices:
            if self.gridLongLots and not self.gridBandingLimitStartPrices.get(self.getGridLongSide()):
                terminate(f"Please specify both {LIConfigKey.gridLongLots} and {LIConfigKey.gridBandingLimitStartPrices}[{self.getGridLongSide()}]!")
            if self.gridShortLots and not self.gridBandingLimitStartPrices.get(self.getGridShortSide()):
                terminate(f"Please specify both {LIConfigKey.gridShortLots} and {LIConfigKey.gridBandingLimitStartPrices}[{self.getGridShortSide()}]!")
            if self.gridLimitStartPrices:
                terminate(f"Please remove {LIConfigKey.gridLimitStartPrices} as {LIConfigKey.gridBandingLimitStartPrices}={self.gridBandingLimitStartPrices}!")
            if not self.bollingerBandsParams:
                terminate(f"Please specify {LIConfigKey.bollingerBandsParams} as {LIConfigKey.gridBandingLimitStartPrices}={self.gridBandingLimitStartPrices}!")
        if self.gridTransfer2Counterpart:
            if self.tradeBothSides() and self.gridLongLots != self.gridShortLots:
                terminate(f"Please make sure {LIConfigKey.gridLongLots}=={LIConfigKey.gridShortLots} "
                          f"as {LIConfigKey.gridTransfer2Counterpart}={self.gridTransfer2Counterpart}.")
        if self.gridCloseCounterpartLots:
            pass  # Add verification later

        if self.tradeBothSides() and self.isContrarianMode() and not self.gridHedgeEnabled:
            if self.gridLimitStartPrices and not (
                    self.gridLimitStartPrices.get(self.getGridLongSide()) and self.gridLimitStartPrices.get(self.getGridShortSide())):
                terminate(f"Please specify both {self.getGridLongSide()} and {self.getGridShortSide()} for {LIConfigKey.gridLimitStartPrices}!")
            if self.gridFixedStartPrices and not (
                    self.gridFixedStartPrices.get(self.getGridLongSide()) and self.gridFixedStartPrices.get(self.getGridShortSide())):
                terminate(f"Please specify both {self.getGridLongSide()} and {self.getGridShortSide()} for {LIConfigKey.gridFixedStartPrices}!")
            if self.gridResetStartPrices and not (
                    self.gridResetStartPrices.get(self.getGridLongSide()) and self.gridResetStartPrices.get(self.getGridShortSide())):
                terminate(f"Please specify both {self.getGridLongSide()} and {self.getGridShortSide()} for {LIConfigKey.gridResetStartPrices}!")
            if not (self.marketBias or self.gridLimitStartPrices or self.gridFixedStartPrices or self.gridResetStartPrices or
                    self.gridBandingStartPrices or self.gridBandingLimitStartPrices):
                terminate(f"Please specify one of {LIConfigKey.marketBias}, {LIConfigKey.gridLimitStartPrices}, {LIConfigKey.gridFixedStartPrices}, "
                          f"{LIConfigKey.gridResetStartPrices}, {LIConfigKey.gridBandingStartPrices} or {LIConfigKey.gridBandingLimitStartPrices}!")
        if self.isBuyAndHoldMode():
            if self.gridShortLots or not self.gridLongLots:
                terminate(f"Please specify only {LIConfigKey.gridLongLots} for {LIConfigKey.gridMode}={self.gridMode}!")
            if not (self.dcaInvestCapital or self.dcaInvestQuantity) or not self.dcaInvestPeriodicity:
                terminate(f"Please specify {LIConfigKey.dcaInvestCapital} or {LIConfigKey.dcaInvestQuantity} and {LIConfigKey.dcaInvestPeriodicity} "
                          f"for {LIConfigKey.gridMode}={self.gridMode}!")
        if self.gridRestartOnFridayClose and not self.liquidateOnFridayClose:
            terminate(f"Please enable {LIConfigKey.liquidateOnFridayClose} as {LIConfigKey.gridRestartOnFridayClose}={self.gridRestartOnFridayClose}")

        if self.stopLossLevelAmount or self.stopLossLevelPercent:
            terminate(f"Please enable boosting mode instead for (trailing) stop loss all positions!")
        if self.gridBoostingTriggerAmount and self.gridBoostingTriggerPercent:
            terminate(f"Please specify either {LIConfigKey.gridBoostingTriggerAmount} or {LIConfigKey.gridBoostingTriggerPercent}.")
        if self.gridBoostingTriggerAmount or self.gridBoostingTriggerPercent:
            if self.isBuyAndHoldMode():
                terminate(f"{LIGridMode.BUYANDHOLD} mode cannot support {LIGridMode.BOOSTING} mode")
            if not self.gridBoostingMaxHoldQuantity:
                terminate(f"Please specify {LIConfigKey.gridBoostingMaxHoldQuantity} to enable boosting mode!")
            if ((self.gridBoostingStopProfitAmounts and self.gridBoostingStopProfitPercents)
                    or (not self.gridBoostingStopProfitAmounts and not self.gridBoostingStopProfitPercents)):
                terminate(f"Please specify either {LIConfigKey.gridBoostingStopProfitAmounts} "
                          f"or {LIConfigKey.gridBoostingStopProfitPercents} to enable boosting mode!")

        if self.liquidateOnTakeProfitAmounts:
            if self.isMomentumMode():
                if not self.liquidateOnTakeProfitAmounts.get(LIGridSide.BTU) or not self.liquidateOnTakeProfitAmounts.get(LIGridSide.STD):
                    terminate(f"Please specify both {LIGridSide.BTU} and {LIGridSide.STD} for {self.gridMode}!")
            elif self.isContrarianMode():
                if not self.liquidateOnTakeProfitAmounts.get(LIGridSide.BTD) or not self.liquidateOnTakeProfitAmounts.get(LIGridSide.STU):
                    terminate(f"Please specify both {LIGridSide.BTD} and {LIGridSide.STU} for {self.gridMode}!")

        self.signalSymbolMonitor = self.getSecurityMonitor(self.signalSymbolStr, self.signalSecurityType)
        self.signalSymbolMonitor.subscribeSecurityChanged(self, LIPriority.LOW)
        self.signalSymbolMonitor.subscribeDataBarUpdated(self, LIPriority.LOW)

        # securityMonitor = signalSymbolMonitor when signalSymbolStr = tradeSymbolStr
        self.securityMonitor = self.getSecurityMonitor(self.tradeSymbolStr, self.tradeSecurityType)
        self.positionManager = self.getPositionManager(self.securityMonitor)
        self.canonicalSymbol = self.positionManager.getCanonicalSymbol()

        self.lastBar = None
        self.gridHeikinAshies: list[HeikinAshi] = []
        if self.gridHeikinAshiPlies:
            for n in range(self.gridHeikinAshiPlies):
                heikinAshi = HeikinAshi(str(n))
                heikinAshi.updated += self.onHeikinAshiUpdated  # Call back to update other indicators
                self.gridHeikinAshies.append(heikinAshi)
        self.comboTrendingIndicator: LIComboTrendingIndicator = None
        if self.comboTrendingParams:
            self.comboTrendingIndicator = self.getComboTrendingIndicator(self.signalSymbolMonitor, self.positionManager)
            self.comboTrendingIndicator.subscribeTradeInsight(self)
        self.bollingerBandsIndicator: LIBollingerBandsIndicator = None
        if self.bollingerBandsParams:
            self.bollingerBandsIndicator = self.getBollingerBandsIndicator(self.signalSymbolMonitor, self.positionManager)
            self.bollingerBandsIndicator.subscribeTradeInsight(self)
        if self.gridBandingStartPrices:
            for bandName in self.gridBandingStartPrices.values():
                if not self.bollingerBandsIndicator.getBand(bandName):
                    terminate(f"Not found {LIConfigKey.gridBandingStartPrices}={self.gridBandingStartPrices} in "
                              f"{self.bollingerBandsIndicator.getBandNames()}!")
        if self.gridBandingOpenFromPrices:
            for bandName in self.gridBandingOpenFromPrices.values():
                if not self.bollingerBandsIndicator.getBand(bandName):
                    terminate(f"Not found {LIConfigKey.gridBandingOpenFromPrices}={self.gridBandingOpenFromPrices} in "
                              f"{self.bollingerBandsIndicator.getBandNames()}!")
        if self.gridBandingLimitStartPrices:
            for bandName in self.gridBandingLimitStartPrices.values():
                if not self.bollingerBandsIndicator.getBand(bandName):
                    terminate(f"Not found {LIConfigKey.gridBandingLimitStartPrices}={self.gridBandingLimitStartPrices} in "
                              f"{self.bollingerBandsIndicator.getBandNames()}!")

        if self.isMomentumMode():
            getAlgo().set_trade_builder(TradeBuilder(FillGroupingMethod.FILL_TO_FILL, FillMatchingMethod.FIFO))
        elif self.isContrarianMode():
            getAlgo().set_trade_builder(TradeBuilder(FillGroupingMethod.FILL_TO_FILL, FillMatchingMethod.LIFO))

        self.gridMetadataKey = None
        self.gridLotsMetadataKey = None
        self.gridMetadata: dict = None
        self.gridLotsMetadata: dict = None

        self.sessionId = 0
        self.sessionStartedTime = None
        self.gridStartPrices = {}
        self.gridOpenFromPrices = {}
        self.gridBoundaryPrices = {}  # Tracking min/max reached prices
        self.lastTradingMarketPrice = None  # Avoid using the same market price

        self.startLot: LIGridTradingLot = None  # The reference/starting lot with #0
        self.transferOrderId = 0  # Decrease with negative id
        self.invalidOrderCount = 0  # Tracking how many orders been rejected/denied!
        self.shiftedGridLotsCount = 0

        self.flipToSignalType = None
        self.reachedOpenPrice = False
        self.liquidatedAlready = False
        self.liquidateByTrailingProfit = 0.0  # Tracking trailing stop profit price/amount/percent for liquidation
        self.overallMaxProfitLoss = (0.0, 0.0)  # Tracking overall max/min profit/loss across multiple sessions

        self.closedTradesCount = 0
        self.stoppedLossPrices = {}  # NOT exceed this red/bottom line!
        self.pauseTradingTillTime = None

        # Dollar-Cost Averaging (DCA)
        self.dcaMaxStartPrice = 0.0
        self.dcaHoldingQuantity = 0
        self.dcaLastInvestedDate: datetime = None

        # Bollinger Bands Trading
        self.startBandName = None
        self.tradingTierName = None

        self.openOrderTicket: OrderTicket = None
        self.closeOrderTicket: OrderTicket = None
        self.avgFilledOpenPrice = None
        self.trailingStopPrice = None
        self.closeOrderUpdatedTimes = 0

    def getPeriodicityTimedelta(self) -> timedelta:
        if self.dcaInvestPeriodicity == LIPeriodicity.DAILY:
            return timedelta(days=1)
        elif self.dcaInvestPeriodicity == LIPeriodicity.WEEKLY:
            return timedelta(weeks=1)
        elif self.dcaInvestPeriodicity == LIPeriodicity.MONTHLY:
            return timedelta(weeks=4)
        else:
            terminate(f"Not support {LIConfigKey.dcaInvestPeriodicity}={self.dcaInvestPeriodicity}")
            return None

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
        return None

    def getLastLot(self, peerLot):
        if peerLot.isLongLot():
            return self.getLastLongLot()
        if peerLot.isShortLot():
            return self.getLastShortLot()
        return None

    def getLotById(self, lotId):
        lot = self.getHeadLot()
        while lot:
            if lot.lotId == lotId:
                return lot
            lot = lot.nextLot
        return None

    def getLastOpenedLot(self, peerLot):
        if peerLot.isLongLot():
            return self.getLastOpenedLongLot()
        if peerLot.isShortLot():
            return self.getLastOpenedShortLot()
        return None

    def getCounterpartLot(self, peerLot):
        lot = self.getHeadLot()
        while lot:
            if lot.lotId == -peerLot.lotId:
                return lot
            lot = lot.nextLot
        return None

    def getLastOpenedCounterpartLot(self, peerLot):
        if peerLot.isLongLot():
            return self.getLastOpenedShortLot()
        if peerLot.isShortLot():
            return self.getLastOpenedLongLot()
        return None

    def getFirstOpenedCounterpartLot(self, peerLot):
        if peerLot.isLongLot():
            return self.getFirstOpenedShortLot()
        if peerLot.isShortLot():
            return self.getFirstOpenedLongLot()
        return None

    def getFirstOpenedLongLot(self):
        lot = self.startLot.nextLot
        while lot:
            if lot.hasOpenPosition():
                return lot
            lot = lot.nextLot
        return None

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
        return None

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
        return None

    def getSecondShortLot(self):
        if self.getFirstShortLot():
            return self.getFirstShortLot().prevLot
        return None

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

    def tradeBothSides(self) -> bool:
        return self.gridLongLots and self.gridShortLots

    def isCommandMode(self):
        return self.gridMode == LIGridMode.COMMAND

    def isNotCommandMode(self):
        return self.gridMode != LIGridMode.COMMAND

    def isBoostingMode(self):
        return self.gridMode == LIGridMode.BOOSTING

    def isMomentumMode(self):
        return self.gridMode == LIGridMode.MOMENTUM

    def isContrarianMode(self):
        """BuyAndHold mode will buy the dip, it's the contrarian mode's long side behavior"""
        return self.gridMode == LIGridMode.CONTRARIAN or self.gridMode == LIGridMode.BUYANDHOLD

    def isBuyAndHoldMode(self):
        return self.gridMode == LIGridMode.BUYANDHOLD

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

    def initializeGridLots(self):
        if self.countTradeLots()[0] == 0:
            self.startLot = self.createGridLot(0)
            if self.gridLongLots:
                for idx in range(self.gridLongLots):
                    self.addLastLongLot()
            if self.gridShortLots:
                for idx in range(self.gridShortLots):
                    self.addLastShortLot()

    def createGridLots(self, maxLots):
        if self.startLot is None:
            self.startLot = self.createGridLot(0)
        if maxLots > 0:
            lot = self.startLot.nextLot
            for idx in range(maxLots):
                if lot is None:
                    lot = self.addLastLongLot()
                lot = lot.nextLot
        if maxLots < 0:
            lot = self.startLot.prevLot
            for idx in range(abs(maxLots)):
                if lot is None:
                    lot = self.addLastShortLot()
                lot = lot.prevLot

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
        return None

    def getGridShortSide(self):
        if self.isMomentumMode():
            return LIGridSide.STD
        elif self.isContrarianMode():
            return LIGridSide.STU
        return None

    def getTradeInsight(self):
        # Overwrite signal type if flip to signal type is enforced!
        if self.tradeInsight and self.flipToSignalType and self.flipToSignalType != LISignalType.NONE and self.flipToSignalType != self.tradeInsight.signalType:
            tradeInsight = copy.copy(self.tradeInsight)  # Shallow copy to avoid modifying the original signal
            tradeInsight.signalType = self.flipToSignalType
            return tradeInsight
        return self.tradeInsight

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

    def getCounterpartMode(self):
        if self.gridMode == LIGridMode.MOMENTUM:
            return LIGridMode.CONTRARIAN
        elif self.gridMode == LIGridMode.CONTRARIAN:
            return LIGridMode.MOMENTUM
        elif self.gridMode == LIGridMode.BUYANDHOLD:
            return LIGridMode.BUYANDHOLD
        else:
            terminate(f"Not able to reverse the {LIConfigKey.gridMode}={self.gridMode}")
            return None

    def adjustGridHedgeLots(self, lots):
        if lots == 0:
            self.startLot.nextLot = None
            self.startLot.prevLot = None
        if lots > 0:
            while self.countLongLots() < lots:
                self.addLastLongLot()
            while self.countLongLots() > lots:
                self.dropLastLongLot().resetTradingLot(reason="Drop last long lot")
        if lots < 0:
            while self.countShortLots() < abs(lots):
                self.addLastShortLot()
            while self.countShortLots() > abs(lots):
                self.dropLastShortLot().resetTradingLot(reason="Drop last short lot")
        self.resetGridLotIds()  # Set proper sequential ids

    def getTradingTierFactorIndex(self):
        tierIndex = int(self.tradingTierName.split("-")[1][1:])
        bandCounts = self.bollingerBandsIndicator.countBands()
        tierFactorIndex = (bandCounts[1] - tierIndex) if ("upper" in self.tradingTierName) else (bandCounts[0] - bandCounts[1] + tierIndex)
        return tierFactorIndex

    def getComboTrendingIndicator(self, securityMonitor: LISecurityMonitor, positionManager: LIPositionManager) -> LIComboTrendingIndicator:
        symbolKey = securityMonitor.getSymbolKey()
        insightIndicator = self.insightIndicators.get(symbolKey)
        if insightIndicator is None:
            insightIndicator = LIComboTrendingIndicator(securityMonitor, positionManager, self.mainChart, self.configs)
            self.insightIndicators[symbolKey] = insightIndicator
        return insightIndicator

    def getBollingerBandsIndicator(self, securityMonitor: LISecurityMonitor, positionManager: LIPositionManager) -> LIBollingerBandsIndicator:
        symbolKey = securityMonitor.getSymbolKey()
        insightIndicator = self.insightIndicators.get(symbolKey)
        if insightIndicator is None:
            insightIndicator = LIBollingerBandsIndicator(securityMonitor, positionManager, self.mainChart, self.configs)
            self.insightIndicators[symbolKey] = insightIndicator
        return insightIndicator

    def initializeMetadata(self):
        # Map of grid trading metadata: {key1: value2, key2: value2}
        self.gridMetadataKey = self.getMetadataKeyPrefix() + "/gridMetadata"
        # Map of grid lots trading metadata: {key1: value2, key2: value2}
        self.gridLotsMetadataKey = self.getMetadataKeyPrefix() + "/gridLotsMetadata"

        if self.gridInitializeSession:
            self.deleteGridMetadata()
        if self.gridResetLotsMetadata:
            self.resetLotsMetadataAndQuit()

        self.gridMetadata: dict = readMetadata(self.gridMetadataKey, "dict", default={})
        self.gridLotsMetadata: dict = readMetadata(self.gridLotsMetadataKey, "dict", default={})

        self.gridMode = self.gridMetadata.get(LIMetadataKey.gridMode, self.gridMode)
        if not self.isBoostingMode():
            self.gridMode = self.gridInitMode
        if not (self.gridBoostingTriggerAmount or self.gridBoostingTriggerPercent):
            self.gridMode = self.gridInitMode
        if not self.configs.get(LIConfigKey.optionContractCode) and self.gridMetadata.get(LIMetadataKey.optionContractCode):
            self.configs[LIConfigKey.optionContractCode] = self.gridMetadata.get(LIMetadataKey.optionContractCode)

        if not self.gridNotifyTargetPrices or self.isBoostingMode():
            self.notifySettings(f"Grid Trading {self.gridMode}")

    def storeGridMetadata(self, logging=True):
        self.refreshGridMetadata()
        saveMetadata(self.gridMetadataKey, self.gridMetadata, logging=logging)
        if self.gridLotsMetadata or self.gridResetLotsMetadata or self.gridResetStartPrices:
            saveMetadata(self.gridLotsMetadataKey, self.gridLotsMetadata, logging=logging)

    def refreshGridMetadata(self):
        self.gridMetadata = {}
        self.gridLotsMetadata = {}
        self.gridMetadata[LIMetadataKey.version] = LIGlobal.latestVersion
        self.gridMetadata[LIMetadataKey.gridMode] = self.gridMode
        self.gridMetadata[LIMetadataKey.sessionId] = self.sessionId
        self.gridMetadata[LIMetadataKey.startPrices] = self.gridStartPrices
        self.gridMetadata[LIMetadataKey.investedQuantity] = self.getInvestedQuantity()
        self.gridMetadata[LIMetadataKey.stoppedLossPrices] = self.stoppedLossPrices
        self.gridMetadata[LIMetadataKey.closedTradesCount] = self.closedTradesCount
        self.gridMetadata[LIMetadataKey.realizedProfitLoss] = self.realizedProfitLoss
        self.gridMetadata[LIMetadataKey.rolloverProfitLoss] = self.rolloverProfitLoss
        self.overallMaxProfitLoss = (max(self.overallMaxProfitLoss[0], self.getMaxProfitLossAmount()),
                                     min(self.overallMaxProfitLoss[1], self.getMaxProfitLossAmount()))
        self.gridMetadata[LIMetadataKey.overallMaxProfitLoss] = self.overallMaxProfitLoss
        if self.isBuyAndHoldMode():
            self.gridMetadata[LIMetadataKey.dcaMaxStartPrice] = self.dcaMaxStartPrice
            self.gridMetadata[LIMetadataKey.dcaHoldingQuantity] = self.dcaHoldingQuantity
            self.gridMetadata[LIMetadataKey.dcaLastInvestedDate] = self.dcaLastInvestedDate.strftime(
                LIGlobal.timestampFormat) if self.dcaLastInvestedDate else None
        if self.bollingerBandsIndicator:
            self.gridMetadata[LIMetadataKey.startBandName] = self.startBandName
            self.gridMetadata[LIMetadataKey.tradingTierName] = self.tradingTierName
        self.gridMetadata[LIMetadataKey.tradeInsight] = self.getTradeInsight().toMetadata()
        if self.liquidateByTrailingProfitPercent:
            self.gridMetadata[LIMetadataKey.liquidateByTrailingProfit] = self.liquidateByTrailingProfit
        if self.gridFixedOpenFromPrices or self.gridBandingOpenFromPrices:
            self.gridMetadata[LIMetadataKey.openFromPrices] = self.gridOpenFromPrices
            self.gridMetadata[LIMetadataKey.reachedOpenPrice] = self.reachedOpenPrice
        if self.flipToSignalType and self.flipToSignalType != LISignalType.NONE:
            self.gridMetadata[LIMetadataKey.flipToSignalType] = self.flipToSignalType
        self.gridMetadata[LIMetadataKey.pauseTradingTillTime] = self.pauseTradingTillTime.strftime(
            LIGlobal.timestampFormat) if self.pauseTradingTillTime else None
        # Reserve current option contract identifier for restart/reboot/resume
        if self.positionManager.getContract() and isOption(self.getSymbol().security_type):
            self.gridMetadata[LIMetadataKey.optionContractCode] = cleanSymbolValue(self.getSymbol())
        elif self.configs.get(LIConfigKey.optionContractCode):
            self.gridMetadata[LIMetadataKey.optionContractCode] = self.configs.get(LIConfigKey.optionContractCode)
        lot = self.getTradeLot()
        while lot:
            lot.refreshLotMetadata()
            lot = lot.getNextLot()

    def restoreGridMetadata(self, postRollover=False):
        if not postRollover:
            self.sessionId = self.gridMetadata.get(LIMetadataKey.sessionId, 1)
        self.gridStartPrices = self.gridMetadata.get(LIMetadataKey.startPrices, {})
        self.stoppedLossPrices = self.gridMetadata.get(LIMetadataKey.stoppedLossPrices, {})
        self.stoppedLossPrices = {} if self.stoppedLossPrices == 0.0 else self.stoppedLossPrices
        self.closedTradesCount = self.gridMetadata.get(LIMetadataKey.closedTradesCount, 0)
        self.realizedProfitLoss = self.gridMetadata.get(LIMetadataKey.realizedProfitLoss, 0.0)
        self.rolloverProfitLoss = self.gridMetadata.get(LIMetadataKey.rolloverProfitLoss, 0.0)
        self.overallMaxProfitLoss = self.gridMetadata.get(LIMetadataKey.overallMaxProfitLoss, (0.0, 0.0))
        if self.isBuyAndHoldMode():
            self.dcaMaxStartPrice = self.gridMetadata.get(LIMetadataKey.dcaMaxStartPrice, 0)
            self.dcaHoldingQuantity = self.gridMetadata.get(LIMetadataKey.dcaHoldingQuantity, 0)
            self.dcaLastInvestedDate = self.gridMetadata.get(LIMetadataKey.dcaLastInvestedDate, None)
            self.dcaLastInvestedDate = datetime.strptime(self.dcaLastInvestedDate, LIGlobal.timestampFormat) if self.dcaLastInvestedDate else getAlgo().time
        if self.bollingerBandsIndicator:
            self.startBandName = self.gridMetadata.get(LIMetadataKey.startBandName, None)
            self.tradingTierName = self.gridMetadata.get(LIMetadataKey.tradingTierName, None)
            self.bollingerBandsIndicator.resetStartBand(self.startBandName)
        if self.liquidateByTrailingProfitPercent:
            self.liquidateByTrailingProfit = self.gridMetadata.get(LIMetadataKey.liquidateByTrailingProfit, 0.0)
        if self.gridFixedOpenFromPrices or self.gridBandingOpenFromPrices:
            self.gridOpenFromPrices = self.gridMetadata.get(LIMetadataKey.openFromPrices, {})
            self.reachedOpenPrice = self.gridMetadata.get(LIMetadataKey.reachedOpenPrice, False)
        self.flipToSignalType = self.gridMetadata.get(LIMetadataKey.flipToSignalType, None) if self.flipSignalAtLiquidateFactor else None
        self.pauseTradingTillTime = datetime.strptime(self.pauseTradingTillTime, LIGlobal.timestampFormat) if self.pauseTradingTillTime else None
        lot = self.getTradeLot()
        while lot:
            lot.restoreLotMetadata(postRollover=postRollover)
            lot = lot.getNextLot()
        # Overwrite for correction purposes
        # self.dcaHoldingQuantity = 18
        # self.dcaMaxStartPrice = 551.33

    def deleteGridMetadata(self):
        deleteMetadata(self.getMetadataKeyPrefix(), logging=True)

    def resetLotsMetadataAndQuit(self):
        deleteMetadata(self.gridLotsMetadataKey, logging=True)
        settings = f"{LIConfigKey.gridResetLotsMetadata}={self.gridResetLotsMetadata}"
        if isLiveMode():  # Avoid auto redeploy (crash/reboot) to reset start prices repeatedly!
            notify(f"{self.getNotifyPrefix()}: Quit algorithm after applied the settings: {settings}, please remove it and redeploy!")
            self.saveMetadataAtEnd = False
            getAlgo().quit("Quit algorithm on RESET LOTS METADATA!")
        else:
            notify(f"{self.getNotifyPrefix()}: Applied the settings: {settings}!")

    def resetGridStartPrices(self, startPrices=None, emptyStartPrices=False, emptyOpenFromPrices=False):
        if emptyStartPrices:
            self.gridStartPrices = {}
        if emptyOpenFromPrices:
            self.gridOpenFromPrices = {}
        if startPrices:
            self.gridStartPrices |= startPrices  # Merge start prices as which could be partial!
            log(f"{self.getSymbolAlias()}: Merged {startPrices} into the grid start prices as {self.gridStartPrices}.")
        elif not self.gridStartPrices:
            marketPrice = self.getMarketPrice()
            if marketPrice:
                if self.gridLongLots:
                    self.gridStartPrices[self.getGridLongSide()] = marketPrice
                if self.gridShortLots:
                    self.gridStartPrices[self.getGridShortSide()] = marketPrice
            else:
                alert(f"{self.getNotifyPrefix()}: Failed to reset start prices due to not able to get market price!")
        elif not self.gridFixedStartPrices:
            marketPrice = self.getMarketPrice()
            if marketPrice:
                if self.gridLongLots:
                    longPrice = self.gridStartPrices.get(self.getGridLongSide(), marketPrice)
                    if self.isMomentumMode():
                        longPrice = min(marketPrice, longPrice)
                    elif self.isContrarianMode():
                        longPrice = max(marketPrice, longPrice)
                    self.gridStartPrices[self.getGridLongSide()] = longPrice
                    log(f"{self.getSymbolAlias()}: Reset long side start price as {LIConfigKey.gridStartPrices}={self.gridStartPrices}", self.verbose)
                if self.gridShortLots:
                    shortPrice = self.gridStartPrices.get(self.getGridShortSide(), marketPrice)
                    if self.isMomentumMode():
                        shortPrice = max(marketPrice, shortPrice)
                    elif self.isContrarianMode():
                        shortPrice = min(marketPrice, shortPrice)
                    self.gridStartPrices[self.getGridShortSide()] = shortPrice
                    log(f"{self.getSymbolAlias()}: Reset short side start price as {LIConfigKey.gridStartPrices}={self.gridStartPrices}", self.verbose)
            else:
                alert(f"{self.getNotifyPrefix()}: Failed to reset start prices as not able to get market price!")
        log(f"{self.getSymbolAlias()}: Reset grid start prices: {self.printGridPrices()}, marketPrice={self.getMarketPrice()}", self.verbose)
        # self.manageGridStartPrices() # DO NOT CALL THIS!

    def manageDCABuyAndHold(self, bar):
        if not self.isBuyAndHoldMode():
            return None

        if self.gridNoMoreOpenOrders:
            log(f"{self.getSymbolAlias()}: Abort placing open order ticket as {LIConfigKey.gridNoMoreOpenOrders}={self.gridNoMoreOpenOrders}", self.verbose)
            return None  # Abort, no more open orders!

        if self.positionManager.isNotExchangeOpen():
            return None

        # Check whether it's time to restart the grid session
        startPrice = self.gridStartPrices[self.getGridLongSide()]
        if not self.dcaMaxStartPrice:
            self.dcaMaxStartPrice = startPrice
            self.dcaInvestQuantity = self.getInvestedQuantity()
        elif self.dcaMaxStartPrice < startPrice:
            openingQuantity = self.getOpeningQuantity()
            if openingQuantity > 0:
                notify(f"{self.getNotifyPrefix()}: Restart grid session upon getting a higher start price from {self.dcaMaxStartPrice} to {startPrice}, "
                       f"and add openingQuantity={openingQuantity} into dcaHoldingQuantity={self.dcaHoldingQuantity}, "
                       f"dcaLastInvestedDate={printFullTime(self.dcaLastInvestedDate)}.")
                self.dcaMaxStartPrice = startPrice
                self.dcaHoldingQuantity = self.getInvestedQuantity()
                self.restartGridSession(reason="Getting a higher start price")
        # Check whether it's time to fill a regular investment
        algoTime = bar.end_time if bar else getAlgo().time
        if isActiveTradingTime(algoTime) and (self.getInvestedQuantity() == 0 or (self.dcaLastInvestedDate + self.getPeriodicityTimedelta()) < algoTime):
            targetQuantity = self.dcaInvestCapital / self.getMarketPrice(bar) if self.dcaInvestCapital else self.dcaInvestQuantity
            targetQuantity = self.positionManager.roundSecuritySize(targetQuantity)
            tagLog = f"Fulfill a DCA regular investment: marketPrice={self.getMarketPrice(bar)}, targetQuantity={targetQuantity}."
            if self.positionManager.limitMarketOrder(targetQuantity, tagLog=tagLog):
                self.dcaLastInvestedDate = algoTime
                # Fulfill a regular investment and continue
                self.dcaHoldingQuantity = self.getInvestedQuantity() - self.getOpeningQuantity()
                self.storeGridMetadata(logging=True)
                dcaInvestMsg = f"dcaInvestCapital={self.dcaInvestCapital}" if self.dcaInvestCapital else f"dcaInvestQuantity={self.dcaInvestQuantity}"
                notify(f"{self.getNotifyPrefix()}: {tagLog}, openingQuantity={self.getOpeningQuantity()}, "
                       f"{dcaInvestMsg}, dcaLastInvestedDate={printFullTime(self.dcaLastInvestedDate)}, "
                       f"dcaHoldingQuantity={self.dcaHoldingQuantity}")
        return None

    def monitorTradingRisk(self):
        # self.manageGridLiquidation()
        if self.riskProposeHedgeInsights:
            if self.tradeSecurityType == SecurityType.FUTURE:
                tradeSymbol = self.getTradeSecurity().symbol
                if self.securityMonitor.isContractExpired(expiryDays=self.riskHedgeOptionExpiryDays):
                    futures = getAlgo().futures_chain(tradeSymbol.canonical)
                    tradeSymbol = sorted([x for x in futures if isExpiredAfterDays(x.id.date, self.riskHedgeOptionExpiryDays)], key=lambda x: x.id.date)[
                        0].symbol
                    log(f"{self.getSymbolAlias()}: Picked the hedge future contract {cleanSymbolValue(tradeSymbol)} expired after {self.riskHedgeOptionExpiryDays} days")
                options = getAlgo().option_chain(tradeSymbol)
                if options and self.isContrarianMode():
                    optionSymbols = []
                    if self.gridLongLots:
                        # Take the middle of stop loss price as the init strike price
                        stopLossPrice = self.getFirstLongLot().getStopLossPrice()[0]
                        stopLossPrice += self.getLastLongLot().getStopLossPrice()[0]
                        stopLossPrice = self.positionManager.roundSecurityPrice(stopLossPrice / 2)
                        optionSymbols += sorted(
                            [x for x in options if
                             x.id.option_style == OptionStyle.AMERICAN and x.id.option_right == OptionRight.PUT and x.id.strike_price <= stopLossPrice],
                            key=lambda x: x.id.strike_price, reverse=True)[0:5]
                    if self.gridShortLots:
                        # Take the middle of stop loss price as the init strike price
                        stopLossPrice = self.getFirstShortLot().getStopLossPrice()[0]
                        stopLossPrice += self.getLastShortLot().getStopLossPrice()[0]
                        stopLossPrice = self.positionManager.roundSecurityPrice(stopLossPrice / 2)
                        optionSymbols += sorted(
                            [x for x in options if
                             x.id.option_style == OptionStyle.AMERICAN and x.id.option_right == OptionRight.CALL and x.id.strike_price >= stopLossPrice],
                            key=lambda x: x.id.strike_price, reverse=False)[0:5]
                    optionContracts = []
                    for optionSymbol in optionSymbols:
                        optionContracts.append(self.securityMonitor.addFutureOptionContract(optionSymbol))
                        # Warm up the open interest cache data
                        history = getAlgo().history[TradeBar](optionSymbol, 10, resolution=Resolution.DAILY)
                        if len(history.index) == 0 or 0 in history.values:
                            alert(f"{self.getNotifyPrefix()}: Open interest history request got empty values!")
                        if optionContracts:
                            proposal = f"Propose to buy some of following future options: \n"
                            for optionContract in optionContracts:
                                proposal += f"{printOptionContract(optionContract)}\n"
                            notify(f"{self.getNotifyPrefix()}: {proposal}")
