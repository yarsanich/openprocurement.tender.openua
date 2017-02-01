# -*- coding: utf-8 -*-
import unittest
from openprocurement.api.tests.lot import BaseTenderLotFeatureResourceTest
from openprocurement.api.tests.base import test_lots, snitch
from openprocurement.api.tests.lot_tests_blanks import (create_tender_lot_invalid,
                                                        delete_tender_lot,
                                                        tender_lot_guarantee)
from openprocurement.tender.openua.tests.base import (BaseTenderUAContentWebTest,
                                                      test_tender_data,
                                                      test_bids)
from openprocurement.tender.openua.tests.lot_test_blanks import (get_tender_lot,
                                                                 get_tender_lots,
                                                                 patch_tender_currency,
                                                                 patch_tender_vat,
                                                                 create_tender_lot,
                                                                 patch_tender_lot,
                                                                 question_blocking,
                                                                 claim_blocking,
                                                                 next_check_value_with_unanswered_question,
                                                                 next_check_value_with_unanswered_claim,
                                                                 patch_tender_bidder,
                                                                 create_tender_bidder_invalid,
                                                                 feature_create_tender_bidder_invalid,
                                                                 feature_create_tender_bidder,
                                                                 lot1_0bid,
                                                                 lot1_1bid,
                                                                 lot1_1bid_patch,
                                                                 lot1_2bid,
                                                                 lot1_3bid_1un,
                                                                 lot2_0bid,
                                                                 lot2_2can,
                                                                 lot2_1bid_0com_1can,
                                                                 lot2_2bid_1lot_del,
                                                                 lot2_1bid_2com_1win,
                                                                 lot2_1bid_0com_0win,
                                                                 lot2_1bid_1com_1win,
                                                                 lot2_2bid_2com_2win)


class BaseTenderLotResourceTest(object):
    test_create_tender_lot_invalid = snitch(create_tender_lot_invalid)
    test_delete_tender_lot = snitch(delete_tender_lot)
    test_tender_lot_guarantee = snitch(tender_lot_guarantee)
    test_get_tender_lot = snitch(get_tender_lot)
    test_get_tender_lots = snitch(get_tender_lots)
    test_patch_tender_currency = snitch(patch_tender_currency)
    test_patch_tender_vat = snitch(patch_tender_vat)
    test_create_tender_lot = snitch(create_tender_lot)
    test_patch_tender_lot = snitch(patch_tender_lot)


class TenderLotResourceTest(BaseTenderUAContentWebTest,
                            BaseTenderLotResourceTest):
    status = 'active.auction'
    test_tender_data = test_tender_data


class BaseTenderLotEdgeCasesTest(object):
    test_question_blocking = snitch(question_blocking)
    test_claim_blocking = snitch(claim_blocking)
    test_next_check_value_with_unanswered_question = snitch(next_check_value_with_unanswered_question)
    test_next_check_value_with_unanswered_claim = snitch(next_check_value_with_unanswered_claim)


class TenderLotEdgeCasesTest(BaseTenderUAContentWebTest,
                             BaseTenderLotEdgeCasesTest):
    initial_lots = test_lots * 2
    initial_bids = test_bids


class TenderLotFeatureResourceTest(BaseTenderUAContentWebTest,
                                   BaseTenderLotFeatureResourceTest):
    initial_lots = 2 * test_lots
    test_tender_data = test_tender_data


class BaseTenderLotBidderResourceTest(object):
    test_create_tender_bidder_invalid = snitch(create_tender_bidder_invalid)
    test_patch_tender_bidder = snitch(patch_tender_bidder)


class TenderLotBidderResourceTest(BaseTenderUAContentWebTest,
                                  BaseTenderLotBidderResourceTest):
    # initial_status = 'active.tendering'
    initial_lots = test_lots


class BaseTenderLotFeatureBidderResourceTest(object):
    test_feature_create_tender_bidder_invalid = snitch(feature_create_tender_bidder_invalid)
    test_feature_create_tender_bidder = snitch(feature_create_tender_bidder)


class TenderLotFeatureBidderResourceTest(BaseTenderUAContentWebTest,
                                         BaseTenderLotFeatureBidderResourceTest):
    initial_lots = test_lots

    def setUp(self):
        super(TenderLotFeatureBidderResourceTest, self).setUp()
        self.lot_id = self.initial_lots[0]['id']
        response = self.app.patch_json('/tenders/{}?acc_token={}'.format(self.tender_id, self.tender_token), {"data": {
            "items": [
                {
                    'relatedLot': self.lot_id,
                    'id': '1'
                }
            ],
            "features": [
                {
                    "code": "code_item",
                    "featureOf": "item",
                    "relatedItem": "1",
                    "title": u"item feature",
                    "enum": [
                        {
                            "value": 0.01,
                            "title": u"good"
                        },
                        {
                            "value": 0.02,
                            "title": u"best"
                        }
                    ]
                },
                {
                    "code": "code_lot",
                    "featureOf": "lot",
                    "relatedItem": self.lot_id,
                    "title": u"lot feature",
                    "enum": [
                        {
                            "value": 0.01,
                            "title": u"good"
                        },
                        {
                            "value": 0.02,
                            "title": u"best"
                        }
                    ]
                },
                {
                    "code": "code_tenderer",
                    "featureOf": "tenderer",
                    "title": u"tenderer feature",
                    "enum": [
                        {
                            "value": 0.01,
                            "title": u"good"
                        },
                        {
                            "value": 0.02,
                            "title": u"best"
                        }
                    ]
                }
            ]
        }})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']['items'][0]['relatedLot'], self.lot_id)


class BaseTenderLotProcessTest(object):
    test_lot1_0bid = snitch(lot1_0bid)
    test_lot1_1bid = snitch(lot1_1bid)
    test_lot1_1bid_patch = snitch(lot1_1bid_patch)
    test_lot1_2bid = snitch(lot1_2bid)
    test_lot1_3bid_1un = snitch(lot1_3bid_1un)
    test_lot2_0bid = snitch(lot2_0bid)
    test_lot2_2can = snitch(lot2_2can)
    test_lot2_1bid_0com_1can = snitch(lot2_1bid_0com_1can)
    test_lot2_2bid_1lot_del = snitch(lot2_2bid_1lot_del)
    test_lot2_1bid_2com_1win = snitch(lot2_1bid_2com_1win)
    test_lot2_1bid_0com_0win = snitch(lot2_1bid_0com_0win)
    test_lot2_1bid_1com_1win = snitch(lot2_1bid_1com_1win)
    test_lot2_2bid_2com_2win = snitch(lot2_2bid_2com_2win)


class TenderLotProcessTest(BaseTenderUAContentWebTest,
                           BaseTenderLotProcessTest):
    setUp = BaseTenderUAContentWebTest.setUp
    test_tender_data = test_tender_data


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TenderLotResourceTest))
    suite.addTest(unittest.makeSuite(TenderLotBidderResourceTest))
    suite.addTest(unittest.makeSuite(TenderLotFeatureBidderResourceTest))
    suite.addTest(unittest.makeSuite(TenderLotProcessTest))
    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='suite')
