from django.db import models
from django.utils.translation import ugettext_lazy as _

from django.contrib.auth.models import User

class FollowAuthor(models.Model):
    
    UserFrom = models.ForeignKey(User, related_name="following", verbose_name=_('follower'))    
    UserTo = models.ForeignKey(User, related_name="follower", verbose_name=_('following'))

