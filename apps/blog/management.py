# -*- coding: iso-8859-1 -*-
from django.conf import settings
from django.db.models import signals
from django.utils.translation import ugettext_noop as _

if "notification" in settings.INSTALLED_APPS:
    from notification import models as notification

    def create_notice_types(app, created_models, verbosity, **kwargs):
        notification.create_notice_type("blog_follow_post", _(u"Novo Post em Blog"), _(u"um amigo seu criou um novo post em seu blog"), default=2,  to_follow=True)
        notification.create_notice_type("blog_post_comment", _(u"Novo Comentário em seu Blog"), _(u"um comentário foi adicionado em um de seus posts"), default=2)

    signals.post_syncdb.connect(create_notice_types, sender=notification)
else:
    print "Skipping creation of NoticeTypes as notification app not found"
