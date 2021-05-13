#!/usr/bin/python

import sys; print(sys.executable)

from mininet.topo import Topo
from mininet.net import Mininet
from mininet.util import dumpNodeConnections
from mininet.log import setLogLevel
#from common.simple_arg_parse import arg_or_default
import pprint
from time import sleep
import sys, os
import random
import os.path

_arg_dict = {}
for arg in sys.argv:
    eq_pos = arg.find('=')
    if eq_pos >= 0:
        _arg_dict[arg[:eq_pos]] = arg[eq_pos + 1:]
    else:
        _arg_dict[arg] = True

def arg_or_default(arg, default=None):
    if arg in _arg_dict.keys():
        result = _arg_dict[arg]
        if isinstance(default, int):
            return int(result)
        if isinstance(default, float):
            return float(result)
        return result
    else:
        return default

def create_folder_if_not(path):
    if not os.path.exists(path):
        os.makedirs(path)
        print("Created folder: ", path)
    else:
        print(path, " folder already exists.")

def read_model_names(model_names, model_names_path):
    with open(model_names_path, 'r') as model_names_file:
        for line in model_names_file:
            #word, type = line.split("\t")
            model_name = line.replace("\n", "")
            model_names.append(model_name)
    model_names_file.close()

model_names_path = arg_or_default("--model_names")
model_folder_path = arg_or_default("--models_at", default="/home/ubuntu/models/")
model_names = []
read_model_names(model_names, model_names_path)
print("Model Names:")
pprint.pprint(model_names)


EXTERNAL_IPS = ["3.90.84.150"]


    
def run_experiment():
    print( "Starting test..." )
    output_folder = arg_or_default("--output", default="/home/ubuntu/mininet_logs/")
    #random.shuffle(net_configs)
    for EXTERNAL_IP in EXTERNAL_IPS:
        #print(config_name)
        print("Testing with configuration: " + config_name)
        create_folder_if_not(output_folder +EXTERNAL_IP)
        create_folder_if_not(output_folder +EXTERNAL_IP + '/receiver/')
        
        #RANDOMIZATION OF THE ORDER OF MODELS
        for model_name in model_names:
            already_done = 0
            
            if(model_name in ['Copa', 'Vivace', 'Cubic'] or 'Vivace' in model_name):
                log_file_path = output_folder +EXTERNAL_IP + "/"+ str(model_name) + ".txt"
                server_log_file_path = output_folder +EXTERNAL_IP + "/receiver/"+ str(model_name) + ".txt"
                #h1.cmd("rm " + server_log_file_path)
                if not os.path.isfile(log_file_path):
                    print("Server Output at " + server_log_file_path)
                    os.system('source /home/ubuntu/environments/my_env/bin/activate')
                    os.system('cd /home/ubuntu/PCC-Uspace/src')
                    os.system('export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$(pwd)/core/')
                    os.system('./app/pccserver recv 9000 > ' + server_log_file_path + ' &')
                    os.system('')
                    os.system('')
                    os.system('')
                    os.system('')
                    os.system('')
                    os.system('')
                    h1.cmd('./app/pccserver recv 9000 > ' + server_log_file_path + ' &')
                    #h2.cmd("rm " + log_file_path)
                    print("Client Output at " + log_file_path)
                    pid = h2.cmd("./app/pccclient send " + str(EXTERNAL_IP) + " 9000 " + model_name + 
                                 " > " + log_file_path + " &")
                else:
                    already_done = 1
            else:
                model_path = str(model_folder_path) + str(model_name)
                log_file_path = output_folder +EXTERNAL_IP + "/"+ str(model_name) + ".txt"
                server_log_file_path = output_folder +EXTERNAL_IP + "/receiver/"+ str(model_name) + ".txt"
                #h1.cmd("rm " + server_log_file_path)
                if not os.path.isfile(log_file_path):
                    print("Server Output at " + server_log_file_path)
                    sender_pid = h1.cmd('./app/pccserver recv 9000 > ' + server_log_file_path + ' &')
                    #h2.cmd("rm " + log_file_path)
                    print("Client Output at " + log_file_path)
                    print("Testing with model at " + model_path)
                    pid = h2.cmd("./app/pccclient send 10.0.0.1 9000 --model-path=" + model_path + "--pcc-rate-control=python" \
                       " -pyhelper=loaded_client -pypath=/home/ubuntu/PCC-RL/src/udt-plugins/testing/ " \
                       "--history-len=10 --pcc-utility-calc=linear " \
                       " > " + log_file_path + " &")
                else:
                    already_done = 1
            
            #print("PCC Server started with PID: " + str(sender_pid) + ".")
            #print("PCC Client started with PID: " + str(pid) + ".")
            if(already_done == 0):
                if('LSTM' in model_name):
                    if('64' in model_name):
                        sleep(25 + 120)
                    elif('128' in model_name):
                        sleep(25 + 120)
                    elif('256' in model_name):
                        sleep(30 + 120)
                    elif('512' in model_name):
                        sleep(40 + 120)
                    else:
                        sleep(20 + 120)
                else:
                    if("Vivace" in model_name):
                        sleep(10 + 120)
                    else:
                        sleep(0 + 120)
            else:
                print("\n\nModel/algo " + model_name + "already used for this net config")
                
            #The axe
            print("Running sudo mn -c")
            os.system('sudo mn -c > /tmp/sudo_mn_c.out')
            wait_period = 10
            print("Waiting for " + str(wait_period) + " seconds for Mininet processes to die...")
            sleep(wait_period)#wait for processes to get killed
            
            if(already_done == 0):
                print( "Reading first 20 lines of output from sender" )
                f = open(log_file_path)
                lineno = 1
                for line in f.readlines():
                    print( "%d: %s" % ( lineno, line.strip() ) )
                    lineno += 1
                    if lineno > 20:
                        break
                f.close()
        
        #pid = int( h1.cmd('echo $!') )
        #h1.cmd('wait', pid)
    print( "Stopping test..." )
    
def test_RL_models():
    run_experiment()
    #testbed.net.stop()

#DOn't FORGET
#sudo PYTHONPATH=/usr/local/lib/python2.7/dist-packages:$PYTHONPATH python3 util/compare_models.py     
test_RL_models()

if __name__ == '__main__':
    setLogLevel( 'info' )
    #perfTest()
