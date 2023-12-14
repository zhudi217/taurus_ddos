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

export DOCKER_SCRIPTS ?= scripts
export MOUNT_DIR ?= $(shell pwd)


####################################################################
# MapReduce
####################################################################

mapreduce-start:
	MAPREDUCE_BM_MOUNT_DIR=$(MOUNT_DIR) \
	$(DOCKER_SCRIPTS)/mapreduce-bm

mapreduce-stop:
	docker stop mapreduce-bm
