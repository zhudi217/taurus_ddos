# *************************************************************************
#
# Copyright 2022 Tushar Swamy (Stanford University),
#                Alexander Rucker (Stanford University),
#                Annus Zulfiqar (Purdue University),
#                Muhammad Shahbaz (Stanford/Purdue University)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# *************************************************************************

import os
import sys
import csv
import timeit
import argparse
import itertools
import numpy as np
from helper import *
import tensorflow as tf
from sklearn import metrics
from tensorflow import keras
from os.path import expanduser
from keras import backend as K
import matplotlib.pyplot as plt
from keras.optimizers import Adam
from keras.models import Sequential
from keras.layers import Dense, Activation

# Global variables for testing Setup
TRAIN_TEST_SPLIT = 0.8
BATCH_SIZE = 1024
NUM_FEATURES = 7
EPOCHS = 30

# global variables for analyzing the flow distribution of our dataset
FREQUENCY = 1000
N_FIELD_DIST = None
N_FLOW_DIST = None
A_FIELD_DIST = None
A_FLOW_DIST = None


def load_data(dataset, write=False, filename='test.csv'):
    full_data, full_labels = [], []
    with open(dataset, newline='\n') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=',')
        for row in spamreader:
            label = row.pop(41)
            full_labels.append(label)
            full_data.append(row)

    def label_multiclass(label):
        mc_label = [0,0]
        if (label == 'normal'):
            mc_label[0] = 1
        else:
            mc_label[1] = 1
        return mc_label

    binary_labels = list(map(lambda label: label_multiclass(label), full_labels))

    def categorize(data_pt):
        data_pt[1] = proto_dict[data_pt[1]]
        data_pt[2] = services_dict[data_pt[2]]
        data_pt[3] = flags_dict[data_pt[3]]
        float_pt = list(map(lambda pt: float(pt), data_pt))
        return float_pt

    def prune(data_pt):
        pruned_pt = [0] * NUM_FEATURES
        pruned_pt[0] = data_pt[0] # duration
        pruned_pt[1] = data_pt[1] # proto
        pruned_pt[2] = data_pt[2] # service
        pruned_pt[3] = data_pt[4] # src_bytes
        pruned_pt[4] = data_pt[5] # dst bytes
        pruned_pt[5] = data_pt[7] # wrong fragment
        pruned_pt[6] = data_pt[8] # urgent
        return pruned_pt

    floatified_data = list(map(lambda data_pt: categorize(data_pt), full_data))
    cleaned_data = list(map(lambda data_pt: prune(data_pt), floatified_data))

    datalen = len(cleaned_data)
    pkt_data, pkt_labels = [], []

    print("*** Generating New Data ***")
    
    for idx, conn in enumerate(cleaned_data):
        if idx > 0 and idx % 10000 == 0:
            print(f"On datapoint: {str(idx)}/{str(datalen)}")
        ad_label = np.argmax(binary_labels[idx])
        pkts = split_conn_2_pkts(N_FIELD_DIST, N_FLOW_DIST, A_FIELD_DIST, A_FLOW_DIST, conn, [False]*NUM_FEATURES, ad_label)
        for pkt in pkts:
            pkt_data.append(pkt)
            pkt_labels.append(binary_labels[idx])
    
    if write:
        with open(filename, 'w+') as csvfile:
            spamwriter = csv.writer(csvfile, delimiter=",", quotechar='|', quoting=csv.QUOTE_MINIMAL)
            for pd_idx, row in enumerate(pkt_data):
                row.append(pkt_labels[pd_idx])
                spamwriter.writerow(row)
    
    print(f"Feature Size = {len(pkt_data[0])}")
    
    # Shuffle data and split into training and test sets
    print("*** Shuffling the Dataset Before Training ***")
    temp_data = list(zip(pkt_data, pkt_labels))
    np.random.shuffle(temp_data)
    pkt_data, pkt_labels = list(zip(*temp_data))
    pkt_data = list(pkt_data)
    pkt_labels = list(pkt_labels)
    
    # Split the dataset into training/testing sets
    train_start, train_stop = 0, int(TRAIN_TEST_SPLIT * len(pkt_data))
    test_start, test_stop = train_stop, len(pkt_data)

    # Get training examples and labels
    trainX = pkt_data[train_start:train_stop]
    trainY = pkt_labels[train_start:train_stop]

    # Get test examples and labels
    testX = pkt_data[test_start:test_stop]
    testY = pkt_labels[test_start:test_stop]

    print("Number of Training Samples = {0}; Number of Test Samples = {1}".format(len(trainX), len(testX)))
    
    return trainX, trainY, testX, testY, len(trainX[0])


# Define Recall, Precision and F1 metrics for training the Neural Network
def recall_metric(y_true, y_pred):
    true_positives = K.sum(K.round(K.clip(y_true * y_pred, 0, 1)))
    possible_positives = K.sum(K.round(K.clip(y_true, 0, 1)))
    recall = true_positives / (possible_positives + K.epsilon())
    return recall


def precision_metric(y_true, y_pred):
    true_positives = K.sum(K.round(K.clip(y_true * y_pred, 0, 1)))
    predicted_positives = K.sum(K.round(K.clip(y_pred, 0, 1)))
    precision = true_positives / (predicted_positives + K.epsilon())
    return precision


def F1_metric(y_true, y_pred):
    precision = precision_metric(y_true, y_pred)
    recall = recall_metric(y_true, y_pred)
    return 2*((precision*recall)/(precision+recall+K.epsilon()))


def create_fc_network(config, input_size):
    # create a dnn model according to configurations
    model = Sequential()    
    for layer_idx, num_hidden_units in enumerate(config):
        if layer_idx == 0:
            model.add(Dense(num_hidden_units, input_dim=input_size, activation='relu'))
        else:
            model.add(Dense(num_hidden_units, activation='relu'))

    # the output layer will perform binary classification
    model.add(Dense(2, activation='softmax'))
    model.compile(loss='categorical_crossentropy', optimizer=Adam(learning_rate=0.001), 
                  metrics=['acc'])

    return model


def train_model(model, epochs, trainX, trainY, batch, save_model=False, write_luts=False, path='.'):
    # Fit the model on training set
    model.fit(np.reshape(trainX, (len(trainX), len(trainX[0]))), 
              np.reshape(trainY, (len(trainY), len(trainY[0]))), 
              epochs=epochs, batch_size=batch, verbose=1)
    
    if save_model:
        model.save(path + '/ad-model')

    # Write trained model luts to output directory
    if write_luts:
        dirname = path + "/" + "params/"

        if not(os.path.isdir(dirname)):
            os.mkdir(dirname)

        for idx, layer in enumerate(model.layers):
            weight_file = dirname + "L" + str(idx) + "_W" + ".csv"
            bias_file = dirname + "L" + str(idx) + "_B" + ".csv"
            layer_params = layer.get_weights()
            weights = layer_params[0]
            weights = weights.transpose([1,0])
            bias = layer_params[1]
            bias = bias.reshape(-1, len(bias)).transpose([1,0])

            with open(weight_file, 'w+') as csvfile:
                spamwriter = csv.writer(csvfile, delimiter=",", quotechar='|', quoting=csv.QUOTE_MINIMAL)
                for neuron in weights:
                    row = []
                    for weight in neuron:
                        row.append(str(weight))
                    spamwriter.writerow(row)

            with open(bias_file, 'w+') as csvfile:
                spamwriter = csv.writer(csvfile, delimiter=",", quotechar='|', quoting=csv.QUOTE_MINIMAL)
                for neuron in bias:
                    row = []
                    for weight in neuron:
                        row.append(str(weight))

                    spamwriter.writerow(row)

    return model


def get_metrics(model, testX, testY, batch):
    print("\nTesting the trained model..")
    y = model.predict(np.reshape(testX, np.shape(testX)), batch_size=batch)
    predicted_labels = np.argmax(y, 1)
    true_labels = np.argmax(testY, 1)
    
    # Get F1 Score, Precision, Recall and Accuracy on the test set
    accuracy = 100*metrics.accuracy_score(true_labels, predicted_labels)
    precision = 100*metrics.precision_score(true_labels, predicted_labels, average="weighted", labels=np.unique(predicted_labels))
    recall = 100*metrics.recall_score(true_labels, predicted_labels, average="weighted")
    f1 = 100*metrics.f1_score(true_labels, predicted_labels, average="weighted", labels=np.unique(predicted_labels))

    print("\nTesting the model on unseen data..")
    print("Weighted Accuracy: {0:.2f}".format(accuracy))
    print("Weighted Precision: {0:.2f}".format(precision))
    print("Weighted Recall: {0:.2f}".format(recall))
    print("Weighted F1-Score: {0:.2f}".format(f1))
    
    tn, fpo, fn, tp = metrics.confusion_matrix(true_labels, predicted_labels).ravel()
    print("\nConfusion Matrix on Test Set:")
    print("TN ", str(tn))
    print("FP: ", str(fpo))
    print("FN: ", str(fn))
    print("TP: ", str(tp))

    return accuracy
    

def main(build_dir):
    training_set = "data/kdd_dataset.txt"
    
    # Analyze the data distribution    
    print("*** Reading Stat Distributions ***")
    global FREQUENCY, N_FIELD_DIST, N_FLOW_DIST, A_FIELD_DIST, A_FLOW_DIST
    N_FIELD_DIST = get_field_dist('data/darpa99/week1/monday/csv/pd_flows_' + str(FREQUENCY) + '.csv')
    N_FLOW_DIST = get_flow_dist('data/darpa99/week1/monday/csv/pd_flow_bins_per_sample_window_' + str(FREQUENCY) + '.csv')

    A_FIELD_DIST = get_field_dist('data/darpa99/week2/monday/csv/pd_flows_' + str(FREQUENCY) + '.csv')
    A_FLOW_DIST = get_flow_dist('data/darpa99/week2/monday/csv/pd_flow_bins_per_sample_window_' + str(FREQUENCY) + '.csv')
    
    # Read training data from the CSV files
    print("*** Reading Training Data ***")
    tnx, tny, tsx, tsy, input_size = load_data(dataset=training_set)

    # Define our DNN model
    MODEL_CONFIG = [12, 6, 3]
    dnn_config = list(map(int, MODEL_CONFIG))
    print("*** Creating Model ***")
    print("DNN Config=", dnn_config)
    model = create_fc_network(dnn_config, input_size)

    # Train and test our model
    print("*** Training Model ***")
    model = train_model(model, EPOCHS, tnx, tny, BATCH_SIZE, True, True, build_dir)

    # Get test results on unseen data
    get_metrics(model, tsx, tsy, BATCH_SIZE)
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Training Script')
    parser.add_argument('--build-dir', type=str, action="store", default="build")
    args = parser.parse_args()
    
    main(args.build_dir)