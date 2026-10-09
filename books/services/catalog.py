from django.db import transaction
from books.models import Author, Copy

@transaction.atomic
def create_book(form):
    book = form.save()
    names = list(dict.fromkeys(n.strip() for n in form.cleaned_data["authors"].split(";") if n.strip()))
    for name in names:
        author, _ = Author.objects.get_or_create(name=name)
        book.authors.add(author)
    Copy.objects.bulk_create([Copy(book=book,state="New") for _ in range(form.cleaned_data["number_of_copies"])])
    return book