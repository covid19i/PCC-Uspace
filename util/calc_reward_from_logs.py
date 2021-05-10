import pprint

BYTES_PER_PACKET = 1500
REWARD_SCALE = 0.001

model_rewards = {}

def print_rewards(s):
    print('File:', s)
    with open(s,'r') as f:
        data=[x.strip().replace("\t\t", "\t").split('\t') for x in f]
    reward = []
    prev_datum = [0., 0., 0., 0., 0.]
    for datum in data:
        #Page 4 of DRL for Congestion
        #10 ∗ throughput − 1000 ∗ latency − 2000 ∗ loss
        #where throughput is measured in packets per second, latency in seconds, 
        #and loss is the proportion of all packets sent but not acknowledged
        if((float(datum[3]) - float(prev_datum[3])) != 0):
            loss_rate = (float(datum[4]) - float(prev_datum[4])) / (float(datum[3]) - float(prev_datum[3]))
        else:
            loss_rate = 0
        reward.append(10 * float(datum[1]) * 1e6 / (8 * BYTES_PER_PACKET) -  float(datum[2]) - 
                      2e3 * loss_rate )
        #datum[3] = float(datum[3]) - float(prev_datum[3])
        #datum[4] = float(datum[4]) - float(prev_datum[4])
        prev_datum = datum
        print(datum, reward[-1])
        #print(reward[-1])
    print('\nAverage Reward in the last 10 rounds:')
    print(sum(reward[-10:])/10)
    print('\n\n\n')
    model_rewards[s] = sum(reward[-10:])/10

print_rewards('/Users/ilyeech/Networks and Mobile Systems/Project/logs/bigger_one_loop.txt')
print_rewards('/Users/ilyeech/Networks and Mobile Systems/Project/logs/bigger_six_loops.txt')
print_rewards('/Users/ilyeech/Networks and Mobile Systems/Project/logs/16x6layers_run3.txt')
print_rewards('/Users/ilyeech/Networks and Mobile Systems/Project/logs/32x4layers_3rdrun.txt')
print_rewards('/Users/ilyeech/Networks and Mobile Systems/Project/logs/32x4layers_60loops.txt')
print_rewards('/Users/ilyeech/Networks and Mobile Systems/Project/logs/8layers_tapering_run2.txt')
print_rewards('/Users/ilyeech/Networks and Mobile Systems/Project/logs/8layers_tapering_run8.txt')
print_rewards('/Users/ilyeech/Networks and Mobile Systems/Project/logs/8layers_60loops.txt')
print_rewards('/Users/ilyeech/Networks and Mobile Systems/Project/logs/original_six_loops.txt')
print_rewards('/Users/ilyeech/Networks and Mobile Systems/Project/logs/LSTM_run3_1600x410_2048_1_lstm_dim_256_test_run1.txt')
#print_rewards('/Users/ilyeech/Networks and Mobile Systems/Project/logs/LSTM_run3_1600x410_2048_1_lstm_dim_256_test_run2.txt')

print_rewards('/Users/ilyeech/Networks and Mobile Systems/Project/logs/LSTM_run6_1600x410_2048_1_lstm_dim_128_test_run1.txt')
print_rewards('/Users/ilyeech/Networks and Mobile Systems/Project/logs/LSTM_run4_1600x410_2048_1_lstm_dim_64_test_run_1.txt')
print_rewards('/Users/ilyeech/Networks and Mobile Systems/Project/logs/LSTM_run4_1600x410_2048_1_lstm_dim_64_test_run_2.txt')
print_rewards('/Users/ilyeech/Networks and Mobile Systems/Project/logs/LSTM_run4_1600x410_2048_1_lstm_dim_64_test_run_3_Mininet.txt')
print_rewards('/Users/ilyeech/Networks and Mobile Systems/Project/logs/LSTM_run5_1600x410_2048_1_lstm_dim_32_test_run_1.txt')
print_rewards('/Users/ilyeech/Networks and Mobile Systems/Project/logs/LSTM_run7_1600x410_2048_1_lstm_dim_16_test_run1.txt')

print("Summary:")
#print(model_rewards)
pprint.pprint(model_rewards)

print("\nWARNING: LSTM numbers aren't from Mininet. Others: Check!")