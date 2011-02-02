# -*- coding: iso-8859-1 -*-
from django import forms
from tintzsettings.models import TintzSettings
from emailconfirmation.models import EmailAddress
from avatar.models import avatar_file_path, Avatar
from django.utils.translation import ugettext_lazy as _, ugettext

class TintzSettingsForm(forms.ModelForm):

    avatar_file = forms.FileField(label=_('Avatar'), required=False)
    email       = forms.CharField(label=_('Email'), widget=forms.TextInput(attrs={'readonly':'readonly'}), required=True)

    email_follow   = forms.BooleanField(label=_(u'Seguidores'), required=False)
    email_publication   = forms.BooleanField(label=_(u'Publicações'), required=False)
    email_post   = forms.BooleanField(label=_(u'Posts'), required=False)

    oldpassword = forms.CharField(label=_("Senha Atual"), widget=forms.PasswordInput(render_value=False), required=False)
    password1 = forms.CharField(label=_("Nova Senha"), widget=forms.PasswordInput(render_value=False), required=False)
    password2 = forms.CharField(label=_("Redigite Nova Senha"), widget=forms.PasswordInput(render_value=False), required=False)

    class Meta:
        model = TintzSettings
        exclude = ('user',)

    def __init__(self, user=None, *args, **kwargs):
        self.user = user
        
	instance = getattr(self, 'instance', None)
        if instance and instance.id:
            self.fields['email'].widget.attrs['readonly'] = True
        super(TintzSettingsForm, self).__init__(*args, **kwargs)

    def clean_oldpassword(self):
        if "oldpassword" in self.cleaned_data:
            oldpassword = self.cleaned_data.get("oldpassword")
            if len(oldpassword) > 0:
                if not self.user.check_password(oldpassword):
                    raise forms.ValidationError(_(u"Senha atual incorreta."))
        return self.cleaned_data["oldpassword"]

    def clean_password2(self):
        if "password1" in self.cleaned_data and "password2" in self.cleaned_data and "oldpassword" in self.cleaned_data:
            oldpassword = self.cleaned_data["oldpassword"]
            password1 = self.cleaned_data["password1"]
            password2 = self.cleaned_data["password2"]	
    
            if len(password1) == 0 and len(oldpassword) > 0:
                raise forms.ValidationError(_(u"Nova Senha vazia."))
            if password1 != password2:
                raise forms.ValidationError(_(u"Senhas não conferem."))
        return self.cleaned_data["password2"]

    def save( self, request ):
        my_email = self.cleaned_data["email"]

        if len(my_email) == 0:
            raise forms.ValidationError(_(u"Favor preencher o email."))

        if my_email != EmailAddress.objects.get_primary(request.user).email:
            EmailAddress.objects.add_email( request.user, my_email )
            new_email = EmailAddress.objects.get(
                           user=request.user,
                            email=my_email,
                        )
            new_email.set_as_primary()
        try:
            tintzSettings = TintzSettings.objects.get(user=request.user)
        except:
            tintzSettings = TintzSettings()

        tintzSettings.email_follow = self.cleaned_data["email_follow"]
        tintzSettings.email_publication = self.cleaned_data["email_publication"]
        tintzSettings.email_post = self.cleaned_data["email_post"]
        tintzSettings.user = request.user

        #try:
        oldpassword = self.cleaned_data["oldpassword"]
        password2 =  self.cleaned_data["password2"]
        if len(oldpassword) > 0 and len(password2) > 0:
            self.user.set_password(password2)
            self.user.save()
            request.user.message_set.create(message=ugettext(u"Senha alterada com sucesso."))
        #except forms.ValidationError:
        #raise forms.ValidationError(_(u"Senhas não conferem."))
        #except:
        #    raise forms.ValidationError(_(u"Erro ao atualizar senha."))

        tintzSettings.save()

        self.change_avatar(request)

    def change_avatar(self, request):
        avatars = Avatar.objects.filter(user=request.user).order_by('-primary')
        if avatars.count() > 0:
            avatar = avatars[0]

        if 'avatar_file' in request.FILES:
            path = avatar_file_path(user=request.user,filename=request.FILES['avatar_file'].name)
            avatar = Avatar(
                user = request.user,
                primary = True,
                avatar = path,
            )
            new_file = avatar.avatar.storage.save(path, request.FILES['avatar_file'])
            avatar.save()





