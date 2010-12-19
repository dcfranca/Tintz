from django.conf.urls.defaults import *
from account.forms import *

urlpatterns = patterns('',
    url(r'^email/$', 'account.views.email', name="acct_email"),
    url(r'^signup/$', 'account.views.signup', name="acct_signup"),
    url(r'^login/$', 'account.views.login', name="acct_login"),
    url(r'^logout/$', 'account.views.logout', name="acct_logout"),
    url(r'^confirm_email/(\w+)/$', 'emailconfirmation.views.confirm_email', name="acct_confirm_email"),
    url(r'^signup_complete/$', 'account.views.signup_complete', name="acct_signup_complete"),
    url(r'^forgot_password/$', 'account.views.forgot_password', name="acct_forgot_password"),

    # ajax validation
    #(r'^validate/$', 'ajax_validation.views.validate', {'form_class': SignupForm}, 'signup_form_validate'),
)
