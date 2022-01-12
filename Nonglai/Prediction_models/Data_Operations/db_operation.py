import pymysql
import numpy as np
import pandas as pd


class DB_Data():
    """此类用于连接数据库和对数据库进行操作"""

    def __init__(self, server='localhost', user='root', pwd='root'):
        """初始化数据库连接，设置数据库连接参数"""
        self.server = server
        self.user = user
        self.pwd = pwd

    def exec_SQL(self, sql, DataBase, warning='SQL语句写入失败！'):
        """此方法用于执行写入类SQL语句
        参数
    ----------
    sql : str，需要执行的SQL语句，str类型
        
    DataBase : str，数据库名
        
    warning : str，报错信息, 默认为‘SQL语句写入失败’

    Returns
    -------
    无
    """

        con = pymysql.connect(self.server, self.user, self.pwd, DataBase)
        cursor = con.cursor()

        try:
            cursor.execute(sql)
        except Exception as e:
            con.rollback()
            print(warning)

        cursor.close()
        con.commit()
        con.close()

    def exec_SQL_read(self, sql, DataBase, warning='SQL语句写入失败！'):
        """"此方法用于执行读取类SQL语句
        参数
    ----------
    sql : str，需要执行的SQL语句，str类型
        
    DataBase : str，数据库名
        
    warning : str，报错信息, 默认为‘SQL语句写入失败’

    Returns
    -------
    n x m 元组：n为数据条数，m为数据项数
    """

        con = pymysql.connect(self.server, self.user, self.pwd, DataBase)
        cursor = con.cursor()

        try:
            cursor.execute(sql)
        except:
            con.rollback()
            print(warning)

        cursor.close()
        con.commit()
        con.close()
        return cursor.fetchall()

    def read_sql(self,  product_id, DataBase="nonglai", table_name="view_time"):
        """"此方法用于从数据库中读取数据，并转化成DataFrame格式
                参数
            ----------
            product_id : int, 需要读取产品的id
                
            DataBase : str，数据库名，默认为‘nonglai’
                
            table_name : str，表名，默认为‘’

            Returns
            -------
            n x m 元组：n为数据条数，m为数据项数
            """
        con = pymysql.connect(host=self.server, user=self.user, password=self.pwd, db=DataBase)
        sql = """select year,month,monthday,weekday,price from %s where marketproduct_id=%d;""" % (table_name, product_id)
        dataframe = pd.read_sql(sql, con)
        return dataframe

    def get_product_id(self, DataBase, table):
        """此方法用于获得nonglai数据库中爬到的农产品列表
            参数
            ----------
            DataBase : str，数据库名
                
            table : str，表名

            Returns
            -------
            长度为n的列表 
        """

        sql = """select DISTINCT marketproduct_id from %s order by marketproduct_id""" % table
        t = list(self.exec_SQL_read(sql, DataBase))
        product_id = []

        for i in t:
            product_id.append(i[0])
        return product_id

    def get_loc(self, product_id, table, DataBase, is_predict):
        """此方法用于获得某一农产品在数据表中的起止位置，以便后续的读取操作
            参数
            ----------
            product_id ： int，产品id
            
            table : str，表名

            DataBase : str，数据库名
            
            is_predict : bool, 是不是预测数据
            
            Returns
            -------
            start : int，检索产品开始位置
             
             end : int,检索产品结束位置
        """

        if product_id == None:
            if is_predict == 1:
                sql_max_n = """select max(id) from %s where is_predict=%d;""" % (table, is_predict)
                sql_min_n = """select min(id) from %s where is_predict=%d;""" % (table, is_predict)
            else:

                sql_max_n = """select max(id) from %s ;""" % table
                sql_min_n = """select min(id) from %s ;""" % table
        else:
            sql_max_n = """select max(id) from %s where marketproduct_id = %d ;""" % (table, product_id)  # 获取数据条数
            sql_min_n = """select min(id) from %s where marketproduct_id = %d ;""" % (table, product_id)

        min = self.exec_SQL_read(sql_min_n, DataBase)[0]
        max = self.exec_SQL_read(sql_max_n, DataBase)[0]
        start = min[0]
        end = max[0]
        return start, end

    def get_width(self, table, DataBase):
        """此方法用于获得读取数据表的字段数
            参数
            ----------
            table : str，表名

            DataBase : str，数据库名
            
            Returns
            -------
            n : int, 检索产品的字段数量
        """

        if table != "products_product_price":
            sql_m = """select * from %s where id=2""" % table
        else:
            sql_m = """select price from %s where id=2""" % table  # 获取数据项数
        result = self.exec_SQL_read(sql_m, DataBase)[0]
        return len(result)

    def get_shape(self, product_id, table, DataBase, is_predict):
        """此方法用于获得检索产品关系表的形状，以便后续写入prediction数据库时缓存
            参数
            ----------
            product_id ： int，产品id
            
            table : str，表名

            DataBase : str，数据库名
            
            is_predict : bool, 是不是预测数据
            
            Returns
            -------
            n : int, 检索产品表的长度（数据条数）
            m : int, 检索产品表的字段数
        """

        n = self.get_loc(product_id, table, DataBase, is_predict)[1] - \
            self.get_loc(product_id, table, DataBase, is_predict)[0]
        m = self.get_width(table, DataBase)

        #data = np.zeros((n, m))  # 使用二维数组存放数据，数据形状为：n行m列
        return n+1, m

    def read_price(self, product_id, table="products_product_price", DataBase='nonglai'):
        """此函数用于从数据库中取出原始价格数据
            参数
            ----------
            product_id ： int，产品id
            
            table : str，表名，默认为‘products_product_price’

            DataBase : str，数据库名，默认为‘nonglai’
            
            
            Returns
            -------
            n x m 数组 ： n为数据条数，m为数据字段数
        """

        n, m = self.get_shape(product_id, table, DataBase, is_predict=0)
        start = self.get_loc(product_id, table, DataBase, is_predict=0)[0]
        price = np.zeros((n, 2))

        for i in range(n):
            sql = """select price ,date_id from %s where id = %d + %d""" % (table, start, i)
            line = self.exec_SQL_read(sql, DataBase)[0]
            price[i][0] = i
            price[i][1] = line[0]
        return price

    def read_data(self, product_id, table, DataBase='prediction', is_predict=0):
        """此函数用于从数据库中取出模型备用数据
            参数
            ----------
            product_id ： int，产品id

            table : str，表名

            DataBase : str，数据库名，默认为‘prediction’

            is_predict ： bool , 是否为预测数据，默认为0
                    
            Returns
            -------
            n x m 数组 ： n为数据条数，m为数据字段数
                """
        start = self.get_loc(product_id, table, DataBase, is_predict)[0]
        n, m = self.get_shape(product_id, table, DataBase, is_predict=is_predict)
        data = np.zeros((n, m-2))

        for i in range(n):
            sql_fech = "select imf1 "
            for j in range(1, m - 2):
                sql_fech += ",imf%d " % (j + 1)

            if is_predict == 0:
                sql = sql_fech + "from %s where id=%d" % (table, i + 1)
            else:
                sql = sql_fech + "from %s where id=%d and is_predict=%d" % (table, i + start, is_predict)
            line = self.exec_SQL_read(sql, DataBase)[0]

            for j in range(len(line)):
                data[i, j] = line[j]

        return data

    def write_data(self, data, table, DataBase='prediction', is_predict=0, update_id=0, marketproduct_id=-1, id_n=0, tag=0):
        """此函数用于向数据库写数据
            参数
            ----------
            data ： n x m 数组，用于写入数据库

            table : str，表名

            DataBase : str，数据库名，默认为‘prediction’

            is_predict ： bool , 是否为预测数据，默认为0
                    
            update_id : bool, 是否更新，默认为0
                    
            marketproduct_id ： 基础数据库产品id，默认-1表示没有读取产品
                    
            id_n ： bool, 写入表id，默认为0
            Returns
            -------
            无
        """

        if DataBase == "prediction":
            if is_predict == 1:
                for i in range(data.shape[0]):
                    valuesstr = str(i+1+update_id) + ',' + str(is_predict)
                    for j in range(0, data.shape[1]):
                        valuesstr += ", " + str(data[i, j])
                    sql_insert = """insert into %s  values (%s);""" % (table, valuesstr)
                    self.exec_SQL(sql_insert, DataBase, warning='insert语句写入失败！')
            else:
                for i in range(data.shape[0]):
                    valuesstr = str(i+1) + ',' + str(is_predict)
                    if tag == 0:
                        for j in range(0, data.shape[1]):
                            valuesstr += ", " + str(data[i, j])
                    else:
                        valuesstr += ", " + str(data[i])
                    sql_insert = """insert into %s  values (%s);""" % (table, valuesstr)
                    self.exec_SQL(sql_insert, DataBase, warning='insert语句写入失败！')
        else:
            sqll = "select max(date_id)+1 from products_product_price where marketproduct_id = "+str(marketproduct_id)
            max_dateid = self.exec_SQL_read(sqll, DataBase='nonglai')[0][0]

            for i in range(len(data)):
                sql_insert = """insert into %s  values (%d,%f,%d,%d,%d);""" % (table, (i + 1)+id_n*30, data[i], i+1, max_dateid+i, marketproduct_id)
                self.exec_SQL(sql_insert, DataBase, warning='insert语句写入失败！')

    def update_predict(self, data, table, marketproduct_id, DataBase='nonglai'):
        """此函数用于向数据库更新数据
                    参数
                    ----------
                    data ： n x m 数组，用于写入数据库

                    table : str，表名

                    DataBase : str，数据库名，默认为‘prediction’

                    marketproduct_id ： 基础数据库产品id，默认-1表示没有读取产品

                    Returns
                    -------
                    无
                """
        for i in range(data.shape[0]):
            sql_insert = """update %s  set price=%f where sequence_id=%d and marketproduct_id=%d;""" \
                         % (table, data[i], i + 1, marketproduct_id)
            self.exec_SQL(sql_insert, DataBase=DataBase, warning='insert语句写入失败！')

    def create_table(self, product_id, data, DataBase='prediction', tag=0):
        """此函数用于向数据库创建备用表
                    参数
                    ----------
                    data ： n x m 数组，用于写入数据库

                    DataBase : str，数据库名，默认为‘prediction’

                    is_predict ： bool , 是否为预测数据，默认为0
                            
                    Returns
                    -------
                    无
                """
        sql_oringin = """CREATE TABLE IF NOT EXISTS  `product%s` 
                        (`id` INT UNSIGNED AUTO_INCREMENT, 
                        `is_predict` binary,
                        """
        if tag == 0:
            for i in range(data.shape[1]):
                sql_oringin += """ `imf%d` float,""" % (i+1)
        else:
            sql_oringin += """`imf1` float,"""

        sql_create = sql_oringin % product_id
        sql_create = sql_create + """PRIMARY KEY ( `id` ));"""
        self.exec_SQL(sql_create, DataBase)
