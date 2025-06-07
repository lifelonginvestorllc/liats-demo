# region imports
import copy

from deprecated import *
from core.LITrading import *
from core.LIGridTradingLot import *
from indicator.LIBollingerBandsIndicator import *
from indicator.LIStochasticComboIndicator import *
from indicator.LIMACDTrendFollowingIndicator import *

# endregion

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
        self.gridUseTradeInsight = configs.get(LIConfigKey.gridUseTradeInsight, LIDefault.gridUseTradeInsight)
        self.gridBaselinePrice = configs.get(LIConfigKey.gridBaselinePrice, LIDefault.gridBaselinePrice)
        self.gridLimitStartPrices = configs.get(LIConfigKey.gridLimitStartPrices, LIDefault.gridLimitStartPrices)
        self.gridResetStartPrices = configs.get(LIConfigKey.gridResetStartPrices, LIDefault.gridResetStartPrices)
        self.gridFixedStartPrices = configs.get(LIConfigKey.gridFixedStartPrices, LIDefault.gridFixedStartPrices)
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
        self.gridRestartOnFridayClose = configs.get(LIConfigKey.gridRestartOnFridayClose, LIDefault.gridRestartOnFridayClose)
        self.gridRestartIfAllLotsPaused = configs.get(LIConfigKey.gridRestartIfAllLotsPaused, LIDefault.gridRestartIfAllLotsPaused)
        self.gridPauseTradingProfitHours = configs.get(LIConfigKey.gridPauseTradingProfitHours, LIDefault.gridPauseTradingProfitHours)

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
        if self.gridResetStartPrices and self.gridFixedStartPrices:
            terminate(f"Please specify either {LIConfigKey.gridResetStartPrices} or {LIConfigKey.gridFixedStartPrices}!")
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
        if not self.gridLotLevelAmount and not self.gridLotLevelPercent:
            terminate(f"Please specify either {LIConfigKey.gridLotLevelAmount} or {LIConfigKey.gridLotLevelPercent}!")
        if self.gridHedgeEnabled:
            reason = f"{LIConfigKey.gridHedgeEnabled}={self.gridHedgeEnabled}"
            if not self.gridHedgeOverLosingLots:
                terminate(f"Please specify {LIConfigKey.gridHedgeOverLosingLots} since {reason}!")
            if self.gridLongLots != self.gridShortLots:
                terminate(f"Please specify the same long and short lots since {reason}!")
        if self.investAmount.maxHolding and not self.gridLotMinQuantity:
            terminate(f"Please specify {LIConfigKey.gridLotMinQuantity} since maxHolding={self.investAmount.maxHolding}!")
        if self.investAmount.maxCapital and not self.gridLotMinQuantity:
            terminate(f"Please specify {LIConfigKey.gridLotMinQuantity} since maxCapital={self.investAmount.maxCapital}!")
        if isNotLiveMode() and self.gridInitializeSession is None:
            terminate(f"Please specify {LIConfigKey.gridInitializeSession} explicitly for backtest mode!")

        # Verify grid settings' integrity upon grid mode
        if self.gridBaselinePrice:
            if self.gridLotLevelPercent:
                log(f"Please note {LIConfigKey.gridBaselinePrice} can only apply to {LIConfigKey.gridLotLevelAmount}!")
            if self.liquidateOnTakeProfitPercent:
                log(f"Please note {LIConfigKey.gridBaselinePrice} can only apply to {LIConfigKey.liquidateOnTakeProfitPercent}!")
            if self.liquidateOnStopLossPercent:
                log(f"Please note {LIConfigKey.gridBaselinePrice} can only apply to {LIConfigKey.liquidateOnStopLossPercent}!")
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
            if not (self.gridUseTradeInsight or self.gridLimitStartPrices or
                    self.gridFixedStartPrices or self.gridResetStartPrices or self.gridBandingStartPrices):
                terminate(f"Please specify one of {LIConfigKey.gridUseTradeInsight}, {LIConfigKey.gridLimitStartPrices}, {LIConfigKey.gridFixedStartPrices}, "
                          f"{LIConfigKey.gridResetStartPrices} or {LIConfigKey.gridBandingStartPrices}!")
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
        # Not to liquidate in position manager, will be taken care in this strategy itself!
        self.positionManager.delegateLiquidateRemovedSecurity = True
        self.canonicalSymbol = self.positionManager.getCanonicalSymbol()

        self.gridHeikinAshies: list[HeikinAshi] = []
        if self.gridHeikinAshiPlies:
            for n in range(self.gridHeikinAshiPlies):
                heikinAshi = HeikinAshi(str(n))
                heikinAshi.updated += self.onHeikinAshiUpdated  # Call back to update other indicators
                self.gridHeikinAshies.append(heikinAshi)
        self.bollingerBandsIndicator: LIBollingerBandsIndicator = None
        if self.bollingerBandsParams:
            self.bollingerBandsIndicator = self.getBollingerBandsIndicator(self.signalSymbolMonitor, self.positionManager)
            self.bollingerBandsIndicator.subscribeTradeInsight(self)
        self.stochasticComboIndicator: LIStochasticComboIndicator = None
        if self.stochasticComboParams:
            self.stochasticComboIndicator = self.getStochasticComboIndicator(self.signalSymbolMonitor, self.positionManager)
            self.stochasticComboIndicator.subscribeTradeInsight(self)
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
            getAlgo().SetTradeBuilder(TradeBuilder(FillGroupingMethod.FillToFill, FillMatchingMethod.FIFO))
        elif self.isContrarianMode():
            getAlgo().SetTradeBuilder(TradeBuilder(FillGroupingMethod.FillToFill, FillMatchingMethod.LIFO))

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

        self.reachedOpenPrice = False
        self.liquidatedAlready = False
        self.liquidateByTrailingProfit = 0.0  # Tracking trailing stop profit price/amount/percent for liquidation
        self.overallMaxProfitLoss = (0.0, 0.0)  # Tracking overall max/min profit/loss across multiple sessions

        self.closedTradesCount = 0
        self.stoppedLossPrices = {}  # NOT exceed this red/bottom line!
        self.realizedProfitLoss = 0.0
        self.pauseTradingTillTime = None

        # Dollar-Cost Averaging (DCA)
        self.dcaMaxStartPrice = 0
        self.dcaHoldingQuantity = 0
        self.dcaLastInvestedDate: datetime = None

        # Bollinger Bands Trading
        self.startBandName = None
        self.tradingTierName = None

        self.accruedFees: float = 0.0
        self.openOrderTicket: OrderTicket = None
        self.closeOrderTicket: OrderTicket = None
        self.avgFilledOpenPrice = None
        self.trailingStopPrice = None
        self.closeOrderUpdatedTimes = 0

    def tradeBothSides(self) -> bool:
        return self.gridLongLots and self.gridShortLots

    def isBoostingMode(self):
        return self.gridMode == LIGridMode.BOOSTING

    def isMomentumMode(self):
        return self.gridMode == LIGridMode.MOMENTUM

    def isContrarianMode(self):
        """BuyAndHold mode will buy the dip, it's the contrarian mode's long side behavior"""
        return self.gridMode == LIGridMode.CONTRARIAN or self.gridMode == LIGridMode.BUYANDHOLD

    def isBuyAndHoldMode(self):
        return self.gridMode == LIGridMode.BUYANDHOLD

    def getCounterpartMode(self):
        if self.gridMode == LIGridMode.MOMENTUM:
            return LIGridMode.CONTRARIAN
        elif self.gridMode == LIGridMode.CONTRARIAN:
            return LIGridMode.MOMENTUM
        elif self.gridMode == LIGridMode.BUYANDHOLD:
            return LIGridMode.BUYANDHOLD
        else:
            terminate(f"Not able to reverse the {LIConfigKey.gridMode}={self.gridMode}")

    def getTradeInsight(self):
        if self.stochasticComboIndicator:
            return self.stochasticComboIndicator.getTradeInsight()
        if self.bollingerBandsIndicator:
            return self.bollingerBandsIndicator.getTradeInsight()
        else:
            return super().getTradeInsight()

    def getHedgeInsightIndicator(self, securityMonitor: LISecurityMonitor, positionManager: LIPositionManager) -> LIInsightIndicator:
        symbolKey = securityMonitor.getSymbolKey()
        insightIndicator = self.insightIndicators.get(symbolKey)
        if insightIndicator is None:
            insightIndicator = LIMACDTrendFollowingIndicator(securityMonitor, positionManager, self.mainChart, self.configs)
            self.insightIndicators[symbolKey] = insightIndicator
        return insightIndicator

    def getBollingerBandsIndicator(self, securityMonitor: LISecurityMonitor, positionManager: LIPositionManager) -> LIInsightIndicator:
        symbolKey = securityMonitor.getSymbolKey()
        insightIndicator = self.insightIndicators.get(symbolKey)
        if insightIndicator is None:
            insightIndicator = LIBollingerBandsIndicator(securityMonitor, positionManager, self.mainChart, self.configs)
            self.insightIndicators[symbolKey] = insightIndicator
        return insightIndicator

    def getStochasticComboIndicator(self, securityMonitor: LISecurityMonitor, positionManager: LIPositionManager) -> LIInsightIndicator:
        symbolKey = securityMonitor.getSymbolKey()
        insightIndicator = self.insightIndicators.get(symbolKey)
        if insightIndicator is None:
            insightIndicator = LIStochasticComboIndicator(securityMonitor, positionManager, self.mainChart, self.configs)
            self.insightIndicators[symbolKey] = insightIndicator
        return insightIndicator

    def getTierFactorIndex(self):
        tierIndex = int(self.tradingTierName.split("-")[1][1:])
        bandCounts = self.bollingerBandsIndicator.countBands()
        tierFactorIndex = (bandCounts[1] - tierIndex) if ("upper" in self.tradingTierName) else (bandCounts[0] - bandCounts[1] + tierIndex)
        return tierFactorIndex

    @deprecated(reason="Use cancelActiveOrders() and resubmit order tickets instead.")
    def assignOpenOrderTickets(self):
        """
        Detect all active (open/close) order tickets and assign to proper trading grid lots!
        Not been used as the open order tickets could be stale and status unknown!
        """
        if self.positionManager.getInvestedQuantity() > 0:  # The long side
            orderTickets.sort(key=lambda x: x.Get(OrderField.LimitPrice), reverse=True)
            for orderTicket in orderTickets:
                assignedLot = False
                tradingLot = self.startLot.nextLot
                while tradingLot:
                    if tradingLot.isLongLot() and not tradingLot.hasOrderTickets():
                        if orderTicket.Quantity > 0:  # An opening order
                            tradingLot.openOrderTicket = orderTicket
                            assignedLot = True
                            break
                        elif orderTicket.Quantity < 0:  # A closing order
                            tradingLot.filledOpenQuantity = -orderTicket.Quantity
                            tradingLot.closeOrderTicket = orderTicket
                            assignedLot = True
                            break
                    tradingLot = tradingLot.nextLot
                if not assignedLot:
                    tagLog = f"Cancel an order as failed to assign to a lot: {orderTicket}."
                    self.positionManager.cancelOrder(orderTicket, tagLog)
        elif self.positionManager.getInvestedQuantity() < 0:  # The short side
            orderTickets.sort(key=lambda x: x.Get(OrderField.LimitPrice), reverse=False)
            for orderTicket in orderTickets:
                assignedLot = False
                tradingLot = self.startLot.prevLot
                while tradingLot:
                    if tradingLot.isShortLot() and not tradingLot.hasOrderTickets():
                        if orderTicket.Quantity < 0:  # A opening order
                            tradingLot.openOrderTicket = orderTicket
                            assignedLot = True
                            break
                        elif orderTicket.Quantity > 0:  # A closing order
                            tradingLot.filledOpenQuantity = -orderTicket.Quantity
                            tradingLot.closeOrderTicket = orderTicket
                            assignedLot = True
                            break
                    tradingLot = tradingLot.prevLot
                if not assignedLot:
                    tagLog = f"Cancel an order as failed to assign to a lot: {orderTicket}."
                    self.positionManager.cancelOrder(orderTicket, tagLog)

    def adjustGridHedgeLots(self, lots):
        if lots == 0:
            self.startLot.nextLot = None
            self.startLot.prevLot = None
        if lots > 0:
            while len(self.getLongLots()) < lots:
                self.addLastLongLot()
            while len(self.getLongLots()) > lots:
                self.dropLastLongLot().resetTradingLot(reason="Drop last long lot")
        if lots < 0:
            while len(self.getShortLots()) < abs(lots):
                self.addLastShortLot()
            while len(self.getShortLots()) > abs(lots):
                self.dropLastShortLot().resetTradingLot(reason="Drop last short lot")
        self.resetGridLotIds()  # Set proper sequential ids

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

        # Migrate metadata if necessary, comment out once migrated!
        # if not self.gridInitializeSession:
        #     if not self.gridMetadata:
        #         log(f"{self.getSymbolAlias()}: Migrating grid metadata...")
        #         gridMetadataKey = self.tradeSymbolStr + "/gridMetadata"
        #         self.gridMetadata = readMetadata(gridMetadataKey, "dict", default={})
        #         self.gridMetadata[LIMetadataKey.version] = LIGlobal.latestVersion
        #         saveMetadata(self.gridMetadataKey, self.gridMetadata, logging=True)
        #         deleteMetadata(gridMetadataKey, logging=True)
        #     if not self.gridLotsMetadata:
        #         log(f"{self.getSymbolAlias()}: Migrating grid lots metadata...")
        #         gridLotsMetadataKey = self.tradeSymbolStr + "/gridLotsMetadata"
        #         self.gridLotsMetadata = readMetadata(gridLotsMetadataKey, "dict", default={})
        #         saveMetadata(self.gridLotsMetadataKey, self.gridLotsMetadata, logging=True)
        #         deleteMetadata(gridLotsMetadataKey, logging=True)
        #     checkMetadataVersion(self.gridMetadata)

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
        if self.stochasticComboIndicator:
            self.gridMetadata[LIMetadataKey.tradeInsight] = self.stochasticComboIndicator.getTradeInsight().toMetadata()
        if self.liquidateByTrailingProfitPercent:
            self.gridMetadata[LIMetadataKey.liquidateByTrailingProfit] = self.liquidateByTrailingProfit
        if self.gridFixedOpenFromPrices or self.gridBandingOpenFromPrices:
            self.gridMetadata[LIMetadataKey.openFromPrices] = self.gridOpenFromPrices
            self.gridMetadata[LIMetadataKey.reachedOpenPrice] = self.reachedOpenPrice
        self.gridMetadata[LIMetadataKey.pauseTradingTillTime] = self.pauseTradingTillTime.strftime(
            LIGlobal.timestampFormat) if self.pauseTradingTillTime else None
        # Reserve current option contract identifier for restart/reboot/resume
        if self.positionManager.getContract() and isOption(self.getSymbol().SecurityType):
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
        self.stoppedLossPrices = self.gridMetadata.get(LIMetadataKey.stoppedLossPrices, 0.0)
        self.closedTradesCount = self.gridMetadata.get(LIMetadataKey.closedTradesCount, 0)
        self.realizedProfitLoss = self.gridMetadata.get(LIMetadataKey.realizedProfitLoss, 0.0)
        self.rolloverProfitLoss = self.gridMetadata.get(LIMetadataKey.rolloverProfitLoss, 0.0)
        self.overallMaxProfitLoss = self.gridMetadata.get(LIMetadataKey.overallMaxProfitLoss, (0.0, 0.0))
        if self.isBuyAndHoldMode():
            self.dcaMaxStartPrice = self.gridMetadata.get(LIMetadataKey.dcaMaxStartPrice, 0)
            self.dcaHoldingQuantity = self.gridMetadata.get(LIMetadataKey.dcaHoldingQuantity, 0)
            self.dcaLastInvestedDate = self.gridMetadata.get(LIMetadataKey.dcaLastInvestedDate, None)
            self.dcaLastInvestedDate = datetime.strptime(self.dcaLastInvestedDate, LIGlobal.timestampFormat) if self.dcaLastInvestedDate else getAlgo().Time
        if self.bollingerBandsIndicator:
            self.startBandName = self.gridMetadata.get(LIMetadataKey.startBandName, None)
            self.tradingTierName = self.gridMetadata.get(LIMetadataKey.tradingTierName, None)
            self.bollingerBandsIndicator.resetStartBand(self.startBandName)
        if self.stochasticComboIndicator:
            self.stochasticComboIndicator.setTradeInsight(LITradeInsight.fromMetadata(self.gridMetadata.get(LIMetadataKey.tradeInsight, None)))
        if self.liquidateByTrailingProfitPercent:
            self.liquidateByTrailingProfit = self.gridMetadata.get(LIMetadataKey.liquidateByTrailingProfit, 0.0)
        if self.gridFixedOpenFromPrices or self.gridBandingOpenFromPrices:
            self.gridOpenFromPrices = self.gridMetadata.get(LIMetadataKey.openFromPrices, {})
            self.reachedOpenPrice = self.gridMetadata.get(LIMetadataKey.reachedOpenPrice, False)
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
            getAlgo().Quit("Quit algorithm on RESET LOTS METADATA!")
        else:
            notify(f"{self.getNotifyPrefix()}: Applied the settings: {settings}!")

    def resetGridStartPrices(self, startPrices=None, emptyStartPrices=False, emptyOpenFromPrices=False):
        if emptyStartPrices:
            self.gridStartPrices = {}
        if emptyOpenFromPrices:
            self.gridOpenFromPrices = {}
        if startPrices:
            self.gridStartPrices |= startPrices  # Merge start prices as which could be partial!
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
            return  # Abort

        if self.gridNoMoreOpenOrders:
            log(f"{self.getSymbolAlias()}: Abort placing open order ticket as {LIConfigKey.gridNoMoreOpenOrders}={self.gridNoMoreOpenOrders}", self.verbose)
            return False  # Abort, no more open orders!

        if not self.positionManager.isExchangeOpen():
            return  # Abort, wait for market open!

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
        algoTime = bar.EndTime if bar else getAlgo().Time
        if isActiveTradingTime(algoTime) and (self.getInvestedQuantity() == 0 or (self.dcaLastInvestedDate + self.getPeriodicityTimedelta()) < algoTime):
            targetQuantity = self.dcaInvestCapital / self.getMarketPrice(bar) if self.dcaInvestCapital else self.dcaInvestQuantity
            targetQuantity = self.positionManager.roundSecuritySize(targetQuantity)
            tradeOrder = LITradeOrder(quantity=targetQuantity)
            tradeInsight = LITradeInsight(signalType=LISignalType.LONG, targetPrice=self.getMarketPrice(bar), tradeOrderSet={tradeOrder})
            if self.positionManager.onEmitTradeInsight(tradeInsight):
                self.dcaLastInvestedDate = algoTime
                # Fulfill a regular investment and continue
                self.dcaHoldingQuantity = self.getInvestedQuantity() - self.getOpeningQuantity()
                self.storeGridMetadata(logging=True)
                dcaInvestMsg = f"dcaInvestCapital={self.dcaInvestCapital}" if self.dcaInvestCapital else f"dcaInvestQuantity={self.dcaInvestQuantity}"
                notify(f"{self.getNotifyPrefix()}: Fulfilled a regular investment: "
                       f"marketPrice={self.getMarketPrice(bar)}, targetQuantity={targetQuantity}, openingQuantity={self.getOpeningQuantity()}, "
                       f"{dcaInvestMsg}, dcaLastInvestedDate={printFullTime(self.dcaLastInvestedDate)}, "
                       f"dcaHoldingQuantity={self.dcaHoldingQuantity}")
                # Fulfill a regular investment and restart session
                # self.dcaHoldingQuantity = self.getInvestedQuantity()
                # dcaInvestMsg = f"dcaInvestCapital={self.dcaInvestCapital}" if self.dcaInvestCapital else f"dcaInvestQuantity={self.dcaInvestQuantity}"
                # notify(f"{self.getNotifyPrefix()}: Fulfilled a regular investment: "
                #        f"marketPrice={self.getMarketPrice(bar)}, targetQuantity={targetQuantity}, openingQuantity={self.getOpeningQuantity()}, "
                #        f"{dcaInvestMsg}, dcaLastInvestedDate={printFullTime(self.dcaLastInvestedDate)}, "
                #        f"dcaHoldingQuantity={self.dcaHoldingQuantity}. And restart grid session.")
                # self.restartGridSession()

    def monitorRiskManagement(self):
        if not self.riskProposeHedgeInsights:
            return  # Abort as not enabled
        if self.tradeSecurityType == SecurityType.FUTURE:
            tradeSymbol = self.getTradeSecurity().Symbol
            if self.securityMonitor.isContractExpired(expiryDays=self.riskHedgeOptionExpiryDays):
                futures = getAlgo().FutureChainProvider.GetFutureContractList(tradeSymbol.Canonical, getAlgo().Time)
                tradeSymbol = sorted([x for x in futures if isExpiredAfterDays(x.ID.Date, self.riskHedgeOptionExpiryDays)], key=lambda x: x.ID.Date)[0]
                log(f"{self.getSymbolAlias()}: Picked the hedge future contract {cleanSymbolValue(tradeSymbol)} expired after {self.riskHedgeOptionExpiryDays} days")
            options = getAlgo().OptionChainProvider.GetOptionContractList(tradeSymbol, getAlgo().Time)
            if options and self.isContrarianMode():
                optionSymbols = []
                if self.gridLongLots:
                    # Take the middle of stop loss price as the init strike price
                    stopLossPrice = self.getFirstLongLot().getStopLossPrice()[0]
                    stopLossPrice += self.getLastLongLot().getStopLossPrice()[0]
                    stopLossPrice = self.positionManager.roundSecurityPrice(stopLossPrice / 2)
                    optionSymbols += sorted(
                        [x for x in options if
                         x.ID.OptionStyle == OptionStyle.American and x.ID.OptionRight == OptionRight.Put and x.ID.StrikePrice <= stopLossPrice],
                        key=lambda x: x.ID.StrikePrice, reverse=True)[0:5]
                if self.gridShortLots:
                    # Take the middle of stop loss price as the init strike price
                    stopLossPrice = self.getFirstShortLot().getStopLossPrice()[0]
                    stopLossPrice += self.getLastShortLot().getStopLossPrice()[0]
                    stopLossPrice = self.positionManager.roundSecurityPrice(stopLossPrice / 2)
                    optionSymbols += sorted(
                        [x for x in options if
                         x.ID.OptionStyle == OptionStyle.American and x.ID.OptionRight == OptionRight.Call and x.ID.StrikePrice >= stopLossPrice],
                        key=lambda x: x.ID.StrikePrice, reverse=False)[0:5]
                optionContracts = []
                for optionSymbol in optionSymbols:
                    optionContracts.append(self.securityMonitor.addFutureOptionContract(optionSymbol))
                # Warm up the open interest cache data
                history = getAlgo().History(OpenInterest, optionSymbols, 10, resolution=Resolution.Daily)
                if len(history.index) == 0 or 0 in history.values:
                    alert(f"{self.getNotifyPrefix()}: Open interest history request got empty values!")
                if optionContracts:
                    proposal = f"Propose to buy some of following future options: \n"
                    for optionContract in optionContracts:
                        proposal += f"{printOptionContract(optionContract)}\n"
                    notify(f"{self.getNotifyPrefix()}: {proposal}")
