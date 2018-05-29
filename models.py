from keras import Sequential, Model, Input
from keras.layers import LSTM, Dropout, Dense, concatenate
from keras import backend as K

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


def future_range_model(input_shape, feature_size, keep_prob):
    inputs = Input(shape=input_shape[1:])

    lstm_1 = LSTM(feature_size, return_sequences=True)(inputs)
    drop_1 = Dropout(keep_prob)(lstm_1)

    lstm_2 = LSTM(feature_size, return_sequences=False)(drop_1)
    drop_2 = Dropout(keep_prob)(lstm_2)

    dense_1 = Dense(32, kernel_initializer='uniform', activation='relu')(drop_2)
    outputs = Dense(2, kernel_initializer='uniform', activation='linear')(dense_1)

    model = Model(inputs=inputs, outputs=outputs)
    model.compile(optimizer='adam', loss='mse', metrics=['mae'])
    model.summary()
    return model


def future_range_momentum_model(input_shape, lstm_neurons, keep_prob):

    def directional_regression_loss(y, y_hat):
        diff = (y - y_hat) ** 2
        prod = y * y_hat + 1e-10
        cost = diff / K.exp(prod / K.abs(prod) - 1)
        loss = K.mean(cost)
        return loss

    inputs = Input(shape=input_shape[1:])

    lstm = LSTM(lstm_neurons, return_sequences=True)(inputs)
    drop = Dropout(keep_prob)(lstm)

    lstm = LSTM(lstm_neurons, return_sequences=False)(drop)
    drop = Dropout(keep_prob)(lstm)

    dense = Dense(32, kernel_initializer='uniform', activation='relu')(drop)

    direction = Dense(1, activation='sigmoid')(dense)
    magnitude = Dense(1, activation='linear')(dense)
    momentum_input = concatenate([direction, magnitude])
    momentum = Dense(1, activation='linear', name='momentum')(momentum_input)

    range = Dense(2, kernel_initializer='uniform', activation='linear', name='range')(dense)

    model = Model(inputs=inputs, outputs=[range, momentum])
    model.compile(optimizer='adam', loss=['mse', directional_regression_loss], metrics=['mae'])
    model.summary()
    return model

