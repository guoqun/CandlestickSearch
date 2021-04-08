# encoding:GBK
from datetime import datetime
from matplotlib.pylab import date2num
import matplotlib.pyplot as plt
import pandas as pd
from pandas.plotting import register_matplotlib_converters
from tkinter.constants import BOTTOM
import log
#from PivotPoint.Pivot import ResistanceThree
register_matplotlib_converters()
import MetaTrader5 as mt5
import time
import mpl_finance as mpf
import os
from log.loginfo import LogFile
import PivotPoint.Pivot as pp
import matplotlib
matplotlib.use('TkAgg')


log = LogFile(__name__).getlog()
def GenerateBarPng(SymbolName,run_time):
    # ���ӵ�MetaTrader 5
    if not mt5.initialize(login=3335660, server="Exness-MT5Real",password="Gcy191119"):
        print("initialize() failed")
        mt5.shutdown()
    # ��������״̬�Ͳ���
    #print(mt5.terminal_info())
    # ��ȡ�й�MetaTrader 5�汾������
    #print(mt5.version())
    try:
        # ͨ�����ַ�ʽ��ȡ��ͬ����Ʒ�ֵ�����ͼ
        if run_time == 'H1':
            rates = mt5.copy_rates_from_pos(SymbolName, mt5.TIMEFRAME_H1, 0, 90)
            SymbolName_Period=SymbolName+'_H1'
        elif run_time=='H4':
            rates = mt5.copy_rates_from_pos(SymbolName, mt5.TIMEFRAME_H4, 0, 90)
            SymbolName_Period=SymbolName+'_H4'
        elif run_time == 'D1':
            rates = mt5.copy_rates_from_pos(SymbolName, mt5.TIMEFRAME_D1, 0, 90)
            SymbolName_Period=SymbolName+'_����'
        else:
            rates=mt5.copy_rates_from_pos(SymbolName, mt5.TIMEFRAME_W1, 0, 90)
            SymbolName_Period = SymbolName + '_����'
        #log.info(rates)
    except Exception as e:
        log.error("����K��ͼʱ����ȡMT5����ʧ��........."+str(e))
     
    # �Ͽ���MetaTrader 5������
    mt5.shutdown()
     
    #DATA
    #print(rates)
    #PLOT
    # ������õ����ݴ���DataFrame
    ticks_frame = pd.DataFrame(rates)
    # ��ʱ�䣨����Ϊ��λ��ת��Ϊ����ʱ���ʽ
    ticks_frame['time']=pd.to_datetime(ticks_frame['time'], unit='s')
    log.info(run_time+'����K�߻��Ҷң�'+SymbolName+'����:\nC#')
    log.info(ticks_frame)
    plt.style.use('ggplot')
    plt.rcParams['font.sans-serif']=['SimHei'] #��ʾ���ı�ǩ
    plt.rcParams['axes.unicode_minus']=False   #��������Ҫ�ֶ�����
    #print(ticks_frame)
    fig = plt.figure(figsize=(8, 6), dpi=100, facecolor="white")
    fig.subplots_adjust(left=0.09, bottom=0.20, right=0.94, top=0.90, wspace=0.2, hspace=0)

    graph_KAV = fig.add_subplot(1, 1, 1)
    graph_KAV.set_title(SymbolName_Period)
    mpf.candlestick2_ochl(graph_KAV, ticks_frame.open, ticks_frame.close, ticks_frame.high, ticks_frame.low, width=0.5,colorup='r', colordown='g')

    graph_KAV.set_xlim(0, len(ticks_frame.time))
    graph_KAV.set_xticks(range(0, len(ticks_frame.time), 6))
    #Support4, Support3, Support2, Support1, PivotPoint, Resistance1, Resistance2, Resistance3, Resistance4
    # SymbolPivot_PP=pp.PPivot(SymbolName).values(4)
    # Resistance_One=pp.ResistanceOne(SymbolName).values(5)
    # Resistance_Two=pp.ResistanceTwo(SymbolName).values(6)
    # Resistance_Three=pp.ResistanceThree(SymbolName).values(7)
    # Support_One=pp.SupportOne(SymbolName).values(3)
    # Support_Two=pp.SupportTwo(SymbolName).values(2)
    # Support_Three=pp.SupportThree(SymbolName).values(1)
    #Support3, Support2, Support1, PivotPoint, Resistance1, Resistance2, Resistance3=pp.PPivot(SymbolName,run_time)
    #����PP���ĵ�λ����
    #plt.plot([60,90],[PivotPoint,PivotPoint],color='orange',linewidth =2.0)
    #plt.text(80, PivotPoint, 'PP')
    #����Resistance1����1λ����
    #plt.plot([60,90],[Resistance1,Resistance1],color='red',linewidth =1.0)
    #plt.text(80,Resistance1,'R1')
    #����Resistance����2λ����
    #plt.plot([60,90],[Resistance2,Resistance2],color='red',linestyle='--',linewidth =1.0)
    #plt.text(80,Resistance2,'R2')
    #����Resistance����3λ����
    #plt.plot([60,90],[Resistance3,Resistance3],color='red',linestyle='-.',linewidth =1.0)
    #plt.text(80,Resistance3,'R3')
    
    #����Support1֧��λ
    #plt.plot([60,90],[Support1,Support1],color='green',linewidth =1.0)
    #plt.text(80,Support1,'S1')
    
    #����Support2֧��λ
    #plt.plot([60,90],[Support2,Support2],color='green',linestyle='--',linewidth =1.0)
    #plt.text(80,Support2,'S2')
    
    #����Support3֧��λ
    #plt.plot([60,90],[Support3,Support3],color='green',linestyle='-.',linewidth =1.0)
    #plt.text(80,Support3,'S3')
    
    # ��ʾ������ͼ��
    FileName = "/../images/"+SymbolName+time.strftime('%Y%m%d%H%M%S ',time.localtime(time.time()))+".png" #ָ�����ɵ�ͼƬ����D:\IMAGESĿ¼��
    plt.savefig(FileName)
    #plt.show(block=False) #  �Զ��ر��޸�Ϊ plt.show(block=False)
    plt.close("fig1")
    current_path = os.path.abspath(FileName)
    #print(current_path)
    return FileName
