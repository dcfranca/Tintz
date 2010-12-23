# -*- coding: iso-8859-1 -*-
import os
from django.db import models
from django.db import models
from django.contrib.auth.models import User
from profiles.models import *

from tagging.fields import TagField

from django.utils.translation import ugettext_lazy as _
from publications.utils import get_profile_path

if "notification" in settings.INSTALLED_APPS:
    from notification import models as notification
else:
    notification = None

import logging

# Create your models here.
class Publication(models.Model):
    """
    A publication (Comic, charge, magazine, etc)
    """
    LANG_CHOICE = ( ('pt_BR',u'Português'),
	            ('en',u'English'),
		  )

    CATEGORY_CHOICE = ( ('Quadrinhos', 'Quadrinhos'),
                       ('Revista', 'Revista'),
                       ('Tira', 'Tira'),
                    )

    RATED_CHOICE = ((0, 'Livre'),
                    (12,  '12 anos'),
                    (16, '16 anos'),
                    (18, '18 anos'))

    title = models.CharField(_('name'), max_length=200, null=False)
    author = models.ForeignKey(User, related_name="added_publications", default="", null=False)
    file_name = models.FileField(_('file_name'), upload_to=get_profile_path, null=False)
    description = models.TextField(_('description'), null=False)
    language    = models.CharField(_('language'), choices=LANG_CHOICE, max_length=20, null=False)
    nr_pages    = models.IntegerField(_('nr_pages'), null=False)
    date_added  = models.DateTimeField(_('date_added'))
    category      = models.CharField(_('category'),  choices=CATEGORY_CHOICE,  max_length=30,  null=False)
    rated           = models.IntegerField(_('rated'),  choices=RATED_CHOICE, null= False)
    tags = TagField(_('tags'), null=True)
    status = models.IntegerField(_('status')) #0 - Waiting to be converted, 1 - Converted
    views  = models.IntegerField(_('views'), default=0, null=True)
    rate = models.DecimalField(_('rate'),max_digits=5, decimal_places=2, null=True)
    is_public = models.BooleanField(_('is_public'), default=False)
    allow_comments  = models.BooleanField(_('allow comments'), default=True)
    images_ext      = models.CharField(_('images_ext'), max_length=10, null=True)

    class Meta:
        verbose_name = _('publication')
        verbose_name_plural = _('publications')

    def get_thumbnail64_name(self):
      fname,fext = os.path.splitext(os.path.basename(self.file_name.path))
      fname = unicode(fname,'utf-8')
      return "".join([ "publications/",self.author.__str__(),"/", fname,".thumb64x64.png"])

    def get_thumbnail128_name(self):
      fname,fext = os.path.splitext(os.path.basename(self.file_name.path))
      fname = unicode(fname,'utf-8')
      return "".join([ "publications/",self.author.__str__(),"/", fname,".thumb128x128.png"])

    def get_thumbnail150_name(self):
      fname,fext = os.path.splitext(os.path.basename(self.file_name.path))
      fname = unicode(fname,'utf-8')
      return "".join([ "publications/",self.author.__str__(),"/", fname,"_001_thumb150", self.images_ext])

    def get_thumbnail260_name(self):
      fname,fext = os.path.splitext(os.path.basename(self.file_name.path))
      return "".join([ "publications/",self.author.__str__(),"/", fname,".thumb256x256.png"])

    def get_basename(self):
      fname,fext = os.path.splitext(os.path.basename(self.file_name.path))
      fname = unicode(fname,'utf-8')
      return "".join([ "publications/",self.author.__str__(),"/", fname] )

    def not_rated(self, author):
      return PublicationRate.getobjects( who_vote = author )

    def get_small_text(self):
        if len(self.description) < 300:
            return self.description
        return self.description[0:296]+"..."

    def format_rate(self):
      return "%5.2f%%" % float(self.rate)

    def incr_views(self):
      self.views += 1
      self.save()

    def get_total_pages(self):
      return str(self.nr_pages)


class PublicationScore(models.Model):
    """
    Score for publications
    """
    RATE_CHOICE = ( (u'1',1),
	            (u'2',2),
		    (u'3',3),
		    (u'4',4),
		    (u'5',5),
		  )

    publication = models.ForeignKey(Publication,related_name="publication_score", default="", null=False)
    vote_date   = models.DateTimeField(_('vote_date'), null=False)
    who_vote    = models.ForeignKey(User, related_name="my_votes", default="", null=False)
    rate        = models.IntegerField(_('score'), choices=RATE_CHOICE, null=False)

    class Meta:
	verbose_name =_('publication rate')
	verbose_name_plural = _('publication rates')

class PublicationReportAbuse(models.Model):
    publication = models.ForeignKey(Publication,related_name="publication_report_abuse", default="", null=False)
    reporter    = models.ForeignKey(User, related_name="my_report", default="", null=False)
    message     = models.TextField(_('message'), null=False)

    class Meta:
        verbose_name = _('publication report abuse')
        verbose_name = _('publication report abuses')

# handle notification of new comments
from threadedcomments.models import ThreadedComment
def new_comment(sender, instance, **kwargs):
    if isinstance(instance.content_object, Publication):
        post = instance.content_object
        if notification:
            notification.send([post.author], "publication_post_comment",
                {"user": instance.user, "post": post, "comment": instance, "publication":instance.content_object})
models.signals.post_save.connect(new_comment, sender=ThreadedComment)
