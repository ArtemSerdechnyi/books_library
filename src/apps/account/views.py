from django.contrib.auth import login, get_user_model, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils.functional import SimpleLazyObject
from django.views.generic import CreateView, ListView

from .forms import RegistrationForm, LoginUserForm


def logout_view(request):
    if request.user.is_authenticated:
        logout(request)
    return redirect('library:index')


class RegistrationView(CreateView):
    """
    View for user registration. It uses a RegistrationForm to register users.
    Upon successful registration, the user is logged in and redirected to their account page.
    """
    template_name = 'account/registration.html'
    form_class = RegistrationForm
    success_url = reverse_lazy('account:user_account')

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return super().form_valid(form)

    def get_form_kwargs(self):
        form_kwargs = super().get_form_kwargs()
        form_kwargs['request'] = self.request
        return form_kwargs


class LoginUserView(LoginView):
    """
    View for user login. It uses a LoginUserForm for user authentication.
    Upon successful login, the user is redirected to their account page.
    """
    form_class = LoginUserForm
    template_name = 'account/login.html'
    success_url = reverse_lazy('account:user_account')

    def get_success_url(self):
        return reverse_lazy('account:user_account')


class AccountView(LoginRequiredMixin, ListView):
    """
    View for user account page.
    """
    model = get_user_model()
    template_name = 'account/account.html'
    context_object_name = 'user'
    redirect_unauthenticated_user = True
    redirect_url = reverse_lazy('account:login')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user: SimpleLazyObject = self.request.user
        context['user'] = user
        return context
