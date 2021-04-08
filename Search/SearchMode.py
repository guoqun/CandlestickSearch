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


# K线模式识别搜索
def K_ModeSelect(run_time):
    global moderedme
    images = []  # 邮件K线模型图存储
    contents = []
    # 定义需要获取数据的列表
    week = weekend.WeekendSearch.WekSear()
    if week == 5 or week == 6:  # 判断周未发送的品种信息，如果是周未则只做BTCUSD的检索
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
        # log.info(run_time+'当前检索货币兑：'+symbol+'数据:\n')
        pd.set_option('display.max_columns', 15000)  # number of columns to be displayed
        pd.set_option('display.width', 15000)  # max table width to displayema
        # 建立与MetaTrader 5程序端的连接
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
                    pool.Pool(symbol) #每天按计划更新趋势池
                except Exception as e:
                    log.error('更新趋势池子错误……')
            elif run_time == 'W1':
                rates = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_W1, 0, 11)
        except Exception as e:
            log.error("计算模型时，获取MT5数据失败......" + str(e))
        mt5.shutdown()  # 关闭MT5
        rates_frame = pd.DataFrame(rates)
        rates_frame['time'] = pd.to_datetime(rates_frame['time'], unit='s')
        log.info(run_time + '计算模型货币兑：' + symbol + '数据:\nC#')
        rates_frame = rates_frame[:10]  # 数据切片处理 减去当前线的时间
        log.info(rates_frame)

        # KD策略生成
        ema = emas.KDEMA_Strategy(symbol,run_time)
        if ema is not None :
            attrfile = generatebar.CandlesstickPng.GenerateBarPng(symbol, run_time)
            images.append(attrfile)
            contents.append('<p><strong>货币兑[' + symbol + ']' + '在' + run_time + '周期发出'+ema+'信号')

        # macd策略生成
        # macd = mr.ResonanceMacd(symbol, run_time)
        # if macd == 'BUY_H1' or   macd == 'BUY_H4' or  macd == 'BUY_D1' :  # 处理MACD多单共振的提醒
        #     try:
        #         attrfile = generatebar.CandlesstickPng.GenerateBarPng(symbol, run_time)
        #         images.append(attrfile)
        #         contents.append('<p><strong>货币兑[' + symbol + ']' + '在' + macd + '周期出MACD发生上穿，并且走势与更大的周期保持一致，请注意查看')
        #     except Exception as e:
        #         log.error('判断MACD上穿时发生异常............... \n')
        #         log.error(e.toStr())
        # if macd == 'SELL_H1' or macd == 'SELL_H4' or macd == 'SELL_D1' : # 处理MACD空单共振的提醒
        #     try:
        #         attrfile = generatebar.CandlesstickPng.GenerateBarPng(symbol, run_time)
        #         images.append(attrfile)
        #         contents.append('<p><strong>货币兑[' + symbol + ']' + '在' + macd + '周期出MACD发生下穿，并且走势与更大的周期保持一致，请注意查看')
        #     except Exception as e:
        #         log.error('判断MACD下穿时发生异常............... \n')
        #         log.error(e.toStr())
        #处理MACDPOOL池子
        try:
            macdpool.TrendMacdpool(symbol,run_time)
        except Exception as e:
            log.error(symbol+'更新MACDPOOL池子出错………………')
            log.error(e)
        #处理MACD趋势
        try:
            macd_trend = macdtrend.TrendMacd(symbol, run_time)
            if macd_trend is not None:
                contents.append('<p><strong>['+symbol+']'+macd_trend+'</strong></p>')
                attrfile = generatebar.CandlesstickPng.GenerateBarPng(symbol, run_time)
                images.append(attrfile)
        except Exception as e:
            log.error(symbol+'计算MACD趋势出错……')
            log.error(e)
        # if macd_trend is not None: #如果趋势形成 则开始检测K线的形态
        #     '''
        #     函数名：CDL2CROWS
        #     名称：Two Crows 两只乌鸦
        #     简介：三日K线模式，第一天长阳，第二天高开收阴，第三天再次高开继续收阴， 收盘比前一日收盘价低，预示股价下跌。
        #     '''
        #     # 开始处理K线形态部份
        #     modec = talib.CDL2CROWS(rates_frame.open.values, rates_frame.high.values, rates_frame.low.values,
        #                             rates_frame.close.values)
        #     if modec[9] == 100 or modec[9] == -100:
        #         if modec[9] == 100 and (macd_trend == 'BUY_TRAND_H1' or macd_trend == 'BUY_TRAND_H4' or macd_trend =='BUY_TRAND_D'):
        #             order_Type = '买单'
        #             moderedme = ' MACD处于[多头]趋势当中,当前K线形态为['
        #         elif modec[9] == -100 and (macd_trend == 'SELL_TRAND_H1' or macd_trend == 'SELL_TRAND_H4' or macd_trend == 'SELL_TRAND_D') :
        #             order_Type = '卖单'
        #             moderedme = 'MACD处于[空头]趋势当中，当前K线形态为['
        #         try:
        #             contents.append(
        #                 '<p><strong>货币兑：[' + symbol + ']' + moderedme + order_Type + ']两只乌鸦模式</strong></p>两只乌鸦三日K'
        #                                                                              '线模式，第一天长阳，第二天高开收阴，第三天再次高开继续收阴， '
        #                                                                              '收盘比前一日收盘价低，预示股价下跌。')
        #             attrfile = generatebar.CandlesstickPng.GenerateBarPng(symbol, run_time)
        #             images.append(attrfile)
        #         except Exception as e:
        #             log.error('发送货币兑：' + symbol + '两只乌鸦发送邮件失败' + str(e))
        #
        #     '''
        #     函数名：CDL3BLACKCROWS
        #     名称：Three Black Crows 三只乌鸦
        #     简介：三日K线模式，连续三根阴线，每日收盘价都下跌且接近最低价， 每日开盘价都在上根K线实体内，预示股价下跌。
        #     '''
        #     modec = talib.CDL3BLACKCROWS(rates_frame.open.values, rates_frame.high.values, rates_frame.low.values,
        #                                  rates_frame.close.values)
        #     if modec[9] == 100 or modec[9] == -100:
        #         if modec[9] == 100 and (macd_trend == 'BUY_TRAND_H1' or macd_trend == 'BUY_TRAND_H4' or macd_trend =='BUY_TRAND_D'):
        #             order_Type = '买单'
        #             moderedme = ' MACD处于[多头]趋势当中,当前K线形态为['
        #         elif modec[9] == -100 and (macd_trend == 'SELL_TRAND_H1' or macd_trend == 'SELL_TRAND_H4' or macd_trend == 'SELL_TRAND_D') :
        #             order_Type = '卖单'
        #             moderedme = 'MACD处于[空头]趋势当中，当前K线形态为['
        #         try:
        #             contents.append(
        #                 '<p><strong>货币兑：[' + symbol + ']' + +moderedme + order_Type + +']三只乌鸦模式</strong></p>三日K'
        #                                                                                '线模式，连续三根阴线，每日收盘价都下跌且接近最低价， '
        #                                                                                '每日开盘价都在上根K线实体内，预示股价下跌。')
        #             attrfile = generatebar.CandlesstickPng.GenerateBarPng(symbol, run_time)
        #             images.append(attrfile)
        #         except Exception as e:
        #             log.error('发送货币兑：' + symbol + '邮件信息失败！ 当前模式为：三只乌鸦' + str(e))
        #
        #     '''
        #     函数名：CDL3INSIDE
        #     名称： Three Inside Up/Down 内部上涨和下跌
        #     简介：三日K线模式，母子信号+长K线，以三内部上涨为例，K线为阴阳阳， 第三天收盘价高于第一天开盘价，第二天K线在第一天K线内部，预示着股价上涨。
        #     '''
        #     modec = talib.CDL3INSIDE(rates_frame.open.values, rates_frame.high.values, rates_frame.low.values,
        #                              rates_frame.close.values)
        #     if modec[9] == 100 or modec[9] == -100:
        #         if modec[9] == 100 and (macd_trend == 'BUY_TRAND_H1' or macd_trend == 'BUY_TRAND_H4' or macd_trend =='BUY_TRAND_D'):
        #             order_Type = '买单'
        #             moderedme = ' MACD处于[多头]趋势当中,当前K线形态为['
        #         elif modec[9] == -100 and (macd_trend == 'SELL_TRAND_H1' or macd_trend == 'SELL_TRAND_H4' or macd_trend == 'SELL_TRAND_D') :
        #             order_Type = '卖单'
        #             moderedme = 'MACD处于[空头]趋势当中，当前K线形态为['
        #         try:
        #             contents.append(
        #                 ' <p><strong>货币兑：[' + symbol + ']' + moderedme + order_Type + ']三内部上涨和下跌模式</strong></p>三日K'
        #                                                                               '线模式，母子信号+长K线，以三内部上涨为例，K线为阴阳阳， '
        #                                                                               '第三天收盘价高于第一天开盘价，第二天K线在第一天K线内部，预示着股价上涨')
        #             attrfile = generatebar.CandlesstickPng.GenerateBarPng(symbol, run_time)
        #             images.append(attrfile)
        #             log.info('发送货币兑：' + symbol + '邮件信息成功！ 当前模式为：三内部上涨和下跌')
        #         except Exception as e:
        #             log.error('发送货币兑：' + symbol + '邮件信息失败！ 当前模式为：三内部上涨和下跌' + str(e))
        #
        #     '''
        #     函数名：CDL3LINESTRIKE
        #     名称： Three-Line Strike 三线打击
        #     简介：四日K线模式，前三根阳线，每日收盘价都比前一日高， 开盘价在前一日实体内，第四日市场高开，收盘价低于第一日开盘价，预示股价下跌。
        #     '''
        #     modec = talib.CDL3LINESTRIKE(rates_frame.open.values, rates_frame.high.values, rates_frame.low.values,
        #                                  rates_frame.close.values)
        #     if modec[9] == 100 or modec[9] == -100:
        #         if modec[9] == 100 and (macd_trend == 'BUY_TRAND_H1' or macd_trend == 'BUY_TRAND_H4' or macd_trend =='BUY_TRAND_D'):
        #             order_Type = '买单'
        #             moderedme = ' MACD处于[多头]趋势当中,当前K线形态为['
        #         elif modec[9] == -100 and (macd_trend == 'SELL_TRAND_H1' or macd_trend == 'SELL_TRAND_H4' or macd_trend == 'SELL_TRAND_D') :
        #             order_Type = '卖单'
        #             moderedme = 'MACD处于[空头]趋势当中，当前K线形态为['
        #         try:
        #             contents.append('<p><strong>货币兑：[' + symbol + ']' + moderedme + order_Type + ']三线打击模式</strong></p> '
        #                                                                                          '四日K线模式，前三根阳线，每日收盘价都比前一日高， '
        #                                                                                          '开盘价在前一日实体内，第四日市场高开，收盘价低于第一日开盘价，预示股价下跌。')
        #             attrfile = generatebar.CandlesstickPng.GenerateBarPng(symbol, run_time)
        #             images.append(attrfile)
        #         except Exception as e:
        #             log.error('发送货币兑：' + symbol + '邮件信息失败！ 当前模式为：三线打击' + str(e))
        #
        #     '''
        #     函数名：CDL3OUTSIDE
        #     名称：Three Outside Up/Down 三外部上涨和下跌
        #     简介：三日K线模式，与三内部上涨和下跌类似，K线为阴阳阳，但第一日与第二日的K线形态相反， 以三外部上涨为例，第一日K线在第二日K线内部，预示着股价上涨。
        #     '''
        #     modec = talib.CDL3OUTSIDE(rates_frame.open.values, rates_frame.high.values, rates_frame.low.values,
        #                               rates_frame.close.values)
        #     if modec[9] == 100 or modec[9] == -100:
        #         if modec[9] == 100 and (macd_trend == 'BUY_TRAND_H1' or macd_trend == 'BUY_TRAND_H4' or macd_trend =='BUY_TRAND_D'):
        #             order_Type = '买单'
        #             moderedme = ' MACD处于[多头]趋势当中,当前K线形态为['
        #         elif modec[9] == -100 and (macd_trend == 'SELL_TRAND_H1' or macd_trend == 'SELL_TRAND_H4' or macd_trend == 'SELL_TRAND_D') :
        #             order_Type = '卖单'
        #             moderedme = 'MACD处于[空头]趋势当中，当前K线形态为['
        #         try:
        #             contents.append(
        #                 '<p><strong>货币兑：[' + symbol + ']' + moderedme + order_Type + ']三外部上涨和下跌模式</strong></p>三日K'
        #                                                                              '线模式，与三内部上涨和下跌类似，K线为阴阳阳，但第一日与第二日的K'
        #                                                                              '线形态相反， '
        #                                                                              '以三外部上涨为例，第一日K线在第二日K线内部，预示着股价上涨。')
        #             attrfile = generatebar.CandlesstickPng.GenerateBarPng(symbol, run_time)
        #             images.append(attrfile)
        #         except Exception as e:
        #             log.error('发送货币兑：' + symbol + '邮件信息失败！ 当前模式为：三外部上涨和下跌' + str(e))
        #     '''
        #     函数名：CDL3STARSINSOUTH
        #     名称：Three Stars In The South 南方三星
        #     简介：三日K线模式，与大敌当前相反，三日K线皆阴，第一日有长下影线， 第二日与第一日类似，K线整体小于第一日，第三日无下影线实体信号， 成交价格都在第一日振幅之内，预示下跌趋势反转，股价上升。
        #     '''
        #     modec = talib.CDL3STARSINSOUTH(rates_frame.open.values, rates_frame.high.values, rates_frame.low.values,
        #                                    rates_frame.close.values)
        #     if modec[9] == 100 or modec[9] == -100:
        #         if modec[9] == 100 and (macd_trend == 'BUY_TRAND_H1' or macd_trend == 'BUY_TRAND_H4' or macd_trend =='BUY_TRAND_D'):
        #             order_Type = '买单'
        #             moderedme = ' MACD处于[多头]趋势当中,当前K线形态为['
        #         elif modec[9] == -100 and (macd_trend == 'SELL_TRAND_H1' or macd_trend == 'SELL_TRAND_H4' or macd_trend == 'SELL_TRAND_D') :
        #             order_Type = '卖单'
        #             moderedme = 'MACD处于[空头]趋势当中，当前K线形态为['
        #         try:
        #             contents.append(
        #                 '<p><strong>货币兑：[' + symbol + ']' + moderedme + order_Type + ']南方三星模式</strong></p>三日K'
        #                                                                              '线模式，与大敌当前相反，三日K线皆阴，第一日有长下影线， '
        #                                                                              '第二日与第一日类似，K线整体小于第一日，第三日无下影线实体信号， '
        #                                                                              '成交价格都在第一日振幅之内，预示下跌趋势反转，股价上升。')
        #             attrfile = generatebar.CandlesstickPng.GenerateBarPng(symbol, run_time)
        #             images.append(attrfile)
        #         except Exception as e:
        #             log.error('发送货币兑：' + symbol + '邮件信息失败！ 当前模式为：南方三星' + str(e))
        #     '''
        #     函数名：CDL3WHITESOLDIERS
        #     名称：Three Advancing White Soldiers 三个白兵
        #     简介：三日K线模式，三日K线皆阳， 每日收盘价变高且接近最高价，开盘价在前一日实体上半部，预示股价上升。
        #     '''
        #     modec = talib.CDL3WHITESOLDIERS(rates_frame.open.values, rates_frame.high.values, rates_frame.low.values,
        #                                     rates_frame.close.values)
        #     if modec[9] == 100 or modec[9] == -100:
        #         if modec[9] == 100 and (macd_trend == 'BUY_TRAND_H1' or macd_trend == 'BUY_TRAND_H4' or macd_trend =='BUY_TRAND_D'):
        #             order_Type = '买单'
        #             moderedme = ' MACD处于[多头]趋势当中,当前K线形态为['
        #         elif modec[9] == -100 and (macd_trend == 'SELL_TRAND_H1' or macd_trend == 'SELL_TRAND_H4' or macd_trend == 'SELL_TRAND_D') :
        #             order_Type = '卖单'
        #             moderedme = 'MACD处于[空头]趋势当中，当前K线形态为['
        #         try:
        #             contents.append('<p><strong>货币兑：[' + symbol + ']' + moderedme + order_Type + ']三个白兵模式</strong></p> '
        #                                                                                          '三日K线模式，三日K线皆阳， '
        #                                                                                          '每日收盘价变高且接近最高价，开盘价在前一日实体上半部，预示股价上升。')
        #             attrfile = generatebar.CandlesstickPng.GenerateBarPng(symbol, run_time)
        #             images.append(attrfile)
        #         except Exception as e:
        #             log.error('发送货币兑：' + symbol + '邮件信息失败！ 当前模式为：三个白兵' + str(e))
        #     '''
        #     函数名：CDLABANDONEDBABY
        #     名称：Abandoned Baby 弃婴
        #     简介：三日K线模式，第二日价格跳空且收十字星（开盘价与收盘价接近， 最高价最低价相差不大），预示趋势反转，发生在顶部下跌，底部上涨。
        #     '''
        #     modec = talib.CDLABANDONEDBABY(rates_frame.open.values, rates_frame.high.values, rates_frame.low.values,
        #                                    rates_frame.close.values, penetration=0)
        #     if modec[9] == 100 or modec[9] == -100:
        #         if modec[9] == 100 and (macd_trend == 'BUY_TRAND_H1' or macd_trend == 'BUY_TRAND_H4' or macd_trend =='BUY_TRAND_D'):
        #             order_Type = '买单'
        #             moderedme = ' MACD处于[多头]趋势当中,当前K线形态为['
        #         elif modec[9] == -100 and (macd_trend == 'SELL_TRAND_H1' or macd_trend == 'SELL_TRAND_H4' or macd_trend == 'SELL_TRAND_D') :
        #             order_Type = '卖单'
        #             moderedme = 'MACD处于[空头]趋势当中，当前K线形态为['
        #         try:
        #             contents.append('<p><strong>货币兑：[' + symbol + ']' + moderedme + order_Type + ']弃婴模式</strong></p>三日K'
        #                                                                                          '线模式，第二日价格跳空且收十字星（开盘价与收盘价接近， '
        #                                                                                          '最高价最低价相差不大），预示趋势反转，发生在顶部下跌，底部上涨。')
        #             attrfile = generatebar.CandlesstickPng.GenerateBarPng(symbol, run_time)
        #             images.append(attrfile)
        #         except Exception:
        #             log.error('发送货币兑：' + symbol + '邮件信息失败！ 当前模式为：弃婴' + str(e))
        #     '''
        #     函数名：CDLADVANCEBLOCK
        #     名称：Advance Block 大敌当前
        #     简介：三日K线模式，三日都收阳，每日收盘价都比前一日高， 开盘价都在前一日实体以内，实体变短，上影线变长。
        #     '''
        #     modec = talib.CDLADVANCEBLOCK(rates_frame.open.values, rates_frame.high.values, rates_frame.low.values,
        #                                   rates_frame.close.values)
        #     if modec[9] == 100 or modec[9] == -100:
        #         if modec[9] == 100 and (macd_trend == 'BUY_TRAND_H1' or macd_trend == 'BUY_TRAND_H4' or macd_trend =='BUY_TRAND_D'):
        #             order_Type = '买单'
        #             moderedme = ' MACD处于[多头]趋势当中,当前K线形态为['
        #         elif modec[9] == -100 and (macd_trend == 'SELL_TRAND_H1' or macd_trend == 'SELL_TRAND_H4' or macd_trend == 'SELL_TRAND_D') :
        #             order_Type = '卖单'
        #             moderedme = 'MACD处于[空头]趋势当中，当前K线形态为['
        #         try:
        #             contents.append(
        #                 '<p><strong>货币兑：[' + symbol + ']' + moderedme + order_Type + ']大敌当前模式</strong></p>三日K'
        #                                                                              '线模式，三日都收阳，每日收盘价都比前一日高， '
        #                                                                              '开盘价都在前一日实体以内，实体变短，上影线变长。')
        #             attrfile = generatebar.CandlesstickPng.GenerateBarPng(symbol, run_time)
        #             images.append(attrfile)
        #         except Exception as e:
        #             log.error('发送货币兑：' + symbol + '邮件信息失败！ 当前模式为：大敌当前' + str(e))
        #     '''
        #     函数名：CDLBELTHOLD
        #     名称：Belt-hold 捉腰带线
        #     简介：两日K线模式，下跌趋势中，第一日阴线， 第二日开盘价为最低价，阳线，收盘价接近最高价，预示价格上涨。
        #     '''
        #     modec = talib.CDLBELTHOLD(rates_frame.open.values, rates_frame.high.values, rates_frame.low.values,
        #                               rates_frame.close.values)
        #     if modec[9] == 100 or modec[9] == -100:
        #         if modec[9] == 100 and (macd_trend == 'BUY_TRAND_H1' or macd_trend == 'BUY_TRAND_H4' or macd_trend =='BUY_TRAND_D'):
        #             order_Type = '买单'
        #             moderedme = ' MACD处于[多头]趋势当中,当前K线形态为['
        #         elif modec[9] == -100 and (macd_trend == 'SELL_TRAND_H1' or macd_trend == 'SELL_TRAND_H4' or macd_trend == 'SELL_TRAND_D') :
        #             order_Type = '卖单'
        #             moderedme = 'MACD处于[空头]趋势当中，当前K线形态为['
        #         try:
        #             contents.append(
        #                 '<p><strong>货币兑：[' + symbol + ']' + moderedme + order_Type + ']捉腰带线模式</strong></p>两日K'
        #                                                                              '线模式，下跌趋势中，第一日阴线， '
        #                                                                              '第二日开盘价为最低价，阳线，收盘价接近最高价，预示价格上涨。')
        #             attrfile = generatebar.CandlesstickPng.GenerateBarPng(symbol, run_time)
        #             images.append(attrfile)
        #         except Exception as e:
        #             log.error('发送货币兑：' + symbol + '邮件信息失败！ 当前模式为：捉腰带线' + str(e))
        #
        #     '''
        #     函数名：CDLBREAKAWAY
        #     名称：Breakaway 脱离
        #     简介：五日K线模式，以看涨脱离为例，下跌趋势中，第一日长阴线，第二日跳空阴线，延续趋势开始震荡， 第五日长阳线，收盘价在第一天收盘价与第二天开盘价之间，预示价格上涨。
        #     '''
        #     modec = talib.CDLBREAKAWAY(rates_frame.open.values, rates_frame.high.values, rates_frame.low.values,
        #                                rates_frame.close.values)
        #     if modec[9] == 100 or modec[9] == -100:
        #         if modec[9] == 100 and (macd_trend == 'BUY_TRAND_H1' or macd_trend == 'BUY_TRAND_H4' or macd_trend =='BUY_TRAND_D'):
        #             order_Type = '买单'
        #             moderedme = ' MACD处于[多头]趋势当中,当前K线形态为['
        #         elif modec[9] == -100 and (macd_trend == 'SELL_TRAND_H1' or macd_trend == 'SELL_TRAND_H4' or macd_trend == 'SELL_TRAND_D') :
        #             order_Type = '卖单'
        #             moderedme = 'MACD处于[空头]趋势当中，当前K线形态为['
        #         try:
        #             contents.append('<p><strong>货币兑：[' + symbol + ']' + moderedme + order_Type + ']脱离模式</strong></p>五日K'
        #                                                                                          '线模式，以看涨脱离为例，下跌趋势中，第一日长阴线，第二日跳空阴线，延续趋势开始震荡， 第五日长阳线，收盘价在第一天收盘价与第二天开盘价之间，预示价格上涨。')
        #             attrfile = generatebar.CandlesstickPng.GenerateBarPng(symbol, run_time)
        #             images.append(attrfile)
        #         except Exception as e:
        #             log.error('发送货币兑：' + symbol + '邮件信息失败！ 当前模式为：脱离' + str(e))
        #
        #     '''
        #     函数名：CDLCLOSINGMARUBOZU
        #     名称：Closing Marubozu 收盘缺影线
        #     简介：一日K线模式，以阳线为例，最低价低于开盘价，收盘价等于最高价， 预示着趋势持续。
        #     '''
        #     modec = talib.CDLCLOSINGMARUBOZU(rates_frame.open.values, rates_frame.high.values, rates_frame.low.values,
        #                                      rates_frame.close.values)
        #     if modec[9] == 100 or modec[9] == -100:
        #         if modec[9] == 100 and (macd_trend == 'BUY_TRAND_H1' or macd_trend == 'BUY_TRAND_H4' or macd_trend =='BUY_TRAND_D'):
        #             order_Type = '买单'
        #             moderedme = ' MACD处于[多头]趋势当中,当前K线形态为['
        #         elif modec[9] == -100 and (macd_trend == 'SELL_TRAND_H1' or macd_trend == 'SELL_TRAND_H4' or macd_trend == 'SELL_TRAND_D') :
        #             order_Type = '卖单'
        #             moderedme = 'MACD处于[空头]趋势当中，当前K线形态为['
        #         try:
        #             contents.append(
        #                 '<p><strong>货币兑：[' + symbol + ']' + moderedme + order_Type + ']收盘缺影线模式</strong></p>一日K'
        #                                                                              '线模式，以阳线为例，最低价低于开盘价，收盘价等于最高价， '
        #                                                                              '预示着趋势持续。')
        #             attrfile = generatebar.CandlesstickPng.GenerateBarPng(symbol, run_time)
        #             images.append(attrfile)
        #         except Exception as e:
        #             log.error('发送货币兑：' + symbol + '邮件信息失败！ 当前模式为：收盘缺影线' + str(e))
        #     '''
        #     函数名：CDLCONCEALBABYSWALL
        #     名称： Concealing Baby Swallow 藏婴吞没
        #     简介：四日K线模式，下跌趋势中，前两日阴线无影线 ，第二日开盘、收盘价皆低于第二日，第三日倒锤头， 第四日开盘价高于前一日最高价，收盘价低于前一日最低价，预示着底部反转。
        #     '''
        #     modec = talib.CDLCONCEALBABYSWALL(rates_frame.open.values, rates_frame.high.values, rates_frame.low.values,
        #                                       rates_frame.close.values)
        #     if modec[9] == 100 or modec[9] == -100:
        #         if modec[9] == 100 and (macd_trend == 'BUY_TRAND_H1' or macd_trend == 'BUY_TRAND_H4' or macd_trend =='BUY_TRAND_D'):
        #             order_Type = '买单'
        #             moderedme = ' MACD处于[多头]趋势当中,当前K线形态为['
        #         elif modec[9] == -100 and (macd_trend == 'SELL_TRAND_H1' or macd_trend == 'SELL_TRAND_H4' or macd_trend == 'SELL_TRAND_D') :
        #             order_Type = '卖单'
        #             moderedme = 'MACD处于[空头]趋势当中，当前K线形态为['
        #         try:
        #             contents.append(
        #                 '<p><strong>货币兑：[' + symbol + ']' + moderedme + order_Type + ']藏婴吞没模式</strong></p>四日K'
        #                                                                              '线模式，下跌趋势中，前两日阴线无影线 '
        #                                                                              '，第二日开盘、收盘价皆低于第二日，第三日倒锤头， '
        #                                                                              '第四日开盘价高于前一日最高价，收盘价低于前一日最低价，预示着底部反转。')
        #             attrfile = generatebar.CandlesstickPng.GenerateBarPng(symbol, run_time)
        #             images.append(attrfile)
        #         except Exception as e:
        #             log.error('发送货币兑：' + symbol + '邮件信息失败！ 当前模式为：藏婴吞没' + str(e))
        #     '''
        #     函数名：CDLCOUNTERATTACK
        #     名称：Counterattack 反击线
        #     简介：二日K线模式，与分离线类似。
        #     '''
        #     modec = talib.CDLCOUNTERATTACK(rates_frame.open.values, rates_frame.high.values, rates_frame.low.values,
        #                                    rates_frame.close.values)
        #     if modec[9] == 100 or modec[9] == -100:
        #         if modec[9] == 100 and (macd_trend == 'BUY_TRAND_H1' or macd_trend == 'BUY_TRAND_H4' or macd_trend =='BUY_TRAND_D'):
        #             order_Type = '买单'
        #             moderedme = ' MACD处于[多头]趋势当中,当前K线形态为['
        #         elif modec[9] == -100 and (macd_trend == 'SELL_TRAND_H1' or macd_trend == 'SELL_TRAND_H4' or macd_trend == 'SELL_TRAND_D') :
        #             order_Type = '卖单'
        #             moderedme = 'MACD处于[空头]趋势当中，当前K线形态为['
        #         try:
        #             contents.append(
        #                 '<p><strong>货币兑：[' + symbol + ']' + moderedme + order_Type + ']反击线模式</strong></p>二日K线模式，与分离线类似。')
        #             attrfile = generatebar.CandlesstickPng.GenerateBarPng(symbol, run_time)
        #             images.append(attrfile)
        #         except Exception as e:
        #             log.error('发送货币兑：' + symbol + '邮件信息失败！ 当前模式为：反击线' + str(e))
        #
        #     '''
        #     函数名：CDLDARKCLOUDCOVER
        #     名称：Dark Cloud Cover 乌云压顶
        #     简介：二日K线模式，第一日长阳，第二日开盘价高于前一日最高价， 收盘价处于前一日实体中部以下，预示着股价下跌。
        #     '''
        #     modec = talib.CDLDARKCLOUDCOVER(rates_frame.open.values, rates_frame.high.values, rates_frame.low.values,
        #                                     rates_frame.close.values)
        #     if modec[9] == 100 or modec[9] == -100:
        #         if modec[9] == 100 and (macd_trend == 'BUY_TRAND_H1' or macd_trend == 'BUY_TRAND_H4' or macd_trend =='BUY_TRAND_D'):
        #             order_Type = '买单'
        #             moderedme = ' MACD处于[多头]趋势当中,当前K线形态为['
        #         elif modec[9] == -100 and (macd_trend == 'SELL_TRAND_H1' or macd_trend == 'SELL_TRAND_H4' or macd_trend == 'SELL_TRAND_D') :
        #             order_Type = '卖单'
        #             moderedme = 'MACD处于[空头]趋势当中，当前K线形态为['
        #         try:
        #             contents.append(
        #                 '<p><strong>货币兑：[' + symbol + ']' + moderedme + order_Type + ']乌云压顶模式</strong></p>二日K'
        #                                                                              '线模式，第一日长阳，第二日开盘价高于前一日最高价， '
        #                                                                              '收盘价处于前一日实体中部以下，预示着股价下跌。')
        #             attrfile = generatebar.CandlesstickPng.GenerateBarPng(symbol, run_time)
        #             images.append(attrfile)
        #         except Exception as e:
        #             log.error('发送货币兑：' + symbol + '邮件信息失败！ 当前模式为：乌云压顶' + str(e))
        #     '''
        #     函数名：CDLDOJI
        #     名称：Doji 十字
        #     简介：一日K线模式，开盘价与收盘价基本相同。
        #     '''
        #     modec = talib.CDLDOJI(rates_frame.open.values, rates_frame.high.values, rates_frame.low.values,
        #                           rates_frame.close.values)
        #     if modec[9] == 100 or modec[9] == -100:
        #         if modec[9] == 100 and (macd_trend == 'BUY_TRAND_H1' or macd_trend == 'BUY_TRAND_H4' or macd_trend =='BUY_TRAND_D'):
        #             order_Type = '买单'
        #             moderedme = ' MACD处于[多头]趋势当中,当前K线形态为['
        #         elif modec[9] == -100 and (macd_trend == 'SELL_TRAND_H1' or macd_trend == 'SELL_TRAND_H4' or macd_trend == 'SELL_TRAND_D') :
        #             order_Type = '卖单'
        #             moderedme = 'MACD处于[空头]趋势当中，当前K线形态为['
        #         try:
        #             contents.append(
        #                 '<p><strong>货币兑：[' + symbol + ']' + moderedme + order_Type + ']十字模式</strong></p>一日K线模式，开盘价与收盘价基本相同。')
        #             attrfile = generatebar.CandlesstickPng.GenerateBarPng(symbol, run_time)
        #             images.append(attrfile)
        #         except Exception as e:
        #             log.error('发送货币兑：' + symbol + '邮件信息失败！ 当前模式为：十字' + str(e))
        #
        #     '''
        #     函数名：CDLDOJISTAR
        #     名称：Doji Star 十字星
        #     简介：一日K线模式，开盘价与收盘价基本相同，上下影线不会很长，预示着当前趋势反转。
        #     '''
        #     modec = talib.CDLDOJISTAR(rates_frame.open.values, rates_frame.high.values, rates_frame.low.values,
        #                               rates_frame.close.values)
        #     if modec[9] == 100 or modec[9] == -100:
        #         if modec[9] == 100 and (macd_trend == 'BUY_TRAND_H1' or macd_trend == 'BUY_TRAND_H4' or macd_trend =='BUY_TRAND_D'):
        #             order_Type = '买单'
        #             moderedme = ' MACD处于[多头]趋势当中,当前K线形态为['
        #         elif modec[9] == -100 and (macd_trend == 'SELL_TRAND_H1' or macd_trend == 'SELL_TRAND_H4' or macd_trend == 'SELL_TRAND_D') :
        #             order_Type = '卖单'
        #             moderedme = 'MACD处于[空头]趋势当中，当前K线形态为['
        #         try:
        #             contents.append('<p><strong>货币兑：[' + symbol + ']' + moderedme + order_Type + ']十字星模式</strong></p> '
        #                                                                                          '一日K线模式，开盘价与收盘价基本相同，上下影线不会很长，预示着当前趋势反转。')
        #             attrfile = generatebar.CandlesstickPng.GenerateBarPng(symbol, run_time)
        #             images.append(attrfile)
        #         except Exception as e:
        #             log.error('发送货币兑：' + symbol + '邮件信息失败！ 当前模式为：十字星' + str(e))
        #     '''
        #     函数名：CDLDRAGONFLYDOJI
        #     名称：Dragonfly Doji 蜻蜓十字/T形十字
        #     简介：一日K线模式，开盘后价格一路走低， 之后收复，收盘价与开盘价相同，预示趋势反转。
        #     '''
        #
        #     modec = talib.CDLDRAGONFLYDOJI(rates_frame.open.values, rates_frame.high.values, rates_frame.low.values,
        #                                    rates_frame.close.values)
        #     if modec[9] == 100 or modec[9] == -100:
        #         if modec[9] == 100 and (macd_trend == 'BUY_TRAND_H1' or macd_trend == 'BUY_TRAND_H4' or macd_trend =='BUY_TRAND_D'):
        #             order_Type = '买单'
        #             moderedme = ' MACD处于[多头]趋势当中,当前K线形态为['
        #         elif modec[9] == -100 and (macd_trend == 'SELL_TRAND_H1' or macd_trend == 'SELL_TRAND_H4' or macd_trend == 'SELL_TRAND_D') :
        #             order_Type = '卖单'
        #             moderedme = 'MACD处于[空头]趋势当中，当前K线形态为['
        #         try:
        #             contents.append(
        #                 '<p><strong>货币兑：[' + symbol + ']' + moderedme + order_Type + ']蜻蜓十字/T形十字模式</strong></p>一日K'
        #                                                                              '线模式，开盘后价格一路走低， '
        #                                                                              '之后收复，收盘价与开盘价相同，预示趋势反转。')
        #             attrfile = generatebar.CandlesstickPng.GenerateBarPng(symbol, run_time)
        #             images.append(attrfile)
        #         except Exception as e:
        #             log.error('发送货币兑：' + symbol + '邮件信息失败！ 当前模式为：蜻蜓十字/T形十字' + str(e))
        #
        #     '''
        #     函数名：CDLENGULFING
        #     名称：Engulfing Pattern 吞噬模式
        #     简介：两日K线模式，分多头吞噬和空头吞噬，以多头吞噬为例，第一日为阴线， 第二日阳线，第一日的开盘价和收盘价在第二日开盘价收盘价之内，但不能完全相同。
        #     '''
        #     # modec=talib.CDLENGULFING(rates_frame.open.values,rates_frame.high.values,rates_frame.low.values,rates_frame.close.values)
        #     # if modec[9]!=0:
        #     #     try:
        #     #         contents.append('<p><strong>货币兑：['+symbol+']多头或空头吞噬模式</strong></p>两日K线模式，分多头吞噬和空头吞噬，以多头吞噬为例，第一日为阴线， 第二日阳线，第一日的开盘价和收盘价在第二日开盘价收盘价之内，但不能完全相同。')
        #     #         attrfile =  generatebar.CandlesstickPng.GenerateBarPng(symbol,run_time)
        #     #         images.append(attrfile)
        #     #     except Exception as e:
        #     #         #print("发送邮件失败")
        #     #         log.error('发送货币兑：'+symbol+'邮件信息失败！ 当前模式为：吞噬模式'+str(e))
        #
        #     '''
        #     函数名：CDLEVENINGDOJISTAR
        #     名称：Evening Doji Star 十字暮星
        #     简介：三日K线模式，基本模式为暮星，第二日收盘价和开盘价相同，预示顶部反转。
        #     '''
        #     modec = talib.CDLEVENINGDOJISTAR(rates_frame.open.values, rates_frame.high.values, rates_frame.low.values,
        #                                      rates_frame.close.values, penetration=0)
        #     if modec[9] == 100 or modec[9] == -100:
        #         if modec[9] == 100 and (macd_trend == 'BUY_TRAND_H1' or macd_trend == 'BUY_TRAND_H4' or macd_trend =='BUY_TRAND_D'):
        #             order_Type = '买单'
        #             moderedme = ' MACD处于[多头]趋势当中,当前K线形态为['
        #         elif modec[9] == -100 and (macd_trend == 'SELL_TRAND_H1' or macd_trend == 'SELL_TRAND_H4' or macd_trend == 'SELL_TRAND_D') :
        #             order_Type = '卖单'
        #             moderedme = 'MACD处于[空头]趋势当中，当前K线形态为['
        #         try:
        #             contents.append('<p><strong>货币兑：[' + symbol + ']' + moderedme + order_Type + ']十字暮星模式<strong><p>三日K'
        #                                                                                          '线模式，基本模式为暮星，第二日收盘价和开盘价相同，预示顶部反转。')
        #             attrfile = generatebar.CandlesstickPng.GenerateBarPng(symbol, run_time)
        #             images.append(attrfile)
        #         except Exception as e:
        #             log.error('发送货币兑：' + symbol + '邮件信息失败！ 当前模式为：十字暮星' + str(e))
        #
        #     '''
        #     函数名：CDLEVENINGSTAR
        #     名称：Evening Star 暮星
        #     简介：三日K线模式，与晨星相反，上升趋势中, 第一日阳线，第二日价格振幅较小，第三日阴线，预示顶部反转。
        #     '''
        #     modec = talib.CDLEVENINGSTAR(rates_frame.open.values, rates_frame.high.values, rates_frame.low.values,
        #                                  rates_frame.close.values, penetration=0)
        #     if modec[9] == 100 or modec[9] == -100:
        #         if modec[9] == 100 and (macd_trend == 'BUY_TRAND_H1' or macd_trend == 'BUY_TRAND_H4' or macd_trend =='BUY_TRAND_D'):
        #             order_Type = '买单'
        #             moderedme = ' MACD处于[多头]趋势当中,当前K线形态为['
        #         elif modec[9] == -100 and (macd_trend == 'SELL_TRAND_H1' or macd_trend == 'SELL_TRAND_H4' or macd_trend == 'SELL_TRAND_D') :
        #             order_Type = '卖单'
        #             moderedme = 'MACD处于[空头]趋势当中，当前K线形态为['
        #         try:
        #             contents.append('<p><strong>货币兑：[' + symbol + ']' + moderedme + order_Type + ']暮星模式</strong></p>三日K'
        #                                                                                          '线模式，与晨星相反，上升趋势中, '
        #                                                                                          '第一日阳线，第二日价格振幅较小，第三日阴线，预示顶部反转。')
        #             attrfile = generatebar.CandlesstickPng.GenerateBarPng(symbol, run_time)
        #             images.append(attrfile)
        #         except Exception as e:
        #             log.error('货币兑：' + symbol + '邮件信息失败！ 当前模式为：暮星' + str(e))
        #
        #     '''
        #     函数名：CDLGAPSIDESIDEWHITE
        #     名称：Up/Down-gap side-by-side white lines 向上/下跳空并列阳线
        #     简介：二日K线模式，上升趋势向上跳空，下跌趋势向下跳空, 第一日与第二日有相同开盘价，实体长度差不多，则趋势持续。
        #     '''
        #     # modec=talib.CDLGAPSIDESIDEWHITE(rates_frame.open.values,rates_frame.high.values,rates_frame.low.values,rates_frame.close.values)
        #     # if modec[9]!=0:
        #     #     try:
        #     #         contents.append('<p><strong>货币兑：['+symbol+']向上/下跳空并列阳线</strong></p>二日K线模式，上升趋势向上跳空，下跌趋势向下跳空, 第一日与第二日有相同开盘价，实体长度差不多，则趋势持续。')
        #     #         attrfile =  generatebar.CandlesstickPng.GenerateBarPng(symbol,run_time)
        #     #         images.append(attrfile)
        #     #     except Exception as e:
        #     #         #print("发送邮件失败")
        #     #         log.error('发送货币兑：'+symbol+'邮件信息失败！ 当前模式为：向上/下跳空并列阳线'+str(e))
        #
        #     '''
        #     函数名：CDLGRAVESTONEDOJI
        #     名称：Gravestone Doji 墓碑十字/倒T十字
        #     简介：一日K线模式，开盘价与收盘价相同，上影线长，无下影线，预示底部反转。
        #     '''
        #     modec = talib.CDLGRAVESTONEDOJI(rates_frame.open.values, rates_frame.high.values, rates_frame.low.values,
        #                                     rates_frame.close.values)
        #     if modec[9] == 100 or modec[9] == -100:
        #         if modec[9] == 100 and (macd_trend == 'BUY_TRAND_H1' or macd_trend == 'BUY_TRAND_H4' or macd_trend =='BUY_TRAND_D'):
        #             order_Type = '买单'
        #             moderedme = ' MACD处于[多头]趋势当中,当前K线形态为['
        #         elif modec[9] == -100 and (macd_trend == 'SELL_TRAND_H1' or macd_trend == 'SELL_TRAND_H4' or macd_trend == 'SELL_TRAND_D') :
        #             order_Type = '卖单'
        #             moderedme = 'MACD处于[空头]趋势当中，当前K线形态为['
        #         try:
        #             contents.append(
        #                 '<p><strong>货币兑：[' + symbol + ']' + moderedme + order_Type + ']墓碑十字/倒T十字模式</strong></p> '
        #                                                                              '一日K线模式，开盘价与收盘价相同，上影线长，无下影线，预示底部反转。')
        #             attrfile = generatebar.CandlesstickPng.GenerateBarPng(symbol, run_time)
        #             images.append(attrfile)
        #         except Exception as e:
        #             log.error('发送货币兑：' + symbol + '邮件信息失败！ 当前模式为：墓碑十字/倒T十字' + str(e))
        #
        #     '''
        #     函数名：CDLHAMMER
        #     名称：Hammer 锤头
        #     简介：一日K线模式，实体较短，无上影线， 下影线大于实体长度两倍，处于下跌趋势底部，预示反转。
        #     '''
        #     modec = talib.CDLHAMMER(rates_frame.open.values, rates_frame.high.values, rates_frame.low.values,
        #                             rates_frame.close.values)
        #     if modec[9] == 100 or modec[9] == -100:
        #         if modec[9] == 100 and (macd_trend == 'BUY_TRAND_H1' or macd_trend == 'BUY_TRAND_H4' or macd_trend =='BUY_TRAND_D'):
        #             order_Type = '买单'
        #             moderedme = ' MACD处于[多头]趋势当中,当前K线形态为['
        #         elif modec[9] == -100 and (macd_trend == 'SELL_TRAND_H1' or macd_trend == 'SELL_TRAND_H4' or macd_trend == 'SELL_TRAND_D') :
        #             order_Type = '卖单'
        #             moderedme = 'MACD处于[空头]趋势当中，当前K线形态为['
        #         try:
        #             contents.append(
        #                 '<p><strong>货币兑：[' + symbol + ']' + moderedme + order_Type + ']锤头模式</strong></p>一日K线模式，实体较短，无上影线， 下影线大于实体长度两倍，处于下跌趋势底部，预示反转。')
        #             attrfile = generatebar.CandlesstickPng.GenerateBarPng(symbol, run_time)
        #             images.append(attrfile)
        #         except Exception as e:
        #             log.error('发送货币兑：' + symbol + '邮件信息失败！ 当前模式为：锤头' + str(e))
        #
        #     '''
        #     函数名：CDLHANGINGMAN
        #     名称：Hanging Man 上吊线
        #     简介：一日K线模式，形状与锤子类似，处于上升趋势的顶部，预示着趋势反转。
        #     '''
        #     modec = talib.CDLHANGINGMAN(rates_frame.open.values, rates_frame.high.values, rates_frame.low.values,
        #                                 rates_frame.close.values)
        #     if modec[9] == 100 or modec[9] == -100:
        #         if modec[9] == 100 and (macd_trend == 'BUY_TRAND_H1' or macd_trend == 'BUY_TRAND_H4' or macd_trend =='BUY_TRAND_D'):
        #             order_Type = '买单'
        #             moderedme = ' MACD处于[多头]趋势当中,当前K线形态为['
        #         elif modec[9] == -100 and (macd_trend == 'SELL_TRAND_H1' or macd_trend == 'SELL_TRAND_H4' or macd_trend == 'SELL_TRAND_D') :
        #             order_Type = '卖单'
        #             moderedme = 'MACD处于[空头]趋势当中，当前K线形态为['
        #         try:
        #             contents.append(
        #                 '<p><strong>货币兑：[' + symbol + ']' + moderedme + order_Type + ']上吊线模式</strong></p>一日K线模式，形状与锤子类似，处于上升趋势的顶部，预示着趋势反转。')
        #             attrfile = generatebar.CandlesstickPng.GenerateBarPng(symbol, run_time)
        #             images.append(attrfile)
        #         except Exception as e:
        #             log.error('发送货币兑：' + symbol + '邮件信息失败！ 当前模式为：上吊线' + str(e))
        #
        #     '''
        #     函数名：CDLHARAMI
        #     名称：Harami Pattern 母子线
        #     简介：二日K线模式，分多头母子与空头母子，两者相反，以多头母子为例，在下跌趋势中，第一日K线长阴， 第二日开盘价收盘价在第一日价格振幅之内，为阳线，预示趋势反转，股价上升。
        #     '''
        #     modec = talib.CDLHARAMI(rates_frame.open.values, rates_frame.high.values, rates_frame.low.values,
        #                             rates_frame.close.values)
        #     if modec[9] == 100 or modec[9] == -100:
        #         if modec[9] == 100 and (macd_trend == 'BUY_TRAND_H1' or macd_trend == 'BUY_TRAND_H4' or macd_trend =='BUY_TRAND_D'):
        #             order_Type = '买单'
        #             moderedme = ' MACD处于[多头]趋势当中,当前K线形态为['
        #         elif modec[9] == -100 and (macd_trend == 'SELL_TRAND_H1' or macd_trend == 'SELL_TRAND_H4' or macd_trend == 'SELL_TRAND_D') :
        #             order_Type = '卖单'
        #             moderedme = 'MACD处于[空头]趋势当中，当前K线形态为['
        #         try:
        #             contents.append('<p><strong>货币兑：[' + symbol + ']' + moderedme + order_Type + ']母子线模式</strong></p> '
        #                                                                                          '二日K'
        #                                                                                          '线模式，分多头母子与空头母子，两者相反，以多头母子为例，在下跌趋势中，第一日K线长阴， 第二日开盘价收盘价在第一日价格振幅之内，为阳线，预示趋势反转，股价上升。')
        #             attrfile = generatebar.CandlesstickPng.GenerateBarPng(symbol, run_time)
        #             images.append(attrfile)
        #         except Exception as e:
        #             log.error('发送货币兑：' + symbol + '邮件信息失败！ 当前模式为：母子线' + str(e))
        #
        #     '''
        #     函数名：CDLHARAMICROSS
        #     名称：Harami Cross Pattern 十字孕线
        #     简介：二日K线模式，与母子县类似，若第二日K线是十字线， 便称为十字孕线，预示着趋势反转。
        #     '''
        #     modec = talib.CDLHARAMICROSS(rates_frame.open.values, rates_frame.high.values, rates_frame.low.values,
        #                                  rates_frame.close.values)
        #     if modec[9] == 100 or modec[9] == -100:
        #         if modec[9] == 100 and (macd_trend == 'BUY_TRAND_H1' or macd_trend == 'BUY_TRAND_H4' or macd_trend =='BUY_TRAND_D'):
        #             order_Type = '买单'
        #             moderedme = ' MACD处于[多头]趋势当中,当前K线形态为['
        #         elif modec[9] == -100 and (macd_trend == 'SELL_TRAND_H1' or macd_trend == 'SELL_TRAND_H4' or macd_trend == 'SELL_TRAND_D') :
        #             order_Type = '卖单'
        #             moderedme = 'MACD处于[空头]趋势当中，当前K线形态为['
        #         try:
        #             contents.append('<p><strong>货币兑：[' + symbol + ']' + moderedme + order_Type + ']十字孕线模式</strong></p> '
        #                                                                                          '二日K线模式，与母子县类似，若第二日K线是十字线， '
        #                                                                                          '便称为十字孕线，预示着趋势反转。')
        #             attrfile = generatebar.CandlesstickPng.GenerateBarPng(symbol, run_time)
        #             images.append(attrfile)
        #         except Exception as e:
        #             log.error('发送货币兑：' + symbol + '邮件信息失败！ 当前模式为：十字孕线' + str(e))
        #
        #     '''
        #     函数名：CDLHIGHWAVE
        #     名称：High-Wave Candle 风高浪大线
        #     简介：三日K线模式，具有极长的上/下影线与短的实体，预示着趋势反转。
        #     '''
        #     modec = talib.CDLHIGHWAVE(rates_frame.open.values, rates_frame.high.values, rates_frame.low.values,
        #                               rates_frame.close.values)
        #     if modec[9] == 100 or modec[9] == -100:
        #         if modec[9] == 100 and (macd_trend == 'BUY_TRAND_H1' or macd_trend == 'BUY_TRAND_H4' or macd_trend =='BUY_TRAND_D'):
        #             order_Type = '买单'
        #             moderedme = ' MACD处于[多头]趋势当中,当前K线形态为['
        #         elif modec[9] == -100 and (macd_trend == 'SELL_TRAND_H1' or macd_trend == 'SELL_TRAND_H4' or macd_trend == 'SELL_TRAND_D') :
        #             order_Type = '卖单'
        #             moderedme = 'MACD处于[空头]趋势当中，当前K线形态为['
        #         try:
        #             contents.append(
        #                 '<p><strong>货币兑：[' + symbol + ']' + moderedme + order_Type + ']风高浪大线模式</strong></p>三日K'
        #                                                                              '线模式，具有极长的上/下影线与短的实体，预示着趋势反转。')
        #             attrfile = generatebar.CandlesstickPng.GenerateBarPng(symbol, run_time)
        #             images.append(attrfile)
        #         except Exception as e:
        #             log.error('发送货币兑：' + symbol + '邮件信息失败！ 当前模式为：风高浪大线' + str(e))
        #
        #     '''
        #     函数名：CDLHIKKAKE
        #     名称：Hikkake Pattern 陷阱
        #     简介：三日K线模式，与母子类似，第二日价格在前一日实体范围内, 第三日收盘价高于前两日，反转失败，趋势继续。
        #     '''
        #     # modec=talib.CDLHIKKAKE(rates_frame.open.values,rates_frame.high.values,rates_frame.low.values,rates_frame.close.values)
        #     # if modec[9]!=0:
        #     #     try:
        #     #         contents.append('<p><strong>货币兑：['+symbol+']陷阱模式</strong></p>三日K线模式，与母子类似，第二日价格在前一日实体范围内, 第三日收盘价高于前两日，反转失败，趋势继续。')
        #     #         attrfile =  generatebar.CandlesstickPng.GenerateBarPng(symbol,run_time)
        #     #         images.append(attrfile)
        #     #     except Exception as e:
        #     #         #print("发送邮件失败")
        #     #         log.error('发送货币兑：'+symbol+'邮件信息失败！ 当前模式为：陷阱'+str(e))
        #
        #     '''
        #     函数名：CDLHIKKAKEMOD
        #     名称：Modified Hikkake Pattern 修正陷阱
        #     简介：三日K线模式，与陷阱类似，上升趋势中，第三日跳空高开； 下跌趋势中，第三日跳空低开，反转失败，趋势继续。
        #     '''
        #     modec = talib.CDLHIKKAKEMOD(rates_frame.open.values, rates_frame.high.values, rates_frame.low.values,
        #                                 rates_frame.close.values)
        #     if modec[9] == 100 or modec[9] == -100:
        #         if modec[9] == 100 and (macd_trend == 'BUY_TRAND_H1' or macd_trend == 'BUY_TRAND_H4' or macd_trend =='BUY_TRAND_D'):
        #             order_Type = '买单'
        #             moderedme = ' MACD处于[多头]趋势当中,当前K线形态为['
        #         elif modec[9] == -100 and (macd_trend == 'SELL_TRAND_H1' or macd_trend == 'SELL_TRAND_H4' or macd_trend == 'SELL_TRAND_D') :
        #             order_Type = '卖单'
        #             moderedme = 'MACD处于[空头]趋势当中，当前K线形态为['
        #         try:
        #             contents.append(
        #                 '<p><strong>货币兑：[' + symbol + ']' + moderedme + order_Type + ']修正陷阱模式</strong></p>三日K'
        #                                                                              '线模式，与陷阱类似，上升趋势中，第三日跳空高开； '
        #                                                                              '下跌趋势中，第三日跳空低开，反转失败，趋势继续。')
        #             attrfile = generatebar.CandlesstickPng.GenerateBarPng(symbol, run_time)
        #             images.append(attrfile)
        #         except Exception as e:
        #             log.error('发送货币兑：' + symbol + '邮件信息失败！ 当前模式为：修正陷阱' + str(e))
        #
        #     '''
        #     函数名：CDLHOMINGPIGEON
        #     名称：Homing Pigeon 家鸽
        #     简介：二日K线模式，与母子线类似，不同的的是二日K线颜色相同， 第二日最高价、最低价都在第一日实体之内，预示着趋势反转
        #     '''
        #     modec = talib.CDLHOMINGPIGEON(rates_frame.open.values, rates_frame.high.values, rates_frame.low.values,
        #                                   rates_frame.close.values)
        #     if modec[9] == 100 or modec[9] == -100:
        #         if modec[9] == 100 and (macd_trend == 'BUY_TRAND_H1' or macd_trend == 'BUY_TRAND_H4' or macd_trend =='BUY_TRAND_D'):
        #             order_Type = '买单'
        #             moderedme = ' MACD处于[多头]趋势当中,当前K线形态为['
        #         elif modec[9] == -100 and (macd_trend == 'SELL_TRAND_H1' or macd_trend == 'SELL_TRAND_H4' or macd_trend == 'SELL_TRAND_D') :
        #             order_Type = '卖单'
        #             moderedme = 'MACD处于[空头]趋势当中，当前K线形态为['
        #         try:
        #             contents.append('<p><strong>货币兑：[' + symbol + ']' + moderedme + order_Type + ']家鸽模式</strong></p>二日K'
        #                                                                                          '线模式，与母子线类似，不同的的是二日K线颜色相同， '
        #                                                                                          '第二日最高价、最低价都在第一日实体之内，预示着趋势反转.')
        #             attrfile = generatebar.CandlesstickPng.GenerateBarPng(symbol, run_time)
        #             images.append(attrfile)
        #         except Exception as e:
        #             log.error('发送货币兑：' + symbol + '邮件信息失败！ 当前模式为：家鸽' + str(e))
        #
        #     '''
        #     函数名：CDLIDENTICAL3CROWS
        #     名称：Identical Three Crows 三胞胎乌鸦
        #     简介：三日K线模式，上涨趋势中，三日都为阴线，长度大致相等， 每日开盘价等于前一日收盘价，收盘价接近当日最低价，预示价格下跌。
        #     '''
        #     modec = talib.CDLIDENTICAL3CROWS(rates_frame.open.values, rates_frame.high.values, rates_frame.low.values,
        #                                      rates_frame.close.values)
        #     if modec[9] == 100 or modec[9] == -100:
        #         if modec[9] == 100 and (macd_trend == 'BUY_TRAND_H1' or macd_trend == 'BUY_TRAND_H4' or macd_trend =='BUY_TRAND_D'):
        #             order_Type = '买单'
        #             moderedme = ' MACD处于[多头]趋势当中,当前K线形态为['
        #         elif modec[9] == -100 and (macd_trend == 'SELL_TRAND_H1' or macd_trend == 'SELL_TRAND_H4' or macd_trend == 'SELL_TRAND_D') :
        #             order_Type = '卖单'
        #             moderedme = 'MACD处于[空头]趋势当中，当前K线形态为['
        #         try:
        #             contents.append(
        #                 '<p><strong>货币兑：[' + symbol + ']' + moderedme + order_Type + ']三胞胎乌鸦模式</strong></p>二日K'
        #                                                                              '线模式，上涨趋势中，三日都为阴线，长度大致相等， '
        #                                                                              '每日开盘价等于前一日收盘价，收盘价接近当日最低价，预示价格下跌。')
        #             attrfile = generatebar.CandlesstickPng.GenerateBarPng(symbol, run_time)
        #             images.append(attrfile)
        #         except Exception as e:
        #             log.error('发送货币兑：' + symbol + '邮件信息失败！ 当前模式为：三胞胎乌鸦' + str(e))
        #
        #     '''
        #     函数名：CDLINNECK
        #     名称：In-Neck Pattern 颈内线
        #     简介：二日K线模式，下跌趋势中，第一日长阴线， 第二日开盘价较低，收盘价略高于第一日收盘价，阳线，实体较短，预示着下跌继续
        #     '''
        #     modec = talib.CDLINNECK(rates_frame.open.values, rates_frame.high.values, rates_frame.low.values,
        #                             rates_frame.close.values)
        #     if modec[9] == 100 or modec[9] == -100:
        #         if modec[9] == 100 and (macd_trend == 'BUY_TRAND_H1' or macd_trend == 'BUY_TRAND_H4' or macd_trend =='BUY_TRAND_D'):
        #             order_Type = '买单'
        #             moderedme = ' MACD处于[多头]趋势当中,当前K线形态为['
        #         elif modec[9] == -100 and (macd_trend == 'SELL_TRAND_H1' or macd_trend == 'SELL_TRAND_H4' or macd_trend == 'SELL_TRAND_D') :
        #             order_Type = '卖单'
        #             moderedme = 'MACD处于[空头]趋势当中，当前K线形态为['
        #         try:
        #             contents.append(
        #                 '<p><strong>货币兑：[' + symbol + ']' + moderedme + order_Type + ']二日K线模式</strong></p>下跌趋势中，第一日长阴线， 第二日开盘价较低，收盘价略高于第一日收盘价，阳线，实体较短，预示着下跌继续.')
        #             attrfile = generatebar.CandlesstickPng.GenerateBarPng(symbol, run_time)
        #             images.append(attrfile)
        #         except Exception as e:
        #             log.error('发送货币兑：' + symbol + '邮件信息失败！ 当前模式为：颈内线' + str(e))
        #
        #     '''
        #     函数名：CDLINVERTEDHAMMER
        #     名称：Inverted Hammer 倒锤头
        #     简介：一日K线模式，上影线较长，长度为实体2倍以上， 无下影线，在下跌趋势底部，预示着趋势反转。
        #     '''
        #     modec = talib.CDLINVERTEDHAMMER(rates_frame.open.values, rates_frame.high.values, rates_frame.low.values,
        #                                     rates_frame.close.values)
        #     if modec[9] == 100 or modec[9] == -100:
        #         if modec[9] == 100 and (macd_trend == 'BUY_TRAND_H1' or macd_trend == 'BUY_TRAND_H4' or macd_trend =='BUY_TRAND_D'):
        #             order_Type = '买单'
        #             moderedme = ' MACD处于[多头]趋势当中,当前K线形态为['
        #         elif modec[9] == -100 and (macd_trend == 'SELL_TRAND_H1' or macd_trend == 'SELL_TRAND_H4' or macd_trend == 'SELL_TRAND_D') :
        #             order_Type = '卖单'
        #             moderedme = 'MACD处于[空头]趋势当中，当前K线形态为['
        #         try:
        #             contents.append(
        #                 '<p><strong>货币兑：[' + symbol + ']' + moderedme + order_Type + ']倒锤头模式</strong></p>一日K线模式，上影线较长，长度为实体2倍以上， 无下影线，在下跌趋势底部，预示着趋势反转。')
        #             attrfile = generatebar.CandlesstickPng.GenerateBarPng(symbol, run_time)
        #             images.append(attrfile)
        #         except Exception as e:
        #             log.error('发送货币兑：' + symbol + '邮件信息失败！ 当前模式为：倒锤头' + str(e))
        #
        #     '''
        #     函数名：CDLKICKING
        #     名称：Kicking 反冲形态
        #     简介：二日K线模式，与分离线类似，两日K线为秃线，颜色相反，存在跳空缺口。
        #     '''
        #     modec = talib.CDLKICKING(rates_frame.open.values, rates_frame.high.values, rates_frame.low.values,
        #                              rates_frame.close.values)
        #     if modec[9] == 100 or modec[9] == -100:
        #         if modec[9] == 100 and (macd_trend == 'BUY_TRAND_H1' or macd_trend == 'BUY_TRAND_H4' or macd_trend =='BUY_TRAND_D'):
        #             order_Type = '买单'
        #             moderedme = ' MACD处于[多头]趋势当中,当前K线形态为['
        #         elif modec[9] == -100 and (macd_trend == 'SELL_TRAND_H1' or macd_trend == 'SELL_TRAND_H4' or macd_trend == 'SELL_TRAND_D') :
        #             order_Type = '卖单'
        #             moderedme = 'MACD处于[空头]趋势当中，当前K线形态为['
        #         try:
        #             contents.append(
        #                 '<p><strong>货币兑：[' + symbol + ']' + moderedme + order_Type + ']反冲形态模式</strong></p>二日K线模式，与分离线类似，两日K线为秃线，颜色相反，存在跳空缺口。')
        #             attrfile = generatebar.CandlesstickPng.GenerateBarPng(symbol, run_time)
        #             images.append(attrfile)
        #         except Exception as e:
        #             log.error('发送货币兑：' + symbol + '邮件信息失败！ 当前模式为：反冲形态' + str(e))
        #
        #     '''
        #     函数名：CDLKICKINGBYLENGTH
        #     名称：Kicking - bull/bear determined by the longer marubozu 由较长缺影线决定的反冲形态
        #     简介：二日K线模式，与反冲形态类似，较长缺影线决定价格的涨跌
        #     '''
        #     modec = talib.CDLKICKINGBYLENGTH(rates_frame.open.values, rates_frame.high.values, rates_frame.low.values,
        #                                      rates_frame.close.values)
        #     if modec[9] == 100 or modec[9] == -100:
        #         if modec[9] == 100 and (macd_trend == 'BUY_TRAND_H1' or macd_trend == 'BUY_TRAND_H4' or macd_trend =='BUY_TRAND_D'):
        #             order_Type = '买单'
        #             moderedme = ' MACD处于[多头]趋势当中,当前K线形态为['
        #         elif modec[9] == -100 and (macd_trend == 'SELL_TRAND_H1' or macd_trend == 'SELL_TRAND_H4' or macd_trend == 'SELL_TRAND_D') :
        #             order_Type = '卖单'
        #             moderedme = 'MACD处于[空头]趋势当中，当前K线形态为['
        #         try:
        #             contents.append(
        #                 '<p><strong>货币兑：[' + symbol + ']' + moderedme + order_Type + ']较长缺影线决定的反冲形态模式</strong></p>二日K线模式，与反冲形态类似，较长缺影线决定价格的涨跌。')
        #             attrfile = generatebar.CandlesstickPng.GenerateBarPng(symbol, run_time)
        #             images.append(attrfile)
        #         except Exception as e:
        #             log.error('发送货币兑：' + symbol + '邮件信息成功！ 当前模失败：由较长缺影线决定的反冲形态' + str(e))
        #
        #     '''
        #     函数名：CDLLADDERBOTTOM
        #     名称：Ladder Bottom 梯底
        #     简介：五日K线模式，下跌趋势中，前三日阴线， 开盘价与收盘价皆低于前一日开盘、收盘价，第四日倒锤头，第五日开盘价高于前一日开盘价， 阳线，收盘价高于前几日价格振幅，预示着底部反转。
        #     '''
        #     modec = talib.CDLLADDERBOTTOM(rates_frame.open.values, rates_frame.high.values, rates_frame.low.values,
        #                                   rates_frame.close.values)
        #     if modec[9] == 100 or modec[9] == -100:
        #         if modec[9] == 100 and (macd_trend == 'BUY_TRAND_H1' or macd_trend == 'BUY_TRAND_H4' or macd_trend =='BUY_TRAND_D'):
        #             order_Type = '买单'
        #             moderedme = ' MACD处于[多头]趋势当中,当前K线形态为['
        #         elif modec[9] == -100 and (macd_trend == 'SELL_TRAND_H1' or macd_trend == 'SELL_TRAND_H4' or macd_trend == 'SELL_TRAND_D') :
        #             order_Type = '卖单'
        #             moderedme = 'MACD处于[空头]趋势当中，当前K线形态为['
        #         try:
        #             contents.append(
        #                 '<p><strong>货币兑：[' + symbol + ']' + moderedme + order_Type + ']梯底模式</strong></p>五日K线模式，下跌趋势中，前三日阴线， 开盘价与收盘价皆低于前一日开盘、收盘价，第四日倒锤头，第五日开盘价高于前一日开盘价， 阳线，收盘价高于前几日价格振幅，预示着底部反转。')
        #             attrfile = generatebar.CandlesstickPng.GenerateBarPng(symbol, run_time)
        #             images.append(attrfile)
        #         except Exception as e:
        #             log.error('发送货币兑：' + symbol + '邮件信息失败！ 当前模式为：梯底' + str(e))
        #
        #     '''
        #     函数名：CDLLONGLEGGEDDOJI
        #     名称：Long Legged Doji 长脚十字
        #     简介：一日K线模式，开盘价与收盘价相同居当日价格中部，上下影线长， 表达市场不确定性。
        #     '''
        #     modec = talib.CDLLONGLEGGEDDOJI(rates_frame.open.values, rates_frame.high.values, rates_frame.low.values,
        #                                     rates_frame.close.values)
        #     if modec[9] == 100 or modec[9] == -100:
        #         if modec[9] == 100 and (macd_trend == 'BUY_TRAND_H1' or macd_trend == 'BUY_TRAND_H4' or macd_trend =='BUY_TRAND_D'):
        #             order_Type = '买单'
        #             moderedme = ' MACD处于[多头]趋势当中,当前K线形态为['
        #         elif modec[9] == -100 and (macd_trend == 'SELL_TRAND_H1' or macd_trend == 'SELL_TRAND_H4' or macd_trend == 'SELL_TRAND_D') :
        #             order_Type = '卖单'
        #             moderedme = 'MACD处于[空头]趋势当中，当前K线形态为['
        #         try:
        #             contents.append(
        #                 '<p><strong>货币兑：[' + symbol + ']' + moderedme + order_Type + ']长脚十字模式</strong></p> 一日K线模式，开盘价与收盘价相同居当日价格中部，上下影线长， 表达市场不确定性。')
        #             attrfile = generatebar.CandlesstickPng.GenerateBarPng(symbol, run_time)
        #             images.append(attrfile)
        #         except Exception as e:
        #             log.error('发送货币兑：' + symbol + '邮件信息失败！ 当前模式为：长脚十字' + str(e))
        #
        #     '''
        #     函数名：CDLLONGLINE
        #     名称：Long Line Candle 长蜡烛
        #     简介：一日K线模式，K线实体长，无上下影线。
        #     '''
        #     modec = talib.CDLLONGLINE(rates_frame.open.values, rates_frame.high.values, rates_frame.low.values,
        #                               rates_frame.close.values)
        #     if modec[9] == 100 or modec[9] == -100:
        #         if modec[9] == 100 and (macd_trend == 'BUY_TRAND_H1' or macd_trend == 'BUY_TRAND_H4' or macd_trend =='BUY_TRAND_D'):
        #             order_Type = '买单'
        #             moderedme = ' MACD处于[多头]趋势当中,当前K线形态为['
        #         elif modec[9] == -100 and (macd_trend == 'SELL_TRAND_H1' or macd_trend == 'SELL_TRAND_H4' or macd_trend == 'SELL_TRAND_D') :
        #             order_Type = '卖单'
        #             moderedme = 'MACD处于[空头]趋势当中，当前K线形态为['
        #         try:
        #             contents.append(
        #                 '<p><strong>货币兑：[' + symbol + ']' + moderedme + order_Type + ']长蜡烛模式</strong></p>一日K线模式，K线实体长，无上下影线。')
        #             attrfile = generatebar.CandlesstickPng.GenerateBarPng(symbol, run_time)
        #             images.append(attrfile)
        #         except Exception as e:
        #             log.error('发送货币兑：' + symbol + '邮件信息失败！ 当前模式为：长蜡烛' + str(e))
        #
        #     '''
        #     函数名：CDLMARUBOZU
        #     名称：Marubozu 光头光脚/缺影线
        #     简介：一日K线模式，上下两头都没有影线的实体， 阴线预示着熊市持续或者牛市反转，阳线相反。
        #     '''
        #     modec = talib.CDLMARUBOZU(rates_frame.open.values, rates_frame.high.values, rates_frame.low.values,
        #                               rates_frame.close.values)
        #     if modec[9] == 100 or modec[9] == -100:
        #         if modec[9] == 100 and (macd_trend == 'BUY_TRAND_H1' or macd_trend == 'BUY_TRAND_H4' or macd_trend =='BUY_TRAND_D'):
        #             order_Type = '买单'
        #             moderedme = ' MACD处于[多头]趋势当中,当前K线形态为['
        #         elif modec[9] == -100 and (macd_trend == 'SELL_TRAND_H1' or macd_trend == 'SELL_TRAND_H4' or macd_trend == 'SELL_TRAND_D') :
        #             order_Type = '卖单'
        #             moderedme = 'MACD处于[空头]趋势当中，当前K线形态为['
        #         try:
        #             contents.append(
        #                 '<p><strong>货币兑：[' + symbol + ']' + moderedme + order_Type + ']光头光脚/缺影线模式</strong></p> 一日K线模式，上下两头都没有影线的实体， 阴线预示着熊市持续或者牛市反转，阳线相反。')
        #             attrfile = generatebar.CandlesstickPng.GenerateBarPng(symbol, run_time)
        #             images.append(attrfile)
        #         except Exception as e:
        #             log.error('发送货币兑：' + symbol + '邮件信息失败！ 当前模式为：光头光脚/缺影线' + str(e))
        #
        #     '''
        #     函数名：CDLMATCHINGLOW
        #     名称：Matching Low 相同低价
        #     简介：二日K线模式，下跌趋势中，第一日长阴线， 第二日阴线，收盘价与前一日相同，预示底部确认，该价格为支撑位。
        #     '''
        #     modec = talib.CDLMATCHINGLOW(rates_frame.open.values, rates_frame.high.values, rates_frame.low.values,
        #                                  rates_frame.close.values)
        #     if modec[9] == 100 or modec[9] == -100:
        #         if modec[9] == 100 and (macd_trend == 'BUY_TRAND_H1' or macd_trend == 'BUY_TRAND_H4' or macd_trend =='BUY_TRAND_D'):
        #             order_Type = '买单'
        #             moderedme = ' MACD处于[多头]趋势当中,当前K线形态为['
        #         elif modec[9] == -100 and (macd_trend == 'SELL_TRAND_H1' or macd_trend == 'SELL_TRAND_H4' or macd_trend == 'SELL_TRAND_D') :
        #             order_Type = '卖单'
        #             moderedme = 'MACD处于[空头]趋势当中，当前K线形态为['
        #         try:
        #             contents.append(
        #                 '<p><strong>货币兑：[' + symbol + ']' + moderedme + order_Type + ']相同低价模式</strong></p> 二日K线模式下跌趋势中，第一日长阴线， 第二日阴线，收盘价与前一日相同，预示底部确认，该价格为支撑位。')
        #             attrfile = generatebar.CandlesstickPng.GenerateBarPng(symbol, run_time)
        #             images.append(attrfile)
        #         except Exception as e:
        #             log.error('发送货币兑：' + symbol + '邮件信息失败！ 当前模式为：相同低价' + str(e))
        #
        #     '''
        #     函数名：CDLMATHOLD
        #     名称：Mat Hold 铺垫
        #     简介：五日K线模式，上涨趋势中，第一日阳线，第二日跳空高开影线， 第三、四日短实体影线，第五日阳线，收盘价高于前四日，预示趋势持续。
        #     '''
        #     modec = talib.CDLMATHOLD(rates_frame.open.values, rates_frame.high.values, rates_frame.low.values,
        #                              rates_frame.close.values, penetration=0)
        #     if modec[9] == 100 or modec[9] == -100:
        #         if modec[9] == 100 and (macd_trend == 'BUY_TRAND_H1' or macd_trend == 'BUY_TRAND_H4' or macd_trend =='BUY_TRAND_D'):
        #             order_Type = '买单'
        #             moderedme = ' MACD处于[多头]趋势当中,当前K线形态为['
        #         elif modec[9] == -100 and (macd_trend == 'SELL_TRAND_H1' or macd_trend == 'SELL_TRAND_H4' or macd_trend == 'SELL_TRAND_D') :
        #             order_Type = '卖单'
        #             moderedme = 'MACD处于[空头]趋势当中，当前K线形态为['
        #         try:
        #             contents.append(
        #                 '<p><strong>货币兑：[' + symbol + ']' + moderedme + order_Type + ']铺垫模式</p></strong>五日K线模式，上涨趋势中，第一日阳线，第二日跳空高开影线， 第三、四日短实体影线，第五日阳线，收盘价高于前四日，预示趋势持续。')
        #             attrfile = generatebar.CandlesstickPng.GenerateBarPng(symbol, run_time)
        #             images.append(attrfile)
        #         except Exception as e:
        #             log.error('发送货币兑：' + symbol + '邮件信息失败！ 当前模式为：铺垫' + str(e))
        #
        #     '''
        #     函数名：CDLMORNINGDOJISTAR
        #     名称：Morning Doji Star 十字晨星
        #     简介：三日K线模式， 基本模式为晨星，第二日K线为十字星，预示底部反转。
        #     '''
        #     modec = talib.CDLMORNINGDOJISTAR(rates_frame.open.values, rates_frame.high.values, rates_frame.low.values,
        #                                      rates_frame.close.values, penetration=0)
        #     if modec[9] == 100 or modec[9] == -100:
        #         if modec[9] == 100 and (macd_trend == 'BUY_TRAND_H1' or macd_trend == 'BUY_TRAND_H4' or macd_trend =='BUY_TRAND_D'):
        #             order_Type = '买单'
        #             moderedme = ' MACD处于[多头]趋势当中,当前K线形态为['
        #         elif modec[9] == -100 and (macd_trend == 'SELL_TRAND_H1' or macd_trend == 'SELL_TRAND_H4' or macd_trend == 'SELL_TRAND_D') :
        #             order_Type = '卖单'
        #             moderedme = 'MACD处于[空头]趋势当中，当前K线形态为['
        #         try:
        #             contents.append(
        #                 '<p><strong>货币兑：[' + symbol + ']' + moderedme + order_Type + ']十字晨星模式</strong></p>三日K线模式， 基本模式为晨星，第二日K线为十字星，预示底部反转。')
        #             attrfile = generatebar.CandlesstickPng.GenerateBarPng(symbol, run_time)
        #             images.append(attrfile)
        #         except Exception as e:
        #             log.error('发送货币兑：' + symbol + '邮件信息失败！ 当前模式为：十字晨星' + str(e))
        #
        #     '''
        #     函数名：CDLMORNINGSTAR
        #     名称：Morning Star 晨星
        #     简介：三日K线模式，下跌趋势，第一日阴线， 第二日价格振幅较小，第三天阳线，预示底部反转。
        #     '''
        #     modec = talib.CDLMORNINGSTAR(rates_frame.open.values, rates_frame.high.values, rates_frame.low.values,
        #                                  rates_frame.close.values, penetration=0)
        #     if modec[9] == 100 or modec[9] == -100:
        #         if modec[9] == 100 and (macd_trend == 'BUY_TRAND_H1' or macd_trend == 'BUY_TRAND_H4' or macd_trend =='BUY_TRAND_D'):
        #             order_Type = '买单'
        #             moderedme = ' MACD处于[多头]趋势当中,当前K线形态为['
        #         elif modec[9] == -100 and (macd_trend == 'SELL_TRAND_H1' or macd_trend == 'SELL_TRAND_H4' or macd_trend == 'SELL_TRAND_D') :
        #             order_Type = '卖单'
        #             moderedme = 'MACD处于[空头]趋势当中，当前K线形态为['
        #         try:
        #             contents.append(
        #                 '<p><strong>货币兑：[' + symbol + ']' + moderedme + order_Type + ']晨星模式</strong></p>三日K线模式， 基本模式为晨星，第二日K线为十字星，预示底部反转。')
        #             attrfile = generatebar.CandlesstickPng.GenerateBarPng(symbol, run_time)
        #             images.append(attrfile)
        #         except Exception as e:
        #             log.error('发送货币兑：' + symbol + '邮件信息失败！ 当前模式为：晨星' + str(e))
        #
        #     '''
        #     函数名：CDLONNECK
        #     名称：On-Neck Pattern 颈上线
        #     简介：二日K线模式，下跌趋势中，第一日长阴线，第二日开盘价较低， 收盘价与前一日最低价相同，阳线，实体较短，预示着延续下跌趋势。
        #     '''
        #     modec = talib.CDLONNECK(rates_frame.open.values, rates_frame.high.values, rates_frame.low.values,
        #                             rates_frame.close.values)
        #     if modec[9] == 100 or modec[9] == -100:
        #         if modec[9] == 100 and (macd_trend == 'BUY_TRAND_H1' or macd_trend == 'BUY_TRAND_H4' or macd_trend =='BUY_TRAND_D'):
        #             order_Type = '买单'
        #             moderedme = ' MACD处于[多头]趋势当中,当前K线形态为['
        #         elif modec[9] == -100 and (macd_trend == 'SELL_TRAND_H1' or macd_trend == 'SELL_TRAND_H4' or macd_trend == 'SELL_TRAND_D') :
        #             order_Type = '卖单'
        #             moderedme = 'MACD处于[空头]趋势当中，当前K线形态为['
        #         try:
        #             contents.append(
        #                 '<p><strong>货币兑：[' + symbol + ']' + moderedme + order_Type + ']颈上线模式</strong><p>二日K线模式，下跌趋势中，第一日长阴线，第二日开盘价较低， 收盘价与前一日最低价相同，阳线，实体较短，预示着延续下跌趋势。')
        #             attrfile = generatebar.CandlesstickPng.GenerateBarPng(symbol, run_time)
        #             images.append(attrfile)
        #         except Exception as e:
        #             log.error('发送货币兑：' + symbol + '邮件信息失败！ 当前模式为：颈上线' + str(e))
        #
        #     '''
        #     函数名：CDLPIERCING
        #     名称：Piercing Pattern 刺透形态
        #     简介：两日K线模式，下跌趋势中，第一日阴线，第二日收盘价低于前一日最低价， 收盘价处在第一日实体上部，预示着底部反转。
        #     '''
        #     modec = talib.CDLPIERCING(rates_frame.open.values, rates_frame.high.values, rates_frame.low.values,
        #                               rates_frame.close.values)
        #     if modec[9] == 100 or modec[9] == -100:
        #         if modec[9] == 100 and (macd_trend == 'BUY_TRAND_H1' or macd_trend == 'BUY_TRAND_H4' or macd_trend =='BUY_TRAND_D'):
        #             order_Type = '买单'
        #             moderedme = ' MACD处于[多头]趋势当中,当前K线形态为['
        #         elif modec[9] == -100 and (macd_trend == 'SELL_TRAND_H1' or macd_trend == 'SELL_TRAND_H4' or macd_trend == 'SELL_TRAND_D') :
        #             order_Type = '卖单'
        #             moderedme = 'MACD处于[空头]趋势当中，当前K线形态为['
        #         try:
        #             contents.append(
        #                 '<p><strong>货币兑：[' + symbol + ']' + moderedme + order_Type + ']刺透形态模式</strong></p>两日K线模式，下跌趋势中，第一日阴线，第二日收盘价低于前一日最低价， 收盘价处在第一日实体上部，预示着底部反转。')
        #             attrfile = generatebar.CandlesstickPng.GenerateBarPng(symbol, run_time)
        #             images.append(attrfile)
        #         except Exception as e:
        #             log.error('发送货币兑：' + symbol + '邮件信息失败！ 当前模式为：刺透形态' + str(e))
        #
        #     '''
        #     函数名：CDLRICKSHAWMAN
        #     名称：Rickshaw Man 黄包车夫
        #     简介：一日K线模式，与长腿十字线类似， 若实体正好处于价格振幅中点，称为黄包车夫。
        #     '''
        #     modec = talib.CDLRICKSHAWMAN(rates_frame.open.values, rates_frame.high.values, rates_frame.low.values,
        #                                  rates_frame.close.values)
        #     if modec[9] == 100 or modec[9] == -100:
        #         if modec[9] == 100 and (macd_trend == 'BUY_TRAND_H1' or macd_trend == 'BUY_TRAND_H4' or macd_trend =='BUY_TRAND_D'):
        #             order_Type = '买单'
        #             moderedme = ' MACD处于[多头]趋势当中,当前K线形态为['
        #         elif modec[9] == -100 and (macd_trend == 'SELL_TRAND_H1' or macd_trend == 'SELL_TRAND_H4' or macd_trend == 'SELL_TRAND_D') :
        #             order_Type = '卖单'
        #             moderedme = 'MACD处于[空头]趋势当中，当前K线形态为['
        #         try:
        #             contents.append(
        #                 '<p><strong>货币兑：[' + symbol + ']' + moderedme + order_Type + ']黄包车夫模式</strong></p>一日K线模式，与长腿十字线类似， 若实体正好处于价格振幅中点，称为黄包车夫。')
        #             attrfile = generatebar.CandlesstickPng.GenerateBarPng(symbol, run_time)
        #             images.append(attrfile)
        #         except Exception as e:
        #             log.error('发送货币兑：' + symbol + '邮件信息失败！ 当前模式为：黄包车夫' + str(e))
        #
        #     '''
        #     函数名：CDLRISEFALL3METHODS 名称：Rising/Falling Three Methods 上升/下降三法
        #     简介： 五日K线模式，以上升三法为例，上涨趋势中， 第一日长阳线，中间三日价格在第一日范围内小幅震荡， 第五日长阳线，收盘价高于第一日收盘价，预示股价上升。
        #     '''
        #     modec = talib.CDLRISEFALL3METHODS(rates_frame.open.values, rates_frame.high.values, rates_frame.low.values,
        #                                       rates_frame.close.values)
        #     if modec[9] == 100 or modec[9] == -100:
        #         if modec[9] == 100 and (macd_trend == 'BUY_TRAND_H1' or macd_trend == 'BUY_TRAND_H4' or macd_trend =='BUY_TRAND_D'):
        #             order_Type = '买单'
        #             moderedme = ' MACD处于[多头]趋势当中,当前K线形态为['
        #         elif modec[9] == -100 and (macd_trend == 'SELL_TRAND_H1' or macd_trend == 'SELL_TRAND_H4' or macd_trend == 'SELL_TRAND_D') :
        #             order_Type = '卖单'
        #             moderedme = 'MACD处于[空头]趋势当中，当前K线形态为['
        #         try:
        #             contents.append(
        #                 '<p><strong>货币兑：[' + symbol + ']' + moderedme + order_Type + ']上升/下降三法模式</strong></p>五日K线模式，以上升三法为例，上涨趋势中， 第一日长阳线，中间三日价格在第一日范围内小幅震荡， 第五日长阳线，收盘价高于第一日收盘价，预示股价上升。')
        #             attrfile = generatebar.CandlesstickPng.GenerateBarPng(symbol, run_time)
        #             images.append(attrfile)
        #         except Exception as e:
        #             log.error('发送货币兑：' + symbol + '邮件信息失败！ 当前模式为：上升/下降三法' + str(e))
        #
        #     '''
        #     函数名：CDLSEPARATINGLINES
        #     名称：Separating Lines 分离线
        #     简介：二日K线模式，上涨趋势中，第一日阴线，第二日阳线， 第二日开盘价与第一日相同且为最低价，预示着趋势继续。
        #     '''
        #     modec = talib.CDLSEPARATINGLINES(rates_frame.open.values, rates_frame.high.values, rates_frame.low.values,
        #                                      rates_frame.close.values)
        #     if modec[9] == 100 or modec[9] == -100:
        #         if modec[9] == 100 and (macd_trend == 'BUY_TRAND_H1' or macd_trend == 'BUY_TRAND_H4' or macd_trend =='BUY_TRAND_D'):
        #             order_Type = '买单'
        #             moderedme = ' MACD处于[多头]趋势当中,当前K线形态为['
        #         elif modec[9] == -100 and (macd_trend == 'SELL_TRAND_H1' or macd_trend == 'SELL_TRAND_H4' or macd_trend == 'SELL_TRAND_D') :
        #             order_Type = '卖单'
        #             moderedme = 'MACD处于[空头]趋势当中，当前K线形态为['
        #         try:
        #             contents.append(
        #                 '<p><strong>货币兑：[' + symbol + ']' + moderedme + order_Type + ']分离线模式</strong></p>二日K线模式，上涨趋势中，第一日阴线，第二日阳线， 第二日开盘价与第一日相同且为最低价，预示着趋势继续。')
        #             attrfile = generatebar.CandlesstickPng.GenerateBarPng(symbol, run_time)
        #             images.append(attrfile)
        #         except Exception as e:
        #             log.error('发送货币兑：' + symbol + '邮件信息失败！ 当前模式为：分离线' + str(e))
        #
        #     '''
        #     函数名：CDLSHOOTINGSTAR
        #     名称：Shooting Star 射击之星
        #     简介：一日K线模式，上影线至少为实体长度两倍， 没有下影线，预示着股价下跌
        #     '''
        #     modec = talib.CDLSHOOTINGSTAR(rates_frame.open.values, rates_frame.high.values, rates_frame.low.values,
        #                                   rates_frame.close.values)
        #     if modec[9] == 100 or modec[9] == -100:
        #         if modec[9] == 100 and (macd_trend == 'BUY_TRAND_H1' or macd_trend == 'BUY_TRAND_H4' or macd_trend =='BUY_TRAND_D'):
        #             order_Type = '买单'
        #             moderedme = ' MACD处于[多头]趋势当中,当前K线形态为['
        #         elif modec[9] == -100 and (macd_trend == 'SELL_TRAND_H1' or macd_trend == 'SELL_TRAND_H4' or macd_trend == 'SELL_TRAND_D') :
        #             order_Type = '卖单'
        #             moderedme = 'MACD处于[空头]趋势当中，当前K线形态为['
        #         try:
        #             contents.append(
        #                 '<p><strong>货币兑：[' + symbol + ']' + moderedme + order_Type + ']射击之星</strong></p>一日K线模式，上影线至少为实体长度两倍， 没有下影线，预示着股价下跌。')
        #             attrfile = generatebar.CandlesstickPng.GenerateBarPng(symbol, run_time)
        #             images.append(attrfile)
        #         except Exception as e:
        #             log.error('发送货币兑：' + symbol + '邮件信息失败！ 当前模式为：射击之星' + str(e))
        #
        #     '''
        #     函数名：CDLSHORTLINE
        #     名称：Short Line Candle 短蜡烛
        #     简介：一日K线模式，实体短，无上下影线
        #     '''
        #     modec = talib.CDLSHORTLINE(rates_frame.open.values, rates_frame.high.values, rates_frame.low.values,
        #                                rates_frame.close.values)
        #     if modec[9] == 100 or modec[9] == -100:
        #         if modec[9] == 100 and (macd_trend == 'BUY_TRAND_H1' or macd_trend == 'BUY_TRAND_H4' or macd_trend =='BUY_TRAND_D'):
        #             order_Type = '买单'
        #             moderedme = ' MACD处于[多头]趋势当中,当前K线形态为['
        #         elif modec[9] == -100 and (macd_trend == 'SELL_TRAND_H1' or macd_trend == 'SELL_TRAND_H4' or macd_trend == 'SELL_TRAND_D') :
        #             order_Type = '卖单'
        #             moderedme = 'MACD处于[空头]趋势当中，当前K线形态为['
        #         try:
        #             contents.append(
        #                 '<p><strong>货币兑：[' + symbol + ']' + moderedme + order_Type + ']短蜡烛模式</strong></p>一日K线模式，实体短，无上下影线。')
        #             attrfile = generatebar.CandlesstickPng.GenerateBarPng(symbol, run_time)
        #             images.append(attrfile)
        #         except Exception as e:
        #             log.error('发送货币兑：' + symbol + '邮件信息失败！ 当前模式为：短蜡烛' + str(e))
        #
        #     '''
        #     函数名：CDLSPINNINGTOP
        #     名称：Spinning Top 纺锤
        #     简介：一日K线，实体小。
        #     '''
        #     modec = talib.CDLSPINNINGTOP(rates_frame.open.values, rates_frame.high.values, rates_frame.low.values,
        #                                  rates_frame.close.values)
        #     if modec[9] == 100 or modec[9] == -100:
        #         if modec[9] == 100 and (macd_trend == 'BUY_TRAND_H1' or macd_trend == 'BUY_TRAND_H4' or macd_trend =='BUY_TRAND_D'):
        #             order_Type = '买单'
        #             moderedme = ' MACD处于[多头]趋势当中,当前K线形态为['
        #         elif modec[9] == -100 and (macd_trend == 'SELL_TRAND_H1' or macd_trend == 'SELL_TRAND_H4' or macd_trend == 'SELL_TRAND_D') :
        #             order_Type = '卖单'
        #             moderedme = 'MACD处于[空头]趋势当中，当前K线形态为['
        #         try:
        #             contents.append(
        #                 '<p><strong>货币兑：[' + symbol + ']' + moderedme + order_Type + ']纺锤模式</strong></p>一日K线，实体小。')
        #             attrfile = generatebar.CandlesstickPng.GenerateBarPng(symbol, run_time)
        #             images.append(attrfile)
        #         except Exception as e:
        #             log.error('发送货币兑：' + symbol + '邮件信息失败！ 当前模式为：纺锤' + str(e))
        #
        #     '''
        #     函数名：CDLSTALLEDPATTERN
        #     名称：Stalled Pattern 停顿形态
        #     简介：三日K线模式，上涨趋势中，第二日长阳线， 第三日开盘于前一日收盘价附近，短阳线，预示着上涨结束
        #     '''
        #     modec = talib.CDLSTALLEDPATTERN(rates_frame.open.values, rates_frame.high.values, rates_frame.low.values,
        #                                     rates_frame.close.values)
        #     if modec[9] == 100 or modec[9] == -100:
        #         if modec[9] == 100 and (macd_trend == 'BUY_TRAND_H1' or macd_trend == 'BUY_TRAND_H4' or macd_trend =='BUY_TRAND_D'):
        #             order_Type = '买单'
        #             moderedme = ' MACD处于[多头]趋势当中,当前K线形态为['
        #         elif modec[9] == -100 and (macd_trend == 'SELL_TRAND_H1' or macd_trend == 'SELL_TRAND_H4' or macd_trend == 'SELL_TRAND_D') :
        #             order_Type = '卖单'
        #             moderedme = 'MACD处于[空头]趋势当中，当前K线形态为['
        #         try:
        #             contents.append(
        #                 '<p><strong>货币兑：[' + symbol + ']' + moderedme + order_Type + ']停顿形态模式</strong></p>三日K线模式，上涨趋势中，第二日长阳线， 第三日开盘于前一日收盘价附近，短阳线，预示着上涨结束。')
        #             attrfile = generatebar.CandlesstickPng.GenerateBarPng(symbol, run_time)
        #             images.append(attrfile)
        #         except Exception as e:
        #             log.error('发送货币兑：' + symbol + '邮件信息失败！ 当前模式为：停顿形态' + str(e))
        #
        #     '''
        #     函数名：CDLSTICKSANDWICH
        #     名称：Stick Sandwich 条形三明治
        #     简介：三日K线模式，第一日长阴线，第二日阳线，开盘价高于前一日收盘价， 第三日开盘价高于前两日最高价，收盘价于第一日收盘价相
        #     '''
        #     modec = talib.CDLSTICKSANDWICH(rates_frame.open.values, rates_frame.high.values, rates_frame.low.values,
        #                                    rates_frame.close.values)
        #     if modec[9] == 100 or modec[9] == -100:
        #         if modec[9] == 100 and (macd_trend == 'BUY_TRAND_H1' or macd_trend == 'BUY_TRAND_H4' or macd_trend =='BUY_TRAND_D'):
        #             order_Type = '买单'
        #             moderedme = ' MACD处于[多头]趋势当中,当前K线形态为['
        #         elif modec[9] == -100 and (macd_trend == 'SELL_TRAND_H1' or macd_trend == 'SELL_TRAND_H4' or macd_trend == 'SELL_TRAND_D') :
        #             order_Type = '卖单'
        #             moderedme = 'MACD处于[空头]趋势当中，当前K线形态为['
        #         try:
        #             contents.append(
        #                 '<p><strong>货币兑：[' + symbol + ']' + moderedme + order_Type + ']条形三明治模式</strong></p>日K线模式，第一日长阴线，第二日阳线，开盘价高于前一日收盘价， 第三日开盘价高于前两日最高价，收盘价于第一日收盘价相。')
        #             attrfile = generatebar.CandlesstickPng.GenerateBarPng(symbol, run_time)
        #             images.append(attrfile)
        #         except Exception as e:
        #             # print("发送邮件失败");
        #             log.error('发送货币兑：' + symbol + '邮件信息失败！ 当前模式为：条形三明治' + str(e))
        #
        #     '''
        #     函数名：CDLTAKURI
        #     名称：Takuri (Dragonfly Doji with very long lower shadow) 探水竿
        #     简介：一日K线模式，大致与蜻蜓十字相同，下影线长度长。
        #     '''
        #     modec = talib.CDLTAKURI(rates_frame.open.values, rates_frame.high.values, rates_frame.low.values,
        #                             rates_frame.close.values)
        #     if modec[9] == 100 or modec[9] == -100:
        #         if modec[9] == 100 and (macd_trend == 'BUY_TRAND_H1' or macd_trend == 'BUY_TRAND_H4' or macd_trend =='BUY_TRAND_D'):
        #             order_Type = '买单'
        #             moderedme = ' MACD处于[多头]趋势当中,当前K线形态为['
        #         elif modec[9] == -100 and (macd_trend == 'SELL_TRAND_H1' or macd_trend == 'SELL_TRAND_H4' or macd_trend == 'SELL_TRAND_D') :
        #             order_Type = '卖单'
        #             moderedme = 'MACD处于[空头]趋势当中，当前K线形态为['
        #         try:
        #             contents.append(
        #                 '<p><strong>货币兑：[' + symbol + ']' + moderedme + order_Type + ']探水竿模式</strong></p>一日K线模式，大致与蜻蜓十字相同，下影线长度长。')
        #             attrfile = generatebar.CandlesstickPng.GenerateBarPng(symbol, run_time)
        #             images.append(attrfile)
        #         except Exception as e:
        #             log.error('发送货币兑：' + symbol + '邮件信息失败！ 当前模式为：探水竿' + str(e))
        #
        #     '''
        #     函数名：CDLTASUKIGAP
        #     名称：Tasuki Gap 跳空并列阴阳线
        #     简介：三日K线模式，分上涨和下跌，以上升为例， 前两日阳线，第二日跳空，第三日阴线，收盘价于缺口中，上升趋势持续。
        #     '''
        #     modec = talib.CDLTASUKIGAP(rates_frame.open.values, rates_frame.high.values, rates_frame.low.values,
        #                                rates_frame.close.values)
        #     if modec[9] == 100 or modec[9] == -100:
        #         if modec[9] == 100 and (macd_trend == 'BUY_TRAND_H1' or macd_trend == 'BUY_TRAND_H4' or macd_trend =='BUY_TRAND_D'):
        #             order_Type = '买单'
        #             moderedme = ' MACD处于[多头]趋势当中,当前K线形态为['
        #         elif modec[9] == -100 and (macd_trend == 'SELL_TRAND_H1' or macd_trend == 'SELL_TRAND_H4' or macd_trend == 'SELL_TRAND_D') :
        #             order_Type = '卖单'
        #             moderedme = 'MACD处于[空头]趋势当中，当前K线形态为['
        #         try:
        #             contents.append(
        #                 '<p><strong>货币兑：[' + symbol + ']' + moderedme + order_Type + ']跳空并列阴阳线模式</strong></p>三日K线模式，分上涨和下跌，以上升为例， 前两日阳线，第二日跳空，第三日阴线，收盘价于缺口中，上升趋势持续。')
        #             attrfile = generatebar.CandlesstickPng.GenerateBarPng(symbol, run_time)
        #             images.append(attrfile)
        #         except Exception as e:
        #             log.error('发送货币兑：' + symbol + '邮件信息失败！ 当前模式为：跳空并列阴阳线' + str(e))
        #
        #     '''
        #     函数名：CDLTHRUSTING
        #     名称：Thrusting Pattern 插入
        #     简介：二日K线模式，与颈上线类似，下跌趋势中，第一日长阴线，第二日开盘价跳空， 收盘价略低于前一日实体中部，与颈上线相比实体较长，预示着趋势持续。
        #     '''
        #     modec = talib.CDLTHRUSTING(rates_frame.open.values, rates_frame.high.values, rates_frame.low.values,
        #                                rates_frame.close.values)
        #     if modec[9] == 100 or modec[9] == -100:
        #         if modec[9] == 100 and (macd_trend == 'BUY_TRAND_H1' or macd_trend == 'BUY_TRAND_H4' or macd_trend =='BUY_TRAND_D'):
        #             order_Type = '买单'
        #             moderedme = ' MACD处于[多头]趋势当中,当前K线形态为['
        #         elif modec[9] == -100 and (macd_trend == 'SELL_TRAND_H1' or macd_trend == 'SELL_TRAND_H4' or macd_trend == 'SELL_TRAND_D') :
        #             order_Type = '卖单'
        #             moderedme = 'MACD处于[空头]趋势当中，当前K线形态为['
        #         try:
        #             contents.append(
        #                 '<p><strong>货币兑：[' + symbol + ']' + moderedme + order_Type + ']插入模式</strong></p>二日K线模式，与颈上线类似，下跌趋势中，第一日长阴线，第二日开盘价跳空， 收盘价略低于前一日实体中部，与颈上线相比实体较长，预示着趋势持续。')
        #             attrfile = generatebar.CandlesstickPng.GenerateBarPng(symbol, run_time)
        #             images.append(attrfile)
        #         except Exception as e:
        #             log.error('发送货币兑：' + symbol + '邮件信息失败！ 当前模式为：插入' + str(e))
        #
        #     '''
        #     函数名：CDLTRISTAR
        #     名称：Tristar Pattern 三星
        #     简介：三日K线模式，由三个十字组成， 第二日十字必须高于或者低于第一日和第三日，预示着反转。
        #     '''
        #     modec = talib.CDLTRISTAR(rates_frame.open.values, rates_frame.high.values, rates_frame.low.values,
        #                              rates_frame.close.values)
        #     if modec[9] == 100 or modec[9] == -100:
        #         if modec[9] == 100 and (macd_trend == 'BUY_TRAND_H1' or macd_trend == 'BUY_TRAND_H4' or macd_trend =='BUY_TRAND_D'):
        #             order_Type = '买单'
        #             moderedme = ' MACD处于[多头]趋势当中,当前K线形态为['
        #         elif modec[9] == -100 and (macd_trend == 'SELL_TRAND_H1' or macd_trend == 'SELL_TRAND_H4' or macd_trend == 'SELL_TRAND_D') :
        #             order_Type = '卖单'
        #             moderedme = 'MACD处于[空头]趋势当中，当前K线形态为['
        #         try:
        #             contents.append(
        #                 '<p><strong>货币兑：[' + symbol + ']' + moderedme + order_Type + ']三星模式</strong></p>二三日K线模式，由三个十字组成， 第二日十字必须高于或者低于第一日和第三日，预示着反转。')
        #             attrfile = generatebar.CandlesstickPng.GenerateBarPng(symbol, run_time)
        #             images.append(attrfile)
        #         except Exception as e:
        #             log.error('发送货币兑：' + symbol + '邮件信息失败！ 当前模式为：三星' + str(e))
        #
        #     '''
        #     函数名：CDLUNIQUE3RIVER
        #     名称：Unique 3 River 奇特三河床
        #     简介：三日K线模式，下跌趋势中，第一日长阴线，第二日为锤头，最低价创新低，第三日开盘价低于第二日收盘价，收阳线， 收盘价不高于第二日收盘价，预示着反转，第二日下影线越长可能性越大。
        #     '''
        #     modec = talib.CDLUNIQUE3RIVER(rates_frame.open.values, rates_frame.high.values, rates_frame.low.values,
        #                                   rates_frame.close.values)
        #     if modec[9] == 100 or modec[9] == -100:
        #         if modec[9] == 100 and (macd_trend == 'BUY_TRAND_H1' or macd_trend == 'BUY_TRAND_H4' or macd_trend =='BUY_TRAND_D'):
        #             order_Type = '买单'
        #             moderedme = ' MACD处于[多头]趋势当中,当前K线形态为['
        #         elif modec[9] == -100 and (macd_trend == 'SELL_TRAND_H1' or macd_trend == 'SELL_TRAND_H4' or macd_trend == 'SELL_TRAND_D') :
        #             order_Type = '卖单'
        #             moderedme = 'MACD处于[空头]趋势当中，当前K线形态为['
        #         try:
        #             contents.append(
        #                 '<p><strong>货币兑：[' + symbol + ']' + moderedme + order_Type + ']奇特三河床模式</strong></p>日K线模式，下跌趋势中，第一日长阴线，第二日为锤头，最低价创新低，第三日开盘价低于第二日收盘价，收阳线， 收盘价不高于第二日收盘价，预示着反转，第二日下影线越长可能性越大。')
        #             attrfile = generatebar.CandlesstickPng.GenerateBarPng(symbol, run_time)
        #             images.append(attrfile)
        #         except Exception as e:
        #             log.error('发送货币兑：' + symbol + '邮件信息失败！ 当前模式为：奇特三河床' + str(e))
        #
        #     '''
        #     函数名：CDLUPSIDEGAP2CROWS
        #     名称：Upside Gap Two Crows 向上跳空的两只乌鸦
        #     简介：三日K线模式，第一日阳线，第二日跳空以高于第一日最高价开盘， 收阴线，第三日开盘价高于第二日，收阴线，与第一日比仍有缺口。
        #     '''
        #     modec = talib.CDLUPSIDEGAP2CROWS(rates_frame.open.values, rates_frame.high.values, rates_frame.low.values,
        #                                      rates_frame.close.values)
        #     if modec[9] == 100 or modec[9] == -100:
        #         if modec[9] == 100 and (macd_trend == 'BUY_TRAND_H1' or macd_trend == 'BUY_TRAND_H4' or macd_trend =='BUY_TRAND_D'):
        #             order_Type = '买单'
        #             moderedme = ' MACD处于[多头]趋势当中,当前K线形态为['
        #         elif modec[9] == -100 and (macd_trend == 'SELL_TRAND_H1' or macd_trend == 'SELL_TRAND_H4' or macd_trend == 'SELL_TRAND_D') :
        #             order_Type = '卖单'
        #             moderedme = 'MACD处于[空头]趋势当中，当前K线形态为['
        #             try:
        #                 contents.append(
        #                     '<p><strong>货币兑：[' + symbol + ']' + moderedme + order_Type + ']向上跳空的两只乌鸦模式</strong></p>三日K线模式，第一日阳线，第二日跳空以高于第一日最高价开盘， 收阴线，第三日开盘价高于第二日，收阴线，与第一日比仍有缺口。')
        #                 attrfile = generatebar.CandlesstickPng.GenerateBarPng(symbol, run_time)
        #                 images.append(attrfile)
        #             except Exception as e:
        #                 log.error('发送货币兑：' + symbol + '邮件信息失败！ 当前模式为：向上跳空的两只乌鸦' + str(e))
        #
        #     '''
        #     函数名：CDLXSIDEGAP3METHODS
        #     名称：Upside/Downside Gap Three Methods 上升/下降跳空三法
        #     简介：五日K线模式，以上升跳空三法为例，上涨趋势中，第一日长阳线，第二日短阳线，第三日跳空阳线，第四日阴线，开盘价与收盘价于前两日实体内， 第五日长阳线，收盘价高于第一日收盘价，预示股价上升。
        #     '''
        #     modec = talib.CDLXSIDEGAP3METHODS(rates_frame.open.values, rates_frame.high.values, rates_frame.low.values,
        #                                       rates_frame.close.values)
        #     if modec[9] == 100 or modec[9] == -100:
        #         if modec[9] == 100 and (macd_trend == 'BUY_TRAND_H1' or macd_trend == 'BUY_TRAND_H4' or macd_trend =='BUY_TRAND_D'):
        #             order_Type = '买单'
        #             moderedme = ' MACD处于[多头]趋势当中,当前K线形态为['
        #         elif modec[9] == -100 and (macd_trend == 'SELL_TRAND_H1' or macd_trend == 'SELL_TRAND_H4' or macd_trend == 'SELL_TRAND_D') :
        #             order_Type = '卖单'
        #             moderedme = 'MACD处于[空头]趋势当中，当前K线形态为['
        #             try:
        #                 contents.append(
        #                     '<p><strong>货币兑：[' + symbol + ']' + moderedme + order_Type + ']上升/下降跳空三法模式</strong></p>五日K'
        #                                                                                  '线模式，以上升跳空三法为例，上涨趋势中，第一日长阳线，第二日短阳线，第三日跳空阳线，第四日阴线，开盘价与收盘价于前两日实体内， 第五日长阳线，收盘价高于第一日收盘价，预示股价上升。')
        #                 attrfile = generatebar.CandlesstickPng.GenerateBarPng(symbol, run_time)
        #                 images.append(attrfile)
        #             except Exception as e:
        #                 # print("发送邮件失败");
        #                 log.error('发送货币兑：' + symbol + '邮件信息失败！ 当前模式为：上升/下降跳空三法' + str(e))
    if len(contents) != 0:
        try:
            m.sendMail(contents, images, run_time)   #系统策略分为两种 MACD 和 KDEMA 当前参数macd区分为，只给库中记录为MACD为1的用户发送邮件
        except Exception as e:
            log.error('发送邮件失败  原因：' + e.toStr())
    log.info('=' * 50 + '搜索完成' + '=' * 50)

# BlockingScheduler
# scheduler = BlockingScheduler()
# scheduler.add_job(K_ModeSelect, 'date', run_date=time(0000), args=['232323'], id='K_ModeSelect')
# scheduler.start()
