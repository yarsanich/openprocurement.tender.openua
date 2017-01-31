# -*- coding: utf-8 -*-
import unittest
from email.header import Header
from openprocurement.api.tests.document_test_blanks import (not_found,
                                                           put_tender_document,
                                                           patch_tender_document,
                                                           create_tender_document,
                                                           create_tender_document_json_invalid,
                                                           create_tender_document_json,
                                                           put_tender_document_json)
from openprocurement.tender.openua.tests.base import BaseTenderUAContentWebTest
from openprocurement.api.tests.base import snitch


class BaseTenderDocumentResourceTest(object):
    docservice = False

    test_not_found = snitch(not_found)
    test_put_tender_document = snitch(put_tender_document)
    test_patch_tender_document = snitch(patch_tender_document)
    test_create_tender_document = snitch(create_tender_document)

class TenderDocumentResourceTest(BaseTenderUAContentWebTest,
                                 BaseTenderDocumentResourceTest):
    status = 'active.auction'


class BaseTenderDocumentWithDSResourceTest(object):
    test_create_tender_document_json_invalid = snitch(create_tender_document_json_invalid)
    test_create_tender_document_json = snitch(create_tender_document_json)
    test_put_tender_document_json = snitch(put_tender_document_json)


class TenderDocumentWithDSResourceTest(TenderDocumentResourceTest,
                                       BaseTenderDocumentWithDSResourceTest):
    docservice = True


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TenderDocumentResourceTest))
    suite.addTest(unittest.makeSuite(TenderDocumentWithDSResourceTest))
    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='suite')
