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

from itertools import accumulate
import numpy as np
import csv

# Assign classes to commong protocol field types

flags = ["OTH", "REJ", "RSTO", "RSTOS0", "RSTR", "S0", "S1", "S2", "S3", "SF", "SH"]
flags_dict = dict(zip(flags, range(len(flags))))

services = [
    "aol", "auth", "bgp", "courier", "csnet_ns", "ctf", "daytime", "discard", "domain", "domain_u", "echo", "eco_i", "ecr_i", "efs",
    "exec", "finger", "ftp", "ftp_data", "gopher", "harvest", "hostnames", "http", "http_2784", "http_443", "http_8001", "imap4",
    "IRC", "iso_tsap", "klogin", "kshell", "ldap", "link", "login", "mtp", "name", "netbios_dgm", "netbios_ns", "netbios_ssn",
    "netstat", "nnsp", "nntp", "ntp_u", "other", "pm_dump", "pop_2", "pop_3", "printer", "private", "red_i", "remote_job", "rje",
    "shell", "smtp", "sql_net", "ssh", "sunrpc", "supdup", "systat", "telnet", "tftp_u", "time", "tim_i", "urh_i", "urp_i", "uucp",
    "uucp_path", "vmnet", "whois", "X11", "Z39_50"
    ]
services_dict = dict(zip(services, range(len(services))))

protocol_types = ["udp", "tcp", "icmp"]
proto_dict = dict(zip(protocol_types, range(len(protocol_types))))


# Functions for analyzing dataset distribution

def sample_flow_size(n_field_dist, n_flow_dist, a_field_dist, a_flow_dist, attack, const=True):

    sample = None
    if const == True:
        sample = 5
    else:
        if (int(attack)==1):
            sample = np.random.choice(a_flow_dist, 1)[0]
        else:
            sample = np.random.choice(n_flow_dist, 1)[0]

    return sample


def split_conn_2_pkts(n_field_dist, n_flow_dist, a_field_dist, a_flow_dist, conn, fields, attack):

    split_conn = []
    num_bins = sample_flow_size(n_field_dist, n_flow_dist, a_field_dist, a_flow_dist, attack, False)
    dist = 'empirical' # 'uniform'

    for field, pkt in enumerate(fields):
        split_field = None
        if (pkt==True):
            if (field == 0):
                split_field = get_incremented_fields(n_field_dist, n_flow_dist, a_field_dist, a_flow_dist, 
                                                     num_bins, conn[field], field, 'float', dist, attack)
            else:
                split_field = get_incremented_fields(n_field_dist, n_flow_dist, a_field_dist, a_flow_dist, 
                                                     num_bins, conn[field], field, 'int', dist, attack)
        else:
            split_field = num_bins * [conn[field]]
        split_conn.append(split_field)

    return np.array(split_conn).T.tolist()
    

def get_incremented_fields(n_field_dist, n_flow_dist, a_field_dist, a_flow_dist, num_bins, max_val, field_idx, type='int', dist='uniform', attack=0):

    field = num_bins * [0]    
    incs = sample_dist(n_field_dist, n_flow_dist, a_field_dist, a_flow_dist, dist, num_bins, max_val, type, field_idx, attack)    
    for idx, pkt in enumerate(field):
        field[idx] = min(field[idx] + incs[idx], max_val)
        if (idx == (len(field)-1)):
            field[idx] = max_val
            
    return field


def sample_dist(n_field_dist, n_flow_dist, a_field_dist, a_flow_dist, dist, num_bins, max_val, type, field, attack):

    samples = None
    if (dist == 'uniform'):
        samples = get_uniform_inc(num_bins, max_val, type)
    elif(dist == 'empirical'):
        samples = get_sampled_inc(n_field_dist, n_flow_dist, a_field_dist, a_flow_dist, num_bins, field, attack)

    return samples


def get_sampled_inc(n_field_dist, n_flow_dist, a_field_dist, a_flow_dist, num_bins, field_idx, attack):

    samples = None

    # Duration
    if (field_idx == 0):
        if (int(attack)==1):
            samples = np.random.choice(a_field_dist[5], num_bins)
        else:
            samples = np.random.choice(n_field_dist[5], num_bins)

    # Src bytes    
    elif (field_idx == 3):
        if (int(attack)==1):
            samples = np.random.choice(a_field_dist[2], num_bins)
        else:
            samples = np.random.choice(n_field_dist[2], num_bins)
        
    # Dst bytes    
    elif (field_idx == 4):
        if (int(attack)==1):
            samples = np.random.choice(a_field_dist[3], num_bins)
        else:
            samples = np.random.choice(n_field_dist[3], num_bins)

    # Wrong fragment
    elif (field_idx == 5):
        if (int(attack)==1):
            samples = np.random.choice(a_field_dist[4], num_bins)
        else:
            samples = np.random.choice(n_field_dist[4], num_bins)
    
    # Urgent
    elif (field_idx == 6):
        if (int(attack)==1):
            samples = np.random.choice(a_field_dist[1], num_bins)
        else:
            samples = np.random.choice(n_field_dist[1], num_bins)

    return list(accumulate(samples.tolist()))


def get_uniform_inc(num_bins, max_val, type):

    inc_norm = 0
    if (type == 'int'):
        inc_norm = max(int(round(max_val / num_bins)), 1)
    else:
        inc_norm = (1.0*max_val) / num_bins

    sampled_incs = []
    for i in range(num_bins):
        sampled_incs.append((i + 1) * inc_norm)
     
    return sampled_incs


def get_field_dist(filename):
 
    stats = []
    with open(filename, newline='\n') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=',')
        i = 0
        for row in spamreader:
            if (not(i == 0)):
                bin = []
                for idx, item in enumerate(row):
                    if (idx == 0):
                        bin.append(int(item))
                    elif (idx == 1):
                        bin.append(int(item))
                    elif (idx == 2):
                        bin.append(int(item))
                    elif (idx == 3):
                        bin.append(int(item))
                    elif (idx == 4):
                        bin.append(int(item))
                    elif (idx == 5):
                        bin.append(float(item))
                stats.append(bin)    
            i = i + 1
        
    return np.array(stats).T.tolist()


def get_flow_dist(filename):
    # analyze flow distribution in the given file
    stats = []
    with open(filename, newline='\n') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=',')
        for row in spamreader:
            for item in row:
                if (not(item=='0')):
                    if not(item==''):
                        stats.append(int(float(item)))
    
    return stats
