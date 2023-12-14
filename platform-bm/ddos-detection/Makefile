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

export DOCKER_SCRIPTS = $(shell pwd)/../../scripts
export DOCKER_APPS_DIR = projects/ddos-detection
export MAX_PKT_SIZE = 1500
export MAX_BATCH_SIZE = 100
export BATCH_SIZE = 60
export RATE_PPS = 30
export FILTER_MACS = 
export FILTER_TYPES = 0x800
export FILTER_IPS = 
export FILTER_PROTOS = 254

clean: onos-clean-app p4-clean mapreduce-clean-app tensorflow-clean


####################################################################
# Mininet
####################################################################

interfaces-setup:
	sudo ip link add s2v type veth peer name v2b
	sudo ip link set s2v up
	sudo ip link set v2b up
	sudo ip link add v2s type veth peer name b2v
	sudo ip link set v2s up
	sudo ip link set b2v up
	
interfaces-clean:
	sudo ip link delete s2v
	sudo ip link delete v2s

mininet-start: interfaces-setup
	$(DOCKER_SCRIPTS)/mn-stratum.run-script python mininet/topo.py --ingress-intf v2s --egress-intf s2v
	make interfaces-clean


####################################################################
# ONOS
####################################################################

onos-start:
	ONOS_APPS=gui,proxyarp,drivers.bmv2 \
	$(DOCKER_SCRIPTS)/onos

# The **password** is: rocks
# Press CTRL+D to exit the CLI
onos-cli:
	$(DOCKER_SCRIPTS)/onos-cli

onos-netcfg:
	$(DOCKER_SCRIPTS)/onos-netcfg netcfg.json

onos-build-app:
	cd onos/app && $(DOCKER_SCRIPTS)/maven clean package

onos-reload-app: 
	$(DOCKER_SCRIPTS)/onos-app reinstall! onos/app/target/forward-1.0-SNAPSHOT.oar

onos-clean-app:
	sudo rm -rf onos/app/target

onos-bypass-mapreduce:
	cd onos/api && python3 rules.py --bypass

onos-traverse-mapreduce:
	cd onos/api && python3 rules.py --enable

onos-reset-rules:
	cd onos/api && python3 rules.py --disable


####################################################################
# P4
####################################################################

p4-build: p4-clean
	mkdir -p onos/app/src/main/resources/bmv2
	$(DOCKER_SCRIPTS)/p4c p4c-bm2-ss --arch v1model -o onos/app/src/main/resources/bmv2/bmv2.json \
		-DTARGET_BMV2 -DCPU_PORT=255 \
		--p4runtime-files onos/app/src/main/resources/bmv2/p4info.txt \
		p4/main.p4
	echo "255" > onos/app/src/main/resources/bmv2/cpu_port.txt

p4-clean:
	sudo rm -rf onos/app/src/main/resources/*


####################################################################
# MapReduce
####################################################################

mapreduce-build-app: mapreduce-clean-app
	docker exec -it mapreduce-bm bash -c \
		"cd script && \
		export MAPREDUCE_BM_MAX_PKT_SIZE=$(MAX_PKT_SIZE); \
		export MAPREDUCE_BM_MAX_BATCH_SIZE=$(MAX_BATCH_SIZE); \
		./build-spatial.sh --apps_dir /mount-dir/$(DOCKER_APPS_DIR) \
			--scala_program spatial"

mapreduce-build-app-rc: mapreduce-clean-app
	docker exec -it mapreduce-bm bash -c \
		"cd script && \
		export MAPREDUCE_BM_MAX_PKT_SIZE=$(MAX_PKT_SIZE); \
		export MAPREDUCE_BM_MAX_BATCH_SIZE=$(MAX_BATCH_SIZE); \
		./build-spatial.sh --apps_dir /mount-dir/$(DOCKER_APPS_DIR) \
			--scala_program spatial --reset_cache 1"

mapreduce-run-app:
	docker exec -it mapreduce-bm bash -c \
		"cp -f script/bm.py build/.; \
		 cd build && python3 bm.py --ingress-iface v2b --egress-iface b2v \
			--batch-size $(BATCH_SIZE) --rate-pps $(RATE_PPS) --macs $(FILTER_MACS) \
			--types $(FILTER_TYPES) --ips $(FILTER_IPS) --protos $(FILTER_PROTOS)"

mapreduce-clean-app:
	docker exec -it mapreduce-bm bash -c \
		"cd script && ./build-spatial.sh --clean; \
		 rm -f /tmp/spatial_batch_*"


####################################################################
# Hosts
####################################################################

h1:
	$(DOCKER_SCRIPTS)/utils/mn-stratum/exec h1

h2:
	$(DOCKER_SCRIPTS)/utils/mn-stratum/exec h2

h1-send:
	$(DOCKER_SCRIPTS)/utils/mn-stratum/exec-script h1 \
        	"cd traffic && ./h1-send.sh"

h2-recv:
	$(DOCKER_SCRIPTS)/utils/mn-stratum/exec-script h2 \
        	"cd traffic && ./h2-recv.sh"


####################################################################
# Tensorflow
####################################################################

.PHONY: tensorflow

tensorflow:
	cd tensorflow && mkdir -p build && \
	$(DOCKER_SCRIPTS)/tensorflow python train.py --build-dir "build"

tensorflow-clean:
	cd tensorflow && \
	$(DOCKER_SCRIPTS)/tensorflow rm -rf build
