'''
检测日线周期多空方向，并进行分类存储 BUY , SELL
'''
import sqlconnection.sqlhelper
from log.loginfo import LogFile
import RequestMT5.MT5RequestData as  QuestDataMt5
import talib as ta
import tools.ToString

log = LogFile(__name__).getlog()
conn=sqlconnection.sqlhelper.SqLHelper()
def Pool(SymbolName):
    try:
        QuestDate_D1 = QuestDataMt5.RequestData(SymbolName, 'D1', 30)
        QuestDate_W1 = QuestDataMt5.RequestData(SymbolName, 'W1', 100)
        ema_k_list = ta.EMA(QuestDate_D1["close"].values, 12)
        ema_d_list = ta.EMA(QuestDate_D1["close"].values, 26)
        STOCH_K, STOCH_D = ta.STOCH(QuestDate_D1.high.values, QuestDate_D1.low.values, QuestDate_D1.close.values, fastk_period=9,
                                    slowk_period=3, slowk_matype=0, slowd_period=3, slowd_matype=0)
        close_w = QuestDate_W1["close"].values
        macd_w, signal_w, hist_w = ta.MACD(close_w, 12, 26, 9)
        if ema_k_list[28] > ema_d_list[28]:
            direction = 'BUY'
        elif ema_k_list[28] < ema_d_list[28]:
            direction = 'SELL'
        else:
            direction = 'BS'   #方向不明确
        #查询当前货币池pool表中是否已有记录
        args = SymbolName
        sql_select = 'select sysbol_Name,direction,ema_signal_day from pool where sysbol_Name=%s'
        ret = conn.select_one(sql=sql_select, param=args)
        todirection = tools.ToString.Byte64String(ret[1])
        if ret[0] is not None:
            if todirection != direction:
                emasignalday=0
            else:
                emasignalday=ret[2]+1
            args = (ema_k_list[28], ema_d_list[28], direction, STOCH_K[28], STOCH_D[28], macd_w[97], signal_w[97],hist_w[97],emasignalday, SymbolName)
            update_sql = 'update pool set ema12=ROUND(%s,15),ema26=ROUND(%s,15), direction=%s,stoch_k_day=ROUND(%s,15),stoch_d_day=ROUND(%s,15),macd_w=ROUND(%s,15),signal_w=ROUND(%s,15), hist_w=ROUND(%s,15),ema_signal_day=%s,date=now() WHERE sysbol_Name LIKE %s'
            rets = conn.update(update_sql, args)
    except Exception as e:
        sql = 'Insert pool(sysbol_Name,ema12,ema26,direction,stoch_k_day,stoch_d_day, macd_w, signal_w, hist_w,date) VALUES(%s,ROUND(%s,15),ROUND(%s,15),%s,ROUND(%s,15),ROUND(%s,15),ROUND(%s,15),ROUND(%s,15),ROUND(%s,15),1,now())'
        args = (SymbolName,ema_k_list[28], ema_d_list[28], direction, STOCH_K[28], STOCH_D[28], macd_w[97], signal_w[97], hist_w[97])
        rets = conn.insert_one(sql, args)
        log.error('分析EMA货币池错误……')
        log.error(e)
