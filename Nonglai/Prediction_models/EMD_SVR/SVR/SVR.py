from sklearn.svm import SVR
from Data_Operations.db_operation import *


def multi_predict(table_name):
    """此函数用于分别对分解过的价格数据分量进行预测
        参数
        ----------
        table_name : str，表名
        Returns
        -------
        无
            """
    db = DB_Data()
    product_id = None
    data = db.read_data(table=table_name, product_id=product_id)
    n = data.shape[0]

    x_ = np.arange(1, n + 1)
    x = x_.reshape(-1, 1)
    x_pred = np.arange(1, 31) + x[-1]
    x_pred_ = x_pred.reshape(-1, 1)
    new_data = np.zeros((30, data.shape[1]))

    for i in range(data.shape[1]):
        y = data[:, i]
        regressor = SVR(kernel='rbf')
        regressor.fit(x, y)
        y_pred = regressor.predict(x_pred_)
        for j in range(len(x_pred_)):
            new_data[j, i] = y_pred[j]

    db.write_data(data=new_data, table=table_name, is_predict=1, update_id=n)


def write_multi_predict():
    """此函数用于把预测的分解过的价格数据分量写入数据库
        参数
        ----------
        无
        Returns
        -------
        无
                """
    db = DB_Data()
    product_id = db.get_product_id(DataBase="nonglai", table="products_product_price")

    i = 1446
    table_name = "product" + str(i)
    multi_predict(table_name=table_name)


def actual_predict():
    """此函数用于从数据库中取出预测的各分量并整合成预测的价格数据
            参数
            ----------
            无
            Returns
            -------
            无
                """
    db = DB_Data()

    product_id = None
    product_id_list = db.get_product_id(DataBase="nonglai", table="products_product_price")
    id_n = 0
    i = 1446
    table_name = "product" + str(i)
    data = db.read_data(product_id, table=table_name, is_predict=1)
    price = []
    for j in range(data.shape[0]):
        t = 0
        for m in range(data.shape[1]):
            t += data[j, m]
        price.append(t)
    db.write_data(data=price, table="products_price_predict1", DataBase="nonglai", marketproduct_id=i, id_n=id_n)
    id_n += 1
        # db.updata_predict(data=price, table="products_price_predict1")

if __name__ == "__main__":
    # write_multi_predict()
    actual_predict()
    print("done!")


