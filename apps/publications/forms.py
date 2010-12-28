# -*- coding: iso-8859-1 -*-
from django import forms
from datetime import datetime
from django.utils.translation import ugettext_lazy as _
from publications.models import Publication, PublicationReportAbuse

class PublicationUploadForm(forms.ModelForm):

    title = forms.CharField(label=u'Título', max_length=300,
            error_messages = {'required': u'Campo Título é obrigatório.' } )
    file_name = forms.FileField(label=u'Arquivo',
            error_messages = {'required': u'Campo Arquivo é obrigatório.' } )
    description = forms.CharField(label=u'Descrição', widget=forms.Textarea(attrs={'rows':2, 'cols':20}), max_length=1024,
            error_messages = {'required': u'Campo Descrição é obrigatório.' } )
    category    = forms.ChoiceField(label=u'Categoria', widget=forms.Select,  choices=Publication.CATEGORY_CHOICE,
            error_messages = {'required': u'Campo Categoria é obrigatório.' } )
    rated       = forms.ChoiceField(label=u'Classificação', widget=forms.Select,  choices=Publication.RATED_CHOICE,
            error_messages = {'required': u'Campo Classificação é obrigatório.' } )
    language    = forms.ChoiceField(label=u'Idioma', widget=forms.Select, choices=Publication.LANG_CHOICE,
            error_messages = {'required': u'Campo Idioma é obrigatório.' } )
    is_public   = forms.BooleanField(label=u'Publico', required=False)
    allow_comments  = forms.BooleanField(label=u'Permitir Comentários', required=False,  initial=True)
    
    rated.widget.attrs["onchange"]="enable_public()" 

    class Meta:
        model = Publication
        exclude = ('author','date_added', 'nr_pages', 'rate', 'status', 'views', 'images_ext')

    def __init__(self, user=None, *args, **kwargs):
        self.user = user
        super(PublicationUploadForm, self).__init__(*args, **kwargs)

class PublicationEditForm(forms.ModelForm):

    title       = forms.CharField(label=u'Título', max_length=300,
                  error_messages = {'required': u'Campo Título é obrigatório.' } )
    description = forms.CharField(label=u'Descrição', widget=forms.Textarea, max_length=1024)
    language    = forms.ChoiceField(label=u'Idioma', widget=forms.Select, choices=Publication.LANG_CHOICE)
    category    = forms.ChoiceField(label=u'Categoria', widget=forms.Select,  choices=Publication.CATEGORY_CHOICE)
    rated       = forms.ChoiceField(label=u'Classificação', widget=forms.Select,  choices=Publication.RATED_CHOICE)
    is_public   = forms.BooleanField(label=u'Publico', required=False, initial=False)
    allow_comments  = forms.BooleanField(label=u'Permitir Comentários', required=False,  initial=True)
    
    rated.widget.attrs["onchange"]="enable_public()" 

    class Meta:
        model = Publication
        exclude = ('file_name','author','date_added', 'nr_pages', 'rate', 'status', 'views','images_ext')

    def __init__(self, user=None, *args, **kwargs):
        self.user = user
        super(PublicationEditForm, self).__init__(*args, **kwargs)

class PublicationReportAbuseForm(forms.ModelForm):

    message = forms.CharField(label=u'Mensagem', widget=forms.Textarea, max_length=1024)

    class Meta:
        model = PublicationReportAbuse
        exclude = ('publication','reporter')

    def __init__(self, user=None, *args, **kwargs):
        self.user = user
        super(PublicationReportAbuseForm, self).__init__(*args, **kwargs)        
