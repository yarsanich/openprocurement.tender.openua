# -*- coding: utf-8 -*-
from copy import deepcopy
from datetime import timedelta
from openprocurement.api.models import get_now
from openprocurement.api.tests.base import test_lots,test_organization


def get_tender_lot(self):
    response = self.app.post_json('/tenders/{}/lots?acc_token={}'.format(
        self.tender_id, self.tender_token), {'data': test_lots[0]})
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    lot = response.json['data']

    response = self.app.get('/tenders/{}/lots/{}'.format(self.tender_id, lot['id']))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(set(response.json['data']), set(
        [u'status', u'date', u'description', u'title', u'minimalStep', u'auctionPeriod', u'value', u'id']))

    self.set_status('active.qualification')

    response = self.app.get('/tenders/{}/lots/{}'.format(self.tender_id, lot['id']))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    lot.pop('auctionPeriod')
    self.assertEqual(response.json['data'], lot)

    response = self.app.get('/tenders/{}/lots/some_id'.format(self.tender_id), status=404)
    self.assertEqual(response.status, '404 Not Found')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': u'Not Found', u'location':
            u'url', u'name': u'lot_id'}
    ])

    response = self.app.get('/tenders/some_id/lots/some_id', status=404)
    self.assertEqual(response.status, '404 Not Found')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': u'Not Found', u'location':
            u'url', u'name': u'tender_id'}
    ])


def get_tender_lots(self):
    response = self.app.post_json('/tenders/{}/lots?acc_token={}'.format(
        self.tender_id, self.tender_token), {'data': test_lots[0]})
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    lot = response.json['data']

    response = self.app.get('/tenders/{}/lots'.format(self.tender_id))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(set(response.json['data'][0]), set(
        [u'status', u'description', u'date', u'title', u'minimalStep', u'auctionPeriod', u'value', u'id']))

    self.set_status('active.qualification')

    response = self.app.get('/tenders/{}/lots'.format(self.tender_id))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    lot.pop('auctionPeriod')
    self.assertEqual(response.json['data'][0], lot)

    response = self.app.get('/tenders/some_id/lots', status=404)
    self.assertEqual(response.status, '404 Not Found')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': u'Not Found', u'location':
            u'url', u'name': u'tender_id'}
    ])


def patch_tender_currency(self):
    # create lot
    response = self.app.post_json('/tenders/{}/lots?acc_token={}'.format(
        self.tender_id, self.tender_token), {'data': test_lots[0]})
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    lot = response.json['data']
    self.assertEqual(lot['value']['currency'], "UAH")

    # update tender currency without mimimalStep currency change
    response = self.app.patch_json('/tenders/{}?acc_token={}'.format(
        self.tender_id, self.tender_token), {"data": {"value": {"currency": "GBP"}}}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': [u'currency should be identical to currency of value of tender'],
         u'location': u'body', u'name': u'minimalStep'}
    ])

    # update tender currency
    response = self.app.patch_json('/tenders/{}?acc_token={}'.format(self.tender_id, self.tender_token), {"data": {
        "value": {"currency": "GBP"},
        "minimalStep": {"currency": "GBP"}
    }})
    self.assertEqual(response.status, '200 OK')
    # log currency is updated too
    response = self.app.get('/tenders/{}/lots/{}'.format(self.tender_id, lot['id']))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    lot = response.json['data']
    self.assertEqual(lot['value']['currency'], "GBP")

    # try to update lot currency
    response = self.app.patch_json('/tenders/{}/lots/{}?acc_token={}'.format(
        self.tender_id, lot['id'], self.tender_token), {"data": {"value": {"currency": "USD"}}})
    self.assertEqual(response.status, '200 OK')
    # but the value stays unchanged
    response = self.app.get('/tenders/{}/lots/{}'.format(self.tender_id, lot['id']))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    lot = response.json['data']
    self.assertEqual(lot['value']['currency'], "GBP")

    # try to update minimalStep currency
    response = self.app.patch_json('/tenders/{}/lots/{}?acc_token={}'.format(
        self.tender_id, lot['id'], self.tender_token), {"data": {"minimalStep": {"currency": "USD"}}})
    self.assertEqual(response.status, '200 OK')
    # but the value stays unchanged
    response = self.app.get('/tenders/{}/lots/{}'.format(self.tender_id, lot['id']))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    lot = response.json['data']
    self.assertEqual(lot['minimalStep']['currency'], "GBP")

    # try to update lot minimalStep currency and lot value currency in single request
    response = self.app.patch_json('/tenders/{}/lots/{}?acc_token={}'.format(
        self.tender_id, lot['id'], self.tender_token),
        {"data": {"value": {"currency": "USD"}, "minimalStep": {"currency": "USD"}}})
    self.assertEqual(response.status, '200 OK')
    # but the value stays unchanged
    response = self.app.get('/tenders/{}/lots/{}'.format(self.tender_id, lot['id']))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    lot = response.json['data']
    self.assertEqual(lot['value']['currency'], "GBP")
    self.assertEqual(lot['minimalStep']['currency'], "GBP")

    self.go_to_enquiryPeriod_end()
    response = self.app.patch_json('/tenders/{}/lots/{}?acc_token={}'.format(
        self.tender_id, lot['id'], self.tender_token),
        {"data": {"value": {"currency": "USD"}, "minimalStep": {"currency": "USD"}}}, status=403)

    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')


def patch_tender_vat(self):
    # set tender VAT
    response = self.app.patch_json('/tenders/{}?acc_token={}'.format(
        self.tender_id, self.tender_token), {"data": {"value": {"valueAddedTaxIncluded": True}}})
    self.assertEqual(response.status, '200 OK')

    # create lot
    response = self.app.post_json('/tenders/{}/lots?acc_token={}'.format(
        self.tender_id, self.tender_token), {'data': test_lots[0]})
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    lot = response.json['data']
    self.assertTrue(lot['value']['valueAddedTaxIncluded'])

    # update tender VAT
    response = self.app.patch_json('/tenders/{}?acc_token={}'.format(
        self.tender_id, self.tender_token),
        {"data": {"value": {"valueAddedTaxIncluded": False}, "minimalStep": {"valueAddedTaxIncluded": False}}})
    self.assertEqual(response.status, '200 OK')
    # log VAT is updated too
    response = self.app.get('/tenders/{}/lots/{}'.format(self.tender_id, lot['id']))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    lot = response.json['data']
    self.assertFalse(lot['value']['valueAddedTaxIncluded'])

    # try to update lot VAT
    response = self.app.patch_json('/tenders/{}/lots/{}?acc_token={}'.format(
        self.tender_id, lot['id'], self.tender_token), {"data": {"value": {"valueAddedTaxIncluded": True}}})
    self.assertEqual(response.status, '200 OK')
    # but the value stays unchanged
    response = self.app.get('/tenders/{}/lots/{}'.format(self.tender_id, lot['id']))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    lot = response.json['data']
    self.assertFalse(lot['value']['valueAddedTaxIncluded'])

    # try to update minimalStep VAT
    response = self.app.patch_json('/tenders/{}/lots/{}?acc_token={}'.format(
        self.tender_id, lot['id'], self.tender_token), {"data": {"minimalStep": {"valueAddedTaxIncluded": True}}})
    self.assertEqual(response.status, '200 OK')
    # but the value stays unchanged
    response = self.app.get('/tenders/{}/lots/{}'.format(self.tender_id, lot['id']))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    lot = response.json['data']
    self.assertFalse(lot['minimalStep']['valueAddedTaxIncluded'])

    # try to update minimalStep VAT and value VAT in single request
    response = self.app.patch_json('/tenders/{}/lots/{}?acc_token={}'.format(
        self.tender_id, lot['id'], self.tender_token),
        {"data": {"value": {"valueAddedTaxIncluded": True}, "minimalStep": {"valueAddedTaxIncluded": True}}})
    self.assertEqual(response.status, '200 OK')
    # but the value stays unchanged
    response = self.app.get('/tenders/{}/lots/{}'.format(self.tender_id, lot['id']))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    lot = response.json['data']
    self.assertFalse(lot['value']['valueAddedTaxIncluded'])
    self.assertEqual(lot['minimalStep']['valueAddedTaxIncluded'], lot['value']['valueAddedTaxIncluded'])

    self.go_to_enquiryPeriod_end()
    response = self.app.patch_json('/tenders/{}/lots/{}?acc_token={}'.format(
        self.tender_id, lot['id'], self.tender_token),
        {"data": {"value": {"currency": "USD"}, "minimalStep": {"currency": "USD"}}}, status=403)

    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')


def create_tender_lot(self):
    response = self.app.post_json('/tenders/{}/lots?acc_token={}'.format(
        self.tender_id, self.tender_token), {'data': test_lots[0]})
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    lot = response.json['data']
    self.assertEqual(lot['title'], 'lot title')
    self.assertEqual(lot['description'], 'lot description')
    self.assertIn('id', lot)
    self.assertIn('date', lot)
    self.assertIn(lot['id'], response.headers['Location'])
    self.assertNotIn('guarantee', lot)

    lot2 = deepcopy(test_lots[0])
    lot2['guarantee'] = {"amount": 100500, "currency": "USD"}
    response = self.app.post_json('/tenders/{}/lots?acc_token={}'.format(self.tender_id, self.tender_token),
                                  {'data': lot2})
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    data = response.json['data']
    self.assertIn('guarantee', data)
    self.assertEqual(data['guarantee']['amount'], 100500)
    self.assertEqual(data['guarantee']['currency'], "USD")

    response = self.app.get('/tenders/{}'.format(self.tender_id))
    self.assertIn('guarantee', response.json['data'])
    self.assertEqual(response.json['data']['guarantee']['amount'], 100500)
    self.assertEqual(response.json['data']['guarantee']['currency'], "USD")
    self.assertNotIn('guarantee', response.json['data']['lots'][0])

    lot3 = deepcopy(test_lots[0])
    lot3['guarantee'] = {"amount": 500, "currency": "UAH"}
    response = self.app.post_json('/tenders/{}/lots?acc_token={}'.format(self.tender_id, self.tender_token),
                                  {'data': lot3}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': [u'lot guarantee currency should be identical to tender guarantee currency'],
         u'location': u'body', u'name': u'lots'}
    ])

    lot3['guarantee'] = {"amount": 500}
    response = self.app.post_json('/tenders/{}/lots?acc_token={}'.format(self.tender_id, self.tender_token),
                                  {'data': lot3}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': [u'lot guarantee currency should be identical to tender guarantee currency'],
         u'location': u'body', u'name': u'lots'}
    ])

    lot3['guarantee'] = {"amount": 20, "currency": "USD"}
    response = self.app.post_json('/tenders/{}/lots?acc_token={}'.format(self.tender_id, self.tender_token),
                                  {'data': lot3})
    self.assertEqual(response.status, '201 Created')
    data = response.json['data']
    self.assertIn('guarantee', data)
    self.assertEqual(data['guarantee']['amount'], 20)
    self.assertEqual(data['guarantee']['currency'], "USD")

    response = self.app.get('/tenders/{}'.format(self.tender_id))
    self.assertIn('guarantee', response.json['data'])
    self.assertEqual(response.json['data']['guarantee']['amount'], 100500 + 20)
    self.assertEqual(response.json['data']['guarantee']['currency'], "USD")

    response = self.app.patch_json('/tenders/{}?acc_token={}'.format(self.tender_id, self.tender_token),
                                   {"data": {"guarantee": {"currency": "EUR"}}})
    self.assertEqual(response.json['data']['guarantee']['amount'], 100500 + 20)
    self.assertEqual(response.json['data']['guarantee']['currency'], "EUR")
    self.assertNotIn('guarantee', response.json['data']['lots'][0])
    self.assertEqual(response.json['data']['lots'][1]['guarantee']['amount'], 100500)
    self.assertEqual(response.json['data']['lots'][1]['guarantee']['currency'], "EUR")
    self.assertEqual(response.json['data']['lots'][2]['guarantee']['amount'], 20)
    self.assertEqual(response.json['data']['lots'][2]['guarantee']['currency'], "EUR")

    response = self.app.post_json('/tenders/{}/lots?acc_token={}'.format(self.tender_id,
                                                                         self.tender_token), {'data': lot},
                                  status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': [u'Lot id should be uniq for all lots'], u'location': u'body', u'name': u'lots'}
    ])

    self.go_to_enquiryPeriod_end()
    response = self.app.post_json('/tenders/{}/lots'.format(self.tender_id), {'data': test_lots[0]}, status=403)

    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')

    self.set_status('active.auction')

    response = self.app.post_json('/tenders/{}/lots?acc_token={}'.format(self.tender_id, self.tender_token),
                                  {'data': test_lots[0]}, status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"],
                     "Can't add lot in current (active.auction) tender status")


def patch_tender_lot(self):
    response = self.app.post_json('/tenders/{}/lots?acc_token={}'.format(
        self.tender_id, self.tender_token), {'data': test_lots[0]})
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    lot = response.json['data']

    response = self.app.patch_json('/tenders/{}/lots/{}?acc_token={}'.format(
        self.tender_id, lot['id'], self.tender_token), {"data": {"title": "new title"}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data']["title"], "new title")

    response = self.app.patch_json(
        '/tenders/{}/lots/{}?acc_token={}'.format(self.tender_id, lot['id'], self.tender_token),
        {"data": {"guarantee": {"amount": 12}}})
    self.assertEqual(response.status, '200 OK')
    self.assertIn('guarantee', response.json['data'])
    self.assertEqual(response.json['data']['guarantee']['amount'], 12)
    self.assertEqual(response.json['data']['guarantee']['currency'], 'UAH')

    response = self.app.patch_json(
        '/tenders/{}/lots/{}?acc_token={}'.format(self.tender_id, lot['id'], self.tender_token),
        {"data": {"guarantee": {"currency": "USD"}}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.json['data']['guarantee']['currency'], 'UAH')

    response = self.app.patch_json('/tenders/{}/lots/some_id'.format(self.tender_id),
                                   {"data": {"title": "other title"}}, status=404)
    self.assertEqual(response.status, '404 Not Found')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': u'Not Found', u'location':
            u'url', u'name': u'lot_id'}
    ])

    response = self.app.patch_json('/tenders/some_id/lots/some_id', {"data": {"title": "other title"}}, status=404)
    self.assertEqual(response.status, '404 Not Found')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': u'Not Found', u'location':
            u'url', u'name': u'tender_id'}
    ])

    response = self.app.get('/tenders/{}/lots/{}'.format(self.tender_id, lot['id']))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data']["title"], "new title")

    self.set_status('active.auction')

    response = self.app.patch_json('/tenders/{}/lots/{}?acc_token={}'.format(
        self.tender_id, lot['id'], self.tender_token), {"data": {"title": "other title"}}, status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"],
                     "Can't update lot in current (active.auction) tender status")


def question_blocking(self):
    self.app.authorization = ('Basic', ('broker', ''))
    response = self.app.post_json('/tenders/{}/questions'.format(self.tender_id),
                                  {'data': {'title': 'question title',
                                            'description': 'question description',
                                            'questionOf': 'lot',
                                            'relatedItem': self.initial_lots[0]['id'],
                                            'author': test_organization}})
    question = response.json['data']
    self.assertEqual(question['questionOf'], 'lot')
    self.assertEqual(question['relatedItem'], self.initial_lots[0]['id'])

    self.set_status('active.auction', extra={"status": "active.tendering"})
    self.app.authorization = ('Basic', ('chronograph', ''))
    response = self.app.patch_json('/tenders/{}'.format(self.tender_id), {'data': {'id': self.tender_id}})

    self.app.authorization = ('Basic', ('broker', ''))
    response = self.app.get('/tenders/{}'.format(self.tender_id))
    self.assertEqual(response.json['data']['status'], 'active.tendering')

    # cancel lot
    response = self.app.post_json(
        '/tenders/{}/cancellations?acc_token={}'.format(self.tender_id, self.tender_token),
        {'data': {'reason': 'cancellation reason',
                  'status': 'active',
                  "cancellationOf": "lot",
                  "relatedLot": self.initial_lots[0]['id']}})

    self.app.authorization = ('Basic', ('chronograph', ''))
    response = self.app.patch_json('/tenders/{}'.format(self.tender_id), {"data": {"id": self.tender_id}})

    self.app.authorization = ('Basic', ('broker', ''))
    response = self.app.get('/tenders/{}'.format(self.tender_id))
    self.assertEqual(response.json['data']['status'], 'active.auction')


def claim_blocking(self):
    self.app.authorization = ('Basic', ('broker', ''))
    response = self.app.post_json('/tenders/{}/complaints'.format(self.tender_id),
                                  {'data': {'title': 'complaint title',
                                            'description': 'complaint description',
                                            'author': test_organization,
                                            'relatedLot': self.initial_lots[0]['id'],
                                            'status': 'claim'}})
    self.assertEqual(response.status, '201 Created')
    complaint = response.json['data']
    owner_token = response.json['access']['token']
    self.assertEqual(complaint['relatedLot'], self.initial_lots[0]['id'])

    self.set_status('active.auction', extra={"status": "active.tendering"})
    self.app.authorization = ('Basic', ('chronograph', ''))
    response = self.app.patch_json('/tenders/{}'.format(self.tender_id), {'data': {'id': self.tender_id}})

    self.app.authorization = ('Basic', ('broker', ''))
    response = self.app.get('/tenders/{}'.format(self.tender_id))
    self.assertEqual(response.json['data']['status'], 'active.tendering')

    # cancel lot
    response = self.app.post_json(
        '/tenders/{}/cancellations?acc_token={}'.format(self.tender_id, self.tender_token),
        {'data': {'reason': 'cancellation reason',
                  'status': 'active',
                  "cancellationOf": "lot",
                  "relatedLot": self.initial_lots[0]['id']}})

    self.app.authorization = ('Basic', ('chronograph', ''))
    response = self.app.patch_json('/tenders/{}'.format(self.tender_id), {"data": {"id": self.tender_id}})

    self.app.authorization = ('Basic', ('broker', ''))
    response = self.app.get('/tenders/{}'.format(self.tender_id))
    self.assertEqual(response.json['data']['status'], 'active.auction')


def next_check_value_with_unanswered_question(self):
    self.app.authorization = ('Basic', ('broker', ''))
    response = self.app.post_json('/tenders/{}/questions'.format(self.tender_id),
                                  {'data': {'title': 'question title',
                                            'description': 'question description',
                                            'questionOf': 'lot',
                                            'relatedItem': self.initial_lots[0]['id'],
                                            'author': test_organization}})
    question = response.json['data']
    self.assertEqual(question['questionOf'], 'lot')
    self.assertEqual(question['relatedItem'], self.initial_lots[0]['id'])

    self.set_status('active.auction', extra={"status": "active.tendering"})
    self.app.authorization = ('Basic', ('chronograph', ''))
    response = self.app.patch_json('/tenders/{}'.format(self.tender_id), {'data': {'id': self.tender_id}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data']["status"], 'active.tendering')
    self.assertNotIn('next_check', response.json['data'])

    self.app.authorization = ('Basic', ('broker', ''))
    response = self.app.post_json(
        '/tenders/{}/cancellations?acc_token={}'.format(self.tender_id, self.tender_token),
        {'data': {'reason': 'cancellation reason',
                  'status': 'active',
                  "cancellationOf": "lot",
                  "relatedLot": self.initial_lots[0]['id']}})

    response = self.app.get('/tenders/{}'.format(self.tender_id, ))
    self.assertIn('next_check', response.json['data'])
    self.assertEqual(response.json['data']['next_check'], response.json['data']['tenderPeriod']['endDate'])

    self.app.authorization = ('Basic', ('chronograph', ''))
    response = self.app.patch_json('/tenders/{}'.format(self.tender_id), {'data': {'id': self.tender_id}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data']["status"], 'active.auction')
    self.assertIn('next_check', response.json['data'])
    self.assertGreater(response.json['data']['next_check'], response.json['data']['tenderPeriod']['endDate'])


def next_check_value_with_unanswered_claim(self):
    self.app.authorization = ('Basic', ('broker', ''))
    response = self.app.post_json('/tenders/{}/complaints'.format(self.tender_id),
                                  {'data': {'title': 'complaint title',
                                            'description': 'complaint description',
                                            'author': test_organization,
                                            'relatedLot': self.initial_lots[0]['id'],
                                            'status': 'claim'}})
    self.assertEqual(response.status, '201 Created')
    complaint = response.json['data']
    owner_token = response.json['access']['token']
    self.assertEqual(complaint['relatedLot'], self.initial_lots[0]['id'])

    self.set_status('active.auction', extra={"status": "active.tendering"})
    self.app.authorization = ('Basic', ('chronograph', ''))
    response = self.app.patch_json('/tenders/{}'.format(self.tender_id), {'data': {'id': self.tender_id}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data']["status"], 'active.tendering')
    self.assertNotIn('next_check', response.json['data'])

    self.app.authorization = ('Basic', ('broker', ''))
    response = self.app.post_json(
        '/tenders/{}/cancellations?acc_token={}'.format(self.tender_id, self.tender_token),
        {'data': {'reason': 'cancellation reason',
                  'status': 'active',
                  "cancellationOf": "lot",
                  "relatedLot": self.initial_lots[0]['id']}})

    response = self.app.get('/tenders/{}'.format(self.tender_id, ))
    self.assertIn('next_check', response.json['data'])
    self.assertEqual(response.json['data']['next_check'], response.json['data']['tenderPeriod']['endDate'])

    self.app.authorization = ('Basic', ('chronograph', ''))
    response = self.app.patch_json('/tenders/{}'.format(self.tender_id), {'data': {'id': self.tender_id}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data']["status"], 'active.auction')
    self.assertIn('next_check', response.json['data'])
    self.assertGreater(response.json['data']['next_check'], response.json['data']['tenderPeriod']['endDate'])


def create_tender_bidder_invalid(self):
    request_path = '/tenders/{}/bids'.format(self.tender_id)
    response = self.app.post_json(request_path, {'data': {'selfEligible': True, 'selfQualified': True,
                                                          'tenderers': [test_organization]}}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': [u'This field is required.'], u'location': u'body', u'name': u'lotValues'}
    ])

    response = self.app.post_json(request_path, {'data': {'selfEligible': True, 'selfQualified': True,
                                                          'tenderers': [test_organization],
                                                          'lotValues': [{"value": {"amount": 500}}]}}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': [{u'relatedLot': [u'This field is required.']}], u'location': u'body',
         u'name': u'lotValues'}
    ])

    response = self.app.post_json(request_path, {'data': {'selfEligible': True, 'selfQualified': True,
                                                          'tenderers': [test_organization], 'lotValues': [
            {"value": {"amount": 500}, 'relatedLot': "0" * 32}]}}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': [{u'relatedLot': [u'relatedLot should be one of lots']}], u'location': u'body',
         u'name': u'lotValues'}
    ])

    response = self.app.post_json(request_path, {'data': {'selfEligible': True, 'selfQualified': True,
                                                          'tenderers': [test_organization], 'lotValues': [
            {"value": {"amount": 5000000}, 'relatedLot': self.initial_lots[0]['id']}]}}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': [{u'value': [u'value of bid should be less than value of lot']}], u'location': u'body',
         u'name': u'lotValues'}
    ])

    response = self.app.post_json(request_path, {'data': {'selfEligible': True, 'selfQualified': True,
                                                          'tenderers': [test_organization], 'lotValues': [
            {"value": {"amount": 500, 'valueAddedTaxIncluded': False}, 'relatedLot': self.initial_lots[0]['id']}]}},
                                  status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': [{u'value': [
            u'valueAddedTaxIncluded of bid should be identical to valueAddedTaxIncluded of value of lot']}],
            u'location': u'body', u'name': u'lotValues'}
    ])

    response = self.app.post_json(request_path, {'data': {'selfEligible': True, 'selfQualified': True,
                                                          'tenderers': [test_organization], 'lotValues': [
            {"value": {"amount": 500, 'currency': "USD"}, 'relatedLot': self.initial_lots[0]['id']}]}}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': [{u'value': [u'currency of bid should be identical to currency of value of lot']}],
         u'location': u'body', u'name': u'lotValues'},
    ])

    response = self.app.post_json(request_path, {'data': {'selfEligible': True, 'selfQualified': True,
                                                          'tenderers': [test_organization],
                                                          "value": {"amount": 500}, 'lotValues': [
            {"value": {"amount": 500}, 'relatedLot': self.initial_lots[0]['id']}]}}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': [u'value should be posted for each lot of bid'], u'location': u'body', u'name': u'value'}
    ])

    response = self.app.post_json(request_path, {'data': {'selfEligible': True, 'selfQualified': True,
                                                          'tenderers': test_organization, 'lotValues': [
            {"value": {"amount": 500}, 'relatedLot': self.initial_lots[0]['id']}]}}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': u"invalid literal for int() with base 10: 'contactPoint'", u'location': u'body',
         u'name': u'data'},
    ])


def patch_tender_bidder(self):
    lot_id = self.initial_lots[0]['id']
    response = self.app.post_json('/tenders/{}/bids'.format(self.tender_id),
                                  {'data': {'selfEligible': True, 'selfQualified': True,
                                            'tenderers': [test_organization],
                                            'lotValues': [{"value": {"amount": 500}, 'relatedLot': lot_id}]}})
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    bidder = response.json['data']
    lot = bidder['lotValues'][0]
    owner_token = response.json['access']['token']

    response = self.app.patch_json('/tenders/{}/bids/{}?acc_token={}'.format(
        self.tender_id, bidder['id'], owner_token),
        {"data": {'tenderers': [{"name": u"Державне управління управлінням справами"}]}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data']['lotValues'][0]['date'], lot['date'])
    self.assertNotEqual(response.json['data']['tenderers'][0]['name'], bidder['tenderers'][0]['name'])

    response = self.app.patch_json('/tenders/{}/bids/{}?acc_token={}'.format(
        self.tender_id, bidder['id'], owner_token), {
        "data": {'lotValues': [{"value": {"amount": 500}, 'relatedLot': lot_id}],
                 'tenderers': [test_organization]}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data']['lotValues'][0]['date'], lot['date'])
    self.assertEqual(response.json['data']['tenderers'][0]['name'], bidder['tenderers'][0]['name'])

    response = self.app.patch_json(
        '/tenders/{}/bids/{}?acc_token={}'.format(self.tender_id, bidder['id'], owner_token),
        {"data": {'lotValues': [{"value": {"amount": 400}, 'relatedLot': lot_id}]}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data']['lotValues'][0]["value"]["amount"], 400)
    self.assertNotEqual(response.json['data']['lotValues'][0]['date'], lot['date'])

    self.set_status('complete')

    response = self.app.get('/tenders/{}/bids/{}'.format(self.tender_id, bidder['id']))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data']['lotValues'][0]["value"]["amount"], 400)

    response = self.app.patch_json('/tenders/{}/bids/{}?acc_token={}'.format(
        self.tender_id, bidder['id'], owner_token),
        {"data": {'lotValues': [{"value": {"amount": 500}, 'relatedLot': lot_id}]}}, status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"],
                     "Can't update bid in current (complete) tender status")


def feature_create_tender_bidder_invalid(self):
    request_path = '/tenders/{}/bids'.format(self.tender_id)
    response = self.app.post_json(request_path, {'data': {'selfEligible': True, 'selfQualified': True,
                                                          'tenderers': [test_organization]}}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': [u'This field is required.'], u'location': u'body', u'name': u'lotValues'},
        {u'description': [u'All features parameters is required.'], u'location': u'body', u'name': u'parameters'}
    ])

    response = self.app.post_json(request_path, {'data': {'selfEligible': True, 'selfQualified': True,
                                                          'tenderers': [test_organization],
                                                          'lotValues': [{"value": {"amount": 500}}]}}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': [{u'relatedLot': [u'This field is required.']}], u'location': u'body',
         u'name': u'lotValues'}
    ])

    response = self.app.post_json(request_path, {'data': {'selfEligible': True, 'selfQualified': True,
                                                          'tenderers': [test_organization], 'lotValues': [
            {"value": {"amount": 500}, 'relatedLot': "0" * 32}]}}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': [{u'relatedLot': [u'relatedLot should be one of lots']}], u'location': u'body',
         u'name': u'lotValues'}
    ])

    response = self.app.post_json(request_path, {'data': {'selfEligible': True, 'selfQualified': True,
                                                          'tenderers': [test_organization], 'lotValues': [
            {"value": {"amount": 5000000}, 'relatedLot': self.lot_id}]}}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': [{u'value': [u'value of bid should be less than value of lot']}], u'location': u'body',
         u'name': u'lotValues'}
    ])

    response = self.app.post_json(request_path, {'data': {'selfEligible': True, 'selfQualified': True,
                                                          'tenderers': [test_organization], 'lotValues': [
            {"value": {"amount": 500, 'valueAddedTaxIncluded': False}, 'relatedLot': self.lot_id}]}}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': [{u'value': [
            u'valueAddedTaxIncluded of bid should be identical to valueAddedTaxIncluded of value of lot']}],
            u'location': u'body', u'name': u'lotValues'}
    ])

    response = self.app.post_json(request_path, {'data': {'selfEligible': True, 'selfQualified': True,
                                                          'tenderers': [test_organization], 'lotValues': [
            {"value": {"amount": 500, 'currency': "USD"}, 'relatedLot': self.lot_id}]}}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': [{u'value': [u'currency of bid should be identical to currency of value of lot']}],
         u'location': u'body', u'name': u'lotValues'},
    ])

    response = self.app.post_json(request_path, {'data': {'selfEligible': True, 'selfQualified': True,
                                                          'tenderers': test_organization, 'lotValues': [
            {"value": {"amount": 500}, 'relatedLot': self.lot_id}]}}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': u"invalid literal for int() with base 10: 'contactPoint'", u'location': u'body',
         u'name': u'data'},
    ])

    response = self.app.post_json(request_path, {'data': {'selfEligible': True, 'selfQualified': True,
                                                          'tenderers': [test_organization], 'lotValues': [
            {"value": {"amount": 500}, 'relatedLot': self.lot_id}]}}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': [u'All features parameters is required.'], u'location': u'body', u'name': u'parameters'}
    ])

    response = self.app.post_json(request_path, {'data': {'selfEligible': True, 'selfQualified': True,
                                                          'tenderers': [test_organization], 'lotValues': [
            {"value": {"amount": 500}, 'relatedLot': self.lot_id}],
                                                          'parameters': [{"code": "code_item", "value": 0.01}]}},
                                  status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': [u'All features parameters is required.'], u'location': u'body', u'name': u'parameters'}
    ])

    response = self.app.post_json(request_path, {'data': {'selfEligible': True, 'selfQualified': True,
                                                          'tenderers': [test_organization], 'lotValues': [
            {"value": {"amount": 500}, 'relatedLot': self.lot_id}],
                                                          'parameters': [{"code": "code_invalid", "value": 0.01}]}},
                                  status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': [{u'code': [u'code should be one of feature code.']}], u'location': u'body',
         u'name': u'parameters'}
    ])

    response = self.app.post_json(request_path, {'data': {'selfEligible': True, 'selfQualified': True,
                                                          'tenderers': [test_organization], 'lotValues': [
            {"value": {"amount": 500}, 'relatedLot': self.lot_id}], 'parameters': [
            {"code": "code_item", "value": 0.01},
            {"code": "code_tenderer", "value": 0},
            {"code": "code_lot", "value": 0.01},
        ]}}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': [{u'value': [u'value should be one of feature value.']}], u'location': u'body',
         u'name': u'parameters'}
    ])


def feature_create_tender_bidder(self):
    request_path = '/tenders/{}/bids'.format(self.tender_id)
    response = self.app.post_json(request_path, {'data': {'selfEligible': True, 'selfQualified': True,
                                                          'tenderers': [test_organization], 'lotValues': [
            {"value": {"amount": 500}, 'relatedLot': self.lot_id}], 'parameters': [
            {"code": "code_item", "value": 0.01},
            {"code": "code_tenderer", "value": 0.01},
            {"code": "code_lot", "value": 0.01},
        ]}})
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    bidder = response.json['data']
    self.assertEqual(bidder['tenderers'][0]['name'], test_organization['name'])
    self.assertIn('id', bidder)
    self.assertIn(bidder['id'], response.headers['Location'])

    self.set_status('complete')

    response = self.app.post_json(request_path, {'data': {'selfEligible': True, 'selfQualified': True,
                                                          'tenderers': [test_organization], 'lotValues': [
            {"value": {"amount": 500}, 'relatedLot': self.lot_id}], 'parameters': [
            {"code": "code_item", "value": 0.01},
            {"code": "code_tenderer", "value": 0.01},
            {"code": "code_lot", "value": 0.01},
        ]}}, status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"], "Can't add bid in current (complete) tender status")


def lot1_0bid(self):
    # create tender
    response = self.app.post_json('/tenders', {"data": self.test_tender_data})
    tender_id = self.tender_id = response.json['data']['id']
    owner_token = response.json['access']['token']
    # add lot
    response = self.app.post_json('/tenders/{}/lots?acc_token={}'.format(tender_id, owner_token),
                                  {'data': test_lots[0]})
    self.assertEqual(response.status, '201 Created')
    lot_id = response.json['data']['id']
    # add relatedLot for item
    response = self.app.patch_json('/tenders/{}?acc_token={}'.format(tender_id, owner_token),
                                   {"data": {"items": [{'relatedLot': lot_id}]}})
    self.assertEqual(response.status, '200 OK')
    # switch to active.tendering
    response = self.set_status('active.tendering', {
        "lots": [{"auctionPeriod": {"startDate": (get_now() + timedelta(days=16)).isoformat()}}]})
    self.assertIn("auctionPeriod", response.json['data']['lots'][0])
    # switch to unsuccessful
    response = self.set_status('active.auction',
                               {"lots": [{"auctionPeriod": {"startDate": None}}], 'status': 'active.tendering'})
    self.app.authorization = ('Basic', ('chronograph', ''))
    response = self.app.patch_json('/tenders/{}'.format(tender_id), {"data": {"id": tender_id}})
    self.assertEqual(response.json['data']["lots"][0]['status'], 'unsuccessful')
    self.assertEqual(response.json['data']['status'], 'unsuccessful')


def lot1_1bid(self):
    # create tender
    response = self.app.post_json('/tenders', {"data": self.test_tender_data})
    tender_id = self.tender_id = response.json['data']['id']
    owner_token = response.json['access']['token']
    # add lot
    response = self.app.post_json('/tenders/{}/lots?acc_token={}'.format(tender_id, owner_token),
                                  {'data': test_lots[0]})
    self.assertEqual(response.status, '201 Created')
    lot_id = response.json['data']['id']
    # add relatedLot for item
    response = self.app.patch_json('/tenders/{}?acc_token={}'.format(tender_id, owner_token),
                                   {"data": {"items": [{'relatedLot': lot_id}]}})
    self.assertEqual(response.status, '200 OK')
    # switch to active.tendering
    response = self.set_status('active.tendering', {
        "lots": [{"auctionPeriod": {"startDate": (get_now() + timedelta(days=16)).isoformat()}}]})
    self.assertIn("auctionPeriod", response.json['data']['lots'][0])
    # create bid
    self.app.authorization = ('Basic', ('broker', ''))
    response = self.app.post_json('/tenders/{}/bids'.format(tender_id),
                                  {'data': {'selfEligible': True, 'selfQualified': True,
                                            'tenderers': [test_organization],
                                            'lotValues': [{"subcontractingDetails": "test",
                                                           "value": {"amount": 500}, 'relatedLot': lot_id}]}})
    # switch to active.qualification
    response = self.set_status('active.auction',
                               {"lots": [{"auctionPeriod": {"startDate": None}}], 'status': 'active.tendering'})
    self.app.authorization = ('Basic', ('chronograph', ''))
    response = self.app.patch_json('/tenders/{}'.format(tender_id), {"data": {"id": tender_id}})
    self.assertEqual(response.json['data']["lots"][0]['status'], 'unsuccessful')
    self.assertEqual(response.json['data']['status'], 'unsuccessful')


def lot1_1bid_patch(self):
    # create tender
    response = self.app.post_json('/tenders', {"data": self.test_tender_data})
    tender_id = self.tender_id = response.json['data']['id']
    owner_token = response.json['access']['token']
    # add lot
    response = self.app.post_json('/tenders/{}/lots?acc_token={}'.format(tender_id, owner_token),
                                  {'data': test_lots[0]})
    self.assertEqual(response.status, '201 Created')
    lot_id = response.json['data']['id']
    # add relatedLot for item
    response = self.app.patch_json('/tenders/{}?acc_token={}'.format(tender_id, owner_token),
                                   {"data": {"items": [{'relatedLot': lot_id}]}})
    self.assertEqual(response.status, '200 OK')
    # create bid
    self.app.authorization = ('Basic', ('broker', ''))
    response = self.app.post_json('/tenders/{}/bids'.format(tender_id),
                                  {'data': {'selfEligible': True, 'selfQualified': True,
                                            'tenderers': [test_organization],
                                            'lotValues': [{"value": {"amount": 500}, 'relatedLot': lot_id}]}})
    bid_id = response.json['data']['id']
    bid_token = response.json['access']['token']

    response = self.app.patch_json('/tenders/{}/lots/{}?acc_token={}'.format(tender_id, lot_id, owner_token),
                                   {'data': {'value': {'amount': 499}}})
    self.assertEqual(response.status, '200 OK')

    response = self.app.get('/tenders/{}/bids/{}?acc_token={}'.format(tender_id, bid_id, bid_token))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.json['data']['status'], 'invalid')


def lot1_2bid(self):
    # create tender
    response = self.app.post_json('/tenders', {"data": self.test_tender_data})
    tender_id = self.tender_id = response.json['data']['id']
    owner_token = response.json['access']['token']
    # add lot
    response = self.app.post_json('/tenders/{}/lots?acc_token={}'.format(tender_id, owner_token),
                                  {'data': test_lots[0]})
    self.assertEqual(response.status, '201 Created')
    lot_id = response.json['data']['id']
    self.initial_lots = [response.json['data']]
    # add relatedLot for item
    response = self.app.patch_json('/tenders/{}?acc_token={}'.format(tender_id, owner_token),
                                   {"data": {"items": [{'relatedLot': lot_id}]}})
    self.assertEqual(response.status, '200 OK')
    # switch to active.tendering
    response = self.set_status('active.tendering', {
        "lots": [{"auctionPeriod": {"startDate": (get_now() + timedelta(days=16)).isoformat()}}]})
    self.assertIn("auctionPeriod", response.json['data']['lots'][0])
    # create bid
    self.app.authorization = ('Basic', ('broker', ''))
    response = self.app.post_json('/tenders/{}/bids'.format(tender_id),
                                  {'data': {'selfEligible': True, 'selfQualified': True,
                                            'tenderers': [test_organization],
                                            'lotValues': [{"subcontractingDetails": "test",
                                                           "value": {"amount": 450}, 'relatedLot': lot_id}]}})
    bid_id = response.json['data']['id']
    bid_token = response.json['access']['token']
    # create second bid
    self.app.authorization = ('Basic', ('broker', ''))
    response = self.app.post_json('/tenders/{}/bids'.format(tender_id),
                                  {'data': {'selfEligible': True, 'selfQualified': True,
                                            'tenderers': [test_organization],
                                            'lotValues': [{"value": {"amount": 475}, 'relatedLot': lot_id}]}})
    # switch to active.auction
    self.set_status('active.auction')
    # get auction info
    self.app.authorization = ('Basic', ('auction', ''))
    response = self.app.get('/tenders/{}/auction'.format(tender_id))
    auction_bids_data = response.json['data']['bids']
    # posting auction urls
    response = self.app.patch_json('/tenders/{}/auction/{}'.format(tender_id, lot_id), {
        'data': {
            'lots': [
                {
                    'id': i['id'],
                    'auctionUrl': 'https://tender.auction.url'
                }
                for i in response.json['data']['lots']
                ],
            'bids': [
                {
                    'id': i['id'],
                    'lotValues': [
                        {
                            'relatedLot': j['relatedLot'],
                            'participationUrl': 'https://tender.auction.url/for_bid/{}'.format(i['id'])
                        }
                        for j in i['lotValues']
                        ],
                }
                for i in auction_bids_data
                ]
        }
    })
    # view bid participationUrl
    self.app.authorization = ('Basic', ('broker', ''))
    response = self.app.get('/tenders/{}/bids/{}?acc_token={}'.format(tender_id, bid_id, bid_token))
    self.assertEqual(response.json['data']['lotValues'][0]['participationUrl'],
                     'https://tender.auction.url/for_bid/{}'.format(bid_id))
    # posting auction results
    self.app.authorization = ('Basic', ('auction', ''))
    response = self.app.post_json('/tenders/{}/auction/{}'.format(tender_id, lot_id),
                                  {'data': {'bids': auction_bids_data}})
    # get awards
    self.app.authorization = ('Basic', ('broker', ''))
    response = self.app.get('/tenders/{}/awards?acc_token={}'.format(tender_id, owner_token))
    # get pending award
    award_id = [i['id'] for i in response.json['data'] if i['status'] == 'pending'][0]
    # set award as active
    self.app.patch_json('/tenders/{}/awards/{}?acc_token={}'.format(tender_id, award_id, owner_token),
                        {"data": {"status": "active", "qualified": True, "eligible": True}})
    # get contract id
    response = self.app.get('/tenders/{}'.format(tender_id))
    contract_id = response.json['data']['contracts'][-1]['id']
    # after stand slill period
    self.set_status('complete', {'status': 'active.awarded'})
    # time travel
    tender = self.db.get(tender_id)
    for i in tender.get('awards', []):
        i['complaintPeriod']['endDate'] = i['complaintPeriod']['startDate']
    self.db.save(tender)
    # sign contract
    self.app.authorization = ('Basic', ('broker', ''))
    self.app.patch_json('/tenders/{}/contracts/{}?acc_token={}'.format(tender_id, contract_id, owner_token),
                        {"data": {"status": "active"}})
    # check status
    self.app.authorization = ('Basic', ('broker', ''))
    response = self.app.get('/tenders/{}'.format(tender_id))
    self.assertEqual(response.json['data']["lots"][0]['status'], 'complete')
    self.assertEqual(response.json['data']['status'], 'complete')


def lot1_3bid_1un(self):
    # create tender
    response = self.app.post_json('/tenders', {"data": self.test_tender_data})
    tender_id = self.tender_id = response.json['data']['id']
    owner_token = response.json['access']['token']
    # add lot
    response = self.app.post_json('/tenders/{}/lots?acc_token={}'.format(tender_id, owner_token),
                                  {'data': test_lots[0]})
    self.assertEqual(response.status, '201 Created')
    lot_id = response.json['data']['id']
    self.initial_lots = [response.json['data']]
    # add relatedLot for item
    response = self.app.patch_json('/tenders/{}?acc_token={}'.format(tender_id, owner_token),
                                   {"data": {"items": [{'relatedLot': lot_id}]}})
    self.assertEqual(response.status, '200 OK')
    # switch to active.tendering
    response = self.set_status('active.tendering', {
        "lots": [{"auctionPeriod": {"startDate": (get_now() + timedelta(days=16)).isoformat()}}]})
    self.assertIn("auctionPeriod", response.json['data']['lots'][0])
    # create bids
    bids_data = {}
    for i in range(3):
        self.app.authorization = ('Basic', ('broker', ''))
        response = self.app.post_json('/tenders/{}/bids'.format(tender_id),
                                      {'data': {'selfEligible': True, 'selfQualified': True,
                                                'tenderers': [test_organization],
                                                'lotValues': [{"value": {"amount": 450}, 'relatedLot': lot_id}]}})
        bids_data[response.json['data']['id']] = response.json['access']['token']

    response = self.app.patch_json('/tenders/{}/lots/{}?acc_token={}'.format(tender_id, lot_id, owner_token),
                                   {'data': {'value': {'amount': 1000}}})
    self.assertEqual(response.status, '200 OK')
    # create second bid
    for bid_id, bid_token in bids_data.items()[:-1]:
        self.app.authorization = ('Basic', ('broker', ''))
        response = self.app.patch_json('/tenders/{}/bids/{}?acc_token={}'.format(tender_id, bid_id, bid_token),
                                       {'data': {'status': "active"}})
        # bids_data[response.json['data']['id']] = response.json['access']['token']
    # switch to active.auction
    self.set_status('active.auction')
    # get auction info
    self.app.authorization = ('Basic', ('auction', ''))
    response = self.app.get('/tenders/{}/auction'.format(tender_id))
    auction_bids_data = response.json['data']['bids']
    # posting auction urls

    auction_data = {
        'data': {
            'lots': [
                {
                    'id': i['id'],
                    'auctionUrl': 'https://tender.auction.url'
                }
                for i in response.json['data']['lots']
                ],
            'bids': []
        }
    }
    for i in auction_bids_data:
        if i.get("status", "active") == "active":
            auction_data["data"]["bids"].append({
                'id': i['id'],
                'lotValues': [
                    {
                        'relatedLot': j['relatedLot'],
                        'participationUrl': 'https://tender.auction.url/for_bid/{}'.format(i['id'])
                    }
                    for j in i['lotValues']
                    ],
            })
        else:
            auction_data["data"]["bids"].append({'id': i['id']})

    response = self.app.patch_json('/tenders/{}/auction/{}'.format(tender_id, lot_id), auction_data)
    # posting auction results
    self.app.authorization = ('Basic', ('auction', ''))
    response = self.app.post_json('/tenders/{}/auction/{}'.format(tender_id, lot_id),
                                  {'data': {'bids': auction_bids_data}})
    self.app.authorization = ('Basic', ('broker', ''))
    response = self.app.get('/tenders/{}/awards?acc_token={}'.format(tender_id, owner_token))
    # get pending award
    award_id = [i['id'] for i in response.json['data'] if i['status'] == 'pending'][0]
    # set award as active
    self.app.patch_json('/tenders/{}/awards/{}?acc_token={}'.format(tender_id, award_id, owner_token),
                        {"data": {"status": "active", "qualified": True, "eligible": True}})
    # get contract id
    response = self.app.get('/tenders/{}'.format(tender_id))
    contract_id = response.json['data']['contracts'][-1]['id']
    # after stand slill period
    self.set_status('complete', {'status': 'active.awarded'})
    # time travel
    tender = self.db.get(tender_id)
    for i in tender.get('awards', []):
        i['complaintPeriod']['endDate'] = i['complaintPeriod']['startDate']
    self.db.save(tender)
    # sign contract
    self.app.authorization = ('Basic', ('broker', ''))
    self.app.patch_json('/tenders/{}/contracts/{}?acc_token={}'.format(tender_id, contract_id, owner_token),
                        {"data": {"status": "active"}})
    # check status
    self.app.authorization = ('Basic', ('broker', ''))
    response = self.app.get('/tenders/{}'.format(tender_id))
    self.assertEqual(response.json['data']["lots"][0]['status'], 'complete')
    self.assertEqual(response.json['data']['status'], 'complete')


def lot2_0bid(self):
    # create tender
    response = self.app.post_json('/tenders', {"data": self.test_tender_data})
    tender_id = self.tender_id = response.json['data']['id']
    owner_token = response.json['access']['token']
    lots = []
    for lot in 2 * test_lots:
        # add lot
        response = self.app.post_json('/tenders/{}/lots?acc_token={}'.format(tender_id, owner_token),
                                      {'data': test_lots[0]})
        self.assertEqual(response.status, '201 Created')
        lots.append(response.json['data']['id'])
    # add item
    response = self.app.patch_json('/tenders/{}?acc_token={}'.format(tender_id, owner_token),
                                   {"data": {"items": [self.test_tender_data['items'][0] for i in lots]}})
    # add relatedLot for item
    response = self.app.patch_json('/tenders/{}?acc_token={}'.format(tender_id, owner_token),
                                   {"data": {"items": [{'relatedLot': i} for i in lots]}})
    self.assertEqual(response.status, '200 OK')
    # switch to active.tendering
    response = self.set_status('active.tendering', {"lots": [
        {"auctionPeriod": {"startDate": (get_now() + timedelta(days=16)).isoformat()}}
        for i in lots
        ]})
    self.assertTrue(all(["auctionPeriod" in i for i in response.json['data']['lots']]))
    # switch to unsuccessful
    response = self.set_status('active.auction', {
        "lots": [
            {"auctionPeriod": {"startDate": None}}
            for i in lots
            ],
        'status': 'active.tendering'})
    self.app.authorization = ('Basic', ('chronograph', ''))
    response = self.app.patch_json('/tenders/{}'.format(tender_id), {"data": {"id": tender_id}})
    self.assertTrue(all([i['status'] == 'unsuccessful' for i in response.json['data']['lots']]))
    self.assertEqual(response.json['data']['status'], 'unsuccessful')


def lot2_2can(self):
    # create tender
    response = self.app.post_json('/tenders', {"data": self.test_tender_data})
    tender_id = self.tender_id = response.json['data']['id']
    owner_token = response.json['access']['token']
    lots = []
    for lot in 2 * test_lots:
        # add lot
        response = self.app.post_json('/tenders/{}/lots?acc_token={}'.format(tender_id, owner_token),
                                      {'data': test_lots[0]})
        self.assertEqual(response.status, '201 Created')
        lots.append(response.json['data']['id'])
    # add item
    response = self.app.patch_json('/tenders/{}?acc_token={}'.format(tender_id, owner_token),
                                   {"data": {"items": [self.test_tender_data['items'][0] for i in lots]}})
    # add relatedLot for item
    response = self.app.patch_json('/tenders/{}?acc_token={}'.format(tender_id, owner_token),
                                   {"data": {"items": [{'relatedLot': i} for i in lots]}})
    self.assertEqual(response.status, '200 OK')
    # switch to active.tendering
    response = self.set_status('active.tendering', {"lots": [
        {"auctionPeriod": {"startDate": (get_now() + timedelta(days=16)).isoformat()}}
        for i in lots
        ]})
    self.assertTrue(all(["auctionPeriod" in i for i in response.json['data']['lots']]))
    # cancel every lot
    for lot_id in lots:
        response = self.app.post_json('/tenders/{}/cancellations?acc_token={}'.format(tender_id, owner_token),
                                      {'data': {
                                          'reason': 'cancellation reason',
                                          'status': 'active',
                                          "cancellationOf": "lot",
                                          "relatedLot": lot_id
                                      }})
    response = self.app.get('/tenders/{}'.format(tender_id))
    self.assertTrue(all([i['status'] == 'cancelled' for i in response.json['data']['lots']]))
    self.assertEqual(response.json['data']['status'], 'cancelled')


def lot2_1bid_0com_1can(self):
    # create tender
    response = self.app.post_json('/tenders', {"data": self.test_tender_data})
    tender_id = self.tender_id = response.json['data']['id']
    owner_token = response.json['access']['token']
    lots = []
    for lot in 2 * test_lots:
        # add lot
        response = self.app.post_json('/tenders/{}/lots?acc_token={}'.format(tender_id, owner_token),
                                      {'data': test_lots[0]})
        self.assertEqual(response.status, '201 Created')
        lots.append(response.json['data']['id'])
    # add item
    response = self.app.patch_json('/tenders/{}?acc_token={}'.format(tender_id, owner_token),
                                   {"data": {"items": [self.test_tender_data['items'][0] for i in lots]}})
    # add relatedLot for item
    response = self.app.patch_json('/tenders/{}?acc_token={}'.format(tender_id, owner_token),
                                   {"data": {"items": [{'relatedLot': i} for i in lots]}})
    self.assertEqual(response.status, '200 OK')
    # switch to active.tendering
    response = self.set_status('active.tendering', {"lots": [
        {"auctionPeriod": {"startDate": (get_now() + timedelta(days=16)).isoformat()}}
        for i in lots
        ]})
    # create bid
    self.app.authorization = ('Basic', ('broker', ''))
    response = self.app.post_json('/tenders/{}/bids'.format(tender_id),
                                  {'data': {'selfEligible': True, 'selfQualified': True,
                                            'tenderers': [test_organization], 'lotValues': [
                                          {"value": {"amount": 500}, 'relatedLot': lot_id}
                                          for lot_id in lots
                                          ]}}
                                  )
    # switch to active.qualification
    response = self.set_status('active.auction', {
        "lots": [
            {"auctionPeriod": {"startDate": None}}
            for i in lots
            ],
        'status': 'active.tendering'})
    self.app.authorization = ('Basic', ('chronograph', ''))
    response = self.app.patch_json('/tenders/{}'.format(tender_id), {"data": {"id": tender_id}})
    self.assertEqual(response.json['data']['status'], 'unsuccessful')


def lot2_2bid_1lot_del(self):
    self.app.authorization = ('Basic', ('broker', ''))
    # create tender
    response = self.app.post_json('/tenders', {"data": self.test_tender_data})
    tender_id = self.tender_id = response.json['data']['id']
    owner_token = response.json['access']['token']
    lots = []
    for lot in 2 * test_lots:
        # add lot
        response = self.app.post_json('/tenders/{}/lots?acc_token={}'.format(tender_id, owner_token),
                                      {'data': test_lots[0]})
        self.assertEqual(response.status, '201 Created')
        lots.append(response.json['data']['id'])
    self.initial_lots = lots
    # add item
    response = self.app.patch_json('/tenders/{}?acc_token={}'.format(tender_id, owner_token),
                                   {"data": {"items": [self.test_tender_data['items'][0] for i in lots]}})
    # add relatedLot for item
    # response = self.app.patch_json('/tenders/{}?acc_token={}'.format(tender_id, owner_token), {"data": {"items": [{'relatedLot': i} for i in lots[]]}})
    # self.assertEqual(response.status, '200 OK')
    # switch to active.tendering
    response = self.set_status('active.tendering', {"lots": [
        {"auctionPeriod": {"startDate": (get_now() + timedelta(days=16)).isoformat()}}
        for i in lots
        ]})
    # create bid

    bids = []
    self.app.authorization = ('Basic', ('broker', ''))
    response = self.app.post_json('/tenders/{}/bids'.format(tender_id),
                                  {'data': {'selfEligible': True, 'selfQualified': True,
                                            'tenderers': [test_organization], 'lotValues': [
                                          {"value": {"amount": 500}, 'relatedLot': lot_id}
                                          for lot_id in lots
                                          ]}})
    bids.append(response.json)
    # create second bid
    self.app.authorization = ('Basic', ('broker', ''))
    response = self.app.post_json('/tenders/{}/bids'.format(tender_id),
                                  {'data': {'selfEligible': True, 'selfQualified': True,
                                            'tenderers': [test_organization], 'lotValues': [
                                          {"value": {"amount": 500}, 'relatedLot': lot_id}
                                          for lot_id in lots
                                          ]}})
    bids.append(response.json)
    response = self.app.delete('/tenders/{}/lots/{}?acc_token={}'.format(self.tender_id, lots[0], owner_token))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')


def lot2_1bid_2com_1win(self):
    # create tender
    response = self.app.post_json('/tenders', {"data": self.test_tender_data})
    tender_id = self.tender_id = response.json['data']['id']
    owner_token = response.json['access']['token']
    lots = []
    for lot in 2 * test_lots:
        # add lot
        response = self.app.post_json('/tenders/{}/lots?acc_token={}'.format(tender_id, owner_token),
                                      {'data': test_lots[0]})
        self.assertEqual(response.status, '201 Created')
        lots.append(response.json['data']['id'])
    # add item
    response = self.app.patch_json('/tenders/{}?acc_token={}'.format(tender_id, owner_token),
                                   {"data": {"items": [self.test_tender_data['items'][0] for i in lots]}})
    # add relatedLot for item
    response = self.app.patch_json('/tenders/{}?acc_token={}'.format(tender_id, owner_token),
                                   {"data": {"items": [{'relatedLot': i} for i in lots]}})
    self.assertEqual(response.status, '200 OK')
    # switch to active.tendering
    response = self.set_status('active.tendering', {"lots": [
        {"auctionPeriod": {"startDate": (get_now() + timedelta(days=16)).isoformat()}}
        for i in lots
        ]})
    # create bid
    self.app.authorization = ('Basic', ('broker', ''))
    response = self.app.post_json('/tenders/{}/bids'.format(tender_id),
                                  {'data': {'selfEligible': True, 'selfQualified': True,
                                            'tenderers': [test_organization], 'lotValues': [
                                          {"value": {"amount": 500}, 'relatedLot': lot_id}
                                          for lot_id in lots
                                          ]}})
    # switch to active.qualification
    response = self.set_status('active.auction', {
        "lots": [
            {"auctionPeriod": {"startDate": None}}
            for i in lots
            ],
        'status': 'active.tendering'})
    self.app.authorization = ('Basic', ('chronograph', ''))
    response = self.app.patch_json('/tenders/{}'.format(tender_id), {"data": {"id": tender_id}})
    for lot_id in lots:
        # get awards
        self.app.authorization = ('Basic', ('broker', ''))
        response = self.app.get('/tenders/{}/awards?acc_token={}'.format(tender_id, owner_token))
        # get pending award
        if len([i['id'] for i in response.json['data'] if i['status'] == 'pending' and i['lotID'] == lot_id]) == 0:
            return
        award_id = [i['id'] for i in response.json['data'] if i['status'] == 'pending' and i['lotID'] == lot_id][0]

        # set award as active
        self.app.patch_json('/tenders/{}/awards/{}?acc_token={}'.format(tender_id, award_id, owner_token),
                            {"data": {"status": "active"}})
        # get contract id
        response = self.app.get('/tenders/{}'.format(tender_id))
        contract_id = response.json['data']['contracts'][-1]['id']
        # after stand slill period
        self.set_status('complete', {'status': 'active.awarded'})
        # time travel
        tender = self.db.get(tender_id)
        for i in tender.get('awards', []):
            i['complaintPeriod']['endDate'] = i['complaintPeriod']['startDate']
        self.db.save(tender)
        # sign contract
        self.app.authorization = ('Basic', ('broker', ''))
        self.app.patch_json('/tenders/{}/contracts/{}?acc_token={}'.format(tender_id, contract_id, owner_token),
                            {"data": {"status": "active"}})
    # check status
    self.app.authorization = ('Basic', ('broker', ''))
    response = self.app.get('/tenders/{}'.format(tender_id))
    self.assertTrue(all([i['status'] == 'complete' for i in response.json['data']['lots']]))
    self.assertEqual(response.json['data']['status'], 'complete')


def lot2_1bid_0com_0win(self):
    # create tender
    response = self.app.post_json('/tenders', {"data": self.test_tender_data})
    tender_id = self.tender_id = response.json['data']['id']
    owner_token = response.json['access']['token']
    lots = []
    for lot in 2 * test_lots:
        # add lot
        response = self.app.post_json('/tenders/{}/lots?acc_token={}'.format(tender_id, owner_token),
                                      {'data': test_lots[0]})
        self.assertEqual(response.status, '201 Created')
        lots.append(response.json['data']['id'])
    # add item
    response = self.app.patch_json('/tenders/{}?acc_token={}'.format(tender_id, owner_token),
                                   {"data": {"items": [self.test_tender_data['items'][0] for i in lots]}})
    # add relatedLot for item
    response = self.app.patch_json('/tenders/{}?acc_token={}'.format(tender_id, owner_token),
                                   {"data": {"items": [{'relatedLot': i} for i in lots]}})
    self.assertEqual(response.status, '200 OK')
    # switch to active.tendering
    response = self.set_status('active.tendering', {"lots": [
        {"auctionPeriod": {"startDate": (get_now() + timedelta(days=16)).isoformat()}}
        for i in lots
        ]})
    # create bid
    self.app.authorization = ('Basic', ('broker', ''))
    response = self.app.post_json('/tenders/{}/bids'.format(tender_id),
                                  {'data': {'selfEligible': True, 'selfQualified': True,
                                            'tenderers': [test_organization], 'lotValues': [
                                          {"value": {"amount": 500}, 'relatedLot': lot_id}
                                          for lot_id in lots
                                          ]}})
    # switch to active.qualification
    response = self.set_status('active.auction', {
        "lots": [
            {"auctionPeriod": {"startDate": None}}
            for i in lots
            ],
        'status': 'active.tendering'})
    self.app.authorization = ('Basic', ('chronograph', ''))
    response = self.app.patch_json('/tenders/{}'.format(tender_id), {"data": {"id": tender_id}})
    self.assertTrue(all([i['status'] == 'unsuccessful' for i in response.json['data']['lots']]))
    self.assertEqual(response.json['data']['status'], 'unsuccessful')


def lot2_1bid_1com_1win(self):
    # create tender
    response = self.app.post_json('/tenders', {"data": self.test_tender_data})
    tender_id = self.tender_id = response.json['data']['id']
    owner_token = response.json['access']['token']
    lots = []
    for lot in 2 * test_lots:
        # add lot
        response = self.app.post_json('/tenders/{}/lots?acc_token={}'.format(tender_id, owner_token),
                                      {'data': test_lots[0]})
        self.assertEqual(response.status, '201 Created')
        lots.append(response.json['data']['id'])
    # add item
    response = self.app.patch_json('/tenders/{}?acc_token={}'.format(tender_id, owner_token),
                                   {"data": {"items": [self.test_tender_data['items'][0] for i in lots]}})
    # add relatedLot for item
    response = self.app.patch_json('/tenders/{}?acc_token={}'.format(tender_id, owner_token),
                                   {"data": {"items": [{'relatedLot': i} for i in lots]}})
    self.assertEqual(response.status, '200 OK')
    # switch to active.tendering
    response = self.set_status('active.tendering', {"lots": [
        {"auctionPeriod": {"startDate": (get_now() + timedelta(days=16)).isoformat()}}
        for i in lots
        ]})
    # create bid
    self.app.authorization = ('Basic', ('broker', ''))
    response = self.app.post_json('/tenders/{}/bids'.format(tender_id),
                                  {'data': {'selfEligible': True, 'selfQualified': True,
                                            'tenderers': [test_organization], 'lotValues': [
                                          {"value": {"amount": 500}, 'relatedLot': lot_id}
                                          for lot_id in lots
                                          ]}})
    # switch to active.qualification
    response = self.set_status('active.auction', {
        "lots": [
            {"auctionPeriod": {"startDate": None}}
            for i in lots
            ],
        'status': 'active.tendering'})
    self.app.authorization = ('Basic', ('chronograph', ''))
    response = self.app.patch_json('/tenders/{}'.format(tender_id), {"data": {"id": tender_id}})
    self.assertEqual(response.json['data']['status'], 'unsuccessful')


def lot2_2bid_2com_2win(self):
    # create tender
    response = self.app.post_json('/tenders', {"data": self.test_tender_data})
    tender_id = self.tender_id = response.json['data']['id']
    owner_token = response.json['access']['token']
    lots = []
    for lot in 2 * test_lots:
        # add lot
        response = self.app.post_json('/tenders/{}/lots?acc_token={}'.format(tender_id, owner_token),
                                      {'data': test_lots[0]})
        self.assertEqual(response.status, '201 Created')
        lots.append(response.json['data']['id'])
    self.initial_lots = lots
    # add item
    response = self.app.patch_json('/tenders/{}?acc_token={}'.format(tender_id, owner_token),
                                   {"data": {"items": [self.test_tender_data['items'][0] for i in lots]}})
    # add relatedLot for item
    response = self.app.patch_json('/tenders/{}?acc_token={}'.format(tender_id, owner_token),
                                   {"data": {"items": [{'relatedLot': i} for i in lots]}})
    self.assertEqual(response.status, '200 OK')
    # switch to active.tendering
    response = self.set_status('active.tendering', {"lots": [
        {"auctionPeriod": {"startDate": (get_now() + timedelta(days=16)).isoformat()}}
        for i in lots
        ]})
    # create bid
    self.app.authorization = ('Basic', ('broker', ''))
    response = self.app.post_json('/tenders/{}/bids'.format(tender_id),
                                  {'data': {'selfEligible': True, 'selfQualified': True,
                                            'tenderers': [test_organization], 'lotValues': [
                                          {"value": {"amount": 500}, 'relatedLot': lot_id}
                                          for lot_id in lots
                                          ]}})
    # create second bid
    self.app.authorization = ('Basic', ('broker', ''))
    response = self.app.post_json('/tenders/{}/bids'.format(tender_id),
                                  {'data': {'selfEligible': True, 'selfQualified': True,
                                            'tenderers': [test_organization], 'lotValues': [
                                          {"value": {"amount": 500}, 'relatedLot': lot_id}
                                          for lot_id in lots
                                          ]}})
    # switch to active.auction
    self.set_status('active.auction')
    # get auction info
    self.app.authorization = ('Basic', ('auction', ''))
    response = self.app.get('/tenders/{}/auction'.format(tender_id))
    auction_bids_data = response.json['data']['bids']
    for lot_id in lots:
        # posting auction urls
        response = self.app.patch_json('/tenders/{}/auction/{}'.format(tender_id, lot_id), {
            'data': {
                'lots': [
                    {
                        'id': i['id'],
                        'auctionUrl': 'https://tender.auction.url'
                    }
                    for i in response.json['data']['lots']
                    ],
                'bids': [
                    {
                        'id': i['id'],
                        'lotValues': [
                            {
                                'relatedLot': j['relatedLot'],
                                'participationUrl': 'https://tender.auction.url/for_bid/{}'.format(i['id'])
                            }
                            for j in i['lotValues']
                            ],
                    }
                    for i in auction_bids_data
                    ]
            }
        })
        # posting auction results
        self.app.authorization = ('Basic', ('auction', ''))
        response = self.app.post_json('/tenders/{}/auction/{}'.format(tender_id, lot_id),
                                      {'data': {'bids': auction_bids_data}})
    # for first lot
    lot_id = lots[0]
    # get awards
    self.app.authorization = ('Basic', ('broker', ''))
    response = self.app.get('/tenders/{}/awards?acc_token={}'.format(tender_id, owner_token))
    # get pending award
    award_id = [i['id'] for i in response.json['data'] if i['status'] == 'pending' and i['lotID'] == lot_id][0]
    # set award as active
    self.app.patch_json('/tenders/{}/awards/{}?acc_token={}'.format(tender_id, award_id, owner_token),
                        {"data": {"status": "active", "qualified": True, "eligible": True}})
    # get contract id
    response = self.app.get('/tenders/{}'.format(tender_id))
    contract_id = response.json['data']['contracts'][-1]['id']
    # after stand slill period
    self.set_status('complete', {'status': 'active.awarded'})
    # time travel
    tender = self.db.get(tender_id)
    for i in tender.get('awards', []):
        i['complaintPeriod']['endDate'] = i['complaintPeriod']['startDate']
    self.db.save(tender)
    # sign contract
    self.app.authorization = ('Basic', ('broker', ''))
    self.app.patch_json('/tenders/{}/contracts/{}?acc_token={}'.format(tender_id, contract_id, owner_token),
                        {"data": {"status": "active"}})
    # for second lot
    lot_id = lots[1]
    # get awards
    self.app.authorization = ('Basic', ('broker', ''))
    response = self.app.get('/tenders/{}/awards?acc_token={}'.format(tender_id, owner_token))
    # get pending award
    award_id = [i['id'] for i in response.json['data'] if i['status'] == 'pending' and i['lotID'] == lot_id][0]
    # set award as unsuccessful
    self.app.patch_json('/tenders/{}/awards/{}?acc_token={}'.format(tender_id, award_id, owner_token),
                        {"data": {"status": "unsuccessful"}})
    # get awards
    self.app.authorization = ('Basic', ('broker', ''))
    response = self.app.get('/tenders/{}/awards?acc_token={}'.format(tender_id, owner_token))
    # get pending award
    award_id = [i['id'] for i in response.json['data'] if i['status'] == 'pending' and i['lotID'] == lot_id][0]
    # set award as active
    self.app.patch_json('/tenders/{}/awards/{}?acc_token={}'.format(tender_id, award_id, owner_token),
                        {"data": {"status": "active", "qualified": True, "eligible": True}})
    # get contract id
    response = self.app.get('/tenders/{}'.format(tender_id))
    contract_id = response.json['data']['contracts'][-1]['id']
    # after stand slill period
    self.set_status('complete', {'status': 'active.awarded'})
    # time travel
    tender = self.db.get(tender_id)
    for i in tender.get('awards', []):
        i['complaintPeriod']['endDate'] = i['complaintPeriod']['startDate']
    self.db.save(tender)
    # sign contract
    self.app.authorization = ('Basic', ('broker', ''))
    self.app.patch_json('/tenders/{}/contracts/{}?acc_token={}'.format(tender_id, contract_id, owner_token),
                        {"data": {"status": "active"}})
    # check status
    self.app.authorization = ('Basic', ('broker', ''))
    response = self.app.get('/tenders/{}'.format(tender_id))
    self.assertTrue(all([i['status'] == 'complete' for i in response.json['data']['lots']]))
    self.assertEqual(response.json['data']['status'], 'complete')