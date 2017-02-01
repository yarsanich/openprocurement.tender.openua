# -*- coding: utf-8 -*-
import unittest
from openprocurement.api.tests.base import (BaseWebTest,
                                            test_organization,
                                            test_lots,
                                            snitch)
from openprocurement.tender.openua.tests.base import BaseTenderUAWebTest
from openprocurement.tender.openua.tests.base import test_tender_data
from openprocurement.api.tests.tender import BaseTenderResourceTest
from openprocurement.tender.openua.tests.tender_tests_blanks import (tender_features,
                                                                     create_tender_draft,
                                                                     patch_tender_local,
                                                                     simple_add_tender,
                                                                     create_tender,
                                                                     patch_tender,
                                                                     invalid_tender_conditions,
                                                                     invalid_bid_tender_features,
                                                                     invalid_bid_tender_lot,
                                                                     one_valid_bid_tender_ua,
                                                                     invalid1_and_1draft_bids_tender,
                                                                     activate_bid_after_adding_lot,
                                                                     first_bid_tender,
                                                                     create_tender_invalid,
                                                                     create_tender_generated,
                                                                     patch_draft_invalid_json)


class TenderUATest(BaseWebTest):
    test_tender_data = test_tender_data
    test_simple_add_tender = snitch(simple_add_tender)


class BaseTenderOpenUAResourceTest(object):
    test_tender_features = snitch(tender_features)
    test_create_tender_draft = snitch(create_tender_draft)
    test_patch_tender_local = snitch(patch_tender_local)


class BaseTenderUAResourceTest(BaseTenderOpenUAResourceTest,
                               BaseTenderResourceTest):
    test_create_tender_invalid = snitch(create_tender_invalid)
    test_create_tender_generated = snitch(create_tender_generated)
    test_patch_draft_invalid_json = snitch(patch_draft_invalid_json)
    test_create_tender = snitch(create_tender)
    test_patch_tender = snitch(patch_tender)


class TenderUAResourceTest(BaseTenderUAWebTest,
                           BaseTenderUAResourceTest):
    test_tender_data = test_tender_data


class BaseTenderUAProcessTest(object):
    test_tender_data = test_tender_data
    test_invalid_tender_conditions = snitch(invalid_tender_conditions)
    test_invalid_bid_tender_features = snitch(invalid_bid_tender_features)
    test_invalid_bid_tender_lot = snitch(invalid_bid_tender_lot)
    test_one_valid_bid_tender_ua = snitch(one_valid_bid_tender_ua)
    test_invalid1_and_1draft_bids_tender = snitch(invalid1_and_1draft_bids_tender)
    test_activate_bid_after_adding_lot = snitch(activate_bid_after_adding_lot)
    test_first_bid_tender = snitch(first_bid_tender)


class TenderUAProcessTest(BaseTenderUAProcessTest,
                          BaseTenderUAWebTest):
    pass


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TenderUAProcessTest))
    suite.addTest(unittest.makeSuite(TenderUAResourceTest))
    suite.addTest(unittest.makeSuite(TenderUATest))
    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='suite')
