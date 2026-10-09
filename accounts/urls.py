from django.urls import path
from .views import SignupPageView, MyAccountView

urlpatterns = [
    path("signup/", SignupPageView.as_view(), name="signup"),
    path("my/", MyAccountView.as_view(), name="myaccount")
]
