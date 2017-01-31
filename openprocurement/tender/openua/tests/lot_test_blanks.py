# -*- coding: utf-8 -*-
from openprocurement.api.tests.base import test_lots


def get_tender_lot(self):
    response = self.app.post_json('/tenders/{}/lots?acc_token={}'.format(
        self.tender_id, self.tender_token), {'data': test_lots[0]})
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    lot = response.json['data']

    response = self.app.get('/tenders/{}/lots/{}'.format(self.tender_id, lot['id']))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(set(response.json['data']), set([u'status', u'date', u'description', u'title', u'minimalStep', u'auctionPeriod', u'value', u'id']))

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
    self.assertEqual(set(response.json['data'][0]), set([u'status', u'description', u'date', u'title', u'minimalStep', u'auctionPeriod', u'value', u'id']))

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
        self.tender_id, lot['id'], self.tender_token), {"data": {"value": {"currency": "USD"}, "minimalStep": {"currency": "USD"}}})
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
        self.tender_id, lot['id'], self.tender_token), {"data": {"value": {"currency": "USD"}, "minimalStep": {"currency": "USD"}}}, status=403)

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
        self.tender_id, self.tender_token), {"data": {"value": {"valueAddedTaxIncluded": False},"minimalStep": {"valueAddedTaxIncluded": False}}})
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
        self.tender_id, lot['id'], self.tender_token), {"data": {"value": {"valueAddedTaxIncluded": True}, "minimalStep": {"valueAddedTaxIncluded": True}}})
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
        self.tender_id, lot['id'], self.tender_token), {"data": {"value": {"currency": "USD"}, "minimalStep": {"currency": "USD"}}}, status=403)

    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
