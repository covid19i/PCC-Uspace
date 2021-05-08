import json
import matplotlib.pyplot as plt
import numpy as np
import sys

if (len(sys.argv) < 2) or (sys.argv[1] == "-h") or (sys.argv[1] == "--help"):
    print("usage: python3 graph_run.py <pcc_env_log_filename.json>")
    exit(0)



filename0 = sys.argv[1]
data0 = {}

with open(filename0) as f:
    data0 = json.load(f)

time_data_0 = [float(event["Time"]) for event in data0["Events"][1:]]
rew_data_0 = [float(event["Reward"]) for event in data0["Events"][1:]]
send_data_0 = [float(event["Send Rate"]) for event in data0["Events"][1:]]
thpt_data_0 = [float(event["Throughput"]) for event in data0["Events"][1:]]
latency_data_0 = [float(event["Latency"]) for event in data0["Events"][1:]]
loss_data_0 = [float(event["Loss Rate"]) for event in data0["Events"][1:]]


fig, axes = plt.subplots(5, figsize=(10, 12))
rew_axis = axes[0]
send_axis = axes[1]
thpt_axis = axes[2]
latency_axis = axes[3]
loss_axis = axes[4]

if(len(sys.argv) == 2):
    rew_axis.plot(time_data_0, rew_data_0)
    rew_axis.set_ylabel("Reward")

    send_axis.plot(time_data_0, send_data_0)
    send_axis.set_ylabel("Send Rate")

    thpt_axis.plot(time_data_0, thpt_data_0)
    thpt_axis.set_ylabel("Throughput")

    latency_axis.plot(time_data_0, latency_data_0)
    latency_axis.set_ylabel("Latency")

    loss_axis.plot(time_data_0, loss_data_0)
    loss_axis.set_ylabel("Loss Rate")
    loss_axis.set_xlabel("Monitor Interval")

    fig.suptitle("Summary Graph for %s" % sys.argv[1])
    fig.savefig("/home/lee/Desktop/training_logs/env_graph.pdf")

elif(len(sys.argv) == 3):
    filename1 = sys.argv[2]
    with open(filename1) as f:
        data1 = json.load(f)

    time_data_1 = [float(event["Time"]) for event in data1["Events"][1:]]
    rew_data_1 = [float(event["Reward"]) for event in data1["Events"][1:]]
    send_data_1 = [float(event["Send Rate"]) for event in data1["Events"][1:]]
    thpt_data_1 = [float(event["Throughput"]) for event in data1["Events"][1:]]
    latency_data_1 = [float(event["Latency"]) for event in data1["Events"][1:]]
    loss_data_1 = [float(event["Loss Rate"]) for event in data1["Events"][1:]]

    rew_axis.plot(time_data_0, rew_data_0, time_data_1, rew_data_1)
    rew_axis.set_ylabel("Reward")
    rew_axis.legend(["model 1", "model 2"])
    rew_axis.grid(True)

    send_axis.plot(time_data_0, send_data_0, time_data_1, send_data_1)
    send_axis.set_ylabel("Send Rate")
    send_axis.legend(["model 1", "model 2"])
    send_axis.grid(True)

    thpt_axis.plot(time_data_0, thpt_data_0, time_data_1, thpt_data_1)
    thpt_axis.set_ylabel("Throughput")
    thpt_axis.legend(["model 1", "model 2"])
    thpt_axis.grid(True)

    latency_axis.plot(time_data_0, latency_data_0, time_data_1, latency_data_1)
    latency_axis.set_ylabel("Latency")
    latency_axis.legend(["model 1", "model 2"])
    latency_axis.grid(True)

    loss_axis.plot(time_data_0, loss_data_0, time_data_1, loss_data_1)
    loss_axis.set_ylabel("Loss Rate")
    loss_axis.set_xlabel("Monitor Interval")
    loss_axis.legend(["model 1", "model 2"])
    loss_axis.grid(True)

    fig.suptitle("Summary Graph for %s" % sys.argv[1])
    fig.savefig("/home/lee/Desktop/training_logs/env_graph.pdf")

elif(len(sys.argv) == 4):

    filename1 = sys.argv[2]
    with open(filename1) as f:
        data1 = json.load(f)

    time_data_1 = [float(event["Time"]) for event in data1["Events"][1:]]
    rew_data_1 = [float(event["Reward"]) for event in data1["Events"][1:]]
    send_data_1 = [float(event["Send Rate"]) for event in data1["Events"][1:]]
    thpt_data_1 = [float(event["Throughput"]) for event in data1["Events"][1:]]
    latency_data_1 = [float(event["Latency"]) for event in data1["Events"][1:]]
    loss_data_1 = [float(event["Loss Rate"]) for event in data1["Events"][1:]]

    filename2 = sys.argv[3]
    with open(filename2) as f:
        data2 = json.load(f)

    time_data_2 = [float(event["Time"]) for event in data2["Events"][1:]]
    rew_data_2 = [float(event["Reward"]) for event in data2["Events"][1:]]
    send_data_2 = [float(event["Send Rate"]) for event in data2["Events"][1:]]
    thpt_data_2 = [float(event["Throughput"]) for event in data2["Events"][1:]]
    latency_data_2 = [float(event["Latency"]) for event in data2["Events"][1:]]
    loss_data_2 = [float(event["Loss Rate"]) for event in data2["Events"][1:]]

    rew_axis.plot(time_data_0, rew_data_0, time_data_1, rew_data_1, time_data_2, rew_data_2)
    rew_axis.set_ylabel("Reward")
    rew_axis.legend(["model 1", "model 2", "model 3"])
    rew_axis.grid(True)

    send_axis.plot(time_data_0, send_data_0, time_data_1, send_data_1, time_data_2, send_data_2)
    send_axis.set_ylabel("Send Rate")
    send_axis.legend(["model 1", "model 2", "model 3"])
    send_axis.grid(True)

    thpt_axis.plot(time_data_0, thpt_data_0, time_data_1, thpt_data_1, time_data_2, thpt_data_2)
    thpt_axis.set_ylabel("Throughput")
    thpt_axis.legend(["model 1", "model 2", "model 3"])
    thpt_axis.grid(True)

    latency_axis.plot(time_data_0, latency_data_0, time_data_1, latency_data_1, time_data_2, latency_data_2)
    latency_axis.set_ylabel("Latency")
    latency_axis.legend(["model 1", "model 2", "model 3"])
    latency_axis.grid(True)

    loss_axis.plot(time_data_0, loss_data_0, time_data_1, loss_data_1, time_data_2, loss_data_2)
    loss_axis.set_ylabel("Loss Rate")
    loss_axis.set_xlabel("Monitor Interval")
    loss_axis.legend(["model 1", "model 2", "model 3"])
    loss_axis.grid(True)

    fig.suptitle("Summary Graph for %s" % sys.argv[1])
    fig.savefig("/home/lee/Desktop/training_logs/env_graph.pdf")










