# encoding:GBK
from log.loginfo import LogFile
import sendmail.toMailClass as Mail
import sqlconnection.sqlhelper
import tools.ToString

'''
 SMTP服务器
'''
# yag = yagmail.SMTP( user="candlestick@126.com", password="LSKYWIJDERIMHBEZ", host='smtp.126.com')
# yag = yagmail.SMTP( user="15214003@qq.com", password="alsgtsupwwhhcbdj", host='smtp.qq.com')


log = LogFile(__name__).getlog()
conn=sqlconnection.sqlhelper.SqLHelper()

def sendMail(content=[], images=[], run_time='',flg='',symbol=''):
    receivers = ["2621333576@qq.com"]
    title = "智能蜡烛图模型识别系统" + run_time + "周期订阅邮件"
    sql='select email_address from user'
    cc_list=tools.ToString.UncodeToString(conn.select_all(sql))
    #cc_list = ["candlesticksearch@outlook.com'"]
    #m=Mail.Mail('smtp.126.com', '', 'candlestick@126.com', 'LSKYWIJDERIMHBEZ', '')
    m = Mail.Mail('smtp.qq.com', '', '15214003@qq.com', 'alsgtsupwwhhcbdj', '')
    m.send_mail(receivers, title, content, cc_list, 'utf-8', True, images)


def sendGQ(symbol='',order=''):
    receivers = ["2621333576@qq.com"]
    title = symbol + '品种出现：'+order+'单 MACD多周期共振邮件提示'
    cc_list = ["candlesticksearch@outlook.com'"]
    content =['当前货币品种'+symbol+'H4小时有多周期共振发生，请到交易软件进行确认']
    m = Mail.Mail('smtp.qq.com', '', '15214003@qq.com', 'alsgtsupwwhhcbdj', '')
    m.send_mail(receivers, title, content, cc_list, 'utf-8', True)