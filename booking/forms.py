from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

SPORT_CHOICES = [
    ("", "Todos"),
    ("futsal", "Futsal"),
    ("tenis", "Tênis"),
    ("volei", "Vôlei"),
    ("basquete", "Basquete"),
    ("beach_tennis", "Beach Tennis"),
]

SORT_CHOICES = [
    ("", "Sem ordenação"),
    ("rating", "Avaliação"),
    ("name", "Alfabética (A-Z)"),
]


class ClubFilterForm(forms.Form):
    sport = forms.ChoiceField(choices=SPORT_CHOICES, required=False, label="Esporte")
    name = forms.CharField(required=False, label="Nome do clube")
    min_rating = forms.FloatField(
        required=False,
        label="Avaliação mínima",
        min_value=0,
        max_value=5,
        initial=0,
        widget=forms.NumberInput(attrs={"type": "range", "step": "0.1", "min": "0", "max": "5"}),
    )
    max_rating = forms.FloatField(
        required=False,
        label="Avaliação máxima",
        min_value=0,
        max_value=5,
        initial=5,
        widget=forms.NumberInput(attrs={"type": "range", "step": "0.1", "min": "0", "max": "5"}),
    )
    sort_by = forms.ChoiceField(choices=SORT_CHOICES, required=False, label="Ordenar por")


class SignUpForm(UserCreationForm):
    first_name = forms.CharField(required=False, label="Nome")
    email = forms.EmailField(required=False, label="Email")

    class Meta:
        model = User
        fields = ("username", "first_name", "email", "password1", "password2")
