# -*- coding: utf-8 -*-
import unittest
from sht21pi import *

class BasicTestSuite(unittest.TestCase):
    """Basic test cases."""

    def test_sht21pi(self):
       sht21pi.StorageHumidityMonitor(1).run()

if __name__ == '__main__':
    unittest.main()
