import sys
import signal
import json
import os
import logging

logging.basicConfig(format='%(message)s', level=logging.INFO)

class STPUtils():
    def __init__(self):
        logging.info("[+] The STPUtils successfully loaded")
        # start listening for a SIGINT
        signal.signal(signal.SIGINT, self.keyboardInterruptHandler)
    
    def getInfile(self, filename):
        """
        Function does return a stp_domain
        derived from a provided json file.
        The data is presented in a dictionary format
        """
        #filename = self.verifyInput()
        try:
            ifile = os.path.join("stp_domains", f"{filename}.json")
            with open(ifile, "r") as infile:
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
    
    def provideOutfile(self, results, ofileName):
        """
        Functions provides an output file in a json format
        based on a provided dictionary
        """
        try:
            filename = os.path.join("results", f"{ofileName}.json")
            with open(filename, "w") as outfile:
                json.dump(results, outfile)
                logging.info("[+] File was successfully created")
        except FileNotFoundError:
            logging.info("[-] The directory you are trying to use does not exist")
    

    def verifyInput(self):
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
            logging.info("[-] usage: ./run.py [infile] [outfile]")
            if not infile:
                infile = input("\nPlease provide a name of the input file: ")
            if not outfile:
                outfile = input("\nPlease provide a name of the output file: ")
        return infile, outfile

       
