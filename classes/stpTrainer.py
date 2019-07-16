#!/usr/bin/python3.6
import json
from classes.utils import STPUtils
import sys
import logging

logging.basicConfig(format='%(message)s', level=logging.INFO)


# define an example self.stp_domain to work with

# each link is described by the use of a following pattern :
# (switch that this link leads to): [(cost of the link), (root path cost), (port role), (port priority), (port id), (device name)]

# Ports Roles : 
# RP = root port
# DP = designated port
# BP = blocking port

#self.stp_domain = {}

### ------------------------------------CLASS-----------------------------------------
class STPTrainer():
    def __init__(self, stp_domain, verbosity, infile=None, outfile=None, switch_label=None, port=None, option=None):
        self.counter = 655362555 # setting the counter to the highest possible value
        self.infile = infile
        self.option = option
        self.outfile = outfile
        self.port = port
        self.stp_domain = stp_domain
        self.switch_label = switch_label
        self.utils = STPUtils()
        self.verbosity = verbosity
        # define who is a root bridge
        self.root_bridge = self.setRootBridge()
        # set general roles for the switches root|non-root
        self.setRoles()
        self.directly_connected, self.not_directly_connected = self.defineSwitchType()  
        self.directly_connected_dict = self.setRootPathCostForDirectlyConnected() 
        self.not_directly_connected_dict = self.setRootPathCostForNotDirectlyConnected()
        self.setRootPathCostForNotDirectlyConnected()
        self.verifyCostBetweenNotDirectlyConnectedDevices()
        self.calculateCostsForNonRootPorts()
        self.setRootPathCostForAll()  
        self.setDesignatedPorts()   
        self.setBlockingPorts()
        if self.verbosity >= 2:
            self.display()
        
        
        if self.option == "portID":
            self.getSwitchPortPriorityAndID(self.port, self.switch_label)
        elif self.option == "distToNeighbor":
            self.getSwitchLinkToNeighborCost(self.port, self.switch_label)
        elif self.option == "bridgeID":
            self.getSwitchBridgeID(self.switch_label)
        elif self.option == "fullOutput":
            if outfile == None:
                self.outfile = self.infile
            self.utils.provideOutfile(self.stp_domain, self.outfile, verbosity)
        elif self.option == "role":
            self.getSwitchRole(self.switch_label)
        elif self.option == "rootPort":
            self.getSwitchRootPort(switch_label)
        elif self.option == "smallerOutputFile":
            if outfile == None:
                self.outfile = self.infile
            self.port_roles = self.getSwitchPortRoles()
            self.utils.provideOutfile(self.port_roles, self.outfile, verbosity)
   


    def calculateCostsForNonRootPorts(self):
        """
        Function is calculating non root paths
        """
        for local_name in self.directly_connected_dict:
            local = self.directly_connected_dict[local_name] # get a dictionary with a useful name to reflect local switches
            for neighbor_name in self.not_directly_connected_dict:
                neighbor = self.not_directly_connected_dict[neighbor_name] # get a dictionary with a useful name to reflect neighboring switches
                if neighbor_name in local:
                    lowest_cost_key = 4200000000  # some arbitrary potentially unreachable cost (for a small network), at least for old 802.1D values
                    if neighbor["lowest"] == local_name or self.stp_domain[neighbor["lowest"]]["lowest"] == local_name: # find neighbor amongst the local machines with root port facing local machine
                        for key in neighbor.keys():
                            if key.startswith('s') and self.stp_domain[key]["lowest"] != local_name and key != local_name:  # parse neighbor links for paths not leading back through local machine
                                lowest_cost_key = neighbor[key][1] if neighbor[key][1] < lowest_cost_key else lowest_cost_key   # find the lowest cost that we can use or set to maximal value
                        link_to_neighbor_cost = local[neighbor_name][0]
                        neighbor_selected_path_cost = lowest_cost_key + link_to_neighbor_cost
                        local[neighbor_name][1] = neighbor_selected_path_cost
                    else:
                        for key in neighbor.keys():
                            if key.startswith('s') and self.stp_domain[key]["lowest"] != local_name and key != local_name: # parse neighbor links for paths not leading back through local machine
                                lowest_cost_key = neighbor[key][1] if neighbor[key][1] < lowest_cost_key else lowest_cost_key  # find the lowest cost that we can use
                            link_to_neighbor_cost =  local[neighbor_name][0]
                            neighbor_selected_path_cost = lowest_cost_key + link_to_neighbor_cost
                            local[neighbor_name][1] = neighbor_selected_path_cost



    def calculateCostThroughNeighbor(self, directly_connected_dict, neighbor_name, local):
        """
        Function calculates minimum cost through neighbor and compares
        that value with local lowest root path cost
        """
        lowest_current_local_root_path_cost = local[local["lowest"]][1]
        link_to_neighbor_cost = local[neighbor_name][0] 
        neighbor_root_path_cost = directly_connected_dict[neighbor_name][self.root_bridge][1]
        local[neighbor_name][1] = link_to_neighbor_cost + neighbor_root_path_cost
        root_path_cost_through_neighbor = local[neighbor_name][1]
        return root_path_cost_through_neighbor < lowest_current_local_root_path_cost
     

    def defineSwitchType(self):
        """
        Function updates the lowest cost for switches that are directly connected to the root bridge
         and figures out who is/isn't directly connected
        """
        #create two holders
        directly_connected = []
        not_directly_connected = []
        for switch in self.stp_domain:
            if self.root_bridge in self.stp_domain[switch]:
                self.stp_domain[switch][self.root_bridge][1] = self.stp_domain[switch][self.root_bridge][0]
                self.stp_domain[switch]["lowest"] = self.root_bridge
                self.stp_domain[switch][self.root_bridge][2] = "RP"
                directly_connected.append(switch)
            elif switch != self.root_bridge:
                not_directly_connected.append(switch)  
        return directly_connected, not_directly_connected
 

    def display(self):
        """
        Function displays the results in a human readable format
        """
        for switch_name in self.stp_domain:
            designated_ports = []
            blocking_ports = []
            switch = self.stp_domain[switch_name]
            logging.info(f"The {switch['name']}  info:")
            logging.info(f"Bridge role: {switch['role']}")
            logging.info(f"Bridge ID:  {switch['bridgeID']}")
            if switch["role"] != "root":   # no need to look for a root port on a root bridge
                logging.info(f"Root port: {switch[switch['lowest']][4]}")
            for key in switch.keys():   # make sure that there are any designated ports
                if key.startswith('s') and switch[key][2] == "DP":
                    designated_ports.append(str(switch[key][4]))
            logging.info(f"Designated ports: {', '.join(designated_ports) if designated_ports else 'None'}")
            for key in switch.keys():   # make sure that there are any blocking ports
                if key.startswith('s') and switch[key][2] == "BP":
                    blocking_ports.append(str(switch[key][4]))
            logging.info(f"Blocking ports: {', '.join(blocking_ports) if blocking_ports else 'None'}")
            logging.info(40 * '-')

    def setBlockingPorts(self):
        """
        Function ensure that all remaining ("none") ports are set to be BPs
        """
        for switch_name in self.stp_domain:
            switch = self.stp_domain[switch_name]
            for key in switch.keys():
                if key.startswith('s'):
                    if switch[key][2] == 'none':
                        switch[key][2] = "BP"

    def setDesignatedPorts(self):
        """
        Function establishes DPs for all of the switches from the stp domain
        then subsequently ensures that all root bridge ports are set to be DPs as well
        """
        for switch_name in self.stp_domain:
            if switch_name is not self.root_bridge:  # mainly look at non-root switches, neighbor of a root can not have a designated port facing the root bridge
                local = self.stp_domain[switch_name] # define a local switch dictionary for simplicity
                for neighbor_name in self.stp_domain:
                    neighbor = self.stp_domain[neighbor_name] # define possible neighbors
                    if neighbor_name in local and neighbor_name != self.root_bridge: # exclude root bridge from neighbors search
                        neighbor_lowest_root_cost = neighbor[neighbor["lowest"]][1]# + neighbor[switch_name][0]
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
        for item in self.stp_domain[self.root_bridge]:
            if item.startswith('s'):
                self.stp_domain[self.root_bridge][item][2] = "DP"
    
    def setDictionaryOfSwitches(self, switches_list):
        """
        Function creates a dictionary out of a list
        """
        return  { switches_list[index]:self.stp_domain[switches_list[index]] for index in range (len(switches_list))}


    def setNewRootPort(self, local, neighbor_name, reset=True):
        """
        Function deals with assigning a RP role after resetting of
        previous lowest port role to none
        """
        if reset:
            local[local["lowest"]][2] = "none"    # reset the root port if necessary
        local["lowest"] = neighbor_name           # name the lowest switch appropriately
        local[local["lowest"]][2] = "RP"          # define a new root port

    def setRootBridge(self):
        """
        Functions finds the root bridge amongst all switches in the domain
        """
        #set max possible bridge ID
        counter = 65536255
        self.root_bridge = ''
        for switchName in self.stp_domain:
            switch = self.stp_domain[switchName]
            if switch["bridgeID"] < counter:
                self.root_bridge = switchName
                counter = self.stp_domain[switchName]["bridgeID"]
        return self.root_bridge
    
    def setRoles(self):
        """
        Function sets the roles for all bridges (root|non-root)
        """
        for switch_name in self.stp_domain:
            switch = self.stp_domain[switch_name]
            switch["role"] = "root" if switch_name == self.root_bridge else "non-root"
            if switch["role"] == "root":
                for key in switch.keys():
                      if key.startswith('s'):
                        switch[key][2] = "DP"
        #return self.stp_domain

    def setRootBridge(self):
        """
        Functions finds the root bridge amongst all switches in the domain
        """
        #set max possible bridge ID
        counter = 65536255
        self.root_bridge = ''
        for switchName in self.stp_domain:
            switch = self.stp_domain[switchName]
            if switch["bridgeID"] < counter:
                self.root_bridge = switchName
                counter = self.stp_domain[switchName]["bridgeID"]
        return self.root_bridge
    
    def setRootPathCostForDirectlyConnected(self):
        """
        Function identifies root ports for directly connected switches
        """
        directly_connected_dict = self.setDictionaryOfSwitches(self.directly_connected)

        for local_name in directly_connected_dict:
            for neighbor_name in self.directly_connected:
                local = directly_connected_dict[local_name] 
                if neighbor_name in local:
                    result = self.calculateCostThroughNeighbor(directly_connected_dict, neighbor_name, local)
                    if result:
                        local[self.root_bridge][2] = "none"
                        local["lowest"] = neighbor_name
                        local[neighbor_name][2] = "RP"
        return directly_connected_dict
    
    def setRootPathCostForAll(self):        
        """
        Function identifies root ports for all of the remaining switches
        """
        for switch_name in self.stp_domain:
            switch = self.stp_domain[switch_name]
            if switch_name != self.root_bridge:
                lowest_root_cost = switch[switch["lowest"]][1]
                current_best_port = switch[switch["lowest"]]
                for key in switch.keys():
                    if key != self.root_bridge and key.startswith("s"):
                        root_cost_through_neighbor = switch[key][1]
                        new_best_port  = switch[key]
                        if root_cost_through_neighbor < lowest_root_cost:
                            #print(best_current_port)
                            current_best_port[2] = 'none'
                            new_best_port[2] = 'RP'

    def setRootPathCostForNotDirectlyConnected(self):
        """
        Function is setting the remaining root ports on both type of switches (connected|not connected)
        """
        not_directly_connected_dict = self.setDictionaryOfSwitches(self.not_directly_connected)
        
        for local_name in not_directly_connected_dict:
            local = not_directly_connected_dict[local_name]
            for neighbor_name in self.directly_connected_dict:
                neighbor = self.directly_connected_dict[neighbor_name]
                if neighbor_name in local:
                    # local to neighbor cost + neighbor to root bridge cost
                    link_to_neighbor_cost = local[neighbor_name][0]
                    neighbors_root_path_cost = neighbor[neighbor["lowest"]][1]
                    local[neighbor_name][1] = link_to_neighbor_cost + neighbors_root_path_cost
                    if local["lowest"] == '':  # add initial root port if none exist
                        self.setNewRootPort(local, neighbor_name, False)
                    elif local[local["lowest"]][1] == "RP":                                                         # in case of a cost tie
                        if self.stp_domain[local["lowest"]]["bridgeID"] > self.stp_domain[neighbor_name]["bridgeID"]:         # look at the bridge ID of neighboring switches, the lower one wins
                            self.setNewRootPort(local, neighbor_name)    
                    elif local[local["lowest"]][1] == "RP" or local[local["lowest"]][1] > local[neighbor_name][1] \
                         or local[local["lowest"]][1] < neighbor[neighbor["lowest"]][1]:    # if appropriate port is already set to the lowest or if a local lowest is smaller than the neighbors lowest
                        self.setNewRootPort(local, neighbor_name)
        return not_directly_connected_dict#, self.stp_domain
     
    def verifyCostBetweenNotDirectlyConnectedDevices(self):
        """
        Function defines root path costs between not directly connected devices
        """
        for local_name in self.not_directly_connected_dict:
            local = self.not_directly_connected_dict[local_name]  # get a local machine information
            for neighbor_name in self.not_directly_connected_dict:
                neighbor = self.not_directly_connected_dict[neighbor_name] # get a neighboring machine name
                if neighbor_name in local:
                    link_to_neighbor_cost = local[neighbor_name][0]
                    neighbor_root_path_cost = neighbor[neighbor["lowest"]][1]
                    local[neighbor_name][1] = link_to_neighbor_cost + neighbor_root_path_cost
                    if local[local["lowest"]][1] == local[neighbor_name][1]:                                    # in case of a cost tie
                        if self.stp_domain[local["lowest"]]["bridgeID"] > self.stp_domain[neighbor_name]["bridgeID"]:     # look at the bidge ID of neighboring switches, the lower one wins
                            self.setNewRootPort(local, neighbor_name)                                                # re-assign appropriate roles (if necessary)
                    elif local[local["lowest"]][1] > local[neighbor_name][1]:    # if the local lowest distance is bigger than the Root path cost for the neighboring switch
                        self.setNewRootPort(local, neighbor_name)                     # reset the root port and subsequently define a correct one   return not_directly_connected_dict
    

               
    # Getters
    
    def getSwitchBridgeID(self,  switch_name):
        """
        Function returns a bridge ID of the provided switch
        """
        try:
            switch_bridge_ID =  self.stp_domain[switch_name]["bridgeID"]
            if self.verbosity == 1:
                logging.info(f"[info] Switch {switch_name}'s bridge ID is: {switch_bridge_ID}")
            else:
                return switch_bridge_ID
        except KeyError:
            logging.info("[-] This switch is not a part of provided stp domain")

 

    def getSwitchLinkToNeighborCost(self,  neighbor_name, local_name):
        """
        Function returns a cost of the link along with the name of the neighboring switch
        
        """
        try:
            local_to_neighbor_link_cost = self.stp_domain[local_name][neighbor_name][0]
            if self.verbosity == 1:
                logging.info(f"[info] Switch {local_name}'s link cost to {neighbor_name} equals: {local_to_neighbor_link_cost}")
            else:
                return (local_to_neighbor_link_cost, neighbor_name)
        except KeyError:

            right_switch = True
            if self.verbosity == 1:
                if  local_name not in self.stp_domain :
                    logging.info("[-] This switch is not a part of provided stp domain")
                    right_switch = False
                if right_switch:
                    if neighbor_name not in self.stp_domain[local_name] and neighbor_name == local_name:
                        logging.info(f"[-] This switch does not have a loopback interface")
                        exit(2)
                    elif neighbor_name not in self.stp_domain[local_name]:
                        logging.info(f"[-] This switch does not connect to {neighbor_name}")
#            logging.info("[-] This switch is not a part of provided stp domain")


    def getSwitchPortPriorityAndID(self, interface_name, local_name):
        """
        Function returns a Port Priority and Port ID for a given interface
        on a provided switch
        """
        try:
                interface = self.stp_domain[local_name][interface_name] 
                port_priority = interface[3]
                port_ID = interface[4]
                if self.verbosity == 1:
                    logging.info(f"[info] Port {local_name}'s priority is: {port_priority}")
                    logging.info(f"[info] Port {local_name}'s ID is: {port_ID}")
                else :
                    return ( port_priority, port_ID, interface_name )
        except KeyError:
            right_switch = True
            if self.verbosity == 1:
                if  local_name not in self.stp_domain :
                    logging.info("[-] This switch is not a part of provided stp domain")
                    right_switch = False

                if right_switch:
                    if interface_name not in self.stp_domain[local_name] and interface_name == local_name:
                        logging.info(f"[-] This switch does not have a loopback interface")
                        exit(2)
                    elif interface_name not in self.stp_domain[local_name]:
                        logging.info(f"[-] This switch does not connect to {interface_name}")
        
    def getSwitchPortRoles(self):

        """
        Function returns a list of lists for:
        blocking ports, designated ports and root ports
        in a following tuple format:
        ( port_id_of_a_root, switch_this_port_belongs_to)
        """
        bp = []
        dp = []
        rp = []
        port_roles =  {
                        "Blocking": bp,
                        "Designated": dp,
                        "Root": rp
                      }

        for switch_name in self.stp_domain:
            switch = self.stp_domain[switch_name]
            for key in switch.keys():
                if key.startswith('s'):
                    switch_in_question = switch[key]
                    if switch[key][2] == "BP":
                        bp.append([switch_in_question[4], switch_name ])
                    elif switch[key][2] == "DP":
                        dp.append([switch_in_question[4], switch_name])
                    else :
                        rp.append([switch_in_question[4], switch_name])
        return port_roles

    def getSwitchRole(self, switch_name):
        """
        Function returns a general switch role either root or non-root
        """
        try:
            switch_role = self.stp_domain[switch_name]["role"]
            if self.verbosity == 1:
                logging.info(f"[info] Switch {switch_name } is a {switch_role}")
            
            return switch_role
        except KeyError:
            logging.info("[-] This switch is not a part of provided stp domain")

    def getSwitchRootPort(self, switch_name):
        """
        Function if successfull returns a tuple in the form:
        (next_hop_device_to_the_root_port, egress_port_ID)
        else returns None
        """
        try:
            switch_in_question = self.stp_domain[switch_name]
            if switch_in_question["role"] != "root":
                best_next_hop_switch = switch_in_question["lowest"]
                root_port_ID = switch_in_question[best_next_hop_switch][4]
                cost = switch_in_question[best_next_hop_switch][1]
                
                if self.verbosity == 1:
                    logging.info(f"[info] Switch {switch_name}'s link to {best_next_hop_switch} is the best root path")
                    logging.info(f"[info] Switch {switch_name}'s best root path cost equals: {cost}")
                return ( root_port_ID, best_next_hop_switch )
            else:
                logging.info("[-] This is a root bridge")

        except KeyError:
            logging.info("[-] This switch is not a part of provided stp domain")


            
"""
Example of a template for creation of a switch with ports to other devices
"s1": {
        "bridgeID": 40961,
        "s2" : [64, 0, "none", 128, 3],
        "s3" : [4, 0, "none", 128, 1],
        "lowest" : "",
        "name": "s1",
        "role": "none"

    },


# verify that Ctrl-D has not been issued
try:
    utils = STPUtils()
    self.stp_domain = utils.getInfile(sys.argv)
    stpD = STPTrainer(self.stp_domain)
    # Provide an output file
    utils.provideOutfile(stpD.self.stp_domain, "test123")
except  EOFError:
    logging.info("\n[Ctrl-D] Shutting down...")
    exit(1)
"""

      

