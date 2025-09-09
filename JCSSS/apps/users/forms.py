# from django import forms
# from django.contrib.auth.forms import UserCreationForm
# from .models import CustomUser

# from django import forms

# class MyForm(forms.Form):
#     phone_number = forms.RegexField(
#         regex=r'^\d{10}$',   # must be exactly 10 digits
#         error_messages={'invalid': "Enter a valid 10-digit phone number."},
#         widget=forms.TextInput(
#             attrs={
#                 "class": "form-control",
#                 "placeholder": "Enter 10-digit phone number",
#                 "pattern": "[0-9]{10}",   # frontend HTML validation
#                 "title": "Enter a 10-digit number"
#             }
#         )
#     )

# from django.core.validators import RegexValidator


# from django import forms
# from django.core.validators import RegexValidator
# from .models import CustomUser


# class CustomUserSignupForm(forms.ModelForm):
#     first_name = forms.CharField(
#         max_length=30,
#         validators=[RegexValidator(
#             regex=r'^[A-Za-z]+$',
#             message="First name must contain only letters."
#         )],
#         widget=forms.TextInput(attrs={
#             "class": "form-control",
#             "placeholder": "First Name",
#             "pattern": "^[A-Za-z]+$",     # ✅ blocks invalid input in UI
#             "title": "Only letters allowed"  # tooltip on hover
#         })
#     )

#     last_name = forms.CharField(
#         max_length=30,
#         validators=[RegexValidator(
#             regex=r'^[A-Za-z]+$',
#             message="Last name must contain only letters."
#         )],
#         widget=forms.TextInput(attrs={
#             "class": "form-control",
#             "placeholder": "Last Name",
#             "pattern": "^[A-Za-z]+$",     # ✅ UI restriction
#             "title": "Only letters allowed"
#         })
#     )

#     class Meta:
#         model = CustomUser
#         fields = ["first_name", "last_name", "email", "phone_number", "password"]




# class CustomUserSignupForm(UserCreationForm):
#     class Meta:
#         model = CustomUser
#         fields = [
#             "first_name",
#             "last_name",
#             "email",
#             "phone_number",
#             "designation",
#             "command_name",
#             "password1",
#             "password2",
#         ]
#         widgets = {
#             "first_name": forms.TextInput(attrs={"class": "form-control", "placeholder": "First Name"}),
#             "last_name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Last Name"}),
#             "email": forms.EmailInput(attrs={"class": "form-control", "placeholder": "Email"}),
#             # "phone_number": forms.TextInput(attrs={"class": "form-control", "placeholder": "Phone Number"}),
#             "designation": forms.TextInput(attrs={"class": "form-control", "placeholder": "Designation"}),
#             "command_name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Command Name", "autocomplete":"off"}),
#         }

#     phone_number = forms.CharField(
#     widget=forms.NumberInput(
#         attrs={
#             "class": "form-control",
#             "placeholder": "Enter phone number",
#             "autocomplete": "off"
#         }
#     )
# )

#     password1 = forms.CharField(
#         label="Password",
#         strip=False,
#         widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "Password"}),
#     )
#     password2 = forms.CharField(
#         label="Confirm Password",
#         strip=False,
#         widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "Confirm Password"}),
#     )
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.validators import RegexValidator
from .models import CustomUser


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
