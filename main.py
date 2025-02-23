# region imports
from core.LIAlgorithm import *


# endregion

class LifelongInvestorMain(LIAlgorithm):

    def Initialize(self):
        super().Initialize()
        setLogSize(500)  # Only for backtesting
        setAlgoName("Backtest")  # Invest account name
        addNotifySetting(LINotifyType.TELEGRAM, "-913280749")
        addAlertSetting(LINotifyType.EMAIL, "lifelonginvestorllc@gmail.com")
        # sendDailyMetadataAlert()  # Enable to send daily metadata via alert
        # liquidateAndStopTrading() # Liquidate all strategies in emergency!
        # migrateProjectCloudId(15964868)  # Migrate metadata from this project

        '''Some functions to run in backtest main.py only!'''
        # Use this to purge some stale/expired metadata if exceeded limit!
        # purgeExpiredMetadata(r"(?i)^liats/.*$", justDryRun=True)
        # purgeExpiredMetadata(r"(?i)^.+/gridLotsMetadata/-?\d+.*$", justDryRun=False)
        # purgeExpiredMetadata(r"(?i)^.+/gridTradingCache.*$", justDryRun=False)
        if self.LiveMode:
            terminate(f"This project is for backtest only!")

        # self.futureGridTrading_Euro_Momentum()
        # self.futureGridTrading_Euro_Contrarian()
        # self.futureGridTrading_Euro_Contrarian_Scalp()
        # self.futureGridTrading_10YNote_Contrarian()
        # self.futureGridTrading_10YNote_Momentum()
        # self.futureGridTrading_Nasdaq_Momentum()
        # self.futureGridTrading_Nasdaq_Momentum_NQ()
        # self.futureGridTrading_Nasdaq_Combo_Hedge()
        # self.futureGridTrading_Nasdaq_Contrarian_Long()
        self.futureGridTrading_Nasdaq_Contrarian_Short()
        # self.futureGridTrading_Oil_Momentum()
        # self.futureGridTrading_Oil_Contrarian_Hour()
        # self.futureGridTrading_Oil_Contrarian_5Mins()

        # self.equityManualTrading()
        # self.futureGridTrading_Nasdaq_Scalp()
        # self.equityGridTrading_SPY_DCA()
        # self.equityGridTrading_IXN_DCA()

        # self.futureGridTrading_Volatility()
        # self.futureGridTrading_Volatility_Trail()
        # self.futureGridTrading_Oil_Hedge()
        # self.futureGridTrading_Oil_Trend()
        # self.futureGridTrading_Oil_Scalp()
        # self.futureGridTrading_Gas_Trend()
        # self.futureGridTrading_Gas_Scalp()
        # self.futureGridTrading_Gold_Trail()
        # self.futureGridTrading_Dow()
        # self.futureGridTrading_Dow_Hedge()
        # self.futureGridTrading_SP500_Micro()
        # self.futureGridTrading_SP500_Short()
        # self.futureGridTrading_SP500_Long()
        # self.futureGridTrading_SP500_Hedge()
        # self.futureGridTrading_SP500_Trail()
        # self.futureGridTrading_Nasdaq()
        # self.futureGridTrading_Nasdaq_Micro()
        # self.futureGridTrading_Nasdaq_Hedge()
        # self.futureGridTrading_Nasdaq_Trail()  # Regression test case
        # self.futureGridTrading_Nasdaq_Boost()
        # self.futureGridTrading_Nasdaq_Trend()
        # self.futureGridTrading_Nasdaq_Scalp()
        # self.futureGridTrading_Nasdaq_Scalp_NQ()  # Regression test case
        # self.futureGridTrading_10YNote_Trail_Short()
        # self.futureGridTrading_10YNote_Scalp_ZN()
        # self.futureGridTrading_Nasdaq_Scalp_Long()
        # self.futureGridTrading_Nasdaq_Turbo()
        # self.futureGridTrading_USD_Trail()
        # self.futureGridTrading_Euro_Trend()

        # self.equityGridTrading_SPY_DCA()
        # self.equityGridTrading_USTech_3X()
        # self.equityGridTrading_Global_Stock()
        # self.equityGridTrading_ChipTech_3X()

        # self.optionGridTrading_QQQ_Trend()
        # self.optionGridTrading_AMD_Trend()

        # self.equitySwingTrading_TQQQ()

    def equityManualTrading(self):
        self.SetCash(1_000_000)
        # Test spreadsheet (6/-0.24%/-2.6%)
        self.SetStartDate(date(2024, 5, 15))
        self.SetEndDate(date(2024, 5, 25))

        configs = {
            LIConfigKey.monitorPeriod: 60,
            LIConfigKey.extendedMarketHours: False,
            LIConfigKey.extendDataBarStream: False,
        }

        investAmount = LIInvestAmount(maxHolding=1)
        self.liStrategies.append(LIEquityManualTrading("SPY", investAmount, **configs))

    def futureGridTrading_Volatility(self):
        self.SetCash(300_000)
        self.SetStartDate(date(2023, 7, 15))
        self.SetEndDate(date(2023, 8, 21))

        configs = {
            LIConfigKey.aliasName: "VIX",
            LIConfigKey.monitorPeriod: 5,  # 5 mins
            LIConfigKey.extendedMarketHours: True,
            LIConfigKey.futurePeriodDays: 35,
            LIConfigKey.futureRolloverDays: 1,
            LIConfigKey.extendDataBarStream: True,  # No data bar with VIX!
            LIConfigKey.gridLongLots: 10,
            LIConfigKey.gridLotLevelPercent: 1.5,  # 1.5 -> 1.85 -> 2.5
            LIConfigKey.gridLotLevelAugment: 0.075,  # 0.075 -> 0.0875
            LIConfigKey.gridLotTakeProfitFactor: 6.0,
            # LIConfigKey.gridMaintainOpenOrders: 5,
            # LIConfigKey.liquidateOnStopLossPercent: 10,
            # LIConfigKey.gridRolloverQuantities: [0, 0],
            # LIConfigKey.gridLimitStartPrices: {LIGridSide.BTD: 18.00},
            LIConfigKey.gridFixedStartPrices: {LIGridSide.BTD: 18.00},
            # LIConfigKey.gridResetStartPrices: {LIGridSide.BTD: 17.25}
            # LIConfigKey.gridMaintainOpenOrders: 5,
            # LIConfigKey.gridInitializeSession: True,  # Be careful! (mostly used in backtest)
        }
        investAmount = LIInvestAmount(lotQuantity=2)
        self.liStrategies.append(LIFutureGridTradingContrarian(Futures.Indices.VIX, investAmount, **configs))

    def futureGridTrading_Volatility_Trail(self):
        self.SetCash(200_000)
        # self.SetStartDate(date(2023, 8, 17))
        # self.SetEndDate(date(2023, 10, 17))
        # self.SetEndDate(date(2023, 10, 23))
        # self.SetEndDate(date(2023, 11, 17))
        # 132/22.91%
        self.SetStartDate(date(2024, 4, 1))
        self.SetEndDate(date(2024, 11, 1))
        self.SetStartDate(date(2024, 7, 15))
        self.SetEndDate(date(2024, 8, 15))

        configs = {
            LIConfigKey.aliasName: "VIXTrail",
            LIConfigKey.monitorPeriod: 5,
            # LIConfigKey.futurePeriodDays: 35,
            # LIConfigKey.futureRolloverDays: 1,
            LIConfigKey.futurePeriodDays: 65,
            LIConfigKey.futureRolloverDays: 30,
            # LIConfigKey.fetchHistoryBarData: False,
            LIConfigKey.closeWithStopOrderType: True,
            LIConfigKey.liquidateOnStopLossAmount: 100_000,
            # LIConfigKey.submitTrailingStopOrder: True,
            # LIConfigKey.updateTrailingStopPrice: False,
            # LIConfigKey.gridRetainOpenedLots: 1,
            LIConfigKey.gridLongLots: 8,
            LIConfigKey.gridShortLots: 8,
            # LIConfigKey.gridLotLevelPercent: 1.5,
            # LIConfigKey.gridLotLevelAugment: 0.075,
            # LIConfigKey.gridLotLevelPercent: 1.5 * 2,
            # LIConfigKey.gridLotLevelAugment: 0.075 * 2,
            # LIConfigKey.gridLotLevelPercent: 1.5 * 3,
            # LIConfigKey.gridLotLevelAugment: 0.075 * 3,
            LIConfigKey.gridLotLevelPercent: 5,
            LIConfigKey.gridLotLevelAugment: 0.25,
            LIConfigKey.gridLotStopLossFactor: 20,
            LIConfigKey.gridLotStopProfitFactors: (0.5, 1),
            # LIConfigKey.gridFixedStartPrices: {LIGridSide.BTD: 16.50, LIGridSide.STU: 16.50},
            # LIConfigKey.gridFixedStartPrices: {LIGridSide.BTD: 17.50, LIGridSide.STU: 17.50},
            LIConfigKey.gridFixedStartPrices: {LIGridSide.BTD: 20, LIGridSide.STU: 20},
            # LIConfigKey.gridFixedOpenFromPrices: {LIGridSide.BTD: 15, LIGridSide.STU: 20},
            # LIConfigKey.gridFixedOpenFromPrices: {LIGridSide.BTD: 12, LIGridSide.STU: 25},
            LIConfigKey.gridFixedOpenFromPrices: {LIGridSide.BTD: 14, LIGridSide.STU: 30},
            LIConfigKey.gridInitializeSession: True,  # Be careful! (mostly used in backtest)
        }
        investAmount = LIInvestAmount(lotQuantity=1)
        self.liStrategies.append(LIFutureGridTradingContrarian(Futures.Indices.VIX, investAmount, **configs))

    def futureGridTrading_Oil_Momentum(self):
        self.SetCash(200_000)
        amplifier = 1  # Amplify invest amount by n times!

        # Reached upper band with raising price:
        # Fixed open from prices: (163/162.83%/-16.30%)
        # Dynamic open from prices: (149/114.18%/-23.40%)
        self.SetStartDate(date(2022, 2, 18))
        self.SetEndDate(date(2022, 4, 18))
        # self.SetStartDate(date(2024, 9, 1))
        # self.SetEndDate(date(2024, 12, 31))

        configs = {
            LIConfigKey.aliasName: "OilTrend",
            LIConfigKey.monitorPeriod: 1,
            LIConfigKey.resolution: LIResolution.HOUR,
            # Adjust it dynamically based on current market trend/volatility and paired contrarian strategy's profit loss!
            LIConfigKey.liquidateOnTakeProfitAmounts: {LIGridSide.BTU: 35_000 * amplifier, LIGridSide.STD: 35_000 * amplifier},
            LIConfigKey.liquidateByTrailingProfitPercent: 15,
            # LIConfigKey.liquidateWithStopOrderType: True,
            LIConfigKey.gridLongLots: 30,
            LIConfigKey.gridShortLots: 30,
            LIConfigKey.gridLotLevelPercent: 0.75,
            LIConfigKey.gridLotStopLossFactor: 30,
            LIConfigKey.gridLotTakeProfitFactor: 25,
            LIConfigKey.gridLotPauseAfterProfit: False,
            # LIConfigKey.gridFixedOpenFromPrices: {LIGridSide.STD: 40, LIGridSide.BTU: 100},
            LIConfigKey.gridBandingOpenFromPrices: True,
            LIConfigKey.bollingerBandsParams: [(365, 2)],
            LIConfigKey.gridInitializeSession: True,  # Be careful!
        }

        # # Reached upper and lower band (37/36.16%/-??%)
        # self.SetStartDate(date(2024, 3, 25))
        # self.SetEndDate(date(2024, 6, 25))
        # configs = {
        #     LIConfigKey.aliasName: "OilTrend",
        #     LIConfigKey.monitorPeriod: 1,
        #     LIConfigKey.resolution: LIResolution.HOUR,
        #     # Adjust it dynamically based on current market trend/volatility and paired contrarian strategy's profit loss!
        #     LIConfigKey.liquidateOnTakeProfitAmounts: {LIGridSide.BTU: 35_000 * amplifier, LIGridSide.STD: 35_000 * amplifier},
        #     # LIConfigKey.liquidateByTrailingProfitPercent: 25,
        #     LIConfigKey.gridLongLots: 30,
        #     LIConfigKey.gridShortLots: 30,
        #     LIConfigKey.gridLotLevelPercent: 0.75,
        #     LIConfigKey.gridLotStopLossFactor: 30,
        #     LIConfigKey.gridLotTakeProfitFactor: 25,
        #     LIConfigKey.gridLotPauseAfterProfit: False,
        #     LIConfigKey.gridFixedOpenFromPrices: {LIGridSide.STD: 74, LIGridSide.BTU: 84},
        #     LIConfigKey.gridInitializeSession: True,  # Be careful!
        # }

        # # Reached lower band twice (33/22.42%/-??%)
        # self.SetStartDate(date(2024, 9, 1))
        # self.SetEndDate(date(2024, 11, 1))
        # configs = {
        #     LIConfigKey.aliasName: "OilTrend",
        #     LIConfigKey.monitorPeriod: 1,
        #     LIConfigKey.resolution: LIResolution.HOUR,
        #     # Adjust it dynamically based on current market trend/volatility and paired contrarian strategy's profit loss!
        #     LIConfigKey.liquidateOnTakeProfitAmounts: {LIGridSide.BTU: 35_000 * amplifier, LIGridSide.STD: 35_000 * amplifier},
        #     # LIConfigKey.liquidateByTrailingProfitPercent: 25,
        #     LIConfigKey.gridLongLots: 30,
        #     LIConfigKey.gridShortLots: 30,
        #     LIConfigKey.gridLotLevelPercent: 0.75,
        #     LIConfigKey.gridLotStopLossFactor: 30,
        #     LIConfigKey.gridLotTakeProfitFactor: 25,
        #     LIConfigKey.gridLotPauseAfterProfit: False,
        #     LIConfigKey.gridFixedOpenFromPrices: {LIGridSide.STD: 67, LIGridSide.BTU: 89},
        #     LIConfigKey.gridInitializeSession: True,  # Be careful!
        # }

        investAmount = LIInvestAmount(lotQuantity=1 * amplifier)
        self.liStrategies.append(LIFutureGridTradingMomentum(Futures.Energies.CrudeOilWTI, investAmount, **configs))

    def futureGridTrading_Oil_Contrarian_Hour(self):
        self.SetCash(300_000)
        # Up/Down/Up bull Trend (49/45.10%):
        # self.SetStartDate(date(2023, 7, 28))
        # self.SetEndDate(date(2023, 9, 28))
        # Up/Down/Up bear Trend: 0 is better than 30
        # self.SetStartDate(date(2023, 9, 15))
        # self.SetEndDate(date(2023, 10, 15))
        # Up and down trend with stop limit:
        # Fixed open from price: (123/69.30%/-11.10%)
        # Dynamic open from price: (104/56.93%/-11.70%) -> (97/65.35%/-10.10%) -> (94/66.52%/-9.30%)
        self.SetStartDate(date(2024, 4, 1))
        self.SetEndDate(date(2024, 9, 1))
        # self.SetStartDate(date(2024, 3, 18))
        # The stop limit order is not working properly!
        # self.SetStartDate(date(2024, 11, 1))
        # self.SetEndDate(date(2024, 11, 15))
        # self.SetStartDate(date(2023, 7, 1))
        # self.SetEndDate(date(2023, 11, 1))
        # Stay low for a few months: (128/50.93%/-27.60%)
        # self.SetStartDate(date(2024, 9, 1))
        # self.SetEndDate(date(2024, 12, 31))
        # Two extremely rising spikes
        # self.SetStartDate(date(2021, 12, 20))
        # self.SetEndDate(date(2022, 4, 20))

        configs = {
            LIConfigKey.aliasName: "OilTrail",
            LIConfigKey.monitorPeriod: 1,
            LIConfigKey.resolution: LIResolution.HOUR,
            LIConfigKey.futurePeriodDays: 35,
            LIConfigKey.futureRolloverDays: 3,
            # LIConfigKey.verboseLogging: True,
            # LIConfigKey.signalSymbolStr: "USOIL",
            # LIConfigKey.signalSecurityType: SecurityType.Cfd,
            # LIConfigKey.futureRolloverDays: 5,
            # LIConfigKey.closeWithStopOrderType: True,
            # LIConfigKey.liquidateAndStopTrading: True,
            # LIConfigKey.liquidateOnReachedPrices: {LIGridSide.BTD: 76, LIGridSide.STU: 78},
            # Adjust it dynamically based on current market trend/volatility and momentum strategy's profit loss!
            LIConfigKey.liquidateOnTakeProfitAmount: 50_000,
            # LIConfigKey.liquidateByTrailingProfitPercent: 15,
            LIConfigKey.liquidateOnStopLossAmount: 100_000,
            # LIConfigKey.gridLotPauseAfterStopLoss: False,
            LIConfigKey.gridLongLots: 20,
            # LIConfigKey.gridLongLotsQty: [1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 3, 3, 3, 3, 3],
            LIConfigKey.gridShortLots: 20,
            # LIConfigKey.gridShortLotsQty: [1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 3, 3, 3, 3, 3],
            LIConfigKey.gridLotLevelPercent: 0.75,
            # LIConfigKey.gridLotLevelAugment: 0.025,
            LIConfigKey.gridLotStopLossFactor: 25,
            # LIConfigKey.gridLotMaxProfitFactor: 10,
            LIConfigKey.gridLotStopProfitFactors: (0.5, 2),
            # LIConfigKey.gridCloseCounterpartLots: False,
            # LIConfigKey.gridFixLeakingPositions: True,
            # 4/1/2024 - 9/1/2024
            # LIConfigKey.gridFixedStartPrices: {LIGridSide.BTD: 79, LIGridSide.STU: 79},
            # LIConfigKey.gridFixedOpenFromPrices: {LIGridSide.BTD: 74, LIGridSide.STU: 84},
            # 9/1/2024 - 12/1/2024
            # LIConfigKey.gridFixedStartPrices: {LIGridSide.BTD: 77, LIGridSide.STU: 77},
            # LIConfigKey.gridFixedOpenFromPrices: {LIGridSide.BTD: 72, LIGridSide.STU: 82},
            # LIConfigKey.gridFixedStartPrices: {LIGridSide.BTD: 76, LIGridSide.STU: 76},
            # LIConfigKey.gridFixedOpenFromPrices: {LIGridSide.BTD: 71, LIGridSide.STU: 81},
            LIConfigKey.gridBandingStartPrices: True,
            LIConfigKey.gridBandingOpenFromPrices: True,
            LIConfigKey.bollingerBandsParams: [(365, 1)],
            LIConfigKey.gridInitializeSession: True,
        }
        investAmount = LIInvestAmount(lotQuantity=1)
        self.liStrategies.append(LIFutureGridTradingContrarian(Futures.Energies.CrudeOilWTI, investAmount, **configs))

    def futureGridTrading_Oil_Contrarian_5Mins(self):
        self.SetCash(300_000)
        # Up/Down/Up bull Trend (49/45.10%):
        # self.SetStartDate(date(2023, 7, 28))
        # self.SetEndDate(date(2023, 9, 28))
        # Up/Down/Up bear Trend: 0 is better than 30
        # self.SetStartDate(date(2023, 9, 15))
        # self.SetEndDate(date(2023, 10, 15))
        # Up and down trend with stop limit:
        # Fixed open from price: (123/69.30%/-11.10%)
        # Dynamic open from price: (104/56.93%/-11.70%) -> (97/65.35%/-10.10%)
        self.SetStartDate(date(2024, 4, 1))
        self.SetEndDate(date(2024, 9, 1))
        # self.SetStartDate(date(2024, 3, 18))
        # The stop limit order is not working properly!
        # self.SetStartDate(date(2024, 11, 1))
        # self.SetEndDate(date(2024, 11, 15))
        # self.SetStartDate(date(2023, 7, 1))
        # self.SetEndDate(date(2023, 11, 1))
        # Stay low for a few months: (143/16.05%/-6.20%)
        # self.SetStartDate(date(2024, 10, 25))
        # self.SetEndDate(date(2024, 12, 31))
        # Trending from neutral to bullish
        self.SetStartDate(date(2024, 12, 1))
        self.SetEndDate(date(2025, 1, 20))
        # self.SetStartDate(date(2024, 12, 4))
        # self.SetEndDate(date(2024, 12, 15))
        # self.SetStartDate(date(2024, 12, 27))
        # self.SetEndDate(date(2025, 1, 7))
        # self.SetStartDate(date(2025, 1, 1))
        # self.SetEndDate(date(2025, 1, 4))

        configs = {
            LIConfigKey.aliasName: "OilTrail",
            LIConfigKey.monitorPeriod: 5,
            LIConfigKey.resolution: LIResolution.MINUTE,
            LIConfigKey.futurePeriodDays: 35,
            LIConfigKey.futureRolloverDays: 3,
            # LIConfigKey.verboseLogging: True,
            # LIConfigKey.signalSymbolStr: "USOIL",
            # LIConfigKey.signalSecurityType: SecurityType.Cfd,
            # LIConfigKey.futureRolloverDays: 5,
            # LIConfigKey.closeWithStopOrderType: True,
            # LIConfigKey.liquidateAndStopTrading: True,
            # LIConfigKey.liquidateOnReachedPrices: {LIGridSide.BTD: 76, LIGridSide.STU: 78},
            # Adjust it dynamically based on current market trend/volatility and momentum strategy's profit loss!
            LIConfigKey.liquidateLossAndRestartTrading: True,
            LIConfigKey.liquidateOnStopLossAmount: 50_000,
            LIConfigKey.liquidateOnTakeProfitAmount: 10_000,
            # LIConfigKey.liquidateByTrailingProfitPercent: 15,
            # LIConfigKey.gridLotPauseAfterStopLoss: False,
            LIConfigKey.gridLongLots: 10,
            LIConfigKey.gridShortLots: 10,
            LIConfigKey.gridLotLevelPercent: 0.5,
            LIConfigKey.gridLotStopLossFactor: 15,
            # LIConfigKey.gridLotMaxProfitFactor: 10,
            LIConfigKey.gridLotStopProfitFactors: (0.5, 2),
            # LIConfigKey.gridCloseCounterpartLots: False,
            # LIConfigKey.gridFixLeakingPositions: True,
            LIConfigKey.gridBandingStartPrices: True,
            LIConfigKey.gridBandingOpenFromPrices: True,
            LIConfigKey.gridFixedStartBandName: "band-#2-upper",  # (100/15.13%/-6.40%)
            # LIConfigKey.gridFixedStartBandName: "band-#0-middle",  # (101/-9.38%%/-25.10%)
            LIConfigKey.bollingerBandsParams: [(300, 1, LIResolution.HOUR), (300, 2, LIResolution.HOUR), (300, 3, LIResolution.HOUR)],
            # LIConfigKey.marketBiased: LIMarketBiased.NEUTRAL,
            LIConfigKey.gridInitializeSession: True,
        }
        investAmount = LIInvestAmount(lotQuantity=1)
        self.liStrategies.append(LIFutureGridTradingContrarian(Futures.Energies.CrudeOilWTI, investAmount, **configs))

    def futureGridTrading_Gas_Trail(self):
        self.SetCash(200_000)
        self.SetStartDate(date(2023, 8, 15))
        self.SetEndDate(date(2023, 10, 9))
        # self.SetStartDate(date(2023, 10, 10))
        # self.SetEndDate(date(2023, 11, 28))

        configs = {
            LIConfigKey.aliasName: "GasMain",
            LIConfigKey.monitorPeriod: 5,  # 5 mins
            LIConfigKey.plotDefaultChart: True,
            LIConfigKey.extendedMarketHours: True,
            LIConfigKey.futurePeriodDays: 35,
            LIConfigKey.futureRolloverDays: 2,
            LIConfigKey.disableBuyingPowerModel: True,
            # LIConfigKey.liquidateAndStopTrading: True,
            # LIConfigKey.gridNoMoreOpenOrders: False,
            # LIConfigKey.gridRetainOpenedLots: 5,
            LIConfigKey.gridLongLots: 18,
            LIConfigKey.gridLotLevelPercent: 1.5,
            LIConfigKey.gridLotLevelAugment: 0.035,
            LIConfigKey.gridLotStopLossFactor: 30,
            # LIConfigKey.gridLotMaxProfitFactor: 6,
            LIConfigKey.gridLotStopProfitFactors: (2, 2),
            LIConfigKey.closeWithStopOrderType: False,
            # LIConfigKey.liquidateOnStopLossPercent: 15,
            LIConfigKey.gridFixedStartPrices: {LIGridSide.BTD: 3.5},
            # LIConfigKey.gridResetStartPrices: {LIGridSide.BTD: 2.95},
            LIConfigKey.gridInitializeSession: True,  # Be careful! (mostly used in backtest)
        }
        investAmount = LIInvestAmount(lotQuantity=1)
        self.liStrategies.append(LIFutureGridTradingContrarian(Futures.Energies.NaturalGas, investAmount, **configs))

    def futureGridTrading_Oil_Trend(self):
        self.SetCash(200_000)
        # Up/Down/Up bull Trend:
        self.SetStartDate(date(2023, 7, 28))
        self.SetEndDate(date(2023, 9, 28))
        # Up/Down/Up bear Trend: 0 is better than 30
        # self.SetStartDate(date(2023, 9, 15))
        # self.SetEndDate(date(2023, 10, 15))

        self.SetStartDate(date(2024, 3, 7))
        self.SetEndDate(date(2024, 4, 7))

        configs = {
            LIConfigKey.aliasName: "OilTrend",
            LIConfigKey.plotDefaultChart: True,
            LIConfigKey.futurePeriodDays: 35,
            LIConfigKey.disableBuyingPowerModel: True,
            # LIConfigKey.liquidateAndStopTrading: True,
            # LIConfigKey.gridRetainOpenedLots: 3,
            LIConfigKey.gridLongLots: 10,
            LIConfigKey.gridShortLots: 10,
            LIConfigKey.gridLotLevelPercent: 0.75,
            # LIConfigKey.gridLotLevelAugment: 0.025,
            LIConfigKey.gridLotStopLossFactor: 1,
            LIConfigKey.gridLotTakeProfitFactor: 2,
            LIConfigKey.gridLotStopProfitFactors: (0.5, 2),
            # LIConfigKey.gridTransfer2Counterpart: False,
            # LIConfigKey.gridMaintainCloseOrders: 2,
            # LIConfigKey.closeWithStopOrderType: False,
            # LIConfigKey.gridFixedStartPrices: {LIGridSide.BTD: 80.00},
            # LIConfigKey.gridLimitStartPrices: {LIGridSide.BTD: 80.00},
            LIConfigKey.gridInitializeSession: True,
        }
        investAmount = LIInvestAmount(lotQuantity=5)
        self.liStrategies.append(LIFutureGridTradingMomentum(Futures.Energies.MicroCrudeOilWTI, investAmount, **configs))

    def futureGridTrading_Oil_Scalp(self):
        self.SetCash(200_000)
        self.SetStartDate(date(2024, 3, 7))
        self.SetEndDate(date(2024, 4, 7))

        configs = {
            LIConfigKey.aliasName: "OilScalp",
            LIConfigKey.monitorPeriod: 5,
            LIConfigKey.futurePeriodDays: 35,
            # LIConfigKey.futureRolloverDays: 5,
            # LIConfigKey.openWithStopOrderType: False,
            # LIConfigKey.closeWithStopOrderType: False,
            LIConfigKey.disableBuyingPowerModel: True,
            # LIConfigKey.liquidateAndStopTrading: True,
            LIConfigKey.gridLongLots: 10,
            # LIConfigKey.gridShortLots: 10,
            # LIConfigKey.gridInitOpenedLots: -1,
            # LIConfigKey.gridRetainOpenedLots: -1,
            LIConfigKey.gridLotLevelPercent: 0.65,
            LIConfigKey.gridLotStopLossFactor: 1,
            LIConfigKey.gridLotTakeProfitFactor: 2,
            LIConfigKey.gridLotStopProfitFactors: (0.5, 2),
            # LIConfigKey.gridBoostingKeepTrading: True,
            # LIConfigKey.gridBoostingTriggerAmount: 1,
            # LIConfigKey.gridBoostingMaxHoldQuantity: 20,
            # LIConfigKey.gridBoostingStopProfitAmounts: (0.5, 0.5),
            # LIConfigKey.liquidateOnTakeProfitAmount: 6_000,
            LIConfigKey.gridInitializeSession: True,  # Be careful!
        }
        investAmount = LIInvestAmount(lotQuantity=1)
        self.liStrategies.append(LIFutureGridTradingMomentum(Futures.Energies.CrudeOilWTI, investAmount, **configs))

    def futureGridTrading_Gas_Trend(self):
        self.SetCash(100_000)
        # Down Trend 199/59.01%(no stop profit)
        # self.SetStartDate(date(2023, 11, 12))
        # self.SetEndDate(date(2023, 12, 12))
        # Up Trend 306/59.89%
        # self.SetStartDate(date(2023, 12, 13))
        # self.SetEndDate(date(2024, 1, 12))
        # 2 Months long run! 454/139.94%(no stop profit)
        # self.SetStartDate(date(2023, 11, 12))
        # self.SetEndDate(date(2024, 1, 12))
        # Daily High Down/Up/Down/Up 103/1.97%(no stop profit)
        # Daily High Down/Up/Down/Up 89/11.17%(stopProfitFactor=1)
        # Daily High Down/Up/Down/Up 92/14.33%(stopProfitFactor=0.5)
        self.SetStartDate(date(2023, 12, 10))
        self.SetEndDate(date(2024, 1, 10))

        # self.SetStartDate(date(2024, 1, 10))
        # self.SetStartDate(date(2024, 2, 1))
        # self.SetEndDate(date(2024, 3, 15))

        configs = {
            LIConfigKey.aliasName: "GasTrend",
            LIConfigKey.monitorPeriod: 5,
            LIConfigKey.futurePeriodDays: 32,
            LIConfigKey.futureRolloverDays: 5,
            LIConfigKey.fetchHistoryBarData: False,
            # LIConfigKey.gridMaintainCloseOrders: 3,
            # LIConfigKey.openWithStopOrderType: True,
            # LIConfigKey.closeWithStopOrderType: True,
            LIConfigKey.disableBuyingPowerModel: True,
            # LIConfigKey.liquidateAndStopTrading: True,
            # LIConfigKey.liquidateOnTakeProfitAmount: 6_000,
            LIConfigKey.gridLongLots: 20,
            # LIConfigKey.gridShortLots: 20,
            # LIConfigKey.gridInitOpenedLots: 1,
            # LIConfigKey.gridRetainOpenedLots: -1,
            LIConfigKey.gridLotLevelPercent: 2,
            LIConfigKey.gridLotStopLossFactor: 1.5,
            LIConfigKey.gridLotTakeProfitFactor: 3,
            LIConfigKey.gridLotStopProfitFactors: (0.5, 2),
            # LIConfigKey.gridResetLotsMetadata: True,
            LIConfigKey.gridInitializeSession: True,  # Be careful!
        }
        investAmount = LIInvestAmount(lotQuantity=1)
        self.liStrategies.append(LIFutureGridTradingMomentum(Futures.Energies.NaturalGas, investAmount, **configs))

    def futureGridTrading_Gas_Scalp(self):
        self.SetCash(100_000)
        # Down Trend 199/59.01%(no stop profit)
        # self.SetStartDate(date(2023, 11, 12))
        # self.SetEndDate(date(2023, 12, 12))
        # Up Trend 306/59.89%
        # self.SetStartDate(date(2023, 12, 13))
        # self.SetEndDate(date(2024, 1, 12))
        # 2 Months long run! 454/139.94%(no stop profit)
        # self.SetStartDate(date(2023, 11, 12))
        # self.SetEndDate(date(2024, 1, 12))
        # Daily High Down/Up/Down/Up 103/1.97%(no stop profit)
        # Daily High Down/Up/Down/Up 89/11.17%(stopProfitFactor=1)
        # Daily High Down/Up/Down/Up 92/14.33%(stopProfitFactor=0.5)
        # self.SetStartDate(date(2024, 1, 9))
        # self.SetEndDate(date(2024, 1, 12))
        # Rollover in down trend
        self.SetStartDate(date(2024, 1, 25))
        self.SetEndDate(date(2024, 2, 10))

        configs = {
            LIConfigKey.aliasName: "GasScalp",
            LIConfigKey.monitorPeriod: 1,
            LIConfigKey.futurePeriodDays: 35,
            LIConfigKey.futureRolloverDays: 5,
            LIConfigKey.openWithStopOrderType: False,
            LIConfigKey.closeWithStopOrderType: False,
            LIConfigKey.disableBuyingPowerModel: True,
            # LIConfigKey.liquidateAndStopTrading: True,
            LIConfigKey.liquidateOnTakeProfitAmount: 6_000,
            LIConfigKey.gridLongLots: 6,
            LIConfigKey.gridShortLots: 6,
            # LIConfigKey.gridInitOpenedLots: -1,
            # LIConfigKey.gridRetainOpenedLots: -1,
            LIConfigKey.gridLotLevelPercent: 1.5,
            LIConfigKey.gridLotStopLossFactor: 1,
            LIConfigKey.gridLotTakeProfitFactor: 2,
            LIConfigKey.gridLotStopProfitFactors: (0.5, 2),
            LIConfigKey.gridInitializeSession: True,  # Be careful!
        }
        investAmount = LIInvestAmount(lotQuantity=1)
        self.liStrategies.append(LIFutureGridTradingMomentum(Futures.Energies.NaturalGas, investAmount, **configs))

    def futureGridTrading_Gold_Trail(self):
        self.SetCash(100_000)
        # self.SetStartDate(date(2023, 4, 15))
        # self.SetEndDate(date(2023, 5, 1))
        # self.SetStartDate(date(2023, 9, 20))
        # self.SetEndDate(date(2023, 10, 20))
        # self.SetStartDate(date(2024, 4, 1))
        # self.SetEndDate(date(2024, 5, 5))
        # A few down/up/down/up/down waves (9/2.33%)
        # self.SetStartDate(date(2024, 5, 1))
        # self.SetEndDate(date(2024, 5, 25))
        # A uptrend with a big dip (129/10.71%/-16.10%)
        self.SetStartDate(date(2024, 8, 1))
        self.SetEndDate(date(2024, 11, 25))

        configs = {
            LIConfigKey.aliasName: "GoldTrail",
            LIConfigKey.monitorPeriod: 5,  # 5 mins
            LIConfigKey.futurePeriodDays: 65,  # 35
            LIConfigKey.futureRolloverDays: 5,
            LIConfigKey.closeWithStopOrderType: True,
            # LIConfigKey.submitTrailingStopOrder: True,
            # LIConfigKey.updateTrailingStopPrice: True,
            LIConfigKey.gridLongLots: 20,
            LIConfigKey.gridRetainOpenedLots: 2,
            LIConfigKey.gridLotLevelPercent: 0.70,
            LIConfigKey.gridLotLevelAugment: 0.0175,
            LIConfigKey.gridLotStopProfitFactors: (0.5, 2),
            LIConfigKey.gridLotStopLossFactor: 25,
            LIConfigKey.gridLotBoostingProfitFactor: 2,
            LIConfigKey.gridLotBoostingDesireProfit: True,  # (139/15.62%/-16.10%)
            LIConfigKey.gridBoostingMaxHoldQuantity: 30,
            # LIConfigKey.gridBoostingKeepTrading: True,
            # LIConfigKey.gridBoostingTriggerPercent: 2.95,
            # LIConfigKey.gridBoostingStopProfitPercents: (0.421, 0.421),
            # LIConfigKey.gridBoostingTriggerAmount: 70,
            # LIConfigKey.gridBoostingStopProfitAmounts: (10, 10),
            LIConfigKey.gridInitializeSession: True,  # Be careful! (mostly used in backtest)
        }
        investAmount = LIInvestAmount(lotQuantity=1)
        self.liStrategies.append(LIFutureGridTradingContrarian(Futures.Metals.MicroGold, investAmount, **configs))

    def futureGridTrading_Dow(self):
        self.SetCash(35000)
        self.SetStartDate(date(2022, 11, 1))
        # self.SetStartDate(date(2023, 1, 1))
        self.SetEndDate(date(2023, 1, 30))

        configs = {
            LIConfigKey.extendedMarketHours: False,
            LIConfigKey.canOpenShortPosition: False,
            LIConfigKey.gridLongLots: 10,
            LIConfigKey.gridLotLevelPercent: 1,
            LIConfigKey.gridLotTakeProfitFactor: 0.5,
        }
        investAmount = LIInvestAmount(maxQuantity=10)  # Invest with 1 contract per unit
        self.liStrategies.append(LIFutureGridTradingContrarian(Futures.Indices.Dow30EMini, investAmount, **configs))

    def futureGridTrading_SP500_Micro(self):
        self.SetCash(350_000)
        self.SetStartDate(date(2023, 7, 27))
        self.SetEndDate(date(2023, 9, 30))

        configs = {
            LIConfigKey.aliasName: "SP500",
            LIConfigKey.monitorPeriod: 5,  # 5 mins
            LIConfigKey.extendedMarketHours: True,
            LIConfigKey.futureRolloverDays: 2,
            LIConfigKey.liquidateAndStopTrading: False,
            LIConfigKey.gridShortLots: 10,
            LIConfigKey.gridLotLevelPercent: 0.65,  # 0.5 -> 0.60 -> 0.65
            LIConfigKey.gridLotLevelAugment: 0.0325,  # 0.025 -> 0.03 -> 0.0325
            LIConfigKey.gridLotTakeProfitFactor: 1.0,
            LIConfigKey.liquidateOnStopLossPercent: 8,
            # LIConfigKey.gridLimitStartPrices: {LIGridSide.STU: 4250},
            LIConfigKey.gridInitializeSession: True,  # Be careful! (mostly used in backtest)
        }
        investAmount = LIInvestAmount(lotQuantity=5)
        self.liStrategies.append(LIFutureGridTradingContrarian(Futures.Indices.MicroSP500EMini, investAmount, **configs))

    def futureGridTrading_SP500_Short(self):
        self.SetCash(350_000)
        # self.SetStartDate(date(2023, 5, 15))
        # self.SetEndDate(date(2023, 5, 25))
        # trades=226, winRate=99%, netProfit=38.034%, annualReturn=547.197%
        self.SetStartDate(date(2023, 7, 27))
        self.SetEndDate(date(2023, 8, 27))
        # self.SetEndDate(date(2023, 9, 27))

        configs = {
            LIConfigKey.aliasName: "SP500",
            LIConfigKey.monitorPeriod: 5,  # 5 mins
            LIConfigKey.extendedMarketHours: True,
            LIConfigKey.futureRolloverDays: 2,
            LIConfigKey.disableBuyingPowerModel: True,
            LIConfigKey.liquidateAndStopTrading: False,
            LIConfigKey.gridShortLots: 10,
            LIConfigKey.gridLotLevelPercent: 0.65,  # 0.5 -> 0.60 -> 0.65
            LIConfigKey.gridLotLevelAugment: -0.0325,  # 0.025 -> 0.03 -> 0.0325
            LIConfigKey.gridRetainOpenedLots: -4,
            LIConfigKey.gridLotTakeProfitFactor: 1.0,
            LIConfigKey.gridFollowAdverseTrend: False,
            # LIConfigKey.liquidateOnStopLossPercent: 8,
            LIConfigKey.gridMaintainCloseOrders: 10,
            # LIConfigKey.gridLimitStartPrices: {LIGridSide.STU: 4250},
            LIConfigKey.gridInitializeSession: True,  # Be careful! (mostly used in backtest)
        }
        investAmount = LIInvestAmount(lotQuantity=1)
        self.liStrategies.append(LIFutureGridTradingContrarian(Futures.Indices.SP500EMini, investAmount, **configs))

    def futureGridTrading_SP500_Long(self):
        self.SetCash(350_000)
        self.SetStartDate(date(2023, 5, 10))
        self.SetEndDate(date(2023, 7, 27))

        configs = {
            LIConfigKey.aliasName: "SP500",
            LIConfigKey.monitorPeriod: 5,  # 5 mins
            LIConfigKey.extendedMarketHours: True,
            LIConfigKey.futureRolloverDays: 2,
            LIConfigKey.liquidateAndStopTrading: False,
            LIConfigKey.gridRetainOpenedLots: -4,
            # LIConfigKey.gridShortLots: 8,
            LIConfigKey.gridLongLots: 8,
            LIConfigKey.gridLotLevelPercent: 0.60,  # 0.5 -> 0.60 -> 0.65
            # LIConfigKey.gridLotLevelAugment: 0.0325,  # 0.025 -> 0.03 -> 0.0325
            LIConfigKey.gridLotTakeProfitFactor: 1.0,
            LIConfigKey.liquidateOnStopLossPercent: 8,
            # LIConfigKey.gridLimitStartPrices: {LIGridSide.STU: 4250},
            LIConfigKey.gridInitializeSession: True,  # Be careful! (mostly used in backtest)
        }
        investAmount = LIInvestAmount(lotQuantity=1)
        self.liStrategies.append(LIFutureGridTradingContrarian(Futures.Indices.SP500EMini, investAmount, **configs))

    def futureGridTrading_SP500_Hedge(self):
        self.SetCash(140_000)
        # Bull trend
        self.SetStartDate(date(2023, 5, 25))
        self.SetEndDate(date(2023, 7, 25))
        # Up/Down 2 cycles trend
        # self.SetStartDate(date(2023, 6, 26))
        # self.SetEndDate(date(2023, 10, 15))
        # Bear trend
        # self.SetStartDate(date(2023, 7, 27))
        # self.SetEndDate(date(2023, 9, 27))

        configs = {
            LIConfigKey.aliasName: "SP500Main",
            LIConfigKey.disableBuyingPowerModel: True,
            LIConfigKey.gridLongLots: 20,
            # LIConfigKey.gridRetainOpenedLots: 1,
            LIConfigKey.gridLotLevelPercent: 0.50,
            LIConfigKey.gridLotStopLossFactor: 20,
            LIConfigKey.gridLotMaxProfitFactor: 5,
            LIConfigKey.gridLotStopProfitFactors: (1, 1),
            LIConfigKey.closeWithStopOrderType: False,
            LIConfigKey.gridInitializeSession: True,  # Be careful! (mostly used in backtest)
        }
        investAmount = LIInvestAmount(lotQuantity=3)
        self.liStrategies.append(LIFutureGridTradingContrarian(Futures.Indices.MicroSP500EMini, investAmount, **configs))

        configs = {
            LIConfigKey.aliasName: "SP500Hedge",
            LIConfigKey.disableBuyingPowerModel: True,
            LIConfigKey.liquidateAndStopTrading: True,
            LIConfigKey.gridShortLots: 6,
            LIConfigKey.gridRetainOpenedLots: -4,
            LIConfigKey.gridLotLevelPercent: 0.50,
            LIConfigKey.gridHedgeAgilely: True,
            LIConfigKey.gridHedgeTargetThreshold: 30,
            LIConfigKey.gridHedgeTargetSizeRatio: 7.5,
            LIConfigKey.gridHedgeTargetSymbolStr: Futures.Indices.MicroSP500EMini,
            LIConfigKey.gridInitializeSession: True,  # Be careful! (mostly used in backtest)
        }
        investAmount = LIInvestAmount(lotQuantity=1)
        self.liStrategies.append(LIFutureGridTradingContrarian(Futures.Indices.SP500EMini, investAmount, **configs))

    def futureGridTrading_SP500_Trail(self):
        self.SetCash(200_000)
        # Bull trend
        # self.SetStartDate(date(2023, 5, 25))
        # self.SetEndDate(date(2023, 7, 25))
        # Up/Down 2 cycles trend
        # self.SetStartDate(date(2023, 6, 26))
        # self.SetEndDate(date(2023, 10, 15))
        # Bear trend
        # self.SetStartDate(date(2023, 7, 27))
        # self.SetEndDate(date(2023, 9, 27))
        # Down/Up Trend
        # self.SetStartDate(date(2023, 10, 10))
        # self.SetEndDate(date(2023, 11, 10))
        # 0.5 (186/73.82%)
        self.SetStartDate(date(2024, 1, 1))
        self.SetEndDate(date(2024, 11, 1))

        configs = {
            LIConfigKey.aliasName: "SP500",
            LIConfigKey.disableBuyingPowerModel: True,
            LIConfigKey.closeWithStopOrderType: False,
            LIConfigKey.liquidateOnStopLossAmount: 100_000,
            LIConfigKey.gridLongLots: 20,
            # LIConfigKey.gridShortLots: 20,
            LIConfigKey.gridRetainOpenedLots: 2,
            LIConfigKey.gridLotLevelPercent: 0.5,
            # LIConfigKey.gridLotLevelAugment: 0.0125,
            LIConfigKey.gridLotStopLossFactor: 20,
            # LIConfigKey.gridLotTakeProfitFactor: 1,
            LIConfigKey.gridLotStopProfitFactors: (0.5, 2),
            # LIConfigKey.gridLotMaxProfitFactor: 15,
            # LIConfigKey.gridLimitStartPrices: {LIGridSide.BTD: 5050},
            # LIConfigKey.gridFixedStartPrices: {LIGridSide.BTD: 5050},
            LIConfigKey.gridInitializeSession: True,  # Be careful! (mostly used in backtest)
        }
        investAmount = LIInvestAmount(lotQuantity=3)
        self.liStrategies.append(LIFutureGridTradingContrarian(Futures.Indices.MicroSP500EMini, investAmount, **configs))

    def futureGridTrading_Nasdaq(self):
        self.SetCash(200_000)
        self.SetStartDate(date(2023, 4, 1))
        self.SetEndDate(date(2023, 6, 1))

        configs = {
            LIConfigKey.monitorPeriod: 5,  # 5 mins
            LIConfigKey.extendedMarketHours: True,
            LIConfigKey.futureRolloverDays: 5,
            LIConfigKey.gridLongLots: 10,
            LIConfigKey.gridLotLevelPercent: 0.56,
            LIConfigKey.gridLotLevelAugment: 0.0125,
            LIConfigKey.gridLotTakeProfitFactor: 1.0,
            LIConfigKey.liquidateOnStopLossPercent: 5,
            # LIConfigKey.gridFixedStartPrices: {LIGridSide.BTD: 12483.25}
            LIConfigKey.gridInitializeSession: True,  # Be careful! (mostly used in backtest)
        }
        investAmount = LIInvestAmount(maxQuantity=10)
        self.liStrategies.append(LIFutureGridTradingContrarian(Futures.Indices.NASDAQ100EMini, investAmount, **configs))

    def futureGridTrading_Nasdaq_Micro(self):
        self.SetCash(50_000)
        # Big losing month!!!
        # self.SetStartDate(date(2022, 12, 1))
        # self.SetEndDate(date(2022, 12, 31))
        # 20 lots, 0.5%, 727.408%, 530 trades
        self.SetStartDate(date(2023, 1, 1))
        self.SetEndDate(date(2023, 3, 17))
        # 20 lots, 0.5%, 1204.641%; 20 lots, 1%, 543.547%; 10 lots, %1, 436.911%
        # self.SetStartDate(date(2022, 12, 13))
        # self.SetEndDate(date(2023, 1, 30))
        # 10 lots, 1%, 229.745%; 20 lots, 1%, 246.547%
        # self.SetStartDate(date(2022, 9, 1))
        # self.SetEndDate(date(2023, 3, 5))
        # 50_000, 15 lots, 0.5%, 451.865% 137 trades, Skip first expired contract
        self.SetStartDate(date(2023, 3, 15))
        self.SetEndDate(date(2023, 4, 15))
        # Short for this period of time!!!
        # self.SetStartDate(date(2023, 7, 15))
        # self.SetEndDate(date(2023, 8, 15))

        configs = {
            LIConfigKey.monitorPeriod: 5,  # 5 mins
            LIConfigKey.benchmarkSymbolStr: "QQQ",
            LIConfigKey.extendedMarketHours: True,
            LIConfigKey.futureRolloverDays: 5,
            LIConfigKey.gridLongLots: 15,
            # LIConfigKey.gridShortLots: 15,
            LIConfigKey.gridLotLevelPercent: 0.5,
            LIConfigKey.gridLotTakeProfitFactor: 1.5,
            LIConfigKey.gridInitializeSession: True,  # Be careful! (mostly used in backtest)
            # LIConfigKey.liquidateOnStopLossPercent: 10,
            # LIConfigKey.liquidateAndStopTrading: True,
            # LIConfigKey.gridLimitStartPrices: {LIGridSide.BTD: 11500.25},
            # LIConfigKey.gridResetStartPrices: {},
            # LIConfigKey.gridResetStartPrices: {LIGridSide.BTD: 12483.25},
            # LIConfigKey.gridFixedStartPrices: {LIGridSide.BTD: 12483.25},
            # LIConfigKey.liquidateOnReachedPrices: {LIGridSide.BTD: 13250.00},
        }
        investAmount = LIInvestAmount(lotQuantity=1)  # Invest with max 20 contracts, 436%
        # investAmount = LIInvestAmount(maxCapital=50000)  # Invest with max 10000 dollars, 1576%
        # investAmount = LIInvestAmount(maxHolding=1)  # Invest with 100% portfolio, 993%
        self.liStrategies.append(LIFutureGridTradingContrarian(Futures.Indices.MicroNASDAQ100EMini, investAmount, **configs))

    def futureGridTrading_Nasdaq_Hedge(self):
        self.SetCash(350_000)
        # Shooting up
        # self.SetStartDate(date(2023, 4, 25))
        # self.SetEndDate(date(2023, 6, 15))
        # Bull trend
        # self.SetStartDate(date(2023, 5, 25))
        # self.SetEndDate(date(2023, 7, 25))
        # Up/Down trend
        # self.SetStartDate(date(2023, 6, 1))
        # self.SetEndDate(date(2023, 10, 1))
        # Bear trend
        # self.SetStartDate(date(2023, 7, 18))
        # self.SetEndDate(date(2023, 8, 18))  # Down to bottom
        # self.SetEndDate(date(2023, 9, 1))  # Up again
        # Down/Up/Down/Up trend (Overall Downtrend)
        # self.SetStartDate(date(2023, 7, 27))
        # self.SetEndDate(date(2023, 10, 27))
        # self.SetStartDate(date(2023, 8, 15))
        # self.SetEndDate(date(2023, 10, 15))
        # Down/Up/Down/Up/Down (Overall Downtrend)
        # self.SetStartDate(date(2023, 7, 19))
        # self.SetEndDate(date(2023, 10, 30))
        # Down/Up/Down/Up (Overall Flat)
        # start:16000,ratio:7.5 -> 267/683.756% -> 295/548.969%
        # start:current,ratio:7.5 -> 254/407.785% -> 259/374.759%
        # self.SetStartDate(date(2023, 9, 15))
        # start:current,ratio:7.5 -> 278/355.487% -> 297/319.547% -> 281/301.603% -> 178/524.745% -> 175/543.094% -> 131/603.077% -> 109/563.630%
        self.SetStartDate(date(2023, 9, 10))
        self.SetEndDate(date(2023, 11, 10))
        # Down Trend
        # self.SetStartDate(date(2023, 9, 15))
        # self.SetEndDate(date(2023, 10, 23))
        # Up Trend
        # self.SetStartDate(date(2023, 10, 23))
        # self.SetEndDate(date(2023, 11, 10))

        configs = {
            LIConfigKey.aliasName: "NasdaqMain",
            # LIConfigKey.extendDataBarStream: True,
            LIConfigKey.disableBuyingPowerModel: True,
            LIConfigKey.gridLongLots: 20,
            LIConfigKey.gridLotLevelPercent: 0.60,
            LIConfigKey.gridLotStopLossFactor: 25,
            LIConfigKey.gridLotMaxProfitFactor: 16,
            LIConfigKey.gridLotStopProfitFactors: (2, 2),
            LIConfigKey.closeWithStopOrderType: False,
            # LIConfigKey.gridRetainOpenedLots: 3,
            # LIConfigKey.gridLimitStartPrices: {LIGridSide.BTD: 16000},
            # LIConfigKey.gridFixedStartPrices: {LIGridSide.BTD: 16000},
            LIConfigKey.gridInitializeSession: True,  # Be careful!
        }
        investAmount = LIInvestAmount(lotQuantity=4)
        self.liStrategies.append(LIFutureGridTradingContrarian(Futures.Indices.MicroNASDAQ100EMini, investAmount, **configs))

        configs = {
            LIConfigKey.aliasName: "NasdaqHedge",
            # LIConfigKey.extendDataBarStream: True,
            LIConfigKey.disableBuyingPowerModel: True,
            # LIConfigKey.liquidateAndStopTrading: True,
            LIConfigKey.gridShortLots: 6,
            LIConfigKey.gridLotLevelPercent: 0.60,
            LIConfigKey.gridRetainOpenedLots: -4,
            LIConfigKey.gridHedgeAgilely: True,
            LIConfigKey.gridHedgeWithIndicator: True,
            # LIConfigKey.gridHedgeTargetThreshold: 30,
            # LIConfigKey.gridHedgeRetainLotsRatio: 1,
            LIConfigKey.gridHedgeTargetSizeRatio: 7.5,
            # LIConfigKey.gridStickToMarketTrend: True, # Use to reset start prices!
            LIConfigKey.gridHedgeTargetSymbolStr: Futures.Indices.MicroNASDAQ100EMini,
            LIConfigKey.gridInitializeSession: True,  # Be careful! (mostly used in backtest)
        }
        investAmount = LIInvestAmount(lotQuantity=1)
        self.liStrategies.append(LIFutureGridTradingContrarian(Futures.Indices.NASDAQ100EMini, investAmount, **configs))

    def futureGridTrading_Nasdaq_Trail(self):
        self.SetCash(200_000)
        # Shooting up
        # self.SetStartDate(date(2023, 4, 25))
        # self.SetEndDate(date(2023, 6, 15))
        # Bull trend
        # self.SetStartDate(date(2023, 5, 25))
        # self.SetEndDate(date(2023, 7, 25))
        # Up/Down trend
        # self.SetStartDate(date(2023, 6, 1))
        # self.SetEndDate(date(2023, 10, 1))
        # Bear trend
        # self.SetStartDate(date(2023, 7, 18))
        # self.SetEndDate(date(2023, 8, 18))  # Down to bottom
        # self.SetEndDate(date(2023, 9, 1))  # Up again
        # Down/Up/Down/Up trend (Overall Downtrend)
        # self.SetStartDate(date(2023, 7, 27))
        # self.SetEndDate(date(2023, 10, 27))
        # self.SetStartDate(date(2023, 8, 15))
        # self.SetEndDate(date(2023, 10, 15))
        # Down/Up/Down/Up/Down (Overall Downtrend)
        # self.SetStartDate(date(2023, 7, 19))
        # self.SetEndDate(date(2023, 10, 30))
        # Down/Up/Down/Up (Overall Flat) (lotQuantity=4)
        # Stop Profit Factor 0: 158/27.44%/319.322%
        # Stop Profit Factor 1: 70/31.46%/403.690%
        # Stop Profit Factor 2: 48/49.35%/(Limit) vs. 43/47.64%(Market)
        # Stop Profit Factor (0.5, 2): 54/55.33%(Limit) vs. 50/46.12%(Market) -> 51/44.59%(Limit) vs. 50/46.12%(Market) -> 62/45.54%(Limit) vs. 62/45.81%(Market)
        #   -> 66/45.69%(Limit) vs. 62/45.78%(Market) -> 72/45.68%(Limit) vs. 62/45.78%(Market) -> 62/45.98%(Limit) vs. 62/45.78%(Market)
        #   -> 50/53.45%(Limit) vs. 49/48.79%(Market) -> 80/53.48%(Limit) vs. 51/48.79%(Market) -> 79/55.54%(Limit) vs. 51/49.81%(Market)
        #   -> 72/55.54%(Limit) vs. 52/54.19%(Market) -> 78/54.04%(Limit) vs. 57/54.37%(Market) -> 96/60.82%(Limit) vs. 76/58.67%(Market)
        #   -> 103/60.83%(Limit) vs. 76/58.68%(Market) -> 101/60.83%(Limit) vs. 76/58.68%(Market) -> 103/61.00%(Limit) vs. 76/58.30%(Market)
        self.SetStartDate(date(2023, 9, 10))
        self.SetEndDate(date(2023, 11, 10))
        # Long term testing with 3 big dips!
        # self.SetCash(350_000)
        # self.SetStartDate(date(2024, 1, 1))
        # self.SetEndDate(date(2024, 10, 1))
        # self.SetStartDate(date(2023, 10, 12))
        # self.SetEndDate(date(2023, 11, 12))
        # Down/Up 71/6.21%/98.711% -> 20/18.57%(Limit) -> 23/15.85%(Market)
        # self.SetStartDate(date(2023, 10, 12))
        # self.SetEndDate(date(2023, 11, 12))
        # self.SetStartDate(date(2023, 11, 15))
        # self.SetEndDate(date(2023, 12, 5))
        # Down Trend
        # self.SetStartDate(date(2023, 9, 15))
        # self.SetEndDate(date(2023, 10, 23))
        # Up Trend
        # self.SetStartDate(date(2023, 10, 23))
        # self.SetEndDate(date(2023, 11, 10))
        # Flat 2 months
        # self.SetStartDate(date(2024, 2, 8))
        # self.SetEndDate(date(2024, 4, 8))
        # 39/30.78%/190.815%
        # self.SetStartDate(date(2023, 10, 6))
        # self.SetEndDate(date(2024, 1, 6))
        # Long term with up and down trends
        # self.SetStartDate(date(2023, 10, 1))
        # self.SetEndDate(date(2024, 5, 1))
        # Covid super dip V trend
        # self.SetStartDate(date(2020, 2, 10))
        # self.SetEndDate(date(2020, 5, 10))
        # Test liquidation on reached/retraced prices
        # self.SetStartDate(date(2023, 10, 21))
        # self.SetEndDate(date(2023, 11, 10))
        # self.SetStartDate(date(2024, 4, 1))
        # self.SetEndDate(date(2024, 7, 11))
        # Down deep and up big
        # self.SetStartDate(date(2024, 7, 10))
        # self.SetStartDate(date(2024, 8, 5))
        # self.SetEndDate(date(2024, 8, 25))

        configs = {
            LIConfigKey.aliasName: "Nasdaq",
            LIConfigKey.monitorPeriod: 5,
            # LIConfigKey.verboseLogging: True,
            # LIConfigKey.futurePeriodDays: 180,
            # LIConfigKey.futureContractCode: "MNQ20Z24",
            # LIConfigKey.futureContractExpiry: date(2024, 12, 20),
            LIConfigKey.extendDataBarStream: True,
            # LIConfigKey.fetchHistoryBarData: False,
            # LIConfigKey.closeWithStopOrderType: True,
            # LIConfigKey.submitTrailingStopOrder: True,
            # LIConfigKey.updateTrailingStopPrice: True,
            LIConfigKey.disableBuyingPowerModel: True,
            # LIConfigKey.riskProposeHedgeInsights: True,
            # LIConfigKey.gridMaintainOpenOrders: 1,
            # LIConfigKey.gridMaintainCloseOrders: 2,
            # LIConfigKey.liquidateOnStopLossAmount: 10_000,
            # LIConfigKey.liquidateOnTakeProfitAmount: 15_000,
            # LIConfigKey.liquidateByTrailingProfitPercent: 30,
            # LIConfigKey.liquidateLossAndRestartTrading: False,
            # LIConfigKey.liquidateProfitAndRestartTrading: True,
            # LIConfigKey.gridMaintainOpenOrders: 1,
            # LIConfigKey.gridMaintainCloseOrders: 2,
            LIConfigKey.gridLongLots: 20,
            # LIConfigKey.gridLongLotsQty: [1, 1, 1, 1, 2, 2, 2, 2, 3, 3, 3, 3, 4, 4, 4, 4, 5, 5, 5, 5],
            # LIConfigKey.gridShortLots: 20,
            LIConfigKey.gridLotLevelPercent: 0.60,
            # LIConfigKey.gridLotLevelAugment: 0.015,  # Perform better in a long run with volatile market
            # LIConfigKey.gridLotTakeProfitFactor: 1,
            # LIConfigKey.gridLotMaxProfitFactor: 16,
            LIConfigKey.gridLotStopLossFactor: 25,
            LIConfigKey.gridLotStopProfitFactors: (0.5, 2),
            # LIConfigKey.gridLotBoostingProfitFactor: 2,  # Max profit with boosting! (180/131.37%/-34.10%)
            # LIConfigKey.gridLotBoostingDesireProfit: True,
            # LIConfigKey.gridBoostingMaxHoldQuantity: 150,
            # LIConfigKey.gridInitOpenedLots: 2,
            # LIConfigKey.gridRetainOpenedLots: 2,
            # LIConfigKey.gridMaintainCloseOrders: 5,
            # LIConfigKey.gridRealignOpenPositions: True,
            # LIConfigKey.gridLimitStartPrices: {LIGridSide.BTD: 16000},
            # LIConfigKey.gridFixedStartPrices: {LIGridSide.BTD: 16000},
            # LIConfigKey.gridPriceInStopProfitFactor: True,
            # LIConfigKey.gridBoostingKeepTrading: True,
            # LIConfigKey.gridBoostingTriggerAmount: 500,
            # LIConfigKey.gridBoostingStopProfitAmounts: (150, 150),
            # LIConfigKey.liquidateOnReachedPrices: {LIGridSide.BTD: 15000, LIGridSide.STU: 13000},
            # LIConfigKey.liquidateByTrailingProfitPercent: 2,
            LIConfigKey.gridInitializeSession: True,  # Be careful!
        }
        investAmount = LIInvestAmount(lotQuantity=4)
        self.liStrategies.append(LIFutureGridTradingContrarian(Futures.Indices.MicroNASDAQ100EMini, investAmount, **configs))

    def futureGridTrading_Nasdaq_Boost(self):
        self.SetCash(300_000)
        # Down/Up/Down/Up (Overall Flat) (317/56.80%/-17.60%)
        # self.SetStartDate(date(2023, 9, 10))
        # self.SetEndDate(date(2023, 11, 10))
        # Big W Shape (Overall a bit down) (360/43.77%/-63.10%)
        # Big W Shape (Overall a bit down) (593/162.76%/-92.90%) with gridLotLevelAugment:0.015
        # Big W Share (Overall a bit down) (452/150.93%/-93.20%) with enableLimitMarketOrder: True
        self.SetStartDate(date(2024, 7, 11))
        self.SetEndDate(date(2024, 10, 11))
        # self.SetStartDate(date(2024, 11, 10))
        # self.SetEndDate(date(2024, 12, 15))

        configs = {
            LIConfigKey.aliasName: "NasdaqBoost",
            LIConfigKey.monitorPeriod: 5,
            # LIConfigKey.verboseLogging: True,
            # LIConfigKey.futurePeriodDays: 180,
            # LIConfigKey.futureContractCode: "MNQ20Z24",
            # LIConfigKey.futureContractExpiry: date(2024, 12, 20),
            LIConfigKey.extendDataBarStream: True,
            # LIConfigKey.fetchHistoryBarData: False,
            LIConfigKey.closeWithStopOrderType: True,
            # LIConfigKey.submitTrailingStopOrder: True,
            # LIConfigKey.updateTrailingStopPrice: True,
            LIConfigKey.enableLimitMarketOrder: True,
            LIConfigKey.disableBuyingPowerModel: True,
            # LIConfigKey.riskProposeHedgeInsights: True,
            # LIConfigKey.gridMaintainOpenOrders: 1,
            # LIConfigKey.gridMaintainCloseOrders: 2,
            LIConfigKey.gridLongLots: 20,
            LIConfigKey.gridLongLotsQty: [2, 2, 2, 2, 2, 2, 2, 2, 3, 3, 3, 3, 3, 3, 3, 4, 4, 4, 4, 4],  # 8 * 2 + 7 * 3 + 5 * 4 = 57
            # LIConfigKey.gridShortLots: 20,
            LIConfigKey.gridLotLevelPercent: 0.60,
            LIConfigKey.gridLotLevelAugment: 0.015,  # Perform better in a long run with volatile market
            # LIConfigKey.gridLotTakeProfitFactor: 1,
            # LIConfigKey.gridLotMaxProfitFactor: 16,
            LIConfigKey.gridLotStopLossFactor: 25,
            LIConfigKey.gridLotStopProfitFactors: (0.5, 2),
            LIConfigKey.gridLotBoostingProfitFactor: 2,
            LIConfigKey.gridBoostingMaxHoldQuantity: 150,
            # LIConfigKey.gridInitOpenedLots: 2,
            # LIConfigKey.gridRetainOpenedLots: 2,
            # LIConfigKey.gridMaintainCloseOrders: 5,
            # LIConfigKey.gridRealignOpenPositions: True,
            # LIConfigKey.gridLimitStartPrices: {LIGridSide.BTD: 16000},
            # LIConfigKey.gridFixedStartPrices: {LIGridSide.BTD: 16000},
            # LIConfigKey.gridPriceInStopProfitFactor: True,
            # LIConfigKey.gridBoostingKeepTrading: True,
            # LIConfigKey.gridBoostingTriggerAmount: 500,
            # LIConfigKey.gridBoostingStopProfitAmounts: (150, 150),
            # LIConfigKey.liquidateOnReachedPrices: {LIGridSide.BTD: 15000, LIGridSide.STU: 13000},
            LIConfigKey.gridInitializeSession: True,  # Be careful!
        }
        investAmount = LIInvestAmount(lotQuantity=2)
        self.liStrategies.append(LIFutureGridTradingContrarian(Futures.Indices.MicroNASDAQ100EMini, investAmount, **configs))

    def futureGridTrading_Nasdaq_Trend(self):
        self.SetCash(50_000)
        # Down/Up/Down/Up (Overall Flat)
        # start:16000,ratio:7.5 -> 267/683.756%
        # start:current,ratio:7.5 -> 254/407.785%
        # self.SetStartDate(date(2023, 9, 15))
        # self.SetEndDate(date(2023, 11, 10))
        # Down Trend
        # self.SetStartDate(date(2023, 9, 15))
        # self.SetEndDate(date(2023, 10, 23))
        # Up Trend
        # self.SetStartDate(date(2023, 10, 23))
        # self.SetEndDate(date(2023, 11, 10))
        # Test Down/Up Trend (60 mins) 43/41.09%/6723.152% -> 48/36.50%/4448.559% -> 72/41.44%/6933.573% -> 78/44.61%/6583.183%
        # Test Down/Up Trend (5 mins) 94/32.46%/2358.282%
        # self.SetStartDate(date(2023, 9, 12))  # 215/88.99%/4129.986%
        # takeProfitFactor=9, stopProfitFactor=3: 153/128.95%/1252883.963% -> 132/118.80%/747270.450%(Limit)
        # takeProfitFactor=9, stopProfitFactor=2: 128/86.98% -> 140/130.74%, 154/127.44%(Limit)
        # Seeking long-term profit and soft landing (2, 2) -> 179/63.62%(Limit) vs. 164/55.93%(Market) -> 188/61.65%(Limit) vs. 180/58.25%(Market)
        # Seeking long-term profit and soft landing (0.5, 2) -> 162/47.83%(Limit) vs. 162/82.77%(Market) -> 194/73.49%(Limit) vs. 162/82.77%(Market)
        #   -> 183/73.39%(Limit) vs. 167/79.41%(Market) -> 193/72.06%(Limit) vs. 169/78.60%(Market) -> 252/52.87%(Limit) vs. 169/78.60%(Market)
        #   -> 252/52.87%(Limit) vs. 169/78.31%(Market) -> 275/47.74%(Limit) vs. 169/80.42%(Market) -> 176/32.70%(Limit) vs. 180/78.71%(Market)
        #   -> 176/32.70%(Limit) vs. 169/76.97%(Market)
        self.SetStartDate(date(2023, 10, 12))
        self.SetEndDate(date(2023, 11, 12))
        # Up/Down/Up/Down/Up volatile market
        # self.SetStartDate(date(2024, 2, 1))
        # self.SetEndDate(date(2024, 2, 28))
        # 5 up/down small waves
        # self.SetStartDate(date(2024, 2, 10))
        # self.SetEndDate(date(2024, 3, 20))
        # Test Up/Down
        # self.SetStartDate(date(2023, 10, 4))
        # self.SetEndDate(date(2023, 10, 26))
        # Flat market style (positive profit)
        # self.SetStartDate(date(2023, 9, 20))
        # self.SetEndDate(date(2023, 10, 20))
        # Flat 2 months (negative profit)
        # self.SetStartDate(date(2024, 2, 8))
        # self.SetEndDate(date(2024, 4, 8))
        # A few small waves
        # self.SetStartDate(date(2024, 4, 1))
        # self.SetEndDate(date(2024, 4, 19))

        # self.SetStartDate(date(2023, 10, 6))
        # self.SetStartDate(date(2023, 12, 13))
        # self.SetStartDate(date(2023, 12, 20))
        # self.SetStartDate(date(2023, 12, 28))
        # self.SetEndDate(date(2024, 1, 31))

        # Up/Down with loss profit 105/-63.034% -> 103/568.270%
        # self.SetStartDate(date(2023, 10, 5))
        # self.SetEndDate(date(2023, 10, 20))
        # LIConfigKey.gridLotTakeProfitFactor: 2.375,
        # LIConfigKey.gridLotPauseAfterProfit: True,
        # LIConfigKey.closeWithStopOrderType: False,
        # LIConfigKey.gridLotStopProfitFactors: (2.75, 2.75),
        # LIConfigKey.gridLotMaxProfitFactor: 2.375,

        # Downtrend overall, approve that Momentum tightly relies on market style!
        # self.SetStartDate(date(2024, 3, 21))  # Big Loss!
        # self.SetStartDate(date(2024, 4, 11)) # Profitable
        # self.SetEndDate(date(2024, 4, 19))

        configs = {
            LIConfigKey.aliasName: "NasdaqTrend",
            LIConfigKey.monitorPeriod: 5,
            # LIConfigKey.extendDataBarStream: True,
            # LIConfigKey.fetchHistoryBarData: False,
            # LIConfigKey.openWithStopOrderType: True,
            # LIConfigKey.closeWithStopOrderType: True,
            # LIConfigKey.disableBuyingPowerModel: True,
            # LIConfigKey.liquidateAndStopTrading: True,
            # LIConfigKey.liquidateOnTakeProfitAmount: 10_000,
            # LIConfigKey.gridMaintainOpenOrders: 1,
            # LIConfigKey.gridMaintainCloseOrders: 2,
            LIConfigKey.gridLongLots: 12,
            LIConfigKey.gridShortLots: 8,
            # LIConfigKey.gridInitOpenedLots: -1,
            # LIConfigKey.gridRetainOpenedLots: -1,
            LIConfigKey.gridLotLevelPercent: 0.4,
            LIConfigKey.gridLotStopLossFactor: 1.5,
            LIConfigKey.gridLotTakeProfitFactor: 3,
            LIConfigKey.gridLotStopProfitFactors: (0.5, 2),
            # LIConfigKey.gridBoostingKeepTrading: True,
            # LIConfigKey.gridBoostingTriggerAmount: 300,
            # LIConfigKey.gridBoostingMaxHoldQuantity: 60,
            # LIConfigKey.gridBoostingStopProfitAmounts: (150, 150),
            # LIConfigKey.gridKeepOpenOrdersApart: True,
            # LIConfigKey.gridKeepStartCloseOrders: 3,
            # LIConfigKey.gridLotStopProfitFactors: (2, 2),
            # LIConfigKey.gridLotMaxProfitFactor: 15,
            # LIConfigKey.gridLotPauseAfterProfit: True,
            # LIConfigKey.gridRestartIfAllLotsPaused: True,
            # LIConfigKey.gridResetStartPrices: {LIGridSide.BTU: 15400, LIGridSide.STD: 15400},
            # LIConfigKey.liquidateOnReachedPrices: {LIGridSide.BTU: 16000, LIGridSide.STD: 14000},
            # LIConfigKey.liquidateOnTakeProfitAmount: 5_000,
            LIConfigKey.gridInitializeSession: True,  # Be careful!
        }
        investAmount = LIInvestAmount(lotQuantity=2)
        self.liStrategies.append(LIFutureGridTradingMomentum(Futures.Indices.MicroNASDAQ100EMini, investAmount, **configs))

    def futureGridTrading_Nasdaq_Scalp(self):
        self.SetCash(100_000)
        # Big Down/Up V trend
        self.SetStartDate(date(2023, 10, 12))
        self.SetEndDate(date(2023, 11, 12))
        # Overall Up trend with small waves
        # self.SetStartDate(date(2024, 1, 1))
        # self.SetEndDate(date(2024, 3, 10))
        # Up/Down/Up/Down/Up volatile market
        # self.SetStartDate(date(2024, 2, 1))
        # self.SetEndDate(date(2024, 2, 28))
        # Big jump (67/24.48%) -> (73/18.46%)
        self.SetStartDate(date(2024, 2, 19))
        self.SetEndDate(date(2024, 2, 23))

        self.SetStartDate(date(2024, 12, 1))
        self.SetEndDate(date(2024, 12, 23))
        # Medium jump
        # self.SetStartDate(date(2024, 3, 19))
        # self.SetEndDate(date(2024, 3, 23))
        # 2 months about 5+ up/down waves
        # self.SetStartDate(date(2024, 2, 1))
        # self.SetEndDate(date(2024, 4, 1))
        # 2 stages sharp uptrend
        # self.SetStartDate(date(2024, 2, 21))
        # self.SetEndDate(date(2024, 3, 2))
        # A few small waves, almost flat
        # self.SetStartDate(date(2024, 2, 29))
        # self.SetEndDate(date(2024, 4, 5))
        # self.SetStartDate(date(2024, 2, 8))
        # self.SetEndDate(date(2024, 4, 8))
        # self.SetStartDate(date(2023, 10, 12))
        # self.SetEndDate(date(2023, 11, 12))
        # self.SetStartDate(date(2024, 4, 1))
        # self.SetEndDate(date(2024, 4, 19))
        # Long term with up and down trends
        # self.SetStartDate(date(2023, 10, 1))
        # self.SetEndDate(date(2024, 5, 1))
        # Downtrend overall, approve that Momentum tightly relies on market style!
        # self.SetStartDate(date(2024, 3, 21))  # Big Loss!
        # self.SetStartDate(date(2024, 4, 11)) # Profitable
        # self.SetEndDate(date(2024, 4, 19))
        # One day sharp drop market
        # self.SetStartDate(date(2024, 4, 4))
        # self.SetEndDate(date(2024, 4, 4))

        configs = {
            LIConfigKey.aliasName: "NasdaqScalp",
            LIConfigKey.monitorPeriod: 5,  # 1 min for live
            # LIConfigKey.enableLimitMarketOrder: True,
            # LIConfigKey.fetchHistoryBarData: False,
            # LIConfigKey.openWithStopOrderType: True,
            # LIConfigKey.closeWithStopOrderType: True,
            # LIConfigKey.liquidateOnFridayClose: True,  # Reduce drawdown and profit
            # LIConfigKey.disableBuyingPowerModel: True,
            # LIConfigKey.liquidateAndStopTrading: True,
            # LIConfigKey.liquidateOnTakeProfitAmount: 10_000,
            # LIConfigKey.gridMaintainOpenOrders: 1,
            # LIConfigKey.gridMaintainCloseOrders: 2,
            LIConfigKey.gridLongLots: 15,
            LIConfigKey.gridShortLots: 12,
            LIConfigKey.gridLotLevelAmount: 50,
            # LIConfigKey.gridLotLevelPercent: 0.3,
            # LIConfigKey.gridLongLots: 10,
            # LIConfigKey.gridShortLots: 8,
            # LIConfigKey.gridLotLevelPercent: 0.4,
            # LIConfigKey.gridInitOpenedLots: -1,
            # LIConfigKey.gridRetainOpenedLots: -1,
            # LIConfigKey.gridUseHeikinAshi: True,
            LIConfigKey.gridLotStopLossFactor: 25,
            LIConfigKey.gridLotTakeProfitFactor: 25,
            LIConfigKey.gridLotStopProfitFactors: (0.5, 2),  # Good for bigger waves
            # LIConfigKey.gridBoostingKeepTrading: True,
            LIConfigKey.gridBoostingTriggerAmount: 120,
            LIConfigKey.gridBoostingMaxHoldQuantity: 30 * 2,
            LIConfigKey.gridBoostingStopProfitAmounts: (90, 90),
            # LIConfigKey.gridBoostingStopProfitAmounts: (100, 75),
            # LIConfigKey.gridRestartOnFridayClose: True,  # Reduce drawdown and profit
            # LIConfigKey.gridRealignOpenPositions: True,
            LIConfigKey.gridInitializeSession: True,  # Be careful!
        }
        investAmount = LIInvestAmount(lotQuantity=2)
        self.liStrategies.append(LIFutureGridTradingMomentum(Futures.Indices.MicroNASDAQ100EMini, investAmount, **configs))

    def futureGridTrading_Nasdaq_Scalp_NQ(self):
        self.SetCash(500_000)
        # Big Down/Up V trend
        self.SetStartDate(date(2023, 10, 12))
        self.SetEndDate(date(2023, 11, 12))
        # Overall Up trend with small waves
        self.SetStartDate(date(2024, 1, 1))
        self.SetEndDate(date(2024, 3, 10))
        # Up/Down/Up/Down/Up volatile market
        # self.SetStartDate(date(2024, 2, 1))
        # self.SetEndDate(date(2024, 2, 28))
        # Big up/down/up/down
        # self.SetStartDate(date(2024, 2, 29))
        # self.SetEndDate(date(2024, 3, 11))
        # Big jump
        # self.SetStartDate(date(2024, 2, 19))
        # self.SetEndDate(date(2024, 2, 23))
        # Medium jump
        # self.SetStartDate(date(2024, 3, 19))
        # self.SetEndDate(date(2024, 3, 23))
        # 2 months about 5+ up/down waves
        # self.SetStartDate(date(2024, 2, 1))
        # self.SetEndDate(date(2024, 4, 1))
        # 2 stages sharp uptrend
        # self.SetStartDate(date(2024, 2, 21))
        # self.SetEndDate(date(2024, 3, 2))
        # Almost flat 2 months
        self.SetStartDate(date(2024, 2, 8))
        self.SetEndDate(date(2024, 4, 8))
        # Up/Down big wave with volatile market
        self.SetStartDate(date(2024, 7, 1))
        self.SetEndDate(date(2024, 7, 27))
        # A few down trend days with good performance
        # self.SetStartDate(date(2024, 7, 23))
        # self.SetEndDate(date(2024, 7, 26))
        # 9+ months period of tense trading
        # self.SetStartDate(date(2024, 1, 1))
        # self.SetEndDate(date(2024, 9, 20))
        # First 3 months of 2024
        # self.SetStartDate(date(2024, 1, 1))
        # self.SetEndDate(date(2024, 4, 1))
        # First 3 months of 2023
        # self.SetStartDate(date(2023, 1, 1))
        # self.SetEndDate(date(2023, 4, 1))
        # First 3 months of 2022 (Always negative performance!?)
        # self.SetStartDate(date(2022, 1, 1))
        # self.SetEndDate(date(2022, 4, 1))
        # Test to identity the best settings lately!
        # self.SetStartDate(datetime.now() - timedelta(days=7))  # Last 7 days
        # self.SetStartDate(datetime.now() - timedelta(days=30)) # Last 30 days
        # self.SetStartDate(datetime.now() - timedelta(days=60))  # Last 60 days
        # self.SetStartDate(datetime.now() - timedelta(days=90)) # Last 90 days
        # self.SetEndDate(datetime.now())

        # LIConfigKey.gridBoostingTriggerAmount: 120,
        # LIConfigKey.gridBoostingStopProfitAmounts: (100, 75),
        # 24/7/23-24/7/27: 1 min (156/25.61%/-10.80%), 5 mins (129/26.01%/-11.10%)
        # 24/7/1-24/7/27: 1 min (440/80.12%/-10.80%), 5 mins (387/70.20%/-13.00%)
        # 24/1/1-24/7/27: 1 min (2647/155.56%/-17.90%), 5 mins (2276/118.57%/-19.90%)
        # 24/1/1-24/3/10: 1 min (806/42.60%/-13.10%), 5 mins (686/36.48%/-13.50%)
        # 24/2/8-24/4/8: 1 min (758/13.56%/-15.60%), 5 mins (579/9.04%/-15.50%)

        # LIConfigKey.gridBoostingTriggerPercent: 0.5,
        # LIConfigKey.gridBoostingStopProfitPercents: (0.45, 0.35),
        # 24/7/23-24/7/27: 1 min (164/26.74%/-9.4%), 5 mins (113/26.94%/-9.3%)
        # 24/7/1-24/7/27: 1 min (468/85.48%/-11.90%) -> (476/84.45%/-11.50%), 5 mins (385/100.62%/-11.80%) -> (378/110.89%/-13.70%) -> (390/106.07%/-11.80%) -> (397/101.92%/-11.60%)
        # 24/1/1-24/7/27: 1 min (2647/155.56%/-17.90%), 5 mins (2276/118.57%/-19.90%)
        # 24/1/1-24/3/10: 1 min (806/42.60%/-13.10%), 5 mins (686/36.48%/-13.50%)
        # 24/2/8-24/4/8: 1 min (758/13.56%/-15.60%), 5 mins (579/9.04%/-15.50%)

        configs = {
            LIConfigKey.aliasName: "NasdaqScalp",
            LIConfigKey.resolution: LIResolution.MINUTE,
            LIConfigKey.monitorPeriod: 5,
            # LIConfigKey.resolution: LIResolution.SECOND,
            # LIConfigKey.monitorPeriod: 10,
            # LIConfigKey.useHeikinAshi: True,
            # LIConfigKey.verboseLogging: True,
            # LIConfigKey.openWithStopOrderType: True,
            # LIConfigKey.closeWithStopOrderType: True,
            LIConfigKey.disableBuyingPowerModel: True,
            # LIConfigKey.enableTrailingStopLoss: False,
            # LIConfigKey.enableLimitMarketOrder: True,
            # LIConfigKey.liquidateAndStopTrading: True,
            # LIConfigKey.gridNoMoreOpenOrders: True,
            # LIConfigKey.gridLongLots: 12,
            # LIConfigKey.gridShortLots: 8,
            LIConfigKey.gridLongLots: 8,
            LIConfigKey.gridShortLots: 6,
            # LIConfigKey.gridLongLots: 5,
            # LIConfigKey.gridShortLots: 4,
            # LIConfigKey.gridInitOpenedLots: -1,
            # LIConfigKey.gridLotLevelAmount: 50,
            # LIConfigKey.gridLotLevelPercent: 0.25,
            LIConfigKey.gridLotLevelPercent: 0.3,
            # LIConfigKey.gridLotLevelPercent: 0.35,
            LIConfigKey.gridLotStopLossFactor: 1,
            LIConfigKey.gridLotTakeProfitFactor: 2,
            LIConfigKey.gridLotStopProfitFactors: (0.5, 2),
            # LIConfigKey.gridLotPauseAfterProfit: False,
            # LIConfigKey.gridPauseTradingProfitHours: (100_000, 3 * 24),
            LIConfigKey.gridBoostingKeepTrading: True,
            LIConfigKey.gridBoostingMaxHoldQuantity: 30,
            # LIConfigKey.gridBoostingTrailingStopQuantity: 20,
            # LIConfigKey.gridBoostingTriggerAmount: 120,
            # LIConfigKey.gridBoostingStopProfitAmounts: (100, 75),
            # LIConfigKey.gridBoostingTriggerAmount: 120 * 0.8,
            # LIConfigKey.gridBoostingStopProfitAmounts: (100 * 0.8, 75 * 0.8),
            LIConfigKey.gridBoostingTriggerPercent: 0.5,  # Best lately
            LIConfigKey.gridBoostingStopProfitPercents: (0.45, 0.35),
            # LIConfigKey.gridBoostingTriggerPercent: 0.568,
            # LIConfigKey.gridBoostingStopProfitPercents: (0.473, 0.355),
            # LIConfigKey.gridBoostingTriggerPercent: 0.58,
            # LIConfigKey.gridBoostingStopProfitPercents: (0.4833, 0.3625),
            # LIConfigKey.gridBoostingTriggerPercent: 0.618,
            # LIConfigKey.gridBoostingStopProfitPercents: (0.515, 0.386),
            LIConfigKey.gridInitializeSession: True,  # Be careful!
        }

        investAmount = LIInvestAmount(lotQuantity=1)
        self.liStrategies.append(LIFutureGridTradingMomentum(Futures.Indices.NASDAQ100EMini, investAmount, **configs))

    # The momentum is hard to win on Nasdaq index futures!
    def futureGridTrading_Nasdaq_Momentum(self):
        self.SetCash(100_000)
        # 2 months about 5+ up/down waves: (24/-2.91%/-7.40%)
        # self.SetStartDate(date(2024, 2, 1))
        # self.SetEndDate(date(2024, 4, 1))
        # A typical big dip and reverse: (143/46.57%/-8.20%) -> (149/50.72%/-6.00%)
        # self.SetStartDate(date(2024, 7, 1))
        # self.SetEndDate(date(2024, 12, 31))
        # 2021 annual performance (244/7.24%/-0.57%)
        # self.SetStartDate(date(2021, 1, 1))
        # self.SetEndDate(date(2021, 12, 31))
        # 2022 annual performance (421/-25.65%/-41.00%)
        # self.SetStartDate(date(2022, 1, 1))
        # self.SetEndDate(date(2022, 12, 31))
        # 2023 annual performance (227/25.50%/-12.60%)
        # self.SetStartDate(date(2023, 1, 1))
        # self.SetEndDate(date(2023, 12, 31))
        # 2024 annual performance (229/-11.12%/-24.40%)
        self.SetStartDate(date(2024, 1, 1))
        self.SetEndDate(date(2024, 12, 31))

        amplifier = 1  # Amplify invest amount by n times!
        configs = {
            LIConfigKey.aliasName: "NasdaqTrend",
            LIConfigKey.monitorPeriod: 60,  # 5
            # LIConfigKey.monitorPeriod: 1, # Perform worse than 60 mins!
            # LIConfigKey.resolution: LIResolution.HOUR,
            # LIConfigKey.openWithStopOrderType: True,
            # LIConfigKey.futureContractExpiry: date(2025, 3, 21),
            # Adjust it dynamically based on current market trend/volatility and paired contrarian strategy's profit loss!
            LIConfigKey.liquidateOnTakeProfitAmounts: {LIGridSide.BTU: 5_000 * amplifier, LIGridSide.STD: 5_000 * amplifier},
            LIConfigKey.gridLongLots: 8,
            LIConfigKey.gridShortLots: 8,
            LIConfigKey.gridLotLevelPercent: 0.60,
            LIConfigKey.gridLotStopLossFactor: 7,
            LIConfigKey.gridLotTakeProfitFactor: 3,
            LIConfigKey.gridLotPauseAfterProfit: False,
            # LIConfigKey.gridBandingOpenFromPrices: True,
            # LIConfigKey.bollingerBandsParams: [(365, 2)],
            # LIConfigKey.gridMonitorPeriodFactors: {LIGridSide.STD: 1, LIGridSide.BTU: 12},
            # LIConfigKey.gridTransfer2Counterpart: True,
            LIConfigKey.gridInitializeSession: True,  # Be careful!
        }

        investAmount = LIInvestAmount(lotQuantity=1 * amplifier)
        self.liStrategies.append(LIFutureGridTradingMomentum(Futures.Indices.MicroNASDAQ100EMini, investAmount, **configs))

    def futureGridTrading_Nasdaq_Contrarian_Long(self):
        self.SetCash(200_000)
        # 2 months about 5+ up/down waves: (46/4.73%/-1.6%)
        # self.SetStartDate(date(2024, 2, 1))
        # self.SetEndDate(date(2024, 4, 1))
        # A typical big dip and reverse:
        # 60 mins: (111/44.56%/-36.90%)
        # 1 hours: (79/30.9%/-30.30%)
        # self.SetStartDate(date(2024, 7, 1))
        # self.SetEndDate(date(2024, 12, 1))
        # Test and update results for below years
        # 2021 annual performance (244/7.24%/-0.57%)
        # self.SetStartDate(date(2021, 1, 1))
        # self.SetEndDate(date(2021, 12, 31))
        # 2022 annual performance (421/-25.65%/-41.00%)
        # self.SetStartDate(date(2022, 1, 1))
        # self.SetEndDate(date(2022, 12, 31))
        # 2023 annual performance (411/43.39%/-11.70%)
        # self.SetStartDate(date(2023, 1, 1))
        # self.SetEndDate(date(2023, 12, 31))
        # 2024 annual performance (288/59.37%/-30.50%) -> (286/80.65%/-30.10%) -> (287/81.00%/30.0%) -> (298/65.85%/-28.10%)
        self.SetStartDate(date(2024, 1, 1))
        self.SetStartDate(date(2024, 10, 1))  # (131/11.72%/-10.70%) -> (101/7.60%/-6.6%)
        self.SetEndDate(date(2024, 12, 31))

        amplifier = 1  # Amplify invest amount by n times!
        configs = {
            LIConfigKey.aliasName: "NasdaqTrail",
            # LIConfigKey.verboseLogging: True,
            LIConfigKey.monitorPeriod: 5 * 12,
            # LIConfigKey.monitorPeriod: 1,
            # LIConfigKey.resolution: LIResolution.HOUR, # Performs worse than 60 mins
            # LIConfigKey.futureContractCode: "MNQ20Z24",
            # LIConfigKey.futureContractExpiry: date(2025, 3, 21),
            # LIConfigKey.closeWithStopOrderType: True,
            LIConfigKey.liquidateOnStopLossAmount: 100_000 * amplifier,
            # LIConfigKey.liquidateLossAndRestartTrading: True,
            # Adjust it dynamically based on current market trend/volatility and paired momentum strategy's profit loss!
            LIConfigKey.liquidateOnTakeProfitAmount: 50_000 * amplifier,
            LIConfigKey.gridLongLots: 20,
            LIConfigKey.gridLotLevelPercent: 0.60,
            LIConfigKey.gridLotLevelAugment: 0.015,  # Perform better in a long run with volatile market
            LIConfigKey.gridLotStopLossFactor: 25,
            LIConfigKey.gridLotStopProfitFactors: (0.5, 2),
            LIConfigKey.gridLotPauseAfterStopLoss: False,
            LIConfigKey.gridLotMaxOpenPriceFactor: 1.0,
            # LIConfigKey.gridBandingStartPrices: True,
            # LIConfigKey.gridBandingOpenFromPrices: True,
            # LIConfigKey.bollingerBandsParams: [(365, 1)],
            # LIConfigKey.gridRetainOpenedLots: 3,
            # LIConfigKey.gridRealignOpenPositions: True,
            LIConfigKey.gridInitializeSession: True,  # Be careful!
        }
        investAmount = LIInvestAmount(lotQuantity=1 * amplifier)
        self.liStrategies.append(LIFutureGridTradingContrarian(Futures.Indices.MicroNASDAQ100EMini, investAmount, **configs))

    def futureGridTrading_Nasdaq_Contrarian_Short(self):
        """Not an all weather strategy, should enable it with a bearish-biased market in mind, liquidate and stop loss in time!"""
        self.SetCash(200_000)
        # 2 months overall up trend with 5+ up/down waves:
        # maxOpenPriceFactor=1.0: (50/1.14%/-9.5%)
        # maxOpenPriceFactor=0.5: (30/-3.77%/-13.9%)
        # self.SetStartDate(date(2024, 2, 1))
        # self.SetEndDate(date(2024, 4, 1))
        # 1+ months big dip and reverse, make sure to stop trading in time!
        # maxOpenPriceFactor=1.0: (69/4.46%/-11.0%)
        # maxOpenPriceFactor=0.5: (138/21.79%/-7.8%)
        # self.SetStartDate(date(2024, 7, 10))
        # self.SetEndDate(date(2024, 8, 20))
        # 3 months strong up trend, liquidated with stop loss:
        # maxOpenPriceFactor=1.0: (81/-6.86/-15.4%)
        # maxOpenPriceFactor=0.5: (66/-8.12%/-12.5%)
        # self.SetStartDate(date(2024, 9, 15))
        # self.SetEndDate(date(2024, 12, 15))
        # 2+ months flat with a few up down oscillations
        # maxOpenPriceFactor=1.0: (84/8.22%/-10.0%)
        # maxOpenPriceFactor=0.5: (91/6.06%/-10.9%)
        # self.SetStartDate(date(2024, 12, 17))
        # self.SetEndDate(date(2025, 2, 18))

        amplifier = 1  # Amplify invest amount by n times!
        configs = {
            LIConfigKey.aliasName: "NasdaqShort",
            LIConfigKey.monitorPeriod: 5,
            # LIConfigKey.closeWithStopOrderType: True,
            LIConfigKey.liquidateOnStopLossAmount: 20_000 * amplifier,  # Liquidate at certain point to stop trading!
            LIConfigKey.liquidateOnTakeProfitAmount: 10_000 * amplifier,
            LIConfigKey.gridShortLots: 20,
            # LIConfigKey.gridRetainOpenedLots: -1,
            # LIConfigKey.gridNoMoreOpenOrders: True,
            LIConfigKey.gridLotLevelPercent: 0.50,
            # LIConfigKey.gridLotLevelAugment: 0.015,
            LIConfigKey.gridLotStopLossFactor: 10,
            LIConfigKey.gridLotTakeProfitFactor: 5,
            LIConfigKey.gridLotStopProfitFactors: (0.5, 1.5),
            LIConfigKey.gridLotPauseAfterStopLoss: False,
            # LIConfigKey.gridLotMaxOpenPriceFactor: 1.0,  # Back fill open positions eagerly!
            LIConfigKey.gridLotMaxOpenPriceFactor: 0.5,  # Back fill open positions aggressively
            # LIConfigKey.gridRealignOpenPositions: True,
            LIConfigKey.gridInitializeSession: True,  # Be careful!
        }
        investAmount = LIInvestAmount(lotQuantity=1 * amplifier)
        self.liStrategies.append(LIFutureGridTradingContrarian(Futures.Indices.MicroNASDAQ100EMini, investAmount, **configs))

    # The momentum is hard to win on Nasdaq index futures!
    def futureGridTrading_Nasdaq_Momentum_NQ(self):
        self.SetCash(200_000)
        # Reverse to uptrend after big dip:
        # 5 mins: (189/101.22%/-24.5%)
        # 1 hour: (149/81.75%/-26.80%)
        # self.SetStartDate(date(2024, 4, 17))
        # self.SetEndDate(date(2024, 7, 10))
        # Reverse to uptrend after big dip
        # 5 mins: (312/68.48%/-36.70%)
        # 1 hour: (161/166.89%/-14.40%) -> (162/174.59%/-13.70%)
        self.SetStartDate(date(2025, 1, 1))
        self.SetEndDate(date(2025, 10, 1))

        # 2021 annual performance:
        # liquidateOnTakeProfitAmount 30_000: (710/171.34%/-42.70%)
        # self.SetStartDate(date(2021, 1, 1))
        # self.SetEndDate(date(2021, 12, 31))
        # 2022 annual performance: dropping market
        # liquidateOnTakeProfitAmount 5_000: (1077/29.25%/-81.10%)
        # self.SetStartDate(date(2022, 1, 1))
        # self.SetEndDate(date(2022, 12, 31))
        # 2023 annual performance:
        # liquidateOnTakeProfitAmount 50_000: (898/139.12%/-28.50%)
        # liquidateOnTakeProfitAmount 40_000: (827/183.54%/-30.00%)
        # liquidateOnTakeProfitAmount 30_000: (757/173.75%/-29.10%)
        # self.SetStartDate(date(2023, 1, 1))
        # self.SetEndDate(date(2023, 12, 31))
        # 2024 annual performance:
        # liquidateOnTakeProfitAmount 60_000: (668/255.05%/-47.80%)
        # liquidateOnTakeProfitAmount 50_000: (632/263.09%/-47.80%)
        # liquidateOnTakeProfitAmount 40_000: (612/140.08%/-54.10%)
        # liquidateOnTakeProfitAmount 30_000: (756/26.78%/-65.60%)
        # self.SetStartDate(date(2024, 1, 1))
        # self.SetEndDate(date(2024, 12, 31))

        amplifier = 1  # Amplify invest amount by n times!
        configs = {
            LIConfigKey.aliasName: "NasdaqTrend",
            # LIConfigKey.monitorPeriod: 5,
            LIConfigKey.monitorPeriod: 1,
            LIConfigKey.resolution: LIResolution.HOUR,
            # LIConfigKey.openWithStopOrderType: True,
            # LIConfigKey.futureContractExpiry: date(2025, 3, 21),
            # Adjust it dynamically based on current market trend/volatility and paired contrarian strategy's profit loss!
            LIConfigKey.liquidateOnTakeProfitAmounts: {LIGridSide.BTU: 50_000 * amplifier, LIGridSide.STD: 50_000 * amplifier},
            # LIConfigKey.gridBaselinePrice: 20_000,
            LIConfigKey.gridLongLots: 8,
            LIConfigKey.gridShortLots: 8,
            LIConfigKey.gridLotLevelPercent: 0.60,
            LIConfigKey.gridLotStopLossFactor: 7,
            LIConfigKey.gridLotTakeProfitFactor: 3,
            LIConfigKey.gridLotPauseAfterProfit: False,
            # LIConfigKey.gridMonitorPeriodFactors: {LIGridSide.STD: 1, LIGridSide.BTU: 12},
            # LIConfigKey.gridTransfer2Counterpart: True,
            LIConfigKey.gridInitializeSession: True,  # Be careful!
        }

        investAmount = LIInvestAmount(lotQuantity=1 * amplifier)
        self.liStrategies.append(LIFutureGridTradingMomentum(Futures.Indices.NASDAQ100EMini, investAmount, **configs))

    def futureGridTrading_Nasdaq_Combo_Hedge(self):
        self.SetCash(400_000)
        # (397/104.81%/-44.20%)
        self.SetStartDate(date(2024, 7, 1))
        self.SetEndDate(date(2024, 12, 1))
        # Better adjust settings due to the index price gap comparing to 2024
        # 2021 annual performance (1255/14.53%/-40.00%)
        # self.SetStartDate(date(2021, 1, 1))
        # self.SetEndDate(date(2021, 12, 31))
        # 2022 annual performance (3291/-94.97%/-97.60%) worst year!!!
        # self.SetStartDate(date(2022, 1, 1))
        # self.SetEndDate(date(2022, 12, 31))
        # 2023 annual performance (1125/79.86%/-24.80%)
        # self.SetStartDate(date(2023, 1, 1))
        # self.SetEndDate(date(2023, 12, 31))
        # 2024 annual performance (908/143.27/-30.10%)
        self.SetStartDate(date(2024, 1, 1))
        self.SetEndDate(date(2024, 12, 31))

        amplifier = 2  # Amplify invest amount by n times!
        configs = {
            LIConfigKey.aliasName: "NasdaqTrail",
            # LIConfigKey.verboseLogging: True,
            LIConfigKey.monitorPeriod: 60,  # 60 mins
            # LIConfigKey.monitorPeriod: 1,  # Perform worse than 60 mins?!
            # LIConfigKey.resolution: LIResolution.HOUR,
            # LIConfigKey.futureContractCode: "MNQ20Z24",
            # LIConfigKey.futureContractExpiry: date(2025, 3, 21),
            # LIConfigKey.closeWithStopOrderType: True,
            # LIConfigKey.liquidateOnStopLossAmount: 100_000,
            # Adjust it dynamically based on current market trend/volatility and paired momentum strategy's profit loss!
            LIConfigKey.liquidateOnTakeProfitAmount: 50_000 * amplifier,
            LIConfigKey.gridLongLots: 20,
            LIConfigKey.gridLotLevelPercent: 0.60,
            # LIConfigKey.gridLotLevelAugment: 0.015,  # Perform better in a long run with volatile market
            LIConfigKey.gridLotStopLossFactor: 25,
            LIConfigKey.gridLotStopProfitFactors: (0.5, 2),
            LIConfigKey.gridLotPauseAfterStopLoss: False,
            # LIConfigKey.gridLotBoostingProfitFactor: 3,  # Perform even worse in a long run with stable rising index futures
            # LIConfigKey.gridBoostingMaxHoldQuantity: 50,
            # LIConfigKey.gridBandingStartPrices: True,
            # LIConfigKey.gridBandingOpenFromPrices: True,
            # LIConfigKey.bollingerBandsParams: [(365, 1)],
            # LIConfigKey.gridRetainOpenedLots: 3,
            # LIConfigKey.gridRealignOpenPositions: True,
            LIConfigKey.gridInitializeSession: True,  # Be careful!
        }
        investAmount = LIInvestAmount(lotQuantity=1 * amplifier)
        self.liStrategies.append(LIFutureGridTradingContrarian(Futures.Indices.MicroNASDAQ100EMini, investAmount, **configs))

        configs = {
            LIConfigKey.aliasName: "NasdaqTrend",
            LIConfigKey.monitorPeriod: 1,
            LIConfigKey.resolution: LIResolution.HOUR,
            # LIConfigKey.openWithStopOrderType: True,
            # LIConfigKey.futureContractExpiry: date(2025, 3, 21),
            # Adjust it dynamically based on current market trend/volatility and paired contrarian strategy's profit loss!
            LIConfigKey.liquidateOnTakeProfitAmounts: {LIGridSide.BTU: 50_000, LIGridSide.STD: 50_000},
            LIConfigKey.gridLongLots: 8,
            LIConfigKey.gridShortLots: 8,
            LIConfigKey.gridLotLevelPercent: 0.60,
            LIConfigKey.gridLotStopLossFactor: 8,
            LIConfigKey.gridLotTakeProfitFactor: 3,
            LIConfigKey.gridLotPauseAfterProfit: False,
            # LIConfigKey.gridTransfer2Counterpart: True,
            LIConfigKey.gridInitializeSession: True,  # Be careful!
        }

        investAmount = LIInvestAmount(lotQuantity=1)
        self.liStrategies.append(LIFutureGridTradingMomentum(Futures.Indices.NASDAQ100EMini, investAmount, **configs))

    def futureGridTrading_10YNote_Contrarian(self):
        self.SetCash(200_000)
        # Big Down/Up V trend
        self.SetStartDate(date(2024, 1, 1))
        self.SetEndDate(date(2024, 8, 1))

        configs = {
            LIConfigKey.aliasName: "10YNoteTrail",
            LIConfigKey.monitorPeriod: 60,  # 5 mins
            LIConfigKey.futureRolloverDays: 28,  # Match ZN's odd calendar!
            # LIConfigKey.fetchHistoryBarData: False,
            # LIConfigKey.liquidateAndStopTrading: True,
            # LIConfigKey.gridNoMoreOpenOrders: True,
            LIConfigKey.closeWithStopOrderType: True,
            LIConfigKey.gridLongLots: 15,
            # LIConfigKey.gridRetainOpenedLots: 2,
            LIConfigKey.gridLotLevelPercent: 0.321,
            LIConfigKey.gridLotLevelAugment: 0.00625,
            LIConfigKey.gridLotStopLossFactor: 20,
            LIConfigKey.gridLotStopProfitFactors: (0.5, 2),
            LIConfigKey.gridLimitStartPrices: {LIGridSide.BTD: 120.0},
            # LIConfigKey.gridFixedStartPrices: {LIGridSide.BTD: 110.0},
            LIConfigKey.gridInitializeSession: True,  # Be careful!
        }

        investAmount = LIInvestAmount(lotQuantity=1)
        self.liStrategies.append(LIFutureGridTradingContrarian(Futures.Financials.Y10TreasuryNote, investAmount, **configs))

    def futureGridTrading_10YNote_Trail_Short(self):
        self.SetCash(200_000)
        # Big Down/Up V trend
        self.SetStartDate(date(2023, 1, 1))
        # self.SetStartDate(date(2024, 1, 1))
        self.SetEndDate(date(2025, 1, 1))

        configs = {
            LIConfigKey.aliasName: "10YNoteShort",
            LIConfigKey.monitorPeriod: 60,  # 5 mins
            LIConfigKey.futureRolloverDays: 28,  # Match ZN's odd calendar!
            # LIConfigKey.fetchHistoryBarData: False,
            # LIConfigKey.liquidateAndStopTrading: True,
            # LIConfigKey.gridNoMoreOpenOrders: True,
            LIConfigKey.closeWithStopOrderType: True,
            LIConfigKey.gridShortLots: 15,
            # LIConfigKey.gridRetainOpenedLots: 2,
            LIConfigKey.gridLotLevelPercent: 0.321,
            LIConfigKey.gridLotLevelAugment: 0.00625,
            LIConfigKey.gridLotStopLossFactor: 20,
            LIConfigKey.gridLotStopProfitFactors: (0.5, 2),
            LIConfigKey.gridLimitStartPrices: {LIGridSide.STU: 105.0},
            # LIConfigKey.gridFixedStartPrices: {LIGridSide.BTD: 115.0},
            LIConfigKey.gridInitializeSession: True,  # Be careful!
        }

        investAmount = LIInvestAmount(lotQuantity=1)
        self.liStrategies.append(LIFutureGridTradingContrarian(Futures.Financials.Y10TreasuryNote, investAmount, **configs))

    def futureGridTrading_10YNote_Momentum(self):
        self.SetCash(200_000)
        self.SetStartDate(date(2024, 7, 1))
        # self.SetEndDate(date(2024, 8, 5))
        self.SetEndDate(date(2024, 11, 5))

        configs = {
            LIConfigKey.aliasName: "10YNoteTrend",
            LIConfigKey.monitorPeriod: 5 * 12,
            LIConfigKey.futureRolloverDays: 28,  # Match ZN's odd calendar!
            # LIConfigKey.openWithStopOrderType: True,
            # LIConfigKey.closeWithStopOrderType: True,
            # LIConfigKey.enableLimitMarketOrder: True,
            # LIConfigKey.liquidateAndStopTrading: True,
            # LIConfigKey.liquidateOnStopLossAmount: 30_000,
            LIConfigKey.liquidateOnTakeProfitAmount: 20_000,
            # Adjust it dynamically based on current market trend/volatility and contrarian strategy's profit loss!
            LIConfigKey.liquidateByTrailingProfitPercent: 15,
            LIConfigKey.liquidateProfitAndRestartTrading: True,
            LIConfigKey.gridLongLots: 30,
            LIConfigKey.gridShortLots: 30,
            # LIConfigKey.gridInitOpenedLots: -2,
            LIConfigKey.gridLotLevelPercent: 0.25,
            LIConfigKey.gridLotStopLossFactor: 30,  # Disable stop loss
            LIConfigKey.gridLotTakeProfitFactor: 10,  # Delay taking profit
            LIConfigKey.gridLotPauseAfterProfit: False,
            # LIConfigKey.gridLotBoostingProfitFactor: 2,
            # LIConfigKey.gridLotBoostingDesireProfit: True,
            # LIConfigKey.gridBoostingMaxHoldQuantity: 100,
            # LIConfigKey.gridRealignOpenPositions: True,
            LIConfigKey.gridInitializeSession: True,  # Be careful!
        }
        investAmount = LIInvestAmount(lotQuantity=1)
        self.liStrategies.append(LIFutureGridTradingMomentum(Futures.Financials.Y10TreasuryNote, investAmount, **configs))

    def futureGridTrading_10YNote_Scalp_ZN(self):
        self.SetCash(500_000)
        # Big Down/Up V trend
        self.SetStartDate(date(2023, 10, 12))
        self.SetEndDate(date(2023, 11, 12))
        # Overall Up trend with small waves
        self.SetStartDate(date(2024, 1, 1))
        self.SetEndDate(date(2024, 3, 10))
        # Up/Down/Up/Down/Up volatile market
        # self.SetStartDate(date(2024, 2, 1))
        # self.SetEndDate(date(2024, 2, 28))
        # Big up/down/up/down
        # self.SetStartDate(date(2024, 2, 29))
        # self.SetEndDate(date(2024, 3, 11))
        # Big jump
        # self.SetStartDate(date(2024, 2, 19))
        # self.SetEndDate(date(2024, 2, 23))
        # Medium jump
        # self.SetStartDate(date(2024, 3, 19))
        # self.SetEndDate(date(2024, 3, 23))
        # 2 months about 5+ up/down waves
        # self.SetStartDate(date(2024, 2, 1))
        # self.SetEndDate(date(2024, 4, 1))
        # 2 stages sharp uptrend
        # self.SetStartDate(date(2024, 2, 21))
        # self.SetEndDate(date(2024, 3, 2))
        # Flat 2 months (negative profit)
        self.SetStartDate(date(2024, 2, 8))
        self.SetEndDate(date(2024, 4, 8))
        # Up/Down big wave with volatile market
        self.SetStartDate(date(2024, 1, 1))
        # self.SetStartDate(date(2024, 7, 1))
        # self.SetStartDate(date(2024, 7, 23))
        self.SetEndDate(date(2024, 7, 27))

        # 24/7/23-24/7/27: 1 min (156/25.61%/-10.80%), 5 mins (129/26.01%/-11.10%)
        # 24/7/1-24/7/27: 1 min (440/80.12%/-10.80%), 5 mins (387/70.20%/-13.00%)
        # 24/1/1-24/7/27: 1 min (2647/155.56%/-17.90%), 5 mins (2276/118.57%/-19.90%)
        # 24/1/1-24/3/10: 1 min (806/42.60%/-13.10%), 5 mins (686/36.48%/-13.50%)
        # 24/2/8-24/4/8: 1 min (758/13.56%/-15.60%), 5 mins (579/9.04%/-15.50%)
        configs1 = {
            LIConfigKey.aliasName: "TreasuryScalp",
            LIConfigKey.monitorPeriod: 5,
            # LIConfigKey.verboseLogging: True,
            LIConfigKey.futureRolloverDays: 28,  # Match ZN's odd calendar!
            # LIConfigKey.openWithStopOrderType: True,
            # LIConfigKey.closeWithStopOrderType: True,
            LIConfigKey.disableBuyingPowerModel: True,
            # LIConfigKey.liquidateAndStopTrading: True,
            # LIConfigKey.gridNoMoreOpenOrders: True,
            LIConfigKey.gridLongLots: 8,
            LIConfigKey.gridShortLots: 6,
            # LIConfigKey.gridInitOpenedLots: -1,
            # LIConfigKey.gridLotLevelAmount: 50,
            LIConfigKey.gridLotLevelPercent: 0.3,
            LIConfigKey.gridLotStopLossFactor: 1,
            LIConfigKey.gridLotTakeProfitFactor: 2,
            LIConfigKey.gridLotStopProfitFactors: (0.5, 2),
            LIConfigKey.gridBoostingKeepTrading: True,
            LIConfigKey.gridBoostingTriggerAmount: 120,
            LIConfigKey.gridBoostingMaxHoldQuantity: 25,
            LIConfigKey.gridBoostingStopProfitAmounts: (100, 75),
            LIConfigKey.gridInitializeSession: True,  # Be careful!
        }

        # 24/7/23-24/7/27: 1 min (164/28.53%/-9.40%), 5 mins (111/30.43%/-8.50%)
        # 24/7/1-24/7/27: 1 min (449/80.64%/-10.90%), 5 mins (365/72.53%/-12.80%)
        # 24/1/1-24/7/27: 1 min (2717/129.04%/-21.60%), 5 mins (2369/113.63%/-20.00%)
        # 24/1/1-24/3/10: 1 min (838/3.75%/-16.90%), 5 mins (731/17.76%/-13.6%)
        # 24/2/8-24/4/8: 1 min (735/9.37%/-13.90%), 5 mins (607/0.19%/-15.70%)
        configs = {
            LIConfigKey.aliasName: "TreasuryScalp",
            LIConfigKey.monitorPeriod: 5,
            # LIConfigKey.verboseLogging: True,
            LIConfigKey.futureRolloverDays: 28,  # Match ZN's odd calendar!
            # LIConfigKey.openWithStopOrderType: True,
            # LIConfigKey.closeWithStopOrderType: True,
            LIConfigKey.disableBuyingPowerModel: True,
            # LIConfigKey.liquidateAndStopTrading: True,
            # LIConfigKey.gridNoMoreOpenOrders: True,
            LIConfigKey.gridLongLots: 8,
            LIConfigKey.gridShortLots: 6,
            # LIConfigKey.gridInitOpenedLots: -1,
            LIConfigKey.gridLotLevelPercent: 0.3,
            LIConfigKey.gridLotStopLossFactor: 1,
            LIConfigKey.gridLotTakeProfitFactor: 2,
            LIConfigKey.gridLotStopProfitFactors: (0.5, 2),
            LIConfigKey.gridBoostingKeepTrading: True,
            LIConfigKey.gridBoostingMaxHoldQuantity: 25,
            # LIConfigKey.gridBoostingTrailingStopQuantity: 20,
            # LIConfigKey.gridBoostingTriggerPercent: 0.5,
            # LIConfigKey.gridBoostingStopProfitPercents: (0.45, 0.35),
            LIConfigKey.gridBoostingTriggerPercent: 0.568,  # 0.58
            LIConfigKey.gridBoostingStopProfitPercents: (0.473, 0.355),  # (0.4833, 0.3625)
            # LIConfigKey.gridBoostingTriggerPercent: 0.618,
            # LIConfigKey.gridBoostingStopProfitPercents: (0.515, 0.386),
            # LIConfigKey.gridRestartOnFridayClose: True,  # Reduce drawdown and profit
            LIConfigKey.gridInitializeSession: True,  # Be careful!
        }

        investAmount = LIInvestAmount(lotQuantity=1)
        self.liStrategies.append(LIFutureGridTradingMomentum(Futures.Financials.Y10TreasuryNote, investAmount, **configs))

    def futureGridTrading_USD_Trail(self):
        self.SetCash(200_000)  # Margin $2,100
        # LIConfigKey.gridLimitStartPrices: {LIGridSide.BTD: 1.1, LIGridSide.STU: 1.1},
        # 78/12.12%
        # self.SetStartDate(date(2023, 11, 23))
        # self.SetEndDate(date(2023, 12, 28))
        # 981/126.27%
        # self.SetStartDate(date(2023, 5, 1))
        # self.SetEndDate(date(2024, 1, 10))
        # self.SetStartDate(date(2024, 5, 10))
        # self.SetStartDate(date(2024, 9, 10))
        # self.SetEndDate(date(2024, 10, 10))
        # Bounce above and below 1.08 middle line (171/23.32%/-6.3%)
        self.SetStartDate(date(2024, 11, 1))
        self.SetEndDate(date(2024, 11, 15))

        configs = {
            LIConfigKey.aliasName: "USDTrail",
            LIConfigKey.monitorPeriod: 5,
            # LIConfigKey.closeWithStopOrderType: True,
            # LIConfigKey.submitTrailingStopOrder: True,
            LIConfigKey.disableBuyingPowerModel: False,
            LIConfigKey.liquidateOnStopLossAmount: 50_000,
            LIConfigKey.gridLongLots: 20,
            LIConfigKey.gridShortLots: 20,
            # LIConfigKey.gridLotLevelAmount: 0.14365
            LIConfigKey.gridLotLevelPercent: 0.139,
            LIConfigKey.gridLotStopLossFactor: 25,
            LIConfigKey.gridLotStopProfitFactors: (0.5, 2),
            # LIConfigKey.gridInitOpenedLots: 2,
            # LIConfigKey.gridRetainOpenedLots: 2,
            # LIConfigKey.gridFixLeakingPositions: True,
            LIConfigKey.gridFixedStartPrices: {LIGridSide.BTD: 103.346, LIGridSide.STU: 103.346},
            # LIConfigKey.gridBandingStartPrices: True,
            LIConfigKey.gridInitializeSession: True,  # Be careful!
        }
        investAmount = LIInvestAmount(lotQuantity=1)
        self.liStrategies.append(LIFutureGridTradingContrarian(Futures.Currencies.USD, investAmount, **configs))

    def futureGridTrading_Euro_Contrarian(self):
        self.SetCash(300_000)  # Margin $2,100
        amplifier = 1  # Amplify invest amount by n times!

        # 2021 annual performance (225/70.82%/-32.00%) - (365, 0)
        # 2021 annual performance (124/86.24%/-29.20%) - (365, 1)
        # self.SetStartDate(date(2021, 1, 1))
        # self.SetEndDate(date(2021, 12, 31))
        # 2022 annual performance (53/-55.89%/-65.40%) - (365, 1)
        # 2022 annual performance (53/-55.89%/-65.40%) - (365, 0)
        # self.SetStartDate(date(2022, 1, 1))
        # self.SetEndDate(date(2022, 12, 31))
        # 2023 annual performance (433/105.05%/-13.10%) - (365, 0)
        # 2023 annual performance (52/38.64%/-5.50%) - (365, 1)
        # self.SetStartDate(date(2023, 1, 1))
        # self.SetEndDate(date(2023, 12, 31))
        # 2024 annual performance (254/47.25%/-26.70%) - (365, 0)
        # 2024 annual performance (183/44.54%/-27.90%) - (365, 1)
        # self.SetStartDate(date(2024, 9, 25))
        self.SetStartDate(date(2024, 11, 5))
        self.SetEndDate(date(2024, 11, 25))

        configs = {
            LIConfigKey.aliasName: "EuroTrail",
            # LIConfigKey.verboseLogging: True,
            # LIConfigKey.monitorPeriod: 5,
            LIConfigKey.monitorPeriod: 1,
            LIConfigKey.resolution: LIResolution.HOUR,
            # LIConfigKey.closeWithStopOrderType: True,
            # LIConfigKey.disableBuyingPowerModel: False,
            # LIConfigKey.forceExchangeOpen: True,
            # LIConfigKey.futureContractExpiry: date(2025, 3, 17),
            LIConfigKey.liquidateOnStopLossAmount: 100_000 * amplifier,
            LIConfigKey.liquidateOnTakeProfitAmount: 50_000 * amplifier,
            # LIConfigKey.liquidateByTrailingProfitPercent: 15,
            # LIConfigKey.liquidateLossAndRestartTrading: True, # Study market and pick another entry point!
            LIConfigKey.gridLongLots: 20,
            LIConfigKey.gridShortLots: 20,
            LIConfigKey.gridLotLevelPercent: 0.2,
            LIConfigKey.gridLotStopProfitFactors: (0.5, 1),
            LIConfigKey.gridLotStopLossFactor: 25,
            LIConfigKey.gridLotPauseAfterStopLoss: True,
            # LIConfigKey.gridLotBoostingProfitFactor: 2,
            # LIConfigKey.gridLotBoostingDesireProfit: True,
            # LIConfigKey.gridBoostingMaxHoldQuantity: 30,
            # LIConfigKey.gridInitOpenedLots: 2,
            # LIConfigKey.gridRetainOpenedLots: 2,
            # LIConfigKey.gridResetLotsMetadata: True,
            # LIConfigKey.gridCloseCounterpartLots: False,
            # LIConfigKey.gridFixedStartPrices: {LIGridSide.BTD: 1.075, LIGridSide.STU: 1.075},  # Based on QuantConnect
            LIConfigKey.gridBandingStartPrices: True,
            # LIConfigKey.gridBandingOpenFromPrices: True,
            LIConfigKey.gridFixedStartBandName: "band-#0-middle",
            LIConfigKey.bollingerBandsParams: [(300, 1), (300, 2), (300, 3)],
            LIConfigKey.investAmountTierFactors: [4, 3, 2, 1, 1, 2, 3, 4],  # Mapping band tiers from upper to lower
            LIConfigKey.gridInitializeSession: True,  # Be careful!
        }
        investAmount = LIInvestAmount(lotQuantity=1 * amplifier)
        self.liStrategies.append(LIFutureGridTradingContrarian(Futures.Currencies.EUR, investAmount, **configs))

    def futureGridTrading_Euro_Contrarian_Scalp(self):
        self.SetCash(100_000)  # Margin $2,100
        amplifier = 2  # Amplify invest amount by n times!

        # Consistent down trend! LOSS!
        # self.SetStartDate(date(2022, 2, 15))
        # self.SetEndDate(date(2022, 10, 15))
        # A few up and down trend
        # self.SetStartDate(date(2024, 1, 1))
        # self.SetEndDate(date(2024, 9, 15))
        # Big down trend
        self.SetStartDate(date(2024, 9, 17))
        self.SetEndDate(date(2025, 12, 15))
        configs = {
            LIConfigKey.aliasName: "EuroScalp",
            LIConfigKey.monitorPeriod: 5,
            # LIConfigKey.monitorPeriod: 1,
            # LIConfigKey.resolution: LIResolution.HOUR,
            # LIConfigKey.closeWithStopOrderType: True,
            LIConfigKey.futureContractExpiry: date(2025, 3, 17),
            LIConfigKey.liquidateLossAndRestartTrading: True,
            LIConfigKey.liquidateOnStopLossAmount: 5000 * amplifier,
            LIConfigKey.liquidateOnTakeProfitAmount: 5000 * amplifier,
            # LIConfigKey.liquidateOnTakeProfitAmount: 2500 * amplifier,
            LIConfigKey.gridLongLots: 10,
            LIConfigKey.gridShortLots: 10,
            LIConfigKey.gridLotLevelPercent: 0.15,
            LIConfigKey.gridLotStopProfitFactors: (0.5, 1),
            LIConfigKey.gridLotStopLossFactor: 15,
            # LIConfigKey.gridInitOpenedLots: 2,
            # LIConfigKey.gridResetLotsMetadata: True,
            # LIConfigKey.gridRealignOpenPositions: True,
            LIConfigKey.gridBandingStartPrices: True,
            LIConfigKey.gridBandingOpenFromPrices: True,
            # LIConfigKey.bollingerBandsParams: [(200, 2, LIResolution.HOUR)],
            LIConfigKey.bollingerBandsParams: [(300, 2, LIResolution.HOUR)],  # 245/55.67%/-34.60%
            # LIConfigKey.bollingerBandsParams: [(400, 2, LIResolution.HOUR)],
            LIConfigKey.gridInitializeSession: True,  # Be careful!
        }
        investAmount = LIInvestAmount(lotQuantity=1 * amplifier)
        self.liStrategies.append(LIFutureGridTradingContrarian(Futures.Currencies.EUR, investAmount, **configs))

    def futureGridTrading_Euro_Momentum(self):
        self.SetCash(200_000)
        amplifier = 2  # Amplify invest amount by n times!

        # Bounce within bollinger bands:
        # Fixed start prices: (2/-0.92%/-2.10%)
        # Dynamic start prices: (5/-0.35%/-1.50%)
        # self.SetStartDate(date(2024, 4, 15))
        # self.SetEndDate(date(2024, 8, 15))
        # Big dip all the way to bottom (253/112.93%/-32.90%)
        # self.SetStartDate(date(2024, 6, 1))
        # self.SetEndDate(date(2024, 12, 31))
        # self.SetStartDate(date(2024, 11, 1))
        # self.SetEndDate(date(2024, 12, 31))
        # 2021 annual performance (64/10.89%/-48.70%)
        # self.SetStartDate(date(2021, 1, 1))
        # self.SetEndDate(date(2021, 12, 31))
        # 2022 annual performance (442/191.22%/-64.10%) - None
        # 2022 annual performance (417/159.38%/-64.90%) - (365, 0)
        # 2022 annual performance (396/165.74%/-64.90%) - (365, 1)
        # 2022 annual performance (211/-11.13%/-75.50%) - (365, 2)
        # self.SetStartDate(date(2022, 1, 1))
        # self.SetEndDate(date(2022, 12, 31))
        # 2023 annual performance (60/74.25%/-24.90%) - (365, 1)
        # 2023 annual performance (0/0/-0%) - (365, 2)
        # self.SetStartDate(date(2023, 1, 1))
        # self.SetEndDate(date(2023, 12, 31))
        # 2024 annual performance (162/39.62%/-48.10%) - (361, 1)
        # 2024 annual performance (95/52.59%/-24.20%) - (365, 2)
        self.SetStartDate(date(2024, 1, 1))
        self.SetEndDate(date(2024, 12, 31))

        configs = {
            LIConfigKey.aliasName: "EuroTrend",
            # LIConfigKey.monitorPeriod: 5 * 12, # Better than 1 hour sometimes!
            LIConfigKey.monitorPeriod: 1,
            LIConfigKey.resolution: LIResolution.HOUR,
            # LIConfigKey.openWithStopOrderType: True,
            # LIConfigKey.closeWithStopOrderType: True,
            # LIConfigKey.submitTrailingStopOrder: True,
            # LIConfigKey.disableBuyingPowerModel: True,
            # LIConfigKey.enableLimitMarketOrder: True,
            # Adjust it dynamically based on current market trend/volatility and contrarian strategy's profit loss!
            LIConfigKey.liquidateOnTakeProfitAmounts: {LIGridSide.BTU: 50_000 * amplifier, LIGridSide.STD: 50_000 * amplifier},
            # LIConfigKey.liquidateByTrailingProfitPercent: 15,
            # LIConfigKey.liquidateWithStopOrderType: True,
            LIConfigKey.gridLongLots: 40,  # Can add more if required
            LIConfigKey.gridShortLots: 40,  # Can add more if required
            LIConfigKey.gridLotLevelPercent: 0.185,  # Not set it too narrow
            LIConfigKey.gridLotStopLossFactor: 40,
            LIConfigKey.gridLotTakeProfitFactor: 20,
            LIConfigKey.gridLotPauseAfterProfit: False,
            LIConfigKey.gridBandingOpenFromPrices: True,
            # LIConfigKey.bollingerBandsParams: [(365, 0)],  # 0 for bouncing in bands
            LIConfigKey.bollingerBandsParams: [(365, 1)],  # 1 for one side trending
            # LIConfigKey.bollingerBandsParams: [(365, 2)],  # 2 for up and down trending
            LIConfigKey.gridInitializeSession: True,  # Be careful!
        }
        investAmount = LIInvestAmount(lotQuantity=1 * amplifier)
        self.liStrategies.append(LIFutureGridTradingMomentum(Futures.Currencies.EUR, investAmount, **configs))

    def equityGridTrading_USTech_3X(self):
        self.SetCash(50_000)
        # self.SetStartDate(date(2022, 9, 1))
        # self.SetStartDate(date(2022, 11, 1))
        # self.SetEndDate(date(2022, 11, 30))
        # self.SetStartDate(date(2022, 12, 1))
        # self.SetEndDate(date(2022, 12, 31))
        # self.SetStartDate(date(2023, 7, 18))
        # self.SetEndDate(date(2023, 11, 18))
        self.SetStartDate(date(2024, 3, 1))
        self.SetEndDate(date(2024, 6, 1))

        configs = {
            LIConfigKey.aliasName: "USTech",
            LIConfigKey.extendedMarketHours: True,
            LIConfigKey.fetchHistoryBarData: False,
            LIConfigKey.closeWithStopOrderType: True,  # Perform better!
            # LIConfigKey.gridNoMoreOpenOrders: True,
            LIConfigKey.gridLongLots: 20,
            LIConfigKey.gridLotMinQuantity: 20,
            LIConfigKey.gridLotLevelPercent: 2,
            LIConfigKey.gridRetainOpenedLots: 8,
            LIConfigKey.gridLotStopProfitFactors: (0.5, 0.5),
            # LIConfigKey.gridRealignOpenPositions: True,
            # LIConfigKey.gridResetLotsMetadata: True,
            # LIConfigKey.gridFixedStartPrices: {LIGridSide.BTD: 80},
            LIConfigKey.gridInitializeSession: True,  # Be careful! (mostly used in backtest)
        }
        investAmount = LIInvestAmount(maxHolding=1)
        # investAmount = LIInvestAmount(maxCapital=50_000)
        self.liStrategies.append(LIEquityGridTradingContrarian("TECL", investAmount, **configs))

    def equityGridTrading_ChipTech_3X(self):
        self.SetCash(50_000)
        self.SetStartDate(date(2023, 10, 12))
        self.SetEndDate(date(2023, 12, 12))

        configs = {
            LIConfigKey.aliasName: "ChipTech",
            LIConfigKey.extendedMarketHours: True,
            LIConfigKey.gridLongLots: 20,
            LIConfigKey.gridLotLevelPercent: 2,
            LIConfigKey.gridRetainOpenedLots: 5,
            # LIConfigKey.gridFixedStartPrices: {LIGridSide.BTD: 60},
            LIConfigKey.gridInitializeSession: True,  # Be careful!!!
        }
        investAmount = LIInvestAmount(maxCapital=50_000)
        # investAmount = LIInvestAmount(maxQuantity=2000)
        self.liStrategies.append(LIEquityGridTradingContrarian("SOXL", investAmount, **configs))

        # def equityGridTrading_Global_Stock(self):
        self.SetCash(100_000)
        # Bear market
        # self.SetStartDate(date(2021, 11, 19))
        # self.SetEndDate(date(2022, 10, 28))
        # self.SetStartDate(date(2022, 9, 1))
        # self.SetStartDate(date(2022, 11, 1))
        # self.SetEndDate(date(2022, 11, 30))
        # self.SetStartDate(date(2022, 12, 1))
        # self.SetEndDate(date(2022, 12, 31))
        self.SetStartDate(date(2023, 3, 1))
        self.SetEndDate(date(2023, 4, 8))

        configs = {
            LIConfigKey.monitorPeriod: 5,
            LIConfigKey.extendedMarketHours: True,
            LIConfigKey.gridLongLots: 10,
            LIConfigKey.gridLotLevelPercent: 1,
            LIConfigKey.gridLotTakeProfitFactor: 1.0,
            LIConfigKey.gridInitializeSession: True,  # Be careful!!!
            # LIConfigKey.gridFixedStartPrices: {LIGridSide.BTD: 95.0},
            # LIConfigKey.liquidateOnStopLossPercent: 10,
        }
        # investAmount = LIInvestAmount(maxHolding=1)
        investAmount = LIInvestAmount(maxCapital=100_000)
        self.liStrategies.append(LIEquityGridTradingContrarian("VT", investAmount, **configs))

    def equityGridTrading_SPY_DCA(self):
        self.SetCash(500_000)
        # 2 Years of V trend
        # self.SetStartDate(date(2022, 1, 1))
        # self.SetEndDate(date(2024, 1, 1))
        # 6 Months of V trend
        # self.SetStartDate(date(2022, 8, 15))
        # self.SetEndDate(date(2023, 2, 15))
        # Temp test trend (62/0.34%)
        self.SetStartDate(date(2022, 10, 1))
        self.SetEndDate(date(2023, 3, 10))

        configs = {
            LIConfigKey.monitorPeriod: 60,
            LIConfigKey.dcaInvestCapital: 10_000,
            LIConfigKey.dcaInvestPeriodicity: LIPeriodicity.WEEKLY,
            LIConfigKey.gridLongLots: 20,
            LIConfigKey.gridLotMinQuantity: 10,
            LIConfigKey.gridLotLevelPercent: 1.5,
            LIConfigKey.gridInitializeSession: True,  # Be careful!!!
        }
        investAmount = LIInvestAmount(maxCapital=200_000)
        self.liStrategies.append(LIEquityGridTradingBuyAndHold("SPY", investAmount, **configs))

    def equityGridTrading_IXN_DCA(self):
        self.SetCash(500_000)
        # (102/6.47%)
        self.SetStartDate(date(2024, 1, 1))
        self.SetEndDate(date(2024, 11, 1))

        configs = {
            LIConfigKey.monitorPeriod: 60,
            LIConfigKey.extendedMarketHours: True,
            LIConfigKey.dcaInvestCapital: 5_000,
            LIConfigKey.dcaInvestPeriodicity: LIPeriodicity.WEEKLY,
            LIConfigKey.gridLongLots: 20,
            LIConfigKey.gridLotMinQuantity: 10,
            LIConfigKey.gridLotLevelPercent: 2,
            LIConfigKey.gridUseHeikinAshi: True,
            # LIConfigKey.gridResetStartPrices: {LIGridSide.BTD: 70},
            LIConfigKey.gridInitializeSession: True
        }
        investAmount = LIInvestAmount(maxCapital=100_000)
        self.liStrategies.append(LIEquityGridTradingBuyAndHold("IXN", investAmount, **configs))

    def optionGridTrading_QQQ_Trend(self):
        self.SetCash(10_000)
        # Down/Up/Down/Up Overall down trend
        # self.SetStartDate(date(2023, 9, 12))
        # self.SetEndDate(date(2023, 11, 12))
        # Down/Up Overall V trend LOSS CASE!
        self.SetStartDate(date(2023, 10, 12))
        self.SetEndDate(date(2023, 11, 12))
        # 0.5/185/650.06%/285281417390819000%
        # 1.5/94/245.34%/320693438348.334% -> 97/218.56%/77087248845.552%
        # self.SetStartDate(date(2023, 5, 11))
        # self.SetEndDate(date(2023, 5, 15))
        # self.SetStartDate(date(2023, 5, 25))
        # self.SetEndDate(date(2023, 5, 31))

        configs = {
            LIConfigKey.aliasName: "QQQPut",
            LIConfigKey.monitorPeriod: 5,
            LIConfigKey.plotDefaultChart: True,
            LIConfigKey.rolloverHoldings: False,
            LIConfigKey.optionRight: OptionRight.Put,
            # LIConfigKey.optionContractCode: "QQQ 230616P00318000",
            # LIConfigKey.optionMinMaxExpiryDays: [10, 35],
            # LIConfigKey.optionMinMaxStrikeLevel: [-10, +10],
            # LIConfigKey.disableBuyingPowerModel: True,
            # LIConfigKey.liquidateAndStopTrading: True,
            LIConfigKey.gridLongLots: 5,  # Only buy puts
            LIConfigKey.gridShortLots: 5,  # Delegate to calls
            LIConfigKey.gridLotLevelPercent: 1.5,
            LIConfigKey.gridLotStopLossFactor: 3,
            LIConfigKey.gridLotTakeProfitFactor: 8,
            LIConfigKey.closeWithStopOrderType: False,
            LIConfigKey.gridLotStopProfitFactors: (2, 2),
            LIConfigKey.gridLotMaxProfitFactor: 16,
            # LIConfigKey.liquidateOnTakeProfitAmount: 50_000,
            # LIConfigKey.liquidateProfitAndRestartTrading: False,
            LIConfigKey.gridInitializeSession: True,  # Be careful!
        }
        investAmount = LIInvestAmount(lotQuantity=2)
        self.liStrategies.append(LIOptionGridTradingMomentum("QQQ", investAmount, **configs))

        configs = {
            LIConfigKey.aliasName: "QQQCall",
            LIConfigKey.monitorPeriod: 5,
            LIConfigKey.plotDefaultChart: True,
            LIConfigKey.rolloverHoldings: False,
            LIConfigKey.optionRight: OptionRight.Call,
            # LIConfigKey.optionContractCode: "QQQ 230616C00334000",
            # LIConfigKey.optionMinMaxExpiryDays: [10, 35],
            # LIConfigKey.optionMinMaxStrikeLevel: [-10, +10],
            # LIConfigKey.disableBuyingPowerModel: True,
            # LIConfigKey.liquidateAndStopTrading: True,
            LIConfigKey.gridLongLots: 5,  # Only buy calls
            LIConfigKey.gridShortLots: 5,  # Delegate to puts
            LIConfigKey.gridLotLevelPercent: 1.5,
            LIConfigKey.gridLotStopLossFactor: 3,
            LIConfigKey.gridLotTakeProfitFactor: 8,
            LIConfigKey.closeWithStopOrderType: False,
            LIConfigKey.gridLotStopProfitFactors: (2, 2),
            LIConfigKey.gridLotMaxProfitFactor: 16,
            # LIConfigKey.liquidateOnTakeProfitAmount: 50_000,
            # LIConfigKey.liquidateProfitAndRestartTrading: False,
            LIConfigKey.gridInitializeSession: True,  # Be careful!
        }
        investAmount = LIInvestAmount(lotQuantity=2)
        self.liStrategies.append(LIOptionGridTradingMomentum("QQQ", investAmount, **configs))
