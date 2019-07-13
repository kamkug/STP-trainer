#!/usr/bin/python3.6

from classes.utils import *
from classes.stpTrainer import STPTrainer
import sys

# verify that Ctrl-D has not been issued
try:
    utils = STPUtils()
    infile, outfile = utils.verifyInput()
    stp_domain = utils.getInfile(infile)
    stpDomain = STPTrainer(stp_domain)
    #print(stpDomain.getSwitchPortRoles(stp_domain))
    #print(stpDomain.getSwitchRootPort(stp_domain, 's2', human_readable=False))
    #print(stpDomain.getSwitchBridgeID(stp_domain, 's2', human_readable=False))
    #print(stpDomain.getSwitchPortPriorityAndID(stp_domain, 's2', 's3', human_readable=False))
    #print(stpDomain.getSwitchLinkToNeighborCost(stp_domain, 's2', 's3', human_readable=False))
    utils.provideOutfile(stpDomain.stp_domain, outfile)
except  EOFError:
    print("\n[Ctrl-D] Shutting down...")
    exit(1)

