# books/tests.py
from django.test import TestCase
from django.urls import resolve, reverse
from django.contrib.auth import get_user_model
from .views import HomePageView
from .models import Book, Author, Copy
import datetime

# TODO add tests coverage for additional classes: Author and Copy


class BookTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Set up 3 types of site viewers
        cls.normal_user = get_user_model().objects.create_user(  # new
            username="Matt User",
            email="matt_user@email.com",
            password="testpass123",
        )

        cls.staff_user = get_user_model().objects.create_user(  # new
            username="Matt Staff Member",
            email="matt_staff_member@email.com",
            password="testpass123",
            is_staff=True,
        )

        cls.super_user = get_user_model().objects.create_superuser(  # new
            username="Matt Admin",
            email="matt_admin@email.com",
            password="testpass123",
        )
        # Set up instances of all classes
        cls.author1 = Author.objects.create(
            name="Harry Pioter",
        )
        cls.author2 = Author.objects.create(
            name="Harry Piuntek",
        )
        cls.book = Book.objects.create(
            title="Magic Mike",
            subtitle="Wizard's wand",
            description="long long long ago",
            published_date=datetime.date.today(),
            page_count=100,
            image_url="https://picsum.photos/seed/picsum/200/329",
        )
        cls.copy1 = Copy.objects.create(
            book=Book.objects.get(id=cls.book.id), state="New"
        )
        cls.book.authors.add(cls.author1, cls.author2)

    ### Views logged out users can access
    # Home
    # Find books
    # Log In
    # Register

    ### Views logged in users can access
    # Home
    # Find books
    # Book detail - only reservation functionality
    # My books - history of books
    # My account - balance and changing the password
    # Log Out

    ### Views logged in staff members can access
    # Home
    # Find books
    # Book detail - only reservation functionality
    # Add book
    # Lend Book
    # Retrieve Book
    # Events history search
    # My books - history of books
    # My account - balance and changing the password
    # Log Out

    # Both tests are to test if page is showing up
    def test_url_exists_at_correct_location(self):
        url = reverse("home")
        self.response = self.client.get(url)
        self.assertEqual(self.response.status_code, 200)

    # testing if correct template is used
    def test_homepage_template(self):
        url = reverse("home")
        self.response = self.client.get(url)
        self.assertTemplateUsed(self.response, "home.html")

    # testing if html contains specified text
    def test_homepage_contains_correct_html(self):
        url = reverse("home")
        self.response = self.client.get(url)
        self.assertContains(self.response, "BESTSELLERS")

    # testing if html does not contain specified text
    def test_homepage_does_not_contain_incorrect_html(self):
        url = reverse("home")
        self.response = self.client.get(url)
        self.assertNotContains(self.response, "It's not a correct page")

    # test home page view
    def test_home_page(self):
        url = reverse("home")
        self.response = self.client.get(url)
        self.assertEqual(f"{self.book.title}", "Magic Mike")
        self.assertQuerysetEqual(
            list(self.book.authors.all()), list(Author.objects.all())
        )  # this test only works cause there are only 2 authors
        # TODO procure a queryset that contains both authors used

    def test_books_list_view(self):
        response = self.client.get(reverse("find_books"))
        self.assertEqual(response.status_code, 302)
        self.assertContains(response, "Magic Mike")
        self.assertTemplateUsed(response, "books/find_books.html")

    # test book detail page and access to it for regular user
    def test_book_detail_view_for_user(self):
        response = self.client.get(self.book.get_absolute_url())
        no_response = self.client.get("/books/12345/")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(no_response.status_code, 404)
        self.assertContains(response, "Magic Mike")
        self.assertTemplateUsed(response, "books/book_detail.html")

    # test book detail page and access to it for staff members
    def test_book_detail_view_for_staff_member(self):
        response = self.client.get(self.book.get_absolute_url())
        no_response = self.client.get("/books/12345/")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(no_response.status_code, 404)
        self.assertContains(response, "Magic Mike")
        self.assertTemplateUsed(response, "books/book_detail.html")

    # TODO: test reservation feature

    # TODO: test borrowing feature

    # TODO: test returning feature

    # TODO: combine above tests and see if the events are generated and saved
