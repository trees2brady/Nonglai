#-*- encoding:utf-8 -*-
import pymysql

class MySQL:
    def __init__(self, host='47.101.31.86', port=3306, user='root', password='Nonglai_1', db='nonglai'):
        self.host=host
        self.port=port
        self.user=user
        self.password=password
        self.db=db

    def get_connect(self):
        conn = pymysql.connect(host=self.host,port=self.port,user=self.user,passwd=self.password,db=self.db)
        return conn

    def sql_execute(self,sql_str):
        conn=self.get_connect()
        cursor=conn.cursor()
        cursor.execute(sql_str)
        result = cursor.fetchall()
        conn.commit()
        cursor.close()
        conn.close()
        return result
