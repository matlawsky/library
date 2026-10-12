from django.db.models import Q, Exists, OuterRef
from django.views.generic import ListView
from books.models import Book, Copy

class CatalogView(ListView):
    model = Book
    context_object_name = "books_list"
    template_name = "books/find_books.html"
    paginate_by = 20
    def get_queryset(self):
        query = self.request.GET.get("q", "").strip()[:200]
        books = Book.objects.prefetch_related("authors").filter(Q(title__icontains=query)|Q(subtitle__icontains=query)|Q(authors__name__icontains=query)).distinct()
        available = Copy.objects.filter(book_id=OuterRef("pk"),holder__isnull=True,reserved_for__isnull=True)
        books = books.annotate(has_available=Exists(available))
        if self.request.GET.get("available") == "1": books = books.filter(has_available=True)
        order = {"title":"title", "newest":"-published_date"}.get(self.request.GET.get("sort"),"title")
        return books.order_by(order,"pk")
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        query = self.request.GET.copy(); query.pop("page",None)
        context["query_string"] = query.urlencode()
        return context