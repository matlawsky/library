from django.test import TestCase
from books.forms import AddBookForm


class AuthorLimitTests(TestCase):
    def form(self, authors):
        return AddBookForm(dict(title="Limits", subtitle="Text", description="Text",
                                published_date="2020-01-01", page_count=1,
                                number_of_copies=0, authors=authors))

    def test_each_author_has_database_length_limit(self):
        form = self.form("Valid;" + "x" * 251)
        self.assertFalse(form.is_valid())
        self.assertIn("authors", form.errors)

    def test_limit_applies_per_trimmed_name(self):
        self.assertTrue(self.form(" " + "x" * 250 + " ; " + "y" * 250).is_valid())