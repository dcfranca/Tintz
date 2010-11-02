from django.db import models
from django.utils.translation import ugettext_lazy as _

from django.contrib.auth.models import User

from apps.publications.models import Publication
from apps.blog.models import Post
import datetime

class FollowAuthor(models.Model):
    
    UserFrom = models.ForeignKey(User, related_name="following", verbose_name=_('follower'))    
    UserTo = models.ForeignKey(User, related_name="follower", verbose_name=_('following'))


class UpdateManager(models.Manager):

    #Update followers timeline
    def update_followers(self, type, item_to_update):
        update = Update()

        if type == 1:
            update.type = 1
            update.publication = item_to_update
        else:
            update.post = item_to_update
            update.type = 2

        update.date_post = datetime.datetime.now()

        try:
            followers = FollowAuthor.objects.filter( UserTo = item_to_update.author )
        except FollowAuthor.DoesNotExist:
            pass

        if followers:
            for follower in followers:
                update.id = None
                update.user = follower.UserFrom
                update.save()


class Update(models.Model):

    UPDATE_TYPE = (('1','Publication') ,
                      ('2','Blog'),
		  )

    type = models.CharField(_('type'), choices=UPDATE_TYPE,  max_length=15, null=False)
    user        = models.ForeignKey(User, related_name="user")
    date_post   = models.DateTimeField(_('date_post'), null=False)
    publication = models.ForeignKey(Publication, related_name="publication", verbose_name=_('publication'), null=True)
    post        = models.ForeignKey(Post, related_name="post", verbose_name=_('post'), null=True)

    objects = UpdateManager()


