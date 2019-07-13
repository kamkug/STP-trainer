#!/usr/bin/python3.6

from classes.utils import *
from classes.stpTrainer import STPTrainer
import sys

# verify that Ctrl-D has not been issued
try:
    utils = STPUtils()
    stp_domain = utils.getInfile(sys.argv)
    stpD = STPTrainer(stp_domain)
    # Provide an output file
    utils.provideOutfile(stpD.stp_domain, "test123")
except  EOFError:
    print("\n[Ctrl-D] Shutting down...")
    exit(1)
