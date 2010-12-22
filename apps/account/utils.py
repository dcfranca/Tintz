from django.conf import settings
from django.core.urlresolvers import reverse
from django.http import   HttpResponseRedirect

LOGIN_REDIRECT_URLNAME = getattr(settings, "LOGIN_REDIRECT_URLNAME", '')


#the decorator
def login_complete(f):
    def wrap(request, *args, **kwargs):
        
        #this check the session if userid key exist, if not it will redirect to login page
        if not request.user.is_authenticated():
            return HttpResponseRedirect(reverse("acct_login"))
            
        profile = request.user.get_profile()

        #import pdb; pdb.set_trace()

        if profile != None and len(profile.first_name) == 0:
            return HttpResponseRedirect(reverse("acct_signup_complete"))
            
        return f(request, *args, **kwargs)
    wrap.__doc__=f.__doc__
    wrap.__name__=f.__name__
    return wrap

def get_default_redirect(request, redirect_field_name="next",
        login_redirect_urlname=LOGIN_REDIRECT_URLNAME):
    """
    Returns the URL to be used in login procedures by looking at different
    values in the following order:
    
    - LOGIN_REDIRECT_URLNAME - the name of a URLconf entry in the tintzsettings
    - LOGIN_REDIRECT_URL - the URL in the setting
    - a REQUEST value, GET or POST, named "next" by default.
    """
    #import pdb; pdb.set_trace()
    
    if login_redirect_urlname:
        default_redirect_to = reverse(login_redirect_urlname)
    else:
        default_redirect_to = settings.LOGIN_REDIRECT_URL
    redirect_to = request.REQUEST.get(redirect_field_name)
    # light security check -- make sure redirect_to isn't garabage.
    if not redirect_to or "://" in redirect_to or " " in redirect_to:
        redirect_to = default_redirect_to
    return redirect_to
