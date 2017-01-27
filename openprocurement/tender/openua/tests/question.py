# -*- coding: utf-8 -*-
import unittest

from datetime import datetime, timedelta
from openprocurement.api.models import get_now
from openprocurement.api.tests.base import test_lots, test_organization
from openprocurement.tender.openua.tests.base import BaseTenderUAContentWebTest, test_tender_data
from openprocurement.api.tests.question import BaseTenderQuestionResourceTest, BaseTenderLotQuestionResourceTest

class BaseTenderUAQuestionResourceTest(object):
    def test_create_tender_question(self):
        response = self.app.post_json('/tenders/{}/questions'.format(
            self.tender_id), {'data': {'title': 'question title', 'description': 'question description', 'author': test_organization}})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        question = response.json['data']
        self.assertEqual(question['author']['name'], test_organization['name'])
        self.assertIn('id', question)
        self.assertIn(question['id'], response.headers['Location'])

        self.go_to_enquiryPeriod_end()
        response = self.app.post_json('/tenders/{}/questions'.format(
            self.tender_id), {'data': {'title': 'question title', 'description': 'question description', 'author': test_organization}}, status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]["description"], "Can add question only in enquiryPeriod")

        self.set_status('active.auction')
        response = self.app.post_json('/tenders/{}/questions'.format(
            self.tender_id), {'data': {'title': 'question title', 'description': 'question description', 'author': test_organization}}, status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]["description"], "Can add question only in enquiryPeriod")

class TenderUAQuestionResourceTest(BaseTenderUAContentWebTest, BaseTenderQuestionResourceTest, BaseTenderUAQuestionResourceTest):
    status = "active.auction"
    test_tender_data = test_tender_data

class TenderUALotQuestionResourceTest(BaseTenderUAContentWebTest, BaseTenderLotQuestionResourceTest):
    initial_lots = 2 * test_lots

    def test_create_tender_question(self):
        response = self.app.post_json('/tenders/{}/cancellations?acc_token={}'.format(self.tender_id, self.tender_token), {'data': {
            'reason': 'cancellation reason',
            'status': 'active',
            "cancellationOf": "lot",
            "relatedLot": self.initial_lots[0]['id']
        }})
        self.assertEqual(response.status, '201 Created')

        response = self.app.post_json('/tenders/{}/questions'.format(self.tender_id), {'data': {
            'title': 'question title',
            'description': 'question description',
            "questionOf": "lot",
            "relatedItem": self.initial_lots[0]['id'],
            'author': test_organization
        }}, status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]["description"], "Can add question only in active lot status")

        response = self.app.post_json('/tenders/{}/questions'.format(self.tender_id), {'data': {
            'title': 'question title',
            'description': 'question description',
            "questionOf": "lot",
            "relatedItem": self.initial_lots[1]['id'],
            'author': test_organization
        }})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        question = response.json['data']
        self.assertEqual(question['author']['name'], test_organization['name'])
        self.assertIn('id', question)
        self.assertIn(question['id'], response.headers['Location'])

    def test_patch_tender_question(self):
        response = self.app.post_json('/tenders/{}/questions'.format(self.tender_id), {'data': {
            'title': 'question title',
            'description': 'question description',
            "questionOf": "lot",
            "relatedItem": self.initial_lots[0]['id'],
            'author': test_organization
        }})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        question = response.json['data']

        response = self.app.post_json('/tenders/{}/cancellations?acc_token={}'.format(self.tender_id, self.tender_token), {'data': {
            'reason': 'cancellation reason',
            'status': 'active',
            "cancellationOf": "lot",
            "relatedLot": self.initial_lots[0]['id']
        }})
        self.assertEqual(response.status, '201 Created')

        response = self.app.patch_json('/tenders/{}/questions/{}?acc_token={}'.format(
            self.tender_id, question['id'], self.tender_token), {"data": {"answer": "answer"}}, status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]["description"], "Can update question only in active lot status")

        response = self.app.post_json('/tenders/{}/questions'.format(self.tender_id), {'data': {
            'title': 'question title',
            'description': 'question description',
            "questionOf": "lot",
            "relatedItem": self.initial_lots[1]['id'],
            'author': test_organization
        }})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        question = response.json['data']

        response = self.app.patch_json('/tenders/{}/questions/{}?acc_token={}'.format(
            self.tender_id, question['id'], self.tender_token), {"data": {"answer": "answer"}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']["answer"], "answer")
        self.assertIn('dateAnswered', response.json['data'])

        response = self.app.get('/tenders/{}/questions/{}'.format(self.tender_id, question['id']))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']["answer"], "answer")
        self.assertIn('dateAnswered', response.json['data'])

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

    def test_tender_has_unanswered_questions(self):
        question_id = self.create_question_for("tender", self.tender_id)

        self.set_status('active.auction', {'status': 'active.tendering'})
        self.app.authorization = ('Basic', ('chronograph', ''))
        response = self.app.patch_json('/tenders/{}'.format(self.tender_id), {"data": {"id": self.tender_id}})
        self.assertEqual(response.json['data']['status'], 'active.tendering')

        self.app.authorization = ('Basic', ('broker', ''))
        response = self.app.post_json('/tenders/{}/cancellations?acc_token={}'.format(self.tender_id, self.tender_token), {'data': {
            'reason': 'cancellation reason',
            'status': 'active',
        }})
        self.assertEqual(response.status, '201 Created')

        response = self.app.get('/tenders/{}'.format(self.tender_id))
        self.assertEqual(response.json['data']['status'], 'cancelled')

    def test_lot_has_unanswered_questions(self):
        question_id = self.create_question_for("lot", self.initial_lots[0]['id'])

        self.set_status('active.auction', {'status': 'active.tendering'})
        self.app.authorization = ('Basic', ('chronograph', ''))
        response = self.app.patch_json('/tenders/{}'.format(self.tender_id), {"data": {"id": self.tender_id}})
        self.assertEqual(response.json['data']['status'], 'active.tendering')

        self.app.authorization = ('Basic', ('broker', ''))
        response = self.app.post_json('/tenders/{}/cancellations?acc_token={}'.format(self.tender_id, self.tender_token), {'data': {
            'reason': 'cancellation reason',
            'status': 'active',
            "cancellationOf": "lot",
            "relatedLot": self.initial_lots[0]['id']
        }})
        self.assertEqual(response.status, '201 Created')

        self.app.authorization = ('Basic', ('chronograph', ''))
        response = self.app.patch_json('/tenders/{}'.format(self.tender_id), {"data": {"id": self.tender_id}})
        self.assertEqual(response.json['data']['status'], 'unsuccessful')

    def test_item_has_unanswered_questions(self):
        items = self.app.get('/tenders/{}'.format(self.tender_id)).json['data']['items']
        question_id = self.create_question_for("item", items[0]['id'])

        self.set_status('active.auction', {'status': 'active.tendering'})
        self.app.authorization = ('Basic', ('chronograph', ''))
        response = self.app.patch_json('/tenders/{}'.format(self.tender_id), {"data": {"id": self.tender_id}})
        self.assertEqual(response.json['data']['status'], 'active.tendering')

        self.app.authorization = ('Basic', ('broker', ''))
        response = self.app.post_json('/tenders/{}/cancellations?acc_token={}'.format(self.tender_id, self.tender_token), {'data': {
            'reason': 'cancellation reason',
            'status': 'active',
            "cancellationOf": "lot",
            "relatedLot": self.initial_lots[0]['id']
        }})
        self.assertEqual(response.status, '201 Created')

        self.app.authorization = ('Basic', ('chronograph', ''))
        response = self.app.patch_json('/tenders/{}'.format(self.tender_id), {"data": {"id": self.tender_id}})
        self.assertEqual(response.json['data']['status'], 'unsuccessful')

def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TenderUAQuestionResourceTest))
    suite.addTest(unittest.makeSuite(TenderUALotQuestionResourceTest))
    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='suite')
