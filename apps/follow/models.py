from django.db import models
from django.utils.translation import ugettext_lazy as _

from django.contrib.auth.models import User

from apps.publications.models import Publication
from apps.blog.models import Post
import datetime
from tintzsettings.models import TintzSettings
from emailconfirmation.models import EmailAddress
from django.utils.translation import ugettext_lazy as _, ugettext
from django.template.loader import render_to_string

from misc.utils import get_send_mail
from markdown import message
import settings
import user

send_mail = get_send_mail()

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
        elif type == 2:
            update.post = item_to_update
            update.type = 2
        elif type == 0:
            subject = _("Tintz - Novo Seguidor")
            message_html = render_to_string("follow/new_follower_message.html", {
                "follower": item_to_update,
            })
            send_mail(subject, message_html, settings.DEFAULT_FROM_EMAIL, [item_to_update.email], priority="high")
            return


        update.date_post = datetime.datetime.now()

        try:
            followers = FollowAuthor.objects.filter( UserTo = item_to_update.author )
        except FollowAuthor.DoesNotExist:
            pass

        if followers:
            for follower in followers:
                if type != 0:
                    update.id = None
                    update.user = follower.UserFrom
                    update.save()

                #Check if it's to send Email
                follower_settings = None
                try:
                    follower_settings = TintzSettings.objects.get( user = follower )
                except:
                    continue

                if follower_settings != None:
                    if type == 1 and follower_settings.email_publication:
                        subject = _("Tintz - Nova Publica&ccedil;&atilde;o")
                        message_html = render_to_string("follow/new_publication_message.html", {
                            "update": update,
                        })
                        send_mail(subject, message_html, settings.DEFAULT_FROM_EMAIL, [follower.UserFrom.email], priority="high")
                    elif type == 2 and follower_settings.email_post == True:
                        subject = _("Tintz - Novo Post")
                        message_html = render_to_string("follow/new_post_message.html", {
                            "update": update,
                        })
                        send_mail(subject, message_html, settings.DEFAULT_FROM_EMAIL, [follower.UserFrom.email], priority="high")

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


