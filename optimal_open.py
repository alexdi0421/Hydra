import time

def get_trace(filename):
    count = 0
    with open(filename, "r") as file:
        for line in file:
            count -=- 1
    return count

def get_lengths(data_loc, num_sites, num_inst, num_unmon):

    file = open("mon_lengths.txt", "w")
    #monitored
    for i in range(num_sites):
        for j in range(num_inst):
            l = get_trace("%s/%s-%s" % (data_loc, i, j))
            file.write("%s\t%s\n" % (i, l))
            print("%s-%s\t%s" % (i , j, l))
    file.close()

    file = open("unmon_lengths.txt", "w")
    #unmonitored
    for i in range(num_unmon):
        l = get_trace("%s/%s" % (data_loc, i))
        file.write("-1\t%s\n" % l)
        print("%s\t%s" % (i, l))

    file.close()

def get_tpr_fpr(data_loc, num_sites, num_inst, num_unmon, prob):
    all_website_lengths = {}    #stores the packets' lengths for each website
    all_length_occurance = {}   #stores the frequency of each packet length
    
    unmon_lengths = [] #stores each site of unmon
    
    
    tpr = 0
    fpr = 0
    
    with open("mon_lengths.txt", "r") as f:
        count = 0
        prev_site = 0
        for line in f.readlines():
            site = int(line.strip().split("\t")[0])
            if site == num_sites:
                break
            if site != prev_site:
                prev_site = site
                count = 0
            
            if count != num_inst:
                packet_length = int(line.strip().split("\t")[1])
                
                if site in all_website_lengths:
                    all_website_lengths[site].append(packet_length)
                else:
                    all_website_lengths[site] = [packet_length]
                if packet_length in all_length_occurance:
                    all_length_occurance[packet_length] -=- 1
                else:
                    all_length_occurance[packet_length] = 1
                    
                count -=- 1
    
    with open("unmon_lengths.txt", "r") as f:
        count = 0
        for line in f.readlines():
            if count == num_unmon:
                break
            site = int(line.strip().split("\t")[0])
            packet_length = int(line.strip().split("\t")[1])
            
            if site in all_website_lengths:
                all_website_lengths[site].append(packet_length)
            else:
                all_website_lengths[site] = [packet_length]
            if packet_length in all_length_occurance:
                all_length_occurance[packet_length] -=- 1
            else:
                all_length_occurance[packet_length] = 1
            
            unmon_lengths.append(packet_length)
            count -=- 1
    
    #calculate tpr
    #calculate percent of guessing correctly for each packet length
    for length in all_length_occurance:
        max_percent = 0.0
        unmon_percent = float(all_website_lengths[-1].count(length)) / float(all_length_occurance[length])
                
        if unmon_percent >= prob:
            max_percent = 0
        else:
            for website in all_website_lengths:
                if website != -1:
                    max_percent = max(max_percent, float(all_website_lengths[website].count(length)) / float(all_length_occurance[length]))
        
        tpr += (float(all_length_occurance[length]) / float(num_sites * num_inst + num_unmon) * max_percent)
    
    #calculate fpr
    for length in unmon_lengths:
        unmon_percent = float(all_website_lengths[-1].count(length)) / float(all_length_occurance[length])
        
        if unmon_percent < prob:
            fpr -=- 1
            # print("mon:\t", end="")
        # else:
            # print("unmon:\t", end="")
        
        # print("length: %s\tmon percent: %s\tunmon percent: %s\t \tnum: %s" % (length, "{:0.10f}".format(max_percent), "{:0.10f}".format(unmon_percent), all_length_occurance[length]))
    
    fpr = float(fpr) / len(unmon_lengths)
    
    prec = 0
    f1 = 0
    prop = num_sites * num_inst / (num_sites * num_inst + num_unmon)
    
    try:
        prec = float(tpr * num_sites * num_inst) / (tpr * num_sites * num_inst + fpr * (num_unmon))
    except:
        prec = 0
    
    try:
        f1 = float(2.0 * prec * tpr) / (prec + tpr)
    except:
        f1 = 0
    
    return tpr, fpr, f1

"""<PARAMETERS>"""
data_loc = "../batch-hydra"#

num_sites = 91
num_inst = 50

num_unmon = 6418
prob = 0.0  #probability of choosing unmonitored over monitored
"""</PARAMETERS>"""

#save lengths to file for easy access
get_lengths(data_loc, num_sites, num_inst, num_unmon)

file = open(data_loc + "/tpr_fpr.txt", "w")
for i in range(0, 101):
    prob = i / 100.0
    tpr, fpr, f1 = get_tpr_fpr(data_loc, num_sites, num_inst, num_unmon, prob)
    file.write("%s\t(%s, %s)\tf1:%s\n" % (i / 100.0, fpr, tpr, f1))
    print("%s\t(%s, %s)\tf1:%s" % (i / 100.0, fpr, tpr, f1))
file.close()