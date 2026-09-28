from django import forms

from .models import Comment, Subscriber


class CommentForm(forms.ModelForm):
    # Honeypot: real visitors never see or fill this field.
    website = forms.CharField(required=False, widget=forms.HiddenInput)

    class Meta:
        model = Comment
        fields = ("name", "email", "body")
        widgets = {
            "name": forms.TextInput(attrs={"autocomplete": "name"}),
            "email": forms.EmailInput(attrs={"autocomplete": "email"}),
            "body": forms.Textarea(attrs={"rows": 5}),
        }
        help_texts = {"email": "No se publica."}

    def clean_website(self):
        if self.cleaned_data["website"]:
            raise forms.ValidationError("Solicitud no válida.")
        return ""


class SubscribeForm(forms.Form):
    email = forms.EmailField(
        label="Correo",
        widget=forms.EmailInput(attrs={"placeholder": "nombre@empresa.co", "autocomplete": "email"}),
    )
    source = forms.ChoiceField(choices=Subscriber.Source.choices, required=False, widget=forms.HiddenInput)
    diagnosis = forms.JSONField(required=False, widget=forms.HiddenInput)


class SearchForm(forms.Form):
    q = forms.CharField(
        label="Buscar",
        max_length=100,
        required=False,
        widget=forms.SearchInput(attrs={"placeholder": "Buscar artículos"}),
    )
