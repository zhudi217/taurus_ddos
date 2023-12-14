# In-network DDoS Detection with ML Models using Taurus
This repository stores the code of DDoS detection project for course UVA 2023 Fall CS6501-014 Software-Defined Networks.

## Instructions to Execute the System
### Prerequisites
Before executing the code, make sure the following OS and tools are installed on the machine
> - Ubuntu 18.04.2 LTS
> - Docker

Guides for installing Docker on Ubuntu 18.04 LTS:
```
https://www.digitalocean.com/community/tutorials/how-to-install-and-use-docker-on-ubuntu-18-04
```
### Step 1: Clone This Repository
```
cd ~
git clone https://github.com/zhudi217/taurus_ddos.git
cd taurus_ddos
```

### Step 2: Setup Taurus MapReduce Behavior Model
Before executing the code, we need to set up Taurus's MapReduce behavior model (BM) first. The following link contains instructions on how to clone and set up MapReduce BM. Make sure the MapReduce BM code is cloned to `mapreduce-bm/`
```
https://gitlab.com/dataplane-ai/taurus/mapreduce-bm
```
After the MapReduce BM is set, run the MapReduce BM docker for testing code in this repository
```
cd ~/taurus_ddos/platform-bm/
make mapreduce-start
```
> - Note: you can stop the docker by running `make mapreduce-stop`

### Step 3: Execute the System
Navigate to the root directory of DDoS detection application by running
```
cd ~/taurus_ddos/platform/ddos-detection/
```

#### (a) Start ONOS
Open a new terminal, and in that terminal run the following command to start the ONOS controller. Wait for the information printing in the terminal to stop before proceeding to the next step.
```
make onos-start
```

#### (b) Start Mininet
Open a second terminal, and run the following command in the second terminal. This command will start the mininet. Once started, you will see the `mininet>` prompt.
```
make mininet-start
```

#### (c) Build P4 Code, ONOS Application, Spatial Application and Run Spatial Application
Open another terminal and execute the following commands.
```
make p4-build
make onos-build-app
make onos-reload-app
make onos-netcfg
make mapreduce-build-app
```
Once the above commands are complete, run the Spatial application with the following command:
```
make mapreduce-run-app
```

#### (d) Enabling Traffic via MapReduce BM
To route traffic through MapReduce BM, run the following command from a separate terminal. This command will install P4 rules in the switch to route traffic through MapReduce BM. The status code `201` means that the rules are successfully installed.
```
make onos-traverse-mapreduce
```

### (e) Sending Packets from Host 1 to Host 2
To send packets from host 1 to host 2, first open a new terminal as the host 2, the receiver.
```
make h2-recv
```
Then, to start sending the packet, open another new terminal as the packet sender, host 1
```
make h1-send
```
If the system works properly, you should be able to see some information in the terminal that runs the Spatial application, and you should also be able to see detection results in `H2`.

## Cleaning
If you are done with the execution, you can stop ONOS and MapReduce BM by pressing `CTRL+C`, and Mininet by typing exit. To clean the compiled outputs, run `make clean`.



