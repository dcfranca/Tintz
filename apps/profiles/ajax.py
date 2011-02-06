from django.utils import simplejson
from dajaxice.core import dajaxice_functions
from dajax.core import Dajax
from follow.models import FollowAuthor
import dajax
from django.contrib.auth.models import User
from avatar.templatetags.avatar_tags import *

from django.core.urlresolvers import reverse

def more_profiles(request, other_user_id, last_profile, type):

    other_user = User.objects.get( pk = other_user_id )
    more_num = 10
    last_prof = int(last_profile)

    template = """<tr><td>
       <div class="profiles-item">
       <div class="avatar span-2"><a href="%s" title="%s %s"><img src="%s" alt="%s" width="70" height="70" /></a></div>
       <div class="profiles-details span-5 last"><a href="%s" title="%s %s">%s %s</a></div>
       <div class="profiles-about span-10 last">%s</div>
       <div class="separator span-10 last"></div>
       </div>
       </td></tr> """

    users = []

    if type == 'Seguidores':
        followers = FollowAuthor.objects.filter( UserTo = other_user ).order_by('-id')
        for  follow in followers:
            if follow.UserFrom:
                users.append( follow.UserFrom )
    elif type == 'Seguindo':
        followings = FollowAuthor.objects.filter( UserFrom = other_user ).order_by('-id')
        for  follow in followings:
            if follow.UserTo:
                users.append( follow.UserTo )

    users = users[last_prof:last_prof+more_num]

    htmlOutput = ""

    for user in users:
        link_prof_details = reverse('profile_detail', args=(user,))

        try:
            name = user.get_profile().first_name
            lastname = user.get_profile().last_name
            small_about = user.get_profile().get_small_about()
        except:
            name = user.username
            lastname = ''
            small_about = ''

        username = user.username
        avatar = avatar_url(user, 70)
        if len(name) == 0:
            name = username
        htmlOutput += template % ( link_prof_details, name, lastname, avatar, username, link_prof_details, name, lastname,
                               name, lastname, small_about )


    dajax = Dajax()
    dajax.append('#list-profiles','innerHTML', htmlOutput)
    dajax.assign('#last_profile','innerHTML', last_prof+len(users))

    return dajax.json()


dajaxice_functions.register(more_profiles)
