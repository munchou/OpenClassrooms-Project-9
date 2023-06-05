from django import forms
from django.contrib.auth.models import User


from .models import Profile


class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)


class UserRegistrationForm(forms.ModelForm):
    username = forms.CharField(label="Username")
    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput,
        required=True)
    confirm_password = forms.CharField(
        label='Confirm password',
        widget=forms.PasswordInput,
        required=True)

    class Meta:
        model = User
        fields = ["username"]

    def check_password(self):
        cleaned_data = super(UserRegistrationForm, self).clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")
        if password != confirm_password:
            raise forms.ValidationError("Passwords don't match.")
        
        return cleaned_data


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ["profile_photo"]
        profile_photo = forms.ImageField(widget=forms.FileInput)


class SubscribeForm(forms.Form):
    followed_user = forms.CharField(label=False, required=True)
