#!/usr/bin/python3.6

import unittest
from unittests.stpTrainer_test import STPTrainerTest


def main():
    """
    Test execution will run here
    """
    # create a loader to load the test cases
    test_loader = unittest.TestLoader() 

    # name a test suite
    test_suite = test_loader.loadTestsFromTestCase(STPTrainerTest)

    # get the runner to execute the test with an appropriate level of verbosity
    test_runner = unittest.TextTestRunner(verbosity=2)

    # perform an actual test
    test_runner.run(test_suite)

if __name__ == "__main__":
    main()
