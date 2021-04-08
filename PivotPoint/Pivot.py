# encoding:GBK
import pandas as pd
from pandas.plotting import register_matplotlib_converters

register_matplotlib_converters()
from log.loginfo import LogFile
import RequestMT5.MT5RequestData as  QuestDataMt5

log = LogFile(__name__).getlog()


#计算PP轴心点公式
def PPivot(SymbolName,Run_time):
    QuestDate=QuestDataMt5.RequestData(SymbolName,'W1',3)
    ticks_frame = pd.DataFrame(QuestDate)
    ticks_frame= ticks_frame[0:1]
    #log.info(ticks_frame)
    high=ticks_frame['high']
    #log.info('high:'+str(high))
    close=ticks_frame['close']
    #log.info('close:'+str(close))
    low=ticks_frame['low']

    #log.info('low:'+str(low))
    #PPoint = (high+low+close)/3
    # 枢轴点
    PivotPoint = (high + low + close) / 3.0
    # 支持位
    Support1 = PivotPoint*2-high
    Support2 = PivotPoint-(high-low)
    Support3 = low - 2*(high-PivotPoint)
    # 阻力位
    Resistance1 = PivotPoint*2 - low
    Resistance2 = PivotPoint+(high-low)
    Resistance3 = high+2*(PivotPoint-low)
    return Support3, Support2, Support1, PivotPoint, Resistance1, Resistance2, Resistance3
#