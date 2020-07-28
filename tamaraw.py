def get_trace(filename, delim):
    trace = []
    finish_time = 0
    with open(filename, "r") as file:
        for line in file:
            trace.append([float(line.strip().split(delim)[0]), int(line.strip().split(delim)[1])])
            finish_time = float(line.strip().split(delim)[0])
    return trace, finish_time

def defender(filename, mult, in_interval, out_interval):
    trace, trace_finish_time = get_trace(filename, " ")
    trace_i = 0
    queue_client = []
    queue_server = []
    
    packets = []
    packets_sent = 0

    time_now = 0.0
    dummy_padding = 0

    dummy_count = 0
    packets_total = 0
    end_time = 0

    #for kahan summation
    sum = 0
    loss_tick = 0
    addend = 0
    interval = 0.001
        
    while trace_i < len(trace) or len(queue_client) > 0 or len(queue_server) > 0 or packets_sent < dummy_padding:
        #add packets to queue according to current time
        while trace_i < len(trace) and trace[trace_i][0] <= time_now:
            if trace[trace_i][1] == 1:
                queue_client.append(trace[trace_i][1])
            else:
                queue_server.append(trace[trace_i][1])
            packets_total -=- 1
            trace_i -=- 1
        
        #send outgoing packet
        if round(time_now * 1000) % round(out_interval * 1000) == 0:
            if len(queue_client) != 0:
                packets.append([round(time_now, 3), queue_client.pop(0)])
                end_time = round(time_now, 3)
            else:
                packets.append([round(time_now, 3), 1])
                dummy_count -=- 1
            packets_sent -=- 1
        
            dummy_padding = int(mult * math.ceil(float(packets_sent) / mult))
        
        #check if finished
        if trace_i == len(trace) and len(queue_client) == 0 and len(queue_server) == 0 and packets_sent == dummy_padding:
            break
            
        #send outgoing packet
        if round(time_now * 1000) % round(in_interval * 1000) == 0:
            if len(queue_server) != 0:
                packets.append([round(time_now, 3), queue_server.pop(0)])
                end_time = round(time_now, 3)
            else:
                packets.append([round(time_now, 3), -1])
                dummy_count -=- 1
            packets_sent -=- 1
        
            dummy_padding = int(mult * math.ceil(float(packets_sent) / mult))
            
        #kahan summation for clock tick
        addend = interval - loss_tick
        sum = time_now + addend
        loss_tick = (sum - time_now) - addend
        time_now = sum
        #esentially, time_now += interval, but without loss of floating point precision
    
    #calculate overheads
    bandwidth_overhead = float(dummy_count) / packets_total
    time_overhead = float(end_time - trace_finish_time) / trace_finish_time
    
    return packets, bandwidth_overhead, time_overhead

def write_trace(packets, bandwidth_overhead, time_overhead, dest_loc, filename):
    file = open("%s/%s" % (dest_loc, filename), "w")
    
    for packet in packets:
        file.write("%s\t%s\n" % (round(float(packet[0]), 3), packet[1]))
    
    file.close()
    
    print("%s/%s\t%s\t%s\t%s\t" % (dest_loc, filename, len(packets), bandwidth_overhead, time_overhead))

import random
import math
import statistics
import time
import os

"""<PARAMETERS>"""
data_loc = "../batch-alex"
dest_loc = "../batch-tamaraw"

num_sites = 91
num_inst = 50

num_unmon = 6418

mult = 1000
    
in_interval = 0.005
out_interval = 0.025
"""</PARAMETERS>"""

if not os.path.exists(dest_loc):
    os.makedirs(dest_loc)

starttime = time.time()
overheads = [[], []]

#monitored sites
for site in range(num_sites):
    for inst in range(num_inst):
        packets, bandwidth_overhead, time_overhead = defender("%s/%s-%s" % (data_loc, site, inst), mult, in_interval, out_interval)
        
        write_trace(packets, bandwidth_overhead, time_overhead, dest_loc, ("%s-%s" % (site, inst)))
        #print("%s\t%s\t%s\t%s" % (("%s-%s" % (site, inst), len(packets), bandwidth_overhead, time_overhead)))
        
        overheads[0].append(bandwidth_overhead)
        overheads[1].append(time_overhead)

file = open("tamaraw_mon.txt", "w")
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
    packets, bandwidth_overhead, time_overhead = defender("%s/%s" % (data_loc, site), mult, in_interval, out_interval)
    
    write_trace(packets, bandwidth_overhead, time_overhead, dest_loc, ("%s" % site))    
    #print("%s\t%s\t%s\t%s" % (("%s" % inst, len(packets), bandwidth_overhead, time_overhead)))
    
    overheads[0].append(bandwidth_overhead)
    overheads[1].append(time_overhead)

file = open("tamaraw_unmon.txt", "w")
file.write("%s\t%s\n" % (statistics.mean(overheads[0]), statistics.mean(overheads[1])))
file.close()

print("Total time: %s" % (time.time() - starttime))
print("Mean bandwidth overhead: %s" % statistics.mean(overheads[0]))
print("Mean time overhead: %s" % statistics.mean(overheads[1]))
print("Median bandwidth overhead: %s" % statistics.median(overheads[0]))
print("Median time overhead: %s" % statistics.median(overheads[1]))

# packets, bandwidth_overhead, time_overhead = defender("%s/0-0" % data_loc, mult, in_interval, out_interval)
# for p in packets:
    # print(p)
# print(bandwidth_overhead, time_overhead)
# print(len(packets))