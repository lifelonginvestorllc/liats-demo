from AlgorithmImports import *
from core.LIAlgorithm import *
from indicator.LIWeeklyTrendingSignals import *


class LifelongInvestorMain(LIAlgorithm):

    def initialize(self):
        super().initialize()
        setLogSize(500)  # Only for backtesting
        setAlgoName("Backtest")  # Invest account name
        # setAccountOwner("Lifelong Investor")  # Invest account owner
        startBenchmark("SPY", date(2025, 4, 1), 100_000, 50_000)
        setIbkrReportKey("30157805795961367012345", "12345678")
        # setPortfolioRepute("Lifelong Investor Testing Fund")
        addNotifySetting(LINotifyType.TELEGRAM, "-913280749")
        addAlertSetting(LINotifyType.EMAIL, "lifelonginvestorllc@gmail.com")
        # sendDailyMetadataAlert()  # Enable to send daily metadata via alert
        # liquidateAndStopTrading() # Liquidate all strategies in emergency!
        # replicateMetadataFrom(15964868)  # Replicate metadata from this project

        '''Some functions to run in backtest main.py only!'''
        # Use this to purge some stale/expired metadata if exceeded limit!
        # purgeExpiredMetadata(r"(?i)^liats/.*$", justDryRun=True)
        # purgeExpiredMetadata(r"(?i)^.+/gridLotsMetadata/-?\d+.*$", justDryRun=False)
        # purgeExpiredMetadata(r"(?i)^.+/gridTradingCache.*$", justDryRun=False)
        if self.live_mode:
            terminate(f"This project is for backtest only!")

    '''Please use accounts under the live directory to backtest or deploy!'''
