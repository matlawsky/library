from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views import generic
from django.contrib.auth.models import User
from .forms import ProfileForm, CustomUserChangeForm, CustomUserCreationForm


class SignupPageView(generic.CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy("login")
    template_name = "registration/signup.html"


class MyAccountView(LoginRequiredMixin, generic.UpdateView):
    form_class = ProfileForm
    template_name = "account/myaccount.html"
    success_url = reverse_lazy("myaccount")
    login_url = "account_login"
    def get_object(self, queryset=None):
        return self.request.user