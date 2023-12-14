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

package taurus

import spatial.dsl._

@spatial trait Kernel extends SpatialApp { 

    // Spatial root direcotry (do not edit this)
    val SPATIAL_APP_ROOT = s"/root/mapreduce-bm/deps/spatial/apps/src"

    // Implementing the Kernel
    def Run(pkt: SRAM1[U8]): Unit = {          
        Pipe {
            // Select a class (0 or 1) based on which logit in L4_OUT is larger
            val output = 1         
            
            // Define constants to access bytes in the packet
            val FEATURE_HDR_OUTPUT_OFFSET = 34
            val FEATURE_HDR_LENGTH = 5 * 4	// 4 bytes * 5 features
            val GROUND_TRUTH_LENGTH = 1
            val idx = FEATURE_HDR_OUTPUT_OFFSET + FEATURE_HDR_LENGTH + GROUND_TRUTH_LENGTH

            // Write output as a byte into the packet 
            pkt(idx) = output.to[U8]
        }
    }
}
