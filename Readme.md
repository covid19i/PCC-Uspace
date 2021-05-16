#PCC

This repository houses the Performance Congestion Control project.

To build PCC, run the following:

cd src
make

This will produce two apps (pccclient and pccserver) in the src/app directory.

To test that PCC is functioning, you can run:

cd src
export LD\_LIBRARY\_PATH=$LD\_LIBRARY\_PATH:`pwd`/core/
./app/pccserver recv 9000
(this creates a PCC server that listens on port 9000 and receives data)

and in a separate terminal, run:

cd src
export LD\_LIBRARY\_PATH=$LD\_LIBRARY\_PATH:`pwd`/core/
./app/pccclient send 127.0.0.1 9000
(this create a PCC client that connects to the local host (IP 127.0.0.1) at port 9000, then sends data to the server at that address.







For installation (on AWS Ubuntu 18.04 image): 
sudo add-apt-repository ppa:deadsnakes/ppa 
sudo apt-get update && sudo apt-get install git cmake libopenmpi-dev python3.5-dev zlib1g-dev python3-pip python3.5-venv python3-testresources tmux sysstat 
(For using GPUs, don't install MPI: sudo apt-get update && sudo apt-get install git cmake python3.5-dev zlib1g-dev python3-pip python3.5-venv python3-testresources tmux sysstat)

mkdir environments 
cd environments 
python3.5 -m venv my_env 
source ~/environments/my_env/bin/activate

PCC-Uspace: 
cd ~/PCC-Uspace/src 
git checkout deep-learning 
make 
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$(pwd)/core/ 
echo $LD_LIBRARY_PATH

pip3 install --upgrade pip==19.0 
pip install tensorflow==1.15 numpy gym scipy stable-baselines[mpi] 
Without MPI version of stable-baselines: pip install tensorflow==1.15 numpy gym scipy stable-baselines

./app/pccserver recv 9000 & 
./app/pccclient send 127.0.0.1 9000 
./app/pccclient send 127.0.0.1 9000 --pcc-rate-control=python -pyhelper=loaded_client -pypath=~/PCC-RL/src/udt-plugins/testing/ --history-len=10 --pcc-utility-calc=linear --model-path=model_path_name 
./app/pccclient send 127.0.0.1 9000 Vivace

To generate plots to compare various DRL models, run something like: python3 ./util/compare_models_gen_plots_bw.py --model_names="./util/models_3_10_30_238.txt" --net_configs="./util/net_config_3_10_30_238.txt" --models_at="../../../models/" --output="./logs/" --plot_styles="./util/plot_styles.txt" --model_labels="./util/model_labels.txt"
