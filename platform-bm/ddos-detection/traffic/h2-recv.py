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

import signal

signal.signal(signal.SIGINT, lambda signum, frame: exit(1))

from scapy.all import *
from helper import *

MAX_PKT_COUNT = 60

# Parse and process incoming packets
run_pkt_count = 0
pred_outputs = list()
true_labels = list()

h2mr_inlist = list()
h2mr_elist = list()
mr2h_inlist = list()
mr2h_elist = list()


def parse_output(pkt):
    global run_pkt_count, pred_outputs, true_labels

    run_pkt_count += 1

    pred_outputs.append(pkt[CustomHeader].output)
    true_labels.append(pkt[CustomHeader].label)

    # Calculate metrics for every 60 packets
    if run_pkt_count % MAX_PKT_COUNT == 0:
	print("Received {} packets.".format(run_pkt_count))
    #     print("Received {0} packets.".format(MAX_PKT_COUNT))

    #     calc_metrics(pred_outputs, true_labels)

    #     run_pkt_count = 0
    #     pred_outputs = list()
    #     true_labels = list()

    h2mr_inlist.append(pkt[CustomHeader].h2mr_ingress)
    h2mr_elist.append(pkt[CustomHeader].h2mr_egress)
    mr2h_inlist.append(pkt[CustomHeader].mr2h_ingress)
    mr2h_elist.append(pkt[CustomHeader].mr2h_egress)

    if len(h2mr_inlist) == 600:
	print("Saving!")
        with open('h2mr_in.txt', 'a') as tfile1:
            tfile1.write('\n'.join([str(ele) for ele in h2mr_inlist]))
	    tfile1.write('\n')
        with open('h2mr_e.txt', 'a') as tfile2:
            tfile2.write('\n'.join([str(ele) for ele in h2mr_elist]))
	    tfile2.write('\n')
        with open('mr2h_in.txt', 'a') as tfile3:
            tfile3.write('\n'.join([str(ele) for ele in mr2h_inlist]))
	    tfile3.write('\n')
        with open('mr2h_e.txt', 'a') as tfile4:
            tfile4.write('\n'.join([str(ele) for ele in mr2h_elist]))
	    tfile4.write('\n')
	exit(1)


# Sniff packets with feature headers
while True:
    sniff(iface='h2-eth0', prn=lambda x: parse_output(x), count=MAX_PKT_COUNT,
          lfilter=lambda x: (IP in x) and (x[IP].proto == 254))
