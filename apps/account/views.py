# -*- coding: iso-8859-1 -*-

from django.conf import settings
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect, HttpResponseForbidden, Http404
from django.db.models import Q
from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login
from django.template import RequestContext
from django.utils.translation import ugettext, ugettext_lazy as _
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required

from account.utils import get_default_redirect
from account.models import OtherServiceInfo
from account.forms import SignupForm, AddEmailForm, LoginForm, \
    ChangePasswordForm, SetPasswordForm, ResetPasswordForm, \
    ChangeTimezoneForm, ChangeLanguageForm, TwitterForm
from emailconfirmation.models import EmailAddress, EmailConfirmation
from django.contrib.auth.models import User
import logging

def login(request, form_class=LoginForm,
        template_name="account/login.html", success_url=None):
    if success_url is None:
        success_url = get_default_redirect(request)
        
    if request.user.is_authenticated():
        return HttpResponseRedirect(success_url)
        
    if request.method == "POST":
        form = form_class(request.POST)
        if form.login(request):
            return HttpResponseRedirect(success_url)
    else:
        form = form_class()
    return render_to_response(template_name, {
        "form": form,
        "is_me": True,
        "other_user": request.user,
    }, context_instance=RequestContext(request))

def signup(request, form_class=SignupForm,
        template_name="account/signup.html", success_url=None):

    import pdb; 
    
    logging.debug("Signup - Enter")

    if success_url is None:
        success_url = get_default_redirect(request)
        
    if request.user.is_authenticated():
        return HttpResponseRedirect(success_url)
        
        
    if request.method == "POST":
        form = form_class(request.POST)
        if form.is_valid():
            username, password, email = form.save()
            user =  User.objects.get(username=username) #  authenticate(username=username, password=password)
            #auth_login(request, user)
            #request.user.message_set.create(
            #    message=_("Login efetuado com sucesso para %(username)s.") % {
            #    'username': user.username
            #})
            pdb.set_trace()                       
            send_email_confirmation(user,  email)
            return  HttpResponseRedirect('/about/confirm_email')
    else:
        form = form_class()
    
    logging.debug("Signup - Leave")
    return render_to_response(template_name, {
        "form": form,
    }, context_instance=RequestContext(request))

@login_required
def email(request, form_class=AddEmailForm,
        template_name="account/email.html"):
    logging.debug("Email - Enter")
    if request.method == "POST" and request.user.is_authenticated():
        if request.POST["action"] == "add":
            logging.debug("Email - Add email")
            add_email_form = form_class(request.user, request.POST)
            if add_email_form.is_valid():
                add_email_form.save()
                add_email_form = form_class() # @@@
        else:
            add_email_form = form_class()
            if request.POST["action"] == "send":                                
                email = request.POST["email"]
                send_email_confirmation(request,  email)
            elif request.POST["action"] == "remove":
                email = request.POST["email"]
                try:
                    email_address = EmailAddress.objects.get(
                        user=request.user,
                        email=email
                    )
                    email_address.delete()
                    request.user.message_set.create(
                        message="Removed email address %s" % email)
                except EmailAddress.DoesNotExist:
                    pass
            elif request.POST["action"] == "primary":
                email = request.POST["email"]
                email_address = EmailAddress.objects.get(
                    user=request.user,
                    email=email,
                )
                email_address.set_as_primary()
    else:
        add_email_form = form_class()
    
    logging.debug("Email - Leave")
    return render_to_response(template_name, {
        "add_email_form": add_email_form,
        "is_me": True,
        "other_user": request.user,
    }, context_instance=RequestContext(request))

def send_email_confirmation(user,  email):
    logging.debug('Email - Send email: %s' % email)
    try:
        email_address = EmailAddress.objects.get(
            user=user,
            email=email,
        )
        #request.user.message_set.create(
        #    message=u"Confirma��o de email enviada para %s" % email)
        
        EmailConfirmation.objects.send_confirmation(email_address)
        logging.debug('Email - Sent to: %s' % email_address)
    except EmailAddress.DoesNotExist:
        pass
        
@login_required
def password_change(request, form_class=ChangePasswordForm,
        template_name="account/password_change.html"):
    if not request.user.password:
        return HttpResponseRedirect(reverse("acct_passwd_set"))
    if request.method == "POST":
        password_change_form = form_class(request.user, request.POST)
        if password_change_form.is_valid():
            password_change_form.save()
            password_change_form = form_class(request.user)
    else:
        password_change_form = form_class(request.user)
    return render_to_response(template_name, {
        "password_change_form": password_change_form,
        "is_me": True,
        "other_user": request.user,
    }, context_instance=RequestContext(request))

@login_required
def password_set(request, form_class=SetPasswordForm,
        template_name="account/password_set.html"):
    if request.user.password:
        return HttpResponseRedirect(reverse("acct_passwd"))
    if request.method == "POST":
        password_set_form = form_class(request.user, request.POST)
        if password_set_form.is_valid():
            password_set_form.save()
            return HttpResponseRedirect(reverse("acct_passwd"))
    else:
        password_set_form = form_class(request.user)
    return render_to_response(template_name, {
        "password_set_form": password_set_form,
    }, context_instance=RequestContext(request))

@login_required
def password_delete(request, template_name="account/password_delete.html"):
    # prevent this view when openids is not present or it is empty.
    if not request.user.password or \
        (not hasattr(request, "openids") or \
            not getattr(request, "openids", None)):
        return HttpResponseForbidden()
    if request.method == "POST":
        request.user.password = u""
        request.user.save()
        return HttpResponseRedirect(reverse("acct_passwd_delete_done"))
    return render_to_response(template_name, {
    }, context_instance=RequestContext(request))

def password_reset(request, form_class=ResetPasswordForm,
        template_name="account/password_reset.html",
        template_name_done="account/password_reset_done.html"):
    if request.method == "POST":
        password_reset_form = form_class(request.POST)
        if password_reset_form.is_valid():
            email = password_reset_form.save()
            return render_to_response(template_name_done, {
                "email": email,
            }, context_instance=RequestContext(request))
    else:
        password_reset_form = form_class()
    
    return render_to_response(template_name, {
        "password_reset_form": password_reset_form,
    }, context_instance=RequestContext(request))


@login_required
def timezone_change(request, form_class=ChangeTimezoneForm,
        template_name="account/timezone_change.html"):
    if request.method == "POST":
        form = form_class(request.user, request.POST)
        if form.is_valid():
            form.save()
    else:
        form = form_class(request.user)
    return render_to_response(template_name, {
        "form": form,
    }, context_instance=RequestContext(request))

@login_required
def language_change(request, form_class=ChangeLanguageForm,
        template_name="account/language_change.html"):
    if request.method == "POST":
        form = form_class(request.user, request.POST)
        if form.is_valid():
            form.save()
            next = request.META.get('HTTP_REFERER', None)
            return HttpResponseRedirect(next)
    else:
        form = form_class(request.user)
    return render_to_response(template_name, {
        "form": form,
    }, context_instance=RequestContext(request))



@login_required
def other_services(request, template_name="account/other_services.html"):
    from microblogging.utils import twitter_verify_credentials
    twitter_form = TwitterForm(request.user)
    twitter_authorized = False
    if request.method == "POST":
        twitter_form = TwitterForm(request.user, request.POST)

        if request.POST['actionType'] == 'saveTwitter':
            if twitter_form.is_valid():
                from microblogging.utils import twitter_account_raw
                twitter_account = twitter_account_raw(
                    request.POST['username'], request.POST['password'])
                twitter_authorized = twitter_verify_credentials(
                    twitter_account)
                if not twitter_authorized:
                    request.user.message_set.create(
                        message="Twitter authentication failed")
                else:
                    twitter_form.save()
    else:
        from microblogging.utils import twitter_account_for_user
        twitter_account = twitter_account_for_user(request.user)
        twitter_authorized = twitter_verify_credentials(twitter_account)
        twitter_form = TwitterForm(request.user)
    return render_to_response(template_name, {
        "twitter_form": twitter_form,
        "twitter_authorized": twitter_authorized,
    }, context_instance=RequestContext(request))

@login_required
def other_services_remove(request):
    # TODO: this is a bit coupled.
    OtherServiceInfo.objects.filter(user=request.user).filter(
        Q(key="twitter_user") | Q(key="twitter_password")
    ).delete()
    request.user.message_set.create(message=ugettext(u"Removed twitter account information successfully."))
    return HttpResponseRedirect(reverse("acct_other_services"))

