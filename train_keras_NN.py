#!/usr/bin/python

import numpy as np
from keras.models import Sequential
from keras.optimizers import SGD,Adam,RMSprop
from keras.layers import Dense, Dropout, LeakyReLU, AlphaDropout
import mvasup


filename = '../MVA_Data/data/training_1l_8ji3bi.csv'
output_model_name = '../MVA_Data/weights/model_1l_8ji3bi_0.h5'
output_weights_name = '../MVA_Data/weights/weights_1l_8ji3bi_0.h5'
output_file_name = '../MVA_Data/output_1l_8ji3bi_0.root'
selected_variable = list(range(1,18))
njet = 8
nbtag = 3

print ("\nReading file..")
f = open(filename)
header = f.readline()
variable_names = np.array(header.split(','))[selected_variable]
dataset = np.loadtxt(filename, delimiter=',', skiprows=1, converters={31: lambda x:int(x=='s'.encode('utf-8')) })
print ("Completed..\n")


variable_size = len(selected_variable)

X = np.array([x[selected_variable] for x in dataset if x[3]>=njet and x[4]>=nbtag and x[18]>=0])
Y = np.array([x[19:31] for x in dataset if x[3]>=njet and x[4]>=nbtag and x[18]>=0])
label = np.array([x[31] for x in dataset if x[3]>=njet and x[4]>=nbtag and x[18]>=0])
W = np.array([x[18] for x in dataset if x[3]>=njet and x[4]>=nbtag and x[18]>=0])

sample_size = len(X)
train_size = int(sample_size/2)

Xor_train, Xor_test = np.copy(X[:train_size, :]), np.copy(X[train_size:, :])
Wor_train, Wor_test = np.copy(W[:train_size]), np.copy(W[train_size:])

print ("Normalizing Inputs----------------------------------------")
norm=mvasup.Norm('strd_1l_8ji3bi','norm/')
X=norm.Standardization(X,variable_names)
print ("End of Normalization--------------------------------------\n")

print ("Splitting data")
X_train, X_test = X[:train_size, :], X[train_size:, :]
Y_train, Y_test = Y[:train_size], Y[train_size:]
W_train, W_test = W[:train_size], W[train_size:]
label_train, label_test = label[:train_size], label[train_size:]



sum_wpos = sum( W_train[i] for i in range(len(label_train)) if label_train[i] == 1.0  )
sum_wneg = sum( W_train[i] for i in range(len(label_train)) if label_train[i] == 0.0  )

for i in range(len(W_train)):
    if (label_train[i]==1.0):
        W_train[i] = W_train[i] * (0.5/sum_wpos)
    else:
        W_train[i] = W_train[i] * (0.5/sum_wneg)

        
W_train_av = sum(W_train)/len(W_train)
W_test_av = sum(W_train)/len(W_train)

print ('Weights average',W_train_av,W_test_av)

W_train = W_train/W_train_av
W_test = W_test/W_test_av
        
sum_wpos_check = sum( W_train[i] for i in range(len(label_train)) if label_train[i] == 1.0  )
sum_wneg_check = sum( W_train[i] for i in range(len(label_train)) if label_train[i] == 0.0  )

# print weight statistics
print ('weight statistics: wpos=%g, wneg=%g, ratio=%g' % ( sum_wpos_check, sum_wneg_check, sum_wneg_check/sum_wpos_check ))


# define the keras model
model = Sequential()
model.add(Dense(256, input_dim=variable_size, activation='selu', kernel_initializer='lecun_normal'))
model.add(AlphaDropout(0.4))
model.add(Dense(256, activation='selu', kernel_initializer='lecun_normal'))
model.add(AlphaDropout(0.3))
model.add(Dense(256, activation='selu', kernel_initializer='lecun_normal'))
model.add(AlphaDropout(0.3))
model.add(Dense(1, activation='sigmoid'))
# compile the keras model
#opt = SGD(lr=0.1, momentum=0.9)
#opt = RMSprop(learning_rate=0.001, rho=0.9)
opt = Adam(learning_rate=1e-03, beta_1=0.9, beta_2=0.999, amsgrad=False)
model.compile(loss='binary_crossentropy', optimizer=opt, metrics=['accuracy'])
# fit the keras model on the dataset
model.fit(X_train, label_train, sample_weight = W_train, validation_data=(X_test, label_test), epochs=42, batch_size=256, shuffle=True)
# evaluate the keras model
_, accuracy = model.evaluate(X, label)
print('Accuracy: %.2f' % (accuracy*100))
model.save(output_model_name)
model.save_weights(output_weights_name)

print ("Storing into NTuple---------------------------------------\n")
Ypred_train = model.predict( X_train )
Ypred_test = model.predict( X_test )

from ROOT import TFile, TTree
from array import array

class_id = array('i', [ 0 ] )
variables = variable_size*[0]
for i in range(variable_size):
    variables[i] = array('f', [ 0. ] )
weight = array('f', [ 0. ] )
score = array('f', [ 0. ] )

f = TFile(output_file_name,'recreate')
t1 = TTree('TestTree','Tree for Test Data')
t2 = TTree('TrainTree','Tree for Training Data')

variable_names=mvasup.CorrectNames(variable_names)

t1.Branch('class_id',class_id,'class_id/I')
for i in range(variable_size):
    t1.Branch(variable_names[i],variables[i],variable_names[i]+'/F')
t1.Branch('weight',weight,'weight/F')
t1.Branch('score',score,'score/F')

t2.Branch('class_id',class_id,'class_id/I')
for i in range(variable_size):
    t2.Branch(variable_names[i],variables[i],variable_names[i]+'/F')
t2.Branch('weight',weight,'weight/F')
t2.Branch('score',score,'score/F')


for i in range(len(label_test)):
    class_id[0] = int(label_test[i])
    for j in range(variable_size):
        variables[j][0] = Xor_test[i][j]
    weight[0] = Wor_test[i]
    score[0] = Ypred_test[i]
    t1.Fill()

for i in range(len(label_train)):
    class_id[0] = int(label_train[i])
    for j in range(variable_size):
        variables[j][0] = Xor_train[i][j]
    weight[0] = Wor_train[i]
    score[0] = Ypred_train[i]
    t2.Fill()

t1.Write()
t2.Write()

f.Write()
f.Close()


print ("Storing the data has been done..------------------------")
