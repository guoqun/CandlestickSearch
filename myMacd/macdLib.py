import talib as ta
import pandas as pd
import numpy as np
import RequestMT5.MT5RequestData as  QuestDataMt5
from log.loginfo import LogFile
log = LogFile(__name__).getlog()
ta.set_compatibility(1)
def remacd(SymbolName):
    try :
        #获取日线MACD的SIGNAL值
        QuestDate_D = QuestDataMt5.RequestData(SymbolName, 'D1',200)
        QuestDate_D=QuestDate_D[:198]
        close_d = QuestDate_D["close"].values
        macd_d, signal_d, hist_d  = ta.MACD(close_d,12,26,9)
        #获取周线的SIGNAL值
        QuestDate_W = QuestDataMt5.RequestData(SymbolName, 'W1', 200)
        QuestDate_W = QuestDate_W[:198]
        close_w = QuestDate_W["close"].values
        macd_w, signal_w, hist_w = ta.MACD(close_w, 12, 26, 9)
        # log.info('日线signal_d')
        # log.info((signal_d[197:198]))
        # log.info('周线signal_w:')
        # log.info(signal_w[197:198])
    except Exception as e:
        log.error('获取MACD错误：'+e.toStr())
    if signal_d[197:198] >0 and signal_w[197:198] >0 :
        return 1
    elif signal_d[197:198] <0 and signal_w[197:198] <0 :
        return -1
    else :
        return 0

