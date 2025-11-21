from __future__ import absolute_import, unicode_literals

from django.contrib.auth.forms import UserChangeForm, UserCreationForm

from .models import User


class CustomUserChangeForm(UserChangeForm):

    class Meta(UserChangeForm.Meta):
        model = User


class CustomUserCreationForm(UserCreationForm):

    class Meta(UserCreationForm.Meta):
        model = User
        fields = (
            'email',
        )
