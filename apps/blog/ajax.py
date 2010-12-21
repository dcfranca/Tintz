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
from blog.models import Post

from django.core.urlresolvers import reverse

def more_posts(request, other_user_id, last_post):
    publications = []

    more_num = 10

    other_user = User.objects.get( pk = other_user_id )
    media_url = '/site_media/'

    last_post = int(last_post)

    if other_user == request.user:
        is_me = True
    else:
        is_me = False


    template =  """<tr><td><a class="span-5 list-posts-title" href="%s">%s</a>
                <div class="list-posts-subtitle last">%s</div>
                <div class="span-10 list-posts-description last">
                        %s
                </div>"""

    if is_me:
        template += """<div class="span-1 list-posts-button"><a href="%s" ><img src="%simages/publication_edit.png" title="Editar Post"></img></a></div>
                  <div class="span-1 list-posts-button last"><a href="%s" onclick=" ConfirmChoice('%s'); return false;"><img src="%simages/publication_delete.png" title="Excluir Post"></img></a></div>"""

    template += """<div class="separator span-13 last"></div></td></tr>"""

    posts = Post.objects.filter(status=2).select_related(depth=1).order_by("-publish")

    if is_me == True:
        posts = posts.filter(author=request.user)[last_post:last_post+more_num]
    else:
        posts = posts.filter(author=other_user)[last_post:last_post+more_num]

    htmlOutput = ""

    for post in posts:

        post_url = post.get_absolute_url()
        date_posted = post.publish.strftime("%d/%m/%Y")
        post_text   = post.get_small_text()
        link_edit = reverse('blog_edit', args=(post.id,))
        link_destroy = reverse('blog_edit', args=(post.id,))

        if is_me:
            htmlOutput += template % ( post_url, post.title, date_posted, post_text,
            link_edit, media_url, link_destroy, link_destroy ,media_url )
        else:
            htmlOutput += template % ( post_url, post.title, date_posted, post_text )

    dajax = Dajax()
    dajax.append('#list-posts','innerHTML', htmlOutput)
    dajax.assign('#last_post','innerText', last_post+len(posts))

    return dajax.json()


dajaxice_functions.register(more_posts)