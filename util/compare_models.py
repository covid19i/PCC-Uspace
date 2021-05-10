#!/usr/bin/python

import sys; print(sys.executable)

from mininet.topo import Topo
from mininet.net import Mininet
from mininet.util import dumpNodeConnections
from mininet.log import setLogLevel
#from common.simple_arg_parse import arg_or_default
import pprint
from time import sleep
import random
import numpy as np

import sys

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
    def build( self, n=2, net_config =dict(bw=1, delay='1s', loss=1, max_queue_size=100, use_htb=True )):
        switch = self.addSwitch( 's1' )
        for h in range(n):
            # Each host gets 50%/n of system CPU
            host = self.addHost( 'h%s' % (h + 1), cpu=.5/n )
            #The parameter bw is expressed as a number in Mbit; delay is expressed as a string with units in place (e.g. '5ms', '100us', '1s'); loss is expressed as a percentage (between 0 and 100); and max_queue_size is expressed in packets.
            # 10 Mbps, 5ms delay, 2% loss, 1000 packet queue
            linkopts = dict(bw=net_config["bw"], delay=str(net_config["lat"])+'s', loss=net_config["loss"]*100,
                              max_queue_size=net_config["queue"], use_htb=True )
            self.addLink( host, switch, **linkopts)

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
pprint.pprint(model_names)

class SpawnMininet():
    def __init__(self):
        self.min_bw, self.max_bw = (10, 1000)
        self.min_lat, self.max_lat = (0.005, 5)
        self.min_queue, self.max_queue = (0, 10)
        self.min_loss, self.max_loss = (0.0, 0.05)
        self.net = None
        
    def create_new_net(self):
        net_config = self.new_net_configuration()
        topo = SingleSwitchTopoWithLinkConfig(4, net_config )
        net = Mininet( topo=topo)
        #,               host=CPULimitedHost, link=TCLink )
        self.net = net
        net.start()
        print( "Dumping host connections" )
        dumpNodeConnections( net.hosts )
        print( "Testing network connectivity" )
        net.pingAll()
        print( "Testing bandwidth between h1 and h4" )
        h1, h4 = net.get( 'h1', 'h4' )
        net.iperf( (h1, h4) )
        
        #self.links = [Link(bw, lat, queue, loss), Link(bw, lat, queue, loss)]
        #self.senders = [Sender(random.uniform(0.3, 1.5) * bw, [self.links[0], self.links[1]], 0, self.features, history_len=self.history_len)]
        #self.run_dur = 3 * lat
    
    def new_net_configuration(self):
        net_config = {}
        net_config["bw"]    = random.uniform(self.min_bw, self.max_bw)
        net_config["lat"]   = random.uniform(self.min_lat, self.max_lat)
        net_config["queue"] = 1 + int(np.exp(random.uniform(self.min_queue, self.max_queue)))
        net_config["loss"]  = random.uniform(self.min_loss, self.max_loss)
        return net_config
    
    def run_experiment(self):
        h1, h2 = net.get( 'h1', 'h2' )  
        result = h1.cmd('ifconfig')
        print( result )
        print( "Starting test..." )
        h1.cmd('while true; do date; sleep 1; done > /tmp/date.out &')
        sleep(120)#send for 2 minutes
        print( "Stopping test" )
        h1.cmd('kill %while')
        print( "Reading output" )
        f = open('/tmp/date.out')
        lineno = 1
        for line in f.readlines():
            print( "%d: %s" % ( lineno, line.strip() ) )
            lineno += 1
        f.close()
    
def test_RL_models():
    testbed = SpawnMininet()
    testbed.create_new_net()
    testbed.run_experiment()
    testbed.net.stop()
    #KILL lingering processes (defunct or running)
    #sudo mn -c??????
    

#DOn't FORGET
#sudo PYTHONPATH=/usr/local/lib/python2.7/dist-packages:$PYTHONPATH python3 util/compare_models.py     
test_RL_models()

def perfTest():
    "Create network and run simple performance test"
    topo = SingleSwitchTopo( n=4 )
    net = Mininet( topo=topo)
    #,               host=CPULimitedHost, link=TCLink )
    net.start()
    print( "Dumping host connections" )
    dumpNodeConnections( net.hosts )
    print( "Testing network connectivity" )
    net.pingAll()
    print( "Testing bandwidth between h1 and h4" )
    h1, h4 = net.get( 'h1', 'h4' )
    net.iperf( (h1, h4) )
    net.stop()

if __name__ == '__main__':
    setLogLevel( 'info' )
    #perfTest()