from AlgorithmImports import *
from core.LIAlgorithm import *


class LifelongInvestorMain(LIAlgorithm):

    def initialize(self):
        super().initialize()
        setLogSize(500)  # Only for backtesting
        setAlgoName("Backtest")  # Invest account name
        addNotifySetting(LINotifyType.TELEGRAM, "-913280749")
        addAlertSetting(LINotifyType.EMAIL, "lifelonginvestorllc@gmail.com")
        # liquidateAndStopTrading() # Liquidate all strategies in emergency!
        # replicateMetadataFrom(15964868)  # Replicate metadata from this project

        if self.live_mode:
            terminate(f"This project is for backtest only!")

        self.futureGridTrading_Nasdaq_Scalp_NQ()
        # self.futureGridTrading_Nasdaq_Scalp_NQ2()
        # self.futureGridTrading_Nasdaq_Scalp_MNQ()

    def futureGridTrading_Nasdaq_Scalp_NQ(self):
        self.set_cash(500_000)
        # Up/Down big wave with volatile market
        # (0.45, 0.35): (566/132.57%/-11.7%); (0.2, 0.4): (596/72.73%/-14.2%)
        self.set_start_date(date(2024, 7, 1))
        self.set_end_date(date(2024, 7, 31))

        configs = {
            LIConfigKey.aliasName: "NasdaqScalp",
            LIConfigKey.monitorPeriod: (5, LIResolution.MINUTE),
            LIConfigKey.disableBuyingPowerModel: True,
            LIConfigKey.openWithMarketOrderType: True,
            LIConfigKey.gridLongLots: 8,
            LIConfigKey.gridShortLots: 6,
            LIConfigKey.gridLotLevelPercent: 0.3,
            # LIConfigKey.gridLotLevelPercent: 0.35,
            LIConfigKey.gridLotStopLossFactor: 1,
            LIConfigKey.gridLotTakeProfitFactor: 2,
            LIConfigKey.gridLotStopProfitFactors: (0.5, 2),
            LIConfigKey.gridBoostingKeepTrading: True,
            LIConfigKey.gridBoostingMaxHoldQuantity: 30,
            LIConfigKey.gridBoostingTriggerPercent: 0.5,  # Best lately
            LIConfigKey.gridBoostingStopProfitPercents: (0.45, 0.35),
            # LIConfigKey.gridBoostingStopProfitPercents: (0.2, 0.4),
            LIConfigKey.gridInitializeSession: True,  # Be careful!
        }

        investAmount = LIInvestAmount(lotQuantity=1)
        self.liStrategies.append(LIFutureGridTradingMomentum(Futures.Indices.NASDAQ100EMini, investAmount, **configs))

    def futureGridTrading_Nasdaq_Scalp_NQ2(self):
        self.set_cash(500_000)
        # Up/Down big wave with volatile market
        # (0.45, 0.35): (172/75.97%/-5.5%); (0.2, 0.4): (160/58.72%/-4.2%)
        # self.set_start_date(date(2024, 7, 1))
        # self.set_end_date(date(2024, 7, 31))

        # (0.45, 0.35): (417/89.65%/-7.3%); (0.2, 0.4): (383/79.5%/-5.5%)
        # self.set_start_date(date(2024, 7, 10))
        # self.set_end_date(date(2024, 8, 22))

        # (0.45, 0.35): (324/37.04%/-17.9%); (0.2, 0.4): (330/50.2%/-8.7%)
        self.set_start_date(date(2025, 2, 20))
        self.set_end_date(date(2025, 3, 30))

        configs = {
            LIConfigKey.aliasName: "NasdaqScalp",
            LIConfigKey.monitorPeriod: (5, LIResolution.MINUTE),
            LIConfigKey.disableBuyingPowerModel: True,
            LIConfigKey.openWithMarketOrderType: True,
            LIConfigKey.liquidateOnStopLossAmount: 10_000,
            LIConfigKey.liquidateLossAndRestartTrading: True,
            LIConfigKey.liquidateOnTakeProfitAmount: 50_000 * 2,
            LIConfigKey.gridLongLots: 8,
            LIConfigKey.gridShortLots: 6,
            LIConfigKey.gridLotLevelPercent: 0.6,
            # LIConfigKey.gridLotLevelPercent: 0.35,
            LIConfigKey.gridLotStopLossFactor: 2,
            LIConfigKey.gridLotTakeProfitFactor: 4,
            LIConfigKey.gridLotStopProfitFactors: (0.5, 1),
            LIConfigKey.gridBoostingKeepTrading: True,
            LIConfigKey.gridBoostingMaxHoldQuantity: 20,
            LIConfigKey.gridBoostingTriggerPercent: 0.5,  # Best lately
            # LIConfigKey.gridBoostingStopProfitPercents: (0.45, 0.35),
            LIConfigKey.gridBoostingStopProfitPercents: (0.2, 0.4),  # Better
            LIConfigKey.gridInitializeSession: True,  # Be careful!
        }

        investAmount = LIInvestAmount(lotQuantity=1)
        self.liStrategies.append(LIFutureGridTradingMomentum(Futures.Indices.NASDAQ_100_E_MINI, investAmount, **configs))

    def futureGridTrading_Nasdaq_Scalp_MNQ(self):
        amplifier = 1

        self.set_cash(50_000 * amplifier)
        # Up/Down big wave with volatile market
        # (0.45, 0.35): (172/75.97%/-5.5%); (0.2, 0.4): (159/58.56%/-4.2%)
        self.set_start_date(date(2024, 7, 1))
        self.set_end_date(date(2024, 7, 31))

        # (0.45, 0.35): (417/89.65%/-7.3%); (0.2, 0.4): (383/77.57%/-5.3%)
        # self.set_start_date(date(2024, 7, 10))
        # self.set_end_date(date(2024, 8, 22))

        # (0.45, 0.35): (321/36.09%/-18.6%); (0.2, 0.4): (329/49.34%/-9.2%)
        # self.set_start_date(date(2025, 2, 20))
        # self.set_end_date(date(2025, 3, 30))
        self.set_start_date(date(2024, 1, 1))
        self.set_end_date(date(2025, 5, 1))

        configs = {
            LIConfigKey.aliasName: "NasdaqScalp",
            LIConfigKey.monitorPeriod: (5, LIResolution.MINUTE),
            LIConfigKey.gridHeikinAshiPlies: 3,
            LIConfigKey.disableBuyingPowerModel: True,
            LIConfigKey.openWithMarketOrderType: False,
            LIConfigKey.closeWithMarketOrderType: False,
            LIConfigKey.liquidateOnStopLossAmount: 1_000 * amplifier,
            LIConfigKey.liquidateLossAndRestartTrading: True,
            LIConfigKey.liquidateOnTakeProfitAmount: 5_000 * 2 * amplifier,
            LIConfigKey.gridLongLots: 8,
            LIConfigKey.gridShortLots: 6,
            LIConfigKey.gridLotLevelPercent: 0.6,
            # LIConfigKey.gridLotLevelPercent: 0.35,
            LIConfigKey.gridLotStopLossFactor: 2,
            LIConfigKey.gridLotTakeProfitFactor: 4,
            LIConfigKey.gridLotStopProfitFactors: (0.5, 1),
            LIConfigKey.gridBoostingKeepTrading: True,
            LIConfigKey.gridBoostingMaxHoldQuantity: 20,
            LIConfigKey.gridBoostingTriggerPercent: 0.5,  # Best lately
            # LIConfigKey.gridBoostingStopProfitPercents: (0.45, 0.35),
            LIConfigKey.gridBoostingStopProfitPercents: (0.2, 0.4),
            LIConfigKey.gridInitializeSession: True,  # Be careful!
        }

        investAmount = LIInvestAmount(lotQuantity=1 * amplifier)
        self.liStrategies.append(LIFutureGridTradingMomentum(Futures.Indices.MICRO_NASDAQ_100_E_MINI, investAmount, **configs))


"""
┌────────────────────────────┬─────────────────┬─────────────────────────────┬─────────────────┐
│ Statistic                  │ Value           │ Statistic                   │ Value           │
├────────────────────────────┼─────────────────┼─────────────────────────────┼─────────────────┤
│ Equity                     │ $1,151,250.50   │ Fees                        │ -$1,556.60      │
│ Holdings                   │ $2,362,110.00   │ Net Profit                  │ $643,290.90     │
│ Probabilistic Sharpe Ratio │ 99.962%         │ Return                      │ 130.25 %        │
│ Unrealized                 │ $7,959.60       │ Volume                      │ $286,443,750.00 │
├────────────────────────────┼─────────────────┼─────────────────────────────┼─────────────────┤
│ Total Orders               │ 525             │ Average Win                 │ 6.22%           │
│ Average Loss               │ -0.14%          │ Compounding Annual Return   │ 1839023.408%    │
│ Drawdown                   │ 11.900%         │ Expectancy                  │ 4.412           │
│ Start Equity               │ 500000          │ End Equity                  │ 1151250.5       │
│ Net Profit                 │ 130.250%        │ Sharpe Ratio                │ 1981.948        │
│ Sortino Ratio              │ 14370.01        │ Probabilistic Sharpe Ratio  │ 99.962%         │
│ Loss Rate                  │ 88%             │ Win Rate                    │ 12%             │
│ Profit-Loss Ratio          │ 44.57           │ Alpha                       │ 0               │
│ Beta                       │ 0               │ Annual Standard Deviation   │ 1.207           │
│ Annual Variance            │ 1.457           │ Information Ratio           │ 1981.994        │
│ Tracking Error             │ 1.207           │ Treynor Ratio               │ 0               │
│ Total Fees                 │ $1556.60        │ Estimated Strategy Capacity │ $41000000.00    │
│ Lowest Capacity Asset      │ NQ YLZ9Z50BJE2P │ Portfolio Turnover          │ 1065.26%        │
└────────────────────────────┴─────────────────┴─────────────────────────────┴─────────────────┘
"""
