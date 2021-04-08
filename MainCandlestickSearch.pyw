# encoding:GBK
from log.loginfo import LogFile
import time
import Search.SearchMode
import schedule
import weekend.WeekendSearch
import sqlconnection.sqlhelper
import myMacd.macdLib as mymacd
'''
Created on 2021年2月21日

@author: Administrator
'''
log = LogFile(__name__).getlog()
conn=sqlconnection.sqlhelper.SqLHelper()
if __name__ == '__main__':
    log.info("主程序启动成功.............................")

    Search.SearchMode.K_ModeSelect('H1')
    # # 1小日k线任务
    # schedule.every().day.at("00:02").do(Search.SearchMode.K_ModeSelect, 'H1')
    # schedule.every().day.at("01:02").do(Search.SearchMode.K_ModeSelect, 'H1')
    # schedule.every().day.at("02:02").do(Search.SearchMode.K_ModeSelect, 'H1')
    # schedule.every().day.at("03:02").do(Search.SearchMode.K_ModeSelect, 'H1')
    # schedule.every().day.at("04:02").do(Search.SearchMode.K_ModeSelect, 'H1')
    # schedule.every().day.at("05:02").do(Search.SearchMode.K_ModeSelect, 'H1')
    # schedule.every().day.at("06:02").do(Search.SearchMode.K_ModeSelect, 'H1')
    # schedule.every().day.at("07:02").do(Search.SearchMode.K_ModeSelect, 'H1')
    # schedule.every().day.at("08:02").do(Search.SearchMode.K_ModeSelect, 'H1')
    # schedule.every().day.at("09:02").do(Search.SearchMode.K_ModeSelect, 'H1')
    # schedule.every().day.at("10:02").do(Search.SearchMode.K_ModeSelect, 'H1')
    # schedule.every().day.at("11:02").do(Search.SearchMode.K_ModeSelect, 'H1')
    # schedule.every().day.at("12:02").do(Search.SearchMode.K_ModeSelect, 'H1')
    # schedule.every().day.at("13:02").do(Search.SearchMode.K_ModeSelect, 'H1')
    # schedule.every().day.at("14:02").do(Search.SearchMode.K_ModeSelect, 'H1')
    # schedule.every().day.at("15:02").do(Search.SearchMode.K_ModeSelect, 'H1')
    # schedule.every().day.at("16:02").do(Search.SearchMode.K_ModeSelect, 'H1')
    # schedule.every().day.at("17:02").do(Search.SearchMode.K_ModeSelect, 'H1')
    # schedule.every().day.at("18:02").do(Search.SearchMode.K_ModeSelect, 'H1')
    # schedule.every().day.at("19:02").do(Search.SearchMode.K_ModeSelect, 'H1')
    # schedule.every().day.at("20:02").do(Search.SearchMode.K_ModeSelect, 'H1')
    # schedule.every().day.at("21:02").do(Search.SearchMode.K_ModeSelect, 'H1')
    # schedule.every().day.at("22:02").do(Search.SearchMode.K_ModeSelect, 'H1')
    # schedule.every().day.at("23:02").do(Search.SearchMode.K_ModeSelect, 'H1')
    # # 4小日k线任务
    # schedule.every().day.at("00:05").do(Search.SearchMode.K_ModeSelect, 'H4')
    # schedule.every().day.at("04:05").do(Search.SearchMode.K_ModeSelect, 'H4')
    # schedule.every().day.at("08:05").do(Search.SearchMode.K_ModeSelect, 'H4')
    # schedule.every().day.at("12:05").do(Search.SearchMode.K_ModeSelect, 'H4')
    # schedule.every().day.at("16:05").do(Search.SearchMode.K_ModeSelect, 'H4')
    # schedule.every().day.at("20:05").do(Search.SearchMode.K_ModeSelect, 'H4')
    # # 日线任务进程
    # schedule.every().day.at("00:10").do(Search.SearchMode.K_ModeSelect, 'D1')
    # #schedule.every().day.at("05:36").do(Search.SearchMode.K_ModeSelect, 'D1')
    # #schedule.every().day.at("06:00").do(Search.SearchMode.K_ModeSelect, 'W1')
    # #每个周一添加一次周线进程
    # # if weekend.WeekendSearch.WekSear() == 0:
    # #     schedule.every().day.at("00:15").do(Search.SearchMode.K_ModeSelect, 'W1')
    # while True:
    #     schedule.run_pending()
    #     time.sleep(10)
