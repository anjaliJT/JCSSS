
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.validators import RegexValidator
from .models import CustomUser
from django.utils.crypto import get_random_string

class CustomUserSignupForm(UserCreationForm):
    # First Name - letters only
    first_name = forms.CharField(
        max_length=30,
        validators=[RegexValidator(
            regex=r'^[A-Za-z]+$',
            message="First name must contain only letters."
        )],
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "First Name",
            "pattern": "^[A-Za-z]+$",
            "title": "Only letters allowed"
        })
    )

    # Last Name - letters only
    last_name = forms.CharField(
        max_length=30,
        validators=[RegexValidator(
            regex=r'^[A-Za-z]+$',
            message="Last name must contain only letters."
        )],
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Last Name",
            "pattern": "^[A-Za-z]+$",
            "title": "Only letters allowed"
        })
    )

    # Phone Number - exactly 10 digits
    phone_number = forms.CharField(
        validators=[RegexValidator(
            regex=r'^\d{10}$',
            message="Phone number must be exactly 10 digits."
        )],
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Enter 10-digit phone number",
            "pattern": "^[0-9]{10}$",   # frontend validation
            "title": "Enter a valid 10-digit phone number",
            "maxlength": "10"           # extra safety
        })
    )

    # Password fields (with Bootstrap styling)
    password1 = forms.CharField(
        label="Password",
        strip=False,
        widget=forms.PasswordInput(attrs={
            "class": "form-control",
            "placeholder": "Password"
        }),
    )
    password2 = forms.CharField(
        label="Confirm Password",
        strip=False,
        widget=forms.PasswordInput(attrs={
            "class": "form-control",
            "placeholder": "Confirm Password"
        }),
    )

    class Meta:
        model = CustomUser
        fields = [
            "first_name",
            "last_name",
            "email",
            "phone_number",
            "designation",
            "command_name",
            "password1",
            "password2",
        ]
        widgets = {
            "email": forms.EmailInput(attrs={"class": "form-control", "placeholder": "Email"}),
            "designation": forms.TextInput(attrs={"class": "form-control", "placeholder": "Designation"}),
            "command_name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Command Name", "autocomplete": "off"}),
        }


# class OEMUserForm(forms.ModelForm):
#     password1 = forms.CharField(widget=forms.PasswordInput(), required=False)
#     password2 = forms.CharField(widget=forms.PasswordInput(), required=False)


#     class Meta:
#         model = CustomUser
#         fields = [
#         "first_name", "last_name", "email", "phone_number",
#         "certificate_number", "designation", "command_name",
#         "role", "is_active",
#         ]


#     def clean(self):
#         cleaned = super().clean()
#         p1 = cleaned.get("password1")
#         p2 = cleaned.get("password2")


#         if p1 or p2:
#             if p1 != p2:
#                 raise forms.ValidationError("Passwords do not match.")
#             if len(p1) < 8:
#                 raise forms.ValidationError("Password must be at least 8 characters long.")
#             return cleaned


#     def save(self, commit=True, is_update=False):
#         user = super().save(commit=False)
#         pwd = self.cleaned_data.get("password1")


#         if pwd:
#             user.set_password(pwd)
#         elif not is_update:
#             user.set_password(get_random_string(12))


#         if commit:
#             user.save()
#         return user