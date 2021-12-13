#~~ TRAIN_NN.PY ~~# 
# Will write this later
rootpath = "/vols/cms/fjo18/Masters2021"

# Training parameters
batch_size = 2000 #1024
stop_patience = 20
no_epochs = 200
learningrate = 0.01

# Model architecture parameters
#dense_layers = [(4,128, False), (2, 54, False)]
dense_layers = [(6,22, False), (0, 40, False)]
conv_layers = [(0,4), (0,3)]
HL_shape = (21,)
im_l_shape = (21,21,1)
im_s_shape = (11,11,1)
inc_dropout = True
dropout_rate = [0.1, 0.5]
use_inputs = [True, True, True]
# A mask to check which inputs to use for the model - above indicates HL only


import datetime
from math import ceil
model_datetime = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

# cache_dataset = True
view_model = False
# DOESN'T WORK - HAVE TO INSTALL IF NECESSARY
save_model = False
small_dataset = True
small_dataset_size = 100000

training_parameters = [batch_size, conv_layers, dense_layers, inc_dropout, \
    dropout_rate, use_inputs, learningrate, no_epochs, stop_patience, save_model, small_dataset]
training_parameter_names = ["batch size", "conv layers", "dense layers", "include dropout?", \
    "dropout rate", "inputs mask", "learning rate", "no. epochs", "stop patience", "save model?", "small dataset?"]

# Load packages
import numpy as np
import pandas as pd
from sklearn.metrics import classification_report, roc_curve, roc_auc_score
import tensorflow as tf
#tf.debugging.set_log_device_placement(True)
# Code will now print the device on which it is running
from tensorflow import TensorSpec
from tensorflow import keras
from tensorflow import Tensor
from tensorflow.keras import layers
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, BatchNormalization, Normalization, Dropout
from tensorflow.keras.callbacks import EarlyStopping
from tensorflow.keras.wrappers.scikit_learn import KerasRegressor
from tensorflow.keras.optimizers import Adam
from sklearn.model_selection import cross_val_score
from sklearn.model_selection import KFold
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.metrics import accuracy_score
from tensorflow.keras.callbacks import History 
from tensorflow.keras.utils import normalize, plot_model

import time

# load data

y_train = pd.read_pickle(rootpath + "/DataFrames/y_train_df.pkl")
y_test = pd.read_pickle(rootpath + "/DataFrames/y_test_df.pkl")

l_im_train = []
l_im_test = []
s_im_train = []
s_im_test = []
X_train = []
X_test = []
# These need to be here so that the later operations don't break when you only use some inputs
if use_inputs[0]:
    l_im_train = np.load(rootpath + "/DataFrames/im_l_array_train.npy")
    l_im_test = np.load(rootpath + "/DataFrames/im_l_array_test.npy")
if use_inputs[1]:
    s_im_train = np.load(rootpath + "/DataFrames/im_s_array_train.npy")
    s_im_test = np.load(rootpath + "/DataFrames/im_s_array_test.npy")
if use_inputs[2]:
    X_train = pd.read_pickle(rootpath + "/DataFrames/X_train_df.pkl")
    X_test = pd.read_pickle(rootpath + "/DataFrames/X_test_df.pkl")




if small_dataset:
    test_size = int(small_dataset_size*.8)
    train_size = int(small_dataset_size*.2)
    X_train = X_train.head(test_size)
    X_test = X_test.head(train_size)
    y_train = y_train[:test_size]
    y_test = y_test[:train_size]
    l_im_train = l_im_train[:test_size]
    l_im_test = l_im_test[:train_size]
    s_im_train = s_im_train[:test_size]
    s_im_test = s_im_test[:train_size]


train_full_inputs = [l_im_train, s_im_train, X_train]
test_full_inputs = [l_im_test, s_im_test, X_test]
train_inputs = []
test_inputs = []
for a in range(len(use_inputs)):
    if use_inputs[a]:
        train_inputs.append(train_full_inputs[a])
        test_inputs.append(test_full_inputs[a])
# Setting up inputs based on the mask





# X_train = tf.data.experimental.load(rootpath + "/Tensors/X_train_tensor", element_spec = TensorSpec(shape=(20,), dtype=tf.float64, name=None)).batch(batch_size)
# X_test = tf.data.experimental.load(rootpath + "/Tensors/X_test_tensor", element_spec = TensorSpec(shape=(20,), dtype=tf.float64, name=None)).batch(batch_size)
# y_train = tf.data.experimental.load(rootpath + "/Tensors/y_train_tensor", element_spec = TensorSpec(shape=(6,), dtype=tf.float32, name=None)).batch(batch_size)
# y_test = tf.data.experimental.load(rootpath + "/Tensors/y_test_tensor", element_spec = TensorSpec(shape=(6,), dtype=tf.float32, name=None)).batch(batch_size)

# l_im_train = tf.data.experimental.load(rootpath + "/Tensors/l_im_train_tensor", element_spec = TensorSpec(shape=(21,21), dtype=tf.uint8, name=None)).batch(batch_size)
# l_im_test = tf.data.experimental.load(rootpath + "/Tensors/l_im_test_tensor", element_spec = TensorSpec(shape=(21,21), dtype=tf.uint8, name=None)).batch(batch_size)
# s_im_train = tf.data.experimental.load(rootpath + "/Tensors/s_im_train_tensor", element_spec = TensorSpec(shape=(11,11), dtype=tf.uint8, name=None)).batch(batch_size)
# s_im_test = tf.data.experimental.load(rootpath + "/Tensors/s_im_test_tensor", element_spec = TensorSpec(shape=(11,11), dtype=tf.uint8, name=None)).batch(batch_size)

# train_inputs = tf.data.Dataset.zip((l_im_train, s_im_train, X_train))
# test_inputs = tf.data.Dataset.zip((l_im_test, s_im_test, X_test))
# # combining three input variables into an object

# train_batch = tf.data.Dataset.zip((train_inputs, y_train))
# test_batch = tf.data.Dataset.zip((test_inputs, y_test))
# # Combining input variables with flags

# train_batch = train_batch.prefetch(tf.data.AUTOTUNE)
# test_batch = test_batch.prefetch(tf.data.AUTOTUNE)
# # prefetching a number of batches, to make loading more efficient possibly

# if cache_dataset:
#     train_batch = train_batch.cache()
#     test_batch = test_batch.cache()
#     print('caching dataset')
# # caching may well save loading time but not sure yet - for image based the cache does not fit in memory
# # may have to partially cache instead of caching entire dataset (i.e. only cache HL variables or something)

# create model

def relu_bn(inputs: Tensor) -> Tensor:
    relu = layers.ReLU()(inputs)
    bn = layers.BatchNormalization()(relu)
    return bn

def CNN_creator_3input(inputshape_l, inputshape_s, inputshape_hl, convlayers, denselayers, dropout_rate, \
                       kernelsize = (3,3), learningrate = 0.001, input_mask = [True,True,True], input_norm = False,\
                            model_image = False, dropout = True):
    # Inputshape should be a 3-comp tuple, where 1st two els are height x width and 3rd is no. layers
    # conv/denselayers denote number of convolutional and dense layers in network
    # convlayers should be a tuple
    # dense layers is 2x2 matrix, first val for dense layers for only HL, second is for the final dense layers
    # - second val in each tuple is the width of the dense layer
    # dense necessarily come after convolutional
    
    # PARSE INPUT VARIABLES #
    poolingsize = (2,2)
    no_conv_layers_l_flat = convlayers[0][0]
    no_conv_layers_s_flat = convlayers[1][0]
    no_conv_layers_l_pool = convlayers[0][1]
    no_conv_layers_s_pool = convlayers[1][1]

    conv_dropout_rate = dropout_rate[0]
    dense_dropout_rate = dropout_rate[1]

    no_dense_hl = denselayers[0][0]
    width_dense_hl = denselayers[0][1]
    decrease_dense_hl = denselayers[0][2]
    no_dense_full = denselayers[1][0]
    width_dense_full = denselayers[1][1]
    decrease_dense_full = denselayers[1][2]

    # INPUTS #
    image_input_l = keras.Input(shape = inputshape_l, name = "L_Input")
    y_l = image_input_l
    image_input_s = keras.Input(shape = inputshape_s, name = "S_Input")
    y_s = image_input_s
    input_hl = keras.Input(shape = inputshape_hl, name = "HL_Input")
    if input_norm:
        y_hl = layers.Normalization(name = 'HL_Norm_Input')(input_hl)
    else:
        y_hl = input_hl
    # Normalise the hl inputs (feature wise) before running them
    
    # CONVOLUTIONAL LAYERS #
        
    for a in range(no_conv_layers_l_flat):
        conv_l = layers.Conv2D(32 *(a+1), kernelsize, padding="same", name = "L_Conv_Flat_" + str(a))(y_l)
        y_l = relu_bn(conv_l)
        if dropout:
            y_l = layers.Dropout(conv_dropout_rate, name = "L_Dropout_Flat_" + str(a))(y_l)
        
    for a in range(no_conv_layers_s_flat):
        conv_s = layers.Conv2D(32*(a+1), kernelsize, padding="same", name = "S_Conv_Flat_" + str(a))(y_s)
        y_s = relu_bn(conv_s)
        if dropout:
            y_s = layers.Dropout(conv_dropout_rate, name = "S_Dropout_Flat_" + str(a))(y_s)

    for a in range(no_conv_layers_l_pool):
        conv_l = layers.Conv2D(32 *(a+1), kernelsize, padding="same", name = "L_Conv_Pool_" + str(a))(y_l)
        bn_l = relu_bn(conv_l)
        y_l = layers.MaxPooling2D(pool_size=poolingsize, name = "L_Pooling_" + str(a))(bn_l)
        if dropout:
            y_l = layers.Dropout(conv_dropout_rate, name = "L_Dropout_Pool_" + str(a))(y_l)

    for a in range(no_conv_layers_s_pool):
        conv_s = layers.Conv2D(32*(a+1), kernelsize, padding="same", name = "S_Conv_Pool_" + str(a))(y_s)
        bn_s = relu_bn(conv_s)
        y_s = layers.MaxPooling2D(pool_size=poolingsize, name = "S_Pooling_" + str(a))(bn_s)
        if dropout:
            y_s = layers.Dropout(conv_dropout_rate, name = "S_Dropout_Pool_" + str(a))(y_s)
        
    # DENSE LAYERS #

    for a in range(no_dense_hl):
        if decrease_dense_hl:
            x_hl = layers.Dense(ceil(width_dense_hl * 0.5 **(a)), name = "HL_hidden_" + str(a))(y_hl)
            # Layers get smaller and smaller
        else:
            x_hl = layers.Dense(width_dense_hl, name = "HL_hidden_" + str(a))(y_hl)
            # Layers stay same size

        y_hl = relu_bn(x_hl)
        if dropout:
            y_hl = layers.Dropout(dense_dropout_rate, name = "HL_Dropout_" + str(a))(y_hl)
        # Added dropout layers into dense (09.12.21)

    # COMBINE INPUTS #
    
    x_l = layers.Flatten(name = "L_Flatten")(y_l)
    x_s = layers.Flatten(name = "S_Flatten")(y_s)
    # Flatten output into 1D, so can be applied to dense layers more easily
    
    # Distinguish based on input_mask which inputs are used
    x_full = [x_l, x_s, y_hl]
    full_inputs = [image_input_l, image_input_s, input_hl]
    model_concat = []
    model_inputs = []
    for a in range(len(input_mask)):
        if input_mask[a]:
            model_concat.append(x_full[a])
            model_inputs.append(full_inputs[a])

    x = layers.concatenate(model_concat)

    # FINAL DENSE LAYERS #
    for a in range(no_dense_full):
        if decrease_dense_full:
            y = layers.Dense(ceil(width_dense_full * 0.5 **a), name = "Full_hidden_" + str(a))(x)
        else:
            y = layers.Dense(width_dense_full, name = "Full_hidden_" + str(a))(x)

        x = relu_bn(y)
        if dropout:
            x = layers.Dropout(dense_dropout_rate, name = "Full_Dropout_" + str(a))(x)
    
    # OUTPUT LAYER #
    outputs = layers.Dense(6, name = "Outputs", activation = "softmax")(x)


    model = keras.Model(inputs=model_inputs, outputs=outputs)
    model.compile(loss="mean_squared_error", optimizer=Adam(learning_rate=learningrate), metrics=["accuracy"],)
    model.summary()
    if model_image:
        plot_model(model, to_file='model_plot.png', show_shapes=True, show_layer_names=True)
    return model

model = CNN_creator_3input(im_l_shape, im_s_shape, HL_shape, conv_layers, dense_layers, \
                           dropout_rate, learningrate = learningrate, input_mask = use_inputs, \
                               model_image=view_model, dropout=inc_dropout)

early_stop = EarlyStopping(monitor = 'val_loss', patience = stop_patience)
history = History()

# fit model
time_start = time.time()
print("Training model")
for a, b in zip(training_parameters, training_parameter_names):
    print(b,':', a)
#print(training_parameters)

model.fit(train_inputs, y_train,
          batch_size = batch_size,
          epochs = no_epochs,
          callbacks=[history, early_stop],
          validation_data = (test_inputs, y_test)) 


prediction = model.predict(test_inputs)
idx = prediction.argmax(axis=1)
y_pred = (idx[:,None] == np.arange(prediction.shape[1])).astype(float)
flatpred = np.argmax(y_pred, axis=-1)
flattest = np.argmax(y_test, axis=-1)
accuracy = accuracy_score(y_test, y_pred)
print(accuracy)

if save_model:
    param_file = open(rootpath + "/Models/Full_model_%.3f_%s_params.txt" % (accuracy, model_datetime), 'w')
    model.save(rootpath + "/Models/Full_model_%.3f_%s" % (accuracy, model_datetime))
    for a in training_parameters:
        param_file.write(str(a) + '\n')
    param_file.write(accuracy + '\n')
    param_file.close()
    # Saves model parameters in a corresponding .txt file


time_elapsed = time.time() - time_start 
time_start = time.time()
print("elapsed time = " + str(time_elapsed))

