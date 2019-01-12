from keras.layers import Input, LSTM, Embedding, normalization, Bidirectional, Dense, TimeDistributed
from keras.layers.core import RepeatVector
from keras.models import Model
from keras import backend as ke
from keras.layers import Lambda


def get_model3(p, em_mat, rmat, word_ind, em_dim, isl, osl):
    """
    Bi-LSTM, BatchNorm, MaxPool, 1-Layer Enc + BN, 1-Layer-Dec + BN + TDD-tanh
    """
    do = p['dropout']
    rdo = p['rec_dropout']
    for w in rmat.keys():
        op_dim = len(rmat[w])
        break
    fine_tune = True if p['learn_embed'] == 1 else False
    si = Input(shape=(isl,), dtype='int32')
    embedding_layer = Embedding(input_dim=len(word_ind) + 1, output_dim=em_dim,
                                input_length=isl, weights=[em_mat], trainable=fine_tune)(si)

    encoded = Bidirectional(LSTM(p['l1'], dropout=do, recurrent_dropout=rdo, return_sequences=True))(embedding_layer)
    bn_enc = normalization.BatchNormalization()(encoded)

    pool_rnn = Lambda(lambda x: ke.max(x, axis=1))(bn_enc)
    decode_inp = RepeatVector(osl)(pool_rnn)
    print 'em_dim=' + str(em_dim)
    print 'op_dim=' + str(op_dim)

    decoded = Bidirectional(LSTM(p['l2'], dropout=do, recurrent_dropout=rdo, return_sequences=True))(decode_inp)
    td = TimeDistributed(Dense(op_dim, activation='tanh'))(decoded)

    s2s_model = Model(inputs=[si], outputs=[td])
    print 'Starting to compile the model ...'
    s2s_model.compile(optimizer='adam', loss=myloss)
    return s2s_model, True


def myloss(y_true, y_pred):
    v1 = y_pred
    v2 = y_true
    numerator = ke.sum(v1 * v2)
    denominator = ke.sqrt(ke.sum(v1 ** 2) * ke.sum(v2 ** 2))
    loss = abs(1 - numerator/denominator)
    return loss
