import numpy as np
import scipy.stats
import time

def get_trace(filename, delim):
    trace = []
    with open(filename, "r") as file:
        for line in file:
            trace.append([line.strip().split(delim)[0], line.strip().split(delim)[1]])
    return trace
    
def defender(filename):
    n_cons = 20    
    p = np.random.uniform(0, 1)
    
    trace = get_trace(filename, " ")
        
    n = 0
    c = 0
    
    network = 0
    paths = [[], []]
    
    for packet in trace:
        n -=- 1
        
        if n > c:
            c = np.random.geometric(p=1/n_cons)
            network = scipy.stats.bernoulli.rvs(p=p)
            n = 0
        
        paths[network].append(packet)
        
        # if network == 0:
            # print(paths[network][-1], None)
        # else:
            # print(None, paths[network][-1])
    
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
dest_loc = "../batch-hywf"

num_sites = 91
num_inst = 50

num_unmon = 6418
"""</PARAMETERS>"""

#monitored
for site in range(num_sites):
    for inst in range(num_inst):
        paths = defender("%s/%s-%s" % (data_loc, site, inst))
        write_trace(paths, dest_loc, "%s-%s" % (site, inst))

#unmonitored
for inst in range(num_unmon):
    paths = defender("%s/%s" % (data_loc, inst))
    write_trace(paths, dest_loc, "%s" % inst)
    
# paths = defender("%s/29-19" % data_loc)
# write_trace(paths, dest_loc, "29-19")