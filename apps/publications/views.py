# -*- coding: iso-8859-1 -*-
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponseRedirect, get_host
from django.template import RequestContext
#from django.db.models import Q
from django.http import Http404
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User

from publications.models import Publication
from publications.models import PublicationScore
from publications.models import PublicationReportAbuse
from profiles.views import calc_age
from follow.models import FollowAuthor

from publications.forms import PublicationUploadForm
from publications.forms import PublicationEditForm, PublicationReportAbuseForm
from tagging.models import TaggedItem
from django.conf import settings
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from profiles.models import Profile
from haystack.query import SearchQuerySet

from django.db import transaction

import os
import datetime

import logging

from account.utils import login_complete


# Create your views here.
SITE_MEDIA_ROOT = getattr(settings, 'MEDIA_ROOT',
    os.path.join(settings.PROJECT_ROOT, 'site_media'))

search_text = ''

def getPublications(request, other_user, is_me):
    publications = []
    try:
        if is_me == True:
            publications = Publication.objects.filter(author = other_user)
        else:
            publications = Publication.objects.filter(author = other_user, rated__lte=request.user.get_profile().age)
    except Publication.DoesNotExist:
        pass
    return publications[:4]


def getFollowers(request, other_user):
    followers = FollowAuthor.objects.filter(UserTo = other_user)
    followerUsers = []

    for follow in followers:
        followerUsers.append(follow.UserFrom)
    return followerUsers


def getFollowings(request, other_user):
    #Finding followings
    followings = FollowAuthor.objects.filter(UserFrom = other_user)
    followinUsers = []
    for follow in followings:
        followinUsers.append(follow.UserTo)
    return followinUsers


def is_valid_format(filename, content_type):
    logging.debug('IS_VALID_FORMAT: '+filename)
    
    filename = filename.lower()
    
    if content_type != 'application/pdf' and content_type != 'image/jpeg' and \
    content_type != 'image/png' and content_type != 'image/gif' and \
    not filename.endswith('.zip') and \
    not filename.endswith('.cbz') and \
    not filename.endswith('.rar') and \
    not filename.endswith('.cbr') and \
    not filename.endswith('.gif') and \
    not filename.endswith('.png') and \
    not filename.endswith('.jpg') and \
    not filename.endswith('.jpeg'):
        logging.debug('VALID FORMAT = FALSE')
        return False

    logging.debug('VALID FORMAT = TRUE')
    return True


@login_complete
def uploadpublication(request, form_class=PublicationUploadForm,
        template_name="publications/upload.html"):
    """
    upload form for publications
    """
    publication = Publication()
    publication.author = request.user
    publication_form = form_class()

    if request.method == 'POST':
        if request.POST.get("action") == "upload":
            publication_form = form_class(request.user, request.POST, request.FILES, instance=publication)
            if publication_form.is_valid():
                if not is_valid_format(request.FILES['file_name'].name, request.FILES['file_name'].content_type):
                    request.user.message_set.create(message=u"Tipo de arquivo inv?lido (Somente arquivos PDF/CBR/CBZ ou Imagem: JPG/GIF/PNG)")
                else:
                    publication = publication_form.save(commit=False)
                    publication.date_added = datetime.datetime.now()
                    publication.status = 0
                    publication.nr_pages = 0
                    publication.save()

                    request.user.message_set.create(message=_(u"Publicação feita com sucesso '%s'") % publication.title)
                    return HttpResponseRedirect(reverse('publications', args=(publication.author, )))

    calc_age(request.user.get_profile())

    return render_to_response(template_name, {
        "form": publication_form,
        "is_me": True,
        "other_user": request.user,
    }, context_instance=RequestContext(request))


@login_complete
def publications(request, username, template_name="publications/list_publications.html"):
    """"
    Show publications
    """

    other_user = get_object_or_404(User, username=username)
    publications = []
    calc_age(request.user.get_profile())

    followingUsers = []
    followerUsers = []

    is_follow = False
    try:
        follow = FollowAuthor.objects.get(UserFrom=request.user, UserTo=other_user)
        if follow:
            is_follow = True
        else:
            is_follow = False

    except FollowAuthor.DoesNotExist:
        pass

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
        publications = Publication.objects.filter(author = other_user).order_by('-date_added')[0:6]
    else:
        publications = Publication.objects.filter(author = other_user, rated__lte=request.user.get_profile().age).order_by('-date_added')[0:6]

    logging.debug("Publications - Leave")

    return render_to_response(template_name, {
        "publications": publications, "username": username,
        "other_user": other_user, "is_me": is_me,
        "title": u"Minhas Publica??es",
        "followers": followerUsers,
        "followings": followingUsers,
        "is_follow": is_follow,
    }, context_instance=RequestContext(request))


@login_complete
def destroypublication(request, id):
    publication = get_object_or_404(Publication, pk=id)

    if not publication:
        return HttpResponseRedirect(reverse('publications'))

    title = publication.title
    if publication.author != request.user:
        request.user.message_set.create(message=u"Voc? n?o possui permiss?o para excluir essa publica??o")
        return HttpResponseRedirect(reverse('publications', args=(publication.author, )))

    try:
        publication.delete()
    except IOError:
        pass
    except:
        request.user.message_set.create(message=u"Erro ao tentar excluir a publica??o")
        return HttpResponseRedirect(reverse('publications', args=(publication.author, )))

    request.user.message_set.create(message=_(u"Publica??o excluida com sucesso.'%s'") % title)
    return HttpResponseRedirect(reverse('publications', args=(publication.author, )))


@login_complete
def reportabuse(request, id, form_class=PublicationReportAbuseForm,
                template_name="publications/report_abuse.html"):
    publication = get_object_or_404(Publication, id=id)

    if publication.author == request.user:
        request.user.message_set.create(message=u"Voce n?o pode denunciar sua pr?pria public?o")
        return HttpResponseRedirect(reverse('publication_details', args=(publication.author, publication.id, )))

    report_abuse_form = form_class(request.user, instance=publication)

    if request.method == "POST":
        report_abuse = PublicationReportAbuse()
        report_abuse_form = form_class(request.user, request.POST, instance=report_abuse)
        if report_abuse_form.is_valid():
            report_abuse = report_abuse_form.save(commit=False)
            report_abuse.reporter = request.user
            report_abuse.publication = publication
            report_abuse.save()
            request.user.message_set.create(message=_(u"Publica??o denunciada com sucesso.'%s'") % publication.title)
            return HttpResponseRedirect(reverse('publication_details', args=(publication.author, publication.id, )))

    return render_to_response(template_name, {
        "form": report_abuse_form,
        "other_user": publication.author,
        "publication": publication,
    }, context_instance=RequestContext(request))


@login_complete
def editpublication(request, id, form_class=PublicationEditForm,
        template_name="publications/editpublication.html"):
    publication = get_object_or_404(Publication, id=id)

    calc_age(request.user.get_profile())

    if request.method == "POST":
        if publication.author != request.user:
            request.user.message_set.create(message="Voce n&atilde;o tem permiss&atilde;o para editar")
            return HttpResponseRedirect(reverse('publication_details', args=(publication.id, )))
        if request.POST["action"] == "update":
            publication_form = form_class(request.user, request.POST, instance=publication)
            if publication_form.is_valid():
                publicationobj = publication_form.save(commit=False)
                publicationobj.save()
                request.user.message_set.create(message=_(u"Publica??o atualizada com sucesso '%s'") % publication.title)

                return HttpResponseRedirect(reverse('publication_details', args=(publication.author, publication.id,)))
        else:
            publication_form = form_class(instance=publication)

    else:
        publication_form = form_class(instance=publication)

    return render_to_response(template_name, {
        "form": publication_form,
        "publication": publication,
        "is_me": True,
        "other_user": request.user,
    }, context_instance=RequestContext(request))

def detailspublication(request, id, username, template_name="publications/details.html"):
    """
    show the publication details
    """

    mypublication = get_object_or_404(Publication, id=id)

    title = mypublication.title
    host = "http://%s" % get_host(request)

    publications   = []
    followingUsers = []
    followerUsers  = []

    is_follow = False
    try:
        follow = FollowAuthor.objects.get( UserFrom=request.user,  UserTo=mypublication.author )
        if follow:
            is_follow = True
        else:
            is_follow = False
    except:
        pass

    if request.user.is_authenticated():
        publications = getPublications(request, mypublication.author, True)
        followerUsers = getFollowers(request, mypublication.author)
        followingUsers = getFollowings(request, mypublication.author)
    elif mypublication.is_public == True:
        return HttpResponseRedirect(reverse('publication_viewer', args=(mypublication.author, mypublication.id,)))
    else:
        return HttpResponseRedirect(reverse('acct_login'))

    if mypublication.author == request.user:
        is_me = True
    else:
        is_me = False
    is_voted = False

    #import pdb; pdb.set_trace()

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

    #Found Related Publications
    try:
        related_publications = TaggedItem.objects.get_by_model( Publication, mypublication.tags ).exclude(author = mypublication.author)[:4]
    except Publication.DoesNotExist:
        related_publications = None

    if mypublication.rate == None:
        mypublication.rate = 0
        mypublication.save()

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
        "is_follow":is_follow,
    }, context_instance=RequestContext(request))

def viewerpublication(request, username, id, template_name="publications/viewer.html"):
    """
    show the publication details
    """
    publication = get_object_or_404(Publication, id=id)

    host = "http://%s" % get_host(request)

    if not request.user.is_authenticated() and publication.is_public == False:
        return HttpResponseRedirect(reverse('acct_login'))

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

@login_complete
def searchprepare(request):
    """
    Prepare the search
    """
    if request.method == 'POST':
        search_text = request.POST['search_text']

    if len(search_text) > 0:
       return HttpResponseRedirect(reverse('search_results',args=(search_text.encode('utf-8'),)))
    else:
       return HttpResponseRedirect(reverse('search_results',args=(" ")))

@login_complete
def searchresults(request, template_name="publications/results.html", search_text=""):
    """
    Show the results of publications search
    """
    publications = []
    users = []

    results = SearchQuerySet().filter(content=search_text).order_by('-date_added')

    for result in results:
        if isinstance( result.object, Publication):
            publications.append(result.object)
        elif isinstance( result.object, Profile):
            users.append(result.object.user)

    if len(publications) == 0:
        return HttpResponseRedirect(reverse('search_results_prof',args=(search_text.encode('utf-8'),)))

    find_prof = False

    if len(users) > 0:
        find_prof = True

    return render_to_response(template_name, {
        "publications": publications,
        "title": "Resultados",
        "other_user": request.user,
        "search_text": search_text,
        "is_me": True,
        "find_prof": find_prof,
    }, context_instance=RequestContext(request))
