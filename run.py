#!/usr/bin/python3.6

from classes.utils import *
from classes.stpTrainer import STPTrainer
import sys
import logging
import os

logging.basicConfig(format='%(message)s', level=logging.INFO)

# verify that Ctrl-D has not been issued
try:
    utils = STPUtils()
    infile, outfile, verbosity = utils.getCommandLineArguments()
    stp_domain = utils.getInfile(infile)
    stpDomain = STPTrainer(stp_domain, verbosity)
    utils.provideOutfile(stpDomain.stp_domain, outfile)
except  EOFError:
    logging.info("\n[Ctrl-D] Shutting down...")
    exit(1)

