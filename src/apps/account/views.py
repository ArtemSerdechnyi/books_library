from django.contrib.auth import login, get_user_model, logout
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
    template_name = 'account/registration.html'
    form_class = RegistrationForm
    success_url = reverse_lazy('account:account')

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return super().form_valid(form)

    def get_form_kwargs(self):
        form_kwargs = super().get_form_kwargs()
        form_kwargs['request'] = self.request
        return form_kwargs


class LoginUserView(LoginView):
    form_class = LoginUserForm
    template_name = 'account/login.html'
    success_url = reverse_lazy('account:user_account')

    def get_success_url(self):
        return reverse_lazy('account:user_account')


class AccountView(ListView):
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

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated and self.redirect_unauthenticated_user:
            return redirect(self.redirect_url)
        return super().dispatch(request, *args, **kwargs)
