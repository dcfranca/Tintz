# -*- coding: iso-8859-1 -*-

import re

from django import forms
from django.template.loader import render_to_string
from django.conf import settings
from django.utils.translation import ugettext_lazy as _, ugettext
from django.utils.encoding import smart_unicode
from profiles.models import *

from misc.utils import get_send_mail
send_mail = get_send_mail()

from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User

from emailconfirmation.models import EmailAddress
from account.models import Account

from timezones.forms import TimeZoneField

import logging

alnum_re = re.compile(r'^\w+$')

class LoginForm(forms.Form):

    username = forms.CharField(label=_(u"Usuário"), max_length=30, widget=forms.TextInput(),
                error_messages = {'required': u'Campo obrigatório.' } )
    password = forms.CharField(label=_(u"Senha"), widget=forms.PasswordInput(render_value=False),
                error_messages = {'required': u'Campo obrigatório.' } )
    remember = forms.BooleanField(label=_(u"Lembrar"), required=False)

    user = None

    def clean(self):
        if self._errors:
            return
        user = authenticate(username=self.cleaned_data["username"], password=self.cleaned_data["password"])
        if user:
            if user.is_active:
                self.user = user
            else:
                raise forms.ValidationError(_(u"Esta conta está inativa."))
        else:
            raise forms.ValidationError(_(u"Usuário ou senha incorretos."))
        return self.cleaned_data

    def login(self, request):
        logging.debug("login - step 1")
        if self.is_valid():
            logging.debug("login - step 2")
            login(request, self.user)
            request.user.message_set.create(message=ugettext("Logado com sucesso: %(username)s.") % {'username': self.user.username})
            logging.debug("login - step3")
            if self.cleaned_data['remember']:
                logging.debug("login - step 4 - if")
                request.session.set_expiry(60 * 60 * 24 * 7 * 3)
            else:
                logging.debug("login - step 4 - else")
                request.session.set_expiry(0)
            logging.debug("login - return true")
            return True
        return False


class SignupForm(forms.Form):

    username  = forms.CharField(label=_(u"Usuário"), max_length=30, widget=forms.TextInput(), 
                               error_messages = {'required': u'Campo é obrigatório.' } )     
    #first_name      = forms.CharField(label=_(u'Nome'),  max_length=30, widget=forms.TextInput(), 
    #                             error_messages = {'required': u'Este campo é obrigatório.' } ) 
    #last_name = forms.CharField(label=_(u'Sobrenome'),  max_length=70, widget=forms.TextInput(), 
    #                             error_messages = {'required': u'Este campo é obrigatório.' } )

    #birth_date = forms.DateField(('%d/%m/%Y',), label=_(u'Data Nasc.(dd/mm/aaaa)'),  widget=forms.DateTimeInput(format='%d/%m/%Y'), required=True, 
    #                             error_messages = {'required': u'Este campo é obrigatório.', 'invalid':u'Informe uma data válida.' } )

    email       = forms.EmailField(label=_(u"Email"), required=True, widget=forms.TextInput(), 
                                              error_messages = {'required': u'Campo obrigatório.' } )

    password1  = forms.CharField(label=_(u"Senha"), widget=forms.PasswordInput(render_value=False), 
                                error_messages = {'required': u'Campo obrigatório.' } ) 
    password2  = forms.CharField(label=_(u"Redigite a Senha"), widget=forms.PasswordInput(render_value=False), 
                                error_messages = {'required': u'Campo obrigatório.' } ) 

    #about     = forms.CharField(label=u'Sobre', widget=forms.Textarea,  required=False)
    #interests = forms.CharField(label=u'Interesses', widget=forms.Textarea,  required=False)
    
    #location = forms.CharField(label=u'Cidade',  required=False)    
    
    #state    = forms.ChoiceField(label=u'Estado', widget=forms.Select, choices=Profile.STATE_CHOICE,  required=False)
    
    #country  = forms.CharField(label=u'País', required=False)    
    

    #website  = forms.URLField(label=u'Website', required=False)
        
    confirmation_key = forms.CharField(max_length=40, required=False, widget=forms.HiddenInput(), 
                                       error_messages = {'required': u'Este campo é obrigatório.' } )
    

    
    def clean_username(self):
        if not alnum_re.search(self.cleaned_data["username"]):
            raise forms.ValidationError(_(u"Nome de Usuário deve conter apenas letras, números e underscores."))
        try:
            user = User.objects.get(username__iexact=self.cleaned_data["username"])
        except User.DoesNotExist:
            return self.cleaned_data["username"]
        raise forms.ValidationError(_(u"Usuário já existe. Escolha outro."))

    
    def clean(self):
        if "password1" in self.cleaned_data and "password2" in self.cleaned_data:
            if self.cleaned_data["password1"] != self.cleaned_data["password2"]:
                raise forms.ValidationError(_(u"Senhas não conferem."))
        return self.cleaned_data

    def save(self):
        logging.debug("Signup.Save - Enter")
        
        logging.debug("Signup - save: username")
        username = self.cleaned_data["username"]
        logging.debug("Signup - save: email")        
        email = self.cleaned_data["email"]
        logging.debug("Signup - save: password1")
        password = self.cleaned_data["password1"]
        
        # @@@ clean up some of the repetition below -- DRY!

        if confirmed:
            logging.debug("Signup.Save - Step 2")
            if email == join_invitation.contact.email:
                logging.debug("Signup.Save - Step 3")
                new_user = User.objects.create_user(username, email, password)                
                join_invitation.accept(new_user) # should go before creation of EmailAddress below
                new_user.message_set.create(message=ugettext(u"Seu email já foi verificado"))
                # already verified so can just create
                EmailAddress(user=new_user, email=email, verified=True, primary=True).save()                
                #create_profile(new_user,  name=fullname)
                profile, created = Profile.objects.get_or_create(user=new_user)
                #profile.first_name = first_name
                #profile.last_name = last_name
                #profile.about = about
                #profile.interests = interests
                #profile.birth_date = birth_date
                #profile.location = location
                #profile.state = state
                #profile.country = country
                #profile.website = website  
                profile.save()                
            else:
                new_user = User.objects.create_user(username, "", password)
                #create_profile(new_user, name=fullname)
                profile, created = Profile.objects.get_or_create(user=new_user)
                #profile.first_name = first_name
                #profile.last_name = last_name
                #profile.about = about
                #profile.interests = interests
                #profile.birth_date = birth_date
                #profile.location = location
                #profile.state = state
                #profile.country = country
                #profile.website = website
                profile.save()
                
                join_invitation.accept(new_user) # should go before creation of EmailAddress below
                if email:
                    new_user.message_set.create(message=ugettext(u"Confirmação enviada para %(email)s") % {'email': email})
                    EmailAddress.objects.add_email(new_user, email)                
            return username, password,  email # required for authenticate()
        else:
            new_user = User.objects.create_user("daniel", "daniel.franca@gmail.com", "daniel")
            create_profile(new_user, name=username)
            profile, created = Profile.objects.get_or_create(user=new_user)
            #profile.first_name = first_name
            #profile.last_name = last_name
            #profile.about = about
            #profile.interests = interests
            #profile.birth_date = birth_date
            #profile.location = location
            #profile.state = state
            #profile.country = country
            #profile.website = website
            profile.save()
            if email:
                new_user.message_set.create(message=ugettext(u"Confirmação enviada para %(email)s") % {'email': email})
                EmailAddress.objects.add_email(new_user, email)
        
        return username, password,  email # required for authenticate()


class OpenIDSignupForm(forms.Form):
    username = forms.CharField(label=_(u"Usuário"), max_length=30, widget=forms.TextInput())
    email = forms.EmailField(label=_(u"Email (opcional)"), required=False, widget=forms.TextInput())
    
    def __init__(self, *args, **kwargs):
        # Remember provided (validated!) OpenID to attach it to the new user later.
        self.openid = kwargs.pop("openid")
        # TODO: do something with this?
        reserved_usernames = kwargs.pop("reserved_usernames")
        super(OpenIDSignupForm, self).__init__(*args, **kwargs)
    
    def clean_username(self):
        if not alnum_re.search(self.cleaned_data["username"]):
            raise forms.ValidationError(_(u"Nome de Usuário deve conter apenas letras, números e underscores."))
        try:
            user = User.objects.get(username__exact=self.cleaned_data["username"])
        except User.DoesNotExist:
            return self.cleaned_data["username"]
        raise forms.ValidationError(_(u"Usuário já existe. Escolha outro."))

    def save(self):
        username = self.cleaned_data["username"]
        email = self.cleaned_data["email"]
        new_user = User.objects.create_user(username, "", "!")

        if email:
            new_user.message_set.create(message=u"Confirmação enviada para %s" % email)
            EmailAddress.objects.add_email(new_user, email)

        if self.openid:
            # Associate openid with the new account.
            new_user.openids.create(openid = self.openid)
        return new_user


class UserForm(forms.Form):

    def __init__(self, user=None, *args, **kwargs):
        self.user = user
        super(UserForm, self).__init__(*args, **kwargs)

class AccountForm(UserForm):

    def __init__(self, *args, **kwargs):
        super(AccountForm, self).__init__(*args, **kwargs)
        try:
            self.account = Account.objects.get(user=self.user)
        except Account.DoesNotExist:
            self.account = Account(user=self.user)


class AddEmailForm(UserForm):

    email = forms.EmailField(label=_("Email"), required=True, widget=forms.TextInput(attrs={'size':'30'}))

    def clean_email(self):
        try:
            EmailAddress.objects.get(user=self.user, email=self.cleaned_data["email"])
        except EmailAddress.DoesNotExist:
            return self.cleaned_data["email"]
        raise forms.ValidationError(_(u"Este email já está associado com esta conta."))

    def save(self):
        self.user.message_set.create(message=ugettext(u"Confirmação enviada para %(email)s") % {'email': self.cleaned_data["email"]})
        return EmailAddress.objects.add_email(self.user, self.cleaned_data["email"])


class ChangePasswordForm(UserForm):

    oldpassword = forms.CharField(label=_("Senha Atual"), widget=forms.PasswordInput(render_value=False))
    password1 = forms.CharField(label=_("Nova Senha"), widget=forms.PasswordInput(render_value=False))
    password2 = forms.CharField(label=_("Redigite Nova Senha"), widget=forms.PasswordInput(render_value=False))

    def clean_oldpassword(self):
        if not self.user.check_password(self.cleaned_data.get("oldpassword")):
            raise forms.ValidationError(_("Please type your current password."))
        return self.cleaned_data["oldpassword"]

    def clean_password2(self):
        if "password1" in self.cleaned_data and "password2" in self.cleaned_data:
            if self.cleaned_data["password1"] != self.cleaned_data["password2"]:
                raise forms.ValidationError(_(u"Senhas não conferem."))
        return self.cleaned_data["password2"]

    def save(self):
        self.user.set_password(self.cleaned_data['password1'])
        self.user.save()
        self.user.message_set.create(message=ugettext(u"Senha alterada com sucesso."))


class SetPasswordForm(UserForm):
    
    password1 = forms.CharField(label=_("Senha"), widget=forms.PasswordInput(render_value=False))
    password2 = forms.CharField(label=_("Redigite a Senha"), widget=forms.PasswordInput(render_value=False))
    
    def clean_password2(self):
        if "password1" in self.cleaned_data and "password2" in self.cleaned_data:
            if self.cleaned_data["password1"] != self.cleaned_data["password2"]:
                raise forms.ValidationError(_(u"Senhas não conferem."))
        return self.cleaned_data["password2"]
    
    def save(self):
        self.user.set_password(self.cleaned_data["password1"])
        self.user.save()
        self.user.message_set.create(message=ugettext(u"Senhada criada com sucesso."))

class ResetPasswordForm(forms.Form):

    email = forms.EmailField(label=_("Email"), required=True, widget=forms.TextInput(attrs={'size':'30'}))

    def clean_email(self):
        if EmailAddress.objects.filter(email__iexact=self.cleaned_data["email"], verified=True).count() == 0:
            raise forms.ValidationError(_("Email não verificado para a conta"))
        return self.cleaned_data["email"]

    def save(self):
        for user in User.objects.filter(email__iexact=self.cleaned_data["email"]):
            new_password = User.objects.make_random_password()
            user.set_password(new_password)
            user.save()
            subject = _("Alterar Senha")
            message = render_to_string("account/password_reset_message.txt", {
                "user": user,
                "new_password": new_password,
            })
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email], priority="high")
        return self.cleaned_data["email"]


class ChangeTimezoneForm(AccountForm):

    timezone = TimeZoneField(label=_("Timezone"), required=True)

    def __init__(self, *args, **kwargs):
        super(ChangeTimezoneForm, self).__init__(*args, **kwargs)
        self.initial.update({"timezone": self.account.timezone})

    def save(self):
        self.account.timezone = self.cleaned_data["timezone"]
        self.account.save()
        self.user.message_set.create(message=ugettext(u"Timezone successfully updated."))

class ChangeLanguageForm(AccountForm):

    language = forms.ChoiceField(label=_("Language"), required=True, choices=settings.LANGUAGES)

    def __init__(self, *args, **kwargs):
        super(ChangeLanguageForm, self).__init__(*args, **kwargs)
        self.initial.update({"language": self.account.language})

    def save(self):
        self.account.language = self.cleaned_data["language"]
        self.account.save()
        self.user.message_set.create(message=ugettext(u"Language successfully updated."))


# @@@ these should somehow be moved out of account or at least out of this module

from account.models import OtherServiceInfo, other_service, update_other_services

class TwitterForm(UserForm):
    username = forms.CharField(label=_("Username"), required=True)
    password = forms.CharField(label=_("Password"), required=True,
                               widget=forms.PasswordInput(render_value=False))

    def __init__(self, *args, **kwargs):
        super(TwitterForm, self).__init__(*args, **kwargs)
        self.initial.update({"username": other_service(self.user, "twitter_user")})

    def save(self):
        from microblogging.utils import get_twitter_password
        update_other_services(self.user,
            twitter_user = self.cleaned_data['username'],
            twitter_password = get_twitter_password(settings.SECRET_KEY, self.cleaned_data['password']),
        )
        self.user.message_set.create(message=ugettext(u"Successfully authenticated."))
