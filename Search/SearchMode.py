# encoding:GBK
import MetaTrader5 as mt5
import talib
import pandas as pd
import sqlconnection.sqlhelper
import weekend.WeekendSearch
import generatebar.CandlesstickPng
from log.loginfo import LogFile
import sendmail.sendfun as m
import log
import tools.ToString
import myMacd.MacdResonance as mr
import myMacd.MacdTrend as macdtrend
import myMacd.macdpool as macdpool
import KdEma.KDStrategy as emas
import KdEma.EMAPool as pool
log = LogFile(__name__).getlog()
conn = sqlconnection.sqlhelper.SqLHelper()


# K��ģʽʶ������
def K_ModeSelect(run_time):
    global moderedme
    images = []  # �ʼ�K��ģ��ͼ�洢
    contents = []
    # ������Ҫ��ȡ���ݵ��б�
    week = weekend.WeekendSearch.WekSear()
    if week == 5 or week == 6:  # �ж���δ���͵�Ʒ����Ϣ���������δ��ֻ��BTCUSD�ļ���
        sql1 = 'select symbol_name from symbol where symbol_name=%s'
        args = 'BTCUSDm'
        my_symbol = tools.ToString.UncodeToString(conn.select_all(sql1,args))
        # my_symbol = ['NZDUSDm','USDCHFm','BTCUSDm','AUDCHFm','AUDCADm','CADJPYm','GBPAUDm','GBPCADm','AUDGBPm','AUDJPYm','AUDNZDm','CADCHFm','CHFJPYm','EURAUDm','EURCHFm','EURGBPm','EURJPYm','EURNZDm','EURUSDm','GBPCHFm','GBPJPYm','GBPUSDm','NZDCADm','NZDJPYm','USDCADm','XAUUSDm']
    else:
        # my_symbol = ['NZDUSDm','USDCHFm','BTCUSDm','AUDCHFm','AUDCADm','CADJPYm','GBPAUDm','GBPCADm','AUDGBPm','AUDJPYm','AUDNZDm','CADCHFm','CHFJPYm','EURAUDm','EURCHFm','EURGBPm','EURJPYm','EURNZDm','EURUSDm','GBPCHFm','GBPJPYm','GBPUSDm','NZDCADm','NZDJPYm','USDCADm','XAUUSDm']
        # my_symbol=['USDCADm']
        sql1 = 'select symbol_name from symbol'
        my_symbol = tools.ToString.UncodeToString(conn.select_all(sql1))
    for index, symbol in enumerate(my_symbol):
        # log.info(run_time+'��ǰ�������Ҷң�'+symbol+'����:\n')
        pd.set_option('display.max_columns', 15000)  # number of columns to be displayed
        pd.set_option('display.width', 15000)  # max table width to displayema
        # ������MetaTrader 5����˵�����
        if not mt5.initialize(login=3335660, server="Exness-MT5Real", password="Gcy191119"):
            # print("initialize() failed, error code =",mt5.last_error())
            log.info("initialize() failed, error code =", mt5.last_error())
            quit()
        try:
            if run_time == 'H1':
                rates = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_H1, 0, 11)
            elif run_time == 'H4':
                rates = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_H4, 0, 11)
            elif run_time == 'D1':
                rates = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_D1, 0, 11)
                try:
                    pool.Pool(symbol) #ÿ�찴�ƻ��������Ƴ�
                except Exception as e:
                    log.error('�������Ƴ��Ӵ��󡭡�')
            elif run_time == 'W1':
                rates = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_W1, 0, 11)
        except Exception as e:
            log.error("����ģ��ʱ����ȡMT5����ʧ��......" + str(e))
        mt5.shutdown()  # �ر�MT5
        rates_frame = pd.DataFrame(rates)
        rates_frame['time'] = pd.to_datetime(rates_frame['time'], unit='s')
        log.info(run_time + '����ģ�ͻ��Ҷң�' + symbol + '����:\nC#')
        rates_frame = rates_frame[:10]  # ������Ƭ���� ��ȥ��ǰ�ߵ�ʱ��
        log.info(rates_frame)

        # KD��������
        ema = emas.KDEMA_Strategy(symbol,run_time)
        if ema is not None :
            attrfile = generatebar.CandlesstickPng.GenerateBarPng(symbol, run_time)
            images.append(attrfile)
            contents.append('<p><strong>���Ҷ�[' + symbol + ']' + '��' + run_time + '���ڷ���'+ema+'�ź�')

        # macd��������
        # macd = mr.ResonanceMacd(symbol, run_time)
        # if macd == 'BUY_H1' or   macd == 'BUY_H4' or  macd == 'BUY_D1' :  # ����MACD�൥���������
        #     try:
        #         attrfile = generatebar.CandlesstickPng.GenerateBarPng(symbol, run_time)
        #         images.append(attrfile)
        #         contents.append('<p><strong>���Ҷ�[' + symbol + ']' + '��' + macd + '���ڳ�MACD�����ϴ��������������������ڱ���һ�£���ע��鿴')
        #     except Exception as e:
        #         log.error('�ж�MACD�ϴ�ʱ�����쳣............... \n')
        #         log.error(e.toStr())
        # if macd == 'SELL_H1' or macd == 'SELL_H4' or macd == 'SELL_D1' : # ����MACD�յ����������
        #     try:
        #         attrfile = generatebar.CandlesstickPng.GenerateBarPng(symbol, run_time)
        #         images.append(attrfile)
        #         contents.append('<p><strong>���Ҷ�[' + symbol + ']' + '��' + macd + '���ڳ�MACD�����´��������������������ڱ���һ�£���ע��鿴')
        #     except Exception as e:
        #         log.error('�ж�MACD�´�ʱ�����쳣............... \n')
        #         log.error(e.toStr())
        #����MACDPOOL����
        try:
            macdpool.TrendMacdpool(symbol,run_time)
        except Exception as e:
            log.error(symbol+'����MACDPOOL���ӳ�������������')
            log.error(e)
        #����MACD����
        try:
            macd_trend = macdtrend.TrendMacd(symbol, run_time)
            if macd_trend is not None:
                contents.append('<p><strong>['+symbol+']'+macd_trend+'</strong></p>')
                attrfile = generatebar.CandlesstickPng.GenerateBarPng(symbol, run_time)
                images.append(attrfile)
        except Exception as e:
            log.error(symbol+'����MACD���Ƴ�����')
            log.error(e)
        # if macd_trend is not None: #��������γ� ��ʼ���K�ߵ���̬
        #     '''
        #     ��������CDL2CROWS
        #     ���ƣ�Two Crows ��ֻ��ѻ
        #     ��飺����K��ģʽ����һ�쳤�����ڶ���߿��������������ٴθ߿����������� ���̱�ǰһ�����̼۵ͣ�Ԥʾ�ɼ��µ���
        #     '''
        #     # ��ʼ����K����̬����
        #     modec = talib.CDL2CROWS(rates_frame.open.values, rates_frame.high.values, rates_frame.low.values,
        #                             rates_frame.close.values)
        #     if modec[9] == 100 or modec[9] == -100:
        #         if modec[9] == 100 and (macd_trend == 'BUY_TRAND_H1' or macd_trend == 'BUY_TRAND_H4' or macd_trend =='BUY_TRAND_D'):
        #             order_Type = '��'
        #             moderedme = ' MACD����[��ͷ]���Ƶ���,��ǰK����̬Ϊ['
        #         elif modec[9] == -100 and (macd_trend == 'SELL_TRAND_H1' or macd_trend == 'SELL_TRAND_H4' or macd_trend == 'SELL_TRAND_D') :
        #             order_Type = '����'
        #             moderedme = 'MACD����[��ͷ]���Ƶ��У���ǰK����̬Ϊ['
        #         try:
        #             contents.append(
        #                 '<p><strong>���Ҷң�[' + symbol + ']' + moderedme + order_Type + ']��ֻ��ѻģʽ</strong></p>��ֻ��ѻ����K'
        #                                                                              '��ģʽ����һ�쳤�����ڶ���߿��������������ٴθ߿����������� '
        #                                                                              '���̱�ǰһ�����̼۵ͣ�Ԥʾ�ɼ��µ���')
        #             attrfile = generatebar.CandlesstickPng.GenerateBarPng(symbol, run_time)
        #             images.append(attrfile)
        #         except Exception as e:
        #             log.error('���ͻ��Ҷң�' + symbol + '��ֻ��ѻ�����ʼ�ʧ��' + str(e))
        #
        #     '''
        #     ��������CDL3BLACKCROWS
        #     ���ƣ�Three Black Crows ��ֻ��ѻ
        #     ��飺����K��ģʽ�������������ߣ�ÿ�����̼۶��µ��ҽӽ���ͼۣ� ÿ�տ��̼۶����ϸ�K��ʵ���ڣ�Ԥʾ�ɼ��µ���
        #     '''
        #     modec = talib.CDL3BLACKCROWS(rates_frame.open.values, rates_frame.high.values, rates_frame.low.values,
        #                                  rates_frame.close.values)
        #     if modec[9] == 100 or modec[9] == -100:
        #         if modec[9] == 100 and (macd_trend == 'BUY_TRAND_H1' or macd_trend == 'BUY_TRAND_H4' or macd_trend =='BUY_TRAND_D'):
        #             order_Type = '��'
        #             moderedme = ' MACD����[��ͷ]���Ƶ���,��ǰK����̬Ϊ['
        #         elif modec[9] == -100 and (macd_trend == 'SELL_TRAND_H1' or macd_trend == 'SELL_TRAND_H4' or macd_trend == 'SELL_TRAND_D') :
        #             order_Type = '����'
        #             moderedme = 'MACD����[��ͷ]���Ƶ��У���ǰK����̬Ϊ['
        #         try:
        #             contents.append(
        #                 '<p><strong>���Ҷң�[' + symbol + ']' + +moderedme + order_Type + +']��ֻ��ѻģʽ</strong></p>����K'
        #                                                                                '��ģʽ�������������ߣ�ÿ�����̼۶��µ��ҽӽ���ͼۣ� '
        #                                                                                'ÿ�տ��̼۶����ϸ�K��ʵ���ڣ�Ԥʾ�ɼ��µ���')
        #             attrfile = generatebar.CandlesstickPng.GenerateBarPng(symbol, run_time)
        #             images.append(attrfile)
        #         except Exception as e:
        #             log.error('���ͻ��Ҷң�' + symbol + '�ʼ���Ϣʧ�ܣ� ��ǰģʽΪ����ֻ��ѻ' + str(e))
        #
        #     '''
        #     ��������CDL3INSIDE
        #     ���ƣ� Three Inside Up/Down �ڲ����Ǻ��µ�
        #     ��飺����K��ģʽ��ĸ���ź�+��K�ߣ������ڲ�����Ϊ����K��Ϊ�������� ���������̼۸��ڵ�һ�쿪�̼ۣ��ڶ���K���ڵ�һ��K���ڲ���Ԥʾ�Źɼ����ǡ�
        #     '''
        #     modec = talib.CDL3INSIDE(rates_frame.open.values, rates_frame.high.values, rates_frame.low.values,
        #                              rates_frame.close.values)
        #     if modec[9] == 100 or modec[9] == -100:
        #         if modec[9] == 100 and (macd_trend == 'BUY_TRAND_H1' or macd_trend == 'BUY_TRAND_H4' or macd_trend =='BUY_TRAND_D'):
        #             order_Type = '��'
        #             moderedme = ' MACD����[��ͷ]���Ƶ���,��ǰK����̬Ϊ['
        #         elif modec[9] == -100 and (macd_trend == 'SELL_TRAND_H1' or macd_trend == 'SELL_TRAND_H4' or macd_trend == 'SELL_TRAND_D') :
        #             order_Type = '����'
        #             moderedme = 'MACD����[��ͷ]���Ƶ��У���ǰK����̬Ϊ['
        #         try:
        #             contents.append(
        #                 ' <p><strong>���Ҷң�[' + symbol + ']' + moderedme + order_Type + ']���ڲ����Ǻ��µ�ģʽ</strong></p>����K'
        #                                                                               '��ģʽ��ĸ���ź�+��K�ߣ������ڲ�����Ϊ����K��Ϊ�������� '
        #                                                                               '���������̼۸��ڵ�һ�쿪�̼ۣ��ڶ���K���ڵ�һ��K���ڲ���Ԥʾ�Źɼ�����')
        #             attrfile = generatebar.CandlesstickPng.GenerateBarPng(symbol, run_time)
        #             images.append(attrfile)
        #             log.info('���ͻ��Ҷң�' + symbol + '�ʼ���Ϣ�ɹ��� ��ǰģʽΪ�����ڲ����Ǻ��µ�')
        #         except Exception as e:
        #             log.error('���ͻ��Ҷң�' + symbol + '�ʼ���Ϣʧ�ܣ� ��ǰģʽΪ�����ڲ����Ǻ��µ�' + str(e))
        #
        #     '''
        #     ��������CDL3LINESTRIKE
        #     ���ƣ� Three-Line Strike ���ߴ��
        #     ��飺����K��ģʽ��ǰ�������ߣ�ÿ�����̼۶���ǰһ�ոߣ� ���̼���ǰһ��ʵ���ڣ��������г��߿������̼۵��ڵ�һ�տ��̼ۣ�Ԥʾ�ɼ��µ���
        #     '''
        #     modec = talib.CDL3LINESTRIKE(rates_frame.open.values, rates_frame.high.values, rates_frame.low.values,
        #                                  rates_frame.close.values)
        #     if modec[9] == 100 or modec[9] == -100:
        #         if modec[9] == 100 and (macd_trend == 'BUY_TRAND_H1' or macd_trend == 'BUY_TRAND_H4' or macd_trend =='BUY_TRAND_D'):
        #             order_Type = '��'
        #             moderedme = ' MACD����[��ͷ]���Ƶ���,��ǰK����̬Ϊ['
        #         elif modec[9] == -100 and (macd_trend == 'SELL_TRAND_H1' or macd_trend == 'SELL_TRAND_H4' or macd_trend == 'SELL_TRAND_D') :
        #             order_Type = '����'
        #             moderedme = 'MACD����[��ͷ]���Ƶ��У���ǰK����̬Ϊ['
        #         try:
        #             contents.append('<p><strong>���Ҷң�[' + symbol + ']' + moderedme + order_Type + ']���ߴ��ģʽ</strong></p> '
        #                                                                                          '����K��ģʽ��ǰ�������ߣ�ÿ�����̼۶���ǰһ�ոߣ� '
        #                                                                                          '���̼���ǰһ��ʵ���ڣ��������г��߿������̼۵��ڵ�һ�տ��̼ۣ�Ԥʾ�ɼ��µ���')
        #             attrfile = generatebar.CandlesstickPng.GenerateBarPng(symbol, run_time)
        #             images.append(attrfile)
        #         except Exception as e:
        #             log.error('���ͻ��Ҷң�' + symbol + '�ʼ���Ϣʧ�ܣ� ��ǰģʽΪ�����ߴ��' + str(e))
        #
        #     '''
        #     ��������CDL3OUTSIDE
        #     ���ƣ�Three Outside Up/Down ���ⲿ���Ǻ��µ�
        #     ��飺����K��ģʽ�������ڲ����Ǻ��µ����ƣ�K��Ϊ������������һ����ڶ��յ�K����̬�෴�� �����ⲿ����Ϊ������һ��K���ڵڶ���K���ڲ���Ԥʾ�Źɼ����ǡ�
        #     '''
        #     modec = talib.CDL3OUTSIDE(rates_frame.open.values, rates_frame.high.values, rates_frame.low.values,
        #                               rates_frame.close.values)
        #     if modec[9] == 100 or modec[9] == -100:
        #         if modec[9] == 100 and (macd_trend == 'BUY_TRAND_H1' or macd_trend == 'BUY_TRAND_H4' or macd_trend =='BUY_TRAND_D'):
        #             order_Type = '��'
        #             moderedme = ' MACD����[��ͷ]���Ƶ���,��ǰK����̬Ϊ['
        #         elif modec[9] == -100 and (macd_trend == 'SELL_TRAND_H1' or macd_trend == 'SELL_TRAND_H4' or macd_trend == 'SELL_TRAND_D') :
        #             order_Type = '����'
        #             moderedme = 'MACD����[��ͷ]���Ƶ��У���ǰK����̬Ϊ['
        #         try:
        #             contents.append(
        #                 '<p><strong>���Ҷң�[' + symbol + ']' + moderedme + order_Type + ']���ⲿ���Ǻ��µ�ģʽ</strong></p>����K'
        #                                                                              '��ģʽ�������ڲ����Ǻ��µ����ƣ�K��Ϊ������������һ����ڶ��յ�K'
        #                                                                              '����̬�෴�� '
        #                                                                              '�����ⲿ����Ϊ������һ��K���ڵڶ���K���ڲ���Ԥʾ�Źɼ����ǡ�')
        #             attrfile = generatebar.CandlesstickPng.GenerateBarPng(symbol, run_time)
        #             images.append(attrfile)
        #         except Exception as e:
        #             log.error('���ͻ��Ҷң�' + symbol + '�ʼ���Ϣʧ�ܣ� ��ǰģʽΪ�����ⲿ���Ǻ��µ�' + str(e))
        #     '''
        #     ��������CDL3STARSINSOUTH
        #     ���ƣ�Three Stars In The South �Ϸ�����
        #     ��飺����K��ģʽ�����е�ǰ�෴������K�߽�������һ���г���Ӱ�ߣ� �ڶ������һ�����ƣ�K������С�ڵ�һ�գ�����������Ӱ��ʵ���źţ� �ɽ��۸��ڵ�һ�����֮�ڣ�Ԥʾ�µ����Ʒ�ת���ɼ�������
        #     '''
        #     modec = talib.CDL3STARSINSOUTH(rates_frame.open.values, rates_frame.high.values, rates_frame.low.values,
        #                                    rates_frame.close.values)
        #     if modec[9] == 100 or modec[9] == -100:
        #         if modec[9] == 100 and (macd_trend == 'BUY_TRAND_H1' or macd_trend == 'BUY_TRAND_H4' or macd_trend =='BUY_TRAND_D'):
        #             order_Type = '��'
        #             moderedme = ' MACD����[��ͷ]���Ƶ���,��ǰK����̬Ϊ['
        #         elif modec[9] == -100 and (macd_trend == 'SELL_TRAND_H1' or macd_trend == 'SELL_TRAND_H4' or macd_trend == 'SELL_TRAND_D') :
        #             order_Type = '����'
        #             moderedme = 'MACD����[��ͷ]���Ƶ��У���ǰK����̬Ϊ['
        #         try:
        #             contents.append(
        #                 '<p><strong>���Ҷң�[' + symbol + ']' + moderedme + order_Type + ']�Ϸ�����ģʽ</strong></p>����K'
        #                                                                              '��ģʽ�����е�ǰ�෴������K�߽�������һ���г���Ӱ�ߣ� '
        #                                                                              '�ڶ������һ�����ƣ�K������С�ڵ�һ�գ�����������Ӱ��ʵ���źţ� '
        #                                                                              '�ɽ��۸��ڵ�һ�����֮�ڣ�Ԥʾ�µ����Ʒ�ת���ɼ�������')
        #             attrfile = generatebar.CandlesstickPng.GenerateBarPng(symbol, run_time)
        #             images.append(attrfile)
        #         except Exception as e:
        #             log.error('���ͻ��Ҷң�' + symbol + '�ʼ���Ϣʧ�ܣ� ��ǰģʽΪ���Ϸ�����' + str(e))
        #     '''
        #     ��������CDL3WHITESOLDIERS
        #     ���ƣ�Three Advancing White Soldiers �����ױ�
        #     ��飺����K��ģʽ������K�߽����� ÿ�����̼۱���ҽӽ���߼ۣ����̼���ǰһ��ʵ���ϰ벿��Ԥʾ�ɼ�������
        #     '''
        #     modec = talib.CDL3WHITESOLDIERS(rates_frame.open.values, rates_frame.high.values, rates_frame.low.values,
        #                                     rates_frame.close.values)
        #     if modec[9] == 100 or modec[9] == -100:
        #         if modec[9] == 100 and (macd_trend == 'BUY_TRAND_H1' or macd_trend == 'BUY_TRAND_H4' or macd_trend =='BUY_TRAND_D'):
        #             order_Type = '��'
        #             moderedme = ' MACD����[��ͷ]���Ƶ���,��ǰK����̬Ϊ['
        #         elif modec[9] == -100 and (macd_trend == 'SELL_TRAND_H1' or macd_trend == 'SELL_TRAND_H4' or macd_trend == 'SELL_TRAND_D') :
        #             order_Type = '����'
        #             moderedme = 'MACD����[��ͷ]���Ƶ��У���ǰK����̬Ϊ['
        #         try:
        #             contents.append('<p><strong>���Ҷң�[' + symbol + ']' + moderedme + order_Type + ']�����ױ�ģʽ</strong></p> '
        #                                                                                          '����K��ģʽ������K�߽����� '
        #                                                                                          'ÿ�����̼۱���ҽӽ���߼ۣ����̼���ǰһ��ʵ���ϰ벿��Ԥʾ�ɼ�������')
        #             attrfile = generatebar.CandlesstickPng.GenerateBarPng(symbol, run_time)
        #             images.append(attrfile)
        #         except Exception as e:
        #             log.error('���ͻ��Ҷң�' + symbol + '�ʼ���Ϣʧ�ܣ� ��ǰģʽΪ�������ױ�' + str(e))
        #     '''
        #     ��������CDLABANDONEDBABY
        #     ���ƣ�Abandoned Baby ��Ӥ
        #     ��飺����K��ģʽ���ڶ��ռ۸���������ʮ���ǣ����̼������̼۽ӽ��� ��߼���ͼ����󣩣�Ԥʾ���Ʒ�ת�������ڶ����µ����ײ����ǡ�
        #     '''
        #     modec = talib.CDLABANDONEDBABY(rates_frame.open.values, rates_frame.high.values, rates_frame.low.values,
        #                                    rates_frame.close.values, penetration=0)
        #     if modec[9] == 100 or modec[9] == -100:
        #         if modec[9] == 100 and (macd_trend == 'BUY_TRAND_H1' or macd_trend == 'BUY_TRAND_H4' or macd_trend =='BUY_TRAND_D'):
        #             order_Type = '��'
        #             moderedme = ' MACD����[��ͷ]���Ƶ���,��ǰK����̬Ϊ['
        #         elif modec[9] == -100 and (macd_trend == 'SELL_TRAND_H1' or macd_trend == 'SELL_TRAND_H4' or macd_trend == 'SELL_TRAND_D') :
        #             order_Type = '����'
        #             moderedme = 'MACD����[��ͷ]���Ƶ��У���ǰK����̬Ϊ['
        #         try:
        #             contents.append('<p><strong>���Ҷң�[' + symbol + ']' + moderedme + order_Type + ']��Ӥģʽ</strong></p>����K'
        #                                                                                          '��ģʽ���ڶ��ռ۸���������ʮ���ǣ����̼������̼۽ӽ��� '
        #                                                                                          '��߼���ͼ����󣩣�Ԥʾ���Ʒ�ת�������ڶ����µ����ײ����ǡ�')
        #             attrfile = generatebar.CandlesstickPng.GenerateBarPng(symbol, run_time)
        #             images.append(attrfile)
        #         except Exception:
        #             log.error('���ͻ��Ҷң�' + symbol + '�ʼ���Ϣʧ�ܣ� ��ǰģʽΪ����Ӥ' + str(e))
        #     '''
        #     ��������CDLADVANCEBLOCK
        #     ���ƣ�Advance Block ��е�ǰ
        #     ��飺����K��ģʽ�����ն�������ÿ�����̼۶���ǰһ�ոߣ� ���̼۶���ǰһ��ʵ�����ڣ�ʵ���̣���Ӱ�߱䳤��
        #     '''
        #     modec = talib.CDLADVANCEBLOCK(rates_frame.open.values, rates_frame.high.values, rates_frame.low.values,
        #                                   rates_frame.close.values)
        #     if modec[9] == 100 or modec[9] == -100:
        #         if modec[9] == 100 and (macd_trend == 'BUY_TRAND_H1' or macd_trend == 'BUY_TRAND_H4' or macd_trend =='BUY_TRAND_D'):
        #             order_Type = '��'
        #             moderedme = ' MACD����[��ͷ]���Ƶ���,��ǰK����̬Ϊ['
        #         elif modec[9] == -100 and (macd_trend == 'SELL_TRAND_H1' or macd_trend == 'SELL_TRAND_H4' or macd_trend == 'SELL_TRAND_D') :
        #             order_Type = '����'
        #             moderedme = 'MACD����[��ͷ]���Ƶ��У���ǰK����̬Ϊ['
        #         try:
        #             contents.append(
        #                 '<p><strong>���Ҷң�[' + symbol + ']' + moderedme + order_Type + ']��е�ǰģʽ</strong></p>����K'
        #                                                                              '��ģʽ�����ն�������ÿ�����̼۶���ǰһ�ոߣ� '
        #                                                                              '���̼۶���ǰһ��ʵ�����ڣ�ʵ���̣���Ӱ�߱䳤��')
        #             attrfile = generatebar.CandlesstickPng.GenerateBarPng(symbol, run_time)
        #             images.append(attrfile)
        #         except Exception as e:
        #             log.error('���ͻ��Ҷң�' + symbol + '�ʼ���Ϣʧ�ܣ� ��ǰģʽΪ����е�ǰ' + str(e))
        #     '''
        #     ��������CDLBELTHOLD
        #     ���ƣ�Belt-hold ׽������
        #     ��飺����K��ģʽ���µ������У���һ�����ߣ� �ڶ��տ��̼�Ϊ��ͼۣ����ߣ����̼۽ӽ���߼ۣ�Ԥʾ�۸����ǡ�
        #     '''
        #     modec = talib.CDLBELTHOLD(rates_frame.open.values, rates_frame.high.values, rates_frame.low.values,
        #                               rates_frame.close.values)
        #     if modec[9] == 100 or modec[9] == -100:
        #         if modec[9] == 100 and (macd_trend == 'BUY_TRAND_H1' or macd_trend == 'BUY_TRAND_H4' or macd_trend =='BUY_TRAND_D'):
        #             order_Type = '��'
        #             moderedme = ' MACD����[��ͷ]���Ƶ���,��ǰK����̬Ϊ['
        #         elif modec[9] == -100 and (macd_trend == 'SELL_TRAND_H1' or macd_trend == 'SELL_TRAND_H4' or macd_trend == 'SELL_TRAND_D') :
        #             order_Type = '����'
        #             moderedme = 'MACD����[��ͷ]���Ƶ��У���ǰK����̬Ϊ['
        #         try:
        #             contents.append(
        #                 '<p><strong>���Ҷң�[' + symbol + ']' + moderedme + order_Type + ']׽������ģʽ</strong></p>����K'
        #                                                                              '��ģʽ���µ������У���һ�����ߣ� '
        #                                                                              '�ڶ��տ��̼�Ϊ��ͼۣ����ߣ����̼۽ӽ���߼ۣ�Ԥʾ�۸����ǡ�')
        #             attrfile = generatebar.CandlesstickPng.GenerateBarPng(symbol, run_time)
        #             images.append(attrfile)
        #         except Exception as e:
        #             log.error('���ͻ��Ҷң�' + symbol + '�ʼ���Ϣʧ�ܣ� ��ǰģʽΪ��׽������' + str(e))
        #
        #     '''
        #     ��������CDLBREAKAWAY
        #     ���ƣ�Breakaway ����
        #     ��飺����K��ģʽ���Կ�������Ϊ�����µ������У���һ�ճ����ߣ��ڶ����������ߣ��������ƿ�ʼ�𵴣� �����ճ����ߣ����̼��ڵ�һ�����̼���ڶ��쿪�̼�֮�䣬Ԥʾ�۸����ǡ�
        #     '''
        #     modec = talib.CDLBREAKAWAY(rates_frame.open.values, rates_frame.high.values, rates_frame.low.values,
        #                                rates_frame.close.values)
        #     if modec[9] == 100 or modec[9] == -100:
        #         if modec[9] == 100 and (macd_trend == 'BUY_TRAND_H1' or macd_trend == 'BUY_TRAND_H4' or macd_trend =='BUY_TRAND_D'):
        #             order_Type = '��'
        #             moderedme = ' MACD����[��ͷ]���Ƶ���,��ǰK����̬Ϊ['
        #         elif modec[9] == -100 and (macd_trend == 'SELL_TRAND_H1' or macd_trend == 'SELL_TRAND_H4' or macd_trend == 'SELL_TRAND_D') :
        #             order_Type = '����'
        #             moderedme = 'MACD����[��ͷ]���Ƶ��У���ǰK����̬Ϊ['
        #         try:
        #             contents.append('<p><strong>���Ҷң�[' + symbol + ']' + moderedme + order_Type + ']����ģʽ</strong></p>����K'
        #                                                                                          '��ģʽ���Կ�������Ϊ�����µ������У���һ�ճ����ߣ��ڶ����������ߣ��������ƿ�ʼ�𵴣� �����ճ����ߣ����̼��ڵ�һ�����̼���ڶ��쿪�̼�֮�䣬Ԥʾ�۸����ǡ�')
        #             attrfile = generatebar.CandlesstickPng.GenerateBarPng(symbol, run_time)
        #             images.append(attrfile)
        #         except Exception as e:
        #             log.error('���ͻ��Ҷң�' + symbol + '�ʼ���Ϣʧ�ܣ� ��ǰģʽΪ������' + str(e))
        #
        #     '''
        #     ��������CDLCLOSINGMARUBOZU
        #     ���ƣ�Closing Marubozu ����ȱӰ��
        #     ��飺һ��K��ģʽ��������Ϊ������ͼ۵��ڿ��̼ۣ����̼۵�����߼ۣ� Ԥʾ�����Ƴ�����
        #     '''
        #     modec = talib.CDLCLOSINGMARUBOZU(rates_frame.open.values, rates_frame.high.values, rates_frame.low.values,
        #                                      rates_frame.close.values)
        #     if modec[9] == 100 or modec[9] == -100:
        #         if modec[9] == 100 and (macd_trend == 'BUY_TRAND_H1' or macd_trend == 'BUY_TRAND_H4' or macd_trend =='BUY_TRAND_D'):
        #             order_Type = '��'
        #             moderedme = ' MACD����[��ͷ]���Ƶ���,��ǰK����̬Ϊ['
        #         elif modec[9] == -100 and (macd_trend == 'SELL_TRAND_H1' or macd_trend == 'SELL_TRAND_H4' or macd_trend == 'SELL_TRAND_D') :
        #             order_Type = '����'
        #             moderedme = 'MACD����[��ͷ]���Ƶ��У���ǰK����̬Ϊ['
        #         try:
        #             contents.append(
        #                 '<p><strong>���Ҷң�[' + symbol + ']' + moderedme + order_Type + ']����ȱӰ��ģʽ</strong></p>һ��K'
        #                                                                              '��ģʽ��������Ϊ������ͼ۵��ڿ��̼ۣ����̼۵�����߼ۣ� '
        #                                                                              'Ԥʾ�����Ƴ�����')
        #             attrfile = generatebar.CandlesstickPng.GenerateBarPng(symbol, run_time)
        #             images.append(attrfile)
        #         except Exception as e:
        #             log.error('���ͻ��Ҷң�' + symbol + '�ʼ���Ϣʧ�ܣ� ��ǰģʽΪ������ȱӰ��' + str(e))
        #     '''
        #     ��������CDLCONCEALBABYSWALL
        #     ���ƣ� Concealing Baby Swallow ��Ӥ��û
        #     ��飺����K��ģʽ���µ������У�ǰ����������Ӱ�� ���ڶ��տ��̡����̼۽Ե��ڵڶ��գ������յ���ͷ�� �����տ��̼۸���ǰһ����߼ۣ����̼۵���ǰһ����ͼۣ�Ԥʾ�ŵײ���ת��
        #     '''
        #     modec = talib.CDLCONCEALBABYSWALL(rates_frame.open.values, rates_frame.high.values, rates_frame.low.values,
        #                                       rates_frame.close.values)
        #     if modec[9] == 100 or modec[9] == -100:
        #         if modec[9] == 100 and (macd_trend == 'BUY_TRAND_H1' or macd_trend == 'BUY_TRAND_H4' or macd_trend =='BUY_TRAND_D'):
        #             order_Type = '��'
        #             moderedme = ' MACD����[��ͷ]���Ƶ���,��ǰK����̬Ϊ['
        #         elif modec[9] == -100 and (macd_trend == 'SELL_TRAND_H1' or macd_trend == 'SELL_TRAND_H4' or macd_trend == 'SELL_TRAND_D') :
        #             order_Type = '����'
        #             moderedme = 'MACD����[��ͷ]���Ƶ��У���ǰK����̬Ϊ['
        #         try:
        #             contents.append(
        #                 '<p><strong>���Ҷң�[' + symbol + ']' + moderedme + order_Type + ']��Ӥ��ûģʽ</strong></p>����K'
        #                                                                              '��ģʽ���µ������У�ǰ����������Ӱ�� '
        #                                                                              '���ڶ��տ��̡����̼۽Ե��ڵڶ��գ������յ���ͷ�� '
        #                                                                              '�����տ��̼۸���ǰһ����߼ۣ����̼۵���ǰһ����ͼۣ�Ԥʾ�ŵײ���ת��')
        #             attrfile = generatebar.CandlesstickPng.GenerateBarPng(symbol, run_time)
        #             images.append(attrfile)
        #         except Exception as e:
        #             log.error('���ͻ��Ҷң�' + symbol + '�ʼ���Ϣʧ�ܣ� ��ǰģʽΪ����Ӥ��û' + str(e))
        #     '''
        #     ��������CDLCOUNTERATTACK
        #     ���ƣ�Counterattack ������
        #     ��飺����K��ģʽ������������ơ�
        #     '''
        #     modec = talib.CDLCOUNTERATTACK(rates_frame.open.values, rates_frame.high.values, rates_frame.low.values,
        #                                    rates_frame.close.values)
        #     if modec[9] == 100 or modec[9] == -100:
        #         if modec[9] == 100 and (macd_trend == 'BUY_TRAND_H1' or macd_trend == 'BUY_TRAND_H4' or macd_trend =='BUY_TRAND_D'):
        #             order_Type = '��'
        #             moderedme = ' MACD����[��ͷ]���Ƶ���,��ǰK����̬Ϊ['
        #         elif modec[9] == -100 and (macd_trend == 'SELL_TRAND_H1' or macd_trend == 'SELL_TRAND_H4' or macd_trend == 'SELL_TRAND_D') :
        #             order_Type = '����'
        #             moderedme = 'MACD����[��ͷ]���Ƶ��У���ǰK����̬Ϊ['
        #         try:
        #             contents.append(
        #                 '<p><strong>���Ҷң�[' + symbol + ']' + moderedme + order_Type + ']������ģʽ</strong></p>����K��ģʽ������������ơ�')
        #             attrfile = generatebar.CandlesstickPng.GenerateBarPng(symbol, run_time)
        #             images.append(attrfile)
        #         except Exception as e:
        #             log.error('���ͻ��Ҷң�' + symbol + '�ʼ���Ϣʧ�ܣ� ��ǰģʽΪ��������' + str(e))
        #
        #     '''
        #     ��������CDLDARKCLOUDCOVER
        #     ���ƣ�Dark Cloud Cover ����ѹ��
        #     ��飺����K��ģʽ����һ�ճ������ڶ��տ��̼۸���ǰһ����߼ۣ� ���̼۴���ǰһ��ʵ���в����£�Ԥʾ�Źɼ��µ���
        #     '''
        #     modec = talib.CDLDARKCLOUDCOVER(rates_frame.open.values, rates_frame.high.values, rates_frame.low.values,
        #                                     rates_frame.close.values)
        #     if modec[9] == 100 or modec[9] == -100:
        #         if modec[9] == 100 and (macd_trend == 'BUY_TRAND_H1' or macd_trend == 'BUY_TRAND_H4' or macd_trend =='BUY_TRAND_D'):
        #             order_Type = '��'
        #             moderedme = ' MACD����[��ͷ]���Ƶ���,��ǰK����̬Ϊ['
        #         elif modec[9] == -100 and (macd_trend == 'SELL_TRAND_H1' or macd_trend == 'SELL_TRAND_H4' or macd_trend == 'SELL_TRAND_D') :
        #             order_Type = '����'
        #             moderedme = 'MACD����[��ͷ]���Ƶ��У���ǰK����̬Ϊ['
        #         try:
        #             contents.append(
        #                 '<p><strong>���Ҷң�[' + symbol + ']' + moderedme + order_Type + ']����ѹ��ģʽ</strong></p>����K'
        #                                                                              '��ģʽ����һ�ճ������ڶ��տ��̼۸���ǰһ����߼ۣ� '
        #                                                                              '���̼۴���ǰһ��ʵ���в����£�Ԥʾ�Źɼ��µ���')
        #             attrfile = generatebar.CandlesstickPng.GenerateBarPng(symbol, run_time)
        #             images.append(attrfile)
        #         except Exception as e:
        #             log.error('���ͻ��Ҷң�' + symbol + '�ʼ���Ϣʧ�ܣ� ��ǰģʽΪ������ѹ��' + str(e))
        #     '''
        #     ��������CDLDOJI
        #     ���ƣ�Doji ʮ��
        #     ��飺һ��K��ģʽ�����̼������̼ۻ�����ͬ��
        #     '''
        #     modec = talib.CDLDOJI(rates_frame.open.values, rates_frame.high.values, rates_frame.low.values,
        #                           rates_frame.close.values)
        #     if modec[9] == 100 or modec[9] == -100:
        #         if modec[9] == 100 and (macd_trend == 'BUY_TRAND_H1' or macd_trend == 'BUY_TRAND_H4' or macd_trend =='BUY_TRAND_D'):
        #             order_Type = '��'
        #             moderedme = ' MACD����[��ͷ]���Ƶ���,��ǰK����̬Ϊ['
        #         elif modec[9] == -100 and (macd_trend == 'SELL_TRAND_H1' or macd_trend == 'SELL_TRAND_H4' or macd_trend == 'SELL_TRAND_D') :
        #             order_Type = '����'
        #             moderedme = 'MACD����[��ͷ]���Ƶ��У���ǰK����̬Ϊ['
        #         try:
        #             contents.append(
        #                 '<p><strong>���Ҷң�[' + symbol + ']' + moderedme + order_Type + ']ʮ��ģʽ</strong></p>һ��K��ģʽ�����̼������̼ۻ�����ͬ��')
        #             attrfile = generatebar.CandlesstickPng.GenerateBarPng(symbol, run_time)
        #             images.append(attrfile)
        #         except Exception as e:
        #             log.error('���ͻ��Ҷң�' + symbol + '�ʼ���Ϣʧ�ܣ� ��ǰģʽΪ��ʮ��' + str(e))
        #
        #     '''
        #     ��������CDLDOJISTAR
        #     ���ƣ�Doji Star ʮ����
        #     ��飺һ��K��ģʽ�����̼������̼ۻ�����ͬ������Ӱ�߲���ܳ���Ԥʾ�ŵ�ǰ���Ʒ�ת��
        #     '''
        #     modec = talib.CDLDOJISTAR(rates_frame.open.values, rates_frame.high.values, rates_frame.low.values,
        #                               rates_frame.close.values)
        #     if modec[9] == 100 or modec[9] == -100:
        #         if modec[9] == 100 and (macd_trend == 'BUY_TRAND_H1' or macd_trend == 'BUY_TRAND_H4' or macd_trend =='BUY_TRAND_D'):
        #             order_Type = '��'
        #             moderedme = ' MACD����[��ͷ]���Ƶ���,��ǰK����̬Ϊ['
        #         elif modec[9] == -100 and (macd_trend == 'SELL_TRAND_H1' or macd_trend == 'SELL_TRAND_H4' or macd_trend == 'SELL_TRAND_D') :
        #             order_Type = '����'
        #             moderedme = 'MACD����[��ͷ]���Ƶ��У���ǰK����̬Ϊ['
        #         try:
        #             contents.append('<p><strong>���Ҷң�[' + symbol + ']' + moderedme + order_Type + ']ʮ����ģʽ</strong></p> '
        #                                                                                          'һ��K��ģʽ�����̼������̼ۻ�����ͬ������Ӱ�߲���ܳ���Ԥʾ�ŵ�ǰ���Ʒ�ת��')
        #             attrfile = generatebar.CandlesstickPng.GenerateBarPng(symbol, run_time)
        #             images.append(attrfile)
        #         except Exception as e:
        #             log.error('���ͻ��Ҷң�' + symbol + '�ʼ���Ϣʧ�ܣ� ��ǰģʽΪ��ʮ����' + str(e))
        #     '''
        #     ��������CDLDRAGONFLYDOJI
        #     ���ƣ�Dragonfly Doji ����ʮ��/T��ʮ��
        #     ��飺һ��K��ģʽ�����̺�۸�һ·�ߵͣ� ֮���ո������̼��뿪�̼���ͬ��Ԥʾ���Ʒ�ת��
        #     '''
        #
        #     modec = talib.CDLDRAGONFLYDOJI(rates_frame.open.values, rates_frame.high.values, rates_frame.low.values,
        #                                    rates_frame.close.values)
        #     if modec[9] == 100 or modec[9] == -100:
        #         if modec[9] == 100 and (macd_trend == 'BUY_TRAND_H1' or macd_trend == 'BUY_TRAND_H4' or macd_trend =='BUY_TRAND_D'):
        #             order_Type = '��'
        #             moderedme = ' MACD����[��ͷ]���Ƶ���,��ǰK����̬Ϊ['
        #         elif modec[9] == -100 and (macd_trend == 'SELL_TRAND_H1' or macd_trend == 'SELL_TRAND_H4' or macd_trend == 'SELL_TRAND_D') :
        #             order_Type = '����'
        #             moderedme = 'MACD����[��ͷ]���Ƶ��У���ǰK����̬Ϊ['
        #         try:
        #             contents.append(
        #                 '<p><strong>���Ҷң�[' + symbol + ']' + moderedme + order_Type + ']����ʮ��/T��ʮ��ģʽ</strong></p>һ��K'
        #                                                                              '��ģʽ�����̺�۸�һ·�ߵͣ� '
        #                                                                              '֮���ո������̼��뿪�̼���ͬ��Ԥʾ���Ʒ�ת��')
        #             attrfile = generatebar.CandlesstickPng.GenerateBarPng(symbol, run_time)
        #             images.append(attrfile)
        #         except Exception as e:
        #             log.error('���ͻ��Ҷң�' + symbol + '�ʼ���Ϣʧ�ܣ� ��ǰģʽΪ������ʮ��/T��ʮ��' + str(e))
        #
        #     '''
        #     ��������CDLENGULFING
        #     ���ƣ�Engulfing Pattern ����ģʽ
        #     ��飺����K��ģʽ���ֶ�ͷ���ɺͿ�ͷ���ɣ��Զ�ͷ����Ϊ������һ��Ϊ���ߣ� �ڶ������ߣ���һ�յĿ��̼ۺ����̼��ڵڶ��տ��̼����̼�֮�ڣ���������ȫ��ͬ��
        #     '''
        #     # modec=talib.CDLENGULFING(rates_frame.open.values,rates_frame.high.values,rates_frame.low.values,rates_frame.close.values)
        #     # if modec[9]!=0:
        #     #     try:
        #     #         contents.append('<p><strong>���Ҷң�['+symbol+']��ͷ���ͷ����ģʽ</strong></p>����K��ģʽ���ֶ�ͷ���ɺͿ�ͷ���ɣ��Զ�ͷ����Ϊ������һ��Ϊ���ߣ� �ڶ������ߣ���һ�յĿ��̼ۺ����̼��ڵڶ��տ��̼����̼�֮�ڣ���������ȫ��ͬ��')
        #     #         attrfile =  generatebar.CandlesstickPng.GenerateBarPng(symbol,run_time)
        #     #         images.append(attrfile)
        #     #     except Exception as e:
        #     #         #print("�����ʼ�ʧ��")
        #     #         log.error('���ͻ��Ҷң�'+symbol+'�ʼ���Ϣʧ�ܣ� ��ǰģʽΪ������ģʽ'+str(e))
        #
        #     '''
        #     ��������CDLEVENINGDOJISTAR
        #     ���ƣ�Evening Doji Star ʮ��ĺ��
        #     ��飺����K��ģʽ������ģʽΪĺ�ǣ��ڶ������̼ۺͿ��̼���ͬ��Ԥʾ������ת��
        #     '''
        #     modec = talib.CDLEVENINGDOJISTAR(rates_frame.open.values, rates_frame.high.values, rates_frame.low.values,
        #                                      rates_frame.close.values, penetration=0)
        #     if modec[9] == 100 or modec[9] == -100:
        #         if modec[9] == 100 and (macd_trend == 'BUY_TRAND_H1' or macd_trend == 'BUY_TRAND_H4' or macd_trend =='BUY_TRAND_D'):
        #             order_Type = '��'
        #             moderedme = ' MACD����[��ͷ]���Ƶ���,��ǰK����̬Ϊ['
        #         elif modec[9] == -100 and (macd_trend == 'SELL_TRAND_H1' or macd_trend == 'SELL_TRAND_H4' or macd_trend == 'SELL_TRAND_D') :
        #             order_Type = '����'
        #             moderedme = 'MACD����[��ͷ]���Ƶ��У���ǰK����̬Ϊ['
        #         try:
        #             contents.append('<p><strong>���Ҷң�[' + symbol + ']' + moderedme + order_Type + ']ʮ��ĺ��ģʽ<strong><p>����K'
        #                                                                                          '��ģʽ������ģʽΪĺ�ǣ��ڶ������̼ۺͿ��̼���ͬ��Ԥʾ������ת��')
        #             attrfile = generatebar.CandlesstickPng.GenerateBarPng(symbol, run_time)
        #             images.append(attrfile)
        #         except Exception as e:
        #             log.error('���ͻ��Ҷң�' + symbol + '�ʼ���Ϣʧ�ܣ� ��ǰģʽΪ��ʮ��ĺ��' + str(e))
        #
        #     '''
        #     ��������CDLEVENINGSTAR
        #     ���ƣ�Evening Star ĺ��
        #     ��飺����K��ģʽ���볿���෴������������, ��һ�����ߣ��ڶ��ռ۸������С�����������ߣ�Ԥʾ������ת��
        #     '''
        #     modec = talib.CDLEVENINGSTAR(rates_frame.open.values, rates_frame.high.values, rates_frame.low.values,
        #                                  rates_frame.close.values, penetration=0)
        #     if modec[9] == 100 or modec[9] == -100:
        #         if modec[9] == 100 and (macd_trend == 'BUY_TRAND_H1' or macd_trend == 'BUY_TRAND_H4' or macd_trend =='BUY_TRAND_D'):
        #             order_Type = '��'
        #             moderedme = ' MACD����[��ͷ]���Ƶ���,��ǰK����̬Ϊ['
        #         elif modec[9] == -100 and (macd_trend == 'SELL_TRAND_H1' or macd_trend == 'SELL_TRAND_H4' or macd_trend == 'SELL_TRAND_D') :
        #             order_Type = '����'
        #             moderedme = 'MACD����[��ͷ]���Ƶ��У���ǰK����̬Ϊ['
        #         try:
        #             contents.append('<p><strong>���Ҷң�[' + symbol + ']' + moderedme + order_Type + ']ĺ��ģʽ</strong></p>����K'
        #                                                                                          '��ģʽ���볿���෴������������, '
        #                                                                                          '��һ�����ߣ��ڶ��ռ۸������С�����������ߣ�Ԥʾ������ת��')
        #             attrfile = generatebar.CandlesstickPng.GenerateBarPng(symbol, run_time)
        #             images.append(attrfile)
        #         except Exception as e:
        #             log.error('���Ҷң�' + symbol + '�ʼ���Ϣʧ�ܣ� ��ǰģʽΪ��ĺ��' + str(e))
        #
        #     '''
        #     ��������CDLGAPSIDESIDEWHITE
        #     ���ƣ�Up/Down-gap side-by-side white lines ����/�����ղ�������
        #     ��飺����K��ģʽ�����������������գ��µ�������������, ��һ����ڶ�������ͬ���̼ۣ�ʵ�峤�Ȳ�࣬�����Ƴ�����
        #     '''
        #     # modec=talib.CDLGAPSIDESIDEWHITE(rates_frame.open.values,rates_frame.high.values,rates_frame.low.values,rates_frame.close.values)
        #     # if modec[9]!=0:
        #     #     try:
        #     #         contents.append('<p><strong>���Ҷң�['+symbol+']����/�����ղ�������</strong></p>����K��ģʽ�����������������գ��µ�������������, ��һ����ڶ�������ͬ���̼ۣ�ʵ�峤�Ȳ�࣬�����Ƴ�����')
        #     #         attrfile =  generatebar.CandlesstickPng.GenerateBarPng(symbol,run_time)
        #     #         images.append(attrfile)
        #     #     except Exception as e:
        #     #         #print("�����ʼ�ʧ��")
        #     #         log.error('���ͻ��Ҷң�'+symbol+'�ʼ���Ϣʧ�ܣ� ��ǰģʽΪ������/�����ղ�������'+str(e))
        #
        #     '''
        #     ��������CDLGRAVESTONEDOJI
        #     ���ƣ�Gravestone Doji Ĺ��ʮ��/��Tʮ��
        #     ��飺һ��K��ģʽ�����̼������̼���ͬ����Ӱ�߳�������Ӱ�ߣ�Ԥʾ�ײ���ת��
        #     '''
        #     modec = talib.CDLGRAVESTONEDOJI(rates_frame.open.values, rates_frame.high.values, rates_frame.low.values,
        #                                     rates_frame.close.values)
        #     if modec[9] == 100 or modec[9] == -100:
        #         if modec[9] == 100 and (macd_trend == 'BUY_TRAND_H1' or macd_trend == 'BUY_TRAND_H4' or macd_trend =='BUY_TRAND_D'):
        #             order_Type = '��'
        #             moderedme = ' MACD����[��ͷ]���Ƶ���,��ǰK����̬Ϊ['
        #         elif modec[9] == -100 and (macd_trend == 'SELL_TRAND_H1' or macd_trend == 'SELL_TRAND_H4' or macd_trend == 'SELL_TRAND_D') :
        #             order_Type = '����'
        #             moderedme = 'MACD����[��ͷ]���Ƶ��У���ǰK����̬Ϊ['
        #         try:
        #             contents.append(
        #                 '<p><strong>���Ҷң�[' + symbol + ']' + moderedme + order_Type + ']Ĺ��ʮ��/��Tʮ��ģʽ</strong></p> '
        #                                                                              'һ��K��ģʽ�����̼������̼���ͬ����Ӱ�߳�������Ӱ�ߣ�Ԥʾ�ײ���ת��')
        #             attrfile = generatebar.CandlesstickPng.GenerateBarPng(symbol, run_time)
        #             images.append(attrfile)
        #         except Exception as e:
        #             log.error('���ͻ��Ҷң�' + symbol + '�ʼ���Ϣʧ�ܣ� ��ǰģʽΪ��Ĺ��ʮ��/��Tʮ��' + str(e))
        #
        #     '''
        #     ��������CDLHAMMER
        #     ���ƣ�Hammer ��ͷ
        #     ��飺һ��K��ģʽ��ʵ��϶̣�����Ӱ�ߣ� ��Ӱ�ߴ���ʵ�峤�������������µ����Ƶײ���Ԥʾ��ת��
        #     '''
        #     modec = talib.CDLHAMMER(rates_frame.open.values, rates_frame.high.values, rates_frame.low.values,
        #                             rates_frame.close.values)
        #     if modec[9] == 100 or modec[9] == -100:
        #         if modec[9] == 100 and (macd_trend == 'BUY_TRAND_H1' or macd_trend == 'BUY_TRAND_H4' or macd_trend =='BUY_TRAND_D'):
        #             order_Type = '��'
        #             moderedme = ' MACD����[��ͷ]���Ƶ���,��ǰK����̬Ϊ['
        #         elif modec[9] == -100 and (macd_trend == 'SELL_TRAND_H1' or macd_trend == 'SELL_TRAND_H4' or macd_trend == 'SELL_TRAND_D') :
        #             order_Type = '����'
        #             moderedme = 'MACD����[��ͷ]���Ƶ��У���ǰK����̬Ϊ['
        #         try:
        #             contents.append(
        #                 '<p><strong>���Ҷң�[' + symbol + ']' + moderedme + order_Type + ']��ͷģʽ</strong></p>һ��K��ģʽ��ʵ��϶̣�����Ӱ�ߣ� ��Ӱ�ߴ���ʵ�峤�������������µ����Ƶײ���Ԥʾ��ת��')
        #             attrfile = generatebar.CandlesstickPng.GenerateBarPng(symbol, run_time)
        #             images.append(attrfile)
        #         except Exception as e:
        #             log.error('���ͻ��Ҷң�' + symbol + '�ʼ���Ϣʧ�ܣ� ��ǰģʽΪ����ͷ' + str(e))
        #
        #     '''
        #     ��������CDLHANGINGMAN
        #     ���ƣ�Hanging Man �ϵ���
        #     ��飺һ��K��ģʽ����״�봸�����ƣ������������ƵĶ�����Ԥʾ�����Ʒ�ת��
        #     '''
        #     modec = talib.CDLHANGINGMAN(rates_frame.open.values, rates_frame.high.values, rates_frame.low.values,
        #                                 rates_frame.close.values)
        #     if modec[9] == 100 or modec[9] == -100:
        #         if modec[9] == 100 and (macd_trend == 'BUY_TRAND_H1' or macd_trend == 'BUY_TRAND_H4' or macd_trend =='BUY_TRAND_D'):
        #             order_Type = '��'
        #             moderedme = ' MACD����[��ͷ]���Ƶ���,��ǰK����̬Ϊ['
        #         elif modec[9] == -100 and (macd_trend == 'SELL_TRAND_H1' or macd_trend == 'SELL_TRAND_H4' or macd_trend == 'SELL_TRAND_D') :
        #             order_Type = '����'
        #             moderedme = 'MACD����[��ͷ]���Ƶ��У���ǰK����̬Ϊ['
        #         try:
        #             contents.append(
        #                 '<p><strong>���Ҷң�[' + symbol + ']' + moderedme + order_Type + ']�ϵ���ģʽ</strong></p>һ��K��ģʽ����״�봸�����ƣ������������ƵĶ�����Ԥʾ�����Ʒ�ת��')
        #             attrfile = generatebar.CandlesstickPng.GenerateBarPng(symbol, run_time)
        #             images.append(attrfile)
        #         except Exception as e:
        #             log.error('���ͻ��Ҷң�' + symbol + '�ʼ���Ϣʧ�ܣ� ��ǰģʽΪ���ϵ���' + str(e))
        #
        #     '''
        #     ��������CDLHARAMI
        #     ���ƣ�Harami Pattern ĸ����
        #     ��飺����K��ģʽ���ֶ�ͷĸ�����ͷĸ�ӣ������෴���Զ�ͷĸ��Ϊ�������µ������У���һ��K�߳����� �ڶ��տ��̼����̼��ڵ�һ�ռ۸����֮�ڣ�Ϊ���ߣ�Ԥʾ���Ʒ�ת���ɼ�������
        #     '''
        #     modec = talib.CDLHARAMI(rates_frame.open.values, rates_frame.high.values, rates_frame.low.values,
        #                             rates_frame.close.values)
        #     if modec[9] == 100 or modec[9] == -100:
        #         if modec[9] == 100 and (macd_trend == 'BUY_TRAND_H1' or macd_trend == 'BUY_TRAND_H4' or macd_trend =='BUY_TRAND_D'):
        #             order_Type = '��'
        #             moderedme = ' MACD����[��ͷ]���Ƶ���,��ǰK����̬Ϊ['
        #         elif modec[9] == -100 and (macd_trend == 'SELL_TRAND_H1' or macd_trend == 'SELL_TRAND_H4' or macd_trend == 'SELL_TRAND_D') :
        #             order_Type = '����'
        #             moderedme = 'MACD����[��ͷ]���Ƶ��У���ǰK����̬Ϊ['
        #         try:
        #             contents.append('<p><strong>���Ҷң�[' + symbol + ']' + moderedme + order_Type + ']ĸ����ģʽ</strong></p> '
        #                                                                                          '����K'
        #                                                                                          '��ģʽ���ֶ�ͷĸ�����ͷĸ�ӣ������෴���Զ�ͷĸ��Ϊ�������µ������У���һ��K�߳����� �ڶ��տ��̼����̼��ڵ�һ�ռ۸����֮�ڣ�Ϊ���ߣ�Ԥʾ���Ʒ�ת���ɼ�������')
        #             attrfile = generatebar.CandlesstickPng.GenerateBarPng(symbol, run_time)
        #             images.append(attrfile)
        #         except Exception as e:
        #             log.error('���ͻ��Ҷң�' + symbol + '�ʼ���Ϣʧ�ܣ� ��ǰģʽΪ��ĸ����' + str(e))
        #
        #     '''
        #     ��������CDLHARAMICROSS
        #     ���ƣ�Harami Cross Pattern ʮ������
        #     ��飺����K��ģʽ����ĸ�������ƣ����ڶ���K����ʮ���ߣ� ���Ϊʮ�����ߣ�Ԥʾ�����Ʒ�ת��
        #     '''
        #     modec = talib.CDLHARAMICROSS(rates_frame.open.values, rates_frame.high.values, rates_frame.low.values,
        #                                  rates_frame.close.values)
        #     if modec[9] == 100 or modec[9] == -100:
        #         if modec[9] == 100 and (macd_trend == 'BUY_TRAND_H1' or macd_trend == 'BUY_TRAND_H4' or macd_trend =='BUY_TRAND_D'):
        #             order_Type = '��'
        #             moderedme = ' MACD����[��ͷ]���Ƶ���,��ǰK����̬Ϊ['
        #         elif modec[9] == -100 and (macd_trend == 'SELL_TRAND_H1' or macd_trend == 'SELL_TRAND_H4' or macd_trend == 'SELL_TRAND_D') :
        #             order_Type = '����'
        #             moderedme = 'MACD����[��ͷ]���Ƶ��У���ǰK����̬Ϊ['
        #         try:
        #             contents.append('<p><strong>���Ҷң�[' + symbol + ']' + moderedme + order_Type + ']ʮ������ģʽ</strong></p> '
        #                                                                                          '����K��ģʽ����ĸ�������ƣ����ڶ���K����ʮ���ߣ� '
        #                                                                                          '���Ϊʮ�����ߣ�Ԥʾ�����Ʒ�ת��')
        #             attrfile = generatebar.CandlesstickPng.GenerateBarPng(symbol, run_time)
        #             images.append(attrfile)
        #         except Exception as e:
        #             log.error('���ͻ��Ҷң�' + symbol + '�ʼ���Ϣʧ�ܣ� ��ǰģʽΪ��ʮ������' + str(e))
        #
        #     '''
        #     ��������CDLHIGHWAVE
        #     ���ƣ�High-Wave Candle ����˴���
        #     ��飺����K��ģʽ�����м�������/��Ӱ����̵�ʵ�壬Ԥʾ�����Ʒ�ת��
        #     '''
        #     modec = talib.CDLHIGHWAVE(rates_frame.open.values, rates_frame.high.values, rates_frame.low.values,
        #                               rates_frame.close.values)
        #     if modec[9] == 100 or modec[9] == -100:
        #         if modec[9] == 100 and (macd_trend == 'BUY_TRAND_H1' or macd_trend == 'BUY_TRAND_H4' or macd_trend =='BUY_TRAND_D'):
        #             order_Type = '��'
        #             moderedme = ' MACD����[��ͷ]���Ƶ���,��ǰK����̬Ϊ['
        #         elif modec[9] == -100 and (macd_trend == 'SELL_TRAND_H1' or macd_trend == 'SELL_TRAND_H4' or macd_trend == 'SELL_TRAND_D') :
        #             order_Type = '����'
        #             moderedme = 'MACD����[��ͷ]���Ƶ��У���ǰK����̬Ϊ['
        #         try:
        #             contents.append(
        #                 '<p><strong>���Ҷң�[' + symbol + ']' + moderedme + order_Type + ']����˴���ģʽ</strong></p>����K'
        #                                                                              '��ģʽ�����м�������/��Ӱ����̵�ʵ�壬Ԥʾ�����Ʒ�ת��')
        #             attrfile = generatebar.CandlesstickPng.GenerateBarPng(symbol, run_time)
        #             images.append(attrfile)
        #         except Exception as e:
        #             log.error('���ͻ��Ҷң�' + symbol + '�ʼ���Ϣʧ�ܣ� ��ǰģʽΪ������˴���' + str(e))
        #
        #     '''
        #     ��������CDLHIKKAKE
        #     ���ƣ�Hikkake Pattern ����
        #     ��飺����K��ģʽ����ĸ�����ƣ��ڶ��ռ۸���ǰһ��ʵ�巶Χ��, ���������̼۸���ǰ���գ���תʧ�ܣ����Ƽ�����
        #     '''
        #     # modec=talib.CDLHIKKAKE(rates_frame.open.values,rates_frame.high.values,rates_frame.low.values,rates_frame.close.values)
        #     # if modec[9]!=0:
        #     #     try:
        #     #         contents.append('<p><strong>���Ҷң�['+symbol+']����ģʽ</strong></p>����K��ģʽ����ĸ�����ƣ��ڶ��ռ۸���ǰһ��ʵ�巶Χ��, ���������̼۸���ǰ���գ���תʧ�ܣ����Ƽ�����')
        #     #         attrfile =  generatebar.CandlesstickPng.GenerateBarPng(symbol,run_time)
        #     #         images.append(attrfile)
        #     #     except Exception as e:
        #     #         #print("�����ʼ�ʧ��")
        #     #         log.error('���ͻ��Ҷң�'+symbol+'�ʼ���Ϣʧ�ܣ� ��ǰģʽΪ������'+str(e))
        #
        #     '''
        #     ��������CDLHIKKAKEMOD
        #     ���ƣ�Modified Hikkake Pattern ��������
        #     ��飺����K��ģʽ�����������ƣ����������У����������ո߿��� �µ������У����������յͿ�����תʧ�ܣ����Ƽ�����
        #     '''
        #     modec = talib.CDLHIKKAKEMOD(rates_frame.open.values, rates_frame.high.values, rates_frame.low.values,
        #                                 rates_frame.close.values)
        #     if modec[9] == 100 or modec[9] == -100:
        #         if modec[9] == 100 and (macd_trend == 'BUY_TRAND_H1' or macd_trend == 'BUY_TRAND_H4' or macd_trend =='BUY_TRAND_D'):
        #             order_Type = '��'
        #             moderedme = ' MACD����[��ͷ]���Ƶ���,��ǰK����̬Ϊ['
        #         elif modec[9] == -100 and (macd_trend == 'SELL_TRAND_H1' or macd_trend == 'SELL_TRAND_H4' or macd_trend == 'SELL_TRAND_D') :
        #             order_Type = '����'
        #             moderedme = 'MACD����[��ͷ]���Ƶ��У���ǰK����̬Ϊ['
        #         try:
        #             contents.append(
        #                 '<p><strong>���Ҷң�[' + symbol + ']' + moderedme + order_Type + ']��������ģʽ</strong></p>����K'
        #                                                                              '��ģʽ�����������ƣ����������У����������ո߿��� '
        #                                                                              '�µ������У����������յͿ�����תʧ�ܣ����Ƽ�����')
        #             attrfile = generatebar.CandlesstickPng.GenerateBarPng(symbol, run_time)
        #             images.append(attrfile)
        #         except Exception as e:
        #             log.error('���ͻ��Ҷң�' + symbol + '�ʼ���Ϣʧ�ܣ� ��ǰģʽΪ����������' + str(e))
        #
        #     '''
        #     ��������CDLHOMINGPIGEON
        #     ���ƣ�Homing Pigeon �Ҹ�
        #     ��飺����K��ģʽ����ĸ�������ƣ���ͬ�ĵ��Ƕ���K����ɫ��ͬ�� �ڶ�����߼ۡ���ͼ۶��ڵ�һ��ʵ��֮�ڣ�Ԥʾ�����Ʒ�ת
        #     '''
        #     modec = talib.CDLHOMINGPIGEON(rates_frame.open.values, rates_frame.high.values, rates_frame.low.values,
        #                                   rates_frame.close.values)
        #     if modec[9] == 100 or modec[9] == -100:
        #         if modec[9] == 100 and (macd_trend == 'BUY_TRAND_H1' or macd_trend == 'BUY_TRAND_H4' or macd_trend =='BUY_TRAND_D'):
        #             order_Type = '��'
        #             moderedme = ' MACD����[��ͷ]���Ƶ���,��ǰK����̬Ϊ['
        #         elif modec[9] == -100 and (macd_trend == 'SELL_TRAND_H1' or macd_trend == 'SELL_TRAND_H4' or macd_trend == 'SELL_TRAND_D') :
        #             order_Type = '����'
        #             moderedme = 'MACD����[��ͷ]���Ƶ��У���ǰK����̬Ϊ['
        #         try:
        #             contents.append('<p><strong>���Ҷң�[' + symbol + ']' + moderedme + order_Type + ']�Ҹ�ģʽ</strong></p>����K'
        #                                                                                          '��ģʽ����ĸ�������ƣ���ͬ�ĵ��Ƕ���K����ɫ��ͬ�� '
        #                                                                                          '�ڶ�����߼ۡ���ͼ۶��ڵ�һ��ʵ��֮�ڣ�Ԥʾ�����Ʒ�ת.')
        #             attrfile = generatebar.CandlesstickPng.GenerateBarPng(symbol, run_time)
        #             images.append(attrfile)
        #         except Exception as e:
        #             log.error('���ͻ��Ҷң�' + symbol + '�ʼ���Ϣʧ�ܣ� ��ǰģʽΪ���Ҹ�' + str(e))
        #
        #     '''
        #     ��������CDLIDENTICAL3CROWS
        #     ���ƣ�Identical Three Crows ����̥��ѻ
        #     ��飺����K��ģʽ�����������У����ն�Ϊ���ߣ����ȴ�����ȣ� ÿ�տ��̼۵���ǰһ�����̼ۣ����̼۽ӽ�������ͼۣ�Ԥʾ�۸��µ���
        #     '''
        #     modec = talib.CDLIDENTICAL3CROWS(rates_frame.open.values, rates_frame.high.values, rates_frame.low.values,
        #                                      rates_frame.close.values)
        #     if modec[9] == 100 or modec[9] == -100:
        #         if modec[9] == 100 and (macd_trend == 'BUY_TRAND_H1' or macd_trend == 'BUY_TRAND_H4' or macd_trend =='BUY_TRAND_D'):
        #             order_Type = '��'
        #             moderedme = ' MACD����[��ͷ]���Ƶ���,��ǰK����̬Ϊ['
        #         elif modec[9] == -100 and (macd_trend == 'SELL_TRAND_H1' or macd_trend == 'SELL_TRAND_H4' or macd_trend == 'SELL_TRAND_D') :
        #             order_Type = '����'
        #             moderedme = 'MACD����[��ͷ]���Ƶ��У���ǰK����̬Ϊ['
        #         try:
        #             contents.append(
        #                 '<p><strong>���Ҷң�[' + symbol + ']' + moderedme + order_Type + ']����̥��ѻģʽ</strong></p>����K'
        #                                                                              '��ģʽ�����������У����ն�Ϊ���ߣ����ȴ�����ȣ� '
        #                                                                              'ÿ�տ��̼۵���ǰһ�����̼ۣ����̼۽ӽ�������ͼۣ�Ԥʾ�۸��µ���')
        #             attrfile = generatebar.CandlesstickPng.GenerateBarPng(symbol, run_time)
        #             images.append(attrfile)
        #         except Exception as e:
        #             log.error('���ͻ��Ҷң�' + symbol + '�ʼ���Ϣʧ�ܣ� ��ǰģʽΪ������̥��ѻ' + str(e))
        #
        #     '''
        #     ��������CDLINNECK
        #     ���ƣ�In-Neck Pattern ������
        #     ��飺����K��ģʽ���µ������У���һ�ճ����ߣ� �ڶ��տ��̼۽ϵͣ����̼��Ը��ڵ�һ�����̼ۣ����ߣ�ʵ��϶̣�Ԥʾ���µ�����
        #     '''
        #     modec = talib.CDLINNECK(rates_frame.open.values, rates_frame.high.values, rates_frame.low.values,
        #                             rates_frame.close.values)
        #     if modec[9] == 100 or modec[9] == -100:
        #         if modec[9] == 100 and (macd_trend == 'BUY_TRAND_H1' or macd_trend == 'BUY_TRAND_H4' or macd_trend =='BUY_TRAND_D'):
        #             order_Type = '��'
        #             moderedme = ' MACD����[��ͷ]���Ƶ���,��ǰK����̬Ϊ['
        #         elif modec[9] == -100 and (macd_trend == 'SELL_TRAND_H1' or macd_trend == 'SELL_TRAND_H4' or macd_trend == 'SELL_TRAND_D') :
        #             order_Type = '����'
        #             moderedme = 'MACD����[��ͷ]���Ƶ��У���ǰK����̬Ϊ['
        #         try:
        #             contents.append(
        #                 '<p><strong>���Ҷң�[' + symbol + ']' + moderedme + order_Type + ']����K��ģʽ</strong></p>�µ������У���һ�ճ����ߣ� �ڶ��տ��̼۽ϵͣ����̼��Ը��ڵ�һ�����̼ۣ����ߣ�ʵ��϶̣�Ԥʾ���µ�����.')
        #             attrfile = generatebar.CandlesstickPng.GenerateBarPng(symbol, run_time)
        #             images.append(attrfile)
        #         except Exception as e:
        #             log.error('���ͻ��Ҷң�' + symbol + '�ʼ���Ϣʧ�ܣ� ��ǰģʽΪ��������' + str(e))
        #
        #     '''
        #     ��������CDLINVERTEDHAMMER
        #     ���ƣ�Inverted Hammer ����ͷ
        #     ��飺һ��K��ģʽ����Ӱ�߽ϳ�������Ϊʵ��2�����ϣ� ����Ӱ�ߣ����µ����Ƶײ���Ԥʾ�����Ʒ�ת��
        #     '''
        #     modec = talib.CDLINVERTEDHAMMER(rates_frame.open.values, rates_frame.high.values, rates_frame.low.values,
        #                                     rates_frame.close.values)
        #     if modec[9] == 100 or modec[9] == -100:
        #         if modec[9] == 100 and (macd_trend == 'BUY_TRAND_H1' or macd_trend == 'BUY_TRAND_H4' or macd_trend =='BUY_TRAND_D'):
        #             order_Type = '��'
        #             moderedme = ' MACD����[��ͷ]���Ƶ���,��ǰK����̬Ϊ['
        #         elif modec[9] == -100 and (macd_trend == 'SELL_TRAND_H1' or macd_trend == 'SELL_TRAND_H4' or macd_trend == 'SELL_TRAND_D') :
        #             order_Type = '����'
        #             moderedme = 'MACD����[��ͷ]���Ƶ��У���ǰK����̬Ϊ['
        #         try:
        #             contents.append(
        #                 '<p><strong>���Ҷң�[' + symbol + ']' + moderedme + order_Type + ']����ͷģʽ</strong></p>һ��K��ģʽ����Ӱ�߽ϳ�������Ϊʵ��2�����ϣ� ����Ӱ�ߣ����µ����Ƶײ���Ԥʾ�����Ʒ�ת��')
        #             attrfile = generatebar.CandlesstickPng.GenerateBarPng(symbol, run_time)
        #             images.append(attrfile)
        #         except Exception as e:
        #             log.error('���ͻ��Ҷң�' + symbol + '�ʼ���Ϣʧ�ܣ� ��ǰģʽΪ������ͷ' + str(e))
        #
        #     '''
        #     ��������CDLKICKING
        #     ���ƣ�Kicking ������̬
        #     ��飺����K��ģʽ������������ƣ�����K��Ϊͺ�ߣ���ɫ�෴����������ȱ�ڡ�
        #     '''
        #     modec = talib.CDLKICKING(rates_frame.open.values, rates_frame.high.values, rates_frame.low.values,
        #                              rates_frame.close.values)
        #     if modec[9] == 100 or modec[9] == -100:
        #         if modec[9] == 100 and (macd_trend == 'BUY_TRAND_H1' or macd_trend == 'BUY_TRAND_H4' or macd_trend =='BUY_TRAND_D'):
        #             order_Type = '��'
        #             moderedme = ' MACD����[��ͷ]���Ƶ���,��ǰK����̬Ϊ['
        #         elif modec[9] == -100 and (macd_trend == 'SELL_TRAND_H1' or macd_trend == 'SELL_TRAND_H4' or macd_trend == 'SELL_TRAND_D') :
        #             order_Type = '����'
        #             moderedme = 'MACD����[��ͷ]���Ƶ��У���ǰK����̬Ϊ['
        #         try:
        #             contents.append(
        #                 '<p><strong>���Ҷң�[' + symbol + ']' + moderedme + order_Type + ']������̬ģʽ</strong></p>����K��ģʽ������������ƣ�����K��Ϊͺ�ߣ���ɫ�෴����������ȱ�ڡ�')
        #             attrfile = generatebar.CandlesstickPng.GenerateBarPng(symbol, run_time)
        #             images.append(attrfile)
        #         except Exception as e:
        #             log.error('���ͻ��Ҷң�' + symbol + '�ʼ���Ϣʧ�ܣ� ��ǰģʽΪ��������̬' + str(e))
        #
        #     '''
        #     ��������CDLKICKINGBYLENGTH
        #     ���ƣ�Kicking - bull/bear determined by the longer marubozu �ɽϳ�ȱӰ�߾����ķ�����̬
        #     ��飺����K��ģʽ���뷴����̬���ƣ��ϳ�ȱӰ�߾����۸���ǵ�
        #     '''
        #     modec = talib.CDLKICKINGBYLENGTH(rates_frame.open.values, rates_frame.high.values, rates_frame.low.values,
        #                                      rates_frame.close.values)
        #     if modec[9] == 100 or modec[9] == -100:
        #         if modec[9] == 100 and (macd_trend == 'BUY_TRAND_H1' or macd_trend == 'BUY_TRAND_H4' or macd_trend =='BUY_TRAND_D'):
        #             order_Type = '��'
        #             moderedme = ' MACD����[��ͷ]���Ƶ���,��ǰK����̬Ϊ['
        #         elif modec[9] == -100 and (macd_trend == 'SELL_TRAND_H1' or macd_trend == 'SELL_TRAND_H4' or macd_trend == 'SELL_TRAND_D') :
        #             order_Type = '����'
        #             moderedme = 'MACD����[��ͷ]���Ƶ��У���ǰK����̬Ϊ['
        #         try:
        #             contents.append(
        #                 '<p><strong>���Ҷң�[' + symbol + ']' + moderedme + order_Type + ']�ϳ�ȱӰ�߾����ķ�����̬ģʽ</strong></p>����K��ģʽ���뷴����̬���ƣ��ϳ�ȱӰ�߾����۸���ǵ���')
        #             attrfile = generatebar.CandlesstickPng.GenerateBarPng(symbol, run_time)
        #             images.append(attrfile)
        #         except Exception as e:
        #             log.error('���ͻ��Ҷң�' + symbol + '�ʼ���Ϣ�ɹ��� ��ǰģʧ�ܣ��ɽϳ�ȱӰ�߾����ķ�����̬' + str(e))
        #
        #     '''
        #     ��������CDLLADDERBOTTOM
        #     ���ƣ�Ladder Bottom �ݵ�
        #     ��飺����K��ģʽ���µ������У�ǰ�������ߣ� ���̼������̼۽Ե���ǰһ�տ��̡����̼ۣ������յ���ͷ�������տ��̼۸���ǰһ�տ��̼ۣ� ���ߣ����̼۸���ǰ���ռ۸������Ԥʾ�ŵײ���ת��
        #     '''
        #     modec = talib.CDLLADDERBOTTOM(rates_frame.open.values, rates_frame.high.values, rates_frame.low.values,
        #                                   rates_frame.close.values)
        #     if modec[9] == 100 or modec[9] == -100:
        #         if modec[9] == 100 and (macd_trend == 'BUY_TRAND_H1' or macd_trend == 'BUY_TRAND_H4' or macd_trend =='BUY_TRAND_D'):
        #             order_Type = '��'
        #             moderedme = ' MACD����[��ͷ]���Ƶ���,��ǰK����̬Ϊ['
        #         elif modec[9] == -100 and (macd_trend == 'SELL_TRAND_H1' or macd_trend == 'SELL_TRAND_H4' or macd_trend == 'SELL_TRAND_D') :
        #             order_Type = '����'
        #             moderedme = 'MACD����[��ͷ]���Ƶ��У���ǰK����̬Ϊ['
        #         try:
        #             contents.append(
        #                 '<p><strong>���Ҷң�[' + symbol + ']' + moderedme + order_Type + ']�ݵ�ģʽ</strong></p>����K��ģʽ���µ������У�ǰ�������ߣ� ���̼������̼۽Ե���ǰһ�տ��̡����̼ۣ������յ���ͷ�������տ��̼۸���ǰһ�տ��̼ۣ� ���ߣ����̼۸���ǰ���ռ۸������Ԥʾ�ŵײ���ת��')
        #             attrfile = generatebar.CandlesstickPng.GenerateBarPng(symbol, run_time)
        #             images.append(attrfile)
        #         except Exception as e:
        #             log.error('���ͻ��Ҷң�' + symbol + '�ʼ���Ϣʧ�ܣ� ��ǰģʽΪ���ݵ�' + str(e))
        #
        #     '''
        #     ��������CDLLONGLEGGEDDOJI
        #     ���ƣ�Long Legged Doji ����ʮ��
        #     ��飺һ��K��ģʽ�����̼������̼���ͬ�ӵ��ռ۸��в�������Ӱ�߳��� ����г���ȷ���ԡ�
        #     '''
        #     modec = talib.CDLLONGLEGGEDDOJI(rates_frame.open.values, rates_frame.high.values, rates_frame.low.values,
        #                                     rates_frame.close.values)
        #     if modec[9] == 100 or modec[9] == -100:
        #         if modec[9] == 100 and (macd_trend == 'BUY_TRAND_H1' or macd_trend == 'BUY_TRAND_H4' or macd_trend =='BUY_TRAND_D'):
        #             order_Type = '��'
        #             moderedme = ' MACD����[��ͷ]���Ƶ���,��ǰK����̬Ϊ['
        #         elif modec[9] == -100 and (macd_trend == 'SELL_TRAND_H1' or macd_trend == 'SELL_TRAND_H4' or macd_trend == 'SELL_TRAND_D') :
        #             order_Type = '����'
        #             moderedme = 'MACD����[��ͷ]���Ƶ��У���ǰK����̬Ϊ['
        #         try:
        #             contents.append(
        #                 '<p><strong>���Ҷң�[' + symbol + ']' + moderedme + order_Type + ']����ʮ��ģʽ</strong></p> һ��K��ģʽ�����̼������̼���ͬ�ӵ��ռ۸��в�������Ӱ�߳��� ����г���ȷ���ԡ�')
        #             attrfile = generatebar.CandlesstickPng.GenerateBarPng(symbol, run_time)
        #             images.append(attrfile)
        #         except Exception as e:
        #             log.error('���ͻ��Ҷң�' + symbol + '�ʼ���Ϣʧ�ܣ� ��ǰģʽΪ������ʮ��' + str(e))
        #
        #     '''
        #     ��������CDLLONGLINE
        #     ���ƣ�Long Line Candle ������
        #     ��飺һ��K��ģʽ��K��ʵ�峤��������Ӱ�ߡ�
        #     '''
        #     modec = talib.CDLLONGLINE(rates_frame.open.values, rates_frame.high.values, rates_frame.low.values,
        #                               rates_frame.close.values)
        #     if modec[9] == 100 or modec[9] == -100:
        #         if modec[9] == 100 and (macd_trend == 'BUY_TRAND_H1' or macd_trend == 'BUY_TRAND_H4' or macd_trend =='BUY_TRAND_D'):
        #             order_Type = '��'
        #             moderedme = ' MACD����[��ͷ]���Ƶ���,��ǰK����̬Ϊ['
        #         elif modec[9] == -100 and (macd_trend == 'SELL_TRAND_H1' or macd_trend == 'SELL_TRAND_H4' or macd_trend == 'SELL_TRAND_D') :
        #             order_Type = '����'
        #             moderedme = 'MACD����[��ͷ]���Ƶ��У���ǰK����̬Ϊ['
        #         try:
        #             contents.append(
        #                 '<p><strong>���Ҷң�[' + symbol + ']' + moderedme + order_Type + ']������ģʽ</strong></p>һ��K��ģʽ��K��ʵ�峤��������Ӱ�ߡ�')
        #             attrfile = generatebar.CandlesstickPng.GenerateBarPng(symbol, run_time)
        #             images.append(attrfile)
        #         except Exception as e:
        #             log.error('���ͻ��Ҷң�' + symbol + '�ʼ���Ϣʧ�ܣ� ��ǰģʽΪ��������' + str(e))
        #
        #     '''
        #     ��������CDLMARUBOZU
        #     ���ƣ�Marubozu ��ͷ���/ȱӰ��
        #     ��飺һ��K��ģʽ��������ͷ��û��Ӱ�ߵ�ʵ�壬 ����Ԥʾ�����г�������ţ�з�ת�������෴��
        #     '''
        #     modec = talib.CDLMARUBOZU(rates_frame.open.values, rates_frame.high.values, rates_frame.low.values,
        #                               rates_frame.close.values)
        #     if modec[9] == 100 or modec[9] == -100:
        #         if modec[9] == 100 and (macd_trend == 'BUY_TRAND_H1' or macd_trend == 'BUY_TRAND_H4' or macd_trend =='BUY_TRAND_D'):
        #             order_Type = '��'
        #             moderedme = ' MACD����[��ͷ]���Ƶ���,��ǰK����̬Ϊ['
        #         elif modec[9] == -100 and (macd_trend == 'SELL_TRAND_H1' or macd_trend == 'SELL_TRAND_H4' or macd_trend == 'SELL_TRAND_D') :
        #             order_Type = '����'
        #             moderedme = 'MACD����[��ͷ]���Ƶ��У���ǰK����̬Ϊ['
        #         try:
        #             contents.append(
        #                 '<p><strong>���Ҷң�[' + symbol + ']' + moderedme + order_Type + ']��ͷ���/ȱӰ��ģʽ</strong></p> һ��K��ģʽ��������ͷ��û��Ӱ�ߵ�ʵ�壬 ����Ԥʾ�����г�������ţ�з�ת�������෴��')
        #             attrfile = generatebar.CandlesstickPng.GenerateBarPng(symbol, run_time)
        #             images.append(attrfile)
        #         except Exception as e:
        #             log.error('���ͻ��Ҷң�' + symbol + '�ʼ���Ϣʧ�ܣ� ��ǰģʽΪ����ͷ���/ȱӰ��' + str(e))
        #
        #     '''
        #     ��������CDLMATCHINGLOW
        #     ���ƣ�Matching Low ��ͬ�ͼ�
        #     ��飺����K��ģʽ���µ������У���һ�ճ����ߣ� �ڶ������ߣ����̼���ǰһ����ͬ��Ԥʾ�ײ�ȷ�ϣ��ü۸�Ϊ֧��λ��
        #     '''
        #     modec = talib.CDLMATCHINGLOW(rates_frame.open.values, rates_frame.high.values, rates_frame.low.values,
        #                                  rates_frame.close.values)
        #     if modec[9] == 100 or modec[9] == -100:
        #         if modec[9] == 100 and (macd_trend == 'BUY_TRAND_H1' or macd_trend == 'BUY_TRAND_H4' or macd_trend =='BUY_TRAND_D'):
        #             order_Type = '��'
        #             moderedme = ' MACD����[��ͷ]���Ƶ���,��ǰK����̬Ϊ['
        #         elif modec[9] == -100 and (macd_trend == 'SELL_TRAND_H1' or macd_trend == 'SELL_TRAND_H4' or macd_trend == 'SELL_TRAND_D') :
        #             order_Type = '����'
        #             moderedme = 'MACD����[��ͷ]���Ƶ��У���ǰK����̬Ϊ['
        #         try:
        #             contents.append(
        #                 '<p><strong>���Ҷң�[' + symbol + ']' + moderedme + order_Type + ']��ͬ�ͼ�ģʽ</strong></p> ����K��ģʽ�µ������У���һ�ճ����ߣ� �ڶ������ߣ����̼���ǰһ����ͬ��Ԥʾ�ײ�ȷ�ϣ��ü۸�Ϊ֧��λ��')
        #             attrfile = generatebar.CandlesstickPng.GenerateBarPng(symbol, run_time)
        #             images.append(attrfile)
        #         except Exception as e:
        #             log.error('���ͻ��Ҷң�' + symbol + '�ʼ���Ϣʧ�ܣ� ��ǰģʽΪ����ͬ�ͼ�' + str(e))
        #
        #     '''
        #     ��������CDLMATHOLD
        #     ���ƣ�Mat Hold �̵�
        #     ��飺����K��ģʽ�����������У���һ�����ߣ��ڶ������ո߿�Ӱ�ߣ� ���������ն�ʵ��Ӱ�ߣ����������ߣ����̼۸���ǰ���գ�Ԥʾ���Ƴ�����
        #     '''
        #     modec = talib.CDLMATHOLD(rates_frame.open.values, rates_frame.high.values, rates_frame.low.values,
        #                              rates_frame.close.values, penetration=0)
        #     if modec[9] == 100 or modec[9] == -100:
        #         if modec[9] == 100 and (macd_trend == 'BUY_TRAND_H1' or macd_trend == 'BUY_TRAND_H4' or macd_trend =='BUY_TRAND_D'):
        #             order_Type = '��'
        #             moderedme = ' MACD����[��ͷ]���Ƶ���,��ǰK����̬Ϊ['
        #         elif modec[9] == -100 and (macd_trend == 'SELL_TRAND_H1' or macd_trend == 'SELL_TRAND_H4' or macd_trend == 'SELL_TRAND_D') :
        #             order_Type = '����'
        #             moderedme = 'MACD����[��ͷ]���Ƶ��У���ǰK����̬Ϊ['
        #         try:
        #             contents.append(
        #                 '<p><strong>���Ҷң�[' + symbol + ']' + moderedme + order_Type + ']�̵�ģʽ</p></strong>����K��ģʽ�����������У���һ�����ߣ��ڶ������ո߿�Ӱ�ߣ� ���������ն�ʵ��Ӱ�ߣ����������ߣ����̼۸���ǰ���գ�Ԥʾ���Ƴ�����')
        #             attrfile = generatebar.CandlesstickPng.GenerateBarPng(symbol, run_time)
        #             images.append(attrfile)
        #         except Exception as e:
        #             log.error('���ͻ��Ҷң�' + symbol + '�ʼ���Ϣʧ�ܣ� ��ǰģʽΪ���̵�' + str(e))
        #
        #     '''
        #     ��������CDLMORNINGDOJISTAR
        #     ���ƣ�Morning Doji Star ʮ�ֳ���
        #     ��飺����K��ģʽ�� ����ģʽΪ���ǣ��ڶ���K��Ϊʮ���ǣ�Ԥʾ�ײ���ת��
        #     '''
        #     modec = talib.CDLMORNINGDOJISTAR(rates_frame.open.values, rates_frame.high.values, rates_frame.low.values,
        #                                      rates_frame.close.values, penetration=0)
        #     if modec[9] == 100 or modec[9] == -100:
        #         if modec[9] == 100 and (macd_trend == 'BUY_TRAND_H1' or macd_trend == 'BUY_TRAND_H4' or macd_trend =='BUY_TRAND_D'):
        #             order_Type = '��'
        #             moderedme = ' MACD����[��ͷ]���Ƶ���,��ǰK����̬Ϊ['
        #         elif modec[9] == -100 and (macd_trend == 'SELL_TRAND_H1' or macd_trend == 'SELL_TRAND_H4' or macd_trend == 'SELL_TRAND_D') :
        #             order_Type = '����'
        #             moderedme = 'MACD����[��ͷ]���Ƶ��У���ǰK����̬Ϊ['
        #         try:
        #             contents.append(
        #                 '<p><strong>���Ҷң�[' + symbol + ']' + moderedme + order_Type + ']ʮ�ֳ���ģʽ</strong></p>����K��ģʽ�� ����ģʽΪ���ǣ��ڶ���K��Ϊʮ���ǣ�Ԥʾ�ײ���ת��')
        #             attrfile = generatebar.CandlesstickPng.GenerateBarPng(symbol, run_time)
        #             images.append(attrfile)
        #         except Exception as e:
        #             log.error('���ͻ��Ҷң�' + symbol + '�ʼ���Ϣʧ�ܣ� ��ǰģʽΪ��ʮ�ֳ���' + str(e))
        #
        #     '''
        #     ��������CDLMORNINGSTAR
        #     ���ƣ�Morning Star ����
        #     ��飺����K��ģʽ���µ����ƣ���һ�����ߣ� �ڶ��ռ۸������С�����������ߣ�Ԥʾ�ײ���ת��
        #     '''
        #     modec = talib.CDLMORNINGSTAR(rates_frame.open.values, rates_frame.high.values, rates_frame.low.values,
        #                                  rates_frame.close.values, penetration=0)
        #     if modec[9] == 100 or modec[9] == -100:
        #         if modec[9] == 100 and (macd_trend == 'BUY_TRAND_H1' or macd_trend == 'BUY_TRAND_H4' or macd_trend =='BUY_TRAND_D'):
        #             order_Type = '��'
        #             moderedme = ' MACD����[��ͷ]���Ƶ���,��ǰK����̬Ϊ['
        #         elif modec[9] == -100 and (macd_trend == 'SELL_TRAND_H1' or macd_trend == 'SELL_TRAND_H4' or macd_trend == 'SELL_TRAND_D') :
        #             order_Type = '����'
        #             moderedme = 'MACD����[��ͷ]���Ƶ��У���ǰK����̬Ϊ['
        #         try:
        #             contents.append(
        #                 '<p><strong>���Ҷң�[' + symbol + ']' + moderedme + order_Type + ']����ģʽ</strong></p>����K��ģʽ�� ����ģʽΪ���ǣ��ڶ���K��Ϊʮ���ǣ�Ԥʾ�ײ���ת��')
        #             attrfile = generatebar.CandlesstickPng.GenerateBarPng(symbol, run_time)
        #             images.append(attrfile)
        #         except Exception as e:
        #             log.error('���ͻ��Ҷң�' + symbol + '�ʼ���Ϣʧ�ܣ� ��ǰģʽΪ������' + str(e))
        #
        #     '''
        #     ��������CDLONNECK
        #     ���ƣ�On-Neck Pattern ������
        #     ��飺����K��ģʽ���µ������У���һ�ճ����ߣ��ڶ��տ��̼۽ϵͣ� ���̼���ǰһ����ͼ���ͬ�����ߣ�ʵ��϶̣�Ԥʾ�������µ����ơ�
        #     '''
        #     modec = talib.CDLONNECK(rates_frame.open.values, rates_frame.high.values, rates_frame.low.values,
        #                             rates_frame.close.values)
        #     if modec[9] == 100 or modec[9] == -100:
        #         if modec[9] == 100 and (macd_trend == 'BUY_TRAND_H1' or macd_trend == 'BUY_TRAND_H4' or macd_trend =='BUY_TRAND_D'):
        #             order_Type = '��'
        #             moderedme = ' MACD����[��ͷ]���Ƶ���,��ǰK����̬Ϊ['
        #         elif modec[9] == -100 and (macd_trend == 'SELL_TRAND_H1' or macd_trend == 'SELL_TRAND_H4' or macd_trend == 'SELL_TRAND_D') :
        #             order_Type = '����'
        #             moderedme = 'MACD����[��ͷ]���Ƶ��У���ǰK����̬Ϊ['
        #         try:
        #             contents.append(
        #                 '<p><strong>���Ҷң�[' + symbol + ']' + moderedme + order_Type + ']������ģʽ</strong><p>����K��ģʽ���µ������У���һ�ճ����ߣ��ڶ��տ��̼۽ϵͣ� ���̼���ǰһ����ͼ���ͬ�����ߣ�ʵ��϶̣�Ԥʾ�������µ����ơ�')
        #             attrfile = generatebar.CandlesstickPng.GenerateBarPng(symbol, run_time)
        #             images.append(attrfile)
        #         except Exception as e:
        #             log.error('���ͻ��Ҷң�' + symbol + '�ʼ���Ϣʧ�ܣ� ��ǰģʽΪ��������' + str(e))
        #
        #     '''
        #     ��������CDLPIERCING
        #     ���ƣ�Piercing Pattern ��͸��̬
        #     ��飺����K��ģʽ���µ������У���һ�����ߣ��ڶ������̼۵���ǰһ����ͼۣ� ���̼۴��ڵ�һ��ʵ���ϲ���Ԥʾ�ŵײ���ת��
        #     '''
        #     modec = talib.CDLPIERCING(rates_frame.open.values, rates_frame.high.values, rates_frame.low.values,
        #                               rates_frame.close.values)
        #     if modec[9] == 100 or modec[9] == -100:
        #         if modec[9] == 100 and (macd_trend == 'BUY_TRAND_H1' or macd_trend == 'BUY_TRAND_H4' or macd_trend =='BUY_TRAND_D'):
        #             order_Type = '��'
        #             moderedme = ' MACD����[��ͷ]���Ƶ���,��ǰK����̬Ϊ['
        #         elif modec[9] == -100 and (macd_trend == 'SELL_TRAND_H1' or macd_trend == 'SELL_TRAND_H4' or macd_trend == 'SELL_TRAND_D') :
        #             order_Type = '����'
        #             moderedme = 'MACD����[��ͷ]���Ƶ��У���ǰK����̬Ϊ['
        #         try:
        #             contents.append(
        #                 '<p><strong>���Ҷң�[' + symbol + ']' + moderedme + order_Type + ']��͸��̬ģʽ</strong></p>����K��ģʽ���µ������У���һ�����ߣ��ڶ������̼۵���ǰһ����ͼۣ� ���̼۴��ڵ�һ��ʵ���ϲ���Ԥʾ�ŵײ���ת��')
        #             attrfile = generatebar.CandlesstickPng.GenerateBarPng(symbol, run_time)
        #             images.append(attrfile)
        #         except Exception as e:
        #             log.error('���ͻ��Ҷң�' + symbol + '�ʼ���Ϣʧ�ܣ� ��ǰģʽΪ����͸��̬' + str(e))
        #
        #     '''
        #     ��������CDLRICKSHAWMAN
        #     ���ƣ�Rickshaw Man �ư�����
        #     ��飺һ��K��ģʽ���볤��ʮ�������ƣ� ��ʵ�����ô��ڼ۸�����е㣬��Ϊ�ư�����
        #     '''
        #     modec = talib.CDLRICKSHAWMAN(rates_frame.open.values, rates_frame.high.values, rates_frame.low.values,
        #                                  rates_frame.close.values)
        #     if modec[9] == 100 or modec[9] == -100:
        #         if modec[9] == 100 and (macd_trend == 'BUY_TRAND_H1' or macd_trend == 'BUY_TRAND_H4' or macd_trend =='BUY_TRAND_D'):
        #             order_Type = '��'
        #             moderedme = ' MACD����[��ͷ]���Ƶ���,��ǰK����̬Ϊ['
        #         elif modec[9] == -100 and (macd_trend == 'SELL_TRAND_H1' or macd_trend == 'SELL_TRAND_H4' or macd_trend == 'SELL_TRAND_D') :
        #             order_Type = '����'
        #             moderedme = 'MACD����[��ͷ]���Ƶ��У���ǰK����̬Ϊ['
        #         try:
        #             contents.append(
        #                 '<p><strong>���Ҷң�[' + symbol + ']' + moderedme + order_Type + ']�ư�����ģʽ</strong></p>һ��K��ģʽ���볤��ʮ�������ƣ� ��ʵ�����ô��ڼ۸�����е㣬��Ϊ�ư�����')
        #             attrfile = generatebar.CandlesstickPng.GenerateBarPng(symbol, run_time)
        #             images.append(attrfile)
        #         except Exception as e:
        #             log.error('���ͻ��Ҷң�' + symbol + '�ʼ���Ϣʧ�ܣ� ��ǰģʽΪ���ư�����' + str(e))
        #
        #     '''
        #     ��������CDLRISEFALL3METHODS ���ƣ�Rising/Falling Three Methods ����/�½�����
        #     ��飺 ����K��ģʽ������������Ϊ�������������У� ��һ�ճ����ߣ��м����ռ۸��ڵ�һ�շ�Χ��С���𵴣� �����ճ����ߣ����̼۸��ڵ�һ�����̼ۣ�Ԥʾ�ɼ�������
        #     '''
        #     modec = talib.CDLRISEFALL3METHODS(rates_frame.open.values, rates_frame.high.values, rates_frame.low.values,
        #                                       rates_frame.close.values)
        #     if modec[9] == 100 or modec[9] == -100:
        #         if modec[9] == 100 and (macd_trend == 'BUY_TRAND_H1' or macd_trend == 'BUY_TRAND_H4' or macd_trend =='BUY_TRAND_D'):
        #             order_Type = '��'
        #             moderedme = ' MACD����[��ͷ]���Ƶ���,��ǰK����̬Ϊ['
        #         elif modec[9] == -100 and (macd_trend == 'SELL_TRAND_H1' or macd_trend == 'SELL_TRAND_H4' or macd_trend == 'SELL_TRAND_D') :
        #             order_Type = '����'
        #             moderedme = 'MACD����[��ͷ]���Ƶ��У���ǰK����̬Ϊ['
        #         try:
        #             contents.append(
        #                 '<p><strong>���Ҷң�[' + symbol + ']' + moderedme + order_Type + ']����/�½�����ģʽ</strong></p>����K��ģʽ������������Ϊ�������������У� ��һ�ճ����ߣ��м����ռ۸��ڵ�һ�շ�Χ��С���𵴣� �����ճ����ߣ����̼۸��ڵ�һ�����̼ۣ�Ԥʾ�ɼ�������')
        #             attrfile = generatebar.CandlesstickPng.GenerateBarPng(symbol, run_time)
        #             images.append(attrfile)
        #         except Exception as e:
        #             log.error('���ͻ��Ҷң�' + symbol + '�ʼ���Ϣʧ�ܣ� ��ǰģʽΪ������/�½�����' + str(e))
        #
        #     '''
        #     ��������CDLSEPARATINGLINES
        #     ���ƣ�Separating Lines ������
        #     ��飺����K��ģʽ�����������У���һ�����ߣ��ڶ������ߣ� �ڶ��տ��̼����һ����ͬ��Ϊ��ͼۣ�Ԥʾ�����Ƽ�����
        #     '''
        #     modec = talib.CDLSEPARATINGLINES(rates_frame.open.values, rates_frame.high.values, rates_frame.low.values,
        #                                      rates_frame.close.values)
        #     if modec[9] == 100 or modec[9] == -100:
        #         if modec[9] == 100 and (macd_trend == 'BUY_TRAND_H1' or macd_trend == 'BUY_TRAND_H4' or macd_trend =='BUY_TRAND_D'):
        #             order_Type = '��'
        #             moderedme = ' MACD����[��ͷ]���Ƶ���,��ǰK����̬Ϊ['
        #         elif modec[9] == -100 and (macd_trend == 'SELL_TRAND_H1' or macd_trend == 'SELL_TRAND_H4' or macd_trend == 'SELL_TRAND_D') :
        #             order_Type = '����'
        #             moderedme = 'MACD����[��ͷ]���Ƶ��У���ǰK����̬Ϊ['
        #         try:
        #             contents.append(
        #                 '<p><strong>���Ҷң�[' + symbol + ']' + moderedme + order_Type + ']������ģʽ</strong></p>����K��ģʽ�����������У���һ�����ߣ��ڶ������ߣ� �ڶ��տ��̼����һ����ͬ��Ϊ��ͼۣ�Ԥʾ�����Ƽ�����')
        #             attrfile = generatebar.CandlesstickPng.GenerateBarPng(symbol, run_time)
        #             images.append(attrfile)
        #         except Exception as e:
        #             log.error('���ͻ��Ҷң�' + symbol + '�ʼ���Ϣʧ�ܣ� ��ǰģʽΪ��������' + str(e))
        #
        #     '''
        #     ��������CDLSHOOTINGSTAR
        #     ���ƣ�Shooting Star ���֮��
        #     ��飺һ��K��ģʽ����Ӱ������Ϊʵ�峤�������� û����Ӱ�ߣ�Ԥʾ�Źɼ��µ�
        #     '''
        #     modec = talib.CDLSHOOTINGSTAR(rates_frame.open.values, rates_frame.high.values, rates_frame.low.values,
        #                                   rates_frame.close.values)
        #     if modec[9] == 100 or modec[9] == -100:
        #         if modec[9] == 100 and (macd_trend == 'BUY_TRAND_H1' or macd_trend == 'BUY_TRAND_H4' or macd_trend =='BUY_TRAND_D'):
        #             order_Type = '��'
        #             moderedme = ' MACD����[��ͷ]���Ƶ���,��ǰK����̬Ϊ['
        #         elif modec[9] == -100 and (macd_trend == 'SELL_TRAND_H1' or macd_trend == 'SELL_TRAND_H4' or macd_trend == 'SELL_TRAND_D') :
        #             order_Type = '����'
        #             moderedme = 'MACD����[��ͷ]���Ƶ��У���ǰK����̬Ϊ['
        #         try:
        #             contents.append(
        #                 '<p><strong>���Ҷң�[' + symbol + ']' + moderedme + order_Type + ']���֮��</strong></p>һ��K��ģʽ����Ӱ������Ϊʵ�峤�������� û����Ӱ�ߣ�Ԥʾ�Źɼ��µ���')
        #             attrfile = generatebar.CandlesstickPng.GenerateBarPng(symbol, run_time)
        #             images.append(attrfile)
        #         except Exception as e:
        #             log.error('���ͻ��Ҷң�' + symbol + '�ʼ���Ϣʧ�ܣ� ��ǰģʽΪ�����֮��' + str(e))
        #
        #     '''
        #     ��������CDLSHORTLINE
        #     ���ƣ�Short Line Candle ������
        #     ��飺һ��K��ģʽ��ʵ��̣�������Ӱ��
        #     '''
        #     modec = talib.CDLSHORTLINE(rates_frame.open.values, rates_frame.high.values, rates_frame.low.values,
        #                                rates_frame.close.values)
        #     if modec[9] == 100 or modec[9] == -100:
        #         if modec[9] == 100 and (macd_trend == 'BUY_TRAND_H1' or macd_trend == 'BUY_TRAND_H4' or macd_trend =='BUY_TRAND_D'):
        #             order_Type = '��'
        #             moderedme = ' MACD����[��ͷ]���Ƶ���,��ǰK����̬Ϊ['
        #         elif modec[9] == -100 and (macd_trend == 'SELL_TRAND_H1' or macd_trend == 'SELL_TRAND_H4' or macd_trend == 'SELL_TRAND_D') :
        #             order_Type = '����'
        #             moderedme = 'MACD����[��ͷ]���Ƶ��У���ǰK����̬Ϊ['
        #         try:
        #             contents.append(
        #                 '<p><strong>���Ҷң�[' + symbol + ']' + moderedme + order_Type + ']������ģʽ</strong></p>һ��K��ģʽ��ʵ��̣�������Ӱ�ߡ�')
        #             attrfile = generatebar.CandlesstickPng.GenerateBarPng(symbol, run_time)
        #             images.append(attrfile)
        #         except Exception as e:
        #             log.error('���ͻ��Ҷң�' + symbol + '�ʼ���Ϣʧ�ܣ� ��ǰģʽΪ��������' + str(e))
        #
        #     '''
        #     ��������CDLSPINNINGTOP
        #     ���ƣ�Spinning Top �Ĵ�
        #     ��飺һ��K�ߣ�ʵ��С��
        #     '''
        #     modec = talib.CDLSPINNINGTOP(rates_frame.open.values, rates_frame.high.values, rates_frame.low.values,
        #                                  rates_frame.close.values)
        #     if modec[9] == 100 or modec[9] == -100:
        #         if modec[9] == 100 and (macd_trend == 'BUY_TRAND_H1' or macd_trend == 'BUY_TRAND_H4' or macd_trend =='BUY_TRAND_D'):
        #             order_Type = '��'
        #             moderedme = ' MACD����[��ͷ]���Ƶ���,��ǰK����̬Ϊ['
        #         elif modec[9] == -100 and (macd_trend == 'SELL_TRAND_H1' or macd_trend == 'SELL_TRAND_H4' or macd_trend == 'SELL_TRAND_D') :
        #             order_Type = '����'
        #             moderedme = 'MACD����[��ͷ]���Ƶ��У���ǰK����̬Ϊ['
        #         try:
        #             contents.append(
        #                 '<p><strong>���Ҷң�[' + symbol + ']' + moderedme + order_Type + ']�Ĵ�ģʽ</strong></p>һ��K�ߣ�ʵ��С��')
        #             attrfile = generatebar.CandlesstickPng.GenerateBarPng(symbol, run_time)
        #             images.append(attrfile)
        #         except Exception as e:
        #             log.error('���ͻ��Ҷң�' + symbol + '�ʼ���Ϣʧ�ܣ� ��ǰģʽΪ���Ĵ�' + str(e))
        #
        #     '''
        #     ��������CDLSTALLEDPATTERN
        #     ���ƣ�Stalled Pattern ͣ����̬
        #     ��飺����K��ģʽ�����������У��ڶ��ճ����ߣ� �����տ�����ǰһ�����̼۸����������ߣ�Ԥʾ�����ǽ���
        #     '''
        #     modec = talib.CDLSTALLEDPATTERN(rates_frame.open.values, rates_frame.high.values, rates_frame.low.values,
        #                                     rates_frame.close.values)
        #     if modec[9] == 100 or modec[9] == -100:
        #         if modec[9] == 100 and (macd_trend == 'BUY_TRAND_H1' or macd_trend == 'BUY_TRAND_H4' or macd_trend =='BUY_TRAND_D'):
        #             order_Type = '��'
        #             moderedme = ' MACD����[��ͷ]���Ƶ���,��ǰK����̬Ϊ['
        #         elif modec[9] == -100 and (macd_trend == 'SELL_TRAND_H1' or macd_trend == 'SELL_TRAND_H4' or macd_trend == 'SELL_TRAND_D') :
        #             order_Type = '����'
        #             moderedme = 'MACD����[��ͷ]���Ƶ��У���ǰK����̬Ϊ['
        #         try:
        #             contents.append(
        #                 '<p><strong>���Ҷң�[' + symbol + ']' + moderedme + order_Type + ']ͣ����̬ģʽ</strong></p>����K��ģʽ�����������У��ڶ��ճ����ߣ� �����տ�����ǰһ�����̼۸����������ߣ�Ԥʾ�����ǽ�����')
        #             attrfile = generatebar.CandlesstickPng.GenerateBarPng(symbol, run_time)
        #             images.append(attrfile)
        #         except Exception as e:
        #             log.error('���ͻ��Ҷң�' + symbol + '�ʼ���Ϣʧ�ܣ� ��ǰģʽΪ��ͣ����̬' + str(e))
        #
        #     '''
        #     ��������CDLSTICKSANDWICH
        #     ���ƣ�Stick Sandwich ����������
        #     ��飺����K��ģʽ����һ�ճ����ߣ��ڶ������ߣ����̼۸���ǰһ�����̼ۣ� �����տ��̼۸���ǰ������߼ۣ����̼��ڵ�һ�����̼���
        #     '''
        #     modec = talib.CDLSTICKSANDWICH(rates_frame.open.values, rates_frame.high.values, rates_frame.low.values,
        #                                    rates_frame.close.values)
        #     if modec[9] == 100 or modec[9] == -100:
        #         if modec[9] == 100 and (macd_trend == 'BUY_TRAND_H1' or macd_trend == 'BUY_TRAND_H4' or macd_trend =='BUY_TRAND_D'):
        #             order_Type = '��'
        #             moderedme = ' MACD����[��ͷ]���Ƶ���,��ǰK����̬Ϊ['
        #         elif modec[9] == -100 and (macd_trend == 'SELL_TRAND_H1' or macd_trend == 'SELL_TRAND_H4' or macd_trend == 'SELL_TRAND_D') :
        #             order_Type = '����'
        #             moderedme = 'MACD����[��ͷ]���Ƶ��У���ǰK����̬Ϊ['
        #         try:
        #             contents.append(
        #                 '<p><strong>���Ҷң�[' + symbol + ']' + moderedme + order_Type + ']����������ģʽ</strong></p>��K��ģʽ����һ�ճ����ߣ��ڶ������ߣ����̼۸���ǰһ�����̼ۣ� �����տ��̼۸���ǰ������߼ۣ����̼��ڵ�һ�����̼��ࡣ')
        #             attrfile = generatebar.CandlesstickPng.GenerateBarPng(symbol, run_time)
        #             images.append(attrfile)
        #         except Exception as e:
        #             # print("�����ʼ�ʧ��");
        #             log.error('���ͻ��Ҷң�' + symbol + '�ʼ���Ϣʧ�ܣ� ��ǰģʽΪ������������' + str(e))
        #
        #     '''
        #     ��������CDLTAKURI
        #     ���ƣ�Takuri (Dragonfly Doji with very long lower shadow) ̽ˮ��
        #     ��飺һ��K��ģʽ������������ʮ����ͬ����Ӱ�߳��ȳ���
        #     '''
        #     modec = talib.CDLTAKURI(rates_frame.open.values, rates_frame.high.values, rates_frame.low.values,
        #                             rates_frame.close.values)
        #     if modec[9] == 100 or modec[9] == -100:
        #         if modec[9] == 100 and (macd_trend == 'BUY_TRAND_H1' or macd_trend == 'BUY_TRAND_H4' or macd_trend =='BUY_TRAND_D'):
        #             order_Type = '��'
        #             moderedme = ' MACD����[��ͷ]���Ƶ���,��ǰK����̬Ϊ['
        #         elif modec[9] == -100 and (macd_trend == 'SELL_TRAND_H1' or macd_trend == 'SELL_TRAND_H4' or macd_trend == 'SELL_TRAND_D') :
        #             order_Type = '����'
        #             moderedme = 'MACD����[��ͷ]���Ƶ��У���ǰK����̬Ϊ['
        #         try:
        #             contents.append(
        #                 '<p><strong>���Ҷң�[' + symbol + ']' + moderedme + order_Type + ']̽ˮ��ģʽ</strong></p>һ��K��ģʽ������������ʮ����ͬ����Ӱ�߳��ȳ���')
        #             attrfile = generatebar.CandlesstickPng.GenerateBarPng(symbol, run_time)
        #             images.append(attrfile)
        #         except Exception as e:
        #             log.error('���ͻ��Ҷң�' + symbol + '�ʼ���Ϣʧ�ܣ� ��ǰģʽΪ��̽ˮ��' + str(e))
        #
        #     '''
        #     ��������CDLTASUKIGAP
        #     ���ƣ�Tasuki Gap ���ղ���������
        #     ��飺����K��ģʽ�������Ǻ��µ���������Ϊ���� ǰ�������ߣ��ڶ������գ����������ߣ����̼���ȱ���У��������Ƴ�����
        #     '''
        #     modec = talib.CDLTASUKIGAP(rates_frame.open.values, rates_frame.high.values, rates_frame.low.values,
        #                                rates_frame.close.values)
        #     if modec[9] == 100 or modec[9] == -100:
        #         if modec[9] == 100 and (macd_trend == 'BUY_TRAND_H1' or macd_trend == 'BUY_TRAND_H4' or macd_trend =='BUY_TRAND_D'):
        #             order_Type = '��'
        #             moderedme = ' MACD����[��ͷ]���Ƶ���,��ǰK����̬Ϊ['
        #         elif modec[9] == -100 and (macd_trend == 'SELL_TRAND_H1' or macd_trend == 'SELL_TRAND_H4' or macd_trend == 'SELL_TRAND_D') :
        #             order_Type = '����'
        #             moderedme = 'MACD����[��ͷ]���Ƶ��У���ǰK����̬Ϊ['
        #         try:
        #             contents.append(
        #                 '<p><strong>���Ҷң�[' + symbol + ']' + moderedme + order_Type + ']���ղ���������ģʽ</strong></p>����K��ģʽ�������Ǻ��µ���������Ϊ���� ǰ�������ߣ��ڶ������գ����������ߣ����̼���ȱ���У��������Ƴ�����')
        #             attrfile = generatebar.CandlesstickPng.GenerateBarPng(symbol, run_time)
        #             images.append(attrfile)
        #         except Exception as e:
        #             log.error('���ͻ��Ҷң�' + symbol + '�ʼ���Ϣʧ�ܣ� ��ǰģʽΪ�����ղ���������' + str(e))
        #
        #     '''
        #     ��������CDLTHRUSTING
        #     ���ƣ�Thrusting Pattern ����
        #     ��飺����K��ģʽ���뾱�������ƣ��µ������У���һ�ճ����ߣ��ڶ��տ��̼����գ� ���̼��Ե���ǰһ��ʵ���в����뾱�������ʵ��ϳ���Ԥʾ�����Ƴ�����
        #     '''
        #     modec = talib.CDLTHRUSTING(rates_frame.open.values, rates_frame.high.values, rates_frame.low.values,
        #                                rates_frame.close.values)
        #     if modec[9] == 100 or modec[9] == -100:
        #         if modec[9] == 100 and (macd_trend == 'BUY_TRAND_H1' or macd_trend == 'BUY_TRAND_H4' or macd_trend =='BUY_TRAND_D'):
        #             order_Type = '��'
        #             moderedme = ' MACD����[��ͷ]���Ƶ���,��ǰK����̬Ϊ['
        #         elif modec[9] == -100 and (macd_trend == 'SELL_TRAND_H1' or macd_trend == 'SELL_TRAND_H4' or macd_trend == 'SELL_TRAND_D') :
        #             order_Type = '����'
        #             moderedme = 'MACD����[��ͷ]���Ƶ��У���ǰK����̬Ϊ['
        #         try:
        #             contents.append(
        #                 '<p><strong>���Ҷң�[' + symbol + ']' + moderedme + order_Type + ']����ģʽ</strong></p>����K��ģʽ���뾱�������ƣ��µ������У���һ�ճ����ߣ��ڶ��տ��̼����գ� ���̼��Ե���ǰһ��ʵ���в����뾱�������ʵ��ϳ���Ԥʾ�����Ƴ�����')
        #             attrfile = generatebar.CandlesstickPng.GenerateBarPng(symbol, run_time)
        #             images.append(attrfile)
        #         except Exception as e:
        #             log.error('���ͻ��Ҷң�' + symbol + '�ʼ���Ϣʧ�ܣ� ��ǰģʽΪ������' + str(e))
        #
        #     '''
        #     ��������CDLTRISTAR
        #     ���ƣ�Tristar Pattern ����
        #     ��飺����K��ģʽ��������ʮ����ɣ� �ڶ���ʮ�ֱ�����ڻ��ߵ��ڵ�һ�պ͵����գ�Ԥʾ�ŷ�ת��
        #     '''
        #     modec = talib.CDLTRISTAR(rates_frame.open.values, rates_frame.high.values, rates_frame.low.values,
        #                              rates_frame.close.values)
        #     if modec[9] == 100 or modec[9] == -100:
        #         if modec[9] == 100 and (macd_trend == 'BUY_TRAND_H1' or macd_trend == 'BUY_TRAND_H4' or macd_trend =='BUY_TRAND_D'):
        #             order_Type = '��'
        #             moderedme = ' MACD����[��ͷ]���Ƶ���,��ǰK����̬Ϊ['
        #         elif modec[9] == -100 and (macd_trend == 'SELL_TRAND_H1' or macd_trend == 'SELL_TRAND_H4' or macd_trend == 'SELL_TRAND_D') :
        #             order_Type = '����'
        #             moderedme = 'MACD����[��ͷ]���Ƶ��У���ǰK����̬Ϊ['
        #         try:
        #             contents.append(
        #                 '<p><strong>���Ҷң�[' + symbol + ']' + moderedme + order_Type + ']����ģʽ</strong></p>������K��ģʽ��������ʮ����ɣ� �ڶ���ʮ�ֱ�����ڻ��ߵ��ڵ�һ�պ͵����գ�Ԥʾ�ŷ�ת��')
        #             attrfile = generatebar.CandlesstickPng.GenerateBarPng(symbol, run_time)
        #             images.append(attrfile)
        #         except Exception as e:
        #             log.error('���ͻ��Ҷң�' + symbol + '�ʼ���Ϣʧ�ܣ� ��ǰģʽΪ������' + str(e))
        #
        #     '''
        #     ��������CDLUNIQUE3RIVER
        #     ���ƣ�Unique 3 River �������Ӵ�
        #     ��飺����K��ģʽ���µ������У���һ�ճ����ߣ��ڶ���Ϊ��ͷ����ͼ۴��µͣ������տ��̼۵��ڵڶ������̼ۣ������ߣ� ���̼۲����ڵڶ������̼ۣ�Ԥʾ�ŷ�ת���ڶ�����Ӱ��Խ��������Խ��
        #     '''
        #     modec = talib.CDLUNIQUE3RIVER(rates_frame.open.values, rates_frame.high.values, rates_frame.low.values,
        #                                   rates_frame.close.values)
        #     if modec[9] == 100 or modec[9] == -100:
        #         if modec[9] == 100 and (macd_trend == 'BUY_TRAND_H1' or macd_trend == 'BUY_TRAND_H4' or macd_trend =='BUY_TRAND_D'):
        #             order_Type = '��'
        #             moderedme = ' MACD����[��ͷ]���Ƶ���,��ǰK����̬Ϊ['
        #         elif modec[9] == -100 and (macd_trend == 'SELL_TRAND_H1' or macd_trend == 'SELL_TRAND_H4' or macd_trend == 'SELL_TRAND_D') :
        #             order_Type = '����'
        #             moderedme = 'MACD����[��ͷ]���Ƶ��У���ǰK����̬Ϊ['
        #         try:
        #             contents.append(
        #                 '<p><strong>���Ҷң�[' + symbol + ']' + moderedme + order_Type + ']�������Ӵ�ģʽ</strong></p>��K��ģʽ���µ������У���һ�ճ����ߣ��ڶ���Ϊ��ͷ����ͼ۴��µͣ������տ��̼۵��ڵڶ������̼ۣ������ߣ� ���̼۲����ڵڶ������̼ۣ�Ԥʾ�ŷ�ת���ڶ�����Ӱ��Խ��������Խ��')
        #             attrfile = generatebar.CandlesstickPng.GenerateBarPng(symbol, run_time)
        #             images.append(attrfile)
        #         except Exception as e:
        #             log.error('���ͻ��Ҷң�' + symbol + '�ʼ���Ϣʧ�ܣ� ��ǰģʽΪ���������Ӵ�' + str(e))
        #
        #     '''
        #     ��������CDLUPSIDEGAP2CROWS
        #     ���ƣ�Upside Gap Two Crows �������յ���ֻ��ѻ
        #     ��飺����K��ģʽ����һ�����ߣ��ڶ��������Ը��ڵ�һ����߼ۿ��̣� �����ߣ������տ��̼۸��ڵڶ��գ������ߣ����һ�ձ�����ȱ�ڡ�
        #     '''
        #     modec = talib.CDLUPSIDEGAP2CROWS(rates_frame.open.values, rates_frame.high.values, rates_frame.low.values,
        #                                      rates_frame.close.values)
        #     if modec[9] == 100 or modec[9] == -100:
        #         if modec[9] == 100 and (macd_trend == 'BUY_TRAND_H1' or macd_trend == 'BUY_TRAND_H4' or macd_trend =='BUY_TRAND_D'):
        #             order_Type = '��'
        #             moderedme = ' MACD����[��ͷ]���Ƶ���,��ǰK����̬Ϊ['
        #         elif modec[9] == -100 and (macd_trend == 'SELL_TRAND_H1' or macd_trend == 'SELL_TRAND_H4' or macd_trend == 'SELL_TRAND_D') :
        #             order_Type = '����'
        #             moderedme = 'MACD����[��ͷ]���Ƶ��У���ǰK����̬Ϊ['
        #             try:
        #                 contents.append(
        #                     '<p><strong>���Ҷң�[' + symbol + ']' + moderedme + order_Type + ']�������յ���ֻ��ѻģʽ</strong></p>����K��ģʽ����һ�����ߣ��ڶ��������Ը��ڵ�һ����߼ۿ��̣� �����ߣ������տ��̼۸��ڵڶ��գ������ߣ����һ�ձ�����ȱ�ڡ�')
        #                 attrfile = generatebar.CandlesstickPng.GenerateBarPng(symbol, run_time)
        #                 images.append(attrfile)
        #             except Exception as e:
        #                 log.error('���ͻ��Ҷң�' + symbol + '�ʼ���Ϣʧ�ܣ� ��ǰģʽΪ���������յ���ֻ��ѻ' + str(e))
        #
        #     '''
        #     ��������CDLXSIDEGAP3METHODS
        #     ���ƣ�Upside/Downside Gap Three Methods ����/�½���������
        #     ��飺����K��ģʽ����������������Ϊ�������������У���һ�ճ����ߣ��ڶ��ն����ߣ��������������ߣ����������ߣ����̼������̼���ǰ����ʵ���ڣ� �����ճ����ߣ����̼۸��ڵ�һ�����̼ۣ�Ԥʾ�ɼ�������
        #     '''
        #     modec = talib.CDLXSIDEGAP3METHODS(rates_frame.open.values, rates_frame.high.values, rates_frame.low.values,
        #                                       rates_frame.close.values)
        #     if modec[9] == 100 or modec[9] == -100:
        #         if modec[9] == 100 and (macd_trend == 'BUY_TRAND_H1' or macd_trend == 'BUY_TRAND_H4' or macd_trend =='BUY_TRAND_D'):
        #             order_Type = '��'
        #             moderedme = ' MACD����[��ͷ]���Ƶ���,��ǰK����̬Ϊ['
        #         elif modec[9] == -100 and (macd_trend == 'SELL_TRAND_H1' or macd_trend == 'SELL_TRAND_H4' or macd_trend == 'SELL_TRAND_D') :
        #             order_Type = '����'
        #             moderedme = 'MACD����[��ͷ]���Ƶ��У���ǰK����̬Ϊ['
        #             try:
        #                 contents.append(
        #                     '<p><strong>���Ҷң�[' + symbol + ']' + moderedme + order_Type + ']����/�½���������ģʽ</strong></p>����K'
        #                                                                                  '��ģʽ����������������Ϊ�������������У���һ�ճ����ߣ��ڶ��ն����ߣ��������������ߣ����������ߣ����̼������̼���ǰ����ʵ���ڣ� �����ճ����ߣ����̼۸��ڵ�һ�����̼ۣ�Ԥʾ�ɼ�������')
        #                 attrfile = generatebar.CandlesstickPng.GenerateBarPng(symbol, run_time)
        #                 images.append(attrfile)
        #             except Exception as e:
        #                 # print("�����ʼ�ʧ��");
        #                 log.error('���ͻ��Ҷң�' + symbol + '�ʼ���Ϣʧ�ܣ� ��ǰģʽΪ������/�½���������' + str(e))
    if len(contents) != 0:
        try:
            m.sendMail(contents, images, run_time)   #ϵͳ���Է�Ϊ���� MACD �� KDEMA ��ǰ����macd����Ϊ��ֻ�����м�¼ΪMACDΪ1���û������ʼ�
        except Exception as e:
            log.error('�����ʼ�ʧ��  ԭ��' + e.toStr())
    log.info('=' * 50 + '�������' + '=' * 50)

# BlockingScheduler
# scheduler = BlockingScheduler()
# scheduler.add_job(K_ModeSelect, 'date', run_date=time(0000), args=['232323'], id='K_ModeSelect')
# scheduler.start()
