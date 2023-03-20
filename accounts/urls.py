from django.urls import path
from .views import SignupPageView, MyAccountView

urlpatterns = [
    path("signup/", SignupPageView.as_view(), name="signup"),
    # path("", MyAccountView.as_view(), name="myaccount"),
]
