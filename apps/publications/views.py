# -*- coding: iso-8859-1 -*-
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponseRedirect, get_host
from django.template import RequestContext
from django.db.models import Q
from django.http import Http404
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required

from publications.models import Publication, PublicationScore
from profiles.views import calc_age
from follow.models import FollowAuthor
from publications.forms import PublicationUploadForm, PublicationEditForm
from tagging.models import *
from django.http import Http404
from django.conf import settings
from django.test.client import Client
from django.core.paginator import Paginator, InvalidPage, EmptyPage

import logging

import unittest

#from django.pimentech.network import *

import os, datetime

from PIL import Image

#service = JSONRPCService()

if "notification" in settings.INSTALLED_APPS:
    from notification import models as notification
else:
    notification = None

# Create your views here.
SITE_MEDIA_ROOT = getattr(settings, 'MEDIA_ROOT',
    os.path.join(settings.PROJECT_ROOT, 'site_media'))


search_text = ''


def getPublications(request, other_user, is_me):
    publications = []
    try:
        if is_me == True:
            publications = Publication.objects.filter( author = other_user )
        else:
            publications = Publication.objects.filter( author = other_user, rated__lte=request.user.get_profile().age )
    except Publication.DoesNotExist:
        pass
    return publications[:4]

def getFollowers(request, other_user):
    followers = FollowAuthor.objects.filter( UserTo = other_user )
    followerUsers = []
    for follow in followers:
        followerUsers.append( follow.UserFrom )
    return followerUsers

def getFollowings(request, other_user):
    #Finding followings
    followings = FollowAuthor.objects.filter( UserFrom = other_user )
    followinUsers = []
    for  follow in followings:
        followinUsers.append( follow.UserTo )
    return followinUsers


@login_required
def uploadpublication(request, form_class=PublicationUploadForm,
        template_name="publications/upload.html"):
    """
    upload form for publications
    """
    publication      = Publication()
    publication.author = request.user
    publication_form = form_class()

    #import pdb; pdb.set_trace()

    if request.method == 'POST':
        if request.POST.get("action") == "upload":
            publication_form = form_class(request.user, request.POST, request.FILES, instance=publication)
            if publication_form.is_valid():
                if request.FILES['file_name'].content_type != 'application/pdf' and request.FILES['file_name'].content_type != 'image/jpeg' and \
                request.FILES['file_name'].content_type != 'image/png' and request.FILES['file_name'].content_type != 'image/gif' and \
                not request.FILES['file_name'].name.endswith('.zip') and not request.FILES['file_name'].name.endswith('.cbz') and not request.FILES['file_name'].name.endswith('.rar') and not request.FILES['file_name'].name.endswith('.cbr'):
                    request.user.message_set.create(message=u"Tipo de arquivo inválido (Somente arquivos PDF/CBR/CBZ ou Imagem: JPG/GIF/PNG)")
                else:
                    publication = publication_form.save(commit=False)
                    publication.date_added = datetime.datetime.now()
                    publication.status = 0
                    publication.nr_pages = 0
                    publication.save()

                    try:
                        followers = FollowAuthor.objects.filter( UserTo = publication.author )
                    except FollowAuthor.DoesNotExist:
                        pass
                    if notification:
                        if followers:
                            notification.send((x.UserFrom for x in followers), "publication_follow_post", {"publication": publication})
                    request.user.message_set.create(message=_("Publicacao feita com sucesso '%s'") % publication.title)
                    return HttpResponseRedirect(reverse('publication_details', args=(publication.author, publication.id,)))

    calc_age(request.user.get_profile())
    return render_to_response(template_name, {
        "form": publication_form,
        "is_me": True,
        "other_user":request.user,
    }, context_instance=RequestContext(request))

@login_required
def publications(request, username, template_name="publications/latest.html"):
    """"
    Show publications
    """

    other_user = get_object_or_404(User, username=username)
    publications = []
    calc_age(request.user.get_profile())

    followingUsers = []
    followerUsers  = []

    if request.user.is_authenticated():
        followerUsers = getFollowers(request, request.user)
        followingUsers = getFollowings(request, request.user)
    else:
        HttpResponseRedirect(reverse('acct_login'))

    if other_user == request.user:
        is_me = True
    else:
        is_me = False

    logging.debug("Publications - Step 2")

    if is_me == True:
        publications = Publication.objects.filter( author = other_user )
    else:
        publications = Publication.objects.filter( author = other_user, rated__lte=request.user.get_profile().age )

    for publication in publications:
        logging.debug("Publication Title %s" % publication.title)

    logging.debug("Publications - Leave")

    return render_to_response(template_name, {
        "publications": publications, "username": username,
        "other_user": other_user, "is_me": is_me,
        "title": u"Minhas Publicações",
        "followers":followerUsers,
        "followings":followingUsers,
    }, context_instance=RequestContext(request))

@login_required
def destroypublication(request, id):
    publication = Publication.objects.get(pk=id)

    if not publication:
        return HttpResponseRedirect(reverse('publications'))

    title = publication.title
    if publication.author != request.user:
        request.user.message_set.create(message=u"Você não possui permissão para excluir essa publicação")
        return HttpResponseRedirect(reverse('publications',args=(publication.author,)))

    publication.delete()
    request.user.message_set.create(message=_(u"Publicação excluida com sucesso.'%s'") % title)
    return HttpResponseRedirect(reverse('publications',args=(publication.author,)))

@login_required
def editpublication(request, id, form_class=PublicationEditForm,
        template_name="publications/editpublication.html"):
    publication = get_object_or_404(Publication, id=id)

    calc_age(request.user.get_profile())

    if request.method == "POST":
        if publication.author != request.user:
            request.user.message_set.create(message="Voce n&atilde;o tem permiss&atilde;o para editar")
            return HttpResponseRedirect(reverse('publication_details', args=(publication.id,)))
        if request.POST["action"] == "update":
            publication_form = form_class(request.user, request.POST, instance=publication)
            if publication_form.is_valid():
                publicationobj = publication_form.save(commit=False)
                publicationobj.save()
                request.user.message_set.create(message=_(u"Publicação atualizada com sucesso '%s'") % publication.title)

                return HttpResponseRedirect(reverse('publication_details', args=(publication.author, publication.id,)))
        else:
            publication_form = form_class(instance=publication)

    else:
        publication_form = form_class(instance=publication)

    return render_to_response(template_name, {
        "publication_form": publication_form,
        "publication": publication,
        "is_me": True,
        "other_user": request.user,
    }, context_instance=RequestContext(request))

@login_required
def detailspublication(request, id, username, template_name="publications/details.html"):
    """
    show the publication details
    """

    mypublication = get_object_or_404(Publication, id=id)
    # @@@: test
    #if not publication.is_public and request.user != publication.author:
    #    raise Http404
    #publication_url = publication.get_display_url()

    title = mypublication.title
    host = "http://%s" % get_host(request)

    publications   = []
    followingUsers = []
    followerUsers  = []

    if request.user.is_authenticated():
        publications = getPublications(request, mypublication.author, True)
        followerUsers = getFollowers(request, mypublication.author)
        followingUsers = getFollowings(request, mypublication.author)
    else:
        HttpResponseRedirect(reverse('acct_login'))

    if mypublication.author == request.user:
        is_me = True
    else:
        is_me = False
    is_voted = False

    if is_me == False:
        calc_age(request.user.get_profile())
        if mypublication.rated > request.user.get_profile().age:
            raise Http404

    try:
        #Check if there's a vote already
        publication_score = PublicationScore.objects.get( publication = mypublication, who_vote = request.user )
        is_voted = True
    except PublicationScore.DoesNotExist:
        publication_score = PublicationScore()
        publication_score.rate = 0
        is_voted = False

    if request.method == "POST":
        rate = request.POST["rate"]
        if rate and rate > 0:
            if not is_voted:
                publication_score.publication = mypublication
                publication_score.who_vote    = request.user

            publication_score.vote_date   = datetime.datetime.now()
            publication_score.rate        = rate

            publication_score.save()
            publications_scores = PublicationScore.objects.filter( publication = mypublication )
            total_rates = 0

            if publications_scores.count() > 100:
                for rates in publications_scores:
                    total_rates += int(rates.rate)

                mypublication.rate = str(float((float(total_rates)/publications_scores.count())*20))
                mypublication.save()

            request.user.message_set.create(message=_("Voto efetuado com sucesso para '%s'") % mypublication.title )
            is_voted = True

    #Found Related Publications
    try:
        related_publications = TaggedItem.objects.get_by_model( Publication, mypublication.tags ).exclude(author = mypublication.author)
    except Publication.DoesNotExist:
        related_publications = None

    pages = range(1, mypublication.nr_pages+1)
    paginator = Paginator(pages, 1)

    # Make sure page request is an int. If not, deliver first page.
    try:
        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1

    # If page request (9999) is out of range, deliver last page of results.
    try:
        publication_pages = paginator.page(page)
    except (EmptyPage, InvalidPage):
        publication_pages = paginator.page(paginator.num_pages)

    return render_to_response(template_name, {
        "host": host,
        "publication": mypublication,
        "related_publications":related_publications,
        "is_me": is_me,
        "is_voted": is_voted,
        "other_user": mypublication.author,
        "publication_score": publication_score.rate,
        "publications": publications,
        "followers":followerUsers,
	"pages": publication_pages,
	"file_ext": mypublication.images_ext,
        "followings":followingUsers,
    }, context_instance=RequestContext(request))

def viewerpublication(request, username, id, template_name="publications/viewer.html"):
    """
    show the publication details
    """
    publication = get_object_or_404(Publication, id=id)

    logging.debug("viewerpublication Username = [%s] - publication.is_public [%s]" % (request.user,publication.is_public) )
    host = "http://%s" % get_host(request)

    if not request.user.is_authenticated() and not publication.is_public:
        return render_to_response(template_name, {
            "host": host,
            "publication": publication,
            "pages": 0,
            "file_ext":"",
            "is_me": False,
            "other_user": publication.author,
        }, context_instance=RequestContext(request))

    if publication.author == request.user:
        is_me = True
    else:
        is_me = False

    if is_me == False and request.user.is_authenticated():
        calc_age(request.user.get_profile())
        if publication.rated > request.user.get_profile().age:
            raise Http404
        publication.incr_views()

    pages = range(1, publication.nr_pages+1)
    file_name, file_ext = os.path.splitext(os.path.basename(publication.file_name.path))

    paginator = Paginator(pages, 1)

    paginator_view = Paginator(pages, 21)

    # Make sure page request is an int. If not, deliver first page.
    try:
        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1

    # Make sure page request is an int. If not, deliver first page.
    try:
        page_view = int(request.GET.get('page_view'))
    except:
        page_view = int(page/21)
	if page % 21 != 0:
	    page_view += 1

    if page == 1 and page_view > 1:
	page = (21*(page_view-1))+1

    # If page request (9999) is out of range, deliver last page of results.
    try:
        publication_pages = paginator.page(page)
    except (EmptyPage, InvalidPage):
        publication_pages = paginator.page(paginator.num_pages)

    # If page request (9999) is out of range, deliver last page of results.
    try:
        pages_viewer = paginator_view.page(page_view)
    except (EmptyPage, InvalidPage):
        pages_viewer = paginator_view.page(paginator_view.num_pages)

    return render_to_response(template_name, {
        "host": host,
        "publication": publication,
        "pages": pages,
        "file_ext":publication.images_ext,
        "is_me": is_me,
	"pages": publication_pages,
	"pages_viewer":pages_viewer,
        "other_user": publication.author,
    }, context_instance=RequestContext(request))

@login_required
def searchprepare(request):
    """
    Prepare the search
    """
    logging.debug('searchprepare - Enter')

    if request.method == 'POST':
        search_text = request.POST['search_text']

    logging.debug('searchprepare - Leave')

    return HttpResponseRedirect(reverse('search_results',args=(search_text.encode('utf-8'),)))


@login_required
def searchresults(request, template_name="publications/latest.html", search_text="", publications=None):
    """
    Show the results of publications search
    """
    publications = []

    queryset = Publication.search.query(search_text.encode('utf-8'))
    publications  = queryset.filter().order_by("@weight")

    return render_to_response(template_name, {
        "publications": publications,
        "title": "Resultados",
    }, context_instance=RequestContext(request))

@login_required
def choose_publication(request, template_name="publications/choose.html"):
    """
    Choose the publication type
    """

    return render_to_response(template_name, {
    "other_user": request.user,
    }, context_instance=RequestContext(request))



"""
Teste
"""
class PublicationTestCase(unittest.TestCase):
    def setUp(self):
        publication = Publication()

    def TestWebRequests(self):
        cl = Client()
        response = cl.post()

    def publicComic(self):
        publication.author = "daniel"
        publication.date_added = datetime.datetime.now()
        publication.is_public = False
        publication.status = 0
        publication.title = "Titulo teste"
        publication.save()
