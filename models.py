from keras import Sequential, Model, Input
from keras.layers import LSTM, Dropout, Dense


def single_price_model(input_shape, feature_size, keep_prob):
    """
    model based on
    https://medium.com/@siavash_37715/how-to-predict-bitcoin-and-ethereum-price-with-rnn-lstm-in-keras-a6d8ee8a5109

    :param input_shape:
    :param feature_size:
    :param keep_prob:
    :return:
    """
    inputs = Input(shape=input_shape[1:])

    lstm_1 = LSTM(feature_size, activation='tanh', return_sequences=True)(inputs)
    drop_1 = Dropout(keep_prob)(lstm_1)

    lstm_2 = LSTM(feature_size, activation='tanh', return_sequences=True)(drop_1)
    drop_2 = Dropout(keep_prob)(lstm_2)

    lstm_3 = LSTM(feature_size, activation='tanh')(drop_2)
    drop_3 = Dropout(keep_prob)(lstm_3)

    output = Dense(units=1, activation='relu')(drop_3)
    model = Model(inputs=inputs, outputs=output)
    model.compile(optimizer='adam', loss='mse', metrics=['mae'])
    return model


