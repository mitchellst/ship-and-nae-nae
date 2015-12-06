from django.test import TestCase
from .uspsinterface import *

# Create your tests here.
class TestRateReqest(TestCase):

    def test_there_are_tests(self):
        self.fail('write some tests.')

class TestLabelMaker(TestCase):

        def test_pound_bug(self):
            fromDict = {'name': 'Mitchell', 'firm': '', 'address2': r'111 Preston Ave', 'address1': '',
                'city': 'Lewiston', 'state': 'ID', 'zip': '83501', 'zip4': ''}
            toDict = {'name': 'Stoutin', 'firm': '', 'address2': r'11160 Jollyvill Rd', 'address1': 'APT #1000',
                'city': 'Austin', 'state': 'TX', 'zip': '78759', 'zip4': ''}
            label_request = build_label_request_xml(fromDict, toDict, 44)
            self.assertNotIn('#', label_request)
