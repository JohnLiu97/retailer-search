


#!/usr/bin/env python
# coding: utf-8


import pickle
import numpy as np

from sklearn.metrics import accuracy_score
from keras.models import Sequential
from keras.layers import Dense, Dropout, Embedding, LSTM, Bidirectional
from sklearn.model_selection import train_test_split
from keras import backend as K
from sklearn.metrics import classification_report
from keras.utils import to_categorical
from keras.callbacks import ModelCheckpoint
from keras.models import load_model
from sklearn.model_selection import StratifiedKFold
import sys

class Logger(object):
    def __init__(self):
        self.terminal = sys.stdout
        self.log = open("log.txt", "w")

    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)  

    def flush(self): 
        self.terminal.flush() 
        self.log.flush()

sys.stdout = Logger()

def BiLSTM(x_train, y_train):
#     max_features = 20000
#     # cut texts after this number of words
#     # (among top max_features most common words)
#     global vocab_size
    maxlen = x_train.shape[1]
#     batch_size = 32

    model = Sequential()
    #model.add(Embedding(20000 , 512, input_length=maxlen))
    model.add(Bidirectional(LSTM(512)))
    model.add(Dropout(0.2))
    model.add(Dense(100))
    model.add(Dropout(0.2))
    model.add(Dense(3, activation='softmax'))

    # try using different optimizers and different optimizer configs
    model.compile('adam', 'categorical_crossentropy', metrics=['categorical_accuracy'])
    return model

def get_10_fold_data(X, Y):
    seed = 7
    
    kfold = StratifiedKFold(n_splits=10, shuffle=True, random_state=seed)
    
    return kfold.split(X, Y)


def gen_dummy_data(x=761,y=128,z=768):
    x_train = np.random.rand(x,y,z)
    y_train = np.array([np.random.randint(2)*2-1 for i in range(x)])
    x_test = np.random.rand(x,y,z)
    y_test = np.array([np.random.randint(2)*2-1 for i in range(x)])
    
    return [x_train, x_test],[y_train, y_test]
    
def get_search_data():
    # x_data = np.load("../../data/results.npy")
    # x_data = np.concatenate([x_data,np.load("../../data/descriptions.npy")],axis=-1)
    # y_data = np.load("../../data/labels_3_cat.npy")+1
    #
    # x_train, x_test, y_train, y_test  = train_test_split(x_data, y_data, train_size=0.8)

    data_1 = np.load('../../data/results_big_one_hot.npy')
    data_2 = np.load('../../data/descriptions_big_one_hot.npy')
    labels_all = to_categorical(np.load('../../data/labels_3_cat_big.npy'))
    con_data=np.concatenate([data_1,data_2],axis=-1)

    split = int(len(data_1) * 9 / 10)

    data_1_train = data_1[0:split]
    data_2_train = data_2[0:split]
    con_data_train = con_data[0:split]


    data_1_test = data_1[split:]
    data_2_test = data_2[split:]
    con_data_test = con_data[split:]

    y_train = labels_all[:split]
    y_test = labels_all[split:]
    print(y_test.shape)

    #only use results for testing
    data_1_test = np.concatenate([data_1_test,data_1_test],axis=-1)

    return [con_data_train, data_1_test],[y_train, y_test]
    
#---------------------------metrics---------------------------------------------#
def recall_m(y_true, y_pred):
        #true_positives = K.sum(K.cast(K.equal(K.round(K.clip(y_pred, 0, 1)),K.round(K.clip(y_true, 0, 1))),'float32'))
        true_positives = K.sum(K.round(K.clip(y_true, 0, 1) * K.clip(y_pred, 0, 1)))                
        possible_positives = K.sum(K.round(K.clip(y_true, 0, 1)))
        recall = true_positives / (possible_positives + K.epsilon())
        return recall

def precision_m(y_true, y_pred):
        #true_positives = K.sum(K.cast(K.equal(K.round(K.clip(y_pred, 0, 1)),K.round(K.clip(y_true, 0, 1))),'float32'))
        true_positives = K.sum(K.round(K.clip(y_true, 0, 1) * K.clip(y_pred, 0, 1))) 
        predicted_positives = K.sum(K.round(K.clip(y_pred, 0, 1)))
        precision = true_positives / (predicted_positives + K.epsilon())
        return precision

def f1_m(y_true, y_pred):
    precision = precision_m(y_true, y_pred)
    recall = recall_m(y_true, y_pred)
    return 2*((precision*recall)/(precision+recall+K.epsilon()))




# [x_train, x_test],[y_train, y_test] = get_search_data()
# #y_train = to_categorical(y_train)
# #y_test = to_categorical(y_test)
# # global vocab_size
# # vocab_size = x_train.shape[-1]

# # x_train = np.argmax(x_train, -1).squeeze()
# # x_test = np.argmax(x_test, -1).squeeze()


# model = BiLSTM(x_train, y_train)
# # model.summary()
# print('Train...')
# callbacks = [
#   # EarlyStopping(monitor='val_loss', patience=args.train_patience, verbose=0),
#   ModelCheckpoint('model.h5', monitor='val_loss', save_best_only=True,
#                   verbose=1),
# ]
# history=model.fit(x_train, y_train,
#            epochs=15,
#            validation_data=[x_test, y_test],
#              batch_size=512,
#              callbacks=callbacks)
# # with open('history_params.sav', 'wb') as f:
# #     pickle.dump(history.history, f, -1)

# model = load_model('model.h5')

# y_pred = model.predict(x_test)
# y_pred_cat = np.round(y_pred)

# print(classification_report(y_test, y_pred_cat))
# print("accuracy {:.2f}".format(accuracy_score(y_test.argmax(-1), y_pred_cat.argmax(-1))))
f = open("10_fold_results.txt","w")

data_1 = np.load('../../data/results_big_one_hot.npy')
data_2 = np.load('../../data/descriptions_big_one_hot.npy')
labels_all = np.load('../../data/labels_3_cat_big.npy')
con_data=np.concatenate([data_1,data_2],axis=-1)


# flag = 0
# avg_dict = {'micro avg': {'precision': 0,'recall': 0,'f1-score':0}, 'macro avg': {'precision': 0,'recall': 0,'f1-score':0}}
# for train, test in get_10_fold_data(con_data, labels_all):
#     flag+=1

#     x_train = con_data[train]
#     y_train = to_categorical(labels_all[train])
#     x_test = con_data[test]
#     y_test = to_categorical(labels_all[test])


#     model = BiLSTM(x_train, y_train)
#     # model.summary()

#     callbacks = [
#       # EarlyStopping(monitor='val_loss', patience=args.train_patience, verbose=0),
#       ModelCheckpoint('BiLSTM_3_cat.h5', monitor='val_loss', save_best_only=True,
#                       verbose=1),
#     ]
#     print('fold: '+ str(flag))
#     print('results + descriptions ---> results + descriptions ')
#     # model.summary()
#     print('Train...')

#     f.write('fold: '+ str(flag))
#     f.write('results + descriptions ---> results + descriptions ')
#     # model.summary()
#     f.write('Train...' + '\n\n')

#     history = model.fit(x_train, y_train,
#                         epochs=15,
#                         validation_data=[x_test, y_test],
#                         batch_size=256,
#                         callbacks=callbacks)
#     model=load_model('BiLSTM_3_cat.h5')
#     y_pred = model.predict(x_test)
#     y_pred_cat = np.round(y_pred)

#     report = classification_report(y_test, y_pred_cat)
#     score = accuracy_score(y_test.argmax(-1), y_pred_cat.argmax(-1))
#     print(report)
#     print("accuracy {:.2f}".format(score))

#     f.write(report)
#     f.write("accuracy {:.2f}".format(score) + '\n\n')

#     temp_dict = classification_report(y_test, y_pred_cat, output_dict = True) 
#     for key1 in avg_dict:
#         for key2 in avg_dict[key1]:
#             avg_dict[key1][key2] += temp_dict[key1][key2]
            
# for key1 in avg_dict:
#     for key2 in avg_dict[key1]:
#         avg_dict[key1][key2] = avg_dict[key1][key2]/10

# print("average score for results + descriptions ---> results + descriptions:")
# print(avg_dict)

# f.write("average score for results + descriptions ---> results + descriptions:")
# f.write(avg_dict)
# f.write('\n\n')

flag = 0
avg_dict = {'micro avg': {'precision': 0,'recall': 0,'f1-score':0}, 'macro avg': {'precision': 0,'recall': 0,'f1-score':0}}
for train, test in get_10_fold_data(con_data, labels_all):
    flag+=1

    x_train = con_data[train]
    y_train = to_categorical(labels_all[train])


    x_test = np.concatenate([data_1[test],np.zeros(data_2[test].shape)],axis=-1)
    y_test = to_categorical(labels_all[test])


    model = BiLSTM(x_train, y_train)
    # model.summary()

    callbacks = [
      # EarlyStopping(monitor='val_loss', patience=args.train_patience, verbose=0),
      ModelCheckpoint('BiLSTM_3_cat.h5', monitor='val_loss', save_best_only=True,
                      verbose=1),
    ]
    print('fold: '+ str(flag))
    print('results + descriptions ---> result')
    # model.summary()
    print('Train...')

    f.write('fold: '+ str(flag))
    f.write('results + descriptions ---> results + descriptions ')
    # model.summary()
    f.write('Train...' + '\n\n')

    history = model.fit(x_train, y_train,
                        epochs=15,
                        validation_data=[x_test, y_test],
                        batch_size=256,
                        callbacks=callbacks)
    model=load_model('BiLSTM_3_cat.h5')
    y_pred = model.predict(x_test)
    y_pred_cat = np.round(y_pred)

    report = classification_report(y_test, y_pred_cat)
    score = accuracy_score(y_test.argmax(-1), y_pred_cat.argmax(-1))
    print(report)
    print("accuracy {:.2f}".format(score))

    f.write(report)
    f.write("accuracy {:.2f}".format(score) + '\n\n')

    temp_dict = classification_report(y_test, y_pred_cat, output_dict = True) 
    for key1 in avg_dict:
        for key2 in avg_dict[key1]:
            avg_dict[key1][key2] += temp_dict[key1][key2]

for key1 in avg_dict:
    for key2 in avg_dict[key1]:
        avg_dict[key1][key2] = avg_dict[key1][key2]/10

print("average score for results + descriptions ---> results:")
print(avg_dict)



f.write("average score for results + descriptions ---> results + descriptions:")
f.write(str(avg_dict))
f.write('\n\n')
