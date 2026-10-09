from concurrent.futures import ThreadPoolExecutor
from threading import Barrier
from datetime import date
from unittest import skipUnless
from django.test import TransactionTestCase
from django.db import connection, close_old_connections
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from books.models import Book, Copy, Event
from books.services.circulation import transition

@skipUnless(connection.vendor == "postgresql", "Requires real PostgreSQL row locks")
class ReservationRaceTests(TransactionTestCase):
    def test_only_one_reservation_wins(self):
        users=[get_user_model().objects.create_user(f"u{i}",f"u{i}@example.com","Strong-pass-123") for i in range(2)]
        book=Book.objects.create(title="Race",subtitle="Race",description="Race",published_date=date(2020,1,1),page_count=1)
        copy=Copy.objects.create(book=book,state="New")
        barrier=Barrier(2)
        def reserve(uid):
            close_old_connections()
            try:
                user=get_user_model().objects.get(pk=uid); barrier.wait(timeout=10)
                try: transition(copy.pk,user,"reserve"); return True
                except ValidationError: return False
            finally: close_old_connections()
        with ThreadPoolExecutor(max_workers=2) as pool: results=list(pool.map(reserve,[u.pk for u in users]))
        self.assertEqual(sorted(results),[False,True])
        self.assertEqual(Event.objects.count(),0)