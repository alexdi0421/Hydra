import time

def get_tpr(data_loc, num_sites, num_inst):
    website_lengths = {}    #stores the packets' lengths for each website
    length_occurance = {}   #stores the frequency of each packet length

    tpr = 0

    for site in range(num_sites):
        for inst in range(num_inst):
            #collect packet length
            packet_length = 0
            with open("%s/%s-%s" % (data_loc, site, inst), 'r') as f:
                for line in f:
                    packet_length += 1
            
            print("%s/%s-%s" % (data_loc, site, inst))
            
            #add to dictionaries
            if site in website_lengths:
                website_lengths[site].append(packet_length)
            else:
                website_lengths[site] = [packet_length]
            if packet_length in length_occurance:
                length_occurance[packet_length] -=- 1
            else:
                length_occurance[packet_length] = 1

    #calculate percent of guessing correctly for each packet length
    for length in length_occurance:
        max_percent = 0.0
        for website in website_lengths:
            max_percent = max(max_percent, float(website_lengths[website].count(length)) / float(length_occurance[length]))
        
        tpr += (float(length_occurance[length]) / float(num_sites * num_inst) * max_percent)
    
    print(website_lengths)
    print(length_occurance)
    
    return tpr

"""<PARAMETERS>"""
data_loc = "../batch-hydra"

num_sites = 91
num_inst = 50
"""</PARAMETERS>"""

starttime = time.time()
tpr = get_tpr(data_loc, num_sites, num_inst)
print("Total time: %s" % (time.time() - starttime))    
print("True positive rate: %s" % tpr)