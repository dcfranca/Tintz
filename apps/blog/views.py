# -*- coding: iso-8859-1 -*-
#!python

import datetime
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponseRedirect, Http404
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from django.conf import settings
import htmlentitydefs, re
import logging

from blog.models import Post
from blog.forms import *
from follow.models import FollowAuthor,Update
from tintzsettings.models import TintzSettings

from account.utils import login_complete

if "notification" in settings.INSTALLED_APPS:
    from notification import models as notification
else:
    notification = None

def blogs(request, username=None, template_name="blog/blogs.html"):
    blogs = Post.objects.filter(status=2).select_related(depth=1).order_by("-publish")
    is_me = False
    user = None

    if username is not None:
        user = get_object_or_404(User, username=username)
        blogs = blogs.filter(author=user)[0:10]
    else:
        blogs = blogs.filter(author=request.user)[0:10]


    if user == None:
        user = request.user

    is_follow = False
    if request.user.is_authenticated():
        try:
            follow = FollowAuthor.objects.get( UserFrom=request.user,  UserTo=user )
            if follow:
                is_follow = True
            else:
                is_follow = False
        except FollowAuthor.DoesNotExist:
            pass

    if request.user == user:
        is_me = True

    is_profile = not request.user.is_authenticated()

    return render_to_response(template_name, {
        "blogs": blogs,
        "other_user": user,
        "is_me": is_me,
        "is_follow":is_follow,
        "is_profile": is_profile,
    }, context_instance=RequestContext(request))


@login_complete
def post(request, username, year, month, slug,
         template_name="blog/post.html"):

    post = Post.objects.filter(slug=slug, publish__year=int(year), publish__month=int(month)).filter(author__username=username)
    if not post:
       raise Http404

    if post[0].status == 1 and post[0].author != request.user:
       raise Http404

    is_me = False
    if post[0].author == request.user:
        is_me = True

    is_follow = False
    try:
        follow = FollowAuthor.objects.get( UserFrom=request.user,  UserTo=post[0].author )
        if follow:
            is_follow = True
        else:
            is_follow = False
    except FollowAuthor.DoesNotExist:
        pass

    return render_to_response(template_name, {
        "post": post[0],
        "is_me": is_me,
        "other_user":post[0].author,
        "is_follow": is_follow,
    }, context_instance=RequestContext(request))

@login_complete
def destroy(request, id):
    post = Post.objects.get(pk=id)
    user = request.user
    title = post.title
    if post.author != request.user:
            request.user.message_set.create(message=_(u'Voc? n?o pode apagar posts de outros usu?rios'))
            return HttpResponseRedirect(reverse("blog_list_user",args=(request.user.username,)))

    post.delete()
    request.user.message_set.create(message=_(u"Post excluido com sucesso'%s'") % title)
    return HttpResponseRedirect(reverse("blog_list_user",args=(request.user.username,)))

@login_complete
def new(request, form_class=BlogForm, template_name="blog/new.html"):
    if request.method == "POST":
        if request.POST["action"] == "create":
            blog_form = form_class(request.user, request.POST)
            if blog_form.is_valid():
                blog = blog_form.save(commit=False)
                blog.author = request.user
                blog.slug    = slugfy( blog.title , '-')

                logging.debug('New Post' )
                #try:
                ind = 1
                exist_blog = Post.objects.filter(author=request.user,  slug=blog.slug)
                logging.debug('exist_blog = %s' % exist_blog)
                while exist_blog:
                    temp_title = blog.title[0:48]+str(ind)
                    logging.debug('temp_title= %s' % temp_title)
                    blog.slug    = slugfy( temp_title, '-')
                    logging.debug('slug= %s' % blog.slug )
                    ind = ind + 1
                    exist_blog = Post.objects.filter(author=request.user,  slug=blog.slug)
                    logging.debug('exist_blog 2= %s' % exist_blog)
                #except:
                 #   logging.debug('Except in exist_blog')
                 #   pass

                if settings.BEHIND_PROXY:
                    blog.creator_ip = request.META["HTTP_X_FORWARDED_FOR"]
                else:
                    blog.creator_ip = request.META['REMOTE_ADDR']
                blog.save()

                request.user.message_set.create(message=_("Postado com sucesso '%s'") % blog.title)

                Update.objects.update_followers(2, blog)


                return HttpResponseRedirect(reverse("blog_list_user",args=(request.user.username,)))
        else:
            blog_form = form_class()
    else:
        blog_form = form_class()

    return render_to_response(template_name, {
        "form": blog_form,
        "is_me": True,
        "other_user": request.user,
        "is_follow":False,
    }, context_instance=RequestContext(request))

@login_complete
def edit(request, id, form_class=BlogForm, template_name="blog/edit.html"):
    post = get_object_or_404(Post, id=id)

    if request.method == "POST":
        if post.author != request.user:
            request.user.message_set.create(message=_(u"Voc? n?o pode editar posts de outros usu?rios"))
            return HttpResponseRedirect(reverse("blog_list_yours"))
        if request.POST["action"] == "update":
            blog_form = form_class(request.user, request.POST, instance=post)
            if blog_form.is_valid():
                blog = blog_form.save(commit=False)
                blog.save()
                request.user.message_set.create(message=_(u"Post  atualizado com sucesso'%s'") % blog.title)
                #if notification:
                    #if blog.status == 2: # published
                        #if friends: # @@@ might be worth having a shortcut for sending to all friends
                        #    notification.send((x['friend'] for x in Friendship.objects.friends_for_user(blog.author)), "blog_follow_post", {"post": blog})

                return HttpResponseRedirect(reverse("blog_list_user",args=(request.user.username,)))
        else:
            blog_form = form_class(instance=post)
    else:
        blog_form = form_class(instance=post)

    return render_to_response(template_name, {
        "form": blog_form,
        "post": post,
        "other_user": request.user,
	    "is_me": True,
    }, context_instance=RequestContext(request))

def slugfy(text, separator):
  ret = ""
  for c in text.lower():
    try:
      ret += htmlentitydefs.codepoint2name[ord(c)]
    except:
      ret += c

  ret = re.sub("([a-zA-Z])(uml|acute|grave|circ|tilde|cedil)", r"\1", ret)
  ret = re.sub("\W", " ", ret)
  ret = re.sub(" +", separator, ret)

  return ret.strip()[0:49]
