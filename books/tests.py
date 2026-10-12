from datetime import date
from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse
from django.core.exceptions import ValidationError, PermissionDenied
from django.db import IntegrityError, transaction
from .models import Book, Copy, Author, Event
from .forms import AddBookForm, CopyManagementForm
from .services.catalog import create_book
from .services.circulation import transition
from .services.audit import issues
from .metadata import normalize_isbn, parse_publication
from unittest.mock import patch


class LibraryCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        User = get_user_model()
        cls.reader = User.objects.create_user("reader", "reader@example.com", "Strong-pass-123")
        cls.other = User.objects.create_user("other", "other@example.com", "Strong-pass-123")
        cls.staff = User.objects.create_user("staff", "staff@example.com", "Strong-pass-123", is_staff=True)
        cls.staff2 = User.objects.create_user("staff2", "staff2@example.com", "Strong-pass-123", is_staff=True)
        cls.book = Book.objects.create(title="Test book", subtitle="Example", description="Text", published_date=date(2020,1,1), page_count=100)
        cls.copy = Copy.objects.create(book=cls.book, state="New")


class CatalogTests(LibraryCase):
    def test_public_catalog(self):
        for name in ["home", "find_books"]:
            self.assertContains(self.client.get(reverse(name)), "Test book")
    def test_detail_requires_login(self):
        self.assertEqual(self.client.get(self.book.get_absolute_url()).status_code, 302)
    def test_reader_and_staff_detail(self):
        for user in [self.reader, self.staff]:
            self.client.force_login(user)
            self.assertTemplateUsed(self.client.get(self.book.get_absolute_url()), "books/book_detail.html")
    def test_reader_cannot_add_book(self):
        self.client.force_login(self.reader)
        self.assertIn(self.client.post(reverse("add_book"), {}).status_code, [302,403])


class FreshPageTests(LibraryCase):
    def test_changes_are_visible(self):
        self.client.get(reverse("find_books"))
        Book.objects.filter(pk=self.book.pk).update(title="Changed title")
        self.assertContains(self.client.get(reverse("find_books")), "Changed title")


class CopyCreationTests(LibraryCase):
    def test_get_never_creates(self):
        self.client.force_login(self.staff)
        before = Copy.objects.count()
        for _ in range(2): self.client.get(self.book.get_absolute_url())
        self.assertEqual(Copy.objects.count(),before)
    def test_post_only_and_staff_only(self):
        url = reverse("add_copy", args=[self.book.pk])
        self.client.force_login(self.reader)
        self.assertIn(self.client.post(url).status_code,[302,403])
        self.client.force_login(self.staff)
        self.assertEqual(self.client.get(url).status_code,405)
        self.assertEqual(self.client.post(url).status_code,302)
        self.assertEqual(Copy.objects.count(),2)
    def test_csrf_required(self):
        client = Client(enforce_csrf_checks=True); client.force_login(self.staff)
        self.assertEqual(client.post(reverse("add_copy",args=[self.book.pk])).status_code,403)


class AddBookTests(LibraryCase):
    def data(self, count):
        return dict(title="New title", subtitle="Subtitle", description="Text", published_date="2020-01-01", page_count=100, authors=" Alice ; ; Bob ", number_of_copies=count)
    def test_bounds(self):
        for count in [-1,101]: self.assertFalse(AddBookForm(self.data(count)).is_valid())
        for count in [0,1,100]: self.assertTrue(AddBookForm(self.data(count)).is_valid())
    def test_atomic_creation(self):
        form = AddBookForm(self.data(2)); self.assertTrue(form.is_valid())
        with patch("books.services.catalog.Copy.objects.bulk_create", side_effect=RuntimeError("failure")):
            with self.assertRaises(RuntimeError): create_book(form)
        self.assertFalse(Book.objects.filter(title="New title").exists())


class CirculationTests(LibraryCase):
    def test_reader_borrows_and_different_staff_receives(self):
        transition(self.copy.pk,self.reader,"reserve")
        transition(self.copy.pk,self.staff,"borrow")
        loan = Event.objects.get(borrowed_copy=self.copy)
        self.assertEqual(loan.borrower,self.reader)
        transition(self.copy.pk,self.staff2,"return")
        loan.refresh_from_db(); self.copy.refresh_from_db()
        self.assertEqual(loan.received_by,self.staff2)
        self.assertIsNone(self.copy.holder_id)
    def test_staff_cancels_but_other_reader_cannot(self):
        transition(self.copy.pk,self.reader,"reserve")
        with self.assertRaises(PermissionDenied): transition(self.copy.pk,self.other,"cancel")
        transition(self.copy.pk,self.staff,"cancel")
        self.copy.refresh_from_db(); self.assertIsNone(self.copy.reserved_for_id)
    def test_reader_cannot_issue(self):
        transition(self.copy.pk,self.reader,"reserve")
        with self.assertRaises(PermissionDenied): transition(self.copy.pk,self.reader,"borrow")
    def test_event_failure_rolls_back(self):
        transition(self.copy.pk,self.reader,"reserve")
        with patch("books.services.circulation.Event.objects.create",side_effect=RuntimeError("fail")):
            with self.assertRaises(RuntimeError): transition(self.copy.pk,self.staff,"borrow")
        self.copy.refresh_from_db(); self.assertEqual(self.copy.reserved_for_id,self.reader.pk)


class TransitionValidationTests(LibraryCase):
    def test_unknown_action(self):
        self.assertFalse(CopyManagementForm({"state":"New","book_copy_decision":"arbitrary"},instance=self.copy).is_valid())
    def test_stale_reservation_is_rejected(self):
        transition(self.copy.pk,self.reader,"reserve")
        with self.assertRaises(ValidationError): transition(self.copy.pk,self.other,"reserve")
    def test_duplicate_return_is_rejected(self):
        transition(self.copy.pk,self.reader,"reserve"); transition(self.copy.pk,self.staff,"borrow")
        transition(self.copy.pk,self.staff,"return")
        with self.assertRaises(ValidationError): transition(self.copy.pk,self.staff,"return")
        self.assertEqual(Event.objects.count(),1)


class AuditTests(LibraryCase):
    def test_audit_does_not_repair_automatically(self):
        Copy.objects.filter(pk=self.copy.pk).update(holder=self.reader)
        before=list(Copy.objects.values())
        self.assertTrue(list(issues()))
        self.assertEqual(before,list(Copy.objects.values()))


class ConstraintTests(LibraryCase):
    def test_duplicate_open_event_is_rejected(self):
        Event.objects.create(borrowed_copy=self.copy,borrower=self.reader)
        with self.assertRaises(IntegrityError), transaction.atomic():
            Event.objects.create(borrowed_copy=self.copy,borrower=self.other)


class HistoryTests(LibraryCase):
    def test_staff_history(self):
        self.client.force_login(self.staff)
        self.assertContains(self.client.get(reverse("events")),"Loan history")
    def test_reader_denied(self):
        self.client.force_login(self.reader)
        self.assertIn(self.client.get(reverse("events")).status_code,[302,403])


class SearchTests(LibraryCase):
    def test_author_search_has_no_duplicates(self):
        self.book.authors.add(Author.objects.create(name="Alice One"), Author.objects.create(name="Alice Two"))
        response=self.client.get(reverse("find_books"),{"q":"Alice"})
        self.assertEqual(len(response.context["books_list"]),1)
    def test_availability_filter(self):
        transition(self.copy.pk,self.reader,"reserve")
        self.assertContains(self.client.get(reverse("find_books"),{"available":"1"}),"No matching books")


class MetadataTests(TestCase):
    def test_isbn_conversion(self):
        self.assertEqual(normalize_isbn("0-306-40615-2"),"9780306406157")
        with self.assertRaises(ValidationError): normalize_isbn("9780306406158")
    def test_partial_date_is_not_a_fake_day(self):
        self.assertEqual(parse_publication("2020"),("2020",None))
        with self.assertRaises(ValidationError): parse_publication("2020-99")