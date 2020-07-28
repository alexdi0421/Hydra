import numpy as np
import time

def get_trace(filename, delim):
    trace = []
    with open(filename, "r") as file:
        for line in file:
            trace.append([line.strip().split(delim)[0], line.strip().split(delim)[1]])
    return trace
    
def defender(filename, num_net):    
    trace = get_trace(filename, " ")
    
    probs = np.random.dirichlet([1 for _ in range(num_net)])
    net_to_send = np.random.choice(a=range(num_net), size=len(trace), p=probs)
    
    paths = [[] for _ in range(num_net)]
        
    for i in range(len(trace)):      
        paths[net_to_send[i]].append(trace[i])
    
    return paths

def write_trace(paths, dest_loc, filename):
    #filter out emtpy paths
    paths_to_choose = []
    
    for k in range(len(paths)):
        if len(paths[k]) != 0:
            paths_to_choose.append(k)
    
    #pick one randomly    
    path_to_write = paths_to_choose[np.random.randint(0, len(paths_to_choose))]
            
    #write one of the paths, which is not empty, to file
    file = open("%s/%s" % (dest_loc, filename), "w")
    
    #start every trace at t = 0
    t0 = float(paths[path_to_write][0][0])
    for packet in paths[path_to_write]:
        file.write("%s\t%s\n" % (float(packet[0]) - t0, packet[1]))
    
    file.close()
    
    print("%s: %s/%s\t%s" % (path_to_write, dest_loc, filename, str([len(paths[i]) for i in range(len(paths))]).replace(", ", "\t")[1:-1]))

"""<PARAMETERS>"""
data_loc = "../batch-alex"
dest_loc = "../batch-traffic-split"

num_sites = 0#91
num_inst = 50

num_unmon = 6418

num_nets = 5
"""</PARAMETERS>"""

#monitored
for site in range(num_sites):
    for inst in range(num_inst):
        paths = defender("%s/%s-%s" % (data_loc, site, inst), num_nets)
        write_trace(paths, dest_loc, "%s-%s" % (site, inst))

#unmonitored
for inst in range(num_unmon):
    paths = defender("%s/%s" % (data_loc, inst), num_nets)
    write_trace(paths, dest_loc, "%s" % inst)