from django import forms

from . import models


class CreateTicket(forms.ModelForm):
    edit_ticket = forms.BooleanField(widget=forms.HiddenInput, initial=True)
    title = forms.CharField(label="Title of the book", max_length=128, required=True)
    description = forms.CharField(max_length=2048, widget=forms.Textarea, required=True)
    image = forms.ImageField(required=True)
    reply = forms.BooleanField(widget=forms.HiddenInput, initial=True)

    class Meta:
        model = models.Ticket
        fields = ["title", "description", "image"]


class DeleteTicket(forms.Form):
    delete_ticket = forms.BooleanField(widget=forms.HiddenInput, initial=True)


class CreateReview(forms.ModelForm):
    edit_review = forms.BooleanField(widget=forms.HiddenInput, initial=True)    
    headline = forms.CharField(label="Title", required=True)
    comment = forms.CharField(label="Comment", max_length=8192, widget=forms.Textarea, required=True)
    rating = forms.ChoiceField(
        initial=3,
        label="Rate this book",
        widget=forms.RadioSelect(attrs={'class': 'inline'}),
        required=True,
        choices=((1, "1 star"),
                 (2, "2 stars"),
                 (3, "3 stars"),
                 (4, "4 stars"),
                 (5, '5 stars')))

    class Meta:
        model = models.Review
        fields = ["headline", "rating", "comment"]


class DeleteReview(forms.Form):
    delete_review = forms.BooleanField(widget=forms.HiddenInput, initial=True)
