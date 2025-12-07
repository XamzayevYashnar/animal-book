# animals/forms.py
from django import forms
from .models import Shelter

class ShelterForm(forms.ModelForm):
    class Meta:
        model = Shelter
        # Faqat modelda mavjud fieldlarni qo'ying
        fields = '__all__'  # yoki
        # fields = ['name', 'phone_number', 'email', 'description', 'image', 'website'] - modelda bor fieldlar
        
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Boshpana nomi'
            }),
            'phone_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+998 XX XXX XX XX'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'email@example.com'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Boshpana haqida batafsil ma\'lumot...'
            }),
            'website': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://example.com'
            }),
        }