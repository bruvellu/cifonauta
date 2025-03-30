from django.test import TestCase
from django.urls import reverse

#TODO: Assert file name matches UUID field.
#TODO: Make test for Media's normalize_title and normalize_caption methods
#TODO: Check that the default ordering of model querysets didn't change
#TODO: Test detection of duplicate references on import
#TODO: Check synchronization of valid/invalid media


class WebsiteTests(TestCase):
    '''Check if website pages are loading properly.'''

    pages = [
            {'url': '/', 'name': 'home'},
            {'url': '/tours/', 'name': 'tours_url'}
            ]

    def test_response_status_code(self):

        for page in self.pages:

            with self.subTest(url=page['url']):
                response = self.client.get(page['url'])
                self.assertEqual(response.status_code, 200)

            with self.subTest(name=page['name']):
                response = self.client.get(reverse(page['name']))
                self.assertEqual(response.status_code, 200)

    # def test_response_status_code_for_page_url(self, page):
        # response = self.client.get(page.url)
        # self.assertEqual(response.status_code, 200)

    # def test_response_status_code_for_page_name(self, page):
        # response = self.client.get(reverse(page.name))
        # self.assertEqual(response.status_code, 200)

