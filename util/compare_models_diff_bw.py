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

class SingleSwitchTopo( Topo ):
    "Single switch connected to n hosts."
    def build( self, n=2 ):
        switch = self.addSwitch( 's1' )
        for h in range(n):
            # Each host gets 50%/n of system CPU
            host = self.addHost( 'h%s' % (h + 1),
                             cpu=.5/n )
            # 10 Mbps, 5ms delay, 2% loss, 1000 packet queue
            self.addLink( host, switch, bw=10, delay='5ms', loss=2,
                              max_queue_size=1000, use_htb=True )
            
class SingleSwitchTopoWithLinkConfig( Topo ):
    "Single switch connected to n hosts with a link of given properties."
    def build( self, n=2, net_config =dict(bw=30, delay="30ms", loss=0, max_queue_size=1000, use_htb=True )):
        switch = self.addSwitch( 's1' )
        for h in range(n):
            # Each host gets 50%/n of system CPU
            host = self.addHost( 'h%s' % (h + 1), cpu=.5/n )
            #The parameter bw is expressed as a number in Mbit; delay is expressed as a string with units in place (e.g. '5ms', '100us', '1s'); loss is expressed as a percentage (between 0 and 100); and max_queue_size is expressed in packets.
            # 10 Mbps, 5ms delay, 2% loss, 1000 packet queue
            self.addLink( host, switch, **net_config)

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

def read_net_configs(net_configs, net_configs_path):
    with open(net_configs_path, 'r') as net_configs_file:
        for line in net_configs_file:
            bw, latency, loss, max_queue_size = line.split("\t")
            linkopts = dict(bw=float(bw), delay=str(latency)+'s', loss=float(loss),
                              max_queue_size=int(max_queue_size), use_htb=True )
            net_configs.append(linkopts)
    net_configs_file.close()

net_configs_path = arg_or_default("--net_configs", default="/home/ubuntu/net_configs.txt")
net_configs = []
read_net_configs(net_configs, net_configs_path)
print("Net Configurations:")
pprint.pprint(net_configs)

class SpawnMininet():
    def __init__(self):
        self.min_bw, self.max_bw = (10, 1000)
        self.min_lat, self.max_lat = (0.005, 5)
        self.min_queue, self.max_queue = (0, 10)
        self.min_loss, self.max_loss = (0.0, 0.05)
        self.net = None
        
    def create_new_net(self, config):
        net_config = config
        pprint.pprint(net_config)
        topo = SingleSwitchTopoWithLinkConfig(4, net_config )
        net = Mininet( topo=topo)
        #,               host=CPULimitedHost, link=TCLink )
        self.net = net
        net.start()
        #print( "New net created. Dumping host connections" )
        #dumpNodeConnections( net.hosts )
        #print( "Testing network connectivity" )
        #net.pingAll()
        #print( "Testing bandwidth between h1 and h4" )
        h1, h2 = net.get( 'h1', 'h2' )
        #net.iperf( (h1, h2) )
        #CHECK WHY THIS RETURNS 24.1Gbits/s when bw=950 say
        
        #self.links = [Link(bw, lat, queue, loss), Link(bw, lat, queue, loss)]
        #self.senders = [Sender(random.uniform(0.3, 1.5) * bw, [self.links[0], self.links[1]], 0, self.features, history_len=self.history_len)]
        #self.run_dur = 3 * lat
        print("New net created and tested.")
    
    def run_experiment(self):
        print( "Starting test..." )
        output_folder = arg_or_default("--output", default="/home/ubuntu/mininet_logs/")
        #random.shuffle(net_configs)
        for config in net_configs:
            links_printed = 0
            config_name = "bw_"+str(config["bw"])+"_latency_"+config["delay"]+"_loss_"+str(config["loss"])+"_queue_"+str(config["max_queue_size"])
            #print(config_name)
            print("Testing with configuration: " + config_name)
            create_folder_if_not(output_folder +config_name)
            create_folder_if_not(output_folder +config_name + '/receiver/')
            
            #RANDOMIZATION OF THE ORDER OF MODELS
            for model_name in model_names:
                already_done = 0
                self.create_new_net(config)
                if(links_printed == 0):
                    print("Links from self.net.topo.links():")
                    pprint.pprint(self.net.topo.links(withKeys=True, withInfo=True)) 
                    links_printed = 1           
                h1, h2 = self.net.get( 'h1', 'h2' )  
                #result = h1.cmd('ifconfig')
                #print( result )
                h1.cmd('source /home/ubuntu/environments/my_env/bin/activate')
                h1.cmd('cd /home/ubuntu/PCC-Uspace/src')
                h1.cmd('export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$(pwd)/core/')
                #h1.cmd('./app/pccserver recv 9000 > /home/ubuntu/mininet_logs/h1_LSTM_run6.out &')
                
                h2.cmd('source /home/ubuntu/environments/my_env/bin/activate')
                h2.cmd('cd /home/ubuntu/PCC-Uspace/src')
                h2.cmd('export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$(pwd)/core/')
                
                if(model_name in ['Copa', 'Vivace', 'Cubic'] or 'Vivace' in model_name):
                    log_file_path = output_folder +config_name + "/"+ str(model_name) + ".txt"
                    server_log_file_path = output_folder +config_name + "/receiver/"+ str(model_name) + ".txt"
                    #h1.cmd("rm " + server_log_file_path)
                    if not os.path.isfile(log_file_path):
                        print("Server Output at " + server_log_file_path)
                        sender_pid = h1.cmd('./app/pccserver recv 9000 > ' + server_log_file_path + ' &')
                        #h2.cmd("rm " + log_file_path)
                        print("Client Output at " + log_file_path)
                        pid = h2.cmd("./app/pccclient send 10.0.0.1 9000 " + model_name + 
                                     " > " + log_file_path + " &")
                    else:
                        already_done = 1
                else:
                    model_path = str(model_folder_path) + str(model_name)
                    log_file_path = output_folder +config_name + "/"+ str(model_name) + ".txt"
                    server_log_file_path = output_folder +config_name + "/receiver/"+ str(model_name) + ".txt"
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
                    
                    h2.cmd('kill -9 ' + str(pid))
                    h2.cmd('kill %\./app/pccclient')
                    h2.cmd('kill %pccclient')
                    #h2.cmd('ps >> /home/ubuntu/mininet_logs/h2_LSTM_run6.out')
                    h1.cmd('kill %\./app/pccserver')
                    h1.cmd('kill %pccserver')
                    h1.cmd('kill -9 ' + str(sender_pid))
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
    testbed = SpawnMininet()
    #testbed.create_new_net()
    testbed.run_experiment()
    #testbed.net.stop()

#DOn't FORGET
#sudo PYTHONPATH=/usr/local/lib/python2.7/dist-packages:$PYTHONPATH python3 util/compare_models.py     
test_RL_models()

if __name__ == '__main__':
    setLogLevel( 'info' )
    #perfTest()
