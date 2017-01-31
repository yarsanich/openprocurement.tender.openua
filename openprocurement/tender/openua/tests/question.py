# -*- coding: utf-8 -*-
import unittest

from openprocurement.api.tests.base import test_lots, test_organization, snitch
from openprocurement.tender.openua.tests.base import BaseTenderUAContentWebTest, test_tender_data
from openprocurement.api.tests.question import BaseTenderQuestionResourceTest, BaseTenderLotQuestionResourceTest
from openprocurement.tender.openua.tests.question_tests_blanks import (create_tender_question,
                                                                       patch_tender_question,
                                                                       tender_has_unanswered_questions,
                                                                       lot_has_unanswered_questions,
                                                                       item_has_unanswered_questions,
                                                                       create_tender_question_lot)


class BaseTenderUAQuestionResourceTest(BaseTenderQuestionResourceTest):
    test_create_tender_question = snitch(create_tender_question)


class TenderUAQuestionResourceTest(BaseTenderUAContentWebTest, BaseTenderUAQuestionResourceTest):
    status = "active.auction"
    test_tender_data = test_tender_data


class BaseTenderUALotQuestionResourceTest(BaseTenderLotQuestionResourceTest):
    def create_question_for(self, questionOf, relatedItem):
        response = self.app.post_json('/tenders/{}/questions'.format(self.tender_id), {'data': {
            'title': 'question title',
            'description': 'question description',
            "questionOf": questionOf,
            "relatedItem": relatedItem,
            'author': test_organization
        }})
        self.assertEqual(response.status, '201 Created')
        return response.json['data']['id']

    test_create_tender_question_lot = snitch(create_tender_question_lot)
    test_patch_tender_question = snitch(patch_tender_question)
    test_tender_has_unanswered_questions = snitch(tender_has_unanswered_questions)
    test_lot_has_unanswered_questions = snitch(lot_has_unanswered_questions)
    test_item_has_unanswered_questions = snitch(item_has_unanswered_questions)


class TenderUALotQuestionResourceTest(BaseTenderUAContentWebTest,
                                      BaseTenderUALotQuestionResourceTest):
    initial_lots = 2 * test_lots

def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TenderUAQuestionResourceTest))
    suite.addTest(unittest.makeSuite(TenderUALotQuestionResourceTest))
    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='suite')
