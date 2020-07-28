import random
import math

def get_trace(filename, delim):
    trace = []
    finish_time = 0
    with open(filename, "r") as file:
        for line in file:
            trace.append([float(line.strip().split(delim)[0]), int(line.strip().split(delim)[1])])
            finish_time = float(line.strip().split(delim)[0])
    return trace, finish_time

def defender(filename, num_paths, interval, threshold, base):
    trace, trace_finish_time = get_trace(filename, " ")
    trace_i = 0
    queue_client = []
    queue_server = []
    
    paths = [[] for _ in range(num_paths)]
    packets_sent = [0 for _ in range(num_paths)]

    time_now = 0.0
    dummy_padding = [0 for _ in range(num_paths)]

    dummy_count = 0
    end_time = 0
    
    client_sent = [False for _ in range(num_paths)]
    is_path_used = [False for _ in range(num_paths)]
    is_path_open = [True for _ in range(num_paths)]

    #for kahan summation
    sum = 0
    loss_tick = 0
    addend = 0
        
    while trace_i < len(trace) or len(queue_client) > 0 or len(queue_server) > 0 or any([packets_sent[i] < dummy_padding[i] for i in range(len(dummy_padding))]):
        #add packets to queue according to current time
        while trace_i < len(trace) and trace[trace_i][0] <= time_now:
            if trace[trace_i][1] == 1:
                queue_client.append(trace[trace_i][1])
            else:
                queue_server.append(trace[trace_i][1])
            trace_i -=- 1
        
        #five packet pattern
        for t in range(5):
            path = [[0, 0] for _ in range(num_paths)]   #solely for display purposes
            #determine whether or not to send packets for each path
            for i in range(0, len(path)):
                if is_path_open[i]:
                    #1 out going packet
                    if t == 0:
                        #assume client sends
                        client_sent[i] = True
                        #send dummy when no packets in queue
                        if (len(queue_client) <= threshold[i] - i) and (len(queue_server) > threshold[i] - i or packets_sent[i] < dummy_padding[i] or (i == 0 and trace_i < len(trace))):    
                            paths[i].append((format(time_now, ".3f"), 1))
                            path[i][0] = 2  #soley for display purposes. 2 is not written to file
                            dummy_count -=- 1
                            packets_sent[i] -=- 1
                        #send real packets
                        elif len(queue_client) > threshold[i] - i:
                            paths[i].append((format(time_now, ".3f"), queue_client.pop(0)))
                            path[i][0] = paths[i][-1][1]
                            if trace_i == len(trace) and len(queue_client) == 0 and len(queue_server) == 0:
                                end_time = time_now
                            packets_sent[i] -=- 1
                        #send no packets when path is closed
                        else:
                            #if not, client didn't send
                            client_sent[i] = False
                    #followed by 4 incoming packets
                    else:
                        #send dummy when no packets in queue
                        if (len(queue_server) <= threshold[i] - i) and (len(queue_client) > threshold[i] - i or client_sent[i]):
                            paths[i].append((format(time_now, ".3f"), -1))
                            path[i][1] = -2 #soley for display purposes. -2 is not written to file
                            dummy_count -=- 1
                            packets_sent[i] -=- 1
                        #send real packets
                        elif len(queue_server) > threshold[i] - i:
                            paths[i].append((format(time_now, ".3f"), queue_server.pop(0)))
                            path[i][1] = paths[i][-1][1]
                            if trace_i == len(trace) and len(queue_client) == 0 and len(queue_server) == 0:
                                end_time = time_now
                            packets_sent[i] -=- 1
                        #otherwise, no packets sent
                
                #determine padding
                if packets_sent[i] != 0:
                    #dummy_padding[i] = int(base * math.ceil(float(packets_sent[i]) / base))
                    dummy_padding[i] = max(int(base ** math.ceil(math.log(math.ceil(float(packets_sent[i]) / 10.0), base))) * 10, 0)
                
                #decide which paths to close
                if client_sent[i]:
                    is_path_used[i] = True
                if not client_sent[i] and is_path_used[i] and i != 0:
                    is_path_open[i] = False
            
            #print("%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s" % (format(time_now, ".3f"), path[0], path[1], path[2], packets_sent, dummy_padding, len(queue_client), len(queue_server)))
                        
            #kahan summation for clock tick
            addend = interval - loss_tick
            sum = time_now + addend
            loss_tick = (sum - time_now) - addend
            time_now = sum
            #esentially, time_now += interval, but without loss of floating point precision
    
    #calculate overheads
    bandwidth_overhead = float(dummy_count) / len(trace)
    time_overhead = float(end_time - trace_finish_time) / trace_finish_time
    
    return paths, bandwidth_overhead, time_overhead

def write_trace(paths, bandwidth_overhead, time_overhead, dest_loc, filename):
    #filter out emtpy paths
    paths_to_choose = []
    
    for k in range(len(paths)):
        if len(paths[k]) != 0:
            paths_to_choose.append(k)
    
    #pick one randomly
    path_to_write = paths_to_choose[random.randint(0, len(paths_to_choose) - 1)]
    
    #write one of the paths, which is not empty, to file
    file = open("%s/%s" % (dest_loc, filename), "w")
    
    #start every trace at t = 0
    t0 = float(paths[path_to_write][0][0])
    for packet in paths[path_to_write]:
        file.write("%s\t%s\n" % (float(packet[0]) - t0, packet[1]))
    
    file.close()
    
    print("%s: %s/%s\t%s\t%s\t%s\t" % (path_to_write, dest_loc, filename, str([len(paths[i]) for i in range(len(paths))]).replace(", ", "\t")[1:-1], bandwidth_overhead, time_overhead))

import statistics
import time
import os

"""<PARAMETERS>"""
data_loc = "../batch-alex"
dest_loc = "../batch-hydra"

num_sites = 91
num_inst = 50

num_unmon = 6418

num_paths = 2
threshold = [0, 400]#[0] + [round(math.exp(i * math.log(max_threshold) / num_paths)) * 100 for i in range(1, num_paths + 1)]
base = 1.1

interval = 0.005
"""</PARAMETERS>"""

if not os.path.exists(dest_loc):
    os.makedirs(dest_loc)

starttime = time.time()
overheads = [[], []]

#monitored sites
for site in range(num_sites):
    for inst in range(num_inst):
        paths, bandwidth_overhead, time_overhead = defender("%s/%s-%s" % (data_loc, site, inst), num_paths, interval, threshold, base)
        
        write_trace(paths, bandwidth_overhead, time_overhead, dest_loc, ("%s-%s" % (site, inst)))
        #print("%s\t%s\t%s\t%s" % (("%s-%s" % (site, inst), str([len(paths[i]) for i in range(len(paths))]).replace(", ", "\t")[1:-1], bandwidth_overhead, time_overhead)))
        
        overheads[0].append(bandwidth_overhead)
        overheads[1].append(time_overhead)

file = open("hydra_mon.txt", "w")
file.write("%s\t%s\n" % (statistics.mean(overheads[0]), statistics.mean(overheads[1])))
file.close()

print("Total time: %s" % (time.time() - starttime))
print("Mean bandwidth overhead: %s" % statistics.mean(overheads[0]))
print("Mean time overhead: %s" % statistics.mean(overheads[1]))
print("Median bandwidth overhead: %s" % statistics.median(overheads[0]))
print("Median time overhead: %s" % statistics.median(overheads[1]))

starttime = time.time()
overheads = [[], []]

#unmonitored sites
for site in range(num_unmon):
    paths, bandwidth_overhead, time_overhead = defender("%s/%s" % (data_loc, site), num_paths, interval, threshold, base)
    
    write_trace(paths, bandwidth_overhead, time_overhead, dest_loc, ("%s" % site))
    #print("%s\t%s\t%s\t%s" % (("%s" % site), str([len(paths[i]) for i in range(len(paths))]).replace(", ", "\t")[1:-1], bandwidth_overhead, time_overhead))    
    
    overheads[0].append(bandwidth_overhead)
    overheads[1].append(time_overhead)
    
file = open("hydra_unmon.txt", "w")
file.write("%s\t%s\n" % (statistics.mean(overheads[0]), statistics.mean(overheads[1])))
file.close()

print("Total time: %s" % (time.time() - starttime))
print("Mean bandwidth overhead: %s" % statistics.mean(overheads[0]))
print("Mean time overhead: %s" % statistics.mean(overheads[1]))
print("Median bandwidth overhead: %s" % statistics.median(overheads[0]))
print("Median time overhead: %s" % statistics.median(overheads[1]))