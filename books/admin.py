from django.contrib import admin

from .models import Book, Author, Copy, Event


class AuthorAdmin(admin.ModelAdmin):
    list_display = ("name",)


class BookAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "get_authors",
        "published_date",
        "page_count",
    )

    # function to get all authors listed
    # Remediation to The value of 'list_display[1]' must not be a
    # ManyToManyField.
    def get_authors(self, obj):
        return "\n".join([str(p) for p in obj.authors.all()])


class CopyAdmin(admin.ModelAdmin):
    list_display = (
        "book",
        "holder",
        "reserved_for",
        "state",
    )


class EventAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "borrowed_book",
        "borrow_date",
        "return_date",
    )


admin.site.register(Author, AuthorAdmin)
admin.site.register(Book, BookAdmin)
admin.site.register(Copy, CopyAdmin)
admin.site.register(Event, EventAdmin)
