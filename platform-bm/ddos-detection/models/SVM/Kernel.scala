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
        
        // Summary: ************************************************************************************************
        // In this benchmark, we implement a simple Support Vector Machine (SVM).  *********************************************************************************************************


        // *********************************************************************************************************
        // Generating SRAMs for storing inputs, and defining useful constants.
        // *********************************************************************************************************

        val params_dir = SPATIAL_APP_ROOT + s"/params"        

        // Define constants to access bytes in the packet
        val BYTE_WIDTH = 1
        val FLOAT_WIDTH = 4
        val FEATURE_HDR_OFFSET = 34
        val FEATURE_DIMS = 5
        val NUM_SUPPORT_VECTORS = 79
        val NUM_INTERCEPTS = 1
        val FEATURE_HDR_OUTPUT_OFFSET = FEATURE_HDR_OFFSET + (FEATURE_DIMS * FLOAT_WIDTH)

        // Generating LUTs to hold pre-trained parameters for each layer of the model
        val SV_LUT = LUT.fromFile[Float](NUM_SUPPORT_VECTORS, FEATURE_DIMS)(params_dir + "/SV.csv")
        val DC_LUT = LUT.fromFile[Float](NUM_SUPPORT_VECTORS)(params_dir + "/DCS.csv")
        val INTERCEPT_LUT = LUT.fromFile[Float](NUM_INTERCEPTS)(params_dir + "/B.csv")
                        
        // SRAM for storing incoming input features.
        // For this benchmark, all elements are 4 byte floats.
        val inputs = SRAM[Float](FEATURE_DIMS)

        // *********************************************************************************************************
	    // Linear SVM Kernel
        // *********************************************************************************************************        
        def SVMKernel(_inputs: SRAM1[Float], _support_vectors: LUT2[Float], svm_idx: I32): Float = {
	    Reduce(Reg[Float](0))(0 until FEATURE_DIMS){ i => 
	        _inputs(i) * _support_vectors(svm_idx, i)
	    }{_+_} 
        }

        // *********************************************************************************************************
        // Generating pipeline stages for the input, intermediate operations, and output
        // *********************************************************************************************************        

        // Read the input features into SRAM
        Pipe {
            Foreach(0 until FEATURE_DIMS){ i =>

                // Calculate index of next feature
                val idx = (i * FLOAT_WIDTH) + FEATURE_HDR_OFFSET

                // Build full feature from pkt bits
		val word = cat(pkt(idx).bits(7::0), pkt(idx+1).bits(7::0), pkt(idx+2).bits(7::0), pkt(idx+3).bits(7::0)).as[U32]
                // Read input words into SRAM
                inputs(i) = word.to[Float]
            }
        }

        // Perform SVM and write result into packet
        Pipe { 
            // An SVM can be built from a reduction across Kernel operations
            val mx = Reduce(Reg[Float](0))(0 until NUM_SUPPORT_VECTORS){ i => 
                val svm_kernel = SVMKernel(inputs, SV_LUT, i)
                DC_LUT(i) * svm_kernel
            }{_ + _}

            // Add in the intercept
            val output = mux(mx + INTERCEPT_LUT(0) > 0, 1, 0)

	    // Define constants to access bytes in the packet
            val FEATURE_HDR_OUTPUT_OFFSET = 34
            val FEATURE_HDR_LENGTH = FEATURE_DIMS * FLOAT_WIDTH	// 4 bytes * 5 features
            val GROUND_TRUTH_LENGTH = 1
            val idx = FEATURE_HDR_OUTPUT_OFFSET + FEATURE_HDR_LENGTH + GROUND_TRUTH_LENGTH

            // Write output as a byte into the packet 
            pkt(idx) = output.to[U8]
        }

    }

} 
