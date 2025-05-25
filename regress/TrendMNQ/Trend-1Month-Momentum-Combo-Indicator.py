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
        # liquidateAndStopTrading() # Liquidate all strategies in emergency!
        # replicateMetadataFrom(15964868)  # Replicate metadata from this project

        if self.live_mode:
            terminate(f"This project is for backtest only!")

        self.futureGridTrading_Nasdaq_Momentum_Indicator()

    def futureGridTrading_Nasdaq_Momentum_Indicator(self):
        self.SetCash(50_000)
        # MES: (119/3.32%/-4.9%); MNQ: (115/13.46%/-6.9%)
        self.SetStartDate(date(2025, 4, 1))
        self.SetEndDate(date(2025, 5, 1))

        amplifier = 1  # Amplify invest amount by n times!
        configs = {
            LIConfigKey.aliasName: "NasdaqScalp",
            # LIConfigKey.verbose: True,
            LIConfigKey.monitorPeriod: 5,
            LIConfigKey.indicatorPeriod: 60,
            # LIConfigKey.extendedMarketHours: True,
            LIConfigKey.extendDataBarStream: True,  # True for MES; False for MNQ
            LIConfigKey.openWithMarketOrderType: False,
            LIConfigKey.closeWithMarketOrderType: False,
            # LIConfigKey.closeWithStopOrderType: True,
            LIConfigKey.heikinAshiPlies: 3,
            LIConfigKey.gridUseTradeInsight: True,
            LIConfigKey.gridLongLots: 2,  # 8
            LIConfigKey.gridShortLots: 2,  # 6
            LIConfigKey.gridLotLevelPercent: 0.6,
            LIConfigKey.gridLotStopLossFactor: 3,  # 2
            LIConfigKey.gridLotTakeProfitFactor: 20,  # 4
            LIConfigKey.stochasticComboParams: {LIIndicator.EMA: 100,
                                                LIIndicator.RSI: 14,
                                                LIIndicator.ATR: (30, 2),
                                                LIIndicator.MACD: (12, 26, 5),
                                                LIIndicator.KDJ: (14, 3, 3, 80, 20),
                                                LIIndicator.SRSI: (14, 14, 3, 3, 90, 10)},
            LIConfigKey.gridInitializeSession: True,  # Be careful!
        }

        investAmount = LIInvestAmount(lotQuantity=1 * amplifier)
        self.liStrategies.append(LIFutureGridTradingMomentum(Futures.Indices.MICRO_NASDAQ_100_E_MINI, investAmount, **configs))


"""
┌────────────────────────────┬──────────────────┬─────────────────────────────┬───────────────┐
│ Statistic                  │ Value            │ Statistic                   │ Value         │
├────────────────────────────┼──────────────────┼─────────────────────────────┼───────────────┤
│ Equity                     │ $65,487.32       │ Fees                        │ -$98.61       │
│ Holdings                   │ $39,955.00       │ Net Profit                  │ $15,420.39    │
│ Probabilistic Sharpe Ratio │ 93.762%          │ Return                      │ 30.97 %       │
│ Unrealized                 │ $66.93           │ Volume                      │ $6,525,931.00 │
├────────────────────────────┼──────────────────┼─────────────────────────────┼───────────────┤
│ Total Orders               │ 173              │ Average Win                 │ 1.74%         │
│ Average Loss               │ -0.47%           │ Compounding Annual Return   │ 2297.645%     │
│ Drawdown                   │ 11.400%          │ Expectancy                  │ 0.703         │
│ Start Equity               │ 50000            │ End Equity                  │ 65487.32      │
│ Net Profit                 │ 30.975%          │ Sharpe Ratio                │ 25.834        │
│ Sortino Ratio              │ 39.69            │ Probabilistic Sharpe Ratio  │ 93.762%       │
│ Loss Rate                  │ 64%              │ Win Rate                    │ 36%           │
│ Profit-Loss Ratio          │ 3.73             │ Alpha                       │ 0             │
│ Beta                       │ 0                │ Annual Standard Deviation   │ 0.499         │
│ Annual Variance            │ 0.249            │ Information Ratio           │ 25.944        │
│ Tracking Error             │ 0.499            │ Treynor Ratio               │ 0             │
│ Total Fees                 │ $98.61           │ Estimated Strategy Capacity │ $79000000.00  │
│ Lowest Capacity Asset      │ MNQ YTG30NVEFCW1 │ Portfolio Turnover          │ 358.37%       │
└────────────────────────────┴──────────────────┴─────────────────────────────┴───────────────┘
"""
