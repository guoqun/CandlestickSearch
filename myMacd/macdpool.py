import talib as ta
import numpy as np
import RequestMT5.MT5RequestData as  QuestDataMt5
from log.loginfo import LogFile
import sqlconnection.sqlhelper
import sendmail.sendfun as m
import tools.ToString
log = LogFile(__name__).getlog()
conn=sqlconnection.sqlhelper.SqLHelper()
def TrendMacdpool(SymbolName,period):
    global select_trend, sqlupdate_macd, macd, signal, macdhist, sql, trend_insert
    # 获取H1MACD的SIGNAL值
    QuestDate = QuestDataMt5.RequestData(SymbolName, period, 200)
    QuestDate = QuestDate[:198]
    close = QuestDate["close"].values
    macd, signal, macdhist = ta.MACD(close, 12, 26, 9)
    sql_select = "select  sysbol_Name from macdpool where sysbol_Name=%s"
    param = [SymbolName]
    ret = conn.select_one(sql=sql_select, param=param)
    try:
        if macd[197] > 0:
            trend_insert = 'BUY'
        elif macd[197] < 0:
            trend_insert = 'SELL'
        toret = tools.ToString.Byte64String(ret[0])
        if toret[0] is not None:
            if period == 'H1':  #处理1小时周期的MACD
                select_trend = "select macd_h1,h1_trend_num from macdpool where sysbol_Name like %s"
                sqlupdate_macd = "update macdpool set macd_h1=ROUND(%s,15),signal_h1=ROUND(%s,15),macdhist_h1=ROUND(%s,15),h1_trend_num=%s,trend_h1=%s,h1_update=now() where sysbol_Name=%s"
            elif period == 'H4':#处理4小时周期的MACD
                select_trend = "select macd_h4,h4_trend_num from macdpool where sysbol_Name like %s"
                sqlupdate_macd = "update macdpool set macd_h4=ROUND(%s,15),signal_h4=ROUND(%s,15),macdhist_h4=ROUND(%s,15),h4_trend_num=%s,trend_H4=%s,h4_update=now() where sysbol_Name=%s"
            elif period == 'D1':#处理日线周期的MACD
                select_trend = "select macd_day,day_trend_num from macdpool where sysbol_Name like %s"
                sqlupdate_macd = "update macdpool set macd_day=ROUND(%s,15),signal_day=ROUND(%s,15),macdhist_day=ROUND(%s,15),day_trend_num=%s,trend_day=%s,day_update=now() where sysbol_Name=%s"
            elif period == 'W1':#处理周线周期的MACD
                select_trend = "select macd_w,w_trend_num from macdpool where sysbol_Name like %s"
                sqlupdate_macd = "update macdpool set macd_w=ROUND(%s,15),signal_w=ROUND(%s,15),macdhist_w=ROUND(%s,15),w_trend_num=%s,trend_w=%s,w_update=now() where sysbol_Name=%s"
            try:
                ret_sql = conn.select_one(sql=select_trend, param=SymbolName)
                if (ret_sql[0] > 0 and macd[197] > 0) or (ret_sql[0] < 0 and macd[197] < 0):
                    trend_num = ret[1] + 1
                else:
                    trend_num = 1
                args = [macd[197], signal[197], macdhist[197], trend_num, trend_insert, SymbolName]
                conn.update(sqlupdate_macd, args)
            except Exception as e:
                trend_num = 1
                args = [macd[197], signal[197], macdhist[197], trend_num, trend_insert, SymbolName]
                conn.update(sqlupdate_macd, args)
    except Exception as e:
        if period == 'H1':
            sql = 'Insert macdpool(sysbol_Name,macd_h1,signal_h1,macdhist_h1,h1_trend_num,trend_h1,h1_update) VALUES(%s,ROUND(%s,' \
              '15),ROUND(%s,15),ROUND(%s,15),1,%s,now()) '
        elif period == 'H4':
            sql = 'Insert macdpool(sysbol_Name,macd_h4,signal_h4,macdhist_h4,h4_trend_num,trend_h4,h4_update) VALUES(%s,ROUND(%s,' \
                  '15),ROUND(%s,15),ROUND(%s,15),1,%s,now()) '
        elif period == 'D1':
            sql = 'Insert macdpool(sysbol_Name,macd_day,signal_day,macdhist_day,day_trend_num,trend_day,day_update) VALUES(%s,ROUND(%s,' \
                  '15),ROUND(%s,15),ROUND(%s,15),1,%s,now()) '
        elif period == 'W1':
            sql = 'Insert macdpool(sysbol_Name,macd_w,signal_w,macdhist_w,w_trend_num,trend_w,w_update) VALUES(%s,ROUND(%s,' \
                  '15),ROUND(%s,15),ROUND(%s,15),1,%s,now()) '
        args = (SymbolName, macd[197], signal[197], macdhist[197], trend_insert)
        conn.insert_one(sql, args)
        log.info('MACD池没有当前品种信息，新增……')
