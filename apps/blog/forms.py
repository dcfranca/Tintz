# -*- coding: iso-8859-1 -*-
from datetime import datetime
from django import forms
from django.utils.translation import ugettext_lazy as _

from blog.models import Post

class BlogForm(forms.ModelForm):
    
    title = forms.CharField( label=_(u'Título') )
    body  = forms.CharField( label=_(u'Texto'), widget=forms.Textarea(attrs={'rows':'100','cols':'100'}))
    allow_comments  = forms.BooleanField(label=_(u'Permitir Comentários'), initial=True,  required=False)
    
    class Meta:
        model = Post
        exclude = ('author', 'slug','creator_ip', 'tease', 'status', 'created_at', 'markup', 'updated_at', 'publish')
    
    def __init__(self, user=None, *args, **kwargs):
        self.user = user
        super(BlogForm, self).__init__(*args, **kwargs)
    
    def clean_slug(self):
        if not self.instance.pk:
            if Post.objects.filter(author=self.user, created_at__month=datetime.now().month, created_at__year=datetime.now().year, slug=self.cleaned_data['slug']).count():
                raise forms.ValidationError(u'Este campo deve ser único para o usuário, ano e mês.')
            return self.cleaned_data['slug']
        try:
            post = Post.objects.get(author=self.user, created_at__month=self.instance.created_at.month, created_at__year=self.instance.created_at.year, slug=self.cleaned_data['slug'])
            if post != self.instance:
                raise forms.ValidationError(u'Este campo deve ser único para o usuário, ano e mês.')
        except Post.DoesNotExist:
            pass
        return self.cleaned_data['slug']
