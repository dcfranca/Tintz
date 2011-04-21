# -*- coding: utf-8 -*-
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseForbidden,HttpResponseRedirect
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core import serializers

from django.utils.translation import ugettext as _
from django.utils.translation import ugettext

from profiles.models import Profile
from profiles.forms import ProfileForm
from publications.models import Publication
from follow.models import FollowAuthor,Update
#from notification.models import *

from datetime import *
from blog.models import Post

from avatar.templatetags.avatar_tags import avatar
from account.utils import login_complete

from blog.models import Post

from haystack.query import SearchQuerySet

import logging, random

from account.utils import login_complete

if "notification" in settings.INSTALLED_APPS:
    from notification import models as notification
else:
    notification = None

def getPublications(request, other_user, is_me):
    publications = []
    try:
        if is_me == True:
            publications = Publication.objects.filter( author = other_user, status=1 ).order_by('-date_added')
        else:
            calc_age(request.user.get_profile())
            publications = Publication.objects.filter( author = other_user, rated__lte=request.user.get_profile().age, status=1 ).order_by('-date_added')
    except Publication.DoesNotExist:
        pass
    return publications

def getPublicPublications(request, other_user):
    publications = []
    try:
        publications = Publication.objects.filter(author = other_user, is_public=True)
    except Publication.DoesNotExist:
        pass
    return publications

def getFollowers(request, other_user):
    followers = FollowAuthor.objects.filter( UserTo = other_user ).order_by('-id')
    followerUsers = []
    for follow in followers:
        followerUsers.append( follow.UserFrom )
    return followerUsers

def getFollowings(request, other_user):
    #Finding followings
    followings = FollowAuthor.objects.filter( UserFrom = other_user ).order_by('-id')
    followinUsers = []
    for  follow in followings:
        followinUsers.append( follow.UserTo )
    return followinUsers

def getRecommendedFollowings(request, other_user):
    #Finding who to follow

    usersToFollow = []

    if request.user.is_authenticated():
        usersToFollow = User.objects.raw("""
                                        SELECT f2."UserTo_id" as id,count(*)
                                        FROM follow_followauthor f1, follow_followauthor f2
                                        WHERE f1."UserFrom_id" = %s
                                        AND f2."UserFrom_id" = f1."UserTo_id"
                                        AND f2."UserTo_id" != %s
                                        AND NOT EXISTS (SELECT id FROM follow_followauthor
                                                        WHERE "UserFrom_id" = %s
                                                        AND "UserTo_id" = f2."UserTo_id" )
                                        
                                        group by 1
                                        order by count desc
                                        limit 20;
                                        """,[ other_user.id,other_user.id, other_user.id ])[:20]
    else:
        usersToFollow = User.objects.raw("""
                                        SELECT f1."UserTo_id" as id,count(*)
                                        FROM follow_followauthor f1            
                                        group by 1
                                        order by count desc
                                        limit 20;
                                        """)[:20]

    random.shuffle(usersToFollow)

    return usersToFollow[:4]

def getRecommendedPublications(request, other_user):
    publications = []

    publications = Publication.objects.raw("""
                                SELECT *
                                FROM publications_publication
                                WHERE date_added
                                BETWEEN (now() - '3 month'::interval)::timestamp AND now()
                                order by views desc
                                limit 20;
                                """)[:20]

    random.shuffle(publications)

    return publications[:5]


def getPosts(request, other_user):
    blogs = Post.objects.filter(status=2).select_related(depth=1).order_by("-publish")
    return blogs.filter(author=other_user)

def getUpdates(request,followingUsers):
    updates = []

    for following in followingUsers:
        publications = getPublications(request,following, False)
        for publication in publications:
            if publication.status == 1:
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

    sorted_updates = sorted(updates, key=lambda update: update.date_post, reverse=True)[:8]
    
    if request.is_ajax():
        return_updates = serializers.serialize("json",sorted_updates)
        return HttpResponse(return_updates,mimetype="text/javascript")
    else:
        return sorted_updates

@login_complete
def home(request, template_name="homepage.html"):

    updates = []
    publications   = []
    followingUsers = []
    followerUsers  = []

    logging.debug("Home - Enter")

    if request.user.is_authenticated():
        logging.debug("home - Usuario logado")
        followerUsers = getFollowers(request, request.user)
        followingUsers = getFollowings(request, request.user)

        updates = getUpdates(request,followingUsers)[:10]

        publications = getPublications(request, request.user, True)
    else:
        logging.debug("Home - Usario nao logado")
        return HttpResponseRedirect(reverse('acct_login'))

    logging.debug("Home - Leave")

    return render_to_response(template_name, {
        "other_user": request.user,
        "is_me": True,
        "updates": updates,
        "notices": None,
        "home": True,
        "publications": publications,
        "followers":followerUsers,
        "followings":followingUsers,
    }, context_instance=RequestContext(request))


def home2(request, template_name="homepage2.html"):

    updates = []
    publications   = []
    followingUsers = []
    followerUsers  = []

    logging.debug("Home - Enter")

    if request.user.is_authenticated():
        logging.debug("home - Usuario logado")
        followerUsers = getFollowers(request, request.user)
        followingUsers = getFollowings(request, request.user)

        updates = getUpdates(request,followingUsers)[:10]

        publications = getPublications(request, request.user, True)

    else:
        logging.debug("Home - Usario nao logado")
        #return HttpResponseRedirect(reverse('acct_login'))

    usersToFollow = getRecommendedFollowings(request, request.user)
    recommended_pubs = getRecommendedPublications(request,request.user)

    logging.debug("Home - Leave")

    return render_to_response(template_name, {
        "other_user": request.user,
        "is_me": True,
        "updates": updates,
        "notices": None,
        "home": True,
        "publications": publications,
        "related_publications": recommended_pubs,
        "followers":followerUsers,
        "followings":followingUsers,
        "other_profiles": usersToFollow,
    }, context_instance=RequestContext(request))


def profiles(request, template_name="profiles/profiles.html"):
    return render_to_response(template_name, {
        "other_profiles": User.objects.all().order_by("-date_joined"),
        "title": "Perfis",
    }, context_instance=RequestContext(request))


@login_complete
def button_follow(request, other_user):
    follow = FollowAuthor()
    follow.UserFrom = request.user
    follow.UserTo = other_user
    Update.objects.update_followers(0, other_user, request.user)
    request.user.message_set.create(message=_(u"Você agora está seguindo %(from_user)s") % {'from_user': other_user.username})
    follow.save()

@login_complete
def button_unfollow(request, other_user):
    try:
        follow = FollowAuthor.objects.get(  UserFrom=request.user,  UserTo=other_user )
        request.user.message_set.create(message=_(u"Você não está mais seguindo %(from_user)s") % {'from_user': other_user.username})
        follow.delete()
    except FollowAuthor.DoesNotExist:
        pass


def profile(request, username, to_follow = None, template_name="profiles/profile.html"):
    other_user = get_object_or_404(User, username=username)
    publications = []
    is_follow = False

    calc_age(other_user.get_profile())

    if request.user == other_user:
        is_me = True
    else:
        is_me = False

    if not is_me and to_follow == '1':
        button_follow(request, other_user)
    elif not is_me and to_follow == '0':
        button_unfollow(request, other_user)

    #Finding publications
    if request.user.is_authenticated():
        calc_age(request.user.get_profile())

        publications = getPublications(request, other_user, is_me)
    else:
        publications = getPublicPublications(request, other_user)

    #Finding followings
    followinUsers = getFollowings(request,other_user)

    #Finding followers
    followerUsers = getFollowers(request,other_user)

    posts = getPosts(request, other_user) # Post.objects.filter(status=2).select_related(depth=1).order_by("-publish")
    #posts = blogs.filter(author=other_user)

    is_edit = False

    if is_me:
        if request.method == "POST":
            if request.POST["action"] == "update":
                profile_form = ProfileForm(request.POST, instance=other_user.get_profile())
                if profile_form.is_valid():
                    profile = profile_form.save()
                    profile.user = other_user
                    profile.save()
                    request.user.message_set.create(message=_(u"Perfil atualizado com sucesso"))
                    template_name="profiles/profile_edit.html"
                    is_edit = True
                else:
                    template_name="profiles/profile_edit.html"
                    is_edit = True
            elif request.POST["action"] == "edit":
                template_name="profiles/profile_edit.html"
                profile_form = ProfileForm(instance=other_user.get_profile())
                is_edit = True
            else:
                profile_form = ProfileForm(instance=other_user.get_profile())
        else:
            profile_form = ProfileForm(instance=other_user.get_profile())
    else:
        profile_form = None

    if request.user.is_authenticated():
        try:
            follow = FollowAuthor.objects.get( UserFrom=request.user,  UserTo=other_user )
            if follow:
                is_follow = True
            else:
                is_follow = False

        except FollowAuthor.DoesNotExist:
            pass

    nr_publications = len(publications)
    nr_posts        = len(posts)
    nr_followings   = len(followinUsers)
    nr_followers    = len(followerUsers)

    publications  = publications[:6]
    posts         = posts[:8]
    followinUsers = followinUsers[:21]
    followerUsers = followerUsers[:21]

    return render_to_response(template_name, {
        "form": profile_form,
        "is_me": is_me,
        "is_follow": is_follow,
        "other_user": other_user,
        "publications": publications,
        "followings": followinUsers,
        "followers": followerUsers,
        "is_profile": True,
        "is_edit": is_edit,
        "posts": posts,
        "nr_publications": nr_publications,
        "nr_posts": nr_posts,
        "nr_followings": nr_followings,
        "nr_followers": nr_followers,
        }, context_instance=RequestContext(request))


def calc_age(profile):
    if profile.birth_date.month > date.today().month or ( profile.birth_date.month == date.today().month and profile.birth_date.day > date.today().day ):
        profile.age = date.today().year - profile.birth_date.year - 1
    else:
        profile.age = date.today().year - profile.birth_date.year


@login_complete
def searchresults(request, template_name="profiles/results.html", search_text=""):
    """
    Show the results of publications search
    """
    users = []
    publications = []

    results = SearchQuerySet().filter(content=search_text)

    for result in results:
        if isinstance( result.object, Profile):
            users.append(result.object.user)
        elif isinstance( result.object, Publication):
            publications.append(result.object)

    find_pub = False

    if len(publications) > 0:
        find_pub = True

    return render_to_response(template_name, {
        "other_profiles": users,
        "title": "Resultados",
        "is_me": True,
        "other_user": request.user,
        "search_text": search_text,
        "is_follow": False,
        "find_pub": find_pub,
        },
    context_instance=RequestContext(request))
