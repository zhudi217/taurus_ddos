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

#ifndef __DEFINE__
#define __DEFINE__

const bit<16> ETHERTYPE_IPV4 = 0x0800;
const bit<16> ETHERTYPE_ARP  = 0x0806;

const bit<8> PROTO_ICMP = 1;
const bit<8> PROTO_TCP = 6;
const bit<8> PROTO_UDP = 17;
//const bit<8> PROTO_ML = 253;
const bit<8> PROTO_ML = 254;

#endif

