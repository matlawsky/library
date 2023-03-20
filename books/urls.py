# books/urls.py
from django.urls import path
from .views import (
    HomePageView,
    FindBooksView,
    UsersSearchView,
    BookDetailView,
    CopyDetailView,
    CreateBookView,
    CopyManagementView,
    CopyReservationView,
    MyBooksListView,
    AllEventsView,
)


urlpatterns = [
    path("", HomePageView.as_view(), name="home"),
    path("find/", FindBooksView.as_view(), name="find_books"),
    path("mybooks/", MyBooksListView.as_view(), name="mybooks"),
    path("newbook/", CreateBookView.as_view(), name="add_book"),
    path("<uuid:pk>/", BookDetailView.as_view(), name="book_detail"),
    path("borrow/", UsersSearchView.as_view(), name="borrow"),
    path("copy/<int:pk>", CopyDetailView.as_view(), name="copy_detail"),
    path("copy/<int:pk>/manage/", CopyManagementView.as_view(), name="copy_manage"),
    path(
        "copy/<int:pk>/reserve/",
        CopyReservationView.as_view(),
        name="copy_reserve",
    ),
    path("events/", AllEventsView.as_view(), name="events"),
]
