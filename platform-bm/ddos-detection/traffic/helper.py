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

from sklearn import metrics
from scapy.all import *
import numpy as np


# Feature Header Protocol for Scapy
class CustomHeader(Packet):
    name = "Custom Header"      # ML Features and timestamp
    fields_desc = [
        IntField("field0", 0),    # DNN Input Feature 0
        IntField("field1", 0),    # DNN Input Feature 1
        IntField("field2", 0),    # DNN Input Feature 2
        IntField("field3", 0),    # DNN Input Feature 3
        IntField("field4", 0),    # DNN Input Feature 4
        ByteField("label", 0),   # DNN Label (Ground Truth)
        ByteField("output", 0),    # DNN Output
        BitField("h2mr_ingress", 0, 48),
        BitField("h2mr_egress", 0, 48),
        BitField("mr2h_ingress", 0, 48),
        BitField("mr2h_egress", 0, 48)
    ]  # DNN Output


bind_layers(IP, CustomHeader, proto=254)


# Function of calculating DNN metrics
def calc_metrics(pred_outputs=[], true_labels=[]):
    accuracy = 100 * metrics.accuracy_score(true_labels, pred_outputs)
    precision = 100 * metrics.precision_score(true_labels, pred_outputs, average="weighted", labels=np.unique(pred_outputs))
    recall = 100 * metrics.recall_score(true_labels, pred_outputs, average="weighted")
    f1 = 100 * metrics.f1_score(true_labels, pred_outputs, average="weighted", labels=np.unique(pred_outputs))

    print("Weighted Accuracy Across 2 Classes: {0:.2f}".format(accuracy))
    print("Weighted Precision Across 2 Classes: {0:.2f}".format(precision))
    print("Weighted Recall Across 2 Classes: {0:.2f}".format(recall))
    print("Weighted F1-Score Across 2 Classes: {0:.2f}".format(f1))
    print("")
