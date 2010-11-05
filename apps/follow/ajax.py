from django.utils import simplejson
from dajaxice.core import dajaxice_functions
from dajax.core import Dajax
from publications.models import Publication
from follow.models import Update
from tintz import settings
import dajax
import logging
from django.contrib.auth.models import User
from avatar.templatetags.avatar_tags import *

from django.core.urlresolvers import reverse

def more_updates(request, last_update):

    media_url = '/site_media/'
    more_num = 10
    last_up = int(last_update)

    template_post = """<tr><td><div class="update-item span-14">
        <div class="update-avatar span-2"><a href="%s" title="%s %s"><img src="%s" alt="%s" width="70" height="70" /></a></div>
        <div class="update-name span-5 last"><a href="%s" title="%s %s">%s %s</a></div>

        <a class="span-10 update-posts-title last" href="%s">%s</a>
        <div class="span-10 update-posts-description last">
            %s
        </div>
        </div></td></tr>"""

    template_pub  = """<tr><td><div class="update-avatar span-2"><a href="%s" title="%s %s"><img src="%s" alt="%s" width="70" height="70" /></a></div>
        <div class="update-name span-5 last"><a href="%s" title="%s %s">%s %s</a></div>
        <div class="update-pub-cover span-4">
        <a href="%s">
        <img src="%s%s" href="%s" alt="%s"/></a>
        </div>
        <div class="update-pub-title span-5 last">
        <a href="%s">%s</a>
        </div>
        <div class="span-10 last update-pub-description">%s</div></td></tr>
        """

    updates = Update.objects.filter( user = request.user )[last_up:last_up+more_num]

    htmlOutput = ""

    for update in updates:

        if update.type == '1':
            link_prof_details_pub  = reverse('profile_detail', args=(update.publication.author,))
            link_details_pub       = reverse('publication_details', args=(update.publication.author,update.publication.id,))
            name = update.publication.author.get_profile().first_name
            lastname = update.publication.author.get_profile().last_name
            text_pub = update.publication.get_small_text()
            username = update.publication.author.username
            avatar_pub = avatar_url(update.publication.author, 70)
            htmlOutput += template_pub % ( link_prof_details_pub, name, lastname, avatar_pub, username  ,link_prof_details_pub, name, lastname,
                                           name, lastname, link_details_pub, media_url, update.publication.get_thumbnail150_name(),
                                           link_details_pub, update.publication.title, link_details_pub, update.publication.title,
                                           text_pub )
        else:
            link_prof_details_post = reverse('profile_detail', args=(update.post.author,))
            link_post_url          = update.post.get_absolute_url()
            name = update.post.author.get_profile().first_name
            lastname = update.post.author.get_profile().last_name
            text_post = update.post.get_small_text()
            username = update.post.author.username
            avatar_post = avatar_url(update.post.author, 70)
            htmlOutput += template_pub % ( link_prof_details_post, name, lastname, avatar_post, username, link_prof_details_post,
                                           name, lastname,
                                           name, lastname, link_post_url, update.post.title, text_post )

    dajax = Dajax()
    dajax.append('#list-updates','innerHTML', htmlOutput)
    dajax.assign('#last_update','innerText', last_up+len(updates))

    return dajax.json()


dajaxice_functions.register(more_updates)