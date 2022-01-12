import os
import json
import math
import matplotlib.pyplot as plt
from core.data_processor import DataLoader
from core.model import Model
from Data_Operations.db_operation import *

#
# def plot_results(predicted_data, true_data):
#     fig = plt.figure(facecolor='white')
#     ax = fig.add_subplot(111)
#     ax.plot(true_data, label='True Data')
#     plt.plot(predicted_data, label='Prediction')
#     plt.legend()
#     plt.show()
#
#
# def plot_results_multiple(predicted_data, true_data, prediction_len):
#     fig = plt.figure(facecolor='white')
#     ax = fig.add_subplot(111)
#     ax.plot(true_data, label='True Data')
#     # Pad the list of predictions to shift it in the graph to it's correct start
#     for i, data in enumerate(predicted_data):
#         padding = [None for p in range(i * prediction_len)]
#         plt.plot(padding + data, label='Prediction')
#         plt.legend()
#     plt.show()

        # model.build_model(configs)
    # x, y = data.get_train_data(
    #     seq_len=configs['data']['sequence_length'],
    #     normalise=configs['data']['normalise']
    # )
    #
    # steps_per_epoch = math.ceil((data.len_train - configs['data']['sequence_length']) / configs['training']['batch_size'])
    # model.train_generator(
    #     data_gen=data.generate_train_batch(
    #         seq_len=configs['data']['sequence_length'],
    #         batch_size=configs['training']['batch_size'],
    #         normalise=configs['data']['normalise']
    #     ),
    #     epochs=configs['training']['epochs'],
    #     batch_size=configs['training']['batch_size'],
    #     steps_per_epoch=steps_per_epoch,
    #     save_dir=configs['model']['save_dir']
    # )

    # x_test, y_test = data.get_test_data(
    #     seq_len=configs['data']['sequence_length'],
    #     normalise=configs['data']['normalise']
    # )
    #
    # model.load_model('saved_models/21032019-170059-e6.h5')
    #
    # predictions = model.predict_sequences_multiple(x_test, configs['data']['sequence_length'], configs['data']['sequence_length'])
    # for i in predictions:
    #     pass#每个值除以第一个值 再减1
    #
    # print(len(predictions))
    #predictions = model.predict_sequence_full(x_test, configs['data']['sequence_length'])
    # predictions = model.predict_point_by_point(x_test)
    # plot_results_multiple(predictions, y_test, configs['data']['sequence_length'])
    # plot_results(predictions, y_test)


if __name__ == '__main__':
    configs = json.load(open('config.json', 'r'))
    if not os.path.exists(configs['model']['save_dir']): os.makedirs(configs['model']['save_dir'])
    db = DB_Data()
    product_id = db.get_product_id(DataBase='nonglai', table='products_product_price')
    model = Model()
    model.load_model('saved_models/21032019-170059-e6.h5')
    if 1:
        i = 1446
        data = DataLoader(
                i,
                split=configs['data']['train_test_split'],
                cols=configs['data']['columns']
            )

        start_value = data.start_value

        x_test, y_test = data.get_test_data(
                seq_len=configs['data']['sequence_length'],
                normalise=configs['data']['normalise']
            )

        predictions = model.predict_sequences_multiple(x_test, configs['data']['sequence_length'],
                                                           configs['data']['sequence_length'])
        x = []
        for m in range(len(predictions[:])):
            for j in range(len(predictions[0])):
                x.append(predictions[m][j])
        for m in range(len(x)):
            x[m] = (1 + x[m]) * start_value

        x_pre = []
        for m in range(30):
            x_pre.append(x[m])
        db.write_data(x_pre, table='products_price_predict2', DataBase='nonglai', is_predict=1, marketproduct_id=i)