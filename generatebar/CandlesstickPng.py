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
    # 连接到MetaTrader 5
    if not mt5.initialize(login=3335660, server="Exness-MT5Real",password="Gcy191119"):
        print("initialize() failed")
        mt5.shutdown()
    # 请求连接状态和参数
    #print(mt5.terminal_info())
    # 获取有关MetaTrader 5版本的数据
    #print(mt5.version())
    try:
        # 通过多种方式获取不同交易品种的柱形图
        if run_time == 'H1':
            rates = mt5.copy_rates_from_pos(SymbolName, mt5.TIMEFRAME_H1, 0, 90)
            SymbolName_Period=SymbolName+'_H1'
        elif run_time=='H4':
            rates = mt5.copy_rates_from_pos(SymbolName, mt5.TIMEFRAME_H4, 0, 90)
            SymbolName_Period=SymbolName+'_H4'
        elif run_time == 'D1':
            rates = mt5.copy_rates_from_pos(SymbolName, mt5.TIMEFRAME_D1, 0, 90)
            SymbolName_Period=SymbolName+'_日线'
        else:
            rates=mt5.copy_rates_from_pos(SymbolName, mt5.TIMEFRAME_W1, 0, 90)
            SymbolName_Period = SymbolName + '_周线'
        #log.info(rates)
    except Exception as e:
        log.error("生成K线图时，获取MT5数据失败........."+str(e))
     
    # 断开与MetaTrader 5的连接
    mt5.shutdown()
     
    #DATA
    #print(rates)
    #PLOT
    # 从所获得的数据创建DataFrame
    ticks_frame = pd.DataFrame(rates)
    # 将时间（以秒为单位）转换为日期时间格式
    ticks_frame['time']=pd.to_datetime(ticks_frame['time'], unit='s')
    log.info(run_time+'生成K线货币兑：'+SymbolName+'数据:\nC#')
    log.info(ticks_frame)
    plt.style.use('ggplot')
    plt.rcParams['font.sans-serif']=['SimHei'] #显示中文标签
    plt.rcParams['axes.unicode_minus']=False   #这两行需要手动设置
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
    #插入PP轴心点位置线
    #plt.plot([60,90],[PivotPoint,PivotPoint],color='orange',linewidth =2.0)
    #plt.text(80, PivotPoint, 'PP')
    #插入Resistance1阻力1位置线
    #plt.plot([60,90],[Resistance1,Resistance1],color='red',linewidth =1.0)
    #plt.text(80,Resistance1,'R1')
    #插入Resistance阻力2位置线
    #plt.plot([60,90],[Resistance2,Resistance2],color='red',linestyle='--',linewidth =1.0)
    #plt.text(80,Resistance2,'R2')
    #插入Resistance阻力3位置线
    #plt.plot([60,90],[Resistance3,Resistance3],color='red',linestyle='-.',linewidth =1.0)
    #plt.text(80,Resistance3,'R3')
    
    #插入Support1支撑位
    #plt.plot([60,90],[Support1,Support1],color='green',linewidth =1.0)
    #plt.text(80,Support1,'S1')
    
    #插入Support2支撑位
    #plt.plot([60,90],[Support2,Support2],color='green',linestyle='--',linewidth =1.0)
    #plt.text(80,Support2,'S2')
    
    #插入Support3支撑位
    #plt.plot([60,90],[Support3,Support3],color='green',linestyle='-.',linewidth =1.0)
    #plt.text(80,Support3,'S3')
    
    # 显示并保存图表
    FileName = "/../images/"+SymbolName+time.strftime('%Y%m%d%H%M%S ',time.localtime(time.time()))+".png" #指定生成的图片放入D:\IMAGES目录中
    plt.savefig(FileName)
    #plt.show(block=False) #  自动关闭修改为 plt.show(block=False)
    plt.close("fig1")
    current_path = os.path.abspath(FileName)
    #print(current_path)
    return FileName
