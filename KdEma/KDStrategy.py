# encoding:GBK
import talib as ta
import pandas as pd
import numpy as np
import RequestMT5.MT5RequestData as  QuestDataMt5
from log.loginfo import LogFile
import sendmail.sendfun as m
import log
import sqlconnection.sqlhelper
import tools.ToString

log = LogFile(__name__).getlog()
conn=sqlconnection.sqlhelper.SqLHelper()

def KDEMA_Strategy(SymbolName, period):
    global QuestDate
    try:
        # 查询当前货币池pool表中是否已有记录
        sql_select = "select  direction,ROUND(ema12,15),ROUND(ema26,15),ROUND(macd_w,15),ROUND(stoch_d_day,15),ema_signal_day from pool where sysbol_Name=%s;"
        param=[SymbolName]
        ret = conn.select_one(sql=sql_select, param=param)
        toret=tools.ToString.Byte64String(ret[0])
        QuestDate = QuestDataMt5.RequestData(SymbolName, period, 30)
        ema_k_list = ta.EMA(QuestDate["close"].values, 12)
        ema_d_list = ta.EMA(QuestDate["close"].values, 26)
        STOCH_K, STOCH_D = ta.STOCH(QuestDate.high.values, QuestDate.low.values, QuestDate.close.values, fastk_period=9,
                                    slowk_period=3, slowk_matype=0, slowd_period=3, slowd_matype=0)
        if toret == 'BUY':
            if (ret[3] > 0) and (ret[4] < 40):
                if (STOCH_K[26] < STOCH_D[26]) and (STOCH_K[27] > STOCH_D[27]) and (STOCH_K[27] < 40):
                    return period + '_KD_BUY_金叉_并且日线多头趋势已维持'+str(ret[5])+'天'
        if toret == 'SELL':
            if (ret[3] < 0) and (ret[4] > 70):
                if (STOCH_K[26] > STOCH_D[26]) and (STOCH_K[27] < STOCH_D[27]) and (STOCH_K[27] > 70):
                    return period + '_KD_SELL_死叉_并且日线空头趋势已维持'+str(ret[5])+'天'
    except Exception as e:
        log.error('获取KD策略出错……')
        log.error(e)
