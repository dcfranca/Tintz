import re
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from tintz import settings

# Create your views here.
class RedirectBrowser:
    """
    Redirect old browsers (IE sux)
    """
    def process_request(self, request):

        #import pdb; pdb.set_trace()

        if request.path.startswith(settings.MEDIA_URL) or request.path.startswith("/about/old_browser/"):
            return None

        if request.META.has_key('HTTP_USER_AGENT'):
            user_agent = request.META['HTTP_USER_AGENT']

            # Test common mobile values.
            pattern = "(MSIE 6|MSIE 7)"
            prog = re.compile(pattern, re.IGNORECASE)
            match = prog.search(user_agent)

            if match:
                return HttpResponseRedirect(reverse('old_browser'))
            else:
                return None

