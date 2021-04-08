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
    ���ݴ���Ļ��Ҷҷ��ţ���ȡ��Ӧ�����ݲ���������
'''


log = LogFile(__name__).getlog()

def RequestData(SymbolName, run_time, Day):
    # ���ӵ�MetaTrader 5
    if not mt5.initialize(login=3335660, server="Exness-MT5Real",password="Gcy191119"):
        print("initialize() failed")
     
    # ��������״̬�Ͳ���
    #print(mt5.terminal_info())
    # ��ȡ�й�MetaTrader 5�汾������
    #print(mt5.version())
    try:
        if run_time == 'H1':
            rates = mt5.copy_rates_from_pos(SymbolName, mt5.TIMEFRAME_H1, 0, Day)
        # ͨ�����ַ�ʽ��ȡ��ͬ����Ʒ�ֵ�����ͼ
        elif run_time == 'H4':
            rates = mt5.copy_rates_from_pos(SymbolName, mt5.TIMEFRAME_H4, 0, Day)
        elif run_time == 'D1':
            rates = mt5.copy_rates_from_pos(SymbolName, mt5.TIMEFRAME_D1, 0, Day)
        elif run_time == 'W1':
            rates = mt5.copy_rates_from_pos(SymbolName, mt5.TIMEFRAME_W1, 0, Day)
    except Exception as e:
        log.error("����K��ͼʱ����ȡMT5����ʧ��........."+str(e))
     
    # �Ͽ���MetaTrader 5������
    mt5.shutdown()
     
    #DATA
    #print(rates)
    #PLOT
    # ������õ����ݴ���DataFrame
    ticks_frame = pd.DataFrame(rates)
    ticks_frame=ticks_frame.drop(ticks_frame.index[1])
    # ��ʱ�䣨����Ϊ��λ��ת��Ϊ����ʱ���ʽ
    ticks_frame['time']=pd.to_datetime(ticks_frame['time'], unit='s')
    return ticks_frame
