#!/usr/bin/python3.6
import json
import sys
# define an example stp_domain to work with
# each link is described by the use of following pattern :
# (switch that this link leads to): [(cost of the link), (root path cost), (port role), (port priority), (port id)]
# Ports Roles : 
# RP = root port
# DP = designated port
# BP = blocking port

stp_domain = {}

with open("stp_domains/3_switch.json", "r") as infile:
    stp_domain = json.load(infile)
#print(stp_domain)

counter = 65536255
root_bridge = ''

# find a root bridge
for switch in stp_domain:
    if stp_domain[switch]["bridgeID"] < counter:
        root_bridge = switch
        counter = stp_domain[switch]["bridgeID"]


# set the roles for all bridges (root|non-root)
for switch_name in stp_domain:
    switch = stp_domain[switch_name]
    switch["role"] = "root" if switch_name == root_bridge else "non-root"
    if switch["role"] == "root":
        for key in switch.keys():
            if key.startswith('s'):
                switch[key][2] = "DP"

# create two holders
directly_connected = []
not_directly_connected = []
# update lowest cost for switches directly connected to the root bridge
# and find out who is/isn't directly connected
for switch in stp_domain:
    if root_bridge in stp_domain[switch]:
        stp_domain[switch][root_bridge][1] = stp_domain[switch][root_bridge][0]
        stp_domain[switch]["lowest"] = root_bridge
        stp_domain[switch][root_bridge][2] = "RP"
        directly_connected.append(switch)
    elif switch != root_bridge:
        not_directly_connected.append(switch)

# creating a dictionary of directly connected devices
directly_connected_dict = { directly_connected[index]:stp_domain[directly_connected[index]] for index in range (len(directly_connected))}

# creating a dictionary of not directly connected devices
#not_directly_connected_dict = {not_directly_connected[index]:stp_domain[not_directly_connected[index]] for index in range (len(not_directly_connected))}
#print(directly_connected_dict)
# define root path cost for all of directly connected devices
for localised in directly_connected_dict:
    for neighbor in directly_connected:
        local = directly_connected_dict[localised] #for simpler naming
        if neighbor in local:
        # local to neighbor cost + neighbor to root bridge cost
            link_to_neighbor_cost = local[neighbor][0]
            neighbors_root_path_cost = directly_connected_dict[neighbor][root_bridge][1]
            local[neighbor][1] = link_to_neighbor_cost + neighbors_root_path_cost #get the root path cost on this outgoing port
           # print("Lowest right now is: ", local[local["lowest"]][1])
            # define an active root port
            if local[neighbor][1] < local[local["lowest"]][1]: #local[root_bridge][1]: #<---- new
                local[root_bridge][2] = "none" 
                local["lowest"] = neighbor      # define a label for a root port
                local[neighbor][2]="RP"   # define a role as a root port

#if len(not_directly_connected) >= 1: # important check of whether not directly devices actually exist !!
#    print(not_directly_connected)
# creating a dictionary of not directly connected devices
not_directly_connected_dict = {not_directly_connected[index]:stp_domain[not_directly_connected[index]] for index in range (len(not_directly_connected))}
#testing
#print(stp_domain["s6"])
for localised in not_directly_connected_dict:
    local = not_directly_connected_dict[localised] # get a dictionary with a useful name that relates to a local switch
    for neighbor_name in directly_connected_dict: 
        neighbor = directly_connected_dict[neighbor_name]
        if neighbor_name in local: 
        # local to neighbor cost + neighbor to root bridge cost
            link_to_neighbor_cost = local[neighbor_name][0]
            neighbors_root_path_cost = neighbor[neighbor["lowest"]][1]
            #print("the loest cost throuh ", neighbor_name, "is :", neighbor[neighbor["lowest"]][1])
            local[neighbor_name][1] = link_to_neighbor_cost + neighbors_root_path_cost # get the root path cost on this egress port
            #print("the lowest cost through ", neighbor_name, " is :", local[neighbor_name][1])
            
            if  local["lowest"] == '':    # add inital root port if none exist 
                local["lowest"] = neighbor_name
                local[local["lowest"]][2] = "RP" # use the "lowest" attribute of a port to assign the root port role accurately
            elif local[local["lowest"]][1] == local[neighbor_name][1]:                              # in case of a cost tie
                if stp_domain[local["lowest"]]["bridgeID"] > stp_domain[neighbor_name]["bridgeID"]: # look at the bridge ID of neighboring switches, the lower one wins
                    local[local["lowest"]][2] = "none"                                              # re-assign appropriate roles (if necessary)
                    local["lowest"] = neighbor_name
                    local[local["lowest"]][2] = "RP"
            elif local[local["lowest"]][1] > local[neighbor_name][1]:  # update the root port as necessary
                local[local["lowest"]][2] = "none"  # reset the root port and subsequently define a new root port
                local["lowest"] = neighbor_name
                local[local["lowest"]][2] = "RP"
            elif local[local["lowest"]][1] < neighbor[neighbor["lowest"]][1]: 
                neighbor[neighbor["lowest"]][2] = "none"
                neighbor["lowest"] = localised
                neighbor[neighbor["lowest"]][2] = "RP" 
                

# for the designated ports sake check the cost between the not directly connected neighbors
for localised in not_directly_connected_dict:
    local = not_directly_connected_dict[localised] # get a local machine variable
    for neighbor_name in not_directly_connected_dict:
        neighbor = not_directly_connected_dict[neighbor_name] # get a neighbor machine variable 
        if neighbor_name in local:                               
        # local to neighbor cost + neighbor to root bridge cost
        #    print(neighbor_name)
            link_to_neighbor_cost = local[neighbor_name][0]      
            neighbor_root_path_cost = neighbor[neighbor["lowest"]][1]
            local[neighbor_name][1] = link_to_neighbor_cost + neighbor_root_path_cost
            if  local["lowest"] == '':    # add inital root port if none exist 
                local["lowest"] = neighbor_name
                local[local["lowest"]][2] = "RP" # use the "lowest" attribute of a port to assign the root port role accurately
            elif local[local["lowest"]][1] == local[neighbor_name][1]:                              # in case of a cost tie
                if stp_domain[local["lowest"]]["bridgeID"] > stp_domain[neighbor_name]["bridgeID"]: # look at the bridge ID of neighboring switches, the lower one wins
                    local[local["lowest"]][2] = "none"                                              # re-assign appropriate roles (if necessary)
                    local["lowest"] = neighbor_name
                    local[local["lowest"]][2] = "RP"

            elif local[local["lowest"]][1] > local[neighbor_name][1]:  # update the root port as necessary
                local[local["lowest"]][2] = "none"  # reset the root port and subsequently define a new root port
                local["lowest"] = neighbor_name
                local[local[neighbor_name[2]]] = "RP" 

# complete the directly connected machines with paths leading through not directly connected devices, for the sake of designated ports
for localised in directly_connected_dict:
    local = directly_connected_dict[localised] # get a dictionary with a useful name to reflect local switches
    for neighbor_name in not_directly_connected_dict:
        neighbor = not_directly_connected_dict[neighbor_name]    # get a dictionary with a useful name to reflect neighboring switches
        if neighbor_name in local : 
            lowest_cost_key = 2000000000  # some arbitrary potentialy unreachable cost (for a small network)
            if neighbor["lowest"] == localised  or stp_domain[neighbor["lowest"]]["lowest"] == localised:    # find neighbor with a local machines with root port facing local machine
                for key in  neighbor.keys():    
                    if key.startswith('s') and stp_domain[key]["lowest"] != localised and key != localised: # parse neighbor links for paths not leading back through local machine
                        lowest_cost_key = neighbor[key][1] if neighbor[key][1] < lowest_cost_key else lowest_cost_key   # find the lowest cost that we can use
                link_to_neighbor_cost = local[neighbor_name][0]                                                      
                neighbor_selected_path_cost = lowest_cost_key + link_to_neighbor_cost
                local[neighbor_name][1] = neighbor_selected_path_cost
            else:
                for key in  neighbor.keys():    
                    if key.startswith('s') and stp_domain[key]["lowest"] != localised and key != localised: # parse neighbor links for paths not leading back through local machine
                        lowest_cost_key = neighbor[key][1] if neighbor[key][1] < lowest_cost_key else lowest_cost_key   # find the lowest cost that we can use
                link_to_neighbor_cost = local[neighbor_name][0]                                                      
                neighbor_selected_path_cost = lowest_cost_key + link_to_neighbor_cost
                local[neighbor_name][1] = neighbor_selected_path_cost

# find designated ports 
for switch_name in stp_domain:
    if switch_name is not root_bridge:  # mainly look at non-root switches
        local = stp_domain[switch_name] # define a local switch dictionary for simplicity
        for neighbor_name in stp_domain:
            neighbor = stp_domain[neighbor_name] # define possible nieighbors
            if neighbor_name in local and neighbor_name != root_bridge: # exclude root bridge from neighbors search
                #print(switch_name, " has ", neighbor_name, "as a neighbor")
                neighbor_lowest_root_cost = neighbor[neighbor["lowest"]][1]
                local_lowest_root_cost = local[local["lowest"]][1]
                if local[neighbor_name][2] == "RP":
                    neighbor[switch_name][2] = "DP"
                elif neighbor_lowest_root_cost >  local_lowest_root_cost: #neighbor[neighbor["lowest"]][1] > local[local["lowest"]][1]: # if neighbor has a lowest root path cost, let his port be designated
                    local[neighbor_name][2] = 'DP'
                elif neighbor_lowest_root_cost ==  local_lowest_root_cost: #neighbor[neighbor["lowest"]][1] == local[local["lowest"][1]:
                    if local["bridgeID"] < neighbor["bridgeID"]:
                        local[neighbor_name][2] = 'DP'
                        neighbor[switch_name][2] = 'BP'
                    else:
                        neighbor[switch_name][2] = 'DP'
                        local[neighbor_name][2] = 'BP'
                    # Can use this test for better understaning of the process
                    #print("neighbor: ", neighbor_name)
                    #print("neighbors lowest cost is: ", neighbor[neighbor["lowest"]][1])
                    #print("local: ", switch_name)
                    #print("local lowest cost is: ",local[local["lowest"]][1])
        #print("\nChange switch\n")

# set all root bridges port to be DP
for item in stp_domain[root_bridge]:
    if item.startswith('s'):
        stp_domain[root_bridge][item][2] = "DP"
# set everything else to a blocking port
for switch_name in stp_domain:
    switch = stp_domain[switch_name]
    for key in switch.keys():
        if key.startswith('s'):
            if switch[key][2] == "none":
                switch[key][2] = "BP"

# For simple testing
#print("s1 info: ",stp_domain["s1"])
#print("s2 info: ",stp_domain["s2"])
#print("s3 info: ",stp_domain["s3"])
#print("s4 info: ",stp_domain["s4"])
#print("s5 info: ",stp_domain["s5"])
#print("s6 info: ",stp_domain["s6"])

for switch_name in stp_domain:
    designated_ports = []
    blocking_ports = []
    switch = stp_domain[switch_name]
    print("The ", switch["name"], " info:")
    print("Bridge role: ",  switch["role"])
    print("Bridge ID: ", switch["bridgeID"])
    if switch["role"] != "root":   # no need to look for a root port on a root bridge
        print("Root port: ", switch[switch["lowest"]][4])
    for key in switch.keys():   # make sure that there are any designated ports
        if key.startswith('s') and switch[key][2] == "DP":
            designated_ports.append(str(switch[key][4]))
    print("Designated ports: ", ', '.join(designated_ports) if designated_ports else "None")
    for key in switch.keys():   # make sure that there are any blocking ports
        if key.startswith('s') and switch[key][2] == "BP":
            blocking_ports.append(str(switch[key][4]))
    
    print("Blocking ports: ", ', '.join(blocking_ports) if blocking_ports else "None")
    print(40 * '-')

with open("results/result.json", "w") as ofile:
    json.dump(stp_domain, ofile)

