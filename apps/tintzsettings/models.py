# -*- coding: iso-8859-1 -*-
from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _


# Create your models here.
class TintzSettings(models.Model):
    """
    Personal Settings
    """
    user         = models.ForeignKey(User, related_name="Settings_user", default="", null=False)
    email_follow = models.BooleanField(_('email_follow'))
    email_publication = models.BooleanField(_('email_publication'))
    email_post = models.BooleanField(_('email_post'))

    class Meta:
        verbose_name = _('tintzsettings')
        verbose_name_plural = _('tintzsettings')

