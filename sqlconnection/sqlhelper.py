# encoding:GBK
from itertools import chain

from sqlconnection.db_dbutils_init import get_my_connection
from log.loginfo import LogFile
"""ִ������ѯ�н�����ؽ��û�з���0����/ɾ/�ķ��ر������������û�з���0"""
log = LogFile(__name__).getlog()

class SqLHelper(object):
    def __init__(self):
        self.db = get_my_connection()  # �����ݳ��л�ȡ����

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, 'inst'):  # ����
            cls.inst = super(SqLHelper, cls).__new__(cls, *args, **kwargs)
        return cls.inst

    # ��װִ������
    def execute(self, sql, param=None, autoclose=False):
        """
        ����Ҫ�ж��Ƿ��в������Ƿ�ִ������ͷ����ӡ�
        :param sql: �ַ������ͣ�sql���
        :param param: sql�����Ҫ�滻�Ĳ���"select %s from tab where id=%s" ���е�%s���ǲ���
        :param autoclose: �Ƿ�ر�����
        :return: ��������conn���α�cursor
        """
        cursor, conn = self.db.getconn()  # �����ӳػ�ȡ����
        count = 0
        try:
            # count : Ϊ�ı����������
            if param:
                count = cursor.execute(sql, param)
            else:
                count = cursor.execute(sql)
            conn.commit()
            if autoclose:
                self.close(cursor, conn)
        except Exception as e:
            pass
        return cursor, conn, count

    # ִ�ж�������
    # def executemany(self, lis):
    #     """
    #     :param lis: ��һ���б�����ŵ���ÿ��sql���ֵ�'[{"sql":"xxx","param":"xx"}....]'
    #     :return:
    #     """
    #     cursor, conn = self.db.getconn()
    #     try:
    #         for order in lis:
    #             sql = order['sql']
    #             param = order['param']
    #             if param:
    #                 cursor.execute(sql, param)
    #             else:
    #                 cursor.execute(sql)
    #         conn.commit()
    #         self.close(cursor, conn)
    #         return True
    #     except Exception as e:
    #         print(e)
    #         conn.rollback()
    #         self.close(cursor, conn)
    #         return False

    # �ͷ�����
    def close(self, cursor, conn):
        """�ͷ����ӹ黹�����ӳ�"""
        cursor.close()
        conn.close()

    # ��ѯ����
    def select_all(self, sql, param=None):
        try:
            cursor, conn, count = self.execute(sql, param)
            res = cursor.fetchall()
            list_res=list(chain.from_iterable(res))
            self.close(cursor,conn)
            return list_res
        except Exception as e:
            print(e)
            self.close(cursor, conn)
            return count

    # ��ѯ����
    def select_one(self, sql, param=None):
        try:
            cursor, conn, count = self.execute(sql, param)
            res = cursor.fetchone()
            self.close(cursor, conn)
            return res
        except Exception as e:
            print("error_msg:", e.args)
            self.close(cursor, conn)
            return count

    # ����
    def insert_one(self, sql, param):
        try:
            cursor, conn, count = self.execute(sql, param)
            # _id = cursor.lastrowid()  # ��ȡ��ǰ�������ݵ�����id����idӦ��Ϊ�Զ�����Ϊ��
            conn.commit()
            self.close(cursor, conn)
            return count
            # ��ֹ����û��id����0
            # if _id == 0:
            #     return True
            # return _id
        except Exception as e:
            print(e)
            conn.rollback()
            self.close(cursor, conn)
            return count

    # ���Ӷ���
    def insert_many(self, sql, param):
        """
        :param sql:
        :param param: ������Ԫ����б�[(),()]�򣨣�����������
        :return:
        """
        cursor, conn, count = self.db.getconn()
        try:
            cursor.executemany(sql, param)
            conn.commit()
            return count
        except Exception as e:
            print(e)
            conn.rollback()
            self.close(cursor, conn)
            return count

    # ɾ��
    def delete(self, sql, param=None):
        try:
            cursor, conn, count = self.execute(sql, param)
            self.close(cursor, conn)
            return count
        except Exception as e:
            print(e)
            conn.rollback()
            self.close(cursor, conn)
            return count

    # ����
    def update(self, sql, param=None):
        try:
            cursor, conn, count = self.execute(sql, param)
            conn.commit()
            self.close(cursor, conn)
            return count
        except Exception as e:
            print(e)
            conn.rollback()
            self.close(cursor, conn)
            return count


    #if __name__ == '__main__':
    #db = MySqLHelper()
    # # ��ѯ����
    # sql1 = 'select * from userinfo where name=%s'
    # args = 'python'
    # ret = db.selectone(sql=sql1, param=args)
    # print(ret)  # (None, b'python', b'123456', b'0')
    # ���ӵ���
    # sql2 = 'insert into userinfo (name,password) VALUES (%s,%s)'
    # ret = db.insertone(sql2, ('old2','22222'))
    # print(ret)
    # ���Ӷ���
    # sql3 = 'insert into userinfo (name,password) VALUES (%s,%s)'
    # li = li = [
    #     ('��ʡ', '123'),
    #     ('����','456')
    # ]
    # ret = db.insertmany(sql3,li)
    # print(ret)
    # ɾ��
    # sql4 = 'delete from  userinfo WHERE name=%s'
    # args = 'xxxx'
    # ret = db.delete(sql4, args)
    # print(ret)
    # ����
    # sql5 = r'update userinfo set password=%s WHERE name LIKE %s'
    # args = ('993333993', '%old%')
    # ret = db.update(sql5, args)
    # print(ret)