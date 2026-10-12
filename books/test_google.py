from unittest.mock import patch, MagicMock
from django.test import SimpleTestCase, override_settings
from books.integrations.google_books import lookup_isbn, MetadataUnavailable
import requests

@override_settings(GOOGLE_BOOKS_API_KEY="test-only")
class GoogleTests(SimpleTestCase):
    def fake(self,payload):
        response=MagicMock(); response.json.return_value=payload
        session=MagicMock(); session.__enter__.return_value=session; session.get.return_value=response
        return session
    def test_maps_partial_fields(self):
        payload={"items":[{"volumeInfo":{"title":"Book","publishedDate":"2020","industryIdentifiers":[{"identifier":"9780306406157"}],"description":"<b>Hello</b>"}}]}
        with patch("books.integrations.google_books.requests.Session",return_value=self.fake(payload)):
            data=lookup_isbn("9780306406157")
        self.assertEqual(data["description"],"Hello"); self.assertIsNone(data["published_date"])
    def test_missing_results(self):
        with patch("books.integrations.google_books.requests.Session",return_value=self.fake({})):
            with self.assertRaises(MetadataUnavailable):
                lookup_isbn("9780306406157")
    def test_timeout(self):
        session=self.fake({}); session.get.side_effect=requests.Timeout()
        with patch("books.integrations.google_books.requests.Session",return_value=session):
            with self.assertRaises(MetadataUnavailable): lookup_isbn("9780306406157")