#encoding:GBK
import talib as ta
import pandas as pd
import numpy as np
import RequestMT5.MT5RequestData as  QuestDataMt5
from log.loginfo import LogFile
import sendmail.sendfun as m
import log
log = LogFile(__name__).getlog()
ta.set_compatibility(1)

def ResonanceMacd(SymbolName,period):
    try:
        # ��ȡH1MACD��SIGNALֵ
        QuestDate_H1 = QuestDataMt5.RequestData(SymbolName, 'H1', 200)
        QuestDate_H1 = QuestDate_H1[:198]
        close_H1 = QuestDate_H1["close"].values
        macd_H1, signal_H1, hist_H1 = ta.MACD(close_H1, 12, 26, 9)
        #��ȡH4MACD��SIGNALֵ
        QuestDate_H4 = QuestDataMt5.RequestData(SymbolName, 'H4', 200)
        QuestDate_H4 = QuestDate_H4[:198]
        close_H4 = QuestDate_H4["close"].values
        macd_H4, signal_H4, macdhist_H4 = ta.MACD(close_H4, 12, 26, 9)
        # ��ȡ����MACD��SIGNALֵ
        QuestDate_D = QuestDataMt5.RequestData(SymbolName, 'D1', 200)
        QuestDate_D = QuestDate_D[:198]
        close_d = QuestDate_D["close"].values
        macd_d, signal_d, macdhist_d = ta.MACD(close_d, 12, 26, 9)
        # ��ȡ���ߵ�SIGNALֵ
        QuestDate_W = QuestDataMt5.RequestData(SymbolName, 'W1', 200)
        QuestDate_W = QuestDate_W[:198]
        close_w = QuestDate_W["close"].values
        macd_w, signal_w, hist_w = ta.MACD(close_w, 12, 26, 9)
        log.info('H1_ǰһ��MACDֵ: ')
        log.info(macd_H1[196:197])
        log.info('H1_��ǰMACDֵ: ')
        log.info(macd_H1[197:198])
        log.info('H4_ǰһ��MACDֵ: ')
        log.info(macd_H4[196:197])
        log.info('H4_��ǰMACDֵ: ')
        log.info(macd_H4[197:198])
        log.info('����MACDֵ: ')
        log.info(macd_d[197:198])
        log.info('����MACDֵ: ')
        log.info(macd_w[197:198])
    except Exception as e:
        log.error('��ȡMACD�ϴ�ָ����󡭡���')
        log.error(e)
    #1Сʱ���ڴ���
    if period == 'H1':
        # 1Сʱ���ڶ൥�ж�
        if (macd_H1[196:197] < 0) and (macd_H1[197:198] > 0 ) : #MACD_H1���ϴ�0��
            if (macd_H4[197:198] > 0) and (macd_d[197:198] > 0)  : #�ж�H4���ں�D1�����Ƿ���H1���ڱ���һ��
                return 'BUY_H1'
        #1Сʱ���ڿյ��ж�
        if (macd_H1[196:197] > 0) and (macd_H1[197:198] < 0): #MACD_H1���´�0��
            if (macd_H4[197:198] < 0) and (macd_d[197:198] < 0):
                return 'SELL_H1'
    #4Сʱ���ڴ���
    if period == 'H4':
        if (macd_H4[196:197] < 0) and (macd_H4[197:198] > 0) : #MACD_H4Сʱ�ϴ�0��
            if(macd_d[197:198] > 0) and (macd_w[197:198] > 0) : #�ж������ں��������Ƿ���H4���ڱ���һ��
                return 'BUY_H4'
        if (macd_H4[196:197] > 0) and (macd_H4[197:198] < 0) :
            if(macd_d[197:198] < 0) and (macd_w[197:198] < 0) :
                return 'SELL_H4'

    # �����������ڴ���
    if period == 'D1':
        if (macd_d[196:197] < 0) and (macd_d[197:198] > 0) : #MACD_H4Сʱ�ϴ�0��
            if macd_w[197:198] > 0 : #�ж������ں��������Ƿ���H4���ڱ���һ��
                return 'BUY_D1'
        if (macd_d[196:197] > 0) and (macd_d[197:198] < 0) :
            if macd_w[197:198] < 0:
                return 'SELL_D1'
