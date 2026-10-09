from django.db import models
from accounts import models as am
from django.urls import reverse, reverse_lazy
from django.db.models.signals import post_save
import uuid
import time
from datetime import datetime


class Author(models.Model):
    name = models.CharField(max_length=250)

    def __str__(self) -> str:
        return self.name


class Book(models.Model):
    # authors is a small list of strings
    # two ideas to store that values are:
    # 1
    # compress authors strings into one separated string
    # and save it
    # when reading, decompress it
    # 2
    # create model for Author,
    # and store those values in another table
    # and here use one to many relationship
    # to assign proper values

    # for learning I will go with the second more canonical approach

    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, auto_created=True
    )

    title = models.CharField(max_length=250)
    authors = models.ManyToManyField(Author)
    subtitle = models.CharField(max_length=250)
    description = models.CharField(max_length=254)
    published_date = models.DateField()
    page_count = models.IntegerField()
    image_url = models.URLField(
        default=f"https://picsum.photos/seed/{time.time() % 12345}/200/300"
    )

    def __str__(self) -> str:
        return self.title

    def get_title(self):
        return self.title

    def check_if_authors_none(self):
        if self.authors.exists():
            if self.authors == None:
                return True

            else:
                return False
        else:
            return True

    def get_copies_list(self):
        return Copy.objects.filter(book__pk=self.pk)

    def get_teaser(self):
        return self.description[:100]

    def get_authors_list(self):
        return [p for p in self.authors.all()]

    def get_authors_as_string_in_list(self):
        return [str(p.name) for p in self.authors.all()]

    def get_authors_str(self):
        text = "; ".join(self.get_authors_as_string_in_list())
        if text == "" or text == " ":
            return "Unknown"
        else:
            return text

    def get_first_author(self):
        n = self.get_authors_as_string_in_list()[0]
        return n

    # search for space separated strings in title, subtitle and author fields
    def get_absolute_url(self):
        return reverse_lazy("book_detail", args=[str(self.id)])

    def add_new_copy(self):
        Copy(state="New", book=self).save()


class Copy(models.Model):
    state = models.CharField(max_length=250)
    holder = models.ForeignKey(
        am.CustomUser,
        null=True,
        on_delete=models.SET_NULL,
        blank=True,
        related_name="holder",
    )
    reserved_for = models.ForeignKey(
        am.CustomUser,
        null=True,
        on_delete=models.SET_NULL,
        blank=True,
        related_name="reserved_for",
    )
    book = models.ForeignKey(Book, on_delete=models.PROTECT)

    class Meta:
        constraints = [models.CheckConstraint(check=models.Q(holder__isnull=True) | models.Q(reserved_for__isnull=True), name="copy_not_both_borrowed_reserved")]

    def get_absolute_url(self):
        return reverse("copy_detail", args=[str(self.pk)])

    def get_book_title(self):
        return self.book.get_title

    def get_holder_str(self):
        return str(self.holder)

    def get_state_str(self):
        return str(self.state)

    def is_not_reserved(self):
        if self.reserved_for == None:
            return True
        else:
            return False

    def is_not_borrowed(self):
        if self.holder == None:
            return True
        else:
            return False

    def reserve_copy(self, usr: am.CustomUser):
        if self.is_not_reserved() == True and self.is_not_borrowed() == True:
            self.reserved_for = usr
        else:
            pass

    def cancel_reservation(self, usr: am.CustomUser):
        if self.is_not_reserved() == False:
            if self.reserved_for == usr:
                self.reserved_for = None
            else:
                pass
        else:
            pass

    def borrow_copy(self, usr: am.CustomUser):
        if self.is_not_reserved() == False and self.is_not_borrowed() == True:
            Event.objects.create(
                borrower=usr, borrowed_copy=self, borrow_date=datetime.now()
            )
            self.reserved_for = None
            self.holder = usr
        else:
            pass

    def return_copy(self, usr: am.CustomUser):
        if self.is_not_borrowed() == False and self.is_not_reserved() == True:
            e = Event.objects.get(
                borrowed_copy__exact=self,
                borrower__exact=usr,
                return_date__exact=None,
            )
            e.return_date = datetime.now()
            e.save(update_fields=["return_date"])
            self.holder = None
        else:
            pass


class Event(models.Model):
    borrower = models.ForeignKey(
        am.CustomUser,
        null=True,
        on_delete=models.SET_NULL,
        blank=True,
        related_name="borrower",
    )
    borrowed_copy = models.ForeignKey(
        Copy,
        null=True,
        on_delete=models.PROTECT,
        blank=True,
        related_name="borrowed_copy",
    )
    issued_by = models.ForeignKey(am.CustomUser, null=True, blank=True, on_delete=models.SET_NULL, related_name="issued_loans")
    received_by = models.ForeignKey(am.CustomUser, null=True, blank=True, on_delete=models.SET_NULL, related_name="received_loans")
    borrow_date = models.DateField(auto_now_add=True)
    return_date = models.DateField(null=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["borrowed_copy"], condition=models.Q(return_date__isnull=True, borrowed_copy__isnull=False), name="one_open_loan_per_copy"),
            models.CheckConstraint(check=models.Q(return_date__isnull=True) | models.Q(return_date__gte=models.F("borrow_date")), name="loan_dates_ordered"),
        ]

    def user(self) -> str:
        return str(self.borrower)

    def borrowed_book(self) -> str:
        if self.borrowed_copy == None:
            return str(None)
        return str(self.borrowed_copy.book.title)
