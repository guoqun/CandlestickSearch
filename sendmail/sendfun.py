# encoding:GBK
from log.loginfo import LogFile
import sendmail.toMailClass as Mail
import sqlconnection.sqlhelper
import tools.ToString

'''
 SMTP������
'''
# yag = yagmail.SMTP( user="candlestick@126.com", password="LSKYWIJDERIMHBEZ", host='smtp.126.com')
# yag = yagmail.SMTP( user="15214003@qq.com", password="alsgtsupwwhhcbdj", host='smtp.qq.com')


log = LogFile(__name__).getlog()
conn=sqlconnection.sqlhelper.SqLHelper()

def sendMail(content=[], images=[], run_time='',flg='',symbol=''):
    receivers = ["2621333576@qq.com"]
    title = "��������ͼģ��ʶ��ϵͳ" + run_time + "���ڶ����ʼ�"
    sql='select email_address from user'
    cc_list=tools.ToString.UncodeToString(conn.select_all(sql))
    #cc_list = ["candlesticksearch@outlook.com'"]
    #m=Mail.Mail('smtp.126.com', '', 'candlestick@126.com', 'LSKYWIJDERIMHBEZ', '')
    m = Mail.Mail('smtp.qq.com', '', '15214003@qq.com', 'alsgtsupwwhhcbdj', '')
    m.send_mail(receivers, title, content, cc_list, 'utf-8', True, images)


def sendGQ(symbol='',order=''):
    receivers = ["2621333576@qq.com"]
    title = symbol + 'Ʒ�ֳ��֣�'+order+'�� MACD�����ڹ����ʼ���ʾ'
    cc_list = ["candlesticksearch@outlook.com'"]
    content =['��ǰ����Ʒ��'+symbol+'H4Сʱ�ж����ڹ��������뵽�����������ȷ��']
    m = Mail.Mail('smtp.qq.com', '', '15214003@qq.com', 'alsgtsupwwhhcbdj', '')
    m.send_mail(receivers, title, content, cc_list, 'utf-8', True)