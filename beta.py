#!/usr/bin/python3.6

from classes.utils import STPUtils
import sys
# define an example stp_domain to work with

# each link is described by the use of a following pattern :
# (switch that this link leads to): [(cost of the link), (root path cost), (port role), (port priority), (port id), (device name)]

# Ports Roles : 
# RP = root port
# DP = designated port
# BP = blocking port

#stp_domain = {}

# verify that Ctrl-D has not been issued
try:
    utils = STPUtils()
    stp_domain = utils.getInfile(sys.argv)
except  EOFError:
    print("\n[Ctrl-D] Shutting down...")
    exit(1)


counter = 65536255
root_bridge = ''

# find a root bridge
for switch in stp_domain:
    if stp_domain[switch]["bridgeID"] < counter:
        root_bridge = switch
        counter = stp_domain[switch]["bridgeID"]

print(root_bridge)
def setRootBridge(stp_domain):
    """
    Functions finds the root bridge amongst all switches in the domain
    """
    #set max possible bridge ID
    counter = 65536255
    root_bridge = ''
    for switchName in stp_domain:
        switch = stp_domain[switchName]
        if switch["bridgeID"] < counter:
            root_bridge = switchName
            counter = stp_domain[switchName]["bridgeID"]
    return root_bridge
 

#print(root_bridge)

def setRoles(root_bridge, stp_domain):
    """
    Function sets the roles for all bridges (root|non-root)
    """
    for switch_name in stp_domain:
        switch = stp_domain[switch_name]
        switch["role"] = "root" if switch_name == root_bridge else "non-root"
        if switch["role"] == "root":
            for key in switch.keys():
                  if key.startswith('s'):
                    switch[key][2] = "DP"
    return stp_domain

def defineSwitchType(stp_domain):
    """
    Function updates the lowest cost for switches that are directly connected to the root bridge
     and figures out who is/isn't directly connected
    """
    #create two holders
    directly_connected = []
    not_directly_connected = []
    for switch in stp_domain:
        if root_bridge in stp_domain[switch]:
            stp_domain[switch][root_bridge][1] = stp_domain[switch][root_bridge][0]
            stp_domain[switch]["lowest"] = root_bridge
            stp_domain[switch][root_bridge][2] = "RP"
            directly_connected.append(switch)
        elif switch != root_bridge:
            not_directly_connected.append(switch)  
    return directly_connected, not_directly_connected, stp_domain

def setDictionaryOfSwitches(switches_list):
    # creating a dictionary of directly connected devices
    return  { switches_list[index]:stp_domain[switches_list[index]] for index in range (len(switches_list))}

def calculateCostThroughNeighbor(neighbor_name, local, root_bridge):
    lowest_current_local_root_path_cost = local[local["lowest"]][1]
    link_to_neighbor_cost = local[neighbor_name][0] 
    neighbor_root_path_cost = directly_connected_dict[neighbor_name][root_bridge][1] 
    local[neighbor_name][1] = link_to_neighbor_cost + neighbor_root_path_cost
    root_path_cost_through_neighbor = local[neighbor_name][1]
    return root_path_cost_through_neighbor < lowest_current_local_root_path_cost
                
        
def setRootPathCostForDirectlyConnected(switches_dict, switches_list, root_bridge):
    for local_name in switches_dict:
        for neighbor_name in switches_list:
            local = switches_dict[local_name] 
            if neighbor_name in local:
                result = calculateCostThroughNeighbor(neighbor_name, local, root_bridge)
                if result:
                    local[root_bridge][2] = "none"
                    local["lowest"] = neighbor_name
                    local[neighbor_name][2] = "RP"
    return switches_dict

def setNewRootPort(local, neighbor_name, reset=True):
    if reset:
        local[local["lowest"]][2] = "none"    # reset the root port if necessary
    local["lowest"] = neighbor_name           # name the lowest switch appropriately
    local[local["lowest"]][2] = "RP"          # define a new root port

def setRootPathCostForNotDirectlyConnected(not_directly_connected_dict, directly_connected_dict, stp_domain):
    """
    Function is setting the remaining root ports on both type of switches (connected|not connected)
    """
    for local_name in not_directly_connected_dict:
        local = not_directly_connected_dict[local_name]
        for neighbor_name in directly_connected_dict:
            neighbor = directly_connected_dict[neighbor_name]
            if neighbor_name in local:
                # local to neighbor cost + neighbor to root bridge cost
                link_to_neighbor_cost = local[neighbor_name][0]
                neighbors_root_path_cost = neighbor[neighbor["lowest"]][1]
                local[neighbor_name][1] = link_to_neighbor_cost + neighbors_root_path_cost
                if local["lowest"] == '':  # add initial root port if none exist
                    setNewRootPort(local, neighbor_name, False)
                elif local[local["lowest"]][1] == "RP":                                                         # in case of a cost tie
                    if stp_domain[local["lowest"]]["bridgeID"] > stp_domain[neighbor_name]["bridgeID"]:         # look at the bridge ID of neighboring switches, the lower one wins
                        setNewRootPort(local, neighbor_name)    
                elif local[local["lowest"]][1] == "RP" or local[local["lowest"]][1] > local[neighbor_name][1] \
                     or local[local["lowest"]][1] < neighbor[neighbor["lowest"]][1]:    # if appropriate port is already set to the lowest or if a local lowest is smaller than the neighbors lowest
                    setNewRootPort(local, neighbor_name)
    return not_directly_connected, stp_domain
 
def verifyCostBetweenNotDirectlyConnectedDevices(not_directly_connected_dict):

    for local_name in not_directly_connected_dict:
        local = not_directly_connected_dict[local_name]  # get a local machine information
        for neighbor_name in not_directly_connected_dict:
            neighbor = not_directly_connected_dict[neighbor_name] # get a neighboring machine name
            if neighbor_name in local:
                link_to_neighbor_cost = local[neighbor_name][0]
                neighbor_root_path_cost = neighbor[neighbor["lowest"]][1]
                local[neighbor_name][1] = link_to_neighbor_cost + neighbor_root_path_cost
                if local["lowest"] == '':    # add inital RP if none exist 
                    setNewRootPort(local, neighbor_name, False)
                elif local[local["lowest"]][1] == local[neighbor_name][1]:                                  # in case of a cost tie
                    if stp_domain[local["lowest"]]["bridgeID"] > stp_domain[neighbor_name]["bridgeID"]:     # look at the bidge ID of neighboring switches, the lower one wins
                        setNewRootPort(local, neighbor_name)                                                # re-assign appropriate roles (if necessary)
                elif local[local["lowest"]][1] > local[neighbor_name][1]:    # if the local lowest distance is bigger than the Root path cost for the neighboring switch
                    setNewRootPort(local, neighbor_name)                     # reset the root port and subsequently define a correct one   return not_directly_connected_dict


def calculateCostsForNonRootPorts(directly_connected_dict, not_directly_connected_dict, stp_domain):
    """
    Function is calculating non root paths
    """
    for local_name in directly_connected_dict:
        local = directly_connected_dict[local_name] # get a dictionary with a useful name to reflect local switches
        for neighbor_name in not_directly_connected_dict:
            neighbor = not_directly_connected_dict[neighbor_name] # get a dictionary with a useful name to reflect neighboring switches
            if neighbor_name in local:
                lowest_cost_key = 4200000000  # some arbitrary potentially unreachable cost (for a small network), at least for old 802.1D values
                if neighbor["lowest"] == local_name or stp_domain[neighbor["lowest"]]["lowest"] == local_name: # find neighbor amongst the local machines with root port facing local machine
                    for key in neighbor.keys():
                        if key.startswith('s') and stp_domain[key]["lowest"] != local_name and key != local_name:  # parse neighbor links for paths not leading back through local machine
                            lowest_cost_key = neighbor[key][1] if neighbor[key][1] < lowest_cost_key else lowest_cost_key   # find the lowest cost that we can use or set to maximal value
                    link_to_neighbor_cost = local[neighbor_name][0]
                    neighbor_selected_path_cost = lowest_cost_key + link_to_neighbor_cost
                    local[neighbor_name][1] = neighbor_selected_path_cost
                else:
                    for key in neighbor.keys():
                        if key.startswith('s') and stp_domain[key]["lowest"] != local_name and key != local_name: # parse neighbor links for paths not leading back through local machine
                            lowest_cost_key = neighbor[key][1] if neighbor[key][1] < lowest_cost_key else lowest_cost_key  # find the lowest cost that we can use
                        link_to_neighbor_cost =  local[neighbor_name][0]
                        neighbor_selected_path_cost = lowest_cost_key + link_to_neighbor_cost
                        local[neighbor_name][1] = neighbor_selected_path_cost
    return stp_domain

def setDesignatedPorts(root_bridge, stp_domain):
    for switch_name in stp_domain:
        if switch_name is not root_bridge:  # mainly look at non-root switches, neighbor of a root can not have a designated port facing the root bridge
            local = stp_domain[switch_name] # define a local switch dictionary for simplicity
            for neighbor_name in stp_domain:
                neighbor = stp_domain[neighbor_name] # define possible neighbors
                if neighbor_name in local and neighbor_name != root_bridge: # exclude root bridge from neighbors search
                    neighbor_lowest_root_cost = neighbor[neighbor["lowest"]][1]
                    local_lowest_root_cost = local[local["lowest"]][1]
                    if local[neighbor_name][2] == "RP":
                        neighbor[switch_name][2] = "DP"
                    elif neighbor_lowest_root_cost > local_lowest_root_cost:
                        local[neighbor_name][2] = "DP"
                    elif neighbor_lowest_root_cost == local_lowest_root_cost:
                        if local["bridgeID"] < neighbor["bridgeID"]:
                            local[neighbor_name][2] = "DP"
                            neighbor[switch_name][2] = "BP"
                        else:
                            local[neighbor_name][2] = "BP"
                            neighbor[switch_name][2] = "DP"
    # set all root bridges ports to be DP
    for item in stp_domain[root_bridge]:
        if item.startswith('s'):
            stp_domain[root_bridge][item][2] = "DP"
    return stp_domain

def setBlockingPorts(stp_domain):
    type(stp_domain)
    for switch_name in stp_domain:
        switch = stp_domain[switch_name]
        for key in switch.keys():
            if key.startswith('s'):
                if switch[key][2] == "none":
                    switch[key][2] == "BP"
    return stp_domain


def display(stp_domain):
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

root_bridge = setRootBridge(stp_domain)
stp_domain = setRoles(root_bridge, stp_domain)
directly_connected, not_directly_connected, stp_domain = defineSwitchType(stp_domain)
directly_connected_dict = setDictionaryOfSwitches(directly_connected)
directly_connected_dict = setRootPathCostForDirectlyConnected(directly_connected_dict, directly_connected, root_bridge)
# creating a dictionary of not directly connected devices
not_directly_connected_dict = setDictionaryOfSwitches(not_directly_connected)
setRootPathCostForNotDirectlyConnected(not_directly_connected_dict, directly_connected_dict, stp_domain)
verifyCostBetweenNotDirectlyConnectedDevices(not_directly_connected_dict) 
stp_domain = calculateCostsForNonRootPorts(directly_connected_dict, not_directly_connected_dict, stp_domain)
setDesignatedPorts(root_bridge, stp_domain)
stp_domain = setBlockingPorts(stp_domain)
display(stp_domain)
# Provide an output file
utils.provideOutfile(stp_domain, "test123")
