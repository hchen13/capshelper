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


def future_range_direction_model(input_shape, lstm_neurons, keep_prob):
    inputs = Input(shape=input_shape[1:])

    lstm = LSTM(lstm_neurons, return_sequences=True)(inputs)
    drop = Dropout(keep_prob)(lstm)

    lstm = LSTM(lstm_neurons, return_sequences=False)(drop)
    drop = Dropout(keep_prob)(lstm)

    dense = Dense(128, kernel_initializer='uniform', activation='relu')(drop)

    range = Dense(2, kernel_initializer='uniform', activation='linear', name='range')(dense)
    direction = Dense(1, activation='sigmoid', name='direction')(dense)

    model = Model(inputs=inputs, outputs=[range, direction])
    model.compile(optimizer='adam', loss=['mse', 'binary_crossentropy'], metrics=['mae', 'acc'])
    model.summary()
    return model


def next_price_direction_model(input_shape, lstm_neurons, keep_prob):
    inputs = Input(shape=input_shape[1:])

    lstm = LSTM(lstm_neurons, return_sequences=True)(inputs)
    drop = Dropout(keep_prob)(lstm)

    lstm = LSTM(lstm_neurons, return_sequences=False)(drop)
    drop = Dropout(keep_prob)(lstm)

    dense = Dense(32, kernel_initializer='uniform', activation='relu')(drop)

    price = Dense(1, activation='linear', name='price')(dense)
    direction = Dense(1, activation='sigmoid', name='direction')(dense)

    model = Model(inputs=inputs, outputs=[price, direction])
    model.compile(optimizer='adam', loss=['mse', 'binary_crossentropy'], metrics=['mae', 'acc'])
    return model


def next_candle_model(input_shape, lstm_neurons, keep_prob):
    inputs = Input(shape=input_shape[1:])

    lstm = LSTM(lstm_neurons, return_sequences=True)(inputs)
    drop = Dropout(keep_prob)(lstm)

    lstm = LSTM(lstm_neurons, return_sequences=False)(drop)
    drop = Dropout(keep_prob)(lstm)

    dense = Dense(32, kernel_initializer='uniform', activation='relu')(drop)

    candle = Dense(5, activation='linear', name='candle')(dense)

    model = Model(inputs=inputs, outputs=candle)
    model.compile(optimizer='adam', loss='mse', metrics=['mae', 'mse'])
    model.summary()
    return model