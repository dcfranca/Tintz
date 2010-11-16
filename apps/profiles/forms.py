# -*- coding: iso-8859-1 -*-
from django import forms
from profiles.models import Profile, AccountType

class ProfileForm(forms.ModelForm):
    first_name = forms.CharField(label=u'Nome', required=True)
    last_name = forms.CharField(label=u'Sobrenome', required=True)
    about = forms.CharField(label=u'Sobre', widget=forms.Textarea,  required=False)
    interests = forms.CharField(label=u'Interesses', widget=forms.Textarea,  required=False)
    birth_date = forms.DateField(('%d/%m/%Y',), label=(u'Data Nasc.(dd/mm/aaaa)'),  widget=forms.DateTimeInput(format='%d/%m/%Y'), required=True)
    location = forms.CharField(label=u'Cidade',  required=False)
    state    = forms.ChoiceField(label=u'Estado', widget=forms.Select, choices=Profile.STATE_CHOICE,  required=False)
    country  = forms.CharField(label=u'País', required=False)
    website  = forms.URLField(label=u'Website', required=False)

    class Meta:
        model = Profile
        exclude = ('user','age')

