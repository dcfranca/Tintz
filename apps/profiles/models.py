# -*- coding: iso-8859-1 -*-
from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.utils.translation import ugettext_lazy as _
import datetime

from timezones.fields import TimeZoneField

class AccountType(models.Model):

    name = models.CharField(_("name"), max_length=100, null=False)
    credits_month = models.IntegerField(_("max credits month"), null=False)
    credits_total = models.IntegerField(_("max credits total"), null=False)
    enable_sell   = models.BooleanField(_("enable sell"), null=False)
    price         = models.DecimalField(_("price"), max_digits=10, decimal_places=2, null=False)

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = _('account type')
        verbose_name_plural = _('account types')

    class Admin:
        pass

class Profile(models.Model):
    """
    User Profile
    """
    STATE_CHOICE = (('','') , 
                                ('AC','AC'),
                                ('AL','AL'),
                                ('AM','AM'),
                                ('AP','AP'),
                                ('BA','BA'),
                                ('CE','CE'),
                                ('DF','DF'),
                                ('ES','ES'),
                                ('GO','GO'),                                
                                ('MA','MA'),
                                ('MG','MG'),                                
                                ('MS','MS'),
                                ('MT','MT'),                                
                                ('PA','PA'),
                                ('PB','PB'),
                                ('PE','PE'),                                
                                ('PI','PI'),
                                ('PR','PR'),
                                ('RJ','RJ'),                                
                                ('RN','RN'),
                                ('RO','RO'),
                                ('RR','RR'),
                                ('RS','RS'),
                                ('SC','SC'),                                
                                ('SE','SE'),
                                ('SP','SP'),
                                ('TO','TO'),
		  )

    ACCOUNT_CHOICE = (('1','Gratuita') , 
                      ('2','Pro'),
                      ('3','Premium'),
		  )

    user = models.ForeignKey(User, unique=True, verbose_name=_('user'))
    first_name = models.CharField(_('first_name'), max_length=30, null=False, default='')
    last_name = models.CharField(_('last_name'), max_length=70, null=False, default='')
    age   = models.IntegerField(_('age'), null=True)
    about = models.TextField(_('about'), null=True, blank=True)
    interests = models.TextField(_('interests'), null=True, blank=True)
    birth_date = models.DateField(_('birth_date'), null=False, default='1900-01-01')
    location = models.CharField(_('location'), max_length=40, null=True, blank=True)
    state    = models.CharField(_('state'), choices=STATE_CHOICE,  max_length=40, null=True, blank=True)
    country  = models.CharField(_('country'), max_length=40, null=True, blank=True)
    website = models.URLField(_('website'), null=True, blank=True)
    account_type = models.ForeignKey(AccountType, verbose_name=('account type'), null=True)
    
    def __unicode__(self):
        return self.user.username
    
    def get_absolute_url(self):
        return ('profile_detail', None, {'username': self.user.username})
    get_absolute_url = models.permalink(get_absolute_url)

    def get_small_about(self):
        if len(self.about) < 200:
            return self.about
        return self.about[0:197]+"..."
    
    class Meta:
        verbose_name = _('profile')
        verbose_name_plural = _('profiles')

def create_profile(sender, instance=None, **kwargs):
    if instance is None:
        return
    profile, created = Profile.objects.get_or_create(user=instance)
    
post_save.connect(create_profile, sender=User)


