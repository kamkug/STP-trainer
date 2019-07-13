#!/usr/bin/python3.6

from classes.utils import *
from classes.stpTrainer import STPTrainer
import sys
import logging

logging.basicConfig(format='%(message)s', level=logging.INFO)

# verify that Ctrl-D has not been issued
try:
    utils = STPUtils()
    infile, outfile = utils.verifyInput()
    stp_domain = utils.getInfile(infile)
    stpDomain = STPTrainer(stp_domain)
    #stpDomain.getSwitchPortRoles(stp_domain))
    #stpDomain.getSwitchRootPort(stp_domain, 's2', human_readable=True))
    #stpDomain.getSwitchBridgeID(stp_domain, 's2', human_readable=True))
    #stpDomain.getSwitchPortPriorityAndID(stp_domain, 's2', 's3', human_readable=True))
    #stpDomain.getSwitchLinkToNeighborCost(stp_domain, 's2', 's3', human_readable=True))
    #stpDomain.getSwitchRole(stp_domain, 's3', human_readable=True)
    utils.provideOutfile(stpDomain.stp_domain, outfile)
except  EOFError:
    logging.info("\n[Ctrl-D] Shutting down...")
    exit(1)

