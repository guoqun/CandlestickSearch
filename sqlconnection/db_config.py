# encoding:GBK
import pymysql

# ���ݿ���Ϣ
DB_TEST_HOST = "127.0.0.1"
DB_TEST_PORT = 3306
DB_TEST_DBNAME = "CandlestickBase"
DB_TEST_USER = "root"
DB_TEST_PASSWORD = "root"

# ���ݿ����ӱ���
DB_CHARSET = "utf8"

# mincached : ����ʱ������������������(ȱʡֵ 0 ��ʼʱ����������)
DB_MIN_CACHED = 10

# maxcached : ���ӳ�����������õ������������(ȱʡֵ 0 �����������ӳش�С)
DB_MAX_CACHED = 10

# maxshared : ����������������������(ȱʡֵ 0 �����������Ӷ���ר�õ�)����ﵽ���������,������Ϊ��������ӽ��ᱻ����ʹ��
DB_MAX_SHARED = 20

# maxconnecyions : �������ӳص��������(ȱʡֵ 0 ��������)
DB_MAX_CONNECYIONS = 100

# blocking : ���������ӳشﵽ�������ʱ����Ϊ(ȱʡֵ 0 �� False ������һ������<toMany......> ������������ֱ������������,���ӱ�����)
DB_BLOCKING = True

# maxusage : �������ӵ���������ô���(ȱʡֵ 0 �� False �������Ƶĸ���).���ﵽ�����ʱ,���ӻ��Զ���������(�رպ����´�)
DB_MAX_USAGE = 0

# setsession : һ����ѡ��SQL�����б�����׼��ÿ���Ự����["set datestyle to german", ...]
DB_SET_SESSION = None

# creator : ʹ���������ݿ��ģ��
DB_CREATOR = pymysql