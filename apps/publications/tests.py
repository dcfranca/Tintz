from publications import *
from django.test.client import Client

import unittest

"""
Tests
"""
class PublicationTestCase(unittest.TestCase):
    def setUp(self):
        publication = Publication()

    def TestWebRequests(self):
        cl = Client()
        response = cl.post()

    def TestIsValidFormat(self):
        self.assertTrue( is_valid_format('teste.zip','') )
        self.assertTrue( is_valid_format('teste.rar','') )
        self.assertTrue( is_valid_format('teste.cbr','') )
        self.assertTrue( is_valid_format('teste.cbz','') )
        self.assertTrue( is_valid_format('teste.cbR','') )
        self.assertTrue( is_valid_format('teste.cbZ','') )
        self.assertTrue( is_valid_format('teste.CBZ','plaintext') )
        self.assertTrue( is_valid_format('/home/danielfranca/olamundo.CBR','') )
        self.assertTrue( is_valid_format('/home/danielfranca/olamundo.txt','image/png') )
        self.assertTrue( is_valid_format('/home/danielfranca/olamundo.png','image/gif') )
        self.assertTrue( is_valid_format('/home/danielfranca/olamundo.jpg','image/jpg') )
        self.assertTrue( is_valid_format('/home/danielfranca/olamundo.pdf','application/pdf') )
        self.assertTrue( is_valid_format('/home/danielfranca/olamundo.jpg','image/jpg') )

        self.assertFalse( is_valid_format('/home/danielfranca/olamundo.txt','') )
        self.assertFalse( is_valid_format('/home/danielfranca/olamundo.cbm','') )
        self.assertFalse( is_valid_format('/home/danielfranca/teste123','plain/text') )
        self.assertFalse( is_valid_format('/home/danielfranca/abc.pnd','') )
        self.assertFalse( is_valid_format('/home/danielfranca/olamundo.CB','') )

    def publicComic(self):
        publication.author = "daniel"
        publication.date_added = datetime.datetime.now()
        publication.is_public = False
        publication.status = 0
        publication.title = "Titulo teste"
        publication.save()
