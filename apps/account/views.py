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
from django.contrib.auth.views import logout as django_logout

from account.utils import get_default_redirect
from account.models import OtherServiceInfo
from account.forms import SignupForm, SignupCompleteForm, AddEmailForm, LoginForm, ForgotPasswordForm
from emailconfirmation.models import EmailAddress, EmailConfirmation
from django.contrib.auth.models import User

#from pagseguropy import *
import logging
#from apps.pagseguropy.pagseguro import Pagseguro
#from apps.misc.paylib import PagSeguro

from account.utils import login_complete

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

def logout(request):
    success_url = get_default_redirect(request)

    django_logout(request)
    return  HttpResponseRedirect(success_url)

def signup(request, form_class=SignupForm,
        template_name="account/signup.html", success_url=None):

    #import pdb; pdb.set_trace()

    if success_url is None:
        success_url = get_default_redirect(request)

    if request.user.is_authenticated():
        return HttpResponseRedirect(success_url)

    if request.method == "POST":
        form = form_class(request.POST)
        if form.is_valid():
            username, password, email = form.save()
            user =  User.objects.get(username=username) #  authenticate(username=username, password=password)
            send_email_confirmation(user,  email)
            return  HttpResponseRedirect('/about/confirm_email')
    else:
        form = form_class()

    return render_to_response(template_name, {
        "form": form,
    }, context_instance=RequestContext(request))

@login_required
def signup_complete(request, form_class=SignupCompleteForm,
        template_name="account/signup_complete.html", success_url=None):

    if success_url is None:
        success_url = get_default_redirect(request)

    if request.method == "POST":
        form = form_class(request.POST)
        if form.is_valid():
            username, password, email = form.save(request)
            user =  User.objects.get(username=username)
            authenticate(username=username, password=password)
            return  HttpResponseRedirect(success_url)
    else:
        form = form_class()

    return render_to_response(template_name, {
        "form": form,
	"username": request.user.username,
    }, context_instance=RequestContext(request))


def forgot_password(request, form_class=ForgotPasswordForm,
        template_name="account/forgot_password.html", success_url=None):

    sent_email = None

    if success_url is None:
        success_url = get_default_redirect(request)

    if request.method == "POST":
        form = form_class(request.POST)
        if form.is_valid():
            sent_email = u"Nova senha enviada para o email informado"
    else:
        form = form_class()

    return render_to_response(template_name, {
        "form": form,
        "sent_email": sent_email,
    }, context_instance=RequestContext(request))


"""
@login_complete
def pay_account(request):

    success_url = get_default_redirect(request)

    if request.method == 'POST':
        # token gerado no painel de controle do PagSeguro
        token = '12345699CA2AAAF4599EA697BB2F7FFF'
        p = PagSeguro()
        retorno = p.processar(token, request.POST)

        if retorno == True:
            try:
                pass

                # Cadastra os dados recebidos no banco de dados.
                # Utilize o request.POST.get('nomedocampo') para obter os valores
            except:
                pass
            return HttpResponse('Ok')
        else:
            return HttpResponse('Error')

    else:
        # Carrega tela contendo a mensagem de compra realizada
        return  HttpResponseRedirect(success_url)
"""


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
    #import pdb; pdb.set_trace()
    logging.debug('Email - Send email: %s' % email)
    try:
        email_address = EmailAddress.objects.get(
            user=user,
            email=email,
        )
        #request.user.message_set.create(
        #    message=u"Confirmacao de email enviada para %s" % email)

        EmailConfirmation.objects.send_confirmation(email_address)

        logging.debug('Email - Sent to: %s' % email_address)
    except EmailAddress.DoesNotExist:
        pass

