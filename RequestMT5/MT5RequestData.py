# encoding:GBK
from datetime import datetime
from matplotlib.pylab import date2num
import matplotlib.pyplot as plt
import pandas as pd
from pandas.plotting import register_matplotlib_converters
from tkinter.constants import BOTTOM
import log
from MetaTrader5._core import copy_ticks_from
register_matplotlib_converters()
import MetaTrader5 as mt5
import time
from mpl_finance import candlestick_ochl
import mpl_finance as mpf
import os
from log.loginfo import LogFile

'''
    根据传入的货币兑符号，获取对应的数据并处理并返回
'''


log = LogFile(__name__).getlog()

def RequestData(SymbolName, run_time, Day):
    # 连接到MetaTrader 5
    if not mt5.initialize(login=3335660, server="Exness-MT5Real",password="Gcy191119"):
        print("initialize() failed")
     
    # 请求连接状态和参数
    #print(mt5.terminal_info())
    # 获取有关MetaTrader 5版本的数据
    #print(mt5.version())
    try:
        if run_time == 'H1':
            rates = mt5.copy_rates_from_pos(SymbolName, mt5.TIMEFRAME_H1, 0, Day)
        # 通过多种方式获取不同交易品种的柱形图
        elif run_time == 'H4':
            rates = mt5.copy_rates_from_pos(SymbolName, mt5.TIMEFRAME_H4, 0, Day)
        elif run_time == 'D1':
            rates = mt5.copy_rates_from_pos(SymbolName, mt5.TIMEFRAME_D1, 0, Day)
        elif run_time == 'W1':
            rates = mt5.copy_rates_from_pos(SymbolName, mt5.TIMEFRAME_W1, 0, Day)
    except Exception as e:
        log.error("生成K线图时，获取MT5数据失败........."+str(e))
     
    # 断开与MetaTrader 5的连接
    mt5.shutdown()
     
    #DATA
    #print(rates)
    #PLOT
    # 从所获得的数据创建DataFrame
    ticks_frame = pd.DataFrame(rates)
    ticks_frame=ticks_frame.drop(ticks_frame.index[1])
    # 将时间（以秒为单位）转换为日期时间格式
    ticks_frame['time']=pd.to_datetime(ticks_frame['time'], unit='s')
    return ticks_frame
