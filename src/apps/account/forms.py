from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth import get_user_model, authenticate, login


class RegistrationForm(UserCreationForm):
    """
    Form for user registration.
    """
    def __init__(self, request, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = request

    class Meta:
        model = get_user_model()
        fields = ['username', 'password1', 'password2', ]

    def save(self, commit=True):
        """
        Saves the form data. Login user after registration.
        """
        user = super().save(commit=commit)
        if commit:
            auth_user = authenticate(
                username=self.cleaned_data['username'],
                password=self.cleaned_data['password1']
            )
            login(self.request, auth_user)

        return user


class LoginUserForm(AuthenticationForm):
    class Meta:
        models = get_user_model()
        fields = ['username', 'password', ]
