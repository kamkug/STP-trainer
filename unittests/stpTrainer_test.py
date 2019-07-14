#!/usr/bin/python3.6

#import unittest
"""
Author: Kamil Kugler
File: stpTrainer_test.py
Purpose: Unit tests for STPTrainer class
"""


from unittest import TestCase
from classes.stpTrainer import STPTrainer
from classes.utils import STPUtils
#print(files)
class STPTrainerTest(TestCase):
    """
    Class defines a test case suite for the STPTrainer class
    """
    
    def setUp(self):
        """
        Function creates a dictionary of results for STPTrainer runs on given domain names.
        The result is given in the following format:
        { 
            "domain_name" : [
                                [ (blocking_port_name, blocking_port_id), ... ],
                                [ (designated_port_name, designated_port_id ), ... ], 
                                [ (root_port_name), root_port_id)  ]
                            ],
          
            "domain_name2: : ...
        
        }
        """

        domains = ["domain0", "domain1", "domain2", "domain3", "domain4"]
        self.stp_domains = {}
        for domain in domains:
            stp_domain = STPUtils.getInfile(self, domain, True)
            self.stp_domains[domain] = STPTrainer(stp_domain, True).port_roles
        #return self.stp_domains     

    def testSTPTrainer(self):
        """
        Function is comparing the results of STPTrainer class against the actual correct cases results
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
                            
                            [ (4, 's1') ],
                            [ (4, 's2'), (4, 's3'), (1, 's4'), (2, 's4') ],
                            [ (3, 's1'), (1, 's2'), (2, 's3') ]

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

        counter = 0
        for stp_domain in self.stp_domains:
            STPTrainerResult = self.stp_domains[stp_domain]
            self.assertEqual(STPTrainerResult, test_against_those_cases[counter])
            counter += 1
                                








#test_suite = STPTrainerTest().setUp()
#print(test_suite)
#STPTrainerTest().testSTPTrainer(test_suite)


