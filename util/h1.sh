source /home/ubuntu/environments/my_env/bin/activate
cd /home/ubuntu/PCC-Uspace/src
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$(pwd)/core/
echo $LD_LIBRARY_PATH
./app/pccserver recv 9000 &
