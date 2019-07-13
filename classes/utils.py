import sys
import signal
import json
import os

class STPUtils():
    def __init__(self):
        print("[+] The STPUtils successfully loaded")
        # start listening for a SIGINT
        signal.signal(signal.SIGINT, self.keyboardInterruptHandler)
    
    def getInfile(self, filename):
        """
        Function does return a stp_domain
        derived from a provided json file.
        The data is presented in a dictionary format
        """
        filename = self.verifyInput()
        try:
            os.path.dirname("STP-802.1D")   
            ifile = os.path.join("stp_domains", f"{filename}.json")
            with open(ifile, "r") as infile:
                print("\n[+] Input file was successfully loaded")
                return json.load(infile)
        except FileNotFoundError:
            try: 
                filename = filename.split('.')[1]
                if filename == 'json':
                    print("\n[-] Try providing a file name without a .json")
                    exit(1)
            except IndexError:
                 print( "\n[-] Provided file does not exist inside of stp_domains directory")
                 exit(2)

    def keyboardInterruptHandler(self, signal, frame):
        """
        This function gratiously handles a SIGINT (Ctrl-C)
        """
        print(f"\n[Ctrl-C] Shutting down ...")
        exit(0)
    
    def provideOutfile(self, results, ofileName):
        """
        Functions provides an output file in a json format
        based on a provided dictionary
        """
        #filename = f"{ofileName}.json"
        try:
            filename = os.path.join("results", f"{ofileName}.json")
            with open(filename, "w") as outfile:
                json.dump(results, outfile)
                print("[+] File was successfully created")
        except FileNotFoundError:
            print("[-] The directory you are trying to use does not exist")
    

    def verifyInput(self):
        """
        Functions ensure that user will provide some input
        and than returns this input.
        """
        filename= ''
        try: 
         filename =  sys.argv[1]
        except IndexError:
            while not filename:
                filename = input("\nPlease provide a name of the file: ")
        return filename

       
