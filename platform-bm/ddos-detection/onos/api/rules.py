#!/usr/bin/env python3

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

import argparse
from collections import defaultdict

from utils.rest import install_rule, delete_rule


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Mininet (Single Switch Topology)')
    parser.add_argument('--bypass', action="store_true")
    parser.add_argument('--enable', action="store_true")
    parser.add_argument('--disable', action="store_true")
    args = parser.parse_args()

    if args.bypass:
        install_rule(table="forward", is_permanent=True, priority=40, ingress_port=1, output=2)
        install_rule(table="forward", is_permanent=True, priority=40, ingress_port=2, output=1)

    if args.enable:
        install_rule(table="forward", is_permanent=True, priority=40, ingress_port=1, output=4)
        install_rule(table="forward", is_permanent=True, priority=40, ingress_port=3, output=2)
        install_rule(table="forward", is_permanent=True, priority=40, ingress_port=2, output=1)  # bypass MapReduce on the reverse path

        install_rule(table="fxpt_format", egress_port=4, is_permanent=True)
    
    if args.disable:
        delete_rule(table="forward", ingress_port=1)
        delete_rule(table="forward", ingress_port=2)
        delete_rule(table="forward", ingress_port=3)
        delete_rule(table="forward", ingress_port=4)

        delete_rule(table="fxpt_format", egress_port=4)
