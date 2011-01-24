# -*- coding: iso-8859-1 -*-
from django import forms
from profiles.models import Profile, AccountType
import datetime
from django.utils.translation import ugettext_lazy as _, ugettext

class ProfileForm(forms.ModelForm):
    first_name = forms.CharField(label=u'Nome', required=True,
        error_messages = {'required': u'Campo Nome é obrigatório.' })
    last_name = forms.CharField(label=u'Sobrenome', required=True,
        error_messages = {'required': u'Campo Sobrenome é obrigatório.' })
    birth_date = forms.DateField(('%d/%m/%Y',), label=(u'Data Nasc.(dd/mm/aaaa)'),  widget=forms.DateTimeInput(format='%d/%m/%Y'), required=True,
        error_messages = {'required': u'Campo Data Nasc. é obrigatório.', 'invalid':u'Informe uma data válida.' } )

    about = forms.CharField(label=u'Sobre', widget=forms.Textarea,  required=False)
    interests = forms.CharField(label=u'Interesses', widget=forms.Textarea,  required=False)
    location = forms.CharField(label=u'Cidade',  required=False)
    state    = forms.ChoiceField(label=u'Estado', widget=forms.Select, choices=Profile.STATE_CHOICE,  required=False)
    country  = forms.CharField(label=u'País', required=False)
    #website  = forms.URLField(label=u'Website', required=False)

    class Meta:
        model = Profile
        exclude = ('user','age','account_type')

    def clean(self):

        if "birth_date" in self.cleaned_data:
            birth_date = self.cleaned_data["birth_date"]
            if birth_date >= datetime.date.today():
                raise forms.ValidationError(_(u"Data de nascimento maior ou igual a data atual."))

        return self.cleaned_data


