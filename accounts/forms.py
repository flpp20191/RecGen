from django.contrib.auth.forms import (
    UserCreationForm,
    SetPasswordForm,
    PasswordChangeForm as AuthPasswordChangeForm,
)
from django.contrib.auth.models import User
from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import EmailValidator
from accounts.models import *

class RegisterForm(UserCreationForm):
    username = forms.CharField(label="Username")
    email = forms.EmailField(required=True, label="Email")
    password1 = forms.CharField(widget=forms.PasswordInput, label="Password")
    password2 = forms.CharField(
        widget=forms.PasswordInput, label="Password confirmation"
    )

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]

    def __init__(self, *args, **kwargs):
        super(RegisterForm, self).__init__(*args, **kwargs)

        self.fields["username"].error_messages = {
            "required": "Username required",
            "unique": "User with such name already exists",
            "invalid": "Invalid username",
        }
        self.fields["email"].error_messages = {
            "required": "Email address is required",
            "unique": "This email address is already registered",
            "invalid": "Invalid email address",
        }

        self.fields["password1"].error_messages = {
            "required": "Password is required",
            "password_mismatch": "Passwords do not match",
            "password_too_short": "Password is too short",
            "password_too_common": "Password is too common",
        }

        self.fields["password2"].error_messages = {
            "required": "Password confirmation is required",
            "password_mismatch": "Passwords do not match",
        }

    def clean_email(self):
        email = self.cleaned_data.get("email")
        # email restriction to certain domains
        '''
        if not email.endswith(("@example.com", "@test.gov.com")):
            raise forms.ValidationError(
                "To register, you must use an <domain> address."
            )
        '''
        return email

    def clean(self):
        super().clean()
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            self.add_error("password2", "Passwords do not match")

class ResetPasswordEmailForm(forms.Form):
    email = forms.EmailField(
        label="Email",
        max_length=254,
        error_messages={
            'required': 'This field is required.',
            'invalid': 'Please enter a valid email address.' 
        }
    )

    def clean_email(self):
        email = self.cleaned_data.get('email')
        email_validator = EmailValidator('Please enter a valid email address.')
        try:
            email_validator(email)
        except ValidationError:
            raise forms.ValidationError('Please enter a valid email address.')
        return email

class SetNewPasswordForm(forms.Form):
    new_password1 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={"class": "form-control", "placeholder": "New password"}
        ),
        max_length=64,
        label="New password",
    )
    new_password2 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={"class": "form-control", "placeholder": "Confirm new password"}
        ),
        max_length=64,
        label="Confirm new password",
    )

    def __init__(self, *args, user=None, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        new_password1 = cleaned_data.get("new_password1")
        new_password2 = cleaned_data.get("new_password2")

        if new_password1 != new_password2:
            raise forms.ValidationError(
                "Passwords do not match. Please ensure both passwords are identical."
            )

    def save(self, commit=True):
        password = self.cleaned_data["new_password1"]
        self.user.set_password(password)
        if commit:
            self.user.save()
        return self.user

class CustomPasswordChangeForm(AuthPasswordChangeForm):
    error_messages = {
        'password_incorrect': "The old password entered is incorrect. Please try again.",
        'password_mismatch': "Passwords do not match.",
        'password_similar': "The new password cannot be the same as the old password.",
        'password_too_short': "The password must be at least 8 characters long.",
        'password_missing_number': "The password must contain at least one digit.",
        'password_missing_letter': "The password must contain at least one alphabet character.",
        'password_missing_lowercase': "The password must contain at least one lowercase letter.",
        'password_missing_uppercase': "The password must contain at least one uppercase letter.",
        'null': "This field cannot be empty.",
        'blank': "This field is required.",
        'invalid': "Invalid value.",
        'invalid_choice': "Invalid choice.",
        'unique': "This value already exists.",
        'unique_for_date': "This value already exists for this date.",
    }

    def __init__(self, *args, **kwargs):
        super(CustomPasswordChangeForm, self).__init__(*args, **kwargs)
        for fieldname in ['old_password', 'new_password1', 'new_password2']:
            self.fields[fieldname].widget = forms.PasswordInput(attrs={
                'class': 'form-control',
            })
            self.fields[fieldname].error_messages = {
                'required': "This field is required.",
                'password_mismatch': self.error_messages['password_mismatch'],
                'password_too_short': self.error_messages['password_too_short'],
                'password_missing_number': self.error_messages['password_missing_number'],
                'password_missing_letter': self.error_messages['password_missing_letter'],
                'password_missing_lowercase': self.error_messages['password_missing_lowercase'],
                'password_missing_uppercase': self.error_messages['password_missing_uppercase'],
                'password_incorrect': self.error_messages['password_incorrect'],
                'null': self.error_messages['null'],
                'blank': self.error_messages['blank'],
                'invalid': self.error_messages['invalid'],
            }

    def clean_new_password1(self):
        password1 = self.cleaned_data.get("new_password1")

        if len(password1) < 8:
            raise forms.ValidationError("The password must be at least 8 characters long.")
        if not any(char.isdigit() for char in password1):
            raise forms.ValidationError("The password must contain at least one digit.")
        if not any(char.isalpha() for char in password1):
            raise forms.ValidationError("The password must contain at least one alphabet character.")
        if not any(char.islower() for char in password1):
            raise forms.ValidationError("The password must contain at least one lowercase letter.")
        if not any(char.isupper() for char in password1):
            raise forms.ValidationError("The password must contain at least one uppercase letter.")

        return password1

    def clean_new_password2(self):
        password1 = self.cleaned_data.get("new_password1")
        password2 = self.cleaned_data.get("new_password2")

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords do not match.")
        return password2

    def clean(self):
        cleaned_data = super().clean()
        old_password = cleaned_data.get("old_password")
        new_password1 = cleaned_data.get("new_password1")

        if old_password and new_password1:
            if old_password == new_password1:
                self.add_error("new_password1", "The new password cannot be the same as the old password.")

        return cleaned_data 

class UserForm(forms.ModelForm):
    class Meta:
        model = UserInformation
        fields = [
            "name",
            "address",
            "contact_number",
            "contact_email",
        ]
