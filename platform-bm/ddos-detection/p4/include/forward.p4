/* *************************************************************************
 *
 * Copyright 2022 Tushar Swamy (Stanford University),
 *                Alexander Rucker (Stanford University),
 *                Annus Zulfiqar (Purdue University),
 *                Muhammad Shahbaz (Stanford/Purdue University)
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 *
 ************************************************************************** */

#ifndef __FORWARD__
#define __FORWARD__

#include "headers.p4"
#include "defines.p4"

control forward_control(inout parsed_headers_t hdr,
                        inout local_metadata_t local_metadata,
                        inout standard_metadata_t standard_metadata) {

    direct_counter(CounterType.packets_and_bytes) foward_counter;

    action noop() { }

    action drop() {
        mark_to_drop(standard_metadata);
    }

    action set_output_port(bit<9> port_num) {
        standard_metadata.egress_spec = port_num;
    }

    action send_to_cpu() {
        standard_metadata.egress_spec = CPU_PORT;
    }

    table forward_table {
        key = {
            standard_metadata.ingress_port: ternary;
            hdr.ethernet.dst_addr: ternary;
            hdr.ethernet.src_addr: ternary;
            hdr.ethernet.ether_type: ternary;
            hdr.ipv4.dst_addr: ternary;
            hdr.ipv4.src_addr: ternary;
            local_metadata.ip_proto: ternary;
            local_metadata.icmp_type: ternary;
            local_metadata.l4_src_port: ternary;
            local_metadata.l4_dst_port: ternary;
        }
        actions = {
            noop;
            drop;
            set_output_port;
            send_to_cpu;
        }
        const default_action = drop;
        counters = foward_counter;
    }

    apply {
        forward_table.apply();
     }
}

#endif

