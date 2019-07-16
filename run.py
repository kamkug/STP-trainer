#!/usr/bin/python3.6

from classes.utils import *
from classes.stpTrainer import STPTrainer
import sys
import logging
import os

logging.basicConfig(format='%(message)s', level=logging.INFO)

# verify that Ctrl-D has not been issued
try:
    #Namespace(infile='domain4', option='portID', outfile=None, port_name='s6', switch_name='s1', verbosity=4)
    utils = STPUtils()
    infile, option, outfile, port, switch_name, verbosity = utils.getCommandLineArguments()
    arguments = utils.getCommandLineArguments()
    stp_domain = utils.getInfile(infile, verbosity)
    stpDomain = STPTrainer(stp_domain, verbosity, option=option, switch_label=switch_name, port=port)
    #utils.provideOutfile(stpDomain.stp_domain, outfile, verbosity)
    #stpDomain.getSwitchPortPriorityAndID(arguments[2], arguments[3])
    #stpDomain.getSwitchLinkToNeighborCost(arguments[2], arguments[3])
    #port_roles = stpDomain.getSwitchPortRoles(stp_domain)
    #print(port_roles)
    #utils.provideOutfile(port_roles, outfile)
except  EOFError:
    logging.info("\n[Ctrl-D] Shutting down...")
    exit(1)

