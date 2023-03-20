from django.urls import reverse_lazy
from django.views import generic
from django.contrib.auth.models import User
from .forms import CustomUserChangeForm
from .forms import CustomUserCreationForm


class SignupPageView(generic.CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy("login")
    template_name = "registration/signup.html"


class MyAccountView(generic.UpdateView):
    form_class = CustomUserChangeForm
    model = User
    template_name = "account/myaccount.html"

    def get_object(self, queryset=None):
        return self.request.user
