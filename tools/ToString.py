'''
从数据库取出数据时都显示为[b'USDCADm']形式转码为['USDCADm']形式
'''
from log.loginfo import LogFile
log = LogFile(__name__).getlog()
def UncodeToString(args=[]):
    ToString=[]
    for strtolist in args:
       str=strtolist.decode()
       ToString.append((str))
    return ToString

def Byte64String(args):
    ref = str(args,encoding='utf-8')
    return ref