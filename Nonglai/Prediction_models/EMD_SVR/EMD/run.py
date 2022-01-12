from Data_Operations.db_operation import *
from EMD_SVR.EMD import emd_functions as emd
import matplotlib.pyplot as plt
import pandas as pd


def write_decomposed_data():
    """此函数用于向数据库写入已经分解的价格数据
        参数
        ----------
        无
        Returns
        -------
        无
            """
    db = DB_Data()
    product_id = db.get_product_id(DataBase='nonglai', table='products_product_price')
    i= 1446
    data = db.read_price(i)

    x = data[:, 0]
    price = data[:, 1]

    c1, r1 = emd.saw_emd(x, price, bc='extrap')

    tag = 0
    if c1.shape != (0,):
        r1 = r1.reshape(-1, 1)
        data = np.concatenate((c1, r1), axis=1)
    else:
        tag = 1
        data = r1

    db.create_table(i, data, tag=tag)
    table_name = 'product' + str(i)

    db.write_data(data, table_name, is_predict=0, tag=tag)

if __name__ == "__main__":

    write_decomposed_data()
    # db = DB_Data()
    # data = db.read_data(product_id=None, table='product1')
    # imf = pd.DataFrame(data)
    # imf.columns = ['imf1', 'imf2', 'imf3', 'imf4', 'imf5']
    # fig, ax = plt.subplots(figsize=(7, 5))     堆叠图可视化
    # n = data.shape[0]
    # x = np.arange(n)
    # ax.stackplot(x, imf['imf1'], imf['imf2'], imf['imf3'], imf['imf4'], imf['imf5'])
    #
    # plt.plot(data[0])
    #
    # plt.show()
    print('done')