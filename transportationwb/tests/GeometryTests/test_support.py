import sys

from Geometry import Support
import unittest

class Test_Support(unittest.TestCase):

    def test_vector_from_angle(self):
        
        self.assertIsNone(
            Support.vector_from_angle('1fdsa.0'), 
            'Supprt.vector_from_angle() fails non-float test'
        )