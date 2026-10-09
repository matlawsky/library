from django import forms
from .models import Author, Book, Copy


COPY_MANAGEMENT_CHOICES = [
    ("borrow", "Borrow the book"),
    ("return", "Return the book"),
    ("cancel", "Cancel reservation"),
]


class DateInput(forms.DateInput):
    input_type = "date"


class AddBookForm(forms.ModelForm):
    number_of_copies = forms.IntegerField(initial=0, min_value=0, max_value=100)
    page_count = forms.IntegerField(min_value=1)
    authors = forms.CharField()
    image_url = forms.URLField(widget=forms.HiddenInput(), required=False)

    def clean_authors(self):
        value = self.cleaned_data["authors"]
        if not any(n.strip() for n in value.split(";")):
            raise forms.ValidationError("Provide at least one author.")
        limit = Author._meta.get_field("name").max_length
        if any(len(name.strip()) > limit for name in value.split(";")):
            raise forms.ValidationError(f"Each author must have at most {limit} characters.")
        return value

    class Meta:
        model = Book
        fields = (
            "title",
            "subtitle",
            "description",
            "published_date",
            "page_count",
        )
        widgets = {
            "published_date": DateInput(),
        }


class CopyReservationForm(forms.ModelForm):
    class Meta:
        model = Copy
        exclude = ("state", "user", "holder", "reserved_for", "book")


class CopyManagementForm(forms.ModelForm):
    book_copy_decision = forms.CharField(
        label="What would you like to do with that reserved book?",
        widget=forms.RadioSelect(choices=COPY_MANAGEMENT_CHOICES),
    )
    state = forms.CharField(
        max_length=254,
        widget=forms.Textarea(attrs={"rows": 7, "cols": 40}),
    )

    class Meta:
        model = Copy
        exclude = (
            "user",
            "holder",
            "reserved_for",
            "book",
        )
        fields = ["state", "book_copy_decision"]
