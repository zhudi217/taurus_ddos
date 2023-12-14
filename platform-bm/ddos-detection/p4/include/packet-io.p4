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

#ifndef __PACKET_IO__
#define __PACKET_IO__

#include "headers.p4"
#include "defines.p4"

control packetio_ingress(inout parsed_headers_t hdr,
                         inout standard_metadata_t standard_metadata) {
    apply {
        if (standard_metadata.ingress_port == CPU_PORT) {
            standard_metadata.egress_spec = hdr.packet_out.egress_port;
            hdr.packet_out.setInvalid();
            exit;
        }
    }
}

control packetio_egress(inout parsed_headers_t hdr,
                        inout standard_metadata_t standard_metadata) {
    apply {
	
	bit<48> egress_time = standard_metadata.egress_global_timestamp;
	bit<48> ingress_time = standard_metadata.ingress_global_timestamp;

	if (standard_metadata.ingress_port == 1) {
            hdr.ml_fields.h2mr_in = ingress_time;
	} else if (standard_metadata.ingress_port == 3) {
	    hdr.ml_fields.mr2h_in = ingress_time;
	}
	
	if (standard_metadata.egress_port == 4) {
            hdr.ml_fields.h2mr_out = egress_time;
	} else if (standard_metadata.egress_port == 2) {
	    hdr.ml_fields.mr2h_out = egress_time;
	}

        if (standard_metadata.egress_port == CPU_PORT) {
            hdr.packet_in.setValid();
            hdr.packet_in.ingress_port = standard_metadata.ingress_port;
        }
    }
}

#endif
