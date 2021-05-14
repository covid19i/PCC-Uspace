#!/usr/bin/python

import sys; print(sys.executable)


#from common.simple_arg_parse import arg_or_default
import pprint
from time import sleep
import sys, os
import random
import os.path
import matplotlib.pyplot as plt
from operator import truediv, sub

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

def read_plot_styles(plot_styles, plot_styles_path):
    with open(plot_styles_path, 'r') as plot_styles_file:
        for line in plot_styles_file:
            print(line)
            model_name, style = line.replace("\n", "").split("\t")
            plot_styles[model_name] = style
    plot_styles_file.close()

plot_styles_path = arg_or_default("--plot_styles", default="/home/ubuntu/plot_styles.txt")
plot_styles = {}
read_plot_styles(plot_styles, plot_styles_path)
print("Plot Styles:")
pprint.pprint(plot_styles)

BYTES_PER_PACKET = 1500 - 28
PACKET_SIZE = BYTES_PER_PACKET * 8
ONE_MEGA_BIT = 1024 * 1024

def gen_plots():
    output_folder = arg_or_default("--output", default="/home/ubuntu/mininet_logs/")
    min_RTTs = []
    bandwidths = []
    latencies = []
    
    model_throughputs = {}
    model_latencies = {}
    for model_name in model_names:
        model_throughputs[model_name] = []
        model_latencies[model_name] = []
        
    for config in net_configs:
        bandwidths.append(config["bw"])
        latencies.append(4 * float(config["delay"].replace("s", "")) )#h1 -> s -> h2 and reverse
        min_RTT = 100000000.0
        config_name = "bw_"+str(config["bw"])+"_latency_"+config["delay"]+"_loss_"+str(config["loss"])+"_queue_"+str(config["max_queue_size"])
        #print(config_name)
        print("Reading data for: " + config_name)
        config_folder = output_folder +config_name
        for model_name in model_names:
            print(model_name)
            received_data = []
            RTTs = []
            
            if(model_name in ['Copa', 'Vivace', 'Cubic', 'Aurora', 'Allegro'] or 'Vivace' in model_name 
               or 'Aurora' in model_name):
                log_file_path = output_folder +config_name + "/"+ str(model_name) + ".txt"
            else:
                model_path = str(model_folder_path) + str(model_name)
                log_file_path = output_folder +config_name + "/"+ str(model_name) + ".txt"
            if not os.path.isfile(log_file_path):
                print("Model/algo " + model_name + " not tested with configuration " + config_name +
                      "Exiting now...")
                sys.exit()
            
            f = open(log_file_path)
            lineno = 1
            for line in f.readlines():
                if(lineno > 5):
                    #print(line)
                    line = line.replace("\t\t\t", "\t")
                    line = line.replace("\t\t", "\t")
                    #BC = line.replace("\t\t", "\t").split('\t')
                    #print(BC)
                    row, send_rate, est_RTT, sent_total, sent, lost, lost_total, nak, ack = line.replace("\t\t", "\t").split('\t')
                    est_RTT = float(est_RTT)
                    #sent = int(sent)
                    #lost = int(lost)
                    ack = ack.replace("\n", "")
                    ack = int(ack)
                    received_data.append(ack * PACKET_SIZE)
                    RTTs.append(est_RTT)
                    #print(send_rate, est_RTT, ack)
                    
                lineno += 1
            if(lineno < 6):
                print("Model/algo " + model_name + " not well tested with configuration " + config_name +
                  "Exiting now... only " + str(lineno) + " lines found in " + log_file_path)
                sys.exit()
            f.close()
            
            #evaluating the efficiency of the model/algo on this net config
            rows_to_use = 120
            avg_throughput = sum(received_data[-rows_to_use:])/rows_to_use
            #print(RTTs[-rows_to_use:])
            avg_RTT = sum(RTTs[-rows_to_use:])/rows_to_use
            print("Avg throughput, Avg est RTT: %.5f %.5f" % (avg_throughput, avg_RTT))
            model_throughputs[model_name].append(avg_throughput)
            model_latencies[model_name].append(avg_RTT)
            min_RTT = min(min_RTT, min(RTTs))
        
        min_RTTs.append(min_RTT)

    pprint.pprint(model_throughputs)
    pprint.pprint(bandwidths)
    model_utilizations = {}
    plt.figure(num = 1)
    for model_name in model_names:
        model_utilizations[model_name] = list(map(truediv, model_throughputs[model_name], 
                                                  [ONE_MEGA_BIT * bandwidth for bandwidth in bandwidths]))
        plt.plot(bandwidths, model_utilizations[model_name], plot_styles[model_name], label = model_name )
        pprint.pprint(model_utilizations[model_name])
    plt.xlabel('Bandwidth (in Mbps)')
    plt.ylabel('Link Utilization')
    plt.xscale("log")
    plt.title('Link Utilization vs Bandwidth')
    plt.legend()
    plt.show()
    
    self_inflicted_latencies = {}
    plt.figure(num = 2)
    for model_name in model_names:
        self_inflicted_latencies[model_name] = list(map(sub, model_latencies[model_name], 
                                                  min_RTTs))
        plt.plot(bandwidths, self_inflicted_latencies[model_name], plot_styles[model_name], label = model_name )
        pprint.pprint(self_inflicted_latencies[model_name])
    plt.xlabel('Bandwidth (in Mbps)')
    plt.ylabel('Self-inflicted latency (ms)')
    plt.xscale("log")
    plt.title('Self-inflicted latency vs Bandwidth')
    plt.legend()
    plt.show()
    
    plt.savefig('bandwidth_sensitivity.png')

gen_plots()

#DOn't FORGET
#sudo PYTHONPATH=/usr/local/lib/python2.7/dist-packages:$PYTHONPATH python3 util/compare_models.py     

#if __name__ == '__main__':
    #setLogLevel( 'info' )
