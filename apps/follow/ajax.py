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
from profiles.views import *

from django.core.urlresolvers import reverse

"""

def getFollowings(request, other_user):
    #Finding followings            
    followings = FollowAuthor.objects.filter( UserFrom = other_user )
    followinUsers = []
    for  follow in followings:
        followinUsers.append( follow.UserTo )
    return followinUsers

def getUpdates(request,followingUsers):
    updates = []
    
    for following in followingUsers:
        publications = getPublications(request,following, False)
        for publication in publications:
            up = Update()
            up.type = '1'
            up.publication = publication
            up.date_post = publication.date_added
            updates.append(up)

        posts = getPosts(request,following)        
        for post in posts:
            up = Update()
            up.type = '2'
            up.post = post
            up.date_post = post.publish
            updates.append(up)        

        #Update.objects.filter(user = request.user).order_by('-date_post')[0:10]

    #import pdb; pdb.set_trace()
    return sorted(updates, key=lambda update: update.date_post, reverse=True)[0:10]

"""

def more_updates(request, last_update):

    media_url = '/site_media/'
    more_num = 10
    last_up = int(last_update)

    template_post = """<div class="update-item span-14"><div class="update-item span-14">
        <div class="update-avatar span-2"><a href="%s" title="%s %s"><img src="%s" alt="%s" width="70" height="70" /></a></div>
        <div class="update-name span-5 last"><a href="%s" title="%s %s">%s %s</a></div>

        <a class="span-10 update-posts-title last" href="%s">%s</a>
        <div class="span-10 update-posts-description last">
            %s
        </div>
        </div>
        </div>"""

    template_pub  = """<div class="update-item span-14"><div class="update-avatar span-2"><a href="%s" title="%s %s"><img src="%s" alt="%s" width="70" height="70" /></a></div>
        <div class="update-name span-3 last"><a href="%s" title="%s %s">%s %s</a></div>
        <div class="update-pub-cover span-4">
        <a href="%s">
        <img src="%s%s" href="%s" alt="%s"/></a>
        </div>
        <div class="update-pub-title span-10 last">
        <a href="%s">%s</a>
        </div>
        <div class="update-pub-description span-10 last ">%s</div>
        </div>
        """

    followings = getFollowings(request, request.user)

    updates = getUpdates(request, followings)[last_up:last_up+more_num]

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
            htmlOutput += template_post % ( link_prof_details_post, name, lastname, avatar_post, username, link_prof_details_post,
                                           name, lastname,
                                           name, lastname, link_post_url, update.post.title, text_post )

    dajax = Dajax()
    dajax.append('#list-updates','innerHTML', htmlOutput)
    dajax.assign('#last_update','innerHTML', last_up+len(updates))

    return dajax.json()


dajaxice_functions.register(more_updates)
