#!/usr/bin/python3
import tensorflow as tf
from keras.backend.tensorflow_backend import set_session
config = tf.ConfigProto()
config.gpu_options.per_process_gpu_memory_fraction = 0.5
set_session(tf.Session(config=config))

from utils.dataset import get_batch

from keras.models import Sequential, Model
from keras.layers import LSTM, Input, Dense
from keras.optimizers import RMSprop, Adam

encoder_input = Input(shape = (None, 250))
encoder = LSTM(256, return_state = True)
encoder_output, state_h, state_c = encoder(encoder_input)

encoder_state = [state_h, state_c]

decoder_input = Input(shape = (None, 51213))
decoder_lstm = LSTM(256, return_sequences = True, return_state = True)
decoder_output, _, _ = decoder_lstm(decoder_input, initial_state = encoder_state)
decoder_output = Dense(51213, activation = 'softmax')(decoder_output)

model = Model([encoder_input, decoder_input], decoder_output)
model.compile(loss = 'categorical_crossentropy', optimizer = RMSprop(clipvalue = 5))
model.summary()

min_loss = 100
for epochs in range(1, 101):
    for batch in range(int(100000 / 128)):
        x_tr, din_tr, y_tr = get_batch(batch_size = 128)
        loss = model.train_on_batch([x_tr, din_tr], y_tr)

        if loss < min_loss:
            min_loss = loss

        if batch % 10 == 0:
            print('epochs: ' + str(epochs) + ', loss: ' + str(loss) + ', min loss: ' + str(min_loss))

    if epochs % 10 == 0:
        model.save('model/s2s.' + str(epochs) + '.bin')

