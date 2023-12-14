# Anomaly Detection DNN using Platform BM

In this project, we implement a real-world [anomaly detection (AD) application](https://ieeexplore.ieee.org/document/7777224) using the [NSL-KDD](https://www.unb.ca/cic/datasets/nsl.html) dataset. We expand the connection-level records to binned packet traces (i.e., each trace element represents a set of packets), and annotate them with their status (anomalous or benign, binary classification). The flow-size distribution, mixing, and packet fields’ rates of change are sampled from the original traces to create a realistic workload. We use this data to train a three-hidden-layer DNN and evaluate it on our Taurus Platform BM.

For testing this project, we will setup the following virtual environment and network topology:

<img src="figures/platform.png" alt="Platform Setup." width="450">

## Start the ONOS, Mininet, and MapReduce Apps

We have provided a `Makefile`, which contains the commands needed to run Mininet, ONOS, MapReduce BM, and other configurations.

### a. Starting ONOS
In a first shell, start ONOS:

```sh
cd ~/platform-bm/projects/anomaly-detection
make onos-start
```

This will start the ONOS controller. You will see a lot of information printed on the terminal; wait until it stops -- and it will stop!

> **Notes:** 
> - As Docker is running these containers for the first time, it will need to download them from https://hub.docker.com. These are large images (hundreds of megabytes), so they may take some time to download depending upon the network speed -- don't worry if the process is slow. It will happen only once, as Docker will cache these images and reuse them whenever the dockers are started again.
> - The docker scripts for Mininet (with Stratum) and ONOS, including other helper code, are located under the [`platform-bm/scripts`](../../scripts) folder. Please go through them to gain some insight into how to use Docker.

### b. Starting Mininet
In a second terminal, **start Mininet**:

```sh
cd ~/platform-bm/projects/anomaly-detection
make mininet-start
```

Once started, you will see the `mininet>` prompt. This indicates that your virtual network is ready and running, and you can now issue commands through this prompt.

### c. Building the P4 program and ONOS application

Before connecting switch `s1` to the ONOS controller, we need to build the P4 program and the associated ONOS application, and load these into ONOS. To do so, run these steps in a separate terminal.

* Build the P4 program.

```sh
cd ~/platform-bm/projects/anomaly-detection
make p4-build
```

> **Note:** you can delete the compiled output using `make p4-clean`.

This will compile the P4 program and store its output into the ONOS application's [resources](onos/app/src/main/resources) folder.

* Next, compile the ONOS application.

```sh
cd ~/platform-bm/projects/anomaly-detection
make onos-build-app
```

> **Note:** you can delete the compiled output using `make onos-clean-app`.

* Finally, load the application into ONOS and connect it with switch `s1`.

```sh
cd ~/platform-bm/projects/anomaly-detection
make onos-reload-app
make onos-netcfg
```

You will see some updates printed on the first terminal, where ONOS is running. Ignore `ERROR`; it's a bug (or typo) in ONOS.

### d. Building and running the Spatial application

Next, we will be build our anomaly-detection Spatial application [`Kernel.scala`](spatial/Kernel.scala), located in the `spatial` folder.

```sh
cd ~/platform-bm/projects/anomaly-detection
make mapreduce-build-app
```

Once the build completes, run the Spatial application.

```sh
cd ~/platform-bm/projects/anomaly-detection
make mapreduce-run-app
```

This will start the MapReduce BM docker with our anomaly-deteciton application, wiating for packets to process.

### e. Enabling trafifc via MapReduce BM

To route traffic through MapReduce BM, run the following command from a separate terminal.

```sh
cd ~/platform-bm/projects/anomaly-detection
make onos-traverse-mapreduce
```

This will install the necessary P4 rules in the switch to traverse traffic through MapReduce BM.

> **Notes:**
> - The status `201` indicates that a rule has been successfully installed.
> - To reset the rules, run `make onos-reset-rules`.
> - To bypass the MapReduce block, run `make onos-bypass-mapreduce`.

### f. Sending traffic from host `h1` to `h2`

Open two separate terminals for sending and receving packets from `h1` and `h2`, respectively.

```sh
cd ~/platform-bm/projects/anomaly-detection
make h2-recv
```

This starts a Scapy receiver, which will receive packets and compute/print the various ML metrics (e.g., F1 score and accuracy).

To send packet, run:

```sh
cd ~/platform-bm/projects/anomaly-detection
make h1-send
```

This will send packets (located in [`traffic/trace.pcap`](traffic/trace.pcap)) from host `h1` using scapy.

The packet will go through MapReduce BM (as can be seen from the output on the terminal running MapReduce). 

> **Note:** you can also run these steps manually by logging into `h1` and `h2` (e.g., to log into `h1` run, `make h1`).

### g. Cleaning up ...

Stop ONOS and MapReduce BM by pressing `CTRL+C`, and Mininet by typing `exit`. To the clean the compiled outputs, run `make clean`. 

## Training the DNN Model and Generate LUTs

You can generate the LUTs (or params) using the model provided under the [`tensorflow`](tensorflow) directory. To train the model, run:

```sh
cd ~/platform-bm/projects/anomaly-detection
make tensorflow
```

This will produce training outputs (i.e., LUTs and a model checkpoint) in the `tensorflow/build` directory. You may replace these LUTs with the ones provided in the [`spatial/params`](spatial/params) directory, for testing.

> **Note:** you can clean the build using `make tensorflow-clean`.

Have fun!
