# -*- coding: iso-8859-1 -*-
from django import forms
from datetime import datetime
from django.utils.translation import ugettext_lazy as _
from publications.models import Publication

class PublicationUploadForm(forms.ModelForm):

    title = forms.CharField(label=u'Título', max_length=300)
    file_name = forms.FileField(label=u'Arquivo')
    description = forms.CharField(label=u'Descrição', widget=forms.Textarea, max_length=1024)
    category    = forms.ChoiceField(label=u'Categoria', widget=forms.Select,  choices=Publication.CATEGORY_CHOICE)
    rated       = forms.ChoiceField(label=u'Classificação', widget=forms.Select,  choices=Publication.RATED_CHOICE)
    language    = forms.ChoiceField(label=u'Idioma', widget=forms.Select, choices=Publication.LANG_CHOICE)
    is_public   = forms.BooleanField(label=u'Publico', required=False)    
    allow_comments  = forms.BooleanField(label=u'Permitir Comentários', required=False,  initial=True)
    
    rated.widget.attrs["onchange"]="enable_public()" 

    class Meta:
        model = Publication
        exclude = ('author','date_added', 'nr_pages', 'rate', 'status', 'views')

    def __init__(self, user=None, *args, **kwargs):
        self.user = user
        super(PublicationUploadForm, self).__init__(*args, **kwargs)

class PublicationEditForm(forms.ModelForm):

    description = forms.CharField(label=u'Descrição', widget=forms.Textarea, max_length=1024)
    language    = forms.ChoiceField(label=u'Idioma', widget=forms.Select, choices=Publication.LANG_CHOICE)
    category    = forms.ChoiceField(label=u'Categoria', widget=forms.Select,  choices=Publication.CATEGORY_CHOICE)
    rated       = forms.ChoiceField(label=u'Classificação', widget=forms.Select,  choices=Publication.RATED_CHOICE)
    is_public   = forms.BooleanField(label=u'Publico', required=False, initial=False)
    allow_comments  = forms.BooleanField(label=u'Permitir Comentários', required=False,  initial=True)
    
    rated.widget.attrs["onchange"]="enable_public()" 

    class Meta:
        model = Publication
        exclude = ('title','file_name','author','date_added', 'nr_pages', 'rate', 'status', 'views')

    def __init__(self, user=None, *args, **kwargs):
        self.user = user
        super(PublicationEditForm, self).__init__(*args, **kwargs)


