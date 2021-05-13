source /home/ubuntu/environments/my_env/bin/activate
cd /home/ubuntu/PCC-Uspace/src
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$(pwd)/core/
echo $LD_LIBRARY_PATH
./app/pccclient send 10.0.0.1 9000 --pcc-rate-control=python -pyhelper=loaded_client -pypath=/home/ubuntu/PCC-RL/src/udt-plugins/testing/ --history-len=10 --pcc-utility-calc=linear --model-path=/home/ubuntu/models/LSTM_run6_1600x410_2048_1_lstm_dim_128 &
