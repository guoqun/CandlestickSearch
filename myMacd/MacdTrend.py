#encoding:GBK
import talib as ta
import sqlconnection.sqlhelper
import pandas as pd
import numpy as np
import RequestMT5.MT5RequestData as  QuestDataMt5
from log.loginfo import LogFile
import sendmail.sendfun as m
log = LogFile(__name__).getlog()
ta.set_compatibility(1)
conn=sqlconnection.sqlhelper.SqLHelper()


def TrendMacd(SymbolName,period):
    sql_select = "select  sysbol_Name,trend_h1,h1_trend_num,trend_h4,h4_trend_num,trend_day,day_trend_num from macdpool where sysbol_Name=%s"
    param = [SymbolName]
    ret = conn.select_one(sql=sql_select, param=param)
    if ret[1] == ret[5]:
        if ret[2] == 1:
            return '1H_周期MACD出现在金叉或死叉并且其它的大周期趋势一致！'
    if ret[3] == ret[5]:
        if ret[4] == 1:
            return '4H_周期MACD出现在金叉或死叉并且其它的大周期趋势一致！'

