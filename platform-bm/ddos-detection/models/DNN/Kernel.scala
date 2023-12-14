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
        // In this benchmark, we implement a DNN to do anomaly detection based on the paper below. It is made up of
        // 5 layers with 24,12,6,3, and 2 layers as well as 8 input features. The result is written back into the
        // packet.
        //
        // Original paper:
        // 
        // Tang, Tuan A., et al. "Deep learning approach for network intrusion detection in software defined networking."
        // 2016 international conference on wireless networks and mobile communications (WINCOM). IEEE, 2016.
        // 
        // *********************************************************************************************************


        // *********************************************************************************************************
        // Generating SRAMs for storing intermediate results, and loading pre-trained model weight into LUTs (a
        // read-only SRAM).
        // *********************************************************************************************************
        
        val params_dir = SPATIAL_APP_ROOT + s"/params"

        // SRAM for storing incoming input features (8 input features)
        val input = SRAM[Float](5)
  
        // SRAM for storing outputs for layer 0, 1, 2, 3 and 4
	val L0_OUT = SRAM[Float](24)
        val L1_OUT = SRAM[Float](12)
        val L2_OUT = SRAM[Float](6)
        val L3_OUT = SRAM[Float](3)
        val L4_OUT = SRAM[Float](2)

        // Generating LUTs to hold pre-trained parameters for each layer of the model
	val L0_W_LUT = LUT.fromFile[Float](24,8)(params_dir + "/L0_W.csv")
        val L0_B_LUT = LUT.fromFile[Float](24)(params_dir + "/L0_B.csv")
        val L1_W_LUT = LUT.fromFile[Float](12,24)(params_dir + "/L1_W.csv")
        val L1_B_LUT = LUT.fromFile[Float](12)(params_dir + "/L1_B.csv")
        val L2_W_LUT = LUT.fromFile[Float](6,12)(params_dir + "/L2_W.csv")
        val L2_B_LUT = LUT.fromFile[Float](6)(params_dir + "/L2_B.csv")
        val L3_W_LUT = LUT.fromFile[Float](3,6)(params_dir + "/L3_W.csv")
        val L3_B_LUT = LUT.fromFile[Float](3)(params_dir + "/L3_B.csv")
        val L4_W_LUT = LUT.fromFile[Float](2,3)(params_dir + "/L4_W.csv")
        val L4_B_LUT = LUT.fromFile[Float](2)(params_dir + "/L4_B.csv")

        // Define constants to access bytes in the packet
        val FEATURE_HDR_OFFSET = 34


        // *********************************************************************************************************
        // Generating pipeline stages for the input, intermediate operations, and output
        // *********************************************************************************************************

        // Read the input features into SRAM
        Pipe {
            Foreach(0 until 5){ i =>

                // Calculate index of next feature
                val idx = i*4 + FEATURE_HDR_OFFSET

                // Build full feature from pkt bits
		val word = cat(pkt(idx).bits(7::0), pkt(idx+1).bits(7::0), pkt(idx+2).bits(7::0), pkt(idx+3).bits(7::0)).as[U32]
                // Read input words into SRAM
                input(i) = word.to[Float]
            }
        }
         
        // A layer can be built from a set of perceptrons. All perceptrons in this layer use
        // a ReLU activation function. The operations used in this function are repeated over
        // the next four layers
        //

        // Layer 0 pipeline stage
        Pipe {

            // We use a tabulated list here instead of a Foreach loop. Tabulate will generate different blocks of 
            // hardware for each perceptron without needing a loop controller. This is more resource intensive but
            // also better performing than a Foreach loop.
            List.tabulate(24) { i =>

                // Similar to the above tabulate, we use List.tabulate to replace the Map portion of a Reduce loop controller 
                // for performance
                val partial_results = List.tabulate(8) { j =>
                    
                    // Multiply weights
                    L0_W_LUT(i, j) * input(j)
                }

                // To replace the rest of the Reduce loop controller we use the reduceTree to generate individual blocks
                // of hardware for performance
                val w = partial_results.reduceTree {_+_}
                
                // ReLU activation function
                L0_OUT(i) = max(w + L0_B_LUT(i), 0)
            }
        }
      
        // Layer 1 pipeline stage
        Pipe {
            List.tabulate(12) { i =>

                val partial_results = List.tabulate(24) { j =>
                    L1_W_LUT(i, j) * L0_OUT(j)
                }

                val w = partial_results.reduceTree {_+_}
                L1_OUT(i) = max(w + L1_B_LUT(i), 0)
            }
        }
        
        // Layer 2 pipeline stage
        Pipe {
          List.tabulate(6) { i =>

              val partial_results = List.tabulate(12) { j =>
                  L2_W_LUT(i, j) * L1_OUT(j)
              }

              val w = partial_results.reduceTree {_+_}
              L2_OUT(i) = max(w + L2_B_LUT(i), 0)
          }
        }

        // Layer 3 pipeline stage
        Pipe {
            List.tabulate(3) { i =>

                val partial_results = List.tabulate(6) { j =>
                    L3_W_LUT(i, j) * L2_OUT(j)
                }

                val w = partial_results.reduceTree {_+_}
                L3_OUT(i) = max(w + L3_B_LUT(i), 0)
            }
        }

	// Layer 4 pipeline stage
        Pipe {
            List.tabulate(2) { i =>

                val partial_results = List.tabulate(3) { j =>
                    L4_W_LUT(i, j) * L3_OUT(j)
                }

                val w = partial_results.reduceTree {_+_}
                L4_OUT(i) = max(w + L4_B_LUT(i), 0)
            }
        }          

        // Select a class and write it back into the packet 
        Pipe {

            // Select a class (0 or 1) based on which logit in L4_OUT is larger
            val output = mux(L4_OUT(0) >= L4_OUT(1), 0, 1)            
            
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
