import pymysql
import pandas as pd
from Data_Operations.db_operation import *


class DataLoader():
    """此类用于载入、划分训练测试集和正则化数据，接收数据文件名，训练集比例和input维度三个初始参数"""

    def __init__(self, product_id, split, cols):
        db = DB_Data()
        dataframe = db.read_sql(product_id)
        self.start_value = dataframe['price'][0]
        i_split = int(len(dataframe) * split)
        # dataframe = pd.read_csv(filename)
        i_split = int(len(dataframe) * split)
        self.data_train = dataframe.get(cols).values[:i_split]
        self.data_test = dataframe.get(cols).values[i_split:]
        self.len_train = len(self.data_train)
        self.len_test = len(self.data_test)
        self.len_train_windows = None

    def get_test_data(self, seq_len, normalise):
        """此方法用于创建x,y的test移动窗口
        参数
        ----------
        seq_len ： int, 预测序列长度

        normalise : bool，是否正则化

        Returns
        -------
        无
        x : n x m数组
        y ：n x 1数组
        """
        data_windows = []                            #data_windows是test数据集中步长为1的移动窗口（移动数据集）
        for i in range(self.len_test - seq_len):
            data_windows.append(self.data_test[i:i+seq_len])

        data_windows = np.array(data_windows).astype(float)
        data_windows = self.normalise_windows(data_windows, single_window=False) if normalise else data_windows

        x = data_windows[:, :-1]
        y = data_windows[:, -1, [0]]
        return x, y

    def get_train_data(self, seq_len, normalise):
        """此方法用于创建x,y的train移动窗口"""
        data_x = []
        data_y = []
        for i in range(self.len_train - seq_len):
            x, y = self._next_window(i, seq_len, normalise)
            data_x.append(x)
            data_y.append(y)
        return np.array(data_x), np.array(data_y)

    def generate_train_batch(self, seq_len, batch_size, normalise):
        """从给定的用于训练/测试的cols分割列表上的文件名生成一个训练数据生成器"""
        i = 0
        while i < (self.len_train - seq_len):
            x_batch = []
            y_batch = []
            for b in range(batch_size):
                if i >= (self.len_train - seq_len):
                    # 如果数据分配不均匀，则为较小的最终批处理设置停止条件
                    yield np.array(x_batch), np.array(y_batch)
                    i = 0
                x, y = self._next_window(i, seq_len, normalise)
                x_batch.append(x)
                y_batch.append(y)
                i += 1
            yield np.array(x_batch), np.array(y_batch)

    def _next_window(self, i, seq_len, normalise):
        """从给定的索引位置i生成下一个数据窗口"""
        window = self.data_train[i:i+seq_len]
        window = self.normalise_windows(window, single_window=True)[0] if normalise else window
        x = window[:-1]
        y = window[-1, [0]]
        return x, y

    def normalise_windows(self, window_data, single_window=False):
        """对window进行正则化"""
        normalised_data = []
        window_data = [window_data] if single_window else window_data
        for window in window_data:
            normalised_window = []
            for col_i in range(window.shape[1]):
                normalised_col = [((float(p) / float(window[0, col_i])) - 1) for p in window[:, col_i]]
                normalised_window.append(normalised_col)
            normalised_window = np.array(normalised_window).T # 把array转换为初始的多维格式
            normalised_data.append(normalised_window)
        return np.array(normalised_data)