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
import json

from mininet.cli import CLI
from mininet.log import setLogLevel
from mininet.net import Mininet
from mininet.topo import Topo
from mininet.link import Intf, Link
from stratum import StratumBmv2Switch


class SingleSwitchTopo(Topo):
    """Single Switch topology"""

    def __init__(self, *args, **kwargs):
        Topo.__init__(self, *args, **kwargs)
        
        self.addSwitch('s1')  # grpc: 50001

        self.addHost('h1', ip="10.0.0.1", mac="00:00:00:00:00:01")
        self.addHost('h2', ip="10.0.0.2", mac="00:00:00:00:00:02")
    
        self.addLink('s1', 'h1')
        self.addLink('s1', 'h2')


topos = {'singleswitch': (lambda: SingleSwitchTopo())}


def main(ingress_intf=None, egress_intf=None):
    net = Mininet(
        topo=SingleSwitchTopo(),
        switch=StratumBmv2Switch,
        controller=None)

    s1 = net.get('s1')
    
    # Add external interfaces
    if ingress_intf:
        Intf(ingress_intf, node=s1, port=3)

    if ingress_intf:
        Intf(egress_intf, node=s1, port=4)

    net.start()
    CLI(net)
    net.stop()


if __name__ == "__main__":
    setLogLevel('info')
    parser = argparse.ArgumentParser(
        description='Mininet script (single switch topology)')
    parser.add_argument('--ingress-intf', type=str, action="store", required=True)
    parser.add_argument('--egress-intf', type=str, action="store", required=True)
    args = parser.parse_args()

    main(args.ingress_intf, args.egress_intf)
