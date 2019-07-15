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
         


"""
        test_against_those_cases =  [
                                    
                        [
                            
                            [ (5, 's3'), (4, 's4'), (6, 's5'), (7, 's5'), (8, 's6') ],   # Blocking ports
                            [ (1, 's1'), (5, 's1'), (2, 's1'), (3, 's2'), (4, 's2'), (6, 's3'), (8, 's3'), (7, 's4'), (9, 's4'), (10, 's6')  ], # Designated ports            
                            [ (1, 's2'), (3, 's3'), (2, 's4'), (10, 's5'), (9, 's6')  ]                                                          # Root ports

                        ],
                        
                        [
                            
                            [ (7, 's1'), (2, 's2'), (9, 's3'), (6, 's4') ],
                            [ (7, 's3'), (2, 's3'), (1, 's4'), (8, 's4'), (3, 's4'), (4, 's5'), (5, 's5'), (9, 's6'), (6, 's6') ],
                            [ (1, 's1'), (8, 's2'), (3, 's3'), (4, 's4'), (5, 's6') ]
                        
                        ],
                        
                        [
                            
                            [ (2, 's3') ],
                            [ (3, 's1'), (4, 's2'), (1, 's4'), (2, 's4') ],                   
                            [ (4, 's1'), (1, 's2'), (3, 's3') ]

                        ],
                        
                        [
                            
                            [ (4, 's2'), (2, 's3') ],
                            [ (4, 's1'), (3, 's1'), (5, 's4'), (1, 's4'), (2, 's4') ],
                            [ (5, 's1'), (1, 's2'), (3, 's3') ]

                        ],
                        
                        [
                            
                            [ (3, 's2')  ],
                            [ (3, 's1'), (1, 's1'), (2, 's3') ],
                            [ (2, 's2'), (1, 's3') ]

                        ]
                    
                    ]


        #counter = 0
        for stp_domain in self.stp_domains:
            STPTrainerResult = self.stp_domains[stp_domain]
            self.assertEqual(STPTrainerResult, test_against_those_cases)
            #counter += 1
"""
                                








#test_suite = STPTrainerTest().setUp()
#print(test_suite)
#STPTrainerTest().testSTPTrainer(test_suite)


