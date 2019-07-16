import sys
import signal
import json
import argparse
import os
import logging

logging.basicConfig(format='%(message)s', level=logging.INFO)

class STPUtils():
    def __init__(self):
        #logging.info("[+] The STPUtils successfully loaded")
        # start listening for a SIGINT
        signal.signal(signal.SIGINT, self.keyboardInterruptHandler)
    
    def getInfile(self, filename, verbosity):
        """
        Function does return a stp_domain
        derived from a provided json file.
        The data is presented in a dictionary format
        """
        try:
            ifile = os.path.join("stp_domains", f"{filename}.json")
            with open(ifile, "r") as infile:
                if verbosity!=1 >= 0:
                    logging.info("\n[+] Input file was successfully loaded")
                return json.load(infile)
        except FileNotFoundError:
            try: 
                filename = filename.split('.')[1]
                if filename == 'json':
                    logging.info("\n[-] Try providing a file name without a .json")
                    exit(1)
            except IndexError:
                 logging.info( "\n[-] Provided file does not exist inside of stp_domains directory")
                 exit(2)

    def keyboardInterruptHandler(self, signal, frame):
        """
        This function gratiously handles a SIGINT (Ctrl-C)
        """
        logging.warning(f"\n[Ctrl-C] Shutting down ...")
        exit(0)
    
    def provideOutfile(self, results, ofileName, verbosity):
        """
        Functions provides an output file in a json format
        based on a provided dictionary
        """
        try:

            if not ofileName:
                ofileName = "dummy"
            filename = os.path.join("results", f"{ofileName}.json")
            with open(filename, "w") as outfile:
                json.dump(results, outfile)
                if verbosity != 1 >= 0:
                    logging.info("[+] File was successfully created")
        except FileNotFoundError:
            logging.info("[-] The directory you are trying to use does not exist")
    
    def getCommandLineArguments(self):
        """
        Function will get command line arguments  and if they are not provides 
        it will alert the user
        """
        parser = argparse.ArgumentParser()
        parser.add_argument("-i", "--infile", dest="infile", type=str, required=True, help="the input file")
        parser.add_argument("-n", "--switch_name", dest="switch_name", type=str, help="switch name to be used")
        parser.add_argument("-o", "--outfile", dest="outfile", type=str, help="the output file")
        parser.add_argument("-g", "--get-me", dest="option", type=str, help="desired information query",\
                            choices= [
                                        "bridgeID",
                                        "distToNeighbor",
                                        "portID"
                                     ]
                            )
        parser.add_argument("-p", "--port-name", type=str, dest="port_name", help="name of the port")
        parser.add_argument("-v", "--verbosity", action="count", dest="verbosity", default=0)
        args = parser.parse_args()
        
        if args.infile != None: #or args.outfile != None:
            if args.verbosity >= 4:
                print(args)
            return args.infile, args.option, args.outfile, args.port_name, args.switch_name,args.verbosity
        else:
            return self.verifyInput(args.verbosity)
            
    def verifyInput(self, verbosity):
        """
        Functions ensure that user will provide some input
        and than returns this input.
        """
        infile = ''
        outfile = ''
        try: 
            infile =  sys.argv[1]
            outfile = sys.argv[2]
        except IndexError:
            if not infile:
                infile = input("\nPlease provide a name of the input file: ")
            if not outfile:
                outfile = input("\nPlease provide a name of the output file: ")
            
            if infile == '' and outfile == '':
                logging.info("\n[-] usage: ./run.py [infile] [outfile]")
                exit(2)
        return infile, outfile, verbosity

       
