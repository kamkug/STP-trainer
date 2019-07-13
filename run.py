#!/usr/bin/python3.6

from classes.utils import *
from classes.stpTrainer import STPTrainer
import sys

# verify that Ctrl-D has not been issued
try:
    utils = STPUtils()
    stp_domain = utils.getInfile(sys.argv)
    stpDomain = STPTrainer(stp_domain)
    print(stpDomain.getSwitchPortRoles(stp_domain))
    utils.provideOutfile(stpDomain.stp_domain, "test123")
except  EOFError:
    print("\n[Ctrl-D] Shutting down...")
    exit(1)

