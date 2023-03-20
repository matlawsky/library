from django.urls import reverse_lazy
from django.db.models import Q
from .forms import AddBookForm, CopyReservationForm, CopyManagementForm
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.views.generic.edit import FormMixin
from .models import Book, Copy, Author, Event

# main page view
class HomePageView(ListView):
    model = Book
    context_object_name = "books_list"
    template_name = "home.html"


# view for searching for books
class FindBooksView(ListView):
    model = Book
    context_object_name = "books_list"
    template_name = "books/find_books.html"

    def get_queryset(self):
        query = self.request.GET.get("q")
        # problem here since every time there will be an backend query running
        # caching would be helpful here
        if not query:
            query = ""
        return Book.objects.filter(
            Q(title__icontains=query) | Q(subtitle__icontains=query)
        )


@method_decorator(staff_member_required, name="dispatch")
@method_decorator(login_required, name="dispatch")
class UsersSearchView(ListView):
    model = Copy
    template_name = "books/borrow_return_copy.html"

    def get_queryset(self):
        query = self.request.GET.get("q")
        # problem here since every time there will be an backend query running
        # caching would be helpful here

        if not query:
            query = ""
        if "%40" in query:
            query.replace("%40", "@")
        return Copy.objects.filter(
            Q(reserved_for__email__exact=query) | Q(holder__email__exact=query)
        )


@method_decorator(login_required, name="dispatch")
class BookDetailView(LoginRequiredMixin, DetailView):
    model = Book
    context_object_name = "book"
    template_name = "books/book_detail.html"
    login_url = "account_login"


@method_decorator(login_required, name="dispatch")
class CopyDetailView(LoginRequiredMixin, DetailView):
    model = Copy
    context_object_name = "copy"
    template_name = "books/copy_detail.html"
    login_url = "account_login"


@method_decorator(staff_member_required, name="dispatch")
@method_decorator(login_required, name="dispatch")
class CreateBookView(LoginRequiredMixin, CreateView):
    form_class = AddBookForm
    context_object_name = "book"
    template_name = "books/add_book.html"
    login_url = "account_login"

    # redirect to newely created object
    def get_success_url(self):
        success_url = reverse_lazy("book_detail", kwargs={"pk": self.object.id})
        return success_url

    def form_valid(self, form):
        Book = form.save()
        names = str(form.cleaned_data["authors"]).split(";")
        for name in names:
            author = Author.objects.get_or_create(name=name)
            Book.authors.add(author[0])

        number_of_copies = form.cleaned_data["number_of_copies"]
        while number_of_copies != 0:
            Book.add_new_copy()
            number_of_copies -= 1
        return super().form_valid(form)


@method_decorator(staff_member_required, name="dispatch")
@method_decorator(login_required, name="dispatch")
class CopyManagementView(LoginRequiredMixin, UpdateView):
    model = Copy
    form_class = CopyManagementForm
    template_name = "books/manage_copy.html"
    login_url = "account_login"

    def form_valid(self, form):
        action = form.cleaned_data.get("book_copy_decision")
        if "borrow" == action:
            self.object.borrow_copy(self.request.user)
        elif "return" == action:
            self.object.return_copy(self.request.user)
        elif "cancel" == action:
            self.object.cancel_reservation(self.request.user)
        return super().form_valid(form)


@method_decorator(login_required, name="dispatch")
class CopyReservationView(LoginRequiredMixin, UpdateView):
    model = Copy
    form_class = CopyReservationForm
    template_name = "books/reserve_book.html"
    login_url = "account_login"

    def form_valid(self, form):
        if "make" in self.request.POST:
            self.object.reserve_copy(self.request.user)
        elif "cancel" in self.request.POST:
            self.object.cancel_reservation(self.request.user)

        return super().form_valid(form)


@method_decorator(login_required, name="dispatch")
class MyBooksListView(LoginRequiredMixin, ListView):
    model = Copy
    template_name = "books/my_books_list.html"
    login_url = "account_login"

    def get_context_data(self, *args, **kwargs):
        context = super(MyBooksListView, self).get_context_data(*args, **kwargs)
        context["my_reserved_copies"] = Copy.objects.filter(
            reserved_for=self.request.user
        )
        context["my_borrowed_copies"] = Copy.objects.filter(holder=self.request.user)
        return context


@method_decorator(staff_member_required, name="dispatch")
@method_decorator(login_required, name="dispatch")
class AllEventsView(LoginRequiredMixin, ListView, FormMixin):
    model = Event
    template_name = "books/books_list.html"
    login_url = "account_login"
