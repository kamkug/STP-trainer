#!/usr/bin/python3.6

#import unittest
"""
Author: Kamil Kugler
File: stpTrainer_test.py
Purpose: Unit tests for STPTrainer class
"""
import json
import os
from unittest import TestCase
from classes.stpTrainer import STPTrainer
from classes.utils import STPUtils

class STPTrainerTest(TestCase):
    """
    Class defines a test case suite for the STPTrainer class
    """
    
    def setUp(self):
        """
        Function creates a dictionary of results for STPTrainer runs on domains collected
        from stp_domains directory. Subsequently the result is given in the following format:
        { 
            "domain_name" : [
                                [ (blocking_port_name, blocking_port_id), ... ],
                                [ (designated_port_name, designated_port_id ), ... ], 
                                [ (root_port_name), root_port_id)  ]
                            ],
          
            "domain_name2: : ...
        
        }
        """
        # collect, sort and remove extensions from filenames inside of stp_domains directory
        domains = [ domain.split('.')[0] for domain in sorted(os.listdir('stp_domains')) if domain.startswith('d') ]
        self.stp_domains = {}
        #print(domains)
        for domain in domains: #domains:
            stp_domain = STPUtils.getInfile(self, domain, True)
            self.stp_domains[domain] = STPTrainer(stp_domain, False).port_roles
        
    def testSTPTrainer(self):
        """
        Function is comparing the results of STPTrainer class against the actual correct cases results
        """
        show = {}
        files = [ domain for domain in os.listdir('stp_domains/test')  ]
        files = sorted(files)
        length = len(files)
        
        # iterate over each element and compare the results
        for i in range(0,length):
            with open('stp_domains/test/'+files[i], 'r') as domain:
                show = json.load(domain)
            self.assertEqual(self.stp_domains["domain"+str(i)], show)
         
