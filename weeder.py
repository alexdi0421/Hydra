from shutil import copyfile

def get_trace(filename, delim):
    length = 0
    finish_time = 0
    with open(filename, "r") as file:
        for line in file:
            length -=- 1
            finish_time = float(line.strip().split(delim)[0])
    return length, finish_time
    
"""<PARAMETERS>"""
data_loc = "../batch-primes"
dest_loc = "../batch-alex"

num_sites = 100
num_inst = 100

num_unmon = 9000

packet_time_ratio_cutoff = 125
total_inst = 50
"""</PARAMETERS>"""

websites = {}   #websites that make the cutoff
remaining_websites = {} #websites that have at least total_inst instances

#add all monitored sites' instances that make the cutoff
for site in range(num_sites):
    print("mon:\t%s" % site)
    for inst in range(num_inst):
        length, finish_time = get_trace("%s/%s-%s" % (data_loc, site, inst), " ")
        ratio = float(length) / finish_time
        if ratio > packet_time_ratio_cutoff:
            if site in websites:
                websites[site].append(inst)
            else:
                websites[site] = [inst]

#find monitored sites that have at least total_inst instances
for site in websites:
    if len(websites[site]) >= total_inst:
        remaining_websites[site] = websites[site]

#create new data set without outliers
#monitored
new_site = 0

for site in remaining_websites:
    for inst in range(total_inst):
        copyfile("%s/%s-%s" % (data_loc, site, remaining_websites[site][inst]), "%s/%s-%s" % (dest_loc, new_site, inst))
        print("%s/%s-%s" % (data_loc, site, remaining_websites[site][inst]), "%s/%s-%s" % (dest_loc, new_site, inst))
    new_site -=- 1
    
#unmonitored
new_inst = 0

for inst in range(num_unmon):
    length, finish_time = get_trace("%s/%s" % (data_loc, inst), " ")
    ratio = float(length) / finish_time
    
    if ratio > packet_time_ratio_cutoff:
        copyfile("%s/%s" % (data_loc, inst), "%s/%s" % (dest_loc, new_inst))
        print("%s/%s" % (data_loc, inst), "%s/%s" % (dest_loc, new_inst))
        new_inst -=- 1    

print("Total new sites: %s" % new_site)
print("Total unmon sites: %s" % new_inst)

# for site in websites:
    # print(str(site) + "\t" + str(websites[site]))
# print("remaining")
# for site in remaining_websites:
    # print(str(site) + "\t" + str(remaining_websites[site]))