# -*- coding: iso-8859-1 -*-
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponseRedirect, get_host
from django.template import RequestContext
from django.core.urlresolvers import reverse

from tintzsettings.forms import TintzSettingsForm
#from emailconfirmation.models import EmailAddress
from tintzsettings.models import TintzSettings
from django.utils.translation import ugettext_lazy as _, ugettext

from account.utils import login_complete

@login_complete
def tintzsettings(request, form_class=TintzSettingsForm,
        template_name="tintzsettings/tintzsettings.html"):
    """
    Settings
    """
    try:
        config = TintzSettings.objects.get( user=request.user )
    except:
        config = TintzSettings()
        config.user = request.user
        pass

    #my_email = EmailAddress.objects.get_primary(request.user).email

    #config_form = form_class({'email': my_email }, request.user, request.POST, instance=config)
    config_form = form_class(initial={'email': request.user.email,'oldpassword':'', 'password1':'', 'password2':'' }, instance=config)

    if request.method == 'POST':
        if request.POST.get("action") == "update":
            config_form = form_class(request.user, request.POST, instance=config)
            if config_form.is_valid():
                config = config_form.save(request)
                request.user.message_set.create(message=ugettext(u"Configurações atualizadas."))
                return HttpResponseRedirect(reverse('tintz_settings'))

    return render_to_response(template_name, {
        "form": config_form,
        "is_me": True,
        "other_user":request.user,
    }, context_instance=RequestContext(request))
